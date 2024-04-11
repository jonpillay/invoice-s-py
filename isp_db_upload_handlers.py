import csv
import sqlite3
import os
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