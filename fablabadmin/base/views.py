from django.shortcuts import render

import cStringIO as StringIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from cgi import escape
from fablabadmin import settings
import os

from fablabadmin.base.models import Invoice


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


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("utf-8")), result, link_callback=link_callback, encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


def change_lang(request):
    return render(request, 'base/change_lang.html')


def invoice(request, id):
    invoice = Invoice.objects.prefetch_related('entries').get(id=id)
    #Retrieve data or whatever you need
    return render_to_pdf(
            'base/invoice.html',
            {
                'invoice': invoice
            }
        )



# MAILCHIMP Test
# from mailchimp3 import MailChimp
# def mailchimp():
#     client = MailChimp(MAILCHIMP_USERNAME, MAILCHIMP_KEY)
#     member = {
#         "email_address": "email",
#         "status": "subscribed",
#         "merge_fields": {
#             "FNAME": "test",
#             "LNAME": "test"
#         }
#     }
#     client.member.create(MAILCHIMP_LIST_ID, member)
#
#
#     import hashlib
#     hash = hashlib.md5('email'.lower()).hexdigest()
#     client.member.delete(MAILCHIMP_LIST_ID, hash)