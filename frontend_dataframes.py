from typing import NamedTuple
import datetime

from dataclasses import dataclass

"""Class for rednering backend information to the frontend"""

@dataclass
class FrontendTransaction:
  invoice_num: int
  amount: float
  paid_on: datetime.date
  paid_by: str
  payment_method: str
  og_string: str
  invoice_id: int = None

@dataclass
class FrontendInvoice:
  invoice_id: int
  invoice_num: int
  amount: float
  date_issued: datetime.date
  issued_to: str


# Data frames for the frontend. Better for code redability for frontend functions.
# Decided to use NamedTuple over dataclasses due to immutability (although this can be acheived with dataclasses.)
# Also faster access.

# Transaction = NamedTuple('Transaction', 'invoice_num, amount, paid_on, company_name, payment_method, og_string, invoice_id')

# Invoice = NamedTuple('Invoice, invoice_num, amount, date_issued, company_name')