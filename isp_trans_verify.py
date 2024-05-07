from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerAliases

import tkinter as tk
import math

def verifyTransactionDetails(transaction, invoice, cur):

  customerAliases = getCustomerAliases(cur, invoice.customer_id)

  if invoice.issued_to != transaction.paid_by or invoice.issued_to not in customerAliases:
    return f"Name Mismatch {transaction.paid_by} to {invoice.issued_to}"
  elif invoice.amount != transaction.amount:
    return invoice.amount - transaction.amount
  else:
    return True
  
def verifyTransactionAmount(transaction, invoice):

  tol = 1e-10
  dif  = abs(invoice.amount - transaction.amount)
  
  if dif < tol:
    return True
  else:
    print(invoice.amount - transaction.amount)
    return False

def verifyAlias(transaction, invoice):

  invoiceIDummy = None
  og_string = " ".join(transaction[5])

  frontendTransaction = Transaction(transaction[0][0], transaction[1], transaction[2], transaction[3], transaction[4], og_string, invoiceIDummy)
  frontendInvoice = Invoice(invoice[0], invoice[1], invoice[2], invoice[3], invoice[4])