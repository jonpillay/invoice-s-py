import tkinter as tk
import re
from datetime import datetime
import copy
from collections import defaultdict

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

  # print(invoice)

  date_issued = datetime.strptime(invoice[3], "%Y-%m-%d")

  invoiceDC = Invoice(
    invoice_id=invoice[0],
    invoice_num=invoice[1],
    amount=invoice[2],
    date_issued=date_issued,
    issued_to=invoice[4],
    customer_id=invoice[5]
  )

  return invoiceDC


def genDBInvoiceDCobj(invoice):

  date_issued = datetime.strptime(invoice[3], "%Y-%m-%d")

  invoiceDC = Invoice(
    invoice_id=invoice[0],
    invoice_num=invoice[1],
    amount=invoice[2],
    date_issued=date_issued,
    issued_to=invoice[4],
    error_flagged=invoice[5],
    error_notes=invoice[6],
    customer_id=invoice[7]
  )

  return invoiceDC

def genTransactionDCobj(transaction):

  date_paid = datetime.strptime(transaction[2], "%Y-%m-%d")
  
  transactionDC = Transaction(
    invoice_num=int(transaction[0]),
    amount=transaction[1],
    paid_on=date_paid,
    paid_by=transaction[3],
    payment_method=transaction[4],
    og_string=transaction[5]
  )

  return transactionDC

