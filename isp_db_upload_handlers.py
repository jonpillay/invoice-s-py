import csv
import sqlite3
import os
import re
from datetime import datetime

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

    # print(invoiceNumsList)

    for entry in CSVreader:
      if int(entry[0]) not in invoiceNumsList:
        entriesList.append(entry)

    print(entriesList)

    con = sqlite3.connect(os.getenv("DB_NAME"))
    cur = con.cursor()

    for invoice in entriesList:

      formattedDate = datetime.strptime(invoice[1], '%d/%m/%Y').strftime('%Y-%m-%d')

      currentInvoice = (int(invoice[0]), float(invoice[4]), formattedDate, invoice[2].strip())

      sql = """INSERT OR IGNORE INTO INVOICES(invoice_num, amount, date_issued, company_name)
               VALUES(?,?,?,?)"""
      
      cur.execute(sql, currentInvoice)

    con.commit()
    con.close()

def handleTransactionUpload(filename):

  compRec = []
  incompRec = []
  multiRec = []

  with open(filename) as csv_file:
    CSVreader = csv.reader(csv_file)

    for entry in CSVreader:
      invMatches = re.findall(os.getenv('CSV_TRANSACTION_REGEX'), entry[2])

      # print(invMatches)
      
      if len(invMatches) == 0:
        incompRec.append(entry)
      elif len(invMatches) == 1:
        compRec.append(entry)
      else:
        multiRec.append(entry)

    print(len(incompRec))
    print(len(compRec))
    print(len(multiRec))

    # for i in incompRec:
    #   print(i)

    # print("Break")
    # print(" ")

    # for i in compRec:
    #   print(i)
    # print("Break")
    # print(" ")
    # for i in multiRec:
    #   print(i)