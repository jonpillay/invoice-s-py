from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerAliases
from isp_popup_window import openTransactionAliasPrompt

from tkinter import *

def verifyTransactionDetails(transaction, invoice, cur):

  customerAliases = getCustomerAliases(cur, invoice.customer_id)

  if invoice.issued_to != transaction.paid_by or invoice.issued_to not in customerAliases:
    return f"Name Mismatch {transaction.paid_by} to {invoice.issued_to}"
  elif invoice.amount != transaction.amount:
    return invoice.amount - transaction.amount
  else:
    return True
  
def verifyAlias(transaction, invoice):

  invoiceIDummy = None
  og_string = " ".join(transaction[5])

  frontendTransaction = Transaction(transaction[0][0], transaction[1], transaction[2], transaction[3], transaction[4], og_string, invoiceIDummy)
  frontendInvoice = Invoice(invoice[0], invoice[1], invoice[2], invoice[3], invoice[4])

def resolveNameMismatches(root, cur, conn, matchNameErrors):

  errorCount = len(matchNameErrors)

  unMatchable = []
  nameResolved = []

  for error in matchNameErrors:

      aliasBool = BooleanVar()

      print(aliasBool.get())
      
      transaction = error[0]
      invoice = error[1]

      openTransactionAliasPrompt(root, invoice, transaction, aliasBool)

      print(aliasBool.get())

  # while len(nameResolved) + len(unMatchable) < errorCount:
  #   for error in matchNameErrors:
  #     print(error)
  #     break
      # Prompt user if the name mismatch is an error

      # Prompt should set some TKVars

      # If alias is found, should add alias to DB and rerun check on all elements in matchNameErrors list
      # First building a new aliases dict with result and resolving for that.

      # If the alias is not a match then the error pair should be put into unMatchable