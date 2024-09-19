import tkinter as tk
from ttkbootstrap.constants import *
import ttkbootstrap as tkb
from isp_frontend_functions import handleInvoiceUploadClick, handleTransactionUploadClick
from isp_frontend_display_functions import fetchCreditPreviewNumbers
from isp_db_helpers import genCustomerNamesIDsDict
from isp_credit_report_constructor import constructCreditReportDictionary
from isp_credit_report_printer import creditReportPrinter

from tkinter import messagebox
from datetime import date, datetime, timedelta

import os
import sqlite3




def renderMain(root):
  root.title("InvoicesPY")
  root.geometry('1400x600')

  root.rowconfigure(0, weight=1)
  root.rowconfigure(1, weight=20)
  root.columnconfigure(0, weight=1)

  title_label = tkb.Label(root, text="InvoicesPY for...", background='red')
  title_label.grid(row=0, column=0, sticky='nesw')

  main_frame = tkb.Frame(root, border=2, relief='raised')
  main_frame.grid(row=1, column=0, sticky='nesw')

  main_frame.rowconfigure(0, weight=10)
  main_frame.rowconfigure(1, weight=10)
  main_frame.columnconfigure(0, weight=1)

  upload_controls_frame = tkb.Frame(main_frame, border=2, relief='groove')
  credit_controls_top_frame = tkb.Frame(main_frame, border=2, relief='groove')

  upload_controls_frame.grid(row=0, column=0, sticky='nesw')
  credit_controls_top_frame.grid(row=1, column=0, sticky='nesw')

  upload_controls_frame.columnconfigure(0, weight=1)
  upload_controls_frame.rowconfigure(0, weight=1)



  # CSV Upload Widget
  upload_frame = tkb.Frame(upload_controls_frame)
  upload_frame.columnconfigure(0, weight=1)
  upload_frame.columnconfigure(1, weight=1)
  upload_frame.grid(row=0, column=0, sticky='nesw')
  upload_frame.rowconfigure(0, weight=1)


  invoice_upload = tkb.Button(upload_frame, text='Invoice Upload', bootstyle='primary', name="uploadInvoice", command= lambda: handleInvoiceUploadClick(root))
  invoice_upload.grid(row=0, column=0)

  statement_upload = tkb.Button(upload_frame, text='Statement Upload', bootstyle='primary', name="uploadTransaction", command= lambda: handleTransactionUploadClick(root))
  statement_upload.grid(row=0, column=1)

  # BOTTOM FRAME!

  credit_controls_top_frame.columnconfigure(0, weight=1)
  # credit_controls_top_frame.columnconfigure(1, weight=9)
  credit_controls_top_frame.rowconfigure(0, weight=1)
  credit_controls_top_frame.rowconfigure(1, weight=10)

  # system status info

  credit_controls_titles_frame = tkb.Frame(credit_controls_top_frame, border=1, relief='groove')
  credit_controls_titles_frame.columnconfigure(0, weight=8)
  credit_controls_titles_frame.columnconfigure(1, weight=10)
  credit_controls_titles_frame.rowconfigure(0, weight=1)
  credit_controls_titles_frame.grid(row=0, column=0, sticky='nesw', pady=2)

  credit_controls_sysinfo_label = tkb.Label(credit_controls_titles_frame, text="System Info")
  credit_controls_sysinfo_label.grid(row=0, column=0, padx=100, sticky='nesw')

  credit_controls_sysinfo_label = tkb.Label(credit_controls_titles_frame, text="Generate Credit Report")
  credit_controls_sysinfo_label.grid(row=0, column=1, padx=100, sticky='nesw')

  credit_controls_frame = tkb.Frame(credit_controls_top_frame)
  credit_controls_frame.columnconfigure(0, weight=8)
  credit_controls_frame.columnconfigure(1, weight=10)
  credit_controls_frame.rowconfigure(0, weight=1)
  credit_controls_frame.grid(row=1, column=0, sticky='nesw')

  system_status_frame = tkb.Frame(credit_controls_frame, border=2, relief='raised')
  system_status_frame.columnconfigure(0, weight=1)
  system_status_frame.rowconfigure(0, weight=1)
  system_status_frame.grid(row=0, column=0, sticky='nesw')

  system_status_label = tkb.Label(system_status_frame, text="System Boop Boop")
  system_status_label.grid(row=0, column=0, sticky='nesw')

  # Report Gen Widget Panel. Report Gen By Date Range and Customer.
  report_gen_controls = tkb.Frame(credit_controls_frame)
  report_gen_controls.columnconfigure(0, weight=5)
  report_gen_controls.columnconfigure(1, weight=5)
  report_gen_controls.columnconfigure(2, weight=3)
  report_gen_controls.rowconfigure(0, weight=4)
  report_gen_controls.rowconfigure(1, weight=10)
  report_gen_controls.rowconfigure(2, weight=15)
  report_gen_controls.grid(row=0, column=1, sticky='nesw')


  conn = sqlite3.connect(os.getenv("DB_NAME"))

  conn.execute('PRAGMA foreign_keys = ON')

  cur = conn.cursor()

  customersIdsDict = genCustomerNamesIDsDict(cur)
  nameList = list(customersIdsDict.keys())

  cur.close()
  conn.close()

  def onCustomerSelected(event):
    
    if report_gen_date_selector.entry.get():

      customer = report_gen_customer_selector.get()
      fromDate = report_gen_date_selector.entry.get()

      # fromDateObj = datetime.strptime(fromDate, '%m/%d/%Y')
      customerID = customersIdsDict[customer]

      conn = sqlite3.connect(os.getenv("DB_NAME"))

      conn.execute('PRAGMA foreign_keys = ON')

      cur = conn.cursor()

      invoiceCount, unpaidInvoiceCount = fetchCreditPreviewNumbers(fromDate, customerID, cur, conn)

      cur.close()

      conn.close()

      report_gen_invoice_total_label.config(text=f"Total Invoices Issued for {customer} since {fromDate} = {invoiceCount}")
      report_gen_unpaid_invoice_total_label.config(text=f"Total Unpaid Invoices for Period = {unpaidInvoiceCount}")

  report_gen_controls_customer_title = tkb.Label(report_gen_controls, text="Gen Report For")
  report_gen_controls_customer_title.grid(row=0, column=0, sticky='s')

  report_gen_controls_date_title = tkb.Label(report_gen_controls, text="From Date")
  report_gen_controls_date_title.grid(row=0, column=1, sticky='s')

  report_gen_customer_selector_frame = tkb.Frame(report_gen_controls)
  report_gen_customer_selector_frame.rowconfigure(0, weight=3)
  report_gen_customer_selector_frame.rowconfigure(1, weight=5)
  report_gen_customer_selector_frame.columnconfigure(0, weight=1)
  report_gen_customer_selector_frame.grid(row=1, column=0, sticky='n')

  report_gen_customer_selector = tkb.Combobox(report_gen_customer_selector_frame, values=nameList)

  report_gen_customer_selector.bind("<<ComboboxSelected>>", onCustomerSelected)

  report_gen_customer_selector.grid(row=0, column=0, sticky='s')

  report_gen_customer_label = tkb.Label(report_gen_customer_selector_frame, text="Select a Customer")
  report_gen_customer_label.grid(row=1, column=0, sticky='n')

  def onDateSelected(event):
    
    if report_gen_customer_selector.get():

      customer = report_gen_customer_selector.get()
      fromDate = report_gen_date_selector.entry.get()

      # fromDateObj = datetime.strptime(fromDate, '%m/%d/%Y')
      customerID = customersIdsDict[customer]

      conn = sqlite3.connect(os.getenv("DB_NAME"))

      conn.execute('PRAGMA foreign_keys = ON')

      cur = conn.cursor()

      invoiceCount, unpaidInvoiceCount = fetchCreditPreviewNumbers(fromDate, customerID, cur, conn)

      cur.close()

      conn.close()

      report_gen_invoice_total_label.config(text=f"Total Invoices Issued for {customer} since {fromDate} = {invoiceCount}")
      report_gen_unpaid_invoice_total_label.config(text=f"Total Unpaid Invoices for Period = {unpaidInvoiceCount}")

      # run function to collect number of invoices, and unpaid invoices
      # take results of functions and print them to label below

  report_gen_date_selector_frame = tkb.Frame(report_gen_controls)
  report_gen_date_selector_frame.rowconfigure(0, weight=3)
  report_gen_date_selector_frame.rowconfigure(1, weight=5)
  report_gen_date_selector_frame.columnconfigure(0, weight=1)
  report_gen_date_selector_frame.grid(row=1, column=1, sticky='n')

  report_gen_date_selector = tkb.DateEntry(report_gen_date_selector_frame, startdate=datetime.today()-timedelta())

  report_gen_date_selector.entry.bind("<FocusIn>", onDateSelected)

  report_gen_date_selector.grid(row=0, column=0, sticky='s')

  report_gen_date_label = tkb.Label(report_gen_date_selector_frame, text="Select a Date")
  report_gen_date_label.grid(row=1, column=0, sticky='n')

  report_gen_button_frame = tkb.Frame(report_gen_controls)
  report_gen_button_frame.columnconfigure(0, weight=1)
  report_gen_button_frame.rowconfigure(0, weight=3)
  report_gen_button_frame.rowconfigure(1, weight=6)
  report_gen_button_frame.grid(row=1, column=2, sticky='n')

  def triggerGenCreditReport():

    if not report_gen_date_selector.entry.get():

      report_gen_invoice_total_label.config(text=f"Please Select a Starting Date")

      return None
    
    elif not report_gen_customer_selector.get():

      report_gen_invoice_total_label.config(text=f"Please Select a Customer")

      return None
    
    else:
    
      customerID = customersIdsDict[report_gen_customer_selector.get()]
      startDate = report_gen_date_selector.entry.get()

      conn = sqlite3.connect(os.getenv("DB_NAME"))

      conn.execute('PRAGMA foreign_keys = ON')

      cur = conn.cursor()
      
      creditReportDict = constructCreditReportDictionary(customerID, startDate, conn, cur)

      creditReportPrinter(creditReportDict, conn, cur)
    
  report_gen_button = tkb.Button(report_gen_button_frame, text="Gen Report", bootstyle='success', name="genReport", command=triggerGenCreditReport)
  report_gen_button.grid(row=0, column=0, sticky='s')

  report_gen_preview_frame = tkb.Frame(report_gen_controls)
  report_gen_preview_frame.rowconfigure(0, weight=1)
  report_gen_preview_frame.rowconfigure(1, weight=1)
  report_gen_preview_frame.rowconfigure(2, weight=1)
  report_gen_preview_frame.grid(row=2, column=0, columnspan=2)

  report_gen_invoice_total_label = tkb.Label(report_gen_preview_frame, text="Make selection for preview results.")
  report_gen_invoice_total_label.grid(row=0, column=0, columnspan=2)

  report_gen_unpaid_invoice_total_label = tkb.Label(report_gen_preview_frame, text="")
  report_gen_unpaid_invoice_total_label.grid(row=1, column=0, padx=20, columnspan=2)

  report_gen_balance_label = tkb.Label(report_gen_preview_frame, text="")
  report_gen_balance_label.grid(row=2, column=0, padx=20, columnspan=2)

  # report_gen_invoice_paid_frame = tkb.Frame(report_gen_controls, bootstyle="dark")
  # report_gen_invoice_paid_frame.grid(row=2, column=1, sticky='nesw')

  # # Tabs for switching between different portions of results (paid, outstanding, possible errors)
  # results_dummy_tabs = tkb.Label(credit_controls_top_frame, text='Results Dummy Tabs', background='#8B8000')

  # # Query Result Printed to console. Each invoice is printed with related payment details- 
  # # except in the case of payments without invoice, which are displayed alone (and marked)
  # results_dummy_text = tkb.Label(credit_controls_top_frame, text='Results Dummy Text', background='orange')

  # results_dummy_tabs.grid(row=0, column=0, sticky='nesw')
  # results_dummy_text.grid(row=1, column=0, sticky='nesw')