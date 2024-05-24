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

  compRec = []
  incompRec = []
  multiRec = []

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
        incompRec.append(transDC)
      elif len(cleanedEntry[0]) == 1:
        compRec.append(cleanedEntry)
      else:
        transactionDC = genMultiTransactionDCobj(cleanedEntry)
        multiRec.append(transactionDC)


    matches = []

    noMatchFromNum = []
    matchPaymentError = []
    matchNameError = []

    transactionUploadList = []

    for transaction in compRec:

      con = sqlite3.connect(os.getenv("DB_NAME"))

      con.execute('PRAGMA foreign_keys = ON')

      cur = con.cursor()

      invoiceNum = int(transaction[0][0])

      invoice = fetchInvoiceByNum(invoiceNum, cur)

      if len(invoice) == 0:
        transactionDC = genTransactionDCobj(transaction)
        noMatchFromNum.append(transactionDC)
        continue
      else:
        invoice = genInvoiceDCobj(invoice)
        transactionDC = genTransactionDCobj(transaction)
        matches.append([transactionDC, invoice])

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


  nameResolved, namesUnresolved = resolveNameMismatches(root, cur, con, matchNameError)

  transactionUploadList.extend(nameResolved)

  transactionUpload = [payPair[0].as_tuple() for payPair in transactionUploadList]

  addTransactionsToDB(transactionUpload, cur)

  con.commit()
 
  multiVerified, multiErrorFlagged, multiInvoiceErrors = resolveMultiInvoiceTransactions(root, cur, con, multiRec)

  dummyTransactions = genMultiTransactionsInvoices(multiVerified, cur, con)

  dummyTransactionTuples = [dummyTrans.as_tuple() for dummyTrans in dummyTransactions]

  addDummyTransactionsToDB(dummyTransactionTuples, cur, con)

  con.commit()

  paymentErrors, incompRec = reMatchPaymentErrors(matchPaymentError, incompRec, cur)

  correctedErrors, incorrectInvoiceNums = resolvePaymentErrors(root, paymentErrors)

  correctedTransactions = [(errorPair[0][0], errorPair[1]) for errorPair in correctedErrors]

  addCorrectedTransactionPairsDB(correctedTransactions, con, cur)

  incompRec.extend(incorrectInvoiceNums)

  incompRec.sort(key=lambda Transaction: Transaction.paid_by)

  matched, noMatches, newCustomersTransactions = resolveNoMatchTransactions(root, incompRec, cur, con)


  print("")
  print("This is matched before selection between invoices")
  print("")


  for boo in matched:
    print(boo)

  for matchPair in matched:
    if len(matchPair[1]) > 1:

      chosenInvoiceID = tk.IntVar(value=0)

      openSelectBetweenInvoices(root, matchPair[0], matchPair[1], chosenInvoiceID)

      invoiceID = chosenInvoiceID.get()

      if invoiceID == 0:
        noMatches.append(matchPair[0])
      else:
        matchInvoice = [matchedInvoice for matchedInvoice in matchPair[1] if matchedInvoice.invoice_num == invoiceID]
        matchPair.pop(1)
        matchPair.append(matchInvoice)

  print("")
  print("This is matched after selection between invoices")
  print("")

  for i in matched:
    print(i)

  print("")
  print("This is no matches")
  print("")

  for b in noMatches:
    print(b)



  # Need to work on matchPaymentError here, List match payment error needs to match the Transaction with invoices that do not
  # already have an Transaction asotiated with them. The original fetchInvoiceByNum needs to be reworked to do the same,
  # as matching with invoices already paid will not work.

  # From there the system need to user prompt about the detail mismatches, either the pair are unrealted or a payment error that
  # can be corrected via a new negative (or positive) transaction.

  """
  What we have left...

  nameUnresolved = names that haven't been varified by the user, invoice, transaction pairs
    - namesUnresolved comes from user verification. Atm still hasn't been amount checked. Amounts need to be checked.

  matchPaymentError = single invoice transactions that have payment error, names do match
    - Need to prompt user if to correct amount with dummy transaction, or add to error list

  incompRec = Transactions without an invoice number attatched
    - Needs to be matched via customer name and amount (and date, needs to be after invoice issued)
  
  multiErrorFlagged = multiTransaction with invoices that do add up, within tol, but have been flagged

  multiInvoiceError = multiTransaction with invoices that either don't add up (out of tol range)

    - Both of the multi invoice errors need to be left until last and an algo written to try and match invoices left

  noMatchFromNum = Transactions with one invoice number, but invoice can't be found
    - Need to match via customer name and amount

  """


    # Function for incomp teansactions (no invoice number) to match transactions with invoices via payment amount and then
    # matching and adding aliases (via user promting) to the database so they can be identified automatically on next upload.

    # for nameError in matchNameError[0:4]:
    #   verifyAlias(nameError[0], nameError[1][0])

    # Need final matching function for transactions that have multiple invoice numbers, which relate to a payment made for invoices
    # between two date. The function should pull relelvant invoices for the transaction cutomer and see if their total matches that paid,
    # with the help of tha aliases table in relation to customers, hopefully this should yeild a full match set.


    # addTransactionsToDB(transactionUploadList, cur)

  
  cur.close()
  con.close()