import sqlite3
import os

from dotenv import load_dotenv, dotenv_values
load_dotenv()

# --begin-sql and --end-sql use python-string-sql in vscode to highlight sql cmds and queries

def dbExists():
  return os.path.exists('./' + os.getenv("DB_NAME"))


def dbInvoicesTableExist():
  con = sqlite3.connect(os.getenv("DB_NAME"))
  cur = con.cursor()

  invoicesTable = cur.execute("""
    --begin-sql
    SELECT tableName FROM sqlite_master WHERE type='table'
    AND tableName='INVOICES'
    --end-sql
    """).fetchall()

  if invoicesTable == []:
    return False
  else:
    return True


def DBTransactionsTableExist():
  con = sqlite3.connect(os.getenv("DB_NAME"))
  cur = con.cursor()

  transactionsTable = cur.execute(
  """SELECT tableName FROM sqlite_master WHERE type='table'
  AND tableName='TRANSACTIONS'; """).fetchall()

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

  cur.execute("""
    --begin-sql
    CREATE TABLE INVOICES(
      invoice_num INT,
      amount REAL,
      date_issued DATE,
      company_name VARCHAR,
    )
    --end-sql      
    """)
  
  con.commit()
  con.close()


def createTransactionsTable():
  con = sqlite3.connect(os.getenv("DB_NAME"))
  cur = con.cursor()

  cur.execute("""
    --begin-sql
    CREATE TABLE TRANSACTIONS(
      invoice_num INT,
      amount REAL,
      paid_on DATE,
      company_name VARCHAR,
    )
    --end-sql
    """)
  
  con.commit()
  con.close()