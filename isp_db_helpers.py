import sqlite3


def getInvoiceNumsIDs(cur):

  invoiceIDnumsSQL = "SELECT id invoice_num from INVOICES"

  cur.execute(invoiceIDnumsSQL)

  invoiceNumsIDs = cur.fetchall()

  return [invoice[0] for invoice in invoiceNumsIDs]

def fetchInvoiceByNum(invoiceNumber, cur):

  sql = f"SELECT id, invoice_num, amount, company_name FROM INVOICES WHERE invoice_num={invoiceNumber}"

  cur.execute(sql)

  invoice = cur.fetchall()

  return invoice

def addTransactionsToDB(transactionsTuples, cur):

  sql = "INSERT INTO TRANSACTIONS (invoice_num, amount, paid_on, company_name, payment_method, og_string, invoice_id) VALUES (?, ?, ?, ?, ?, ?, ?)"

  cur.executemany(sql, transactionsTuples)