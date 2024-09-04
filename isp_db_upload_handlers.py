import tkinter as tk
import csv
import sqlite3
import os
import re
from datetime import datetime

import json

from isp_csv_helpers import cleanTransactionRaw, cleanInvoiceListRawGenCustomerList
from isp_trans_verify import verifyTransactionDetails, verifyAlias, verifyTransactionAmount, checkIfTransactionListContainsErrorCorrections
from isp_db_helpers import getInvoiceNumsIDs, fetchInvoiceByNum, fetchUnpaidInvoiceByNum, addTransactionsToDB, addNewCustomersToDB, getDBInvoiceNums, getCustomerNamesIDs, resolveNewCustomersDB, addCashInvoicesAndTransactions, addInvoicesToDB, addDummyTransactionsToDB, addCorrectedTransactionPairsDB, addParentErrorTransactionsToDB
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

  print("this is count at line 107")
  print(count)

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

  # print(len(matchPaymentError)+len(matchNameError)+len(matchedSingles)+len(noMatchFromNum)+len(incompRec)+len(multiRec))
  # records are complete at this point

  # resolve name mismatches
  nameResolved, namesUnresolved, resolvedNamePaymentErrors = resolveNameMismatches(root, cur, con, matchNameError)

  incompRec.append(namesUnresolved)
  
  # print(len(matchPaymentError)+len(nameResolved)+len(matchedSingles)+len(noMatchFromNum)+len(incompRec)+len(multiRec))
  # records are complete at this point

  matchPaymentError.extend(resolvedNamePaymentErrors)

  matchedSingles[1].extend(nameResolved)

  transactionUpload = [payPair[0].as_tuple() for payPair in matchedSingles[1]]

  transactionUploadObjs = [payPair[0] for payPair in matchedSingles[1]]

  addTransactionsToDB(transactionUpload, cur)

  con.commit()

  upLoadedPairs.extend(matchedSingles)

  # print("Transaction count @line 192")
  # print(len(matchPaymentError)+len(incompRec)+len(multiRec)+len(upLoadedPairs))

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

  # print("Transaction count @line 207")
  # print(len(matchPaymentError)+len(noMatchFromNum)+len(incompRec)+len(multiVerified)+len(multiErrorFlagged)+len(multiInvoiceErrors)+len(upLoadedPairs))


  # print(len(matchPaymentError)+len(nameResolved)+len(upLoadedPairs)+len(noMatchFromNum)+len(incompRec)+len(multiVerified)+len(multiErrorFlagged)+len(multiInvoiceErrors))


  # Resolve Payment Errors

  invoiceNumCorrectedList, stillMatchPaymentError = checkPaymentErrorAgainstUnpaidInvoices(cur, con, root, matchPaymentError)

  invoiceNumRematchedReport = ['invoiceNumRematchedReport', invoiceNumCorrectedList]

  # rematch payment errors against updated DB
  reMatched, noMatch = reMatchPaymentErrors(stillMatchPaymentError, cur)


  # print("Transaction count @line 220")
  # print(len(reMatched)+len(noMatch)+len(noMatchFromNum)+len(incompRec)+len(multiVerified)+len(multiErrorFlagged)+len(multiInvoiceErrors)+len(upLoadedPairs))

  incompRec.extend(noMatch)

  # print(len(reMatched))

  correctedErrors, incorrectInvoiceNums = resolvePaymentErrors(root, reMatched, cur, con)


  # need a function here to check if any of the payment errors are corrections of previous payments.
  # starting with those in the current list and then going backwards through the DB invoices.

  # print("Transaction count @line 229")
  # print(len(correctedErrors)+len(incorrectInvoiceNums)+len(incompRec)+len(multiVerified)+len(multiErrorFlagged)+len(multiInvoiceErrors)+len(upLoadedPairs))

  incompRec.extend(incorrectInvoiceNums)

  # print("This is corrected errors")

  # print(correctedErrors)

  correctedTransactions = [(correctedPair[0][0], correctedPair[1]) for correctedPair in correctedErrors]

  updatedCorrectedErrors = addCorrectedTransactionPairsDB(correctedErrors, con, cur)

  con.commit()

  # function now returns two lists. correctedErrorsReport is a list of incoming transactions that have had to be corrected
  # and have not found a previous error they relate to.
  # correctionTransactionErrorsReport is a list of the incoming transaction and the invoice/s or dummy transaction they pay for.

  correctedErrorsReportList, correctionTransactionErrorsReportList = checkIfTransactionListContainsErrorCorrections(root, updatedCorrectedErrors, con, cur)

  correctedErrorsReport = ['correctedErrorsReport', correctedErrorsReportList]

  correctionTransactionErrorsReport = ['correctionErrorsReort', correctionTransactionErrorsReportList]


  # Start of Matching Transactions with errorness invoice_numbers

  incompRec.sort(key=lambda Transaction: Transaction.paid_by)


  # print("InComp rec len check")
  # print(len(incompRec))
  # print("")

  inCompMatchedList, inCompMultiMatchList, noMatches, newCustomersTransactionsList = resolveNoMatchTransactions(root, incompRec, cur, con)

  inCompMatched = ['inCompMatched', inCompMatchedList]
  inCompMultiMatch = ['inCompMultiMatch', inCompMultiMatchList]
  newCustomerTransactions = ['newCustomerTransactions', newCustomersTransactionsList]

  # print("Ouput len check line 267")
  # print(len(inCompMatched)+len(noMatches)+len(newCustomersTransactionsList))
  # print("")

  con.commit()

  upLoadedPairs.extend(inCompMatched)

  inCompErrorCorrectionMatchedList, finalNoMatchList = final_resolver(root, noMatches, cur, con)

  inCompErrorCorrectionMatched = ['inCompErrorCorrectionMatched', inCompErrorCorrectionMatchedList]

  finalNoMatch = ['finalNoMatch', finalNoMatchList]

  print("This is the final count of all final transaction lists")
  print(len(matchedSingles[1]) + len(correctedErrorsReport[1]) + len(correctionTransactionErrorsReport[1]) + len(inCompMatched[1]) + len(inCompErrorCorrectionMatched[1]) + len(uploadedMultiTransactionPairs[1]) + len(inCompMultiMatch[1]) + len(finalNoMatch[1]) + len(multiErrorFlagged[1]) + len(multiInvoiceErrors[1]) + len(newCustomerTransactions[1]))

  print(len(matchedSingles[1])) #255
  print(len(correctedErrorsReport[1])) #6
  print(len(correctionTransactionErrorsReport[1])) #0
  print(len(inCompMatched[1])) #22
  print(len(inCompErrorCorrectionMatched[1])) #0
  print(len(uploadedMultiTransactionPairs[1])) #7
  print(len(multiErrorFlagged[1])) #0
  print(len(multiInvoiceErrors[1])) #0
  print(len(inCompMultiMatch[1])) #0
  print(len(finalNoMatch[1])) #28
  print(len(newCustomerTransactions[1])) #2

  finalListOfLists = [matchedSingles, correctedErrorsReport, invoiceNumRematchedReport, correctionTransactionErrorsReport, inCompMatched, inCompErrorCorrectionMatched, uploadedMultiTransactionPairs, multiErrorFlagged, multiInvoiceErrors, inCompMultiMatch, finalNoMatch, newCustomerTransactions]


  outputPrintDict = {output[0]: output[1] for output in finalListOfLists}

  print_transaction_upload_results(outputPrintDict)

  print(type(outputPrintDict))

  f = open("../output.txt", "a")

  f.write(str(outputPrintDict))

  f.close()
  

  """
  
  - numbers from desanned data

    This is the final count of all final transaction lists
    320
    255
    5
    0
    23
    0
    7
    0
    0
    0
    28
    2

  - numbers from sensitive data
  
    This is the final count of all final transaction lists
    320
    255
    5
    0
    23
    0
    7
    0
    0
    0
    28
    2


  """

  











  # print("Transaction count @line 260")
  # print(len(noMatches)+len(namesUnresolved)+len(newCustomersTransactions)+len(multiVerified)+len(multiErrorFlagged)+len(multiInvoiceErrors)+len(upLoadedPairs))




  # print("Start of matched")
  # print("")

  # for match in matched:
  #   print(match)

  #   print("Start of noMatches")
  #   print("")

  # for noMatch in noMatches:
  #   print(match)
  #   print("")


  """

  What we have left at this point and where they're going.

  """

  #List of all the uploaded Transaction/Single Invoice pairs that have been uploaded - To be sent to printer (274)
  # print(len(upLoadedPairs))

  # List of transactions that have not found a match. (36)
  # print(len(noMatches))
  # for i in noMatches:
  #   print(i)
  #   print(" ")

  # List of new customer transactions that have no matching invoices or records on the DB - to be sent for printing (3)
  # print(len(newCustomersTransactions))

  # Transactions that have the wrong name on them (0)
  # print(len(namesUnresolved))

  # List of pairs of lists containing transaction/invoices. The first Transaction in the list is the original multi transaction,
  # the following ones are dummy transaction (a split of the main one) to pay each invoice. (7)
  # print(len(uploadedMultiTransactionPairs))

  # Any multi invoice errors where the listed invoices do not total to the transaction amount. Should be possibly tried to match earlier. (0)
  # print(len(multiInvoiceErrors)) 

  # Multi-invoice errors that even though they do add up to the correct amount, were flaggeed as errors by the user
  # I expect this to be none, as if the invoices already add up, then I would assume it errorless.
  # print(len(multiErrorFlagged))

  # for e in upLoadedPairs:
  #   print(e)
  #   print("")

  # print("No Matches")
  # print("")
  # for i in noMatches:
  #   print(i)
  #   print("")

  # print("")
  # print("Match Pairs")
  # print("")
  # for i in finalPaymentMatches:
  #   print(i)
  #   print("")

  """
    We have left -

    upLoadedPairs = all the Transaction and Invoice pairs that have been matched and uploaded

    uploadedMultiTransactionPairs - two lists containing original multi transaction
    with dummy transactions and all invoices paired

    newCustomersTransactions - Transactions that have come in without a matching invoice
    and new customers added to DB so assumed no invoice exists on DB

  """


  
  cur.close()
  con.close()

  # print("This is the uploaded pairs")

  # for uploaded in upLoadedPairs:

  #   print(uploaded[0])
  #   print(uploaded[1])
  #   print("")
  #   print("")

  # print("upLoadedPairs len is ")
  # print(len(upLoadedPairs))

  # for multipair in uploadedMultiTransactionPairs:

  #   print(multipair[0])
  #   print("")
  #   print(multipair[1])
  #   print("")

  # print("multipair len is ")
  # print(len(multipair))
