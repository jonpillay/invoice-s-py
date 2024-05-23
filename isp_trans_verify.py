from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerAliases

import tkinter as tk

  
def verifyTransactionAmount(transaction, invoice, tol):

  dif  = abs(invoice.amount - transaction.amount)
  
  if dif <= tol:
    return True
  else:
    return False


def verifyTransactionDetails(transaction, invoice, cur):

  customerAliases = getCustomerAliases(cur, invoice.customer_id)

  amountVerified = verifyTransactionAmount(transaction, invoice, 0.01)

  if amountVerified == True and invoice.issued_to != transaction.paid_by or amountVerified == True and invoice.issued_to not in customerAliases:
    return f"Name Mismatch {transaction.paid_by} to {invoice.issued_to}"
  elif amountVerified == False:
    return invoice.amount - transaction.amount
  else:
    return True

def verifyAlias(transaction, invoice):

  invoiceIDummy = None
  og_string = " ".join(transaction[5])

  frontendTransaction = Transaction(transaction[0][0], transaction[1], transaction[2], transaction[3], transaction[4], og_string, invoiceIDummy)
  frontendInvoice = Invoice(invoice[0], invoice[1], invoice[2], invoice[3], invoice[4])