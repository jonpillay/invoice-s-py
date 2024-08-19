import sqlite3
import os

from output_test import outputDict as testOutputDict
from isp_data_handlers import groupDataClassObjsByAttribute
from isp_db_helpers import getCustomerNamesIDs, getCustomerIDs
from isp_output_prep import populateCustomerOutputDict

def print_transaction_upload_results(outputDict):

  outputResults = populateCustomerOutputDict(outputDict)

  for customer in outputResults:

    hasResults = False

    customerResultsDict = outputResults[customer]

    for category in customerResultsDict:

      if len(customerResultsDict[category]) > 0:
        hasResults = True

    if hasResults == False:
      continue


      



  

print_transaction_upload_results(testOutputDict)