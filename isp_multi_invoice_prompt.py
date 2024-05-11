import tkinter as tk
import ttkbootstrap as tkb

from isp_treeviews import renderPromptInvoices, renderPromptMulitTransactions

def openMultiInvoicePrompt(root, transaction, invoiceList):

    promptWindow = tk.Toplevel(root)
    promptWindow.title('Invoices Match?')
    promptWindow.geometry('1000x600')

    def updateWindowHeight():
      
      height = sum([widget.winfo_height() for widget in promptWindow.winfo_children()])

      print(f'This is the height {height}')

      promptWindow.geometry(f'1000x{height}')

    title_label = tkb.Label(promptWindow, text=f"Multiple Invoice Transaction", background='red')
    title_label.pack(side='top')

    main_frame = tkb.Frame(promptWindow)
    main_frame.pack(side='top', expand=True)

    prompt_frame = tkb.Frame(main_frame)
    prompt_frame.pack()

    prompt_label = tkb.Label(prompt_frame, text=f"Multiple Invoice Transaction from {transaction[3]} for invoices {transaction[0][0]} to {transaction[0][1]} total paid {transaction[1]}")
    prompt_label.pack()

    og_string_label = tkb.Label(prompt_frame, text=f"{transaction[5]}")
    og_string_label.pack()

    renderPromptMulitTransactions(main_frame, [transaction])

    renderPromptInvoices(main_frame, invoiceList)

    promptWindow.update()

    updateWindowHeight()

    promptWindow.wait_window()