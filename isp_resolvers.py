from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerAliases, getCustomerNamesIDs, addAliasToDB
from isp_popup_window import openTransactionAliasPrompt, openTransactionPaymentErrorPrompt
from isp_data_handlers import constructCustomerAliasesDict

import tkinter as tk

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

def resolvePaymentErrors(paymentErrors):

  nonErrors = []
  errors = []

  for error in paymentErrors:

    transaction = error[0]
    invoice = error[1]

    resolveBool = tk.BooleanVar()
    checkedBool = tk.BooleanVar()

    openTransactionPaymentErrorPrompt()