import tkinter as tk
import ttkbootstrap as tkb
from tkinter import ttk

import sqlite3
import os

from isp_treeviews import renderPromptInvoices, renderPromptTransactions, renderPromptMulitTransactions
from isp_db_helpers import fetchUnpaidInvoicesByCustomerBeforeDate
from isp_data_handlers import genInvoiceDCobj
from isp_trans_verify import verifyTransactionAmount


def openMultiInvoicePrompt(root, transaction, invoiceList, checkedBool, verifyBool):

    promptWindow = tk.Toplevel(root)
    promptWindow.title('Invoices Match?')
    promptWindow.geometry('1100x600')

    def updateWindowHeight():
      
      height = sum([widget.winfo_height() for widget in promptWindow.winfo_children()])

      promptWindow.geometry(f'1000x{height+200}')

    title_label = tkb.Label(promptWindow, text=f"Multiple Invoice Transaction", background='red')
    title_label.pack(side='top')

    main_frame = tkb.Frame(promptWindow)
    main_frame.pack(side='top', expand=True)

    prompt_frame = tkb.Frame(main_frame)
    prompt_frame.pack()

    prompt_label = tkb.Label(prompt_frame, text=f"Multiple Invoice Transaction from {transaction.paid_by} for invoices {transaction.invoice_num} to {transaction.high_invoice}\n Total Paid £{transaction.amount}", font=('Helvetica-bold', 11), justify='center')
    prompt_label.pack(pady=10)

    og_string_label = tkb.Label(prompt_frame, wraplength=900, text=f"\"{transaction.og_string}\"")
    og_string_label.pack()
    og_string_label.configure(anchor='center', justify='center')

    renderPromptMulitTransactions(main_frame, [transaction])

    renderPromptInvoices(main_frame, invoiceList)

    verification_frame = tkb.Frame(main_frame)
    verification_frame.pack()

    total_invoiced = round(sum([invoice.amount for invoice in invoiceList]), 2)

    totals_label = tkb.Label(verification_frame, text=f"Total Invoiced = {total_invoiced} > Total Paid = {transaction.amount}", font=('Helvetica-bold', 11))
    totals_label.pack(pady=10)

    verification_buttons_frame = tkb.Frame(verification_frame)
    verification_buttons_frame.columnconfigure(0, weight=1)
    verification_buttons_frame.columnconfigure(1, weight=1)

    verification_buttons_frame.pack(pady=20)

    verify_button = tkb.Button(verification_buttons_frame, text="Verify", command=lambda: verifyTransaction())
    verify_button.grid(row=0, column=0, padx=40)

    error_button = tkb.Button(verification_buttons_frame, text="Error", command=lambda: errorFlagTransaction())
    error_button.grid(row=0, column=1, padx=40)

    promptWindow.update()

    updateWindowHeight()

    def verifyTransaction():
       checkedBool.set(True)
       verifyBool.set(True)
       promptWindow.destroy()

    def errorFlagTransaction():
       checkedBool.set(True)
       verifyBool.set(False)
       promptWindow.destroy()

    promptWindow.wait_window()

# User prompt for transactions that have no invoice number assotiated, but have been matched with a group of unpaid invoices by amount

def openMatchedMultiInvoicePrompt(root, transaction, invoiceList, verifyBool):

    promptWindow = tkb.Toplevel(root)
    promptWindow.title('Invoices Match?')
    promptWindow.geometry('1100x600')

    def updateWindowHeight():
      
      height = sum([widget.winfo_height() for widget in promptWindow.winfo_children()])

      promptWindow.geometry(f'1000x{height+200}')

    title_label = tkb.Label(promptWindow, text=f"Multiple Invoice Transaction", background='red')
    title_label.pack(side='top')

    main_frame = tkb.Frame(promptWindow)
    main_frame.pack(side='top', expand=True)

    prompt_frame = tkb.Frame(main_frame)
    prompt_frame.pack()

    prompt_label = tkb.Label(prompt_frame, text=f"Multiple Invoice Match No Num Transaction from {transaction.paid_by} for invoices {invoiceList[0].invoice_num} to {invoiceList[-1].invoice_num}\n Total Paid £{transaction.amount}", font=('Helvetica-bold', 11), justify='center')
    prompt_label.pack(pady=10)

    og_string_label = tkb.Label(prompt_frame, wraplength=900, text=f"\"{transaction.og_string}\"")
    og_string_label.pack()
    og_string_label.configure(anchor='center', justify='center')

    renderPromptMulitTransactions(main_frame, [transaction])

    renderPromptInvoices(main_frame, invoiceList)

    verification_frame = tkb.Frame(main_frame)
    verification_frame.pack()

    total_invoiced = round(sum([invoice.amount for invoice in invoiceList]), 2)

    totals_label = tkb.Label(verification_frame, text=f"Total Invoiced = {total_invoiced} > Total Paid = {transaction.amount}", font=('Helvetica-bold', 11))
    totals_label.pack(pady=10)

    verification_buttons_frame = tkb.Frame(verification_frame)
    verification_buttons_frame.columnconfigure(0, weight=1)
    verification_buttons_frame.columnconfigure(1, weight=1)

    verification_buttons_frame.pack(pady=20)

    verify_button = tkb.Button(verification_buttons_frame, text="Pay Matched Invoice Group With Transaction?", command=lambda: verifyTransaction())
    verify_button.grid(row=0, column=0, padx=40)

    error_button = tkb.Button(verification_buttons_frame, text="Error", command=lambda: errorFlagTransaction())
    error_button.grid(row=0, column=1, padx=40)

    promptWindow.update()

    updateWindowHeight()

    def verifyTransaction():
       verifyBool.set(True)
       promptWindow.destroy()

    def errorFlagTransaction():
       verifyBool.set(False)
       promptWindow.destroy()

    promptWindow.wait_window()



