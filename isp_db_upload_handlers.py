import tkinter as tk
import csv
import sqlite3
import os
import re
from datetime import datetime

import json

from isp_csv_helpers import cleanTransactionRaw, cleanInvoiceListRawGenCustomerList
from isp_trans_verify import verifyTransactionDetails, verifyAlias, verifyTransactionAmount, checkIfTransactionListContainsErrorCorrections
from isp_db_helpers import getInvoiceNumsIDs, fetchInvoiceByNum, fetchUnpaidInvoiceByNum, addTransactionsToDB, addNewCustomersToDB, getDBInvoiceNums, getCustomerNamesIDs, resolveNewCustomersDB, addCashInvoicesAndTransactions, addInvoicesToDB, addDummyTransactionsToDB, addCorrectedTransactionPairsDB, addParentErrorTransactionsToDB, addNoMatchTransactionsToDB
from isp_data_handlers import constructCustomerAliasesDict, constructCustomerIDict, prepInvoiceUploadList, genInvoiceDCobj, genTransactionDCobj, genMultiTransactionDCobj, prepMatchedTransforDB, genMultiTransactions, reMatchPaymentErrors, genNoNumTransactionDCobj
from isp_resolvers import resolveNameMismatches, resolvePaymentErrors, resolveMultiInvoiceTransactions, resolveNoMatchTransactions
from isp_multi_invoice_prompt import openSelectBetweenInvoices
from isp_error_payment_check import checkPaymentErrorAgainstUnpaidInvoices

from isp_results_printer import print_transaction_upload_results

from isp_final_resolver import final_resolver

from isp_dataframes import Transaction


def handleInvoiceUpload(root, filename):

  conn = sqlite3.connect(os.getenv("DB_NAME"))

  conn.execute('PRAGMA foreign_keys = ON')

  cur = conn.cursor()

  with open(filename) as csv_file:
    CSVreader = csv.reader(csv_file)

    entriesList = []

    invoiceNumsList = getDBInvoiceNums(cur)

    for entry in CSVreader:
      try: 
        if int(entry[0]) not in invoiceNumsList:
          entriesList.append(entry)
      except:
        continue
    
  cleanedInvoices, customers = cleanInvoiceListRawGenCustomerList(entriesList)

  dbCustomers = getCustomerNamesIDs(cur)

  alisesDict = constructCustomerAliasesDict(cur, dbCustomers)

  resolveNewCustomersDB(root, customers, alisesDict, cur, conn)

  updatedDBCustomers = getCustomerNamesIDs(cur)

  updatedAliasesDict = constructCustomerAliasesDict(cur, updatedDBCustomers)

  customerIDict = constructCustomerIDict(cur, updatedAliasesDict)

  invoiceUploadTups, cashInvoiceUploadTups = prepInvoiceUploadList(cleanedInvoices, customerIDict)

  addCashInvoicesAndTransactions(cashInvoiceUploadTups, cur, conn)

  addInvoicesToDB(invoiceUploadTups, cur)

  conn.commit()

  cur.close()
  conn.close()




