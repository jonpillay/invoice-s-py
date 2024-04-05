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

main_frame = tkb.Frame(root)
main_frame.grid(row=1, column=0, sticky='nesw')

main_frame.rowconfigure(0, weight=5)
main_frame.rowconfigure(1, weight=19)
main_frame.columnconfigure(0, weight=1)

controls_frame = tkb.Frame(main_frame)
results_frame = tkb.Frame(main_frame)

controls_frame.grid(row=0, column=0, sticky='nesw')
results_frame.grid(row=1, column=0, sticky='nesw')

controls_frame.columnconfigure(0, weight=1)
controls_frame.columnconfigure(1, weight=1)
controls_frame.rowconfigure(0, weight=1)

results_frame.rowconfigure(0, weight=1)
results_frame.rowconfigure(1, weight=10)
results_frame.columnconfigure(0, weight=1)

controls_dummy1 = tkb.Label(controls_frame, text='Controls Dummy', background='black')
controls_dummy2 = tkb.Label(controls_frame, text='Controls Dummy2', background='orange')

controls_dummy1.grid(row=0, column=0, sticky='nesw')
controls_dummy2.grid(row=0, column=1, sticky='nesw')

results_dummy_tabs = tkb.Label(results_frame, text='Results Dummy Tabs', background='grey')
results_dummy_text = tkb.Label(results_frame, text='Results Dummy Text', background='green')

results_dummy_tabs.grid(row=0, column=0, sticky='nesw')
results_dummy_text.grid(row=1, column=0, sticky='nesw')

root.mainloop()