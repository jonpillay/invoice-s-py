import sqlite3
import os

from output_test import outputDict as testOutputDict

from isp_db_helpers import genCustomerNamesIDsDict

from isp_PDF_class import TransactionUploadPDF

from isp_credit_report_constructor import constructCreditReportDictionary


def creditReportPrinter(creditReportDict, con, cur):

  results = TransactionUploadPDF('P', 'mm', 'A4')

  results.add_page()
  results.register_fonts()

  customerIDsDict = genCustomerNamesIDsDict(cur)

  customerName = customerIDsDict[creditReportDict["customerID"]]

  results.printCategoryTitle(f"Credit Report for {customerName} From {creditReportDict['afterDate']}")

  results.output('../testCredit.pdf')





con = sqlite3.connect(os.getenv("DB_NAME"))

con.execute('PRAGMA foreign_keys = ON')

cur = con.cursor()

reportDict = constructCreditReportDictionary(9, '2020-10-01', con, cur)

creditReportPrinter(reportDict, con, cur)

cur.close()

con.close()
