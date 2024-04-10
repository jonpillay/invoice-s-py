import sqlite3
import os

def dbStartUpChecks():
  return os.path.exists('./test.txt')