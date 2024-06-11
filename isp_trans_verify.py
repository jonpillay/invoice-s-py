from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerAliases, fetchUnpaidInvoicesByCustomerBeforeDate
from isp_data_handlers import genInvoiceDCobj
from isp_close_enough_prompts import openVerifyCloseEnoughtMatch

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

  # print(transaction.invoice_num)
  # print(invoice.invoice_num)
  # print("")

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


  """
    Need a verfifyCorrectionPayment function to check if the under/over payment is correct with current transaction.
    Performed by taking the amount on the dummy transaction and minusing it from the transaction amount and then doing
    an amount check against outstanding invoices. If a match is found, dummy transaction is removed and each transaction/invoice
    pair in matched together.
    
  """
    

def checkIfTransactionErrorIsCorrection(root, transaction, dummyCorrectionTransaction, tol, cur):

  correctedAmount = transaction.amount - dummyCorrectionTransaction.amount

  candInvoices = fetchUnpaidInvoicesByCustomerBeforeDate(transaction.paid_on, transaction.customer_id, cur)

  candInvoiceDCs = [genInvoiceDCobj(invoice) for invoice in candInvoices]

  # needs completion with each if statement if evaluating to True tieing the current transaction to the matched invoice
  # and deleting the old dummy transaction and noting on all 4 of the invoices/transactions the cross payment

  # should possibly be rewrittent to allow user to choose between matched invoices, also means that backend upload functions
  # for perfectly matched paris should be performed here

  for candInvoice in candInvoiceDCs:

    if verifyTransactionAmount(transaction, candInvoice, 0):
      
      return candInvoice.invoice_id

    if verifyTransactionAmount(transaction, candInvoice, 10):
      
      matchVerifiedBool = tk.BooleanVar()

      openVerifyCloseEnoughtMatch(root, transaction, candInvoice, matchVerifiedBool)

      if matchVerifiedBool.get() == True:

        return candInvoice.invoice_id