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

  incompRec.extend(noMatchFromNum)

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

  # print(len(matchPaymentError)+len(matchNameError)+len(transactionUploadList)+len(noMatchFromNum)+len(incompRec)+len(multiRec))
  # records are complete at this point

  # resolve name mismatches
  nameResolved, namesUnresolved = resolveNameMismatches(root, cur, con, matchNameError)
  
  # print(len(matchPaymentError)+len(nameResolved)+len(transactionUploadList)+len(noMatchFromNum)+len(incompRec)+len(multiRec))
  # records are complete at this point

  transactionUploadList.extend(nameResolved)

  transactionUpload = [payPair[0].as_tuple() for payPair in transactionUploadList]

  addTransactionsToDB(transactionUpload, cur)

  con.commit()

  upLoadedPairs.extend(transactionUploadList)

  transactionUploadList = []


  print("Transaction count @line 192")
  print(len(matchPaymentError)+len(incompRec)+len(multiRec)+len(upLoadedPairs))

  # Start of multi-invoice transaction verification.
 
  multiVerified, multiErrorFlagged, multiInvoiceErrors = resolveMultiInvoiceTransactions(root, cur, con, multiRec)

  dummyTransactions, uploadedMultiTransactionPairs = genMultiTransactionsInvoices(multiVerified, cur, con)

  dummyTransactionTuples = [dummyTrans.as_tuple() for dummyTrans in dummyTransactions]

  addDummyTransactionsToDB(dummyTransactionTuples, cur, con)

  con.commit()

  # print("Transaction count @line 207")
  # print(len(matchPaymentError)+len(noMatchFromNum)+len(incompRec)+len(multiVerified)+len(multiErrorFlagged)+len(multiInvoiceErrors)+len(upLoadedPairs))


  # print(len(matchPaymentError)+len(nameResolved)+len(upLoadedPairs)+len(noMatchFromNum)+len(incompRec)+len(multiVerified)+len(multiErrorFlagged)+len(multiInvoiceErrors))


  # Resolve Payment Errors


  # rematch payment errors against updated DB
  reMatched, noMatch = reMatchPaymentErrors(matchPaymentError, cur)

  # print("Transaction count @line 220")
  # print(len(reMatched)+len(noMatch)+len(noMatchFromNum)+len(incompRec)+len(multiVerified)+len(multiErrorFlagged)+len(multiInvoiceErrors)+len(upLoadedPairs))

  incompRec.extend(noMatch)

  # print(len(reMatched))

  correctedErrors, incorrectInvoiceNums = resolvePaymentErrors(root, reMatched)

  # print("Transaction count @line 229")
  # print(len(correctedErrors)+len(incorrectInvoiceNums)+len(incompRec)+len(multiVerified)+len(multiErrorFlagged)+len(multiInvoiceErrors)+len(upLoadedPairs))

  incompRec.extend(incorrectInvoiceNums)

  correctedTransactions = [(errorPair[0][0], errorPair[1]) for errorPair in correctedErrors]

  addCorrectedTransactionPairsDB(correctedTransactions, con, cur)

  con.commit()

  uploadRecs = [(uploadedPair[0][0], uploadedPair[0][1]) for uploadedPair in correctedErrors]

  upLoadedPairs.extend(uploadRecs)



  # Start of Matching Transactions with errorness invoice_numbers

  incompRec.sort(key=lambda Transaction: Transaction.paid_by)


  print("InComp rec len check")
  print(len(incompRec))
  print("")

  matched, noMatches, newCustomersTransactions = resolveNoMatchTransactions(root, incompRec, cur, con)

  print("Ouput len check")
  print(len(matched)+len(noMatches)+len(newCustomersTransactions))
  print("")

  con.commit()

  upLoadedPairs.extend(matched)

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