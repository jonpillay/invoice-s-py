from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerID, fetchRangeInvoicesByCustomer, getCustomerNamesIDs, addAliasToDB, addNewCustomerToDB, addTransactionToDB, findCustomerIDInTup, fetchUnpaidInvoicesByCustomerDateRange, fetchUnpaidInvoicesByCustomerBeforeDate, updateInvoiceRec, addDummyTransactionsToDB, addDummyNoteTransactionsToDB, addErrorTransactionToDB
from isp_popup_window import openTransactionAliasPrompt, openTransactionPaymentErrorPrompt, openNewCustomerPrompt
from isp_data_handlers import constructCustomerAliasesDict, genInvoiceDCobj, genNoNumTransactionDCobj, prepMatchedTransforDB, constructCustomerIDict, getCustomerIDForTrans, prepNewlyMatchedTransactionForDB, prepNewlyMatchedErrorTransactionForDB, genMultiTransactions
from isp_data_comparers import compareCustomerToAliasesDict, getCustomerDBName
from isp_multi_invoice_prompt import openMultiInvoicePrompt, openMatchedMultiInvoicePrompt, openSelectBetweenInvoices
from isp_trans_verify import verifyTransactionAmount
from isp_close_enough_prompts import openVerifyCloseEnoughtMatch, openSelectBetweenCloseEnoughInvoices

import tkinter as tk
from datetime import datetime

def resolveNameMismatches(root, cur, conn, matchNameErrors):

  """
  
  Getting double transaction records. With IDs jusmping 23, and then if shows again 22, think I have a problem with a loop,
  I think it may be this loop. Will start with testing the length of matchNameErrors... in the morning.
  
  """

  errorCount = len(matchNameErrors)
  print("this is the error count we are interested in")
  print(matchNameErrors)

  unMatchable = []
  nameResolved = []
  
  # need a list to be returned for resolved names, but with payment error
  paymentErrors = []

  index = 0

  for error in matchNameErrors:

    dbCustomers = getCustomerNamesIDs(cur)

    aliasesDict = constructCustomerAliasesDict(cur, dbCustomers)
      
    transaction = error[0]
    invoice = error[1]
    
    for name in aliasesDict:

      if transaction.paid_by in aliasesDict[name] or transaction.paid_by == name:

        if transaction.amount == invoice.amount:

          prepMatchedTransforDB(error[0], error[1])

          nameResolved.append(error)
          index += 1

          break

        else:

          paymentErrors.append([transaction, invoice])
          index += 1

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

        if transaction.amount == invoice.amount:

          prepMatchedTransforDB(error[0], error[1])

          nameResolved.append(error)
          index += 1
          continue

        else:

          paymentErrors.append([transaction, invoice])
          index += 1

          continue

      elif aliasBool.get() == False and rejectedBool.get() == True:

        unMatchable.append(error)
        index += 1
        continue

      else:
        continue

  return nameResolved, unMatchable, paymentErrors



def resolveNamesIntoDB(root, cur, con, namesList):

  for name in namesList:

    dbCustomers = getCustomerNamesIDs(cur)
    alisesDict = constructCustomerAliasesDict(cur, dbCustomers)

    nameCheck = compareCustomerToAliasesDict(name, alisesDict)

    if nameCheck == True:

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


      elif aliasName != "":

        customerID = findCustomerIDInTup(aliasName, dbCustomers)

        addAliasToDB(name, customerID, cur)

        con.commit()


      elif customerName != "" and customerName != name:
        
        addNewCustomerToDB(customerName, cur)

        con.commit()

        customerID = cur.lastrowid

        addAliasToDB(name, customerID, cur)

        con.commit()

        # This also needs to add the original invoice name as a customer alias for the newly created customer entry.





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

    # Needs to be a close enough, with a tolerance of maybe 1 pound (tolerance should maybe be set relatively to the amount of invoices being paid for.)

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
          
          errorList = [checkTrans, checkInvoices]

          multiErrorFlagged.append(errorList)
          multiInvoiceMatches.pop(0)
          break
  
  return multiVerified, multiErrorFlagged, multiInvoiceErrors




def resolvePaymentErrors(root, paymentErrors, cur, con):

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
        
        correctionAmount = round((invoice.amount - transaction.amount), 2)

        dummyTransaction = Transaction(
          amount=correctionAmount,
          paid_on=transaction.paid_on,
          paid_by=transaction.paid_by,
          payment_method=methodStr,
          og_string=transaction.og_string,
          invoice_num=transaction.invoice_num,
          error_notes=noteString.get(),
          invoice_id=transaction.invoice_id,
          customer_id=transaction.customer_id
        )

        error[0].error_flagged = 1
        error[0].error_notes = f"CORRECTED BY = {correctionAmount}"

        invoiceErrorStr = f"CORRECTED BY = {correctionAmount}"

        updateInvoiceRec(invoice.invoice_id, "error_flagged", "1", cur, con)
        updateInvoiceRec(invoice.invoice_id, "error_notes", invoiceErrorStr, cur, con)
        
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







