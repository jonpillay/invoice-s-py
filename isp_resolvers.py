from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerAliases, getCustomerNamesIDs, addAliasToDB
from isp_popup_window import openTransactionAliasPrompt, openTransactionPaymentErrorPrompt
from isp_data_handlers import constructCustomerAliasesDict

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

          print(searchName)

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

  print(errorCount)
  print(len(nameResolved))
  print(len(unMatchable))

  # print(matchNameErrors)

  return nameResolved, unMatchable

def resolvePaymentErrors(root, paymentErrors):

  dummyTransactionUploadTups = []

  errors = []

  while len(paymentErrors) > 0:

    for error in paymentErrors:

      transaction = error[0]
      invoice = error[1]

      print(len(str(transaction.amount)))
      print(len(str(invoice.amount)))

      print(len(paymentErrors))

      checkedBool = tk.BooleanVar()
      resolveBool = tk.BooleanVar()

      resolveString = tk.StringVar()
      noteString = tk.StringVar()

      openTransactionPaymentErrorPrompt(root, invoice, transaction, checkedBool, resolveBool, resolveString, noteString)

      print(noteString.get())

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

        print("check but error")

        errors.append(error)

        paymentErrors.pop(0)

        break