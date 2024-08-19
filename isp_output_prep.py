import sqlite3
import os

from output_test import outputDict as testOutputDict
from isp_data_handlers import groupDataClassObjsByAttribute
from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerNamesIDs, getCustomerIDs

# sort output dict into subdicts by customer

def genCustomerOutputDict(outputDict):

  conn = sqlite3.connect(os.getenv("DB_NAME"))

  conn.execute('PRAGMA foreign_keys = ON')

  cur = conn.cursor()

  customerIDs = getCustomerIDs(cur)
  # customerNames = [nameIDtup[0] for nameIDtup in customerNamesIDs]

  resultsCategories = [category for category in outputDict]

  customerResultsDict = {}

  cur.close()
  conn.close()

  for customer in customerIDs:

    resultsDict = {category:[] for category in resultsCategories}

    customerResultsDict[customer] = resultsDict

  return customerResultsDict

# genCustomerOutputDict(testOutputDict)


def populateCustomerOutputDict(outputDict):

  customerOutputDict = genCustomerOutputDict(outputDict)

  for category in outputDict:

    catList = outputDict[category]

    for entry in catList:
      
      customerID = None

      try:
        customerID = entry[0].customer_id
      except:
        try:
          customerID = entry.customer_id
        except:
          customerID = entry[0][0].customer_id

      customerOutputDict[customerID][category].append(entry)

  return customerOutputDict