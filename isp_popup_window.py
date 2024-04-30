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
      print('running')
      newCustomerReturn.set(add_customer_entry.get())
      promptWindow.destroy()

    def updateNewAliasVar():
      print('runningAlias')
      newAliasReturn.set(add_alias_dropdown.get())
      promptWindow.destroy()

    promptWindow.wait_window(main_frame)