import os
import sqlite3

from isp_db_helpers import *

def fetchCreditPreviewNumbers(fromDate, customer_id, cur, con):
  
  invoiceCount = countInvoicesByCustomerAfterDate(fromDate, customer_id, cur)

  print(invoiceCount)

conn = sqlite3.connect(os.getenv("DB_NAME"))

conn.execute('PRAGMA foreign_keys = ON')

cur = conn.cursor()

fetchCreditPreviewNumbers()

cur.close()
conn.close()