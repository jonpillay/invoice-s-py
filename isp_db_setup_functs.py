import sqlite3
import os

from dotenv import load_dotenv, dotenv_values
load_dotenv()

# --begin-sql and --end-sql use python-string-sql in vscode to highlight sql cmds and queries

def dbExists():
  return os.path.exists('./' + os.getenv("DB_NAME"))


def dbInvoicesTableExists():
  con = sqlite3.connect(os.getenv("DB_NAME"))
  cur = con.cursor()

  invoicesTable = cur.execute("""
    --begin-sql
    SELECT name FROM sqlite_master WHERE type='table' AND name='INVOICES'
    --end-sql
    """).fetchall()

  if invoicesTable == []:
    return False
  else:
    return True


def dbTransactionsTableExists():

  con = sqlite3.connect(os.getenv("DB_NAME"))
  cur = con.cursor()

  transactionsTable = cur.execute("""
    --begin-sql
    SELECT name FROM sqlite_master WHERE type='table' AND name='TRANSACTIONS'
    --end-sql
    """).fetchall()
  

  if transactionsTable == []:
    return False
  else:
    return True
  

def createDB():
  con = sqlite3.connect(os.getenv("DB_NAME"))
  con.close()


def createInvoicesTable():
  con = sqlite3.connect(os.getenv("DB_NAME"))
  cur = con.cursor()

  cur.execute( """
    --begin-sql
    CREATE TABLE INVOICES (
      id INTEGER PRIMARY KEY NOT NULL,
      invoice_num INTEGER,
      amount REAL,
      date_issued DATE,
      company_name VARCHAR(255)
    )
    --end-sql      
    """ )
  
  con.close()


def createTransactionsTable():
  con = sqlite3.connect(os.getenv("DB_NAME"))
  cur = con.cursor()

  cur.execute("""
    --begin-sql
    CREATE TABLE TRANSACTIONS(
      id INTEGER PRIMARY KEY NOT NULL,
      invoice_num INTEGER,
      amount REAL,
      paid_on DATE,
      company_name VARCHAR(255),
      payment_method VARCHAR(255),
      og_string VARCHAR(255),
      invoice_id INTEGER,
      FOREIGN KEY(invoice_id) REFERENCES INVOICES(id)
    )
    --end-sql
    """)
  
  con.close()

def createCustomersTable():
  con = sqlite3.connect(os.getenv("DB_NAME"))
  cur = con.cursor()

  cur.execute("""
    --begin-sql
    CREATE TABLE IF NOT EXISTS CUSTOMER(
      id INTEGER PRIMARY KEY NOT NULL,
      customer_name VARCHAR(255)
    )
    --end-sql
    """)
  
def createAliasesTable():
  con = sqlite3.connect(os.getenv("DB_NAME"))
  cur = con.cursor()

  cur.execute("""
    --begin-sql
    CREATE TABLE IF NOT EXISTS ALIASES(
      id INTEGER PRIMARY KEY NOT NULL,
      customer_alias VARCHAR(255),
      customer_id INTEGER,
      FOREIGN KEY(customer_id) REFERENCES CUSTOMER(id)
    )
    --end-sql
    """)
  
  
  con.close()

def checkDBStatus():

  if dbExists() == False:
    createDB()
    createCustomersTable()
    createAliasesTable()

  if dbTransactionsTableExists() == False:
    createTransactionsTable()

  if dbInvoicesTableExists() == False:
    createInvoicesTable()