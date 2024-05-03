from isp_dataframes import Transaction, Invoice

def verifyTransactionDetails(transaction, invoice):

  invoice = invoice[0]

  if invoice[4] != transaction[3]:
    return f"Name Mismatch {transaction[3]} to {invoice[3]}"
  elif invoice[2] != transaction[1]:
    return invoice[2] - transaction[1]
  else:
    return True
  
def verifyAlias(transaction, invoice):

  invoiceIDummy = None
  og_string = " ".join(transaction[5])

  frontendTransaction = Transaction(transaction[0][0], transaction[1], transaction[2], transaction[3], transaction[4], og_string, invoiceIDummy)
  frontendInvoice = Invoice(invoice[0], invoice[1], invoice[2], invoice[3], invoice[4])