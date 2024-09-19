import os
import sqlite3
from datetime import datetime

from isp_db_helpers import *

def fetchCreditPreviewNumbers(fromDate, customer_id, cur, con):

  fromDateObj = datetime.strptime(fromDate, '%d/%m/%Y')
  
  invoiceCount = countInvoicesByCustomerAfterDate(fromDateObj, customer_id, cur)

  unpaidInvoiceCount = countUnpaidInvoicesByCustomerAfterDate(fromDateObj, customer_id, cur)

  return invoiceCount, unpaidInvoiceCount

conn = sqlite3.connect(os.getenv("DB_NAME"))

conn.execute('PRAGMA foreign_keys = ON')

cur = conn.cursor()

startDate = "21/09/2020"

fetchCreditPreviewNumbers(startDate, 9, cur, conn)

cur.close()
conn.close()