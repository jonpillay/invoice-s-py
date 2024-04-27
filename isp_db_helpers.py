import sqlite3

import tkinter as tk

from isp_user_prompts import promptUserNewCustomer
from isp_data_comparers import compareCustomerToAliasesDict

def getInvoiceNumsIDs(cur):

  invoiceIDnumsSQL = "SELECT id invoice_num from INVOICES"

  cur.execute(invoiceIDnumsSQL)

  invoiceNumsIDs = cur.fetchall()

  return [invoice[0] for invoice in invoiceNumsIDs]

def fetchInvoiceByNum(invoiceNumber, cur):

  sql = f"SELECT id, invoice_num, amount, date_issued, company_name FROM INVOICES WHERE invoice_num={invoiceNumber}"

  cur.execute(sql)

  invoice = cur.fetchall()

  return invoice

def addTransactionsToDB(transactionsTuples, cur):

  sql = "INSERT INTO TRANSACTIONS (invoice_num, amount, paid_on, company_name, payment_method, og_string, invoice_id) VALUES (?, ?, ?, ?, ?, ?, ?)"

  cur.executemany(sql, transactionsTuples)

def addNewCustomersToDB(customerList, cur):

  customerTuples = []

  for customer in customerList:

    customerTuple = (customer.strip(),)

    customerTuples.append(customerTuple)

    # popup for new customers asking if wanting to attatch to existing customer

  sql = "INSERT OR IGNORE INTO CUSTOMERS (customer_name) VALUES (?)"

  customerTuples.sort(key= lambda x: x[0])

  cur.executemany(sql, customerTuples)


def getDBInvoiceNums(cur):

  fetctInvNumSQL = "SELECT invoice_num from INVOICES"

  cur.execute(fetctInvNumSQL)

  invoiceNums = cur.fetchall()

  return [invoice[0] for invoice in invoiceNums]


def getCustomerNamesIDs(cur):

  fetctInvNumSQL = "SELECT id, customer_name from CUSTOMERS"

  cur.execute(fetctInvNumSQL)

  customerNames = cur.fetchall()

  return [(customer[0], customer[1]) for customer in customerNames]

def getCustomerAliases(cur, customerID):

  sql = f"SELECT customer_alias FROM ALIASES WHERE customer_id={customerID}"

  cur.execute(sql)

  customerAliases = cur.fetchall()

  return [alias[0].upper() for alias in customerAliases]

def resolveNewCustomersDB(root, invoiceCustomers, aliasesDict, dbCustomers):

  updateDict = {}

  for customer in invoiceCustomers:

    existsBool = compareCustomerToAliasesDict(customer, aliasesDict)

    if existsBool == True:
      print("here Though")
      continue
    else:
      print("here")

      response = tk.StringVar()

      promptUserNewCustomer(root, customer, dbCustomers, response)

      print(response.get())