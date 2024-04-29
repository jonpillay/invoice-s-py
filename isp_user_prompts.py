import tkinter as tk
import ttkbootstrap as tkb

from isp_popup_window import openNewCustomerPrompt

def promptUserNewCustomer(root, customer, dbCustomers, nameReturn, customerIDReturn):
  openNewCustomerPrompt(root, customer, dbCustomers, nameReturn, customerIDReturn)