def resolveNoMatchTransactions(root, incompTransactions, cur, con):

  """
  Takes transactions that have either no invoice number or an invoice number which has been flagged as incorrect.

  First attempts to match the transaction via amount against single unpaid invoices.

  Secondly attempting to match two or more unpaid invoices.

  Finally an attempt is made to match the transaction to an invoice, but giving a tolerance to the match amount
  
  """

  existingCustomerTransactions, newCustomersTransactions = getCustomerIDForTrans(root, incompTransactions, cur, con)


  matched = []
  noMatches = []
  multiMatched = []

  transactionCount = len(existingCustomerTransactions)

  paidInvoiceMemo = []

  while len(matched) + len(noMatches) < transactionCount:

    for transaction in existingCustomerTransactions:

      # fetch all unpaid invoices, if there are zero unpaid then append the transaction to noMatches and move on

      candInvoices = fetchUnpaidInvoicesByCustomerBeforeDate(transaction.paid_on, transaction.customer_id, cur)

      if len(candInvoices) == 0:
        noMatches.append(transaction)
        existingCustomerTransactions.pop(0)
        break

      formattedInvoices = [genInvoiceDCobj(curInvoice) for curInvoice in candInvoices]

      paymentMatches = [customerInvoice for customerInvoice in formattedInvoices if verifyTransactionAmount(transaction, customerInvoice, 0.01) == True and customerInvoice.invoice_num not in paidInvoiceMemo]

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

        runningInvoiceTotal = 0
        candMultiInvoiceGroup = []

        for candInvoice in formattedInvoices:

          candMultiInvoiceGroup.append(candInvoice)

          runningInvoiceTotal += candInvoice.amount

          if runningInvoiceTotal > transaction.amount:
            break

          if runningInvoiceTotal == transaction.amount:

            verifyBool = tk.BooleanVar()
            
            openMatchedMultiInvoicePrompt(root, transaction, candMultiInvoiceGroup, verifyBool)

            if verifyBool.get() == True:

              dummyTransactions, uploadedMultiTransactionPairs = genMultiTransactions([(transaction, candMultiInvoiceGroup)], cur, con)

              dummyTransactionTuples = [dummyTrans.as_tuple() for dummyTrans in dummyTransactions]

              addDummyTransactionsToDB(dummyTransactionTuples, cur, con)

              con.commit()

              multiMatched.append([transaction, candMultiInvoiceGroup])

              existingCustomerTransactions.pop(0)
              
              break

        # start of trying to match the transaction to a single invoice, but allowing for a tolerance in matching the amount

        closeEnoughMatched = [closeEnoughInvoice for closeEnoughInvoice in formattedInvoices if verifyTransactionAmount(transaction, closeEnoughInvoice, 1) == True and closeEnoughInvoice.invoice_num not in paidInvoiceMemo]

        if len(closeEnoughMatched) == 0:
          noMatches.append(transaction)
          existingCustomerTransactions.pop(0)
          break

        if len(closeEnoughMatched) == 1:

          matchVerifiedBool = tk.BooleanVar()

          invoice = closeEnoughMatched[0]

          openVerifyCloseEnoughtMatch(root, transaction, invoice, matchVerifiedBool)

          if matchVerifiedBool.get() == True:

            paidInvoiceMemo.append(invoice.invoice_num)

            correctionAmount = round((invoice.amount - transaction.amount), 2)

            transaction.error_flagged = 1
            transaction.error_notes = f"CORRECTED BY = {correctionAmount}"

            preppedTransaction = prepNewlyMatchedErrorTransactionForDB(transaction, invoice)

            transactionTuple = preppedTransaction.as_tuple()

            parentID = addErrorTransactionToDB(transactionTuple, con, cur)

            dummyTransaction = Transaction(
              amount=correctionAmount,
              paid_on=transaction.paid_on,
              paid_by=transaction.paid_by,
              payment_method="CORDUM",
              error_notes=f"CORRECTION BY {correctionAmount}",
              og_string=transaction.og_string,
              invoice_num=transaction.invoice_num,
              invoice_id=transaction.invoice_id,
              customer_id=transaction.customer_id,
              parent_trans=parentID
            )

            addDummyNoteTransactionsToDB([dummyTransaction.as_tuple()], con, cur)

            invoiceErrorStr = f"CORRECTED BY = {correctionAmount}"

            updateInvoiceRec(invoice.invoice_id, "error_flagged", "1", cur, con)
            updateInvoiceRec(invoice.invoice_id, "error_notes", invoiceErrorStr, cur, con)

            matched.append([preppedTransaction, closeEnoughMatched[0], correctionAmount])

            existingCustomerTransactions.pop(0)

            break
        
        if len(closeEnoughMatched) > 1:

          invoiceIDVar = tk.IntVar()

          openSelectBetweenCloseEnoughInvoices(root, transaction, closeEnoughMatched, invoiceIDVar)

          invoiceID = invoiceIDVar.get()

          if invoiceID == 0:
            noMatches.append(transaction)
            existingCustomerTransactions.pop(0)
            break

          else:
            selectedInvoice = [possInvoice for possInvoice in paymentMatches if possInvoice.invoice_num == invoiceID][0]

            paidInvoiceMemo.append(selectedInvoice.invoice_num)

            preppedTransaction = prepNewlyMatchedErrorTransactionForDB(transaction, selectedInvoice)

            transactionTuple = preppedTransaction.as_tuple()

            parentID = addErrorTransactionToDB(transactionTuple, con, cur)

            correctionAmount = round((invoice.amount - transaction.amount), 2)

            dummyTransaction = Transaction(
              amount=correctionAmount,
              paid_on=transaction.paid_on,
              paid_by=transaction.paid_by,
              payment_method="CORDUM",
              error_notes=f"CORRECTION BY {correctionAmount}",
              og_string=transaction.og_string,
              invoice_num=transaction.invoice_num,
              invoice_id=transaction.invoice_id,
              customer_id=transaction.customer_id,
              parent_trans=parentID
            )

            addDummyNoteTransactionsToDB([dummyTransaction.as_tuple()], con, cur)

            transaction.error_flagged = 1
            transaction.error_notes = f"CORRECTED BY = {correctionAmount}"

            invoiceErrorStr = f"CORRECTED BY = {correctionAmount}"

            updateInvoiceRec(invoice.invoice_id, "error_flagged", "1", cur, con)
            updateInvoiceRec(invoice.invoice_id, "error_notes", invoiceErrorStr, cur, con)

            matched.append([preppedTransaction, selectedInvoice, correctionAmount])

            existingCustomerTransactions.pop(0)

            break


  # [print(i) for i in matched]
  # [print(i) for i in noMatches]

  # print("Start of the noMatch transactions as they are recieved by resolveNoMatchTransactions")
  # print("")

  # for noMatch in noMatches:
  #   print(noMatch)
  #   print("")

  # quit()

  return matched, multiMatched, noMatches, newCustomersTransactions








