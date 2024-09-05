from isp_db_helpers import fetchUnpaidInvoicesByCustomer
from isp_rematch_trans_prompt import openRematchTransactionPrompt
from isp_data_handlers import genInvoiceDCobj
from isp_db_helpers import addErrorTransactionToDB
from isp_dataframes import Transaction, Invoice

import tkinter as tk
import datetime
import os
import sqlite3

"""
Function to check error payments (transactions whose mathcing invoice, via number, doesn't match on payments)
against the customers unpaid invoices to see if a closer amount match can be made.

  Takes in => match payment errors - a list of transaction and invoices. match by num but not amount

  Returns => unPaidAmountMatch - list transactions that have been rematched via amount exactly to an unpaid invoice and the origianl invoice
  from the error payment
  stillErrorPayments => transactions and their invoice number matching invoice that has an amount error

"""

# matchPaymentErrorTestList = [[Transaction(amount=524.0, paid_on=datetime.datetime(2023, 4, 24, 0, 0), paid_by='CHOY HOUSE GREENWI', payment_method='BAC', og_string="24 Apr 2023 BAC CHOY HOUSE GREENWI, 5356 , FP 22/04/23 1346 , CBBPI1346371571821 524.00 KFS (KAH'S FOOD SERV 600537-24191612", transaction_id=None, invoice_num=5356, error_flagged=None, error_notes=None, high_invoice=None, customer_id=None, invoice_id=None, parent_trans=None), Invoice(invoice_num=5356, amount=468.1, date_issued=datetime.datetime(2023, 4, 13, 0, 0), issued_to='KATA', error_flagged=None, error_notes=None, invoice_id=626, customer_id=13)], [Transaction(amount=513.35, paid_on=datetime.datetime(2023, 4, 26, 0, 0), paid_by='VIETFOOD GROUP LTD', payment_method='BAC', og_string="26 Apr 2023 BAC VIETFOOD GROUP LTD, HOA 5389 , FP 26/04/23 1355 , 000000FT23116WQSKG 513.35 KFS (KAH'S FOOD SERV 600537-24191612", transaction_id=None, invoice_num=5389, error_flagged=None, error_notes=None, high_invoice=None, customer_id=None, invoice_id=None, parent_trans=None), Invoice(invoice_num=5389, amount=322.06, date_issued=datetime.datetime(2023, 4, 19, 0, 0), issued_to='HOA SEN', error_flagged=None, error_notes=None, invoice_id=659, customer_id=7)], [Transaction(amount=376.0, paid_on=datetime.datetime(2023, 5, 2, 0, 0), paid_by='JP FRESH FOO', payment_method='BAC', og_string="02 May 2023 BAC JP FRESH FOO , JP FRESH - 5404 , FP 01/05/23 2120 , 172748530212105001 376.00 KFS (KAH'S FOOD SERV 600537-24191612", transaction_id=None, invoice_num=5404, error_flagged=None, error_notes=None, high_invoice=None, customer_id=None, invoice_id=None, parent_trans=None), Invoice(invoice_num=5404, amount=367.0, date_issued=datetime.datetime(2023, 4, 21, 0, 0), issued_to='J.P FRESH', error_flagged=None, error_notes=None, invoice_id=673, customer_id=2)], [Transaction(amount=729.0, paid_on=datetime.datetime(2023, 5, 9, 0, 0), paid_by='JP FRESH FOO', payment_method='BAC', og_string="09 May 2023 BAC JP FRESH FOO , JP FRESH - 5445 , FP 08/05/23 0930 , 577475920390805001 729.00 KFS (KAH'S FOOD SERV 600537-24191612", transaction_id=None, invoice_num=5445, error_flagged=None, error_notes=None, high_invoice=None, customer_id=None, invoice_id=None, parent_trans=None), Invoice(invoice_num=5445, amount=526.5, date_issued=datetime.datetime(2023, 4, 28, 0, 0), issued_to='J.P FRESH', error_flagged=None, error_notes=None, invoice_id=712, customer_id=2)], [Transaction(amount=1105.66, paid_on=datetime.datetime(2023, 5, 23, 0, 0), paid_by='VIET HUB 53 LTD', payment_method='BAC', og_string="23 May 2023 BAC VIET HUB 53 LTD , 5547 , FP 23/05/23 0909 , PMU5S2PJOBOLM1AZ83 1105.66 KFS (KAH'S FOOD SERV 600537-24191612", transaction_id=None, invoice_num=5547, error_flagged=None, error_notes=None, high_invoice=None, customer_id=None, invoice_id=None, parent_trans=None), Invoice(invoice_num=5547, amount=926.46, date_issued=datetime.datetime(2023, 5, 17, 0, 0), issued_to='BANG BANG', error_flagged=None, error_notes=None, invoice_id=808, customer_id=14)], [Transaction(amount=405.21, paid_on=datetime.datetime(2023, 6, 26, 0, 0), paid_by='VIETFOOD GROUP LTD', payment_method='BAC', og_string="26 Jun 2023 BAC VIETFOOD GROUP LTD, HOA 5746 , FP 24/06/23 1505 , 000000FT23174S5F9T 405.21 KFS (KAH'S FOOD SERV 600537-24191612", transaction_id=None, invoice_num=5746, error_flagged=None, error_notes=None, high_invoice=None, customer_id=None, invoice_id=None, parent_trans=None), Invoice(invoice_num=5746, amount=379.79, date_issued=datetime.datetime(2023, 6, 22, 0, 0), issued_to='HOA SEN', error_flagged=None, error_notes=None, invoice_id=1003, customer_id=7)], [Transaction(amount=301.99, paid_on=datetime.datetime(2023, 6, 26, 0, 0), paid_by='VIETFOOD GROUP LTD', payment_method='BAC', og_string="26 Jun 2023 BAC VIETFOOD GROUP LTD, HOA 5752 , FP 24/06/23 1506 , 000000FT23174N5ML7 301.99 KFS (KAH'S FOOD SERV 600537-24191612", transaction_id=None, invoice_num=5752, error_flagged=None, error_notes=None, high_invoice=None, customer_id=None, invoice_id=None, parent_trans=None), Invoice(invoice_num=5752, amount=291.22, date_issued=datetime.datetime(2023, 6, 23, 0, 0), issued_to='HOA SEN', error_flagged=None, error_notes=None, invoice_id=1009, customer_id=7)]]

