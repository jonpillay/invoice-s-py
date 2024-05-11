from tkinter import ttk

def renderPromptInvoices(parentWindow, invoiceList):

  invoiceTable = ttk.Treeview(parentWindow, show='headings', height=len(invoiceList))

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

  invoiceTable.pack()

  style = ttk.Style(invoiceTable)
  style.theme_use('alt')
  style.configure("Treeview",
    rowheight=30
  )

def renderPromptMulitTransactions(parentWindow, transactionList):

  multiTransactionTable = ttk.Treeview(parentWindow, columns=('low_invoice', 'high_invoice', 'paid_by', 'amount', 'paid_on', 'payment_method'), show='headings', height=len(transactionList))


  multiTransactionTable.column('low_invoice', width=100, anchor='center')
  multiTransactionTable.heading('low_invoice', text='From #')

  multiTransactionTable.column('high_invoice', width=100, anchor='center')
  multiTransactionTable.heading('high_invoice', text='To #')
  
  multiTransactionTable.column('paid_by', width=260, anchor='center')
  multiTransactionTable.heading('paid_by', text='Paid By')
  
  multiTransactionTable.column('amount', width=120, anchor='center')
  multiTransactionTable.heading('amount', text='Paid (£)')

  multiTransactionTable.column('paid_on', width=110, anchor='center')
  multiTransactionTable.heading('paid_on', text='Date Paid')

  multiTransactionTable.column('payment_method', width=90, anchor='center')
  multiTransactionTable.heading('payment_method', text='Method')

  style = ttk.Style(multiTransactionTable)
  style.theme_use('alt')
  style.configure("Treeview",
    rowheight=30
  )

  multiTransactionTable.pack()

  for i in range(len(transactionList)):

    multiTransactionTable.insert(parent='', index=i, values=(transactionList[i][0][0], transactionList[i][0][1], transactionList[i][3], transactionList[i][1], transactionList[i][2], transactionList[i][4]))


