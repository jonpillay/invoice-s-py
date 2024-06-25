import tkinter as tk
import ttkbootstrap as tkb
from tkinter import ttk

import sqlite3
import os

from isp_treeviews import renderPromptInvoices, renderPromptTransactions, renderPromptMulitTransactions
from isp_db_helpers import fetchUnpaidInvoicesByCustomerBeforeDate
from isp_data_handlers import genInvoiceDCobj



def openVerifyCloseEnoughtMatch(root, transaction, invoice, matchVerifiedBool):

  promptWindow = tk.Toplevel(root)
  promptWindow.title('Match Close Enough')
  promptWindow.geometry('1100x600')

  def updateWindowHeight():
    
    height = sum([widget.winfo_height() for widget in promptWindow.winfo_children()])

    promptWindow.geometry(f'1000x{height+200}')

  title_label = tkb.Label(promptWindow, text=f"Verify Match", background='red')
  title_label.pack(side='top')

  main_frame = tkb.Frame(promptWindow)
  main_frame.pack(side='top', expand=True)

  prompt_frame = tkb.Frame(main_frame)
  prompt_frame.pack()

  prompt_label = tkb.Label(prompt_frame, text=f"Match Invoice amount {invoice.amount} to Transaction payment {transaction.amount}", font=('Helvetica-bold', 11), justify='center')
  prompt_label.pack(pady=10)

  og_string_label = tkb.Label(prompt_frame, wraplength=900, text=f"\"{transaction.og_string}\"")
  og_string_label.pack()
  og_string_label.configure(anchor='center', justify='center')

  renderPromptTransactions(main_frame, [transaction])

  invoiceTable = ttk.Treeview(main_frame, show='headings', height=1, selectmode=tk.BROWSE)

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

  formattedDate = invoice.date_issued.strftime("%d/%m/%Y")

  invoiceTable.insert(parent='', index=0, values=(invoice.invoice_num, invoice.issued_to, invoice.amount, formattedDate, invoice.error_notes))

  invoiceTable.pack(padx=10)

  style = ttk.Style(invoiceTable)
  style.theme_use('alt')
  style.configure("Treeview",
    rowheight=30
  )

  verification_frame = tkb.Frame(main_frame)
  verification_frame.pack(pady=10)

  totals_label = tkb.Label(verification_frame, text=f"Make Payment Match? Difference = {round(abs(invoice.amount - transaction.amount), 2)}p", font=('Helvetica-bold', 11))
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
      matchVerifiedBool.set(True)
      promptWindow.destroy()

  def errorFlagTransaction():
      matchVerifiedBool.set(False)
      promptWindow.destroy()
      
  promptWindow.wait_window()



