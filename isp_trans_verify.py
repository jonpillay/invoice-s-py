from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerAliases, fetchUnpaidInvoicesByCustomerBeforeDate, deleteTransactionRec, updateTransactionRec, updateInvoiceRec, addErrorTransactionToDB
from isp_data_handlers import genInvoiceDCobj, prepMatchedTransforDB
from isp_close_enough_prompts import openVerifyCloseEnoughtMatch

import tkinter as tk

  
def verifyTransactionAmount(transaction, invoice, tol, correctionAmount = 0):

  dif  = abs(invoice.amount - (transaction.amount - correctionAmount))
  
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
    
  """

  Need a new transaction that only takes in the invoice and transaction, which match by number and name. 
  This is to be used in the first resolve payment errors to see if the transaction error can be matched with
  any past invoices' amount or error correction. This needs to be run before (and feed) resolvePaymentErrors.
  Taking in the

  checkIfTransactionErrorIsCorrection needs to be rewritten to take in only the error amount and 

  """

def getTransactionCorrectionNexusDif(transaction, invoice, tol, correctionAmount = 0):

  dif  = abs(invoice.amount - (transaction.amount - correctionAmount))
  
  if dif <= tol:
    return dif
  else:
    return False
  


def checkIfNoNumTransactionErrorIsCorrection(transaction, errorTransaction, dummyCorrectionTransaction, cur, con):

  # needs to return only the matched invoice, the rest of the information is already present in the calling function

  candInvoices = fetchUnpaidInvoicesByCustomerBeforeDate(transaction.paid_on, transaction.customer_id, cur)

  candInvoiceDCs = [genInvoiceDCobj(invoice) for invoice in candInvoices]

  # needs completion with each if statement if evaluating to True tieing the current transaction to the matched invoice
  # and deleting the old dummy transaction and noting on all 4 of the invoices/transactions the cross payment

  # should possibly be rewrittent to allow user to choose between matched invoices, also means that backend upload functions
  # for perfectly matched paris should be performed here

  matchedIDsMemo = []

  bestMatch = None

  for candInvoice in candInvoiceDCs:

    if candInvoice.invoice_id in matchedIDsMemo:
      continue

    if verifyTransactionAmount(transaction, candInvoice, 0.1, dummyCorrectionTransaction.amount):
      
      # amounts match exactly (within flaoting point error). Assume that the under/overpayment was a correction on the previous invoice

      # Still needs to be rewritten if the amount is > 0

      if dummyCorrectionTransaction.amount < 0:

        errorStr = f"Transaction also pays £{0-dummyCorrectionTransaction.amount} towards invoiceID {candInvoice.invoice_id}"

        updateTransactionRec(errorTransaction.id, "error_notes", errorStr)

        updateInvoiceRec(errorTransaction.invoice_id, "error_notes", "")

        updateInvoiceRec(errorTransaction.invoice_id, "error_flagged", "0")

        prepMatchedTransforDB(transaction, candInvoice)

        transaction.error_flagged = 0

        transaction.error_notes = f"Transaction uses {0-dummyCorrectionTransaction.amount} from transID {errorTransaction.transaction_id} for invoiceID {candInvoice.invoice_id}"

        transactionTup = transaction.as_tuple()

        print(transactionTup)

        deleteTransactionRec(dummyCorrectionTransaction.id, con, cur)

        print("exact match")

        matchedIDsMemo.append(candInvoice.invoice_id)

        return [True, candInvoice]
      
      else:
        
        errorStr = f"Transaction has £{0-dummyCorrectionTransaction.amount} from invoiceID {candInvoice.invoice_id}"

        updateTransactionRec(errorTransaction.id, "error_notes", errorStr)

        updateInvoiceRec(errorTransaction.invoice_id, "error_notes", "")

        updateInvoiceRec(errorTransaction.invoice_id, "error_flagged", "0")

        prepMatchedTransforDB(transaction, candInvoice)

        transaction.error_flagged = 0

        transaction.error_notes = f"Transaction pays {0-dummyCorrectionTransaction.amount} towards transID {errorTransaction.transaction_id} for invoiceID {candInvoice.invoice_id}"

        transactionTup = transaction.as_tuple()

        print(transactionTup)

        deleteTransactionRec(dummyCorrectionTransaction.id, con, cur)

        print("exact match")

        matchedIDsMemo.append(candInvoice.invoice_id)

        return [True, candInvoice]
      
    dif = getTransactionCorrectionNexusDif(transaction, candInvoice, 15, dummyCorrectionTransaction.amount)

    if dif != False:

      if bestMatch == None or dif < bestMatch[0]:
        print(f"This is the {dif}")
        bestMatch = [dif, candInvoice]

      # matchVerifiedBool = tk.BooleanVar()

      # openVerifyCloseEnoughtMatch(root, transaction, candInvoice, matchVerifiedBool)

      # if matchVerifiedBool.get() == True:

      #   return candInvoice.invoice_id
  
  return bestMatch


def checkIfTransactionListContainsErrorCorrections(root, correctedErrors, con, cur):

  for tupTransactionGroup in correctedErrors:

    transaction = tupTransactionGroup[0][0]
    invoice = tupTransactionGroup[0][1]
    dummyTransaction = tupTransactionGroup[1]

    # check if transaction over - payment is payment on unpaid invoices

    if dummyTransaction.amount < 0:

      candInvoices = fetchUnpaidInvoicesByCustomerBeforeDate(transaction.paid_on, transaction.customer_id, cur)

      for candInvoice in candInvoices:

        if candInvoice.amount + dummyTransaction.amount == 0:
          
          # unpaid invoice has been found for the payment error

          # Need to delete the old dummy transaction from the DB and create 2 new dummy transactions to represent the split
          # and pay for both of the matched invoices

          pass
        




  # will be passed the output from resolvePaymentErrors for transactions that have been corrected.
  # A list of Tuples, the first element being a list of the original Transaction and the invoice
  # it now matches to. The second element in the tuple is the dummy correction Transaction created by
  # resolvePaymentErrors.

  # The function not only has to check database for invoice/transaction pair errors, but also first
  # itself.

  # It should perform corrections in loop to avoid candidate transactions being pulled twice

  pass