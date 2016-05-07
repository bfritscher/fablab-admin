from django import forms
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from fablabadmin.accounting.models import BankTransaction
from fablabadmin.accounting.utils import parse_CAMT
from django.contrib import messages
from django.contrib.auth.models import User
from fablabadmin.base.models import Invoice


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
