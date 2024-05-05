from isp_dataframes import Transaction, Invoice
from isp_db_helpers import getCustomerAliases

def verifyTransactionDetails(transaction, invoice, cur):

  customerAliases = getCustomerAliases(cur, invoice.customer_id)

  if invoice.issued_to != transaction.paid_by or invoice.issued_to not in customerAliases:
    return f"Name Mismatch {transaction.paid_by} to {invoice.issued_to}"
  elif invoice.amount != transaction.amount:
    return invoice.amount - transaction.amount
  else:
    return True
  
def verifyAlias(transaction, invoice):

  invoiceIDummy = None
  og_string = " ".join(transaction[5])

  frontendTransaction = Transaction(transaction[0][0], transaction[1], transaction[2], transaction[3], transaction[4], og_string, invoiceIDummy)
  frontendInvoice = Invoice(invoice[0], invoice[1], invoice[2], invoice[3], invoice[4])

def resolveNameMismatches(matchNameErrors):

  errorCount = len(matchNameErrors)

  unMatchable = []
  nameResolved = []

  while len(nameResolved) + len(unMatchable) < errorCount:
    for error in matchNameErrors:
      pass
      # Prompt user if the name mismatch is an error

      # Prompt should set some TKVars

      # If alias is found, should add alias to DB and rerun check on all elements in matchNameErrors list
      # First building a new aliases dict with result and resolving for that.

      # If the alias is not a match then the error pair should be put into unMatchable