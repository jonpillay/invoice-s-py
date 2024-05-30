from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerID, fetchRangeInvoicesByCustomer, getCustomerNamesIDs, addAliasToDB, addNewCustomerToDB, addTransactionToDB, findCustomerIDInTup, fetchUnpaidInvoicesByCustomerDateRange, fetchUnpaidInvoicesByCustomerBeforeDate
from isp_popup_window import openTransactionAliasPrompt, openTransactionPaymentErrorPrompt, openNewCustomerPrompt
from isp_data_handlers import constructCustomerAliasesDict, genInvoiceDCobj, genNoNumTransactionDCobj, prepMatchedTransforDB, constructCustomerIDict, getCustomerIDForTrans, prepNewlyMatchedTransactionForDB
from isp_data_comparers import compareCustomerToAliasesDict, getCustomerDBName
from isp_multi_invoice_prompt import openMultiInvoicePrompt, openSelectBetweenInvoices
from isp_trans_verify import verifyTransactionAmount
from isp_close_enough_prompts import openVerifyCloseEnoughtMatch, openSelectBetweenCloseEnoughInvoices

import tkinter as tk
from datetime import datetime

def resolveNameMismatches(root, cur, conn, matchNameErrors):

  errorCount = len(matchNameErrors)

  print(errorCount)

  unMatchable = []
  nameResolved = []

  while len(nameResolved) + len(unMatchable) < errorCount:

    dbCustomers = getCustomerNamesIDs(cur)

    aliasesDict = constructCustomerAliasesDict(cur, dbCustomers)

    for error in matchNameErrors:
      
      transaction = error[0]
      invoice = error[1]

      if transaction.paid_by in aliasesDict[invoice.issued_to]:

        print(transaction.paid_by)
        print(aliasesDict[invoice.issued_to])

        prepMatchedTransforDB(error[0], error[1])

        nameResolved.append(error)
        matchNameErrors.pop(0)

        # Whilst I don't think technically needed, I added the break here to reset the loop after popping an element.
        break

      else:

        aliasBool = tk.BooleanVar()
        rejectedBool = tk.BooleanVar()

        openTransactionAliasPrompt(root, invoice, transaction, aliasBool, rejectedBool)

        if aliasBool.get() == True:

          # for customer in alisesDict:
          #   if invoice.issued_to in alisesDict[customer]:
          #     searchName = customer
          #   else:
          #     searchName = invoice.issued_to

          addAliasToDB(transaction.paid_by, invoice.customer_id, cur)

          conn.commit()

          prepMatchedTransforDB(error[0], error[1])

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

          con.commit()

          namesList.pop(0)

          resolvedCount += 1

          break

        elif customerName != "" and customerName != name:
          
          addNewCustomerToDB(customerName, cur)

          con.commit()

          customerID = cur.lastrowid

          addAliasToDB(name, customerID, cur)

          con.commit()

          namesList.pop(0)

          resolvedCount += 1

          break

          # This also needs to add the original invoice name as a customer alias for the newly created customer entry.


def resolvePaymentErrors(root, paymentErrors):

  print("Start of resolvePaymentErrors")

  errorCount = len(paymentErrors)

  dummyTransactionUploadTups = []

  errors = []

  while len(dummyTransactionUploadTups) + len(errors) < errorCount:

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

        prepMatchedTransforDB(error[0], error[1])

        if resolveString.get() == "CASH":
          methodStr = "CORDUM (CASH)"
        elif resolveString.get() == "BACS":
          methodStr = "CORDUM (BACS)"
        
        correctionAmount = 0 - (invoice.amount - transaction.amount)

        dummyTransaction = Transaction(
          invoice_num=transaction.invoice_num,
          amount=correctionAmount,
          paid_on=datetime.today().strftime('%Y-%m-%d'),
          paid_by=transaction.paid_by,
          payment_method=methodStr,
          og_string=transaction.og_string,
          error_notes=noteString.get(),
          invoice_id=transaction.invoice_id,
          customer_id=transaction.customer_id
        )
        
        uploadTuple = (error, dummyTransaction)

        dummyTransactionUploadTups.append(uploadTuple)

        paymentErrors.pop(0)

        break
      
      elif checkedBool.get() == True and resolveBool.get() == False:

        transaction.error_flagged = 1

        transaction.error_notes = f"Transaction Invoice # Error - {noteString.get()}"

        errors.append(transaction)

        paymentErrors.pop(0)

        break

  return dummyTransactionUploadTups, errors



def resolveMultiInvoiceTransactions(root, cur, con, multiRecs):
  
  namesList = list(set([rec.paid_by.strip().upper() for rec in multiRecs]))

  resolveNamesIntoDB(root, cur, con, namesList)

  dbCustomers = getCustomerNamesIDs(cur)
  aliasesDict = constructCustomerAliasesDict(cur, dbCustomers)

  multiInvoiceMatches = []

  multiInvoiceErrors = []

  for rec in multiRecs:
    
    searchCustomer = getCustomerDBName(aliasesDict, rec.paid_by)

    customerID = getCustomerID(cur, searchCustomer)
    
    invoices = fetchRangeInvoicesByCustomer(rec.invoice_num, rec.high_invoice, customerID, cur)

    invoiceOBJs = [genInvoiceDCobj(invoice) for invoice in invoices]

    totalInvoiced = sum([invoice.amount for invoice in invoiceOBJs])

    # Needs to be a close enough, with a tollerance of maybe 1 pound (tollerance should maybe be set relatively to the amount of invoices being paid for.)

    if round(totalInvoiced, 2) == rec.amount:

      matchTuple = (rec, invoiceOBJs)

      multiInvoiceMatches.append(matchTuple)
    else:
      errorTuple = (rec, invoiceOBJs)

      multiInvoiceErrors.append(errorTuple)

  matchCount = len(multiInvoiceMatches)

  multiVerified = []
  multiErrorFlagged = []

  while len(multiVerified) + len(multiErrorFlagged) < matchCount:

    for checkTrans, checkInvoices in multiInvoiceMatches:

      # checkTrans = multiInvoice[0]
      # checkInvoices = multiInvoice[1]

      checkedBool = tk.BooleanVar()
      verifyBool = tk.BooleanVar()

      openMultiInvoicePrompt(root, checkTrans, checkInvoices, checkedBool, verifyBool)

      if checkedBool.get() == False:
        break
      else:
        if verifyBool.get() == True:
          checkTrans.customer_id = checkInvoices[0].customer_id

          verifiedTuple = (checkTrans, checkInvoices)

          multiVerified.append(verifiedTuple)
          multiInvoiceMatches.pop(0)
          break
        elif verifyBool.get() == False:
          
          errorList =[checkTrans, checkInvoices]

          multiErrorFlagged.append(errorList)
          multiInvoiceMatches.pop(0)
          break
  
  return multiVerified, multiErrorFlagged, multiInvoiceErrors



