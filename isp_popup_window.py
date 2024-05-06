import tkinter as tk
import ttkbootstrap as tkb

def openNewCustomerPrompt(root, customer, dbCustomers, newCustomerReturn, newAliasReturn):
    
    customerNames = []

    promptWindow = tk.Toplevel(root)
    promptWindow.title('New Customer?')
    promptWindow.geometry('800x600')

    promptWindow.rowconfigure(0, weight=1)
    promptWindow.rowconfigure(1, weight=20)
    promptWindow.columnconfigure(0, weight=1)

    title_label = tkb.Label(promptWindow, text=f"Add new customer '{customer}'?", background='red')
    title_label.grid(row=0, column=0, sticky='nesw')

    main_frame = tkb.Frame(promptWindow)
    main_frame.grid(row=1, column=0, sticky='nesw')

    main_frame.rowconfigure(0, weight=1)
    main_frame.rowconfigure(1, weight=1)

    main_frame.columnconfigure(1, weight=1)

    add_customer_frame = tkb.Frame(main_frame)
    add_customer_frame.grid(row=0, column=0, sticky='nesw')

    add_customer_frame_label = tkb.Label(add_customer_frame, text="Add Customer", background='red')
    add_customer_frame_label.grid(row=1, column=1, sticky='ew')

    add_customer_entry = tkb.Entry(add_customer_frame, textvariable=newCustomerReturn)
    newCustomerReturn.set(customer)
    add_customer_entry.grid(row=1, column=0)

    add_customer_button = tkb.Button(add_customer_frame, text='Submit', command= lambda: updateNewCustomerVar())
    add_customer_button.grid(row=2, column=0)

    add_alias_frame = tkb.Frame(main_frame)
    add_alias_frame.grid(row=1, column=0, sticky='nesw')

    add_alias_frame_label = tkb.Label(add_alias_frame, text="Add Alias", background='blue')
    add_alias_frame_label.grid(row=0, column=0)

    for id, name in dbCustomers:
      customerNames.append(name)

    add_alias_dropdown = tkb.Combobox(add_alias_frame, values=customerNames)
    add_alias_dropdown.grid(row=1, column=0)

    add_alias_button = tkb.Button(add_alias_frame, text='Submit', command= lambda: updateNewAliasVar())
    add_alias_button.grid(row=2, column=0)

    def updateNewCustomerVar():
      newAliasReturn.set("")
      print('running')
      newCustomerReturn.set(add_customer_entry.get())
      promptWindow.destroy()

    def updateNewAliasVar():
      newCustomerReturn.set("")
      print('runningAlias')
      newAliasReturn.set(add_alias_dropdown.get())
      promptWindow.destroy()

    promptWindow.wait_window(main_frame)

def openTransactionAliasPrompt(root, invoice, transaction, aliasBool, rejectedBool):
    
    promptWindow = tk.Toplevel(root)
    promptWindow.title('New Customer?')
    promptWindow.geometry('800x600')

    promptWindow.rowconfigure(0, weight=1)
    promptWindow.rowconfigure(1, weight=20)
    promptWindow.columnconfigure(0, weight=1)

    title_label = tkb.Label(promptWindow, text=f"Add new alias for {invoice.issued_to}?", background='red')
    title_label.grid(row=0, column=0, sticky='nesw')

    main_frame = tkb.Frame(promptWindow)
    main_frame.grid(row=1, column=0, sticky='nesw')

    main_frame.rowconfigure(0, weight=1)
    main_frame.rowconfigure(1, weight=1)
    main_frame.rowconfigure(2, weight=1)

    main_frame.columnconfigure(0, weight=1)

    detail_frame = tkb.Frame(main_frame)
    detail_frame.rowconfigure(0, weight=1)
    detail_frame.rowconfigure(1, weight=2)
    detail_frame.rowconfigure(3, weight=1)

    detail_frame.grid(row=0, column=0, sticky='nesw')

    transaction_deatails_label = tkb.Label(detail_frame, text=f"{transaction.paid_by}")
    transaction_deatails_label.grid(row=0, column=0)

    connector_label = tkb.Label(detail_frame, text="FOR")
    connector_label.grid(row=1, column=0)

    invoice_details_label = tkb.Label(detail_frame, text=f"{invoice.issued_to}")
    invoice_details_label.grid(row=2, column=0)

    prompt_frame = tkb.Frame(main_frame)
    prompt_frame.rowconfigure(0, weight=1)
    prompt_frame.columnconfigure(0, weight=1)
    prompt_frame.grid(row=1, column=0)

    prompt_label = tkb.Label(prompt_frame, text=f"Would you like to make {transaction.paid_by} an alias for {invoice.issued_to}?")
    prompt_label.grid(row=0, column=0)

    decision_buttons_frame = tkb.Frame(main_frame)
    decision_buttons_frame.grid(row=2, column=0)
    decision_buttons_frame.rowconfigure(0, weight=1)
    decision_buttons_frame.columnconfigure(0, weight=1)
    decision_buttons_frame.columnconfigure(1, weight=1)

    verify_alias_frame = tkb.Frame(decision_buttons_frame)
    verify_alias_frame.grid(row=0, column=0)

    verify_alias_button = tkb.Button(verify_alias_frame, text="Verify", command=lambda: verifyAlias())
    verify_alias_button.grid(row=0, column=0)

    reject_alias_frame = tkb.Frame(decision_buttons_frame)
    reject_alias_frame.grid(row=0, column=1)

    reject_alias_button = tkb.Button(reject_alias_frame, text="Reject", command=lambda: rejectAlias())
    reject_alias_button.grid(row=0, column=0)

    def verifyAlias():
       aliasBool.set(True)
       promptWindow.destroy()

    def rejectAlias():
       rejectedBool.set(True)
       promptWindow.destroy()

    promptWindow.wait_window(main_frame)

