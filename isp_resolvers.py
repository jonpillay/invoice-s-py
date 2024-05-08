from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerAliases, getCustomerNamesIDs, addAliasToDB, addNewCustomerToDB, findCustomerIDInTup
from isp_popup_window import openTransactionAliasPrompt, openTransactionPaymentErrorPrompt, openNewCustomerPrompt
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

  while len(namesList) > 0:

    dbCustomers = getCustomerNamesIDs(cur)
    alisesDict = constructCustomerAliasesDict(cur, dbCustomers)

    for name in namesList:
      for customer in alisesDict:
        if name.strip().upper() == customer.strip().upper():
          namesList.pop(0)
          break
        elif name.strip().upper() in alisesDict[customer]:
          namesList.pop(0)
          break
        else:
          newCustomerReturn = tk.StringVar()

          newAliasReturn = tk.StringVar()

          openNewCustomerPrompt(root, name, dbCustomers, newCustomerReturn, newAliasReturn)

          customerName = newCustomerReturn.get()

          aliasName = newAliasReturn.get()

          if customerName != "" and customerName == customer:

            print("It took us here")

            addNewCustomerToDB(customer, cur)

            print(cur.lastrowid)

            con.commit()

          elif aliasName != "":

            customerID = findCustomerIDInTup(aliasName, dbCustomers)

            addAliasToDB(customer, customerID, cur)

            print(cur.lastrowid)

            con.commit()

          elif customerName != "" and customerName != customer:
            
            addNewCustomerToDB(customerName, cur)

            customerID = cur.lastrowid

            print(cur.lastrowid)

            con.commit()

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

  print(namesList)

  resolveNamesIntoDB(root, cur, con, namesList)

