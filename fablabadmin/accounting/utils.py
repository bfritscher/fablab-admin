# -*- coding: utf-8 -*-
import untangle
import hmac
import hashlib
import datetime
import requests

from fablabadmin.accounting.models import BankTransaction
from fablabadmin.base.models import Contact, Invoice, LedgerEntry, EventRegistration, Event, ContactStatus
from fablabadmin.settings import CCVSHOP_DOMAIN, CCVSHOP_PRIVATE_KEY, CCVSHOP_PUBLIC_KEY


def parse_CAMT(f):
    doc = untangle.parse(f)
    stmt = doc.Document.BkToCstmrStmt.Stmt
    iban = stmt.Acct.Id.IBAN.cdata
    date_from = stmt.Bal[0].Dt.Dt.cdata
    date_to = stmt.Bal[1].Dt.Dt.cdata
    n = 0
    for e in stmt.Ntry:
        transaction_id = e.AcctSvcrRef.cdata
        bt, created = BankTransaction.objects.get_or_create(transaction_id=transaction_id, iban=iban,
            defaults={
                'currency': e.Amt['Ccy'],
                'amount': e.Amt.cdata,
                'type': e.CdtDbtInd.cdata, # 'CRDT' or 'DBIT'
                'booking_date': datetime.datetime.strptime(e.BookgDt.Dt.cdata, "%Y-%m-%d"),
                'raw_text': e.AddtlNtryInf.cdata
            })
        if created:
            n += 1
    return u"Parsed %s, from: %s to: %s with %s new entries." % (iban, date_from, date_to, n)


def ccvshop_parse_order(order_id):
    order = ccvshop_call_api("/api/rest/v1/orders/%s" % order_id)

    # check that order has not already been imported
    if Invoice.objects.filter(external_reference=order['id']).exists():
        # TODO: support update?
        return

    # find or create contact
    first_name = order['customer']['billingaddress']['first_name'].strip()
    last_name = order['customer']['billingaddress']['last_name'].strip()
    postal_code = order['customer']['billingaddress']['zipcode']

    def find_contact():
        contacts = Contact.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name)
        if len(contacts) == 1:
            return contacts[0]
        if len(contacts) > 1:
            # check with zipcode
            filtered = [c for c in contacts if c.postal_code == postal_code]
            if len(filtered) == 1:
                return filtered[0]
            # TODO: oder matching test?
        return None

    contact = find_contact()
    if contact is None:
        contact_status, created = ContactStatus.objects.get_or_create(name='shop')
        contact = Contact()
        contact.status = contact_status
        contact.first_name = first_name
        contact.last_name = last_name
        contact.postal_code = postal_code
        contact.city = order['customer']['billingaddress']['city']
        contact.address = order['customer']['billingaddress']['address_line_1']
        contact.country = order['customer']['billingaddress']['country']
        contact.phone = order['customer']['billingaddress']['telephone']
        contact.email = order['customer']['email']
        contact.save()

    # create invoice
    # order.status   ?? --> set paid?

    invoice = Invoice()
    invoice.external_reference = order['id']
    invoice.title = "shop %s" % order['ordernumber']
    invoice.buyer = contact
    invoice.date = datetime.datetime.strptime(order['create_date'], "%Y-%m-%dT%H:%M:%SZ")
    invoice.manual_total = order['total_price']
    # set false before publish to not send e-mail
    invoice.draft = False
    invoice.save()

    # create invoice ledger_entries or event_registrations
    orderrows = ccvshop_call_api("/api/rest/v1/orders/%s/orderrows" % order_id)

    for item in orderrows['items']:
        e = LedgerEntry()
        # find Event by item.product_number
        event = Event.objects.filter(slug=item['product_number']).first()
        if event:
            e = EventRegistration()
            e.event = event

        e.title = item['product_name']
        e.quantity = 1
        e.unit_price = item['total_price']
        e.description = "\n".join(["%s: %s" % (a['option_name'], a['value_name']) for a in item['attributes']])
        e.date = invoice.date
        e.user = contact
        e.invoice = invoice
        e.external_reference = item['id']
        e.save()

    invoice.publish()


def ccvshop_call_api(api_uri, method="GET", data=""):
    ts = datetime.datetime.now().isoformat("T")  # UTC 2016-05-06T14:07:25Z
    hash_string = "|".join([CCVSHOP_PUBLIC_KEY, method, api_uri, data, ts])
    hash = hmac.new(CCVSHOP_PRIVATE_KEY, hash_string, hashlib.sha512).hexdigest()
    headers = {"x-date": ts, "x-hash": hash, "x-public": CCVSHOP_PUBLIC_KEY}
    r = requests.get(CCVSHOP_DOMAIN + api_uri, headers=headers)
    return r.json()
