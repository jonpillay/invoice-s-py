import csv
import sqlite3
import os
import re
from datetime import datetime

from isp_csv_helpers import cleanTransactionRaw, cleanInvoiceListRawGenCustomerList
from isp_trans_verify import verifyTransactionDetails, verifyAlias, resolveNameMismatches
from isp_db_helpers import getInvoiceNumsIDs, fetchInvoiceByNum, addTransactionsToDB, addNewCustomersToDB, getDBInvoiceNums, getCustomerNamesIDs, resolveNewCustomersDB, addCashInvoicesAndTransactions, addInvoicesToDB
from isp_data_handlers import constructCustomerAliasesDict, constructCustomerIDict, prepInvoiceUploadList, genInvoiceDCobj
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

  conn = sqlite3.connect(os.getenv("DB_NAME"))

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
        print("Here")
        continue

      cleanedEntry = cleanTransactionRaw(entry)

      """ Check to see if the Transaction entry has one, numerous, or no invoice number matches """
      
      if len(cleanedEntry[0]) == 0:
        incompRec.append(cleanedEntry)
      elif len(cleanedEntry[0]) == 1:
        compRec.append(cleanedEntry)
      else:
        multiRec.append(cleanedEntry)

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

      invoiceNum = transaction[0][0]

      invoice = fetchInvoiceByNum(invoiceNum, cur)

      if len(invoice) == 0:
        noMatchFromNum.append(transaction)
        continue
      else:
        invoice = genInvoiceDCobj(invoice)
        matches.append(transaction)

      date_paid = datetime.strptime(transaction[2], "%Y-%m-%d")

      transaction = Transaction(
        invoice_num=transaction[0][0],
        amount=transaction[1],
        paid_on=date_paid,
        paid_by=transaction[3],
        payment_method=transaction[4],
        og_string=transaction[5]
      )

      # print(transaction)
      # print(invoice)

      detailMatch = verifyTransactionDetails(transaction, invoice, cur)

      if type(detailMatch) == float:
        matchPaymentError.append([transaction, invoice])
      elif type(detailMatch) == str:
        matchNameError.append([transaction, invoice])
      elif detailMatch == True:
        # og_string = " ".join(transaction[5])
        # transactionTuple = (transaction[0][0], transaction[1], transaction[2], transaction[3], transaction[4], og_string, invoice[0][0])
        transactionUploadList.append(transaction)
      else:
        print("cannot match")

  print(count)

  print(len(matchPaymentError))
  print(len(matchNameError))
  print(len(transactionUploadList))
  print(len(multiRec))
  print(len(incompRec))
  print(len(noMatchFromNum))

  resolveNameMismatches(root, cur, conn, matchNameError)

  






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
  conn.close()