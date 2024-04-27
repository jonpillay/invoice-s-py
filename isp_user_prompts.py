import tkinter as tk
import ttkbootstrap as tkb

from isp_popup_window import openNewCustomerPrompt

def promptUserNewCustomer(root, customer, dbCustomers, response):
  openNewCustomerPrompt(root, customer, dbCustomers, response)
