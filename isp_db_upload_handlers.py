import csv
from tkinter import filedialog
import os

def handleInvoiceUpload(filename):

  with open(filename) as csv_file:
    CSVreader = csv.reader(csv_file)

    for entry in CSVreader:
      print(entry)