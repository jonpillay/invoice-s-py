import tkinter as tk
import ttkbootstrap as tkb

def promptUserNewCustomer(root, customer, dbCustomers):
  promptWindow = tk.Toplevel(root)
  promptWindow.title('New Customer?')
  promptWindow.geometry('800x600')

  promptWindow.rowconfigure(0, weight=1)
  promptWindow.rowconfigure(1, weight=20)
  promptWindow.columnconfigure(0, weight=1)

  title_label = tkb.Label(promptWindow, text="InvoicesPY for...", background='red')
  title_label.grid(row=0, column=0, sticky='nesw')

  main_frame = tkb.Frame(promptWindow)
  main_frame.grid(row=1, column=0, sticky='nesw')

  add_customer_frame = tkb.Frame(main_frame)
  add_customer_frame.grid(row=0, column=0, sticky='nesw')
  add_customer_frame_label = tkb.Label(add_customer_frame, text="Add Customer", background='red')
  add_customer_frame_label.pack()

  add_alias_frame = tkb.Frame(main_frame)
  add_alias_frame.grid(row=1, column=0, sticky='nesw')
  add_alias_frame_label = tkb.Label(add_alias_frame, text="Add Alias", background='blue')
  add_alias_frame_label.pack()
