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

  sql = "SELECT id, invoice_num, amount, date_issued, issued_to, error_flagged, error_notes, customer_id FROM INVOICES WHERE invoice_num=?"

  cur.execute(sql, (invoiceNumber,))

  invoice = cur.fetchall()

  return invoice


def fetchInvoiceByID(invoiceID, cur):

  sql = "SELECT * FROM INVOICES WHERE id=?"

  cur.execute(sql, (invoiceID,))

  invoice = cur.fetchall()

  return invoice


def fetchUnpaidInvoiceByNum(invoiceNumber, cur):

  sql = "SELECT INVOICES.id, INVOICES.invoice_num, INVOICES.amount, INVOICES.date_issued, INVOICES.issued_to, INVOICES.customer_id FROM INVOICES LEFT JOIN TRANSACTIONS ON INVOICES.id = TRANSACTIONS.invoice_id WHERE INVOICES.invoice_num=? AND TRANSACTIONS.invoice_id IS NULL"

  cur.execute(sql, (invoiceNumber,))

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


def fetchInvoicesByCustomerBeforeDate(beforeDate, customerID, cur):

  sql = "SELECT id, invoice_num, amount, date_issued, issued_to, error_flagged, error_notes, customer_id FROM INVOICES WHERE date_issued < ? and INVOICES.customer_id=? ORDER BY invoice_num"

  cur.execute(sql, (beforeDate, customerID))

  invoices = cur.fetchall()

  return invoices



def fetchUnpaidInvoicesByCustomer(customerID, cur):

  sql = "SELECT id, invoice_num, amount, date_issued, issued_to, customer_id FROM INVOICES WHERE NOT EXISTS (SELECT 1 FROM TRANSACTIONS WHERE INVOICES.id = TRANSACTIONS.invoice_id) and INVOICES.customer_id = ? ORDER BY invoice_num"

  cur.execute(sql, (customerID, ))

  invoices = cur.fetchall()

  return invoices

# def fetchUnpaidInvoicesByCustomer(customerID, cur):

#   sql = "SELECT INVOICES.id, INVOICES.invoice_num, INVOICES.amount, INVOICES.date_issued, INVOICES.issued_to, INVOICES.customer_id FROM INVOICES LEFT JOIN TRANSACTIONS ON INVOICES.customer_id = TRANSACTIONS.customer_id WHERE INVOICES.customer_id=? AND TRANSACTIONS.invoice_id IS NULL ORDER BY INVOICES.invoice_num"

#   cur.execute(sql, (customerID, ))

#   invoices = cur.fetchall()

#   return invoices


def fetchUnpaidInvoicesByCustomerBeforeDate(beforeDate, customerID, cur):

  sql = "SELECT INVOICES.id, INVOICES.invoice_num, INVOICES.amount, INVOICES.date_issued, INVOICES.issued_to, INVOICES.customer_id FROM INVOICES LEFT JOIN TRANSACTIONS ON INVOICES.id = TRANSACTIONS.invoice_id WHERE date_issued < ? AND INVOICES.customer_id=? AND TRANSACTIONS.invoice_id IS NULL ORDER BY INVOICES.invoice_num"

  cur.execute(sql, (beforeDate, customerID))

  invoices = cur.fetchall()

  return invoices


def fetchInvoicesByCustomerDateRange(lowDate, highDate, customerID, cur):

  sql = "SELECT id, invoice_num, amount, date_issued, issued_to, error_flagged, error_notes, customer_id FROM INVOICES WHERE INVOICES.date_issued BETWEEN ? and ? and INVOICES.customer_id=? ORDER BY invoice_num"

  cur.execute(sql, (lowDate, highDate, customerID))

  invoices = cur.fetchall()

  return invoices

# quick count of invoices after a date by customer for fast retrieval for frontend display

def countInvoicesByCustomerAfterDate(startDate, customerID, cur):

  sql = "SELECT COUNT(id) FROM INVOICES WHERE date_issued > ? and customer_id=? ORDER BY invoice_num"

  cur.execute(sql, (startDate, customerID))

  invoiceCount = cur.fetchone()[0]

  return invoiceCount


def countUnpaidInvoicesByCustomerAfterDate(startDate, customerID, cur):

  sql = "SELECT COUNT(INVOICES.id) FROM INVOICES LEFT JOIN TRANSACTIONS ON INVOICES.id = TRANSACTIONS.invoice_id WHERE INVOICES.date_issued > ? AND INVOICES.customer_id=? AND TRANSACTIONS.invoice_id IS NULL ORDER BY INVOICES.invoice_num"

  cur.execute(sql, (startDate, customerID))

  invoiceCount = cur.fetchone()[0]

  return invoiceCount



# Needs to fetch invoices by customer and also only before the transaction was paid

