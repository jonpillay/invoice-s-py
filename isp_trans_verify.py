from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerAliases, fetchUnpaidInvoicesByCustomerBeforeDate, deleteTransactionRec, updateTransactionRec, updateInvoiceRec, addErrorTransactionToDB, deleteDummyTransactionsByParentID, addDummyNoteTransactionsToDB, fetchTransactionsByCustomerPaymentMethod
from isp_data_handlers import genInvoiceDCobj, prepMatchedTransforDB, genDBInvoiceDCobj, genDBTransactionDCobj
from isp_close_enough_prompts import openVerifyCloseEnoughtMatch

import tkinter as tk
import copy

  
def verifyTransactionAmount(transaction, invoice, tol, correctionAmount = 0):

  dif  = abs(invoice.amount - (transaction.amount - correctionAmount))
  
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

  """
  Checks if a none numbered incoming transaction (transaction) corrected by a past error (errorTransaction, dummyCorrectionTransaction)
  Now pays for an unpaid invoice (what is eventually candInvoice), eith exactly, or within a tolerance.

  Returns a list, if the match is exact, the list is composed of True bool and the matched invoice. If the match is not exact the list
  is composed of the difference, and the matched invoice.

  If no match is found, then bestMatch is returned as None, as it was initialised.

  """

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

      if dummyCorrectionTransaction.amount < 0:

        errorStr = f"Transaction also pays £{0-dummyCorrectionTransaction.amount} towards invoiceID {candInvoice.invoice_id}"

        updateTransactionRec(errorTransaction.id, "error_notes", errorStr, cur, con)

        updateTransactionRec(dummyCorrectionTransaction.id, "payment_method", "*SPLITDUM*", cur, con)

        updateInvoiceRec(errorTransaction.invoice_id, "error_notes", "", cur, con)

        updateInvoiceRec(errorTransaction.invoice_id, "error_flagged", "0", cur, con)

        prepMatchedTransforDB(transaction, candInvoice)

        transaction.error_flagged = 0

        transaction.error_notes = f"Transaction uses {0-dummyCorrectionTransaction.amount} from transID {errorTransaction.transaction_id} for invoiceID {candInvoice.invoice_id}"

        transactionTup = transaction.as_tuple()

        recordedTrans = addDummyNoteTransactionsToDB([transactionTup, con, cur])

        dummyErrorStr = f"Transaction is corrected by trans ID {recordedTrans}"

        updateTransactionRec(dummyCorrectionTransaction, "error_notes", dummyErrorStr, cur, con)

        matchedIDsMemo.append(candInvoice.invoice_id)

        return [True, candInvoice]
      
      else:
        
        errorStr = f"Transaction has £{0-dummyCorrectionTransaction.amount} from invoiceID {candInvoice.invoice_id}"

        updateTransactionRec(errorTransaction.id, "error_notes", errorStr, cur, con)

        updateTransactionRec(errorTransaction.id, "payment_method", "*SPLITDUM*", cur, con)

        updateInvoiceRec(errorTransaction.invoice_id, "error_notes", "", cur, con)

        updateInvoiceRec(errorTransaction.invoice_id, "error_flagged", "0", cur, con)

        prepMatchedTransforDB(transaction, candInvoice)

        transaction.error_flagged = 0

        transaction.error_notes = f"Transaction pays {0-dummyCorrectionTransaction.amount} towards transID {errorTransaction.transaction_id} for invoiceID {candInvoice.invoice_id}"

        transactionTup = transaction.as_tuple()

        recordedTrans = addDummyNoteTransactionsToDB([transactionTup], con, cur)

        dummyErrorStr = f"Transaction is corrected by trans ID {recordedTrans}"

        updateTransactionRec(dummyCorrectionTransaction, "error_notes", dummyErrorStr, cur, con)

        matchedIDsMemo.append(candInvoice.invoice_id)

        return [True, candInvoice]
      
    dif = getTransactionCorrectionNexusDif(transaction, candInvoice, 1, dummyCorrectionTransaction.amount)

    if dif != False:

      if bestMatch == None or dif < bestMatch[0]:

        bestMatch = [dif, candInvoice]
  
  return bestMatch




