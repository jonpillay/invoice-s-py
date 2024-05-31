import tkinter as tk
import csv
import sqlite3
import os
import re
from datetime import datetime

from isp_csv_helpers import cleanTransactionRaw, cleanInvoiceListRawGenCustomerList
from isp_trans_verify import verifyTransactionDetails, verifyAlias, verifyTransactionAmount
from isp_db_helpers import getInvoiceNumsIDs, fetchInvoiceByNum, fetchUnpaidInvoiceByNum, addTransactionsToDB, addNewCustomersToDB, getDBInvoiceNums, getCustomerNamesIDs, resolveNewCustomersDB, addCashInvoicesAndTransactions, addInvoicesToDB, addDummyTransactionsToDB, addCorrectedTransactionPairsDB
from isp_data_handlers import constructCustomerAliasesDict, constructCustomerIDict, prepInvoiceUploadList, genInvoiceDCobj, genTransactionDCobj, genMultiTransactionDCobj, prepMatchedTransforDB, genMultiTransactionsInvoices, reMatchPaymentErrors, genNoNumTransactionDCobj
from isp_resolvers import resolveNameMismatches, resolvePaymentErrors, resolveMultiInvoiceTransactions, resolveNoMatchTransactions
from isp_multi_invoice_prompt import openSelectBetweenInvoices

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

  print(len(compRec)+len(incompRec)+len(multiRec))
  #records are complete at this point

  # final lists

  upLoadedPairs = []
  noMatchFinal = []

  # working lists

  matches = []
  noMatchFromNum = []

  matchPaymentError = []
  matchNameError = []

  transactionUploadList = []

  for transaction in compRec:

    con = sqlite3.connect(os.getenv("DB_NAME"))

    con.execute('PRAGMA foreign_keys = ON')

    cur = con.cursor()

    invoiceNum = transaction.invoice_num

    # fetch invoice via number on transaction

    invoice = fetchInvoiceByNum(invoiceNum, cur)

    if len(invoice) == 0:
      noMatchFromNum.append(transaction)
    else:
      invoice = genInvoiceDCobj(invoice[0])
      matches.append([transaction, invoice])

  # for transaction, invoice in matches:
  #   print(transaction.invoice_num)
  #   print(invoice.invoice_num)
  #   print("")

  for transaction, invoice in matches:

    detailMatch = verifyTransactionDetails(transaction, invoice, cur)

    if type(detailMatch) == float:
      matchPaymentError.append([transaction, invoice])
    elif type(detailMatch) == str:
      matchNameError.append([transaction, invoice])
    elif detailMatch == True:
      prepMatchedTransforDB(transaction, invoice)
      matchPair = (transaction, invoice)
      transactionUploadList.append(matchPair)
    else:
      print("cannot match")

  print(len(matchPaymentError)+len(matchNameError)+len(transactionUploadList)+len(noMatchFromNum)+len(incompRec)+len(multiRec))
  # records are complete at this point

  # resolve name mismatches
  nameResolved, namesUnresolved = resolveNameMismatches(root, cur, con, matchNameError)
  
  print(len(matchPaymentError)+len(nameResolved)+len(transactionUploadList)+len(noMatchFromNum)+len(incompRec)+len(multiRec))
  # records are complete at this point

  transactionUploadList.extend(nameResolved)

  transactionUpload = [payPair[0].as_tuple() for payPair in transactionUploadList]

  addTransactionsToDB(transactionUpload, cur)

  con.commit()

  upLoadedPairs.extend(transactionUploadList)

  transactionUploadList = []


  # Start of multi-invoice transaction verification.
 
  multiVerified, multiErrorFlagged, multiInvoiceErrors = resolveMultiInvoiceTransactions(root, cur, con, multiRec)

  dummyTransactions, uploadedMultiTransactionPairs = genMultiTransactionsInvoices(multiVerified, cur, con)

  dummyTransactionTuples = [dummyTrans.as_tuple() for dummyTrans in dummyTransactions]

  addDummyTransactionsToDB(dummyTransactionTuples, cur, con)

  con.commit()


  # Resolve Payment Errors


  # rematch payment errors against updated DB
  reMatched, noMatch = reMatchPaymentErrors(matchPaymentError, cur)

  incompRec.extend(noMatch)

  print(len(reMatched))

  correctedErrors, incorrectInvoiceNums = resolvePaymentErrors(root, reMatched)

  incompRec.extend(incorrectInvoiceNums)

  correctedTransactions = [(errorPair[0][0], errorPair[1]) for errorPair in correctedErrors]

  addCorrectedTransactionPairsDB(correctedTransactions, con, cur)

  con.commit()

  uploadedRec = [(uploadedPair[0][0], uploadedPair[0][1]) for uploadedPair in correctedErrors]

  upLoadedPairs.extend(uploadedRec)



  # Start of Matching Transactions with errorness invoice_numbers

  incompRec.sort(key=lambda Transaction: Transaction.paid_by)

  # for i in incompRec:
  #   print(i)

  matched, noMatches, newCustomersTransactions = resolveNoMatchTransactions(root, incompRec, cur, con)

  upLoadedPairs.extend(matched)

  print(len(upLoadedPairs))
  print(len(noMatches))
  print(len(newCustomersTransactions))
  print(len(namesUnresolved))
  print(len(uploadedMultiTransactionPairs))
  print(len(multiInvoiceErrors))

  transactionUploadList = []

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