def fetchUnpaidInvoicesByCustomerDateRange(lowDate, highDate, customerID, cur):

  sql = "SELECT INVOICES.id, INVOICES.invoice_num, INVOICES.amount, INVOICES.date_issued, INVOICES.issued_to, INVOICES.customer_id FROM INVOICES LEFT JOIN TRANSACTIONS ON INVOICES.id = TRANSACTIONS.invoice_id WHERE INVOICES.date_issued BETWEEN ? AND ? AND INVOICES.customer_id=? AND TRANSACTIONS.invoice_id IS NULL ORDER BY INVOICES.invoice_num"

  cur.execute(sql, (lowDate, highDate, customerID))

  invoices = cur.fetchall()

  return invoices


def fetchTransactionsByInvoiceID(invoiceID, cur):
  
  sql = "SELECT * FROM TRANSACTIONS WHERE invoice_id=?"

  cur.execute(sql, (invoiceID,))

  transactions = cur.fetchall()

  return transactions


def fetchTransactionsByCustomerPaymentMethod(paymentMethod, customerID, cur):

  sql ="SELECT * FROM TRANSACTIONS WHERE payment_method LIKE ? AND customer_id = ?"

  cur.execute(sql, (paymentMethod, customerID))

  transactions = cur.fetchall()

  return transactions


def fetchTransactionByParentID(parentID, cur):
  
  sql = "SELECT * FROM TRANSACTIONS WHERE parent_trans=? ORDER BY invoice_num"

  cur.execute(sql, (parentID,))

  transaction = cur.fetchall()

  return transaction



def fetchTransactionByID(ID, cur):
  
  sql = "SELECT * FROM TRANSACTIONS WHERE id=?"

  cur.execute(sql, (ID,))

  transaction = cur.fetchall()

  return transaction


def deleteDummyTransactionsByParentID(paarentTransID, cur, con):

  sql = "DELETE FROM TRANSACTIONS WHERE parent_id = ?"

  cur.execute(sql, (paarentTransID,))

  con.commit()


def addInvoicesToDB(invoicesTuples, cur):

  sql = "INSERT INTO invoices (invoice_num, amount, date_issued, issued_to, customer_id) VALUES (?,?,?,?,?)"

  cur.executemany(sql, invoicesTuples)



def addCashInvoicesAndTransactions(cashInvoiceList, cur, con):

  for invoice in cashInvoiceList:
    sql = "INSERT OR IGNORE INTO INVOICES (invoice_num, amount, date_issued, issued_to, customer_id) VALUES (?,?,?,?,?)"

    cur.execute(sql, invoice.as_tuple(),)

    con.commit()

    invoiceID = cur.lastrowid

    invoiceDT = datetime.strptime(invoice.date_issued, "%Y-%m-%d")

    dummyCashPaymentDt = invoiceDT + timedelta(days=1)
  
    transactionTup = (invoice.amount, dummyCashPaymentDt, invoice.issued_to, "CASH", "CASH TRANSACTION", invoice.invoice_num, invoice.customer_id, invoiceID)

    addTransactionToDB(transactionTup, con, cur)

    con.commit()



def addTransactionToDB(transactionTuple, con, cur):
  
  sql = "INSERT INTO TRANSACTIONS (amount, paid_on, company_name, payment_method, og_string, invoice_num, customer_id, invoice_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

  cur.execute(sql, transactionTuple)

  con.commit()

  transID = cur.lastrowid

  return transID


def addErrorNoteTransactionToDB(transactionTuple, con, cur):
  
  sql = "INSERT INTO TRANSACTIONS (amount, paid_on, company_name, payment_method, og_string, invoice_num, error_notes, customer_id, invoice_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

  cur.execute(sql, transactionTuple)

  con.commit()

  transID = cur.lastrowid

  return transID



def addErrorTransactionToDB(transactionTuple, con, cur):
  
  sql = "INSERT INTO TRANSACTIONS (amount, paid_on, company_name, payment_method, og_string, invoice_num, error_flagged, error_notes, customer_id, invoice_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

  cur.execute(sql, transactionTuple)

  con.commit()

  transID = cur.lastrowid

  return transID



def addTransactionsToDB(transactionsTuples, cur):

  sql = "INSERT INTO TRANSACTIONS (amount, paid_on, company_name, payment_method, og_string, invoice_num, customer_id, invoice_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

  cur.executemany(sql, transactionsTuples)



def addParentTransactionToDB(transactionTuple, cur, con):
  
  sql = "INSERT INTO TRANSACTIONS (amount, paid_on, company_name, payment_method, og_string, invoice_num, high_invoice, customer_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

  cur.execute(sql, transactionTuple)

  con.commit()

  transID = cur.lastrowid

  return transID

def addParentErrorTransactionsToDB(transactionTuples, cur, con):
  
  sql = "INSERT INTO TRANSACTIONS (amount, paid_on, company_name, payment_method, og_string, invoice_num, high_invoice, error_flagged, error_notes, customer_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

  cur.executemany(sql, transactionTuples)

  con.commit()



