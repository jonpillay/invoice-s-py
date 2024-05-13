import re
from datetime import datetime

from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerAliases, getCustomerID

def constructCustomerAliasesDict(cur, namesIDsTups):
  
  aliasesDict = {}

  for id, name in namesIDsTups:

    customerAliases = getCustomerAliases(cur, id)

    aliasesDict[name] = customerAliases

  return aliasesDict

def constructCustomerIDict(cur, aliasesDict):

  customerIDict = {}

  for customerName in aliasesDict:
    customerID = getCustomerID(cur, customerName)

    namesList = aliasesDict[customerName]

    namesList.append(customerName)

    customerIDict[customerID] = namesList

  return customerIDict


def prepInvoiceUploadList(invoiceList, customerAliasIDict):

  invoiceUploadTups = []

  cashInvoiceUploadTups = []

  for invoice in invoiceList:

    customerName = invoice.issued_to.upper().strip()

    if re.search("CASH", customerName):
      for id in customerAliasIDict:
        if "CASH" in customerAliasIDict[id]:

          # Transaction data obj - information that is local at the moment from Invoice obj - passed, completed after invoice upload

          invoice.customer_id = id

          cashInvoiceTup =  (
            invoice.invoice_num,
            invoice.amount,
            invoice.date_issued,
            invoice.issued_to,
            invoice.customer_id
          )

          cashInvoiceUploadTups.append(cashInvoiceTup)

          break
      
    else:
      for id in customerAliasIDict:
        if invoice.issued_to.upper().strip() in customerAliasIDict[id]:
          invoice.customer_id = id

          invoiceTup = (
            invoice.invoice_num,
            invoice.amount,
            invoice.date_issued,
            invoice.issued_to,
            invoice.customer_id
          )

          invoiceUploadTups.append(invoiceTup)

  return invoiceUploadTups, cashInvoiceUploadTups

def genInvoiceDCobj(invoice):

  invoiceTup = invoice[0]

  date_issued = datetime.strptime(invoiceTup[3], "%Y-%m-%d")

  invoiceDC = Invoice(
    invoice_id=invoiceTup[0],
    invoice_num=invoiceTup[1],
    amount=invoiceTup[2],
    date_issued=date_issued,
    issued_to=invoiceTup[4],
    customer_id=invoiceTup[5]
  )

  return invoiceDC

def genTransactionDCobj(transaction):

  date_paid = datetime.strptime(transaction[2], "%Y-%m-%d")
  
  transactionDC = Transaction(
    invoice_num=transaction[0][0],
    amount=transaction[1],
    paid_on=date_paid,
    paid_by=transaction[3],
    payment_method=transaction[4],
    og_string=transaction[5]
  )

  return transactionDC