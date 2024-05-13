import datetime
from dataclasses import dataclass, field

# print(dataclasses.__version__)

"""Class for rendering backend information to the frontend"""

@dataclass
class Transaction:
  invoice_num: int
  amount: float
  paid_on: datetime.date
  paid_by: str
  payment_method: str
  og_string: str
  high_invoice: int = None
  invoice_id: int = None
  customer_id: int = None
  parent_trans: int = None

  def as_tuple(self):
    return tuple(getattr(self, field.name) for field in self.__dataclass_fields__ if getattr(self, field) is not None)

@dataclass
class Invoice:
  invoice_num: int
  amount: float
  date_issued: datetime.date
  issued_to: str
  error_notes: str = None
  error_flagged: int = None
  invoice_id: int = None
  customer_id: int = None

  def as_tuple(self):
    return tuple(getattr(self, field.name) for field in self.__dataclass_fields__ if getattr(self, field) is not None)

@dataclass
class Customer:
  customer_name: str
  customer_aliases: list[str] = field(default_factory=list)

# Transaction = NamedTuple('Transaction', 'invoice_num, amount, paid_on, company_name, payment_method, og_string, invoice_id')