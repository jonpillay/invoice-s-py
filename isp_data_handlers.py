import re
from datetime import datetime
import copy

from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerAliases, getCustomerID, addParentTransactionToDB, fetchUnpaidInvoiceByNum, getCustomerNamesIDs, resolveNewCustomersDB, resolveNameIntoDB



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

          # cashInvoiceTup =  (
          #   invoice.invoice_num,
          #   invoice.amount,
          #   invoice.date_issued,
          #   invoice.issued_to,
          #   invoice.customer_id
          # )

          cashInvoiceUploadTups.append(invoice)

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

          invoiceUploadTups.append(invoice.as_tuple())

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
    invoice_num=int(transaction[0][0]),
    amount=transaction[1],
    paid_on=date_paid,
    paid_by=transaction[3],
    payment_method=transaction[4],
    og_string=transaction[5]
  )

  return transactionDC

def genNoNumTransactionDCobj(transaction):

  date_paid = datetime.strptime(transaction[2], "%Y-%m-%d")
  
  transactionDC = Transaction(
    amount=transaction[1],
    paid_on=date_paid,
    paid_by=transaction[3],
    payment_method=transaction[4],
    og_string=transaction[5]
  )

  return transactionDC

def genMultiTransactionDCobj(transaction):

  date_paid = datetime.strptime(transaction[2], "%Y-%m-%d")
  
  transactionDC = Transaction(
    invoice_num=int(transaction[0][0]),
    amount=transaction[1],
    paid_on=date_paid,
    paid_by=transaction[3],
    payment_method=transaction[4],
    og_string=transaction[5],
    high_invoice=int(transaction[0][1])
  )

  return transactionDC



def genMultiTransactionsInvoices(transactionsList, cur, con):

  transactionUploadList = []
  
  for transaction, invoices in transactionsList:
    
    transactionID = addParentTransactionToDB(transaction.as_tuple(), cur, con)

    for invoice in invoices:

      dummyTransaction = copy.deepcopy(transaction)

      updatedOGstr = "*MULTIDUM* " + dummyTransaction.og_string

      dummyTransaction.invoice_num = invoice.invoice_num
      dummyTransaction.amount = invoice.amount
      dummyTransaction.og_string = updatedOGstr
      dummyTransaction.high_invoice = None
      dummyTransaction.invoice_id = invoice.invoice_id
      dummyTransaction.parent_trans = transactionID

      transactionUploadList.append(dummyTransaction)

  return transactionUploadList


def prepMatchedTransforDB(transaction, invoice):
  transaction.invoice_id = invoice.invoice_id
  transaction.customer_id = invoice.customer_id


def reMatchPaymentErrors(matchPaymentErrors, incompRec, cur):
  # print(matchPaymentErrors[0])
  # print(matchPaymentErrors[1])

  rematched = []

  transactionList = [paymenError[0] for paymenError in matchPaymentErrors]

  for transaction in transactionList:
    invoice = fetchUnpaidInvoiceByNum(transaction.invoice_num, cur)

    if len(invoice) > 0:

      invoiceDC = genInvoiceDCobj(invoice)

      matched = [transaction, invoiceDC]

      rematched.append(matched)
    else:

      if transaction.error_notes == None:
        existNote = ""
      else:
        existNote = transaction.error_notes        

      transaction.error_flagged = 1
      transaction.error_notes = " ".join(["INVOICE NUM ERROR", existNote])

      incompRec.append(transaction)
  
  return rematched, incompRec



def getCustomerIDForTrans(root, transList, cur, con):

  customerIDMemo = {}
  matched = []
  newCustomers = []

  misMatchedCount = len(transList)

  print(misMatchedCount)

  while len(matched) + len(newCustomers) < misMatchedCount:

    for transaction in transList:

      for id in customerIDMemo:
        if transaction.paid_by in customerIDMemo[id]:
          print("here")
          transaction.customer_id = id
          matched.append(transaction)
          transList.pop(0)
          break

      
      if transaction.customer_id is None:
        
        DBCustomers = getCustomerNamesIDs(cur)

        AliasesDict = constructCustomerAliasesDict(cur, DBCustomers)

        customerIDict = constructCustomerIDict(cur, AliasesDict)

        customerIDMemo = dict(customerIDict)

        for id in customerIDict:
          if transaction.paid_by in customerIDict[id]:
            print("here though")
            transaction.customer_id = id
            matched.append(transaction)
            transList.pop(0)
            break


      if transaction.customer_id is None:

        customerID = resolveNameIntoDB(root, transaction.paid_by, DBCustomers, cur, con)

        errorStr = f"{datetime.today().strftime('%Y-%m-%d')} CUSTOMER ADDED TO DATABASE"

        transaction.customer_id = customerID
        transaction.error_flagged = 1
        transaction.error_notes = errorStr

        newCustomers.append(transaction)
        print("heat me now!")
        transList.pop(0)

        break

  return matched, newCustomers