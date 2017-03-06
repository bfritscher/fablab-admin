from mailchimp3 import MailChimp
from django.template.loader import get_template
import hashlib
import cStringIO as StringIO
from xhtml2pdf import pisa
from fablabadmin import settings
import os
import environ
from mail_templated import EmailMessage
from raven.contrib.django.raven_compat.models import client

env = environ.Env()

mailchimp_client = MailChimp(env('MAILCHIMP_USERNAME'), env('MAILCHIMP_KEY'))


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL       # Typically /static/media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
    return path

def make_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("utf-8")), result, link_callback=link_callback, encoding='UTF-8')
    if not pdf.err:
        return result
    else:
        raise Exception(pdf.err)

def mailchimp_add(contact):
    member = {
        "email_address": contact.email,
        "status": "subscribed",
        "merge_fields": {
            "FNAME": contact.first_name,
            "LNAME": contact.last_name
        }
    }
    try:
        mailchimp_client.lists.members.create(env('MAILCHIMP_MEMBER_LIST_ID'), member)
    except:
        client.captureException()
    try:
        mailchimp_client.lists.members.create(env('MAILCHIMP_NEWSLETTER_LIST_ID'), member)
    except:
        client.captureException()


def mailchimp_remove(contact):
    hash = hashlib.md5(contact.email.lower()).hexdigest()
    try:
        mailchimp_client.lists.members.delete(env('MAILCHIMP_MEMBER_LIST_ID'), hash)
    except:
        client.captureException()


def send_invoice(invoice):
    # Initialize message on creation.
    message = EmailMessage('base/mail/invoice.html', {'invoice': invoice}, invoice.seller.email,
                           to=[invoice.buyer.email])

    message.attach_file(invoice.document.path)
    # Send message when ready. It will be rendered automatically if needed.
    message.send()


def invoice_open_ledegerentries(contact):
    from fablabadmin.base.models import LedgerEntry, MembershipInvoice, Expense, Invoice
    #check has open ledgerentries without invoices
    #excluding credits, membership and expenses
    entries = LedgerEntry.objects.not_instance_of(MembershipInvoice, Expense)\
        .filter(type='D', invoice__isnull=True, user=contact).all()
    if len(entries) == 0:
        return

    #check has an open draft invoice or create one
    invoice = Invoice.objects.filter(buyer=contact, draft=True, type='I').first()
    if invoice is None:
        invoice = Invoice.objects.create(buyer=contact, type='I')
        invoice.save()

    #add open entries to invoice
    for e in entries:
        e.invoice = invoice
        e.save()

    return invoice


def expense_open_expenses(contact):
    from fablabadmin.base.models import Expense, Invoice
    entries = Expense.objects.filter(invoice__isnull=True, user=contact).all()
    if len(entries) == 0:
        return

    #check has an open draft invoice or create one
    invoice = Invoice.objects.filter(seller=contact, draft=True, type='E').first()
    if invoice is None:
        invoice = Invoice.objects.create(seller=contact, type='E')
        invoice.save()

    #add open entries to invoice
    for e in entries:
        e.invoice = invoice
        e.save()

    return invoice
