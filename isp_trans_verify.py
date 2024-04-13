def verifyTransactionDetails(transaction, invoice):

  invoice = invoice[0]

  if invoice[2] != transaction[1]:
    return invoice[2] - transaction[1]
  elif invoice[3] != transaction[3]:
    return f"Name Mismatch {transaction[3]} to {invoice[3]}"
  else:
    return True