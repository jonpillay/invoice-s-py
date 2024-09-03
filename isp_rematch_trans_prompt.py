import tkinter as tk
import ttkbootstrap as tkb
from tkinter import ttk

from isp_treeviews import renderPromptInvoices, renderPromptTransactions, renderPromptMulitTransactions, renderSimplePromptInvoices
from isp_db_helpers import fetchUnpaidInvoicesByCustomerBeforeDate
from isp_data_handlers import genInvoiceDCobj

def openRematchTransactionPrompt(root, transaction, errorInvoice, reMatchInvoice, rematchVerifiedBool):

  promptWindow = tkb.Toplevel(root)
  promptWindow.title('Match Close Enough')
  promptWindow.geometry('1100x600')

  title_label = tkb.Label(promptWindow, text=f"RematchTransaction?", background='red')
  title_label.pack(side='top')

  main_frame = tkb.Frame(promptWindow)
  main_frame.pack(side='top', expand=True)

  prompt_frame = tkb.Frame(main_frame)
  prompt_frame.pack()

  prompt_label = tkb.Label(prompt_frame, text=f"Transaction from {transaction.paid_by} marked with invoice # {transaction.invoice_num}", font=('Helvetica-bold', 11), justify='center')
  prompt_label.pack(pady=10)

  renderPromptTransactions(prompt_frame, [transaction])

  errorAmount = round(errorInvoice.amount - transaction.amount, 2)

  prompt_label = tkb.Label(prompt_frame, text=f"does not match by {errorAmount} to", font=('Helvetica-bold', 11), justify='center')
  prompt_label.pack(pady=10)

  if errorInvoice.error_notes == None:
    renderSimplePromptInvoices(prompt_frame, [errorInvoice])
  else:
    renderPromptInvoices(prompt_frame, [errorInvoice])

  prompt_label = tkb.Label(prompt_frame, text=f"Transaction amount matches exactly to Invoice # {reMatchInvoice.invoice_num}", font=('Helvetica-bold', 11), justify='center')
  prompt_label.pack(pady=10)

  if reMatchInvoice.error_notes == None:
    renderSimplePromptInvoices(prompt_frame, [reMatchInvoice])
  else:
    renderPromptInvoices(prompt_frame, [reMatchInvoice])

  verification_frame = tkb.Frame(main_frame)
  verification_frame.pack(pady=10)

  rematch_prompt = tkb.Label(verification_frame, text=f"Rematch the Transaction to Invoice?", font=('Helvetica-bold', 11))
  rematch_prompt.pack(pady=10)

  verification_buttons_frame = tkb.Frame(verification_frame)
  verification_buttons_frame.columnconfigure(0, weight=1)
  verification_buttons_frame.columnconfigure(1, weight=1)

  verification_buttons_frame.pack(pady=20)

  verify_button = tkb.Button(verification_buttons_frame, text="Rematch", command=lambda: verifyRematch())
  verify_button.grid(row=0, column=0, padx=40)

  error_button = tkb.Button(verification_buttons_frame, text="Ignore", command=lambda: ignoreRematch())
  error_button.grid(row=0, column=1, padx=40)

  def verifyRematch():
      rematchVerifiedBool.set(True)
      promptWindow.destroy()

  def ignoreRematch():
      rematchVerifiedBool.set(False)
      promptWindow.destroy()
      
  promptWindow.wait_window()

