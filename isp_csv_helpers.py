import os
import re
from dotenv import load_dotenv, dotenv_values
from datetime import datetime

load_dotenv()

from tkinter import filedialog
import csv

def getFilename ():

  filename = filedialog.askopenfilename(
    initialdir=os.getenv("CSV_INITIAL_PATH"),
    title="Open Document",
    filetypes=([("CSV Files","*.csv*")])
  )
  
  return filename

def cleanTransactionRaw(entry):

  invMatches = re.findall(os.getenv('CSV_TRANSACTION_REGEX'), entry[2])

  customer = entry[2].split(',')[0].strip()

  formattedDate = datetime.strptime(entry[0], '%d %b %Y').strftime('%Y-%m-%d')

  payment = float(entry[3])

  paidBy = entry[1]

  return [invMatches, payment, formattedDate, customer, paidBy, entry] 