def resolveNoMatchTransactions(root, incompTransactions, cur, con):

  existingCustomerTransactions, newCustomersTransactions = getCustomerIDForTrans(root, incompTransactions, cur, con)

  matched = []
  noMatches = []

  transactionCount = len(existingCustomerTransactions)

  paidInvoiceMemo = []

  while len(matched) + len(noMatches) < transactionCount:

    for transaction in existingCustomerTransactions:

      candInvoices = fetchUnpaidInvoicesByCustomerBeforeDate(transaction.paid_on, transaction.customer_id, cur)

      if len(candInvoices) == 0:
        noMatches.append(transaction)
        existingCustomerTransactions.pop(0)
        print("here innit")
        break

      formattedInvoices = [genInvoiceDCobj(curInvoice) for curInvoice in candInvoices]

      paymentMatches = [customerInvoice for customerInvoice in formattedInvoices if verifyTransactionAmount(transaction, customerInvoice, 0.01) == True and customerInvoice.invoice_num not in paidInvoiceMemo]

      print(paymentMatches)

      if len(paymentMatches) == 1:

        matchedInvoice = paymentMatches[0]

        preppedTransaction = prepNewlyMatchedTransactionForDB(transaction, matchedInvoice)

        transactionTuple = preppedTransaction.as_tuple()

        addTransactionToDB(transactionTuple, con, cur)

        paidInvoiceMemo.append(matchedInvoice.invoice_num)

        matched.append([preppedTransaction, matchedInvoice])

        existingCustomerTransactions.pop(0)
        break

      if len(paymentMatches) > 1:

        chosenInvoiceID = tk.IntVar(value=0)

        openSelectBetweenInvoices(root, transaction, paymentMatches, chosenInvoiceID)

        invoiceID = chosenInvoiceID.get()

        if invoiceID == 0:
          noMatches.append(transaction)
          existingCustomerTransactions.pop(0)
          break
        else:
          selectedInvoice = [possInvoice for possInvoice in paymentMatches if possInvoice.invoice_num == invoiceID][0]

          paidInvoiceMemo.append(selectedInvoice.invoice_num)

          preppedTransaction = prepNewlyMatchedTransactionForDB(transaction, selectedInvoice)

          transactionTuple = preppedTransaction.as_tuple()

          addTransactionToDB(transactionTuple, con, cur)

          matched.append([preppedTransaction, selectedInvoice])

          existingCustomerTransactions.pop(0)

          break

      if len(paymentMatches) == 0:

        closeEnoughMatched = [closeEnoughInvoice for closeEnoughInvoice in formattedInvoices if verifyTransactionAmount(transaction, closeEnoughInvoice, 100) == True and closeEnoughInvoice.invoice_num not in paidInvoiceMemo]

        if len(closeEnoughMatched) == 1:

          matchVerifiedBool = tk.BooleanVar()

          openVerifyCloseEnoughtMatch(root, transaction, closeEnoughMatched[0], matchVerifiedBool)

          if matchVerifiedBool.get() == True:

            paidInvoiceMemo.append(closeEnoughMatched[0].invoice_num)

            preppedTransaction = prepNewlyMatchedTransactionForDB(transaction, closeEnoughMatched[0])

            transactionTuple = preppedTransaction.as_tuple()

            addTransactionToDB(transactionTuple, con, cur)

            matched.append([preppedTransaction, closeEnoughMatched[0]])

            existingCustomerTransactions.pop(0)

            break
        
        if len(closeEnoughMatched) > 1:

          # Error here where for some reason I had a loop. Need to write popup to verify between close enoughs

          invoiceIDVar = tk.IntVar()

          print(closeEnoughMatched)

          openSelectBetweenCloseEnoughInvoices(root, transaction, closeEnoughMatched, invoiceIDVar)

          invoiceID = chosenInvoiceID.get()

          if invoiceID == 0:
            noMatches.append(transaction)
            existingCustomerTransactions.pop(0)
            break
          else:
            selectedInvoice = [possInvoice for possInvoice in paymentMatches if possInvoice.invoice_num == invoiceID][0]

            paidInvoiceMemo.append(selectedInvoice.invoice_num)

            preppedTransaction = prepNewlyMatchedTransactionForDB(transaction, selectedInvoice)

            transactionTuple = preppedTransaction.as_tuple()

            addTransactionToDB(transactionTuple, con, cur)

            matched.append([preppedTransaction, selectedInvoice])

            existingCustomerTransactions.pop(0)

            break
        


  [print(i) for i in matched]
  [print(i) for i in noMatches]  

  return matched, noMatches, newCustomersTransactions