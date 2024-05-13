import tkinter as tk
import ttkbootstrap as tkb

from isp_treeviews import renderPromptInvoices, renderPromptMulitTransactions

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
       checkedBool.set(False)
       verifyBool.set(False)
       promptWindow.destroy()

    promptWindow.wait_window()