# con = sqlite3.connect(os.getenv("DB_NAME"))

# con.execute('PRAGMA foreign_keys = ON')

# cur = con.cursor()

def checkPaymentErrorAgainstUnpaidInvoices(cur, con, root, matchPaymentErrors):


  reMatched = []
  stillMatchPaymentError = []

  for paymentErrorPair in matchPaymentErrors:

    transaction = paymentErrorPair[0]
    invoice = paymentErrorPair[1]

    candInvoices = fetchUnpaidInvoicesByCustomer(invoice.customer_id, cur)

    candInvoiceDCs = [genInvoiceDCobj(candInvoice) for candInvoice in candInvoices]

    matched = False

    for candInvoiceDC in candInvoiceDCs:

      if candInvoiceDC.amount == transaction.amount:

        reMatchVerifyBool = tk.BooleanVar()

        openRematchTransactionPrompt(root, transaction, invoice, candInvoiceDC, reMatchVerifyBool)

        if reMatchVerifyBool.get() == True:

          transaction.error_notes = f"*INVOICE NUM CORRECTED* from {invoice.invoice_num}"
          transaction.invoice_num = candInvoiceDC.invoice_num
          transaction.invoice_id = candInvoiceDC.invoice_id
          transaction.error_flagged = 0
          transaction.customer_id = candInvoiceDC.customer_id
          transaction.invoice_id = candInvoiceDC.invoice_id

          addErrorTransactionToDB(transaction.as_tuple(), con, cur)

          resultList = [transaction, invoice, candInvoiceDC]

          reMatched.append(resultList)

          matched = True

          break

        else:

          stillMatchPaymentError.append(paymentErrorPair)

    if not matched:
      stillMatchPaymentError.append(paymentErrorPair)

  return reMatched, stillMatchPaymentError


# checkPaymentErrorAgainstUnpaidInvoices(cur, con, root, matchPaymentErrorTestList)

# cur.close()
# con.close()