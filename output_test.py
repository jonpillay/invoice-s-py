from isp_dataframes import Transaction, Invoice
import datetime


def readOutputDictRaw():

  f = open('../output.txt', 'r')

  outputDict = None

  if f != "TEST":

    outputDict = eval(f.read())

  return outputDict

  # print(type(outputDict))