import os

from dotenv import load_dotenv, dotenv_values

load_dotenv()

from tkinter import filedialog
import csv

def getCSVfile():
  filename = filedialog.askopenfilename(
    initialdir=os.getenv("CSV_INITIAL_PATH"),
    title="Open Invoice",
    filetypes=([("CSV Files","*.csv*")])
  )

  with open(filename) as csv_file:
    csv_reader = csv.reader(csv_file)

    for entry in csv_reader:
      print(entry)