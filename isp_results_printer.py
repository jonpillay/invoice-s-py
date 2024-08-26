import sqlite3
import os

from output_test import outputDict as testOutputDict

from isp_db_helpers import getCustomerNamesIDs, getCustomerIDs, genCustomerNamesIDsDict
from isp_output_prep import populateCustomerOutputDict

from isp_PDF_class import TransactionUploadPDF

def print_transaction_upload_results(outputDict):

  con = sqlite3.connect(os.getenv("DB_NAME"))

  con.execute('PRAGMA foreign_keys = ON')

  cur = con.cursor()

  results = TransactionUploadPDF('P', 'mm', 'A4')

  results.add_page()
  results.register_fonts()

  outputResults = populateCustomerOutputDict(outputDict)

  customerIDsDict = genCustomerNamesIDsDict(cur)

  for customer in outputResults:

    hasResults = False

    customerResultsDict = outputResults[customer]

    for category in customerResultsDict:

      if len(customerResultsDict[category]) > 0:
        hasResults = True

    if hasResults == False:
      continue

    customerName = customerIDsDict[customer]

    results.printCustomerName(customerName)

    for category in customerResultsDict:

      catResults = customerResultsDict[category]

      if len(catResults) > 0:
        
        if category == 'matchedSingles':

          results.printCategoryTitle(category)

          for matchedSingle in catResults:

            results.printMatchedSingles(matchedSingle)

        elif category == 'correctedErrorsReport':

          results.printCategoryTitle(category)

          for errorCorrected in catResults:

            results.printCorrectedErrorsReport(errorCorrected)

        elif category == 'correctionTransactionErrorsReport':

          results.printCategoryTitle(category)

          for correctionTransaction in catResults:

            results.printCorrectionTransactionError(correctionTransaction)

        elif category == 'inCompMatched':

          results.printCategoryTitle(category)

          for inCompMatch in catResults:

            results.printInCompMatchedPair(inCompMatch)

        elif category == 'uploadedMultiTransactionPairs':

          results.printCategoryTitle(category)

          for multiInvoiceMatch in catResults:

            results.printMultiInvoiceTransactionMatch(multiInvoiceMatch)

        elif category == 'inCompMultiMatch':

          results.printCategoryTitle("Multi-Invoice Numberless Transactions Matched Via Amount")

          for incompMultiInvoiceMatch in catResults:

            results.printMultiInvoiceTransactionMatch(incompMultiInvoiceMatch)

        elif category == 'multiErrorFlagged':

          results.printCategoryTitle("Multi-Invoice Transactions Matched Via Amount, User Flagged as Error")

          for multiInvoiceMatchFlagged in catResults:

            results.printMultiInvoiceTransactionMatch(multiInvoiceMatchFlagged)

        elif category == 'finalNoMatch':

          results.printCategoryTitle("No Match Transactions")

          for noMatch in catResults:

            results.printNoMatchTransaction(noMatch)

        elif category == 'newCustomerTransactions':

          results.printCategoryTitle("New Customer Transactions (No Invoice in DB)")

          for newCustomerTransaction in catResults:

            results.printNewCustomerTransaction(newCustomerTransaction)

  cur.close()
  con.close()

  results.output('../test.pdf')



print_transaction_upload_results(testOutputDict)