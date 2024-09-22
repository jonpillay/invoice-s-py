import sqlite3
import os
from datetime import datetime

from isp_db_helpers import genIDsCustomerNamesDict
from isp_dataframes import Invoice, Transaction

from isp_PDF_class import TransactionUploadPDF

from isp_credit_report_constructor import constructCreditReportDictionary

import subprocess
import time


def creditReportPrinter(creditReportDict, con, cur):

  results = TransactionUploadPDF('P', 'mm', 'A4')

  results.add_page()
  results.register_fonts()

  customerIDsDict = genIDsCustomerNamesDict(cur)

  customerName = customerIDsDict[creditReportDict["customerID"]]

  results.printCategoryTitle(f"Credit Report for ")
  results.set_x(20)
  results.printCustomerName(f"{customerName}")
  results.ln(2)
  results.set_x(25)

  results.printInlineDescription("From")
  results.printInlineBold(f"{creditReportDict['afterDate']}")
  results.printInlineDescription("To Present -")
  results.printInlineDescription("Invoices Issued =")
  results.printInlineBold(f"{creditReportDict['invoicesIssued']}")
  results.printInlineDescription(" Invoices Paid =")
  results.printInlineBold(f"{creditReportDict['invoicesPaid']}")
  results.ln(7)
  results.set_x(25)

  results.printInlineDescription(f"Balance To Date =")
  results.set_x(50)
  results.printInlineBold(f"£{creditReportDict['ballance']} ")
  results.printInlineDescription(f"  Corrections = ")
  results.printInlineBold(f"£{creditReportDict['correctionAmount']}")

  results.ln(8)

  results.printCategoryTitle("PAID")

  for paidPair in creditReportDict['paid']:

    # check if the el is a single invoice payment or multi invoice payment - if first el in the subject is an Invoice obj 
    # the subject will be a single invoice payment, if it is a Transaction, it will be a multi invoice payment.
    if type(paidPair[0]) == Invoice:
      
      results.printMatchedSingles(paidPair)

    elif type(paidPair[0]) == Transaction:

      results.printMultiInvoiceTransactionMatch(paidPair)

    else:
      results.printInlineBold("Corrupted creditReportDict Entry")

  results.ln(10)

  # print unpaid invoices

  results.printCategoryTitle("Unpaid Invoices")

  unpaidTotal = 0

  for unpaidInvoice in creditReportDict['unpaid']:

    unpaidTotal += unpaidInvoice.amount

    results.printInvoiceNumber(unpaidInvoice.invoice_num)
    results.set_x(20) 
    results.printInvoice(unpaidInvoice)
    results.ln(5)

  results.ln(5)
  results.printInlineDescription("Total Unpaid Invoices = ")
  results.printInlineBold(f"£{str(creditReportDict['unPaidInvoicesTotal'])}")
  results.ln(5)

  results.printCategoryTitle("UnMatched Transactions")
  results.ln(5)

  for unMatchedTransaction in creditReportDict['unMatchedTransactions']:

    results.set_x(25)
    results.printTransaction(unMatchedTransaction)
  
    if unMatchedTransaction.error_notes != None:

      results.ln(5)
      results.set_x(30)
      results.printInlineDescription(unMatchedTransaction.error_notes)

    results.ln(8)

  results.set_x(20)
  results.printInlineDescription("Un-Matched Transaction Total = ")
  results.printInlineBold(f"£{str(creditReportDict['unMatchedTransactionsTotal'])}")
  results.ln(10)

  results.set_x(18)
  results.printInlineDescriptionLarge("Invoices Issued for Period = ")
  results.printInlineBoldLarge(str(creditReportDict['invoicesIssued']))
  results.ln(10)

  results.set_x(18)
  results.printInlineDescriptionLarge("Invoices Paid for Period = ")
  results.printInlineBoldLarge(str(creditReportDict['invoicesPaid']))
  results.ln(10)

  results.set_x(18)
  results.printInlineDescriptionLarge("Total Un-Paid Invoices = ")
  results.printInlineBoldLarge(f"£{str(creditReportDict['unPaidInvoicesTotal'])}")
  results.ln(10)

  results.set_x(18)
  results.printInlineDescriptionLarge("Total Un-Matched Transactions = ")
  results.printInlineBoldLarge(f"£{str(creditReportDict['unMatchedTransactionsTotal'])}")
  results.ln(10)

  results.set_x(18)
  results.printInlineDescriptionLarge("Corrections for Period = ")
  results.printInlineBoldLarge(f"£{str(0 - creditReportDict['correctionAmount'])}")
  results.ln(5)
  results.set_x(20)
  results.printInlineDescription("Correction amount is the total of corrected errors on matched Invoices for period.")
  results.ln(4)
  results.set_x(20)
  results.printInlineDescription("Positive number is in Customer's favour.")
  results.ln(8)

  results.set_x(18)
  results.printInlineDescriptionLarge("Closing Balance = ")
  results.printInlineBoldLarge(f"£{str(creditReportDict['ballance'])}")
  results.ln(10)

  dateFrom = creditReportDict['afterDate'].replace('/', '_')
  dateToday = datetime.today().strftime("%d_%m_%Y")
  formattedCustomerName = customerName.replace(" ", "_")
  
  outputDir = os.path.join("ISPCreditReports", formattedCustomerName)
  outputFile = os.path.join(outputDir, f"{formattedCustomerName}-{dateFrom}-{dateToday}.pdf")

  if not os.path.exists(os.path.join("ISPCreditReports", formattedCustomerName)):

    os.makedirs(outputDir, exist_ok=True)

  results.output(outputFile)

  # subprocess.Popen([outputFile], shell=True)

  os.startfile(outputFile)