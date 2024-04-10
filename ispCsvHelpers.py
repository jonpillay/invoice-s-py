import os
import re
from dotenv import load_dotenv, dotenv_values

load_dotenv()

from tkinter import filedialog
import csv

def getCSVfile():

  matchList = []
  errorList= []
  count = 0

  filename = filedialog.askopenfilename(
    initialdir=os.getenv("CSV_INITIAL_PATH"),
    title="Open Invoice",
    filetypes=([("CSV Files","*.csv*")])
  )

  with open(filename) as csv_file:
    csv_reader = csv.reader(csv_file)
    count = 0
    for entry in csv_reader:
      count += 1
      matchFound = False
      for el in entry:
        match = re.findall(os.getenv("CSV_TRANSACTION_REGEX"), el)
        if match:
          # print(match)
          matchList.append(match[0])
          matchFound = True
      if matchFound == False:
        errorList.append(entry)

      # if len(matches) == 0:
      #   errorList.append(entry)
      # else:
      #   for match in matches:
      #     matchList.append(match)

    # print(count)
    # print(len(matchList))
    for error in errorList:
      print(error)
    
    # for error in errorList:
    #   print(error)