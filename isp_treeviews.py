from tkinter import ttk

def renderSimplePromptInvoices(parentWindow, invoiceList):

  invoiceTable = ttk.Treeview(parentWindow, show='headings', height=len(invoiceList))

  invoiceTable['columns'] = ('invoice_num', 'issued_to', 'amount', 'date_issued')

  invoiceTable.column('invoice_num', width=110, anchor='center')
  invoiceTable.heading('invoice_num', text="Invoice #")

  invoiceTable.column('issued_to', width=270, anchor='center')
  invoiceTable.heading('issued_to', text='Customer')
  
  invoiceTable.column('amount', width=110, anchor='center')
  invoiceTable.heading('amount', text='Amount (£)')
  
  invoiceTable.column('date_issued', width=110, anchor='center')
  invoiceTable.heading('date_issued', text='Issued On')


  for i in range(len(invoiceList)):

    formattedDate = invoiceList[i].date_issued.strftime("%d/%m/%Y")

    invoiceTable.insert(parent='', index=i, values=(invoiceList[i].invoice_num, invoiceList[i].issued_to, invoiceList[i].amount, formattedDate))

  invoiceTable.pack()

  style = ttk.Style(invoiceTable)
  style.theme_use('alt')
  style.configure("Treeview",
    rowheight=30
  )

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

  invoiceTable.pack(padx=10)

  style = ttk.Style(invoiceTable)
  style.theme_use('alt')
  style.configure("Treeview",
    rowheight=30
  )

def renderPromptTransactions(parentWindow, transactionList):

  transactionTable = ttk.Treeview(parentWindow, columns=('low_invoice', 'paid_by', 'amount', 'paid_on', 'payment_method'), show='headings', height=len(transactionList))

  transactionTable.column('low_invoice', width=100, anchor='center')
  transactionTable.heading('low_invoice', text='From #')
  
  transactionTable.column('paid_by', width=260, anchor='center')
  transactionTable.heading('paid_by', text='Paid By')
  
  transactionTable.column('amount', width=120, anchor='center')
  transactionTable.heading('amount', text='Paid (£)')

  transactionTable.column('paid_on', width=110, anchor='center')
  transactionTable.heading('paid_on', text='Date Paid')

  transactionTable.column('payment_method', width=90, anchor='center')
  transactionTable.heading('payment_method', text='Method')

  style = ttk.Style(transactionTable)
  style.theme_use('alt')
  style.configure("Treeview",
    rowheight=30
  )

  transactionTable.pack(pady=10)

  for i in range(len(transactionList)):

    formattedDate = transactionList[i].paid_on.strftime("%d/%m/%Y")

    transactionTable.insert(parent='', index=i, values=(transactionList[i].invoice_num, transactionList[i].paid_by, transactionList[i].amount, formattedDate, transactionList[i].payment_method))



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

  multiTransactionTable.pack(pady=20)

  for i in range(len(transactionList)):

    formattedDate = transactionList[i].paid_on.strftime("%d/%m/%Y")

    multiTransactionTable.insert(parent='', index=i, values=(transactionList[i].invoice_num, transactionList[i].high_invoice, transactionList[i].paid_by, transactionList[i].amount, formattedDate, transactionList[i].payment_method))