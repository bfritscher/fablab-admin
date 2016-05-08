import thread
from django import forms
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json
from fablabadmin.base.models import Invoice
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest

from .models import BankTransaction
from .utils import parse_CAMT, ccvshop_parse_order


class UploadFileForm(forms.Form):
    file = forms.FileField()


@permission_required('accounting.change_banktransaction')
def consolidation(request):
    title = 'Consolidation'
    # Handle new file upload
    if request.method == 'POST' and 'file' in request.FILES:
        try:
            parsed = parse_CAMT(request.FILES['file'].read())
            messages.success(request, parsed)
        except Exception as e:
            messages.error(request, "error %s" % e)

    # consolidate
    if request.method == 'POST' and 'invoice_id' in request.POST and 'bt_id' in request.POST:
        invoice = Invoice.objects.get(pk=request.POST['invoice_id'])
        bt = BankTransaction.objects.get(pk=request.POST['bt_id'])
        bt.invoice = invoice
        bt.save()
        invoice.paid = bt.booking_date
        invoice.save()

        messages.success(request, "closed %s with %s" % (invoice, bt))

    form = UploadFileForm()

    # Display non-consolidated items
    bts = BankTransaction.objects.filter(invoice__isnull=True, counterpart_account__isnull=True)

    # find potential matches
    for bt in bts:
        # unpaid invoices before date of bt involving same amount and match any of:
        potential_invoices = Invoice.objects.filter(date__lte=bt.booking_date, paid__isnull=True,
                                                    type="I" if bt.type == BankTransaction.CREDIT else "E")
        # total not yet stored in db :-( and need poymorphic aggregation support
        bt.potential_invoices = [i for i in potential_invoices if i.total == bt.amount]
        # TODO: more filtering
        # - lastname
        # - account
        # - invoice number

    return render(request, 'accounting/consolidation.html', locals())

@csrf_exempt
def ccvshop_order_webhook(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            # thread for processing because hook has to respond < 1s
            # TODO: should be moved to a task queue system
            thread.start_new_thread(ccvshop_parse_order, (json_data['id'],))
        except KeyError:
            HttpResponseServerError("Malformed data!")

        return HttpResponse(status=200)

    if request.method == 'GET' and 'id' in request.GET:
        ccvshop_parse_order(request.GET['id'])

    return HttpResponseBadRequest()