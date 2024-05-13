import sqlite3
import tkinter as tk
from datetime import datetime, timedelta, date

from isp_popup_window import openNewCustomerPrompt
from isp_data_comparers import compareCustomerToAliasesDict, findCustomerIDInTup
# from isp_data_handlers import genCashTransactionTup

def getInvoiceNumsIDs(cur):

  invoiceIDnumsSQL = "SELECT id invoice_num from INVOICES"

  cur.execute(invoiceIDnumsSQL)

  invoiceNumsIDs = cur.fetchall()

  return [invoice[0] for invoice in invoiceNumsIDs]



def fetchInvoiceByNum(invoiceNumber, cur):

  sql = f"SELECT id, invoice_num, amount, date_issued, issued_to, customer_id FROM INVOICES WHERE invoice_num={invoiceNumber}"

  cur.execute(sql)

  invoice = cur.fetchall()

  return invoice

def fetchRangeInvoices(low, high, cur):

  sql = "SELECT id, invoice_num, amount, date_issued, issued_to, customer_id FROM invoices WHERE invoice_num BETWEEN ? and ? ORDER BY invoice_num"

  cur.execute(sql, (low, high))

  invoices = cur.fetchall()

  return invoices

def fetchRangeInvoicesByCustomer(low, high, customerID, cur):

  sql = "SELECT id, invoice_num, amount, date_issued, issued_to, customer_id FROM invoices WHERE invoice_num BETWEEN ? and ? and customer_id=? ORDER BY invoice_num"

  cur.execute(sql, (low, high, customerID))

  invoices = cur.fetchall()

  return invoices

def addInvoicesToDB(invoicesTuples, cur):

  sql = "INSERT INTO invoices (invoice_num, amount, date_issued, issued_to, customer_id) VALUES (?,?,?,?,?)"

  cur.executemany(sql, invoicesTuples)



def addCashInvoicesAndTransactions(cashInvoiceList, cur, conn):

  for invoice in cashInvoiceList:
    sql = "INSERT OR IGNORE INTO INVOICES (invoice_num, amount, date_issued, issued_to, customer_id) VALUES (?,?,?,?,?)"

    cur.execute(sql, invoice,)

    conn.commit()

    invoiceID = cur.lastrowid

    invoiceDT = datetime.strptime(invoice[2], "%Y-%m-%d")

    print(invoiceDT)

    dummyCashPaymentDt = invoiceDT + timedelta(days=1)
  
    transactionTup = (invoice[0], invoice[1], dummyCashPaymentDt, invoice[3], "CASH", "CASH TRANSACTION", invoiceID, invoice[4])

    addTransactionToDB(transactionTup, cur)

    conn.commit()



def addTransactionToDB(transactionTuple, cur, con):
  
  sql = "INSERT INTO TRANSACTIONS (invoice_num, amount, paid_on, company_name, payment_method, og_string, invoice_id, customerID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

  cur.execute(sql, transactionTuple)

  con.commit()



def addTransactionsToDB(transactionsTuples, cur):

  sql = "INSERT INTO TRANSACTIONS (invoice_num, amount, paid_on, company_name, payment_method, og_string, invoice_id) VALUES (?, ?, ?, ?, ?, ?, ?)"

  cur.executemany(sql, transactionsTuples)



def addParentTransactionToDB(transactionTuple, cur, con):
  
  sql = "INSERT INTO TRANSACTIONS (invoice_num, amount, paid_on, company_name, payment_method, og_string, high_invoice, invoice_id, customer_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

  cur.execute(sql, transactionTuple)

  con.commit()

  transID = cur.lastrowid

  return transID




def addNewCustomerToDB(customerName, cur):

  sql = "INSERT OR IGNORE INTO CUSTOMERS (customer_name) VALUES (?)"

  cur.execute(sql, (customerName.strip(),))



def addNewCustomersToDB(customerList, cur):

  customerTuples = []

  for customer in customerList:

    customerTuple = (customer.strip(),)

    customerTuples.append(customerTuple)

  sql = "INSERT OR IGNORE INTO CUSTOMERS (customer_name) VALUES (?)"

  customerTuples.sort(key= lambda x: x[0])

  cur.executemany(sql, customerTuples)



def addAliasToDB(aliasName, customerID, cur):

  aliasEntry = (aliasName.strip(), customerID)
  
  sql = "INSERT OR IGNORE INTO ALIASES (customer_alias, customer_id) VALUES (?,?)"

  cur.execute(sql, aliasEntry)




def getDBInvoiceNums(cur):

  fetctInvNumSQL = "SELECT invoice_num from INVOICES"

  cur.execute(fetctInvNumSQL)

  invoiceNums = cur.fetchall()

  return [invoice[0] for invoice in invoiceNums]




def getCustomerID(cur, name):

  fetchCustomerIDSQL = f"SELECT id FROM CUSTOMERS WHERE customer_name=?"

  cur.execute(fetchCustomerIDSQL, (name,))

  customerID = cur.fetchall()

  return customerID[0][0]


def getCustomerNamesIDs(cur):

  fetctInvNumSQL = "SELECT id, customer_name from CUSTOMERS"

  cur.execute(fetctInvNumSQL)

  customerNames = cur.fetchall()

  return [(customer[0], customer[1]) for customer in customerNames]




def getCustomerAliases(cur, customerID):

  sql = f"SELECT customer_alias FROM ALIASES WHERE customer_id={customerID}"

  cur.execute(sql)

  customerAliases = cur.fetchall()

  return [alias[0].upper().strip() for alias in customerAliases]



def resolveNewCustomersDB(root, invoiceCustomers, aliasesDict, cur, conn):

  for customer in invoiceCustomers:

    dbCustomers = getCustomerNamesIDs(cur)

    existsBool = compareCustomerToAliasesDict(customer, aliasesDict)

    if existsBool == True:
      continue
    else:

      newCustomerReturn = tk.StringVar()

      newAliasReturn = tk.StringVar()

      openNewCustomerPrompt(root, customer, dbCustomers, newCustomerReturn, newAliasReturn)

      customerName = newCustomerReturn.get()

      aliasName = newAliasReturn.get()

      """ 
      If user has edited the entry box on the form to enter the customer name
      as different from that of the invoice - the edited name should be entered as the customer
      name and the invoice name as an alias of it.

      THIS NEEDS TO BE SEPARETD INTO ITS OWN FUNCITON
      """

      if customerName != "" and customerName == customer:

        print("It took us here")

        print(customerName)

        addNewCustomerToDB(customer, cur)

        print(cur.lastrowid)

        conn.commit()

      elif aliasName != "":

        print(aliasName + "this is from the alias")

        customerID = findCustomerIDInTup(aliasName, dbCustomers)

        addAliasToDB(customer, customerID, cur)

        conn.commit()

      elif customerName != "" and customerName != customer:
        
        addNewCustomerToDB(customerName, cur)

        customerID = cur.lastrowid

        conn.commit()

        addAliasToDB(customer, customerID, cur)

        conn.commit()
      else:
        print("Nothing happened")



def uploadInvoicesToDB(cur, invoiceList):
  pass