from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerAliases, getCustomerNamesIDs, addAliasToDB
from isp_popup_window import openTransactionAliasPrompt
from isp_data_handlers import constructCustomerAliasesDict

import tkinter as tk

def verifyTransactionDetails(transaction, invoice, cur):

  customerAliases = getCustomerAliases(cur, invoice.customer_id)

  if invoice.issued_to != transaction.paid_by or invoice.issued_to not in customerAliases:
    return f"Name Mismatch {transaction.paid_by} to {invoice.issued_to}"
  elif invoice.amount != transaction.amount:
    return invoice.amount - transaction.amount
  else:
    return True
  
def verifyAlias(transaction, invoice):

  invoiceIDummy = None
  og_string = " ".join(transaction[5])

  frontendTransaction = Transaction(transaction[0][0], transaction[1], transaction[2], transaction[3], transaction[4], og_string, invoiceIDummy)
  frontendInvoice = Invoice(invoice[0], invoice[1], invoice[2], invoice[3], invoice[4])

def resolveNameMismatches(root, cur, conn, matchNameErrors):

  errorCount = len(matchNameErrors)

  unMatchable = []
  nameResolved = []

  while len(nameResolved) + len(unMatchable) < errorCount:

    dbCustomers = getCustomerNamesIDs(cur)

    alisesDict = constructCustomerAliasesDict(cur, dbCustomers)

    for error in matchNameErrors:
      
      transaction = error[0]
      invoice = error[1]

      if transaction.paid_by in alisesDict[invoice.issued_to]:
        nameResolved.append(error)
        matchNameErrors.pop(0)

        # Whilst I don't think technically needed, I added the break here to reset the loop after popping an element.
        break

      else:

        aliasBool = tk.BooleanVar()
        rejectedBool = tk.BooleanVar()

        openTransactionAliasPrompt(root, invoice, transaction, aliasBool)

        if aliasBool.get() == True:

          for customer, aliases in alisesDict:
            if invoice.issued_to in aliases:
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

        elif aliasBool == False and rejectedBool == True:
          
          unMatchable.append(error)
          matchNameErrors.pop(0)
          break

        else:
          break


      # Prompt user if the name mismatch is an error

      # Prompt should set some TKVars

      # If alias is found, should add alias to DB and rerun check on all elements in matchNameErrors list
      # First building a new aliases dict with result and resolving for that.

      # If the alias is not a match then the error pair should be put into unMatchable