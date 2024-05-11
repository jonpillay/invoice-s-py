from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerID, fetchRangeInvoicesByCustomer, getCustomerNamesIDs, addAliasToDB, addNewCustomerToDB, findCustomerIDInTup
from isp_popup_window import openTransactionAliasPrompt, openTransactionPaymentErrorPrompt, openNewCustomerPrompt
from isp_data_handlers import constructCustomerAliasesDict, genInvoiceDCobj
from isp_data_comparers import compareCustomerToAliasesDict, getCustomerDBName
from isp_multi_invoice_prompt import openMultiInvoicePrompt

import tkinter as tk
import datetime

def resolveNameMismatches(root, cur, conn, matchNameErrors):

  errorCount = len(matchNameErrors)

  print(errorCount)

  unMatchable = []
  nameResolved = []

  while len(nameResolved) + len(unMatchable) < errorCount:

    dbCustomers = getCustomerNamesIDs(cur)

    alisesDict = constructCustomerAliasesDict(cur, dbCustomers)

    for error in matchNameErrors:
      
      transaction = error[0]
      invoice = error[1]

      if transaction.paid_by in alisesDict[invoice.issued_to]:

        for id, name in dbCustomers:
            if invoice.issued_to == name:
              customerID = id

        nameResolved.append(error)
        matchNameErrors.pop(0)

        # Whilst I don't think technically needed, I added the break here to reset the loop after popping an element.
        break

      else:

        aliasBool = tk.BooleanVar()
        rejectedBool = tk.BooleanVar()

        openTransactionAliasPrompt(root, invoice, transaction, aliasBool, rejectedBool)

        if aliasBool.get() == True:

          for customer in alisesDict:
            if invoice.issued_to in alisesDict[customer]:
              searchName = customer
            else:
              searchName = invoice.issued_to

          for id, name in dbCustomers:
            if searchName == name:
              customerID = id

          addAliasToDB(transaction.paid_by, customerID, cur)

          conn.commit()

          nameResolved.append(error)
          matchNameErrors.pop(0)
          break

        elif aliasBool.get() == False and rejectedBool.get() == True:

          unMatchable.append(error)
          matchNameErrors.pop(0)
          break

        else:
          break

  # print(matchNameErrors)

  return nameResolved, unMatchable


def resolveNamesIntoDB(root, cur, con, namesList):

  nameCount = len(namesList)

  resolvedCount = 0

  while nameCount > resolvedCount:

    for name in namesList:

      dbCustomers = getCustomerNamesIDs(cur)
      alisesDict = constructCustomerAliasesDict(cur, dbCustomers)

      nameCheck = compareCustomerToAliasesDict(name, alisesDict)

      if nameCheck == True:

        resolvedCount += 1

        continue

      else:
        newCustomerReturn = tk.StringVar()

        newAliasReturn = tk.StringVar()

        openNewCustomerPrompt(root, name, dbCustomers, newCustomerReturn, newAliasReturn)

        customerName = newCustomerReturn.get()

        aliasName = newAliasReturn.get()

        if customerName != "" and customerName.strip().upper() == name.strip().upper():

          addNewCustomerToDB(name, cur)

          con.commit()

          namesList.pop(0)

          resolvedCount += 1

          break

        elif aliasName != "":

          customerID = findCustomerIDInTup(aliasName, dbCustomers)

          addAliasToDB(name, customerID, cur)

          print(cur.lastrowid)

          con.commit()

          namesList.pop(0)

          resolvedCount += 1

          break

        elif customerName != "" and customerName != name:
          
          addNewCustomerToDB(customerName, cur)

          con.commit()

          customerID = cur.lastrowid

          addAliasToDB(name, customerID, cur)

          print(cur.lastrowid)

          con.commit()

          namesList.pop(0)

          resolvedCount += 1

          break

          # This also needs to add the original invoice name as a customer alias for the newly created customer entry.


def resolvePaymentErrors(root, paymentErrors):

  dummyTransactionUploadTups = []

  errors = []

  while len(paymentErrors) > 0:

    for error in paymentErrors:

      transaction = error[0]
      invoice = error[1]

      checkedBool = tk.BooleanVar()
      resolveBool = tk.BooleanVar()

      resolveString = tk.StringVar()
      noteString = tk.StringVar()

      openTransactionPaymentErrorPrompt(root, invoice, transaction, checkedBool, resolveBool, resolveString, noteString)


      if checkedBool.get() == False:
        break

      elif checkedBool.get() == True and resolveBool.get() == True:

        if resolveString.get() == "CASH":
          methodStr = "DUMMY (CASH)"
        elif resolveString.get() == "BACS":
          methodStr = "DUMMY (BACS)"
        
        correctionAmount = 0 - (invoice.amount - transaction.amount)
        
        dummyTransaction = Transaction(invoice.invoice_num, correctionAmount, datetime.date.now(), transaction.paid_by, methodStr, noteString.get(), invoice.invoice_id, invoice.customer_id)

        uploadTuple = (error, dummyTransaction)

        dummyTransactionUploadTups.append(uploadTuple)

        paymentErrors.pop(0)

        break
      
      elif checkedBool.get() == True and resolveBool.get() == False:

        invoice.error_flagged = 1

        invoice.error_notes = noteString.get()

        errors.append(error)

        paymentErrors.pop(0)

        break

  return dummyTransactionUploadTups, errors



def resolveMultiInvoiceTransactions(root, cur, con, multiRecs):
  
  namesList = list(set([rec[3].strip().upper() for rec in multiRecs]))

  resolveNamesIntoDB(root, cur, con, namesList)

  dbCustomers = getCustomerNamesIDs(cur)
  aliasesDict = constructCustomerAliasesDict(cur, dbCustomers)

  print(len(multiRecs))

  for rec in multiRecs:
    
    searchCustomer = getCustomerDBName(aliasesDict, rec[3])

    customerID = getCustomerID(cur, searchCustomer)
    
    invoices = fetchRangeInvoicesByCustomer(rec[0][0], rec[0][1], customerID, cur)

    invoiceOBJs = [genInvoiceDCobj([invoice]) for invoice in invoices]

    totalInvoiced = sum([invoice.amount for invoice in invoiceOBJs])

    multiInvoiceMatches = []

    multiInvoiceErrors = []

    if round(totalInvoiced, 2) == rec[1]:
      matchTuple = (rec, invoiceOBJs)

      multiInvoiceMatches.append(matchTuple)
    else:
      errorTuple = (rec, invoiceOBJs)

      multiInvoiceErrors.append(errorTuple)

  errorBool = tk.BooleanVar()

  openMultiInvoicePrompt(root, rec, invoiceOBJs)


def resolveMultiInvTransErrors():
  pass