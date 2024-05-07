import sqlite3
import os

from dotenv import load_dotenv, dotenv_values
load_dotenv()

# --begin-sql and --end-sql use python-string-sql in vscode to highlight sql cmds and queries

def dbExists():
  return os.path.exists('./' + os.getenv("DB_NAME"))

def createDB(conn):
  conn = sqlite3.connect(os.getenv("DB_NAME"))


def dbInvoicesTableExists(cur):

  invoicesTable = cur.execute("""
    --begin-sql
    SELECT name FROM sqlite_master WHERE type='table' AND name='INVOICES'
    --end-sql
    """).fetchall()

  if invoicesTable == []:
    return False
  else:
    return True


def dbTransactionsTableExists(cur):

  transactionsTable = cur.execute("""
    --begin-sql
    SELECT name FROM sqlite_master WHERE type='table' AND name='TRANSACTIONS'
    --end-sql
    """).fetchall()
  

  if transactionsTable == []:
    return False
  else:
    return True
  
def createCustomersTable(cur):

  cur.execute("""
    --begin-sql
    CREATE TABLE IF NOT EXISTS CUSTOMERS(
      id INTEGER PRIMARY KEY NOT NULL,
      customer_name VARCHAR(255),
      UNIQUE(customer_name)
    )
    --end-sql
    """)
  
  sql = ("INSERT OR IGNORE INTO CUSTOMERS (customer_name) VALUES (?)")

  cur.execute(sql, ("CASH",))


def createAliasesTable(cur):

  cur.execute("""
    --begin-sql
    CREATE TABLE IF NOT EXISTS ALIASES(
      id INTEGER PRIMARY KEY NOT NULL,
      customer_alias VARCHAR(255),
      customer_id INTEGER,
      FOREIGN KEY(customer_id) REFERENCES CUSTOMERS(id)
    )
    --end-sql
    """)


def createInvoicesTable(cur):

  cur.execute( """
    --begin-sql
    CREATE TABLE INVOICES (
      id INTEGER PRIMARY KEY NOT NULL,
      invoice_num INTEGER,
      amount REAL,
      date_issued DATE,
      issued_to VARCHAR(255),
      error_flagged INTEGER,
      customer_id INTEGER,
      FOREIGN KEY(customer_id) REFERENCES CUSTOMERS(id)      
    )
    --end-sql      
    """ )


def createTransactionsTable(cur):

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
      parent_trans INTEGER,
      FOREIGN KEY(invoice_id) REFERENCES INVOICES(id),
      FOREIGN KEY(parent_trans) REFERENCES TRANSACTIONS(id)
    )
    --end-sql
    """)


def checkDBStatus(cur, conn):

  if dbExists() == False:
    createDB(conn)

  if dbTransactionsTableExists(cur) == False:
    createTransactionsTable(cur)

  if dbInvoicesTableExists(cur) == False:
    createInvoicesTable(cur)
  
  createCustomersTable(cur)
  createAliasesTable(cur)

  conn.commit()