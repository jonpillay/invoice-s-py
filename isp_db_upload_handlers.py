import csv
import sqlite3
import os
import re
from datetime import datetime

from isp_csv_helpers import cleanTransactionRaw
from isp_trans_verify import verifyTransactionDetails
from isp_db_helpers import getInvoiceNumsIDs, fetchInvoiceByNum, addTransactionsToDB

def getDBInvoiceNums():
    
    con = sqlite3.connect(os.getenv("DB_NAME"))
    cur = con.cursor()

    fetctInvNumSQL = "SELECT invoice_num from INVOICES"

    cur.execute(fetctInvNumSQL)

    invoiceNums = cur.fetchall()

    return [invoice[0] for invoice in invoiceNums]


def handleInvoiceUpload(filename):

  with open(filename) as csv_file:
    CSVreader = csv.reader(csv_file)

    entriesList = []

    invoiceNumsList = getDBInvoiceNums()

    for entry in CSVreader:
      if int(entry[0]) not in invoiceNumsList:
        entriesList.append(entry)

    con = sqlite3.connect(os.getenv("DB_NAME"))

    con.execute('PRAGMA foreign_keys = ON')

    cur = con.cursor()

    for invoice in entriesList:

      formattedDate = datetime.strptime(invoice[1], '%d/%m/%Y').strftime('%Y-%m-%d')

      currentInvoice = (int(invoice[0]), float(invoice[4]), formattedDate, invoice[2].strip())

      sql = """INSERT OR IGNORE INTO INVOICES(invoice_num, amount, date_issued, company_name)
               VALUES(?,?,?,?)"""
      
      try:
        cur.execute(sql, currentInvoice)
      except:
        print("Invoice upload failed")

    con.commit()
    con.close()

def handleTransactionUpload(filename):

  compRec = []
  incompRec = []
  multiRec = []

  with open(filename) as csv_file:
    CSVreader = csv.reader(csv_file)

    for entry in CSVreader:
      try:
        datetime.strptime(entry[0].strip(), '%d %b %Y')
      except:
        continue

      cleanedEntry = cleanTransactionRaw(entry)

      # print(cleanedEntry)
      
      if len(cleanedEntry[0]) == 0:
        incompRec.append(cleanedEntry)
      elif len(cleanedEntry[0]) == 1:
        compRec.append(cleanedEntry)
      else:
        multiRec.append(cleanedEntry)

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
        matches.append(transaction)

      detailMatch = verifyTransactionDetails(transaction, invoice)

      if type(detailMatch) == int:
        matchPaymentError.append([transaction, invoice])
      elif type(detailMatch) == str:
        matchNameError.append([transaction, invoice])
      elif detailMatch == True:
        og_string = " ".join(transaction[5])
        transactionTuple = (transaction[0][0], transaction[1], transaction[2], transaction[3], transaction[4], og_string, invoice[0][0])
        transactionUploadList.append(transactionTuple)
      else:
        print("cannot match")

    # Function for incomp teansactions (no invoice number) to match transactions with invoices via payment amount and then
    # matching and adding aliases (via user promting) to the database so they can be identified automatically on next upload.

    for nameError in matchNameError:
      pass
      # aliasMatchFunction(nameError[0], nameError[1])

    # Need final matching function for transactions that have multiple invoice numbers, which relate to a payment made for invoices
    # between two date. The function should pull relelvant invoices for the transaction cutomer and see if their total matches that paid,
    # with the help of tha aliases table in relation to customers, hopefully this should yeild a full match set.


    addTransactionsToDB(transactionUploadList, cur)


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