def resolveNoMatchTransactions2(root, incompTransactions, cur, con):



  existingCustomerTransactions, newCustomersTransactions = getCustomerIDForTrans(root, incompTransactions, cur, con)

  matched = []
  noMatches = []

  transactionCount = len(existingCustomerTransactions)

  paidInvoiceMemo = []

  while len(existingCustomerTransactions) > 0:

    transaction = existingCustomerTransactions[0]

    candInvoices = fetchUnpaidInvoicesByCustomerBeforeDate(transaction.paid_on, transaction.customer_id, cur)

    if len(candInvoices) == 0:
      noMatches.append(transaction)
      existingCustomerTransactions.pop(0)
      print("here innit")
      continue

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
      continue

    if len(paymentMatches) > 1:

      chosenInvoiceID = tk.IntVar(value=0)

      openSelectBetweenInvoices(root, transaction, paymentMatches, chosenInvoiceID)

      invoiceID = chosenInvoiceID.get()

      if invoiceID == 0:
        noMatches.append(transaction)
        existingCustomerTransactions.pop(0)
        continue
      else:
        selectedInvoice = [possInvoice for possInvoice in paymentMatches if possInvoice.invoice_num == invoiceID][0]

        paidInvoiceMemo.append(selectedInvoice.invoice_num)

        preppedTransaction = prepNewlyMatchedTransactionForDB(transaction, selectedInvoice)

        transactionTuple = preppedTransaction.as_tuple()

        addTransactionToDB(transactionTuple, con, cur)

        matched.append([preppedTransaction, selectedInvoice])

        existingCustomerTransactions.pop(0)

        continue

    if len(paymentMatches) == 0:

      closeEnoughMatched = [closeEnoughInvoice for closeEnoughInvoice in formattedInvoices if verifyTransactionAmount(transaction, closeEnoughInvoice, 10) == True and closeEnoughInvoice.invoice_num not in paidInvoiceMemo]

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

          continue
      
      if len(closeEnoughMatched) > 1:

        # Error here where for some reason I had a loop. Need to write popup to verify between close enoughs

        invoiceIDVar = tk.IntVar()

        print(closeEnoughMatched)

        openSelectBetweenCloseEnoughInvoices(root, transaction, closeEnoughMatched, invoiceIDVar)

        invoiceID = chosenInvoiceID.get()

        if invoiceID == 0:
          noMatches.append(transaction)
          existingCustomerTransactions.pop(0)
          continue
        else:
          selectedInvoice = [possInvoice for possInvoice in paymentMatches if possInvoice.invoice_num == invoiceID][0]

          paidInvoiceMemo.append(selectedInvoice.invoice_num)

          preppedTransaction = prepNewlyMatchedTransactionForDB(transaction, selectedInvoice)

          transactionTuple = preppedTransaction.as_tuple()

          addTransactionToDB(transactionTuple, con, cur)

          matched.append([preppedTransaction, selectedInvoice])

          existingCustomerTransactions.pop(0)

          continue
      
      if len(closeEnoughMatched) == 0:
        noMatches.append(transaction)
        existingCustomerTransactions.pop(0)
        break



  # [print(i) for i in matched]
  # [print(i) for i in noMatches] 
  # print(len(matched))
  # print(len(noMatches)) 
  # print(transactionCount)


  return matched, noMatches, newCustomersTransactions