def openSelectBetweenCloseEnoughInvoices(root, transaction, closeEnoughMatched, invoiceIDVar):

  invoiceList = closeEnoughMatched

  promptWindow = tk.Toplevel(root)
  promptWindow.title('Chose Invoice To Pay')
  promptWindow.geometry('1100x600')

  def updateWindowHeight():
    
    height = sum([widget.winfo_height() for widget in promptWindow.winfo_children()])

    promptWindow.geometry(f'1000x{height+200}')

  title_label = tkb.Label(promptWindow, text=f"Select an Invoice to Pay", background='red')
  title_label.pack(side='top')

  main_frame = tkb.Frame(promptWindow)
  main_frame.pack(side='top', expand=True)

  prompt_frame = tkb.Frame(main_frame)
  prompt_frame.pack()

  prompt_label = tkb.Label(prompt_frame, text=f"Multiple Invoices Within Error Margin. Select One Invoice to Pay", font=('Helvetica-bold', 11), justify='center')
  prompt_label.pack(pady=10)

  og_string_label = tkb.Label(prompt_frame, wraplength=900, text=f"\"{transaction.og_string}\"")
  og_string_label.pack()
  og_string_label.configure(anchor='center', justify='center')

  renderPromptMulitTransactions(main_frame, [transaction])

  invoiceTable = ttk.Treeview(main_frame, show='headings', height=len(invoiceList), selectmode=tk.BROWSE)

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

  style = ttk.Style(invoiceTable)
  style.theme_use('alt')
  style.configure("Treeview",
    rowheight=30
  )

  verification_frame = tkb.Frame(main_frame)
  verification_frame.pack(pady=10)

  difference_label = tkb.Label(verification_frame, text=f"0", font=('Helvetica-bold', 11))
  difference_label.pack(pady=10)

  # Need to alter verification, and add in a lebel showing the difference error of the selected invoice.

  verify_button = tkb.Button(main_frame, text="Select Invoice to Pay", command=lambda: selectInvoice())
  verify_button.pack()

  promptWindow.update()

  updateWindowHeight()

  def display_invoice_error(event):
     
     selectedInvoice = invoiceTable.focus()

     if selectedInvoice:
        invoiceDetails = invoiceTable.item(selectedInvoice)
        invoiceAmount = float(invoiceDetails.get("values")[2])
        errorDif = round(invoiceAmount - transaction.amount, 2)
        difference_label.config(text=f"Difference is {errorDif}")

  def selectInvoice():
      
      selectedRow = invoiceTable.focus()

      invoiceDetails = invoiceTable.item(selectedRow)

      invoiceIDVar.set(invoiceDetails.get("values")[0])

      promptWindow.destroy()
  
  invoiceTable.bind("<<TreeviewSelect>>", display_invoice_error)

  promptWindow.wait_window()

  

  def openVerifyErrorCorrectionCloseEnoughMatch(root, transaction, matchedInvoice, OGerrorTrans, OGdummyTrans, matchVerifiedBool):

    promptWindow = tk.Toplevel(root)
    promptWindow.title('Match Close Enough')
    promptWindow.geometry('1100x600')

    def updateWindowHeight():
      
      height = sum([widget.winfo_height() for widget in promptWindow.winfo_children()])

      promptWindow.geometry(f'1000x{height+200}')

    title_label = tkb.Label(promptWindow, text=f"Verify Match", background='red')
    title_label.pack(side='top')

    main_frame = tkb.Frame(promptWindow)
    main_frame.pack(side='top', expand=True)

    prompt_frame = tkb.Frame(main_frame)
    prompt_frame.pack()

    # render the transaction that doesn't match directly by amount

    formattedTransDate = transaction.paid_on.strftime("%d/%m/%Y")

    og_trans_prompt_label = tkb.Label(prompt_frame, text=f"Transaction dated {formattedTransDate} does not match by Amount", font=('Helvetica-bold', 11), justify='center')
    og_trans_prompt_label.pack(pady=10)

    og_string_label = tkb.Label(prompt_frame, wraplength=900, text=f"\"{transaction.og_string}\"")
    og_string_label.pack()
    og_string_label.configure(anchor='center', justify='center')

    renderPromptTransactions(main_frame, [transaction])



    # Render Error corrected transaction

    formattedOGerrorTransDate = OGerrorTrans.paid_on.strftime("%d/%m/%Y")

    og_error_prompt_label = tkb.Label(prompt_frame, text=f"Transaction dated {formattedOGerrorTransDate} was correct by {OGdummyTrans.amount}", font=('Helvetica-bold', 11), justify='center')
    og_error_prompt_label.pack(pady=10)

    og_error_string_label = tkb.Label(prompt_frame, wraplength=900, text=f"\"{OGerrorTrans.og_string}\"")
    og_error_string_label.pack()
    og_error_string_label.configure(anchor='center', justify='center')

    renderPromptTransactions(main_frame, [OGerrorTrans])

    # Render the the invoice that now Matches

    invoice_match_label = tkb.Label(prompt_frame, text=f"Invoice Num {matchedInvoice.invoice_num} now matches with a difference", font=('Helvetica-bold', 11), justify='center')
    invoice_match_label.pack(pady=10)

    invoiceTable = ttk.Treeview(main_frame, show='headings', height=1, selectmode=tk.BROWSE)

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

    formattedDate = matchedInvoice.date_issued.strftime("%d/%m/%Y")

    invoiceTable.insert(parent='', index=0, values=(matchedInvoice.invoice_num, matchedInvoice.issued_to, matchedInvoice.amount, formattedDate, matchedInvoice.error_notes))

    invoiceTable.pack(padx=10)

    style = ttk.Style(invoiceTable)
    style.theme_use('alt')
    style.configure("Treeview",
      rowheight=30
    )

    verification_frame = tkb.Frame(main_frame)
    verification_frame.pack(pady=10)

    totals_label = tkb.Label(verification_frame, text=f"Make Payment Match? Difference = {round(abs(matchedInvoice.amount - transaction.amount + OGdummyTrans.amount), 2)}p", font=('Helvetica-bold', 11))
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
        matchVerifiedBool.set(True)
        promptWindow.destroy()

    def errorFlagTransaction():
        matchVerifiedBool.set(False)
        promptWindow.destroy()
        
    promptWindow.wait_window()