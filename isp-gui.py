from tkinter import *
from ttkbootstrap.constants import *
import ttkbootstrap as tkb

root = tkb.Window(themename="solar")

root.title("InvoicesPY")
root.geometry('1400x1000')

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=20)
root.columnconfigure(0, weight=1)

title_label = tkb.Label(root, text="InvoicesPY for...", background='red')
title_label.grid(row=0, column=0, sticky='nesw')

controls_frame = tkb.Frame(root)
controls_frame.grid(row=1, column=0)

root.mainloop()