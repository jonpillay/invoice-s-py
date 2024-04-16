from typing import NamedTuple

# Data frames for the frontend. Better for code redability for frontend functions.
# Decided to use NamedTuple over dataclasses due to immutability (although this can be acheived with dataclasses.)
# Also faster access.

Transaction = NamedTuple('Transaction', 'invoice_num, amount, paid_on, company_name, payment_method, og_string, invoice_id')

# Invoice = NamedTuple('Invoice, invoice_num, amount, date_issued, company_name')