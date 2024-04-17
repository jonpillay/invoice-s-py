import os
import re
from dotenv import load_dotenv, dotenv_values
from datetime import datetime

from isp_dataframes import Invoice

load_dotenv()

from tkinter import filedialog
import csv

def getFilename ():

  filename = filedialog.askopenfilename(
    initialdir=os.getenv("CSV_INITIAL_PATH"),
    title="Open Document",
    filetypes=([("CSV Files","*.csv*")])
  )
  
  return filename

def cleanTransactionRaw(entry):

  invMatches = re.findall(os.getenv('CSV_TRANSACTION_REGEX'), entry[2])

  customer = entry[2].split(',')[0].strip()

  formattedDate = datetime.strptime(entry[0], '%d %b %Y').strftime('%Y-%m-%d')

  payment = float(entry[3])

  paidBy = entry[1]

  return [invMatches, payment, formattedDate, customer, paidBy, entry]

def cleanInvoiceListRawGenCustomerList(entries):
  
  uniqueCustomers = []
  cleanedInvoices = []

  for invoice in entries:

    formattedDate = datetime.strptime(invoice[1], '%d/%m/%Y').strftime('%Y-%m-%d')
    
    customerName = invoice[2].strip().upper()

    customerName = customerName.replace("  ", " ")

    if customerName not in uniqueCustomers:
      uniqueCustomers.append(customerName)

    formattedInvoice = Invoice(int(invoice[0]), float(invoice[4]), formattedDate, customerName)

    cleanedInvoices.append(formattedInvoice)

  return cleanedInvoices, uniqueCustomers



