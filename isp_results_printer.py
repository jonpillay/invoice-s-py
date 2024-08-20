import sqlite3
import os

from fpdf import FPDF

from output_test import outputDict as testOutputDict
from isp_data_handlers import groupDataClassObjsByAttribute
from isp_db_helpers import getCustomerNamesIDs, getCustomerIDs, genCustomerNamesIDsDict
from isp_output_prep import populateCustomerOutputDict

from isp_PDF_class import TransactionUploadPDF

def print_transaction_upload_results(outputDict):

  con = sqlite3.connect(os.getenv("DB_NAME"))

  con.execute('PRAGMA foreign_keys = ON')

  cur = con.cursor()

  results = TransactionUploadPDF('P', 'mm', 'A4')

  results.add_page()

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

  cur.close()
  con.close()

  results.output('../test.pdf')


      



  

print_transaction_upload_results(testOutputDict)