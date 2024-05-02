import re

from isp_db_helpers import getCustomerAliases, getCustomerID

def constructCustomerAliasesDict(cur, namesIDsTups):
  
  aliasesDict = {}

  for id, name in namesIDsTups:

    customerAliases = getCustomerAliases(cur, id)

    aliasesDict[name] = customerAliases

  return aliasesDict

def constructCustomerIDict(cur, aliasesDict):

  customerIDict = {}

  for customerName in aliasesDict:
    customerID = getCustomerID(cur, customerName)

    namesList = aliasesDict[customerName]

    namesList.append(customerName)

    customerIDict[customerID] = namesList

  return customerIDict

def prepInvoiceUploadList(invoiceList, customerAliasIDict):

  invoiceUploadTups = []

  for invoice in invoiceList:

    customerName = invoice.issued_to.upper().strip()

    if re.search("CASH", customerName):
      for id in customerAliasIDict:
        print("here")
        if "CASH" in customerAliasIDict[id]:
          invoice.customer_id = id
          print("this" + str(invoice.customer_id))
          break

    for id in customerAliasIDict:
      if invoice.issued_to.upper().strip() in customerAliasIDict[id]:
        invoice.customer_id = id
    print("this" + str(invoice.customer_id))