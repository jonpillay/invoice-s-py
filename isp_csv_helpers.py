import os
import re
from dotenv import load_dotenv, dotenv_values

load_dotenv()

from tkinter import filedialog
import csv

def getFilename():

  filename = filedialog.askopenfilename(
    initialdir=os.getenv("CSV_INITIAL_PATH"),
    title="Open Invoice",
    filetypes=([("CSV Files","*.csv*")])
  )
  
  return filename