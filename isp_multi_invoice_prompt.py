import tkinter as tk
import ttkbootstrap as tkb

from isp_treeviews import renderPromptInvoices

def openMultiInvoicePrompt(root, transaction, invoiceList):

    promptWindow = tk.Toplevel(root)
    promptWindow.title('Invoices Match?')
    promptWindow.geometry('800x600')

    promptWindow.rowconfigure(0, weight=1)
    promptWindow.rowconfigure(1, weight=20)
    promptWindow.columnconfigure(0, weight=1)

    title_label = tkb.Label(promptWindow, text=f"Multiple Invoice Transaction", background='red')
    title_label.grid(row=0, column=0, sticky='nesw')

    main_frame = tkb.Frame(promptWindow)
    main_frame.grid(row=1, column=0, sticky='nesw')

    main_frame.rowconfigure(0, weight=1)
    main_frame.rowconfigure(1, weight=1)
    main_frame.columnconfigure(0, weight=1)

    renderPromptInvoices(promptWindow, invoiceList, 0, 0)

    promptWindow.wait_window(main_frame)