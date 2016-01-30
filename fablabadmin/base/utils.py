from mailchimp3 import MailChimp
from django.template.loader import get_template
import hashlib
import cStringIO as StringIO
from xhtml2pdf import pisa
from fablabadmin import settings
import os
import environ
from mail_templated import EmailMessage

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
        mailchimp_client.member.create(env('MAILCHIMP_MEMBER_LIST_ID'), member)
    except:
        pass
    try:
        mailchimp_client.member.create(env('MAILCHIMP_NEWSLETTER_LIST_ID'), member)
    except:
        pass


def mailchimp_remove(contact):
    hash = hashlib.md5(contact.email.lower()).hexdigest()
    try:
        mailchimp_client.member.delete(env('MAILCHIMP_MEMBER_LIST_ID'), hash)
    except:
        pass


def send_invoice(invoice):
    # Create new empty message.
    message = EmailMessage()

    # Initialize message on creation.
    message = EmailMessage('base/mail/invoice.html', {'invoice': invoice}, invoice.seller.email,
                           to=[invoice.buyer.email])

    message.attach_file(invoice.document.path)
    # Send message when ready. It will be rendered automatically if needed.
    message.send()