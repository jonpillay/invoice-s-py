import csv
import sqlite3
import os
from datetime import datetime

def handleInvoiceUpload(filename):

  with open(filename) as csv_file:
    CSVreader = csv.reader(csv_file)

    entriesList = []

    for entry in CSVreader:
      entriesList.append(entry)
      

    con = sqlite3.connect(os.getenv("DB_NAME"))
    cur = con.cursor()

    for invoice in entriesList:

      formattedDate = datetime.strptime(invoice[1], '%d/%m/%Y').strftime('%Y-%m-%d')

      currentInvoice = (int(invoice[0]), float(invoice[4]), formattedDate, invoice[2].strip())

      sql = """INSERT INTO INVOICES(invoice_num, amount, date_issued, company_name)
               VALUES(?,?,?,?)"""
      
      cur.execute(sql, currentInvoice)

    con.commit()
    con.close()