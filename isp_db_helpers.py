import sqlite3


def getInvoiceNumsIDs(cur):

  invoiceIDnumsSQL = "SELECT id invoice_num from INVOICES"

  cur.execute(invoiceIDnumsSQL)

  invoiceNumsIDs = cur.fetchall()

  return [invoice[0] for invoice in invoiceNumsIDs]

def transactionInvoiceMatcher(invoiceNumber, cur):

  sql = "SELECT id, invoice_num, amount, company_name FROM INVOICES WHERE invoice_num=?"

  cur.execute(sql, str(invoiceNumber))

  invoice = cur.fetchall()

  return invoice