def checkIfTransactionListContainsErrorCorrections(root, correctedErrors, con, cur):

  """
  Takes in a list of the corrected errors from the incoming Transactions and checks against both past unpaid invoices
  and also past corrections. This checks if the current error from corrected errors is a correction on a past error or unpaid invoice.
  """

  errorCount = len(correctedErrors)

  reMatched = []
  stillErrors = []

  while len(reMatched) + len(stillErrors) < errorCount:

    for tupTransactionGroup in correctedErrors:

      transaction = tupTransactionGroup[0][0]
      invoice = tupTransactionGroup[0][1]
      dummyTransaction = tupTransactionGroup[1]

      # check if transaction overpayment is payment on unpaid invoices

      if dummyTransaction.amount < 0:

        candInvoices = fetchUnpaidInvoicesByCustomerBeforeDate(transaction.paid_on, transaction.customer_id, cur)

        candInvoiceDCs = [genInvoiceDCobj(DBinvoice) for DBinvoice in candInvoices]

        for candInvoice in candInvoiceDCs:

          if candInvoice.amount + dummyTransaction.amount == 0:
            
            # unpaid invoice has been found for the payment error

            # Need to delete the old dummy transaction from the DB

            deleteDummyTransactionsByParentID(transaction.transaction_id, con, cur)

            # create 2 new dummy transactions to represent the split
            # and pay for both of the matched invoices

            matchedInvoiceNumTransDummy = copy.deepcopy(transaction)

            matchedInvoiceNumTransDummy.transaction_id = None
            matchedInvoiceNumTransDummy.invoice_num = invoice.invoice_num
            matchedInvoiceNumTransDummy.amount = invoice.amount
            matchedInvoiceNumTransDummy.payment_method = f"*SPLITDUM* with {candInvoice.invoice_num}"
            matchedInvoiceNumTransDummy.invoice_id = invoice.invoice_id
            matchedInvoiceNumTransDummy.parent_trans = transaction.transaction_id

            matchedInvoiceCorrectionTransDummy = copy.deepcopy(transaction)

            matchedInvoiceCorrectionTransDummy.transaction_id = None
            matchedInvoiceCorrectionTransDummy.invoice_num = candInvoice.invoice_num
            matchedInvoiceCorrectionTransDummy.amount = candInvoice.amount
            matchedInvoiceCorrectionTransDummy.payment_method = f"*SPLITDUM* with {candInvoice.invoice_num}"
            matchedInvoiceCorrectionTransDummy.invoice_id = candInvoice.invoice_id
            matchedInvoiceCorrectionTransDummy.parent_trans = transaction.transaction_id

            # add the split dummy transactions to the DB which now pays for the two invoices

            addDummyNoteTransactionsToDB([matchedInvoiceNumTransDummy, matchedInvoiceCorrectionTransDummy], cur, con)

            # modify invoices' error_notes to note new split payment

            updateInvoiceRec(invoice.invoice_id, 'error_notes', f'Paid for with SPLIT transaction shares with invoice # {candInvoice.invoice_num}', cur, con)
            updateInvoiceRec(candInvoice.invoice_id, 'error_notes', f'Paid for with SPLIT transaction shares with invoice # {invoice.invoice_num}', cur, con)

            reMatched.append([transaction, invoice], candInvoice)

            correctedErrors.pop(0)

            break

        # start of check to see if transaction over payment is a correction for a group of invoices

        runningInvoiceTotal = 0
        invoiceGroup = []

        for currentInvoice in candInvoices:

          if runningInvoiceTotal > dummyTransaction.amount:
            break

          elif runningInvoiceTotal == dummyTransaction.amount:

            # transaction overpayment matches with total of group of unpaid invoices

            # delete the existing dummy transaction
            deleteDummyTransactionsByParentID(transaction.transaction_id, con, cur)

            # create dummy transactions for the invoices to be paid and update error_note on invoice

            dummyTransactionGroup = []

            for paidInvoice in invoiceGroup:

              dummyTransaction = copy.deepcopy(transaction)

              dummyTransaction.transaction_id = None
              dummyTransaction.invoice_num = paidInvoice.invoice_num
              dummyTransaction.amount = paidInvoice.amount
              dummyTransaction.payment_method = f"*SPLITDUM* from {transaction.transaction_id}"
              dummyTransaction.invoice_id = paidInvoice.invoice_id
              dummyTransaction.parent_trans = transaction.transaction_id

              # update invoice DB record
              updateInvoiceRec(paidInvoice.invoice_id, 'error_notes', f'Paid for with SPLITGROUP transaction', cur, con)

              dummyTransactionGroup.append(dummyTransaction)

            # upload the dummy transactions to the DB
            addDummyNoteTransactionsToDB(dummyTransactionGroup, cur, con)

            reMatched.append([transaction, invoice], invoiceGroup)

            correctedErrors.pop(0)

            break

          else:
            # if the total of the candInvoices that have been looped over is under and does not equal the overpayment
            # then add the current invoice amount to the running total and append the invoice into the invoice group
            runningInvoiceTotal += currentInvoice.amount
            invoiceGroup.append(currentInvoice)

      # fetch previous dummy transactions to see if the error on the current transaction is a correction on a previous transaction

      candDummyTransactions = fetchTransactionsByCustomerPaymentMethod("%CORDUM%", transaction.customer_id, cur)

      candDummyTransactionDCs = [genDBTransactionDCobj(transDC) for transDC in candDummyTransactions]

      for prevDummyTransaction in candDummyTransactionDCs:

        if prevDummyTransaction.amount + dummyTransaction.amount == 0:

          # if the incoming error amount added to the previous error equals 0, then it is assumed the incoming error is a correction on the previous error.

          """
          
          - What happens now?
          
          - The incoming transaction (transaction) needs an error note saying it corrects the previous transaction (take the parent_transaction_id from previousDummyTransaction).

          - The corrected transaction (grab ID from the prevDummyTransaction) needs an error note saying it is corrected by the incoming transaction

          - That previousDummyTransaction needs to be made a *SPLITCOR* (split correction), keeping it's details, but the with an error note saying it is
          - corrected by the incoming transaction (transaction).

          - The incoming transaction's already created dummy transaction (dummyTransaction) also needs to be updated with *SPLITCOR* and error noted that it 
          - corrects previousDummyTransaction and thus the previous transaction (previosuDummyTransaction's parent_transaction)

          - They can keep their original amounts. The prevDummyTransaction amount still relates to the error amount between the previous error transaction
          - and the Invoice. It is the same amount (but opposite in its positive/negative value) that corrects the incoming transaction/invoice pair.

          """

          # The incoming transaction (transaction) needs an error note saying it corrects the previous transaction (take the parent_transaction_id from previousDummyTransaction).

          updateTransactionRec(transaction.transaction_id, 'error_notes', f"error corrects *transID* {prevDummyTransaction.parent_trans}", cur, con)

          # The corrected transaction (grab ID from the prevDummyTransaction) needs an error note saying it is corrected by the incoming transaction

          updateTransactionRec(prevDummyTransaction.parent_trans, 'error_notes', f"error corrected by *transID* {transaction.transaction_id}", cur, con)

          # That previousDummyTransaction needs to be made a *SPLITCORRECTED*, keeping it's details, but the with an error note saying it is
          # corrected by the incoming transaction (transaction).

          updateTransactionRec(prevDummyTransaction.transaction_id, 'payment_method', "*SPLITCORRECTED*", cur, con)

          # The incoming transaction's already created dummy transaction (dummyTransaction) needs to be updated with *SPLITCORRECTION*

          updateTransactionRec(dummyTransaction.transaction_id, 'payment_method', "*SPLITCORRECTION*", cur, con)

          reMatched.append([transaction, invoice], prevDummyTransaction)
          correctedErrors.pop(0)
          break

      stillErrors.append(tupTransactionGroup)
      correctedErrors.pop(0)
      break

  return stillErrors, reMatched