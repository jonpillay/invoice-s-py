import sqlite3
import os
import subprocess
from datetime import datetime

from isp_db_helpers import genIDsCustomerNamesDict
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

  customerIDsDict = genIDsCustomerNamesDict(cur)

  for customer in outputResults:

    hasResults = False

    customerResultsDict = outputResults[customer]

    for category in customerResultsDict:

      if len(customerResultsDict[category]) > 0:
        hasResults = True

    if hasResults == False:
      continue

    customerName = customerIDsDict[customer]

    results.set_x(8)

    results.printCustomerName(customerName)

    for category in customerResultsDict:

      catResults = customerResultsDict[category]

      if len(catResults) > 0:
        
        if category == 'matchedSingles':

          results.printCategoryTitle("Single Invoice Transactions - Exact Match")

          for matchedSingle in catResults:

            results.printMatchedSingles(matchedSingle)

        elif category == 'invoiceNumRematchedReport':

          results.printCategoryTitle("Invoice Number Corrected - Transaction Rematched")

          for correctInvoiceNum in catResults:

            results.printInvoiceNumCorrectedReport(correctInvoiceNum)

        elif category == 'correctedErrorsReport':

          results.printCategoryTitle("Single Invoice Transactions -  Corrected Payment Errors")

          for errorCorrected in catResults:

            results.printCorrectedErrorsReport(errorCorrected)

        elif category == 'correctionTransactionErrorsReport':

          results.printCategoryTitle("Transaction Payments Correcting Past Errors")

          for correctionTransaction in catResults:

            results.printCorrectionTransactionError(correctionTransaction)

        elif category == 'inCompMatched':

          results.printCategoryTitle("Transactions Matched Via Amount")

          for inCompMatch in catResults:

            results.printInCompMatchedPair(inCompMatch)

        elif category == 'uploadedMultiTransactionPairs':

          results.printCategoryTitle("Multi-Invoice Transactions")

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

          results.printCategoryTitle("Unable to Find Matches")

          for noMatch in catResults:

            results.printNoMatchTransaction(noMatch)

        elif category == 'newCustomerTransactions':

          results.printCategoryTitle("New Customer Transactions (No Invoices in DB)")

          for newCustomerTransaction in catResults:

            results.printNewCustomerTransaction(newCustomerTransaction)

  cur.close()
  con.close()

  dateToday = datetime.today().strftime("%d_%m_%Y")
  
  outputDir = os.path.join("..", "ISPTransactionUploadReports")
  outputFile = os.path.join(outputDir, f"transcation_upload_report-{dateToday}.pdf")

  if not os.path.exists(outputDir):

    os.makedirs(outputDir, exist_ok=True)

  results.output(outputFile)

  subprocess.Popen([outputFile], shell=True)

  results.output('../test.pdf')