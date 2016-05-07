# -*- coding: utf-8 -*-
import untangle
import datetime
from fablabadmin.accounting.models import BankTransaction


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
