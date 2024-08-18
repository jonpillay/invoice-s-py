import json
import datetime
from isp_dataframes import Transaction, Invoice

f = open('../output.txt', 'r')

outputDict = eval(f.read())