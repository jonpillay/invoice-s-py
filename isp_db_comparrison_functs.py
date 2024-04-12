import os
import sqlite3

def compareInvNumbers(conn, transInvNum):
  cur = conn.cursor()
  sql = "SELECT * FROM INVOICES WHERE invoice_num=?"

  cur.execute(sql, transInvNum)

  result = cur.fetchall()

  return result