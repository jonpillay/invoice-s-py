import tkinter as tk

from isp_noMatch_list import noMatchList
from isp_data_handlers import groupDataClassObjsByAttribute, genDBInvoiceDCobj, genDBTransactionDCobj
from isp_db_helpers import fetchInvoicesByCustomerBeforeDate, fetchTransactionsByInvoiceID
from isp_trans_verify import checkIfNoNumTransactionErrorIsCorrection
from isp_close_enough_prompts import openVerifyErrorCorrectionCloseEnoughMatch

import sqlite3
import os
from operator import attrgetter
from datetime import datetime, timedelta

def final_resolver(root, matchlessList, cur, con):

  matched = []
  nonMatchable = []

  # Sort noMatch list of Transactions into sublists orderd by customer_id
  noMatchGroups = groupDataClassObjsByAttribute(matchlessList, 'customer_id')

  for customerTransactionGroup in noMatchGroups:

    # Sort grouped customer Transactions by date
    customerTransactionGroup.sort(key=attrgetter('paid_on'))

    for transaction in customerTransactionGroup:

      # each Transaction here has been unable to match to an invoice, either it doesn't have an invoice number,
      # or invoice number was an error.

      possibleMatches = []

      bestMatch = None

      # fetch all invoices before the transaction date
      candInvoices = fetchInvoicesByCustomerBeforeDate(transaction.paid_on, transaction.customer_id, cur)

      candInvoiceDCs = [genDBInvoiceDCobj(candInvoice) for candInvoice in candInvoices]

      for invoiceDC in candInvoiceDCs:

        # from those invoices check if any had errors
        if invoiceDC.error_flagged == 1:

          # if there were errors fetch the both the Original Transaction and the correction dummy
          candTransactions = fetchTransactionsByInvoiceID(invoiceDC.invoice_id, cur)

          if len(candTransactions) > 0:

            errorTransaction = None
            dummyTransaction = None

            # convert to DCs and assign to descriptive variables
            for candTransaction in candTransactions:
              if "CORRECTED BY" in candTransaction[8]:
                errorTransaction = genDBTransactionDCobj(candTransaction)
              elif "CORDUM" in candTransaction[5]:
                dummyTransaction = genDBTransactionDCobj(candTransaction)

            # pass all three into funct to see if the error correction and any other unpaid invoice match the transaction amount
            matchCheck = checkIfNoNumTransactionErrorIsCorrection(transaction, invoiceDC, dummyTransaction, cur, con)

            if matchCheck[0] == True:

              # If true is returned in the list here then the match is exact and no user query needed. The returned invoice
              # and related Transactions should be appended to the matched list for reporting and then break the loop.

              # Form the a list for reporting. In order, OG No Num Transaction, The invoice it was matched to, with the error Transaction that ballances the numbers.
              matchReport = [transaction, matchCheck[1], errorTransaction]

              matched.append(matchReport)

            else:
              # if the list returned does not have True as its first element then it is a close enough match. This should be compared
              # against the current best match to see if it is closer.

              if bestMatch == None or matchCheck[0] < bestMatch[0]:

                bestMatch = matchCheck

          """
            Need a verfifyCorrectionPayment function to check if the under/over payment is correct with current transaction.
            Performed by taking the amount on the dummy transaction and minusing it from the transaction amount and then doing
            an amount check against outstanding invoices. If a match is found, dummy transaction is removed and each transaction/invoice
            pair in matched together.

          """


            # for candTransaction in candTransactions:

            #   candTransaction = genDBTransactionDCobj(candTransaction)

            #   if candTransaction.error_flagged == 1:
            #     pass
            #   else:
            #     print("NOTHING")
      
      if bestMatch != None:

        matchVerifiedBool = tk.BooleanVar()
        
        openVerifyErrorCorrectionCloseEnoughMatch(root, transaction, bestMatch[1], errorTransaction, dummyTransaction, matchVerifiedBool)

        verified = matchVerifiedBool.get()

        if verified == True:
          print("Worked")
        else:
          print("Also Worked")

      else:
        nonMatchable.append(transaction)

  return matched, nonMatchable

  


# dummyConn = sqlite3.connect(os.getenv("DB_NAME"))

# dummyConn.execute('PRAGMA foreign_keys = ON')

# dummyCur = dummyConn.cursor()

# final_resolver(noMatchList, dummyCur, dummyConn)