import sqlite3
import os
from datetime import datetime

from isp_data_handlers import genDBInvoiceDCobj, genDBTransactionDCobj
from isp_db_helpers import fetchTransactionByID

con = sqlite3.connect(os.getenv("DB_NAME"))

con.execute('PRAGMA foreign_keys = ON')

cur = con.cursor()

def constructInvTransMatchedPairsReport(customer_id, afterDate):

  formattedDate = datetime.strptime(afterDate, '%Y-%m-%d')

  unpaid = []
  paid = []

  # running multi is a sorting list that contains the details for multi invocie transactions. With the parent transaction at the start,
  # followed by pairs of paid invoices and the dummy transaction that pays them. 
  runningMulti = []

  sql = f"SELECT * FROM INVOICES WHERE customer_id=? AND date_issued >= ?"

  cur.execute(sql, (customer_id, formattedDate))

  invoices = cur.fetchall()

  invoiceDCs = [genDBInvoiceDCobj(invoiceRaw) for invoiceRaw in invoices]
  
  multiInvoicePaymentDict = {}

  dummyIDMemo = 0

  for invoice in invoiceDCs:
    
    sql = f"SELECT * FROM TRANSACTIONS WHERE invoice_id = {invoice.invoice_id}"

    cur.execute(sql)

    transaction = cur.fetchall()

    if len(transaction) > 0:

      transactionDC = genDBTransactionDCobj(transaction[0])

      if len(runningMulti) > 0:

        # check if the incoming transaction is part of the current running multi list report (see line 18) if not appen
        if runningMulti[-1][1].parent_trans != transactionDC.parent_trans:

          paid.append(runningMulti)

          runningMulti = []

      if "*MULTIDUM*" in transactionDC.og_string:

        if dummyIDMemo == transactionDC.parent_trans:

          runningMulti.append([invoice, transactionDC])

          multiInvoicePaymentDict[transactionDC.parent_trans].append([invoice, transactionDC])

        else:

          parentTransaction = fetchTransactionByID(transactionDC.parent_trans, cur)

          parentTransactionDC = genDBTransactionDCobj(parentTransaction[0])

          runningMulti.append(parentTransactionDC)
          runningMulti.append([invoice, transactionDC])

          multiInvoicePaymentDict[transactionDC.parent_trans] = [[parentTransaction], [invoice, transactionDC]]

          dummyIDMemo = transactionDC.parent_trans
      
      else:

        paid.append([invoice, transactionDC])

    else:
      unpaid.append(invoice)

  for i in paid:
    print(i)

# constructInvTransMatchedPairsReport(3, '2023-10-01')



def constructUnmatchedTransactionReport(customerID, afterDate):
  
  formattedDate = datetime.strptime(afterDate, '%Y-%m-%d')

  sql = f"SELECT * FROM TRANSACTIONS WHERE customer_id = ? AND paid_on > ? AND invoice_id IS NULL"

  cur.execute(sql, (customerID, formattedDate))

  unMatchedTransactions = cur.fetchall()

  for i in unMatchedTransactions:
    print(i)


constructUnmatchedTransactionReport(10, '2020-10-01')

cur.close()
con.close()