def openSelectBetweenInvoices(root, transaction, candInvoices, invoiceIDVar):

  invoiceList = candInvoices

  promptWindow = tkb.Toplevel(root)
  promptWindow.title('Invoices Match?')
  promptWindow.geometry('1100x600')

  def updateWindowHeight():
    
    height = sum([widget.winfo_height() for widget in promptWindow.winfo_children()])

    promptWindow.geometry(f'1000x{height+200}')

  title_label = tkb.Label(promptWindow, text=f"Select an Invoice", background='red')
  title_label.pack(side='top')

  main_frame = tkb.Frame(promptWindow)
  main_frame.pack(side='top', expand=True)

  prompt_frame = tkb.Frame(main_frame)
  prompt_frame.pack()

  prompt_label = tkb.Label(prompt_frame, text=f"Multiple Invoices Match Via Total Paid £{transaction.amount}", font=('Helvetica-bold', 11), justify='center')
  prompt_label.pack(pady=10)

  og_string_label = tkb.Label(prompt_frame, wraplength=900, text=f"\"{transaction.og_string}\"")
  og_string_label.pack()
  og_string_label.configure(anchor='center', justify='center')

  renderPromptMulitTransactions(main_frame, [transaction])

  invoiceTable = tkb.Treeview(main_frame, style='success', show='headings', height=len(invoiceList), selectmode=tk.BROWSE)

  invoiceTable['columns'] = ('invoice_num', 'issued_to', 'amount', 'date_issued', 'notes')

  invoiceTable.column('invoice_num', width=110, anchor='center')
  invoiceTable.heading('invoice_num', text="Invoice #")

  invoiceTable.column('issued_to', width=270, anchor='center')
  invoiceTable.heading('issued_to', text='Customer')
  
  invoiceTable.column('amount', width=110, anchor='center')
  invoiceTable.heading('amount', text='Amount (£)')
  
  invoiceTable.column('date_issued', width=110, anchor='center')
  invoiceTable.heading('date_issued', text='Issued On')
  
  invoiceTable.column('notes', width=360, anchor='center')
  invoiceTable.heading('notes', text='Notes')

  for i in range(len(invoiceList)):

    formattedDate = invoiceList[i].date_issued.strftime("%d/%m/%Y")

    invoiceTable.insert(parent='', index=i, values=(invoiceList[i].invoice_num, invoiceList[i].issued_to, invoiceList[i].amount, formattedDate, invoiceList[i].error_notes))

  invoiceTable.pack(padx=10)

  # style = ttk.Style(invoiceTable)
  # style.theme_use('alt')
  # style.configure("Treeview",
  #   rowheight=30
  # )

  verification_frame = tkb.Frame(main_frame)
  verification_frame.pack(pady=10)

  totals_label = tkb.Label(verification_frame, text=f"Select One Invoice", font=('Helvetica-bold', 11))
  totals_label.pack(pady=10)

  verify_button = tkb.Button(main_frame, text="Select Invoice to Pay", command=lambda: selectInvoice())
  verify_button.pack()

  promptWindow.update()

  updateWindowHeight()

  def selectInvoice():
      
      selectedRow = invoiceTable.focus()

      invoiceDetails = invoiceTable.item(selectedRow)

      invoiceIDVar.set(invoiceDetails.get("values")[0])

      promptWindow.destroy()

  promptWindow.wait_window()