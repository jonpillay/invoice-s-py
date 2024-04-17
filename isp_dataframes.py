import datetime
from dataclasses import dataclass

"""Class for rednering backend information to the frontend"""

@dataclass
class Transaction:
  invoice_num: int
  amount: float
  paid_on: datetime.date
  paid_by: str
  payment_method: str
  og_string: str
  invoice_id: int = None

@dataclass
class Invoice:
  invoice_num: int
  amount: float
  date_issued: datetime.date
  issued_to: str
  invoice_id: int = None

# Transaction = NamedTuple('Transaction', 'invoice_num, amount, paid_on, company_name, payment_method, og_string, invoice_id')