def handleTransactionUpload(root, filename):

  unsortedCompRec = []
  unsortedIncompRec = []
  unsortedMultiRec = []

  with open(filename) as csv_file:
    CSVreader = csv.reader(csv_file)

    count = 0

    for entry in CSVreader:
      
      try:
        datetime.strptime(entry[0].strip(), '%d %b %Y')
        count += 1
      except:
        continue

      cleanedEntry = cleanTransactionRaw(entry)

      """ Check to see if the Transaction entry has one, numerous, or no invoice number matches """
      
      if len(cleanedEntry[0]) == 0:
        transDC = genNoNumTransactionDCobj(cleanedEntry)
        transDC.error_notes = "No Invoice Number Attatched"
        unsortedIncompRec.append(transDC)
      elif len(cleanedEntry[0]) == 1:
        num = cleanedEntry[0][0]
        cleanedEntry[0] = num
        transDC = genTransactionDCobj(cleanedEntry)
        unsortedCompRec.append(transDC)
      else:
        transactionDC = genMultiTransactionDCobj(cleanedEntry)
        unsortedMultiRec.append(transactionDC)

  # Sort lists by date_paid

  # comprec is transactions with a single invoice number
  compRec = sorted(unsortedCompRec, key=lambda transaction:transaction.paid_on)

  # incomprec are transactions with now invoice nuumber
  incompRec = sorted(unsortedIncompRec, key=lambda transaction:transaction.paid_on)

  # multirec are transactions with 2 or more invoice numbers
  multiRec = sorted(unsortedMultiRec, key=lambda transaction:transaction.paid_on)


  print("This is the transaction count at line 117")
  print(len(compRec)+len(incompRec)+len(multiRec))

  upLoadedPairs = []

  # working lists

  matches = []

  matchPaymentError = []
  matchNameError = []

  matchedSingles = ['matchedSingles', []]

  con = sqlite3.connect(os.getenv("DB_NAME"))

  con.execute('PRAGMA foreign_keys = ON')

  cur = con.cursor()

  for transaction in compRec:

    invoiceNum = transaction.invoice_num

    # fetch invoice via number on transaction

    invoice = fetchInvoiceByNum(invoiceNum, cur)

    if len(invoice) == 0:
      transaction.error_notes = "No Match For Invoice Number Found."
      incompRec.append(transaction)
    else:
      invoiceClean = [el for el in invoice[0] if el != None]
      invoice = genInvoiceDCobj(invoiceClean)
      matches.append([transaction, invoice])


  for transaction, invoice in matches:

    detailMatch = verifyTransactionDetails(transaction, invoice, cur)

    if type(detailMatch) == float:
      matchPaymentError.append([transaction, invoice])
    elif type(detailMatch) == str:
      matchNameError.append([transaction, invoice])
    elif detailMatch == True:
      prepMatchedTransforDB(transaction, invoice)
      matchPair = (transaction, invoice)
      matchedSingles[1].append(matchPair)
    else:
      print("cannot match")


  # resolve name mismatches
  nameResolved, namesUnresolved, resolvedNamePaymentErrors = resolveNameMismatches(root, cur, con, matchNameError)

  incompRec.extend(namesUnresolved)

  matchPaymentError.extend(resolvedNamePaymentErrors)

  matchedSingles[1].extend(nameResolved)

  transactionUpload = [payPair[0].as_tuple() for payPair in matchedSingles[1]]

  transactionUploadObjs = [payPair[0] for payPair in matchedSingles[1]]

  addTransactionsToDB(transactionUpload, cur)

  con.commit()

  upLoadedPairs.extend(matchedSingles)

  # Start of multi-invoice transaction verification.
 
  multiVerified, multiErrorFlaggedList, multiInvoiceErrorsList = resolveMultiInvoiceTransactions(root, cur, con, multiRec)

  # upLoad parent transaction and gen multi dummy transactions.

  dummyTransactions, uploadedMultiTransactionPairsList = genMultiTransactions(multiVerified, cur, con)

  dummyTransactionTuples = [dummyTrans.as_tuple() for dummyTrans in dummyTransactions]

  addDummyTransactionsToDB(dummyTransactionTuples, cur, con)

  # need to upload the incomng multi transactions from multiErrors and also multi flagged - both should have error notes
  # multi error flagged are lists => [incoming transaction, invoices supposed to pay for] 
  # multi error elements are tuples => (incoming transaction, invoices supposed to pay for)

  multiErrorFlaggedTuples = [errorFlagged.as_tuple() for errorFlagged in multiErrorFlaggedList]
  multiInvoiceErrorTuples = [multiInvoiceError.as_tuple() for multiInvoiceError in multiInvoiceErrorsList]


  addParentErrorTransactionsToDB(multiErrorFlaggedTuples, cur, con)
  addParentErrorTransactionsToDB(multiInvoiceErrorTuples, cur, con)


  con.commit()

  uploadedMultiTransactionPairs = ['uploadedMultiTransactionPairs', uploadedMultiTransactionPairsList]

  multiErrorFlagged = ['multiErrorFlagged', multiErrorFlaggedList]
  multiInvoiceErrors = ['multiInvoiceErrors', multiInvoiceErrorsList]


  # Resolve Payment Errors

  invoiceNumCorrectedList, stillMatchPaymentError = checkPaymentErrorAgainstUnpaidInvoices(cur, con, root, matchPaymentError)

  invoiceNumRematchedReport = ['invoiceNumRematchedReport', invoiceNumCorrectedList]

  # rematch payment errors against updated DB
  reMatched, noMatch = reMatchPaymentErrors(stillMatchPaymentError, cur)

  incompRec.extend(noMatch)

  """
    *** seems counter intuative to run this here as the system should possibly check if the errors are corrections first? ***
  """

  correctedErrors, incorrectInvoiceNums = resolvePaymentErrors(root, reMatched, cur, con)

  incompRec.extend(incorrectInvoiceNums)

  updatedCorrectedErrors = addCorrectedTransactionPairsDB(correctedErrors, con, cur)

  con.commit()

  # function now returns two lists. correctedErrorsReport is a list of incoming transactions that have had to be corrected
  # and have not found a previous error they relate to.
  # correctionTransactionErrorsReport is a list of the incoming transaction and the invoice/s or dummy transaction they pay for.

  """
    *** This (checkIfTransactionListContainsErrorCorrections) should possibly be reordered to before resolvePaymentErrors.
        At the moment forces the user to come back to the transactions previously examined/verified.
  """

  correctedErrorsReportList, correctionTransactionErrorsReportList = checkIfTransactionListContainsErrorCorrections(root, updatedCorrectedErrors, con, cur)

  correctedErrorsReport = ['correctedErrorsReport', correctedErrorsReportList]

  correctionTransactionErrorsReport = ['correctionErrorsReort', correctionTransactionErrorsReportList]


  # Start of Matching Transactions with errorness invoice_numbers

  incompRec.sort(key=lambda Transaction: Transaction.paid_by)

  inCompMatchedList, inCompMultiMatchList, noMatches, newCustomersTransactionsList = resolveNoMatchTransactions(root, incompRec, cur, con)

  inCompMatched = ['inCompMatched', inCompMatchedList]
  inCompMultiMatch = ['inCompMultiMatch', inCompMultiMatchList]
  newCustomerTransactions = ['newCustomerTransactions', newCustomersTransactionsList]

  con.commit()

  upLoadedPairs.extend(inCompMatched)

  inCompErrorCorrectionMatchedList, finalNoMatchList = final_resolver(root, noMatches, cur, con)

  dateToday = datetime.today().strftime("%d-%m-%Y")

  for transaction in finalNoMatchList:

    transaction.error_flagged = 1
    transaction.invoice_num = None

    if transaction.error_notes == None:
      transaction.error_notes = f"No Match Found On {dateToday}"
    else:
      updatedErrorNote = f"{transaction.error_notes} - No Match Found On {dateToday}"
      transaction.error_notes = updatedErrorNote

  noMatchTransactionTups = [noMatchTransaction.as_tuple() for noMatchTransaction in finalNoMatchList]

  addNoMatchTransactionsToDB(noMatchTransactionTups, con, cur)

  inCompErrorCorrectionMatched = ['inCompErrorCorrectionMatched', inCompErrorCorrectionMatchedList]

  finalNoMatch = ['finalNoMatch', finalNoMatchList]

  print("This is the final count of all final transaction lists")

  print(len(matchedSingles[1]) + len(correctedErrorsReport[1]) + len(invoiceNumRematchedReport[1]) + len(correctionTransactionErrorsReport[1]) + len(inCompMatched[1]) + len(inCompErrorCorrectionMatched[1]) + len(uploadedMultiTransactionPairs[1]) + len(inCompMultiMatch[1]) + len(finalNoMatch[1]) + len(multiErrorFlagged[1]) + len(multiInvoiceErrors[1]) + len(newCustomerTransactions[1]))

  finalListOfLists = [matchedSingles, correctedErrorsReport, invoiceNumRematchedReport, correctionTransactionErrorsReport, inCompMatched, inCompErrorCorrectionMatched, uploadedMultiTransactionPairs, multiErrorFlagged, multiInvoiceErrors, inCompMultiMatch, finalNoMatch, newCustomerTransactions]


  outputPrintDict = {output[0]: output[1] for output in finalListOfLists}

  f = open("../output.txt", "w")

  f.write(str(outputPrintDict))

  print_transaction_upload_results(outputPrintDict)
  f.close()

  cur.close()
  con.close()