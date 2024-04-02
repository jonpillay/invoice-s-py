from tkinter import *
from ttkbootstrap.constants import *
import ttkbootstrap as tkb

root = tkb.Window(themename="solar")

root.title("InvoicesPY")
root.geometry('600x400')

test_label = tkb.Label(text="We are live!")
test_label.pack(pady=50)

root.mainloop()