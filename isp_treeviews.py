from tkinter import ttk

def renderPromptInvoices(parentWindow, invoiceList, gridRow, gridColumn):

  invoiceTable = ttk.Treeview(parentWindow, columns = ('invoice_num', 'issued_to', 'amount', 'date_issued', 'notes'), show='headings', height=len(invoiceList))

  invoiceTable.heading('invoice_num', text="Invoice Num")
  invoiceTable.heading('issued_to', text='Customer')
  invoiceTable.heading('amount', text='Amount (£)')
  invoiceTable.heading('date_issued', text='Issued On')
  invoiceTable.heading('notes', text='Notes')

  invoiceTable.pack()

  for i in range(len(invoiceList)):
    invoiceTable.insert(parent='', index=i, values=(invoiceList[i].invoice_num, invoiceList[i].issued_to, invoiceList[i].amount, invoiceList[i].date_issued, invoiceList[i].error_notes))

def renderPromptMulitTransactions(parentWindow, transactionList, gridRow, gridColumn):

  multiTransactionTable = ttk.Treeview(parentWindow, columns=('low_invoice', 'high_invoice', 'amount', 'paid_on', 'paid_by', 'payment_method', 'og_string'), show='headings', height=len(transactionList))

  multiTransactionTable.heading('low_invoice', text='From Invoice')
  multiTransactionTable.heading('high_invoice', text='To Invoice')
  multiTransactionTable.heading('amount', text='Paid (£)')
  multiTransactionTable.heading('paid_on', text='Date Paid')
  multiTransactionTable.heading('paid_by', text='Paid By')
  multiTransactionTable.heading('payment_method', text='Method')
  multiTransactionTable.heading('og_string', text='Description')

  multiTransactionTable.pack()

  for i in range(len(transactionList)):

    multiTransactionTable.insert(parent='', index=i, values=(transactionList[i][0][0], transactionList[i][0][1], transactionList[i][1], transactionList[i][2], transactionList[i][3], transactionList[i][4], transactionList[i][5]))


