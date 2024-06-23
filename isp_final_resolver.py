from isp_noMatch_list import noMatchList
from isp_data_handlers import groupDataClassObjsByAttribute, genDBInvoiceDCobj, genDBTransactionDCobj
from isp_db_helpers import fetchInvoicesByCustomerBeforeDate, fetchTransactionsByInvoiceID
from isp_trans_verify import checkIfTransactionErrorIsCorrection

import sqlite3
import os
from operator import attrgetter
from datetime import datetime, timedelta

def final_resolver(matchlessList, cur, con):

  matched = []
  nonMatchable = []

  # Sort noMatch list of Transactions into sublists orderd by customer_id
  noMatchGroups = groupDataClassObjsByAttribute(matchlessList, 'customer_id')

  for customerTransactionGroup in noMatchGroups:

    print(customerTransactionGroup[0].paid_by)

    # Sort grouped customer Transactions by date
    customerTransactionGroup.sort(key=attrgetter('paid_on'))



    for transaction in customerTransactionGroup:

      # each Transaction here has been unable to match to an invoice, either it doesn't have an invoice number,
      # or invoice number was an error.

      possibleMatches = []

      # fetch all invoices before the transaction date
      candInvoices = fetchInvoicesByCustomerBeforeDate(transaction.paid_on, transaction.customer_id, cur)

      candInvoiceDCs = [genDBInvoiceDCobj(candInvoice) for candInvoice in candInvoices]

      for invoiceDC in candInvoiceDCs:

        # from those invoices check if any were errors
        if invoiceDC.error_flagged == 1:

          # if they are errors fetch the both the Original Transaction and the correction dummy
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
            matchCheck = checkIfTransactionErrorIsCorrection(transaction, errorTransaction, dummyTransaction, cur, con)

            if type(matchCheck) == list:
              # if a list is returned it will be a list of possible matches.
              # These are a group of unpaid invoices that are close enough matches to the transaction payment
              # when corrected by the previous error.
              # Each list needs to be ordered by the error invoice it relates to, probably a dictionary
              print("We here though")
              print(matchCheck)
            else:
              print("This is the tup")
              print(matchCheck)

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




dummyConn = sqlite3.connect(os.getenv("DB_NAME"))

dummyConn.execute('PRAGMA foreign_keys = ON')

dummyCur = dummyConn.cursor()

final_resolver(noMatchList, dummyCur, dummyConn)