def genDBTransactionDCobj(transaction):

  try:
    date_paid = datetime.strptime(transaction[3], "%Y-%m-%d %H:%M:%S")
  except ValueError:
      date_paid = datetime.strptime(transaction[3], "%Y-%m-%d")

  invoiceNum = None

  if transaction[1] == None:
    invoiceNum = transaction[1]
  else:
    invoiceNum = int(transaction[1])
  
  transactionDC = Transaction(
    transaction_id=transaction[0],
    invoice_num=invoiceNum,
    amount=transaction[2],
    paid_on=date_paid,
    paid_by=transaction[4],
    payment_method=transaction[5],
    og_string=transaction[6],
    error_flagged=transaction[7],
    error_notes=transaction[8],
    high_invoice=transaction[9],
    invoice_id=transaction[10],
    customer_id=transaction[11],
    parent_trans=transaction[12]
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



def genMultiTransactions(multiTransInvPairs, cur, con):

  """
  
  takes verified multi invoice transactions and the invoices they pay for and
  creates dummy transactions to pay for each, uploading the parent transaction
  and retrieving its databae id to be added to the dummy transactions.

  returns

  uploadedMultiTransactionPairs - list of two lists. The first containing the
  parent transaction as its first element, followed by the created dummy transactions.
  With the second list containing the invoices paid for. For reporting.

  transactionUploadList - list of the newly created dummy transactions for upload.



  """  

  dummyTransactionUploadList = []

  uploadedMultiTransactionPairs = []
  
  for transaction, invoices in multiTransInvPairs:

    multiInvoiceTransactionGroup = []

    parentTransaction = transaction

    multiInvoiceTransactionGroup.append(parentTransaction)
    
    transactionID = addParentTransactionToDB(transaction.as_tuple(), cur, con)

    parentTransaction.transaction_id = transactionID

    invTransPairs = []

    for invoice in invoices:

      dummyTransaction = copy.deepcopy(transaction)

      updatedOGstr = "*MULTIDUM* " + dummyTransaction.og_string

      dummyTransaction.invoice_num = invoice.invoice_num
      dummyTransaction.amount = invoice.amount
      dummyTransaction.og_string = updatedOGstr
      dummyTransaction.high_invoice = None
      dummyTransaction.invoice_id = invoice.invoice_id
      dummyTransaction.parent_trans = transactionID
      dummyTransaction.transaction_id = None

      dummyTransactionUploadList.append(dummyTransaction)

      invTransPairs.append([invoice, dummyTransaction])

    multiInvoiceTransactionGroup.append(invTransPairs)

    uploadedMultiTransactionPairs.append(multiInvoiceTransactionGroup)

  return dummyTransactionUploadList, uploadedMultiTransactionPairs


def prepMatchedTransforDB(transaction, invoice):
  transaction.invoice_id = invoice.invoice_id
  transaction.customer_id = invoice.customer_id
  transaction.invoice_num = invoice.invoice_num



def reMatchPaymentErrors(matchPaymentErrors, cur):
  # print(matchPaymentErrors[0])
  # print(matchPaymentErrors[1])

  rematched = []
  noMatch = []

  transactionList = [paymenError[0] for paymenError in matchPaymentErrors]

  for transaction in transactionList:
    
    invoice = fetchUnpaidInvoiceByNum(transaction.invoice_num, cur)

    if len(invoice) > 0:

      invoiceDC = genInvoiceDCobj(invoice[0])

      matched = [transaction, invoiceDC]

      rematched.append(matched)
    else:

      if transaction.error_notes == None:
        existNote = ""
      else:
        existNote = transaction.error_notes

      transaction.error_flagged = 1
      transaction.error_notes = " ".join(["INVOICE NUM ERROR", existNote])

      noMatch.append(transaction)
  
  return rematched, noMatch



def getCustomerIDForTrans(root, transList, cur, con):

  customerIDMemo = {}
  newCustomerNamesMemo = []

  matched = []
  newCustomerTransactions = []

  misMatchedCount = len(transList)

  while len(matched) + len(newCustomerTransactions) < misMatchedCount:

    for transaction in transList:

      if transaction.paid_by in newCustomerNamesMemo:
        newCustomerTransactions.append(transaction)
        transList.pop(0)
        break

      idListMemo = [id for id, names in customerIDMemo.items() if transaction.paid_by in names]

      if len(idListMemo) > 0:
        transaction.customer_id = idListMemo[0]
        matched.append(transaction)
        transList.pop(0)
        break

      # for id in customerIDMemo:
      #   if transaction.paid_by in customerIDMemo[id]:

      #     transaction.customer_id = id
      #     matched.append(transaction)
      #     transList.pop(0)
      #     break


      if transaction.customer_id is None:
        
        DBCustomers = getCustomerNamesIDs(cur)

        AliasesDict = constructCustomerAliasesDict(cur, DBCustomers)

        customerIDict = constructCustomerIDict(cur, AliasesDict)

        customerIDMemo = dict(customerIDict)

        idListDict = [id for id, names in customerIDict.items() if transaction.paid_by in names]

        if len(idListDict) > 0:
          transaction.customer_id = idListDict[0]
          matched.append(transaction)
          transList.pop(0)
          break

        # for id in customerIDict:
        #   if transaction.paid_by in customerIDict[id]:

        #     transaction.customer_id = id
        #     matched.append(transaction)
        #     transList.pop(0)
        #     break


      if transaction.customer_id is None:

        newCustomerBool = tk.BooleanVar()

        customerID = resolveNameIntoDB(root, transaction.paid_by, DBCustomers, newCustomerBool, cur, con)

        if newCustomerBool.get() == True:

          errorStr = f"{datetime.today().strftime('%d-%m-%Y')} CUSTOMER ADDED TO DATABASE - NO INVOICE PRESENT"

          transaction.customer_id = customerID
          transaction.error_flagged = 1
          transaction.error_notes = errorStr

          newCustomerNamesMemo.append(transaction.paid_by)
          newCustomerTransactions.append(transaction)

          transList.pop(0)
          break
        
        else:
          transaction.customer_id = customerID
          matched.append(transaction)

          transList.pop(0)
          break

  return matched, newCustomerTransactions

def prepNewlyMatchedTransactionForDB(transaction, invoice):

  prepMatchedTransforDB(transaction, invoice)

  transaction.invoice_num = invoice.invoice_num
  transaction.invoice_id = invoice.invoice_id
  transaction.customer_id = invoice.customer_id
  transaction.error_flagged = None
  transaction.error_notes = None

  return transaction

def prepNewlyMatchedErrorTransactionForDB(transaction, invoice):

  prepMatchedTransforDB(transaction, invoice)

  transaction.invoice_num = invoice.invoice_num
  transaction.invoice_id = invoice.invoice_id
  transaction.customer_id = invoice.customer_id

  return transaction



def groupDataClassObjsByAttribute(DCList, attribute):

  attrGroup = defaultdict(list)

  for DC in DCList:

    customer_id = getattr(DC, attribute)

    attrGroup[customer_id].append(DC)

  return attrGroup.values()

def groupDataClassObjsByAttribute(DCList, attribute):

  attrGroup = defaultdict(list)

  for DC in DCList:

    customer_id = getattr(DC, attribute)

    attrGroup[customer_id].append(DC)

  return attrGroup.values()