def openTransactionPaymentErrorPrompt(root, invoice, transaction):
   
   # Should return a list of verified Transactions ready to be uploaded onto the DB.
   # Also return of unverified Transactions and Invoices to be reported on.
   # Invoices may need extra errors bool, so they can have a Transaction assotiated, but also have an error flag.
   # Means they can also be errorless even if the payment amount is still an error (through user veryfication.)

    promptWindow = tk.Toplevel(root)
    promptWindow.title('Payment Error')
    promptWindow.geometry('800x600')

    promptWindow.rowconfigure(0, weight=1)
    promptWindow.rowconfigure(1, weight=20)
    promptWindow.columnconfigure(0, weight=1)

    title_label = tkb.Label(promptWindow, text=f"Payment Error for {invoice.issued_to}?", background='red')
    title_label.grid(row=0, column=0, sticky='nesw')

    main_frame = tkb.Frame(promptWindow)
    main_frame.grid(row=1, column=0, sticky='nesw')

    main_frame.rowconfigure(0, weight=1)
    main_frame.rowconfigure(1, weight=1)
    main_frame.rowconfigure(2, weight=1)
    main_frame.rowconfigure(3, weight=1)
    main_frame.rowconfigure(4, weight=1)

    main_frame.columnconfigure(0, weight=1)

    # customer details

    customer_details_frame = tkb.Frame(main_frame)
    customer_details_frame.grid(row=0, column=0)

    customer_details_frame.columnconfigure(0, weight=1)
    customer_details_frame.columnconfigure(1, weight=1)
    customer_details_frame.columnconfigure(2, weight=1)

    customer_details_trans_label = tkb.Label(customer_details_frame, text=f"{transaction.paid_by}")
    customer_details_trans_label.grid(row=0, column=0)

    # probably going to need a spacer, will test

    customer_details_invoice_label = tkb.Label(customer_details_frame, text=f"{invoice.issued_to}")
    customer_details_invoice_label.grid(row=0, column=2)

    # arrow frame

    arrow_frame = tkb.Frame(main_frame)
    arrow_frame.grid(row=1, column=0)

    arrow_frame.columnconfigure(0, weight=1)
    arrow_frame.columnconfigure(1, weight=1)
    arrow_frame.columnconfigure(2, weight=1)

    arrow_frame.rowconfigure(0, weight=1)

    arrow_frame_label = tkb.Label(arrow_frame, text=">")
    arrow_frame_label.grid(row=0, column=1)

    # Payment Details

    payment_details_frame = tkb.Frame(main_frame)
    payment_details_frame.grid(row=2, column=0)

    payment_details_frame.columnconfigure(0, weight=1)
    payment_details_frame.columnconfigure(1, weight=1)
    payment_details_frame.columnconfigure(2, weight=1)
  
    payment_details_frame.rowconfigure(0, weight=1)

    payment_details_invoice_label = tkb.Label(payment_details_frame, text=f"{invoice.amount}")
    payment_details_invoice_label.grid(row=0, column=0)

    payment_details_transaction_label = tkb.Label(payment_details_frame, text=f"{invoice.amount}")
    payment_details_transaction_label.grid(row=0, column=2)

    # add note

    add_note_frame = tkb.Frame(main_frame)
    add_note_frame.grid(row=3, column=0)

    add_note_frame.rowconfigure(0, weight=1)
    add_note_frame.columnconfigure(0, weight=1)

    add_note_entry = tkb.Text(add_note_frame, width=30, height=5)
    add_note_entry.grid(row=0, column=0)

    # transaction error verification buttons

    decision_buttons_frame = tkb.Frame(main_frame)
    decision_buttons_frame.grid(row=4, column=0)
    decision_buttons_frame.rowconfigure(0, weight=1)
    decision_buttons_frame.columnconfigure(0, weight=1)
    decision_buttons_frame.columnconfigure(1, weight=1)
    decision_buttons_frame.columnconfigure(2, weight=1)

    verify_cash_frame = tkb.Frame(decision_buttons_frame)
    verify_cash_frame.grid(row=0, column=0)

    verify_cash_button = tkb.Button(verify_cash_frame, text="Verify With Cash")
    verify_cash_button.grid(row=0, column=0)

    verify_BACS_frame = tkb.Frame(decision_buttons_frame)
    verify_BACS_frame.grid(row=0, column=1)

    verify_BACS_button = tkb.Button(verify_BACS_frame, text="Verify With Bacs")
    verify_BACS_button.grid(row=0, column=0)

    raise_error_frame = tkb.Frame(decision_buttons_frame)
    raise_error_frame.grid(row=0, column=2)

    raise_error_button = tkb.Button(raise_error_frame, text="Raise Error")
    raise_error_button.grid(row=0, column=0)