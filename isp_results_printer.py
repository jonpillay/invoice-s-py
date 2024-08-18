import sqlite3
import os

from output_test import outputDict as testOutputDict
from isp_data_handlers import groupDataClassObjsByAttribute
from isp_db_helpers import getCustomerNamesIDs

# sort output dict into subdicts by customer

def genCustomerOutputDict(outputDict):

  conn = sqlite3.connect(os.getenv("DB_NAME"))

  conn.execute('PRAGMA foreign_keys = ON')

  cur = conn.cursor()

  customerNames = getCustomerNamesIDs(cur)
  resultsCategories = [category for category in outputDict]

  customerIDNamesDict = {customer[0]:customer[1] for customer in customerNames}

  customerResultsDict = {}

  for customer in customerNames:

    resultsDict = {category:[] for category in resultsCategories}

    customerResultsDict[customer] = resultsDict

  print(customerResultsDict)


  cur.close()
  conn.close()

genCustomerOutputDict(testOutputDict)