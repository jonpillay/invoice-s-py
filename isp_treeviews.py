from tkinter import ttk

def renderPromptInvoices(parentWindow, invoiceList, gridRow, gridColomn):

  invoiceTable = ttk.Treeview(parentWindow, columns = ('invoice_num', 'issued_to', 'amount', 'date_issued', 'notes'), show='headings')

  invoiceTable.heading('invoice_num', text="Invoice Num")
  invoiceTable.heading('issued_to', text='Customer')
  invoiceTable.heading('amount', text='Amount (£)')
  invoiceTable.heading('date_issued', text='Issued On')
  invoiceTable.heading('notes', text='Notes')

  invoiceTable.grid(row=gridRow, column=gridColomn)

  for i in range(len(invoiceList)):
    invoiceTable.insert(parent='', index=0, values=(invoiceList[i].invoice_num, invoiceList[i].issued_to, invoiceList[i].amount, invoiceList[i].date_issued, invoiceList[i].error_notes))