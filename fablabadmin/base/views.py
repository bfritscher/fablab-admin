from django.shortcuts import render
from django.http import HttpResponse
from fablabadmin.base.models import Invoice
from fablabadmin.base.utils import make_pdf


def render_to_pdf(template_src, context_dict):
    try:
        result = make_pdf(template_src, context_dict)
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    except Exception as e:
        return HttpResponse('We had some errors<pre>%s</pre>' % e)


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


def invoice_html(request, id):
    invoice = Invoice.objects.prefetch_related('entries').get(id=id)
    #Retrieve data or whatever you need
    return render(request,
            'base/invoice.html',
            {
                'invoice': invoice
            }
        )


def mail_template(request, id):
    invoice = Invoice.objects.prefetch_related('entries').get(id=id)
    return render(request, 'base/mail/invoice.html',{
                'invoice': invoice
            })