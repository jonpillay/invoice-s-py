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