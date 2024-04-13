import csv
import sqlite3
import os
import re
from datetime import datetime

from isp_db_comparrison_functs import compareInvNumbers
from isp_csv_helpers import cleanTransactionRaw

from isp_db_helpers import getInvoiceNumsIDs, transactionInvoiceMatcher

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
      
      if len(cleanedEntry[0]) == 0:
        incompRec.append(cleanedEntry)
      elif len(cleanedEntry[0]) == 1:
        compRec.append(cleanedEntry)
      else:
        multiRec.append(cleanedEntry)

    con = sqlite3.connect(os.getenv("DB_NAME"))

    con.execute('PRAGMA foreign_keys = ON')

    cur = con.cursor()

    for i in compRec:
      invoiceNum = i[0][0]

      invoice = transactionInvoiceMatcher(invoiceNum, cur)

      print(invoice)
    

    # for entry in compRec:

    #   con = sqlite3.connect(os.getenv("DB_NAME"))

    #   match = compareInvNumbers()

    #   print(match)

    # for i in incompRec:
    #   print(i)
    # print(len(compRec))
    # print(len(multiRec))