from tkinter import *
from ttkbootstrap.constants import *
import ttkbootstrap as tkb

from isp_csv_helpers import *
from isp_db_helpers import *

checkDBStatus()

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

main_frame.rowconfigure(0, weight=10)
main_frame.rowconfigure(1, weight=19)
main_frame.columnconfigure(0, weight=1)

controls_frame = tkb.Frame(main_frame)
results_frame = tkb.Frame(main_frame)

controls_frame.grid(row=0, column=0, sticky='nesw')
results_frame.grid(row=1, column=0, sticky='nesw')

controls_frame.columnconfigure(0, weight=6)
controls_frame.columnconfigure(1, weight=3)
controls_frame.rowconfigure(0, weight=1)

results_frame.rowconfigure(0, weight=1)
results_frame.rowconfigure(1, weight=10)
results_frame.columnconfigure(0, weight=1)

# CSV Upload Widget
upload_frame = tkb.Frame(controls_frame)
upload_frame.columnconfigure(0, weight=1)
upload_frame.columnconfigure(1, weight=1)
upload_frame.grid(row=0, column=0, sticky='nesw')
upload_frame.rowconfigure(0, weight=1)


invoice_upload = tkb.Button(upload_frame, text='Invoice Upload', bootstyle='primary', command=getCSVfile)
invoice_upload.grid(row=0, column=0)

statement_upload = tkb.Button(upload_frame, text='Statement Upload', bootstyle='primary')
statement_upload.grid(row=0, column=1)

# Report Gen Widget Panel. Report Gen By Date Range and Customer. Gen both OnScreen and PDF.
report_gen_dummy = tkb.Label(controls_frame, text='Report Gen Controls Dummy', background='green')
report_gen_dummy.grid(row=0, column=1, sticky='nesw')

# Tabs for switching between different portions of results (paid, outstanding, possible errors)
results_dummy_tabs = tkb.Label(results_frame, text='Results Dummy Tabs', background='#8B8000')

# Query Result Printed to console. Each invoice is printed with related payment details- 
# except in the case of payments without invoice, which are displayed alone (and marked)
results_dummy_text = tkb.Label(results_frame, text='Results Dummy Text', background='orange')

results_dummy_tabs.grid(row=0, column=0, sticky='nesw')
results_dummy_text.grid(row=1, column=0, sticky='nesw')

root.mainloop()