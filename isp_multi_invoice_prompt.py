import tkinter as tk
import ttkbootstrap as tkb

from isp_treeviews import renderPromptInvoices, renderPromptMulitTransactions

def openMultiInvoicePrompt(root, transaction, invoiceList):

    promptWindow = tk.Toplevel(root)
    promptWindow.title('Invoices Match?')
    promptWindow.geometry('1100x600')

    def updateWindowHeight():
      
      height = sum([widget.winfo_height() for widget in promptWindow.winfo_children()])

      print(f'This is the height {height}')

      promptWindow.geometry(f'1000x{height+100}')

    title_label = tkb.Label(promptWindow, text=f"Multiple Invoice Transaction", background='red')
    title_label.pack(side='top')

    main_frame = tkb.Frame(promptWindow)
    main_frame.pack(side='top', expand=True)

    prompt_frame = tkb.Frame(main_frame)
    prompt_frame.pack()

    prompt_label = tkb.Label(prompt_frame, text=f"Multiple Invoice Transaction from {transaction[3]} for invoices {transaction[0][0]} to {transaction[0][1]}\n Total Paid £{transaction[1]}", font=('Helvetica-bold', 11), justify='center')
    prompt_label.pack(pady=10)

    og_string_label = tkb.Label(prompt_frame, wraplength=900, text=f"\"{transaction[5]}\"")
    og_string_label.pack(pady=10)
    og_string_label.configure(anchor='center', justify='center')

    renderPromptMulitTransactions(main_frame, [transaction])

    renderPromptInvoices(main_frame, invoiceList)

    verification_frame = tkb.Frame(main_frame)
    verification_frame.pack()

    total_invoiced = round(sum([invoice.amount for invoice in invoiceList]), 2)

    print(total_invoiced)

    totals_label = tkb.Label(verification_frame, text=f"Total Invoiced = {total_invoiced} > Total Paid = {transaction[1]}", font=('Helvetica-bold', 11))
    totals_label.pack(pady=10)

    promptWindow.update()

    updateWindowHeight()

    promptWindow.wait_window()