def addDummyTransactionsToDB(transactionUploadList, cur, con):

  sql = "INSERT INTO TRANSACTIONS (amount, paid_on, company_name, payment_method, og_string, invoice_num, customer_id, invoice_id, parent_trans) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

  cur.executemany(sql, transactionUploadList)

  con.commit()


def addDummyNoteTransactionsToDB(transactionUploadList, con, cur):

  sql = "INSERT INTO TRANSACTIONS (amount, paid_on, company_name, payment_method, og_string, invoice_num, error_notes, customer_id, invoice_id, parent_trans) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

  cur.executemany(sql, transactionUploadList)

  con.commit()

  transID = cur.lastrowid

  return transID

def addNewCustomerTransactionsToDB(newCustomerTransactions, con, cur):

  sql = "INSERT INTO TRANSACTIONS (amount, paid_on, company_name, payment_method, og_string, error_flagged, error_notes, customer_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

  cur.executemany(sql, newCustomerTransactions)

  con.commit()


def addNoMatchTransactionsToDB(noMatchTransactions, con, cur):

  sql = "INSERT INTO TRANSACTIONS (amount, paid_on, company_name, payment_method, og_string, error_flagged, error_notes, customer_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

  cur.executemany(sql, noMatchTransactions)

  con.commit()


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

  aliasEntry = (aliasName.strip().upper(), customerID)
  
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


def genIDsCustomerNamesDict(cur):

  fetctInvNumSQL = "SELECT id, customer_name from CUSTOMERS"

  cur.execute(fetctInvNumSQL)

  customerNames = cur.fetchall()

  return {customer[0]: customer[1] for customer in customerNames}


def genCustomerNamesIDsDict(cur):

  fetctInvNumSQL = "SELECT id, customer_name from CUSTOMERS"

  cur.execute(fetctInvNumSQL)

  customerNames = cur.fetchall()

  return {customer[1]: customer[0] for customer in customerNames}


def getCustomerIDs(cur):

  fetctInvNumSQL = "SELECT id from CUSTOMERS"

  cur.execute(fetctInvNumSQL)

  customerIDs = cur.fetchall()

  return [idTup[0] for idTup in customerIDs]




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



def addCorrectedTransactionPairsDB(correctedErrors, con, cur):

  for errorTup in correctedErrors:
  
    parentTransaction = errorTup[0][0]
    correctionTransation = errorTup[1]

    parentID = addErrorTransactionToDB(parentTransaction.as_tuple(), con, cur)

    parentTransaction.transaction_id = parentID

    # if len(parentTransactionTup) == 8:
    #   print(parentTransactionTup)
    #   parentID = addTransactionToDB(parentTransactionTup, con, cur)
    # else:
    #   print(parentTransactionTup)
    #   parentID = addDummyNoteTransactionsToDB([parentTransactionTup], con, cur)

    correctionTransation.parent_trans = parentID

    addDummyNoteTransactionsToDB([correctionTransation.as_tuple()], con, cur)

  return correctedErrors



def resolveNameIntoDB(root, name, dbCustomers, newCustomerBool, cur, con):

  newCustomerReturn = tk.StringVar()

  newAliasReturn = tk.StringVar()

  openNewCustomerPrompt(root, name, dbCustomers, newCustomerReturn, newAliasReturn)

  customerName = newCustomerReturn.get()

  aliasName = newAliasReturn.get()

  if customerName != "" and customerName.strip().upper() == name.strip().upper():

    addNewCustomerToDB(name, cur)

    con.commit()

    customerID = cur.lastrowid

    newCustomerBool.set(True)

    return customerID

  elif aliasName != "":

    customerID = findCustomerIDInTup(aliasName, dbCustomers)

    addAliasToDB(name, customerID, cur)

    con.commit()

    return customerID

  elif customerName != "" and customerName != name:
    
    addNewCustomerToDB(customerName, cur)

    con.commit()

    customerID = cur.lastrowid

    addAliasToDB(name, customerID, cur)

    con.commit()

    return customerID
  

def updateInvoiceRec(invoice_id, field, updateValue, cur, con):

  sql = f"UPDATE INVOICES SET {field} = ? WHERE id = ?"

  cur.execute(sql, (updateValue, invoice_id))

  con.commit()


def updateTransactionRec(transaction_id, field, updateValue, cur, con):

  sql = f"UPDATE TRANSACTIONS SET {field} = ? WHERE id = ?"

  cur.execute(sql, (updateValue, transaction_id))

  con.commit()



def deleteTransactionRec(id, cur, con):

  sql = "DELETE FROM TRANSACTIONS WHERE id = ?"

  cur.execute(sql, (id,))

  con.commit()