from isp_dataframes import Transaction, Invoice
import datetime


f = open('../output.txt', 'r')

if f != "TEST":

  outputDict = eval(f.read())

  print(type(outputDict))