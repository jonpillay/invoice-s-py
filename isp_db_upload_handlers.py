import csv
import sqlite3
import os
import re
from datetime import datetime

from isp_csv_helpers import cleanTransactionRaw, cleanInvoiceListRawGenCustomerList
from isp_trans_verify import verifyTransactionDetails, verifyAlias, verifyTransactionAmount
from isp_db_helpers import getInvoiceNumsIDs, fetchInvoiceByNum, addTransactionsToDB, addNewCustomersToDB, getDBInvoiceNums, getCustomerNamesIDs, resolveNewCustomersDB, addCashInvoicesAndTransactions, addInvoicesToDB, addDummyTransactionsToDB
from isp_data_handlers import constructCustomerAliasesDict, constructCustomerIDict, prepInvoiceUploadList, genInvoiceDCobj, genTransactionDCobj, genMultiTransactionDCobj, prepMatchedTransforDB, genMultiTransactionsInvoices
from isp_resolvers import resolveNameMismatches, resolvePaymentErrors, resolveMultiInvoiceTransactions

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


  # addCashInvoiceAndTransaction(cashInvoiceUploadTups, cur, conn)

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
        incompRec.append(cleanedEntry)
      elif len(cleanedEntry[0]) == 1:
        compRec.append(cleanedEntry)
      else:
        transactionDC = genMultiTransactionDCobj(cleanedEntry)
        multiRec.append(transactionDC)

    """
      Two database related functions need to be written. One here and one on the invoice upload.

      One here needs to go through the entries that have matched with one invoice number and also
      amounts and see if there are instnaces where the name does not match and promt the user if
      if they want to create a alias assotiation with the customer object in the db (the alias being
      a DB object with the FK to customer.

      The function needs to loop through the list of entries examining each, but needs to skip associations
      already made in run of the function. A list of tuples should also be made to compare before prompting the
      user.

      With this added verifyTransactionDetails() below can also verify via aliases. Leaving only actual naming errors
      to be flagged (which you would assume there would be none - payment + invoice are varified).

      The other function that needs to be added (first) is in the invoiceUpload to build a list of Customer objects in
      the database from new customers (which they all will be first time).
    """

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

  # print(len(matchPaymentError))
  # print(len(matchNameError))
  # print(len(transactionUploadList))
  # print(len(multiRec))
  # print(len(incompRec))
  # print(len(noMatchFromNum))

  nameResolved, nameUnresolved = resolveNameMismatches(root, cur, con, matchNameError)

  con.commit()

  for paymentPair in nameResolved:
    
    transaction = paymentPair[0]
    invoice = paymentPair[1]

    paymentMatch = verifyTransactionAmount(transaction, invoice)

    if paymentMatch == True:
      prepMatchedTransforDB(transaction, invoice)
      transactionUploadList.append((transaction, invoice))
    else:
      matchPaymentError.append(paymentPair)
 
  multiVerified, multiErrorFlagged, multiInvoiceErrors = resolveMultiInvoiceTransactions(root, cur, con, multiRec)

  dummyTransactions = genMultiTransactionsInvoices(multiVerified, cur, con)

  dummyTransactionTuples = [dummyTrans.as_tuple() for dummyTrans in dummyTransactions]

  addDummyTransactionsToDB(dummyTransactionTuples, cur, con)


    # Function for incomp teansactions (no invoice number) to match transactions with invoices via payment amount and then
    # matching and adding aliases (via user promting) to the database so they can be identified automatically on next upload.

    # for nameError in matchNameError[0:4]:
    #   verifyAlias(nameError[0], nameError[1][0])

    # Need final matching function for transactions that have multiple invoice numbers, which relate to a payment made for invoices
    # between two date. The function should pull relelvant invoices for the transaction cutomer and see if their total matches that paid,
    # with the help of tha aliases table in relation to customers, hopefully this should yeild a full match set.


    # addTransactionsToDB(transactionUploadList, cur)


      # print(invoice)
      # print(i)

      
    

    # for entry in compRec:

    #   con = sqlite3.connect(os.getenv("DB_NAME"))

    #   match = compareInvNumbers()

    #   print(match)

    # for i in incompRec:
    #   print(i)
    # print(len(compRec))
    # print(len(multiRec))
  
  cur.close()
  con.close()