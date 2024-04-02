from tkinter import *
from ttkbootstrap.constants import *
import ttkbootstrap as tkb

root = tkb.Window(themename="solar")

root.title("InvoicesPY")
root.geometry('1000x800')

test_label = tkb.Label(root, text="We are live!")
test_label.grid(column=2, row=1)

test_label2 = tkb.Label(root, text="here though", bootstyle='danger')
test_label2.grid(column=1, row=0)

test_label3 = tkb.Label(root, text="here next", bootstyle='danger')
test_label3.grid(column=1, row=1)

root.mainloop()