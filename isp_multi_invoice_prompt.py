import tkinter as tk
import ttkbootstrap as tkb

from isp_treeviews import renderPromptInvoices, renderPromptMulitTransactions

def openMultiInvoicePrompt(root, transaction, invoiceList):

    promptWindow = tk.Toplevel(root)
    promptWindow.title('Invoices Match?')
    promptWindow.geometry('800x600')

    def updateWindowHeight():
      
      height = sum([widget.winfo_height() for widget in promptWindow.winfo_children()])

      print(f'This is the height {height}')

      promptWindow.geometry(f'800x{height}')

    # promptWindow.rowconfigure(0, weight=1)
    # promptWindow.rowconfigure(1, weight=40)
    # promptWindow.columnconfigure(0, weight=1)

    title_label = tkb.Label(promptWindow, text=f"Multiple Invoice Transaction", background='red')
    # title_label.grid(row=0, column=0, sticky='nesw')
    title_label.pack(side='top')

    main_frame = tkb.Frame(promptWindow)
    # main_frame.grid(row=1, column=0, sticky='nesw')
    main_frame.pack(side='top', expand=True)

    main_frame.rowconfigure(0, weight=1)
    main_frame.rowconfigure(1, weight=1)
    main_frame.columnconfigure(0, weight=1)

    renderPromptMulitTransactions(main_frame, [transaction], 0, 0)

    renderPromptInvoices(main_frame, invoiceList, 1, 0)

    promptWindow.update()

    updateWindowHeight()

    promptWindow.wait_window()