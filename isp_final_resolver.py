from isp_noMatch_list import noMatchList
from isp_data_handlers import groupDataClassObjsByAttribute, genInvoiceDCobj, genDBTransactionDCobj
from isp_db_helpers import fetchInvoicesByCustomerBeforeDate, fetchTransactionsByInvoiceID

import sqlite3
import os
from operator import attrgetter
from datetime import datetime, timedelta

def final_resolver(matchlessList, cur, con):

  # Sort noMatch list of Transactions into sublists orderd by customer_id
  noMatchGroups = groupDataClassObjsByAttribute(matchlessList, 'customer_id')

  for customerTransactionGroup in noMatchGroups:

    # Sort grouped customer Transactions by date
    customerTransactionGroup.sort(key=attrgetter('paid_on'))

    for transaction in customerTransactionGroup:

      # print("This is the transaction")
      # print(transaction)

      candInvoices = fetchInvoicesByCustomerBeforeDate(transaction.paid_on, transaction.customer_id, cur)

      candInvoiceDCs = [genInvoiceDCobj(candInvoice) for candInvoice in candInvoices]

      for invoiceDC in candInvoiceDCs:

        print(invoiceDC)
        candTransactions = fetchTransactionsByInvoiceID(invoiceDC.invoice_id, cur)

        if len(candTransactions) > 0:

          for candTransaction in candTransactions:


            candTransaction = genDBTransactionDCobj(candTransaction)



            
            if candTransaction.error_flagged == 1:
              pass
            else:
              print("NOTHING")




dummyConn = sqlite3.connect(os.getenv("DB_NAME"))

dummyConn.execute('PRAGMA foreign_keys = ON')

dummyCur = dummyConn.cursor()

final_resolver(noMatchList, dummyCur, dummyConn)