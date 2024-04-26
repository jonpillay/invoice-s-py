from isp_db_helpers import getCustomerNamesIDs, getCustomerAliases

def sortCustmoerInvoiceLists(invoiceList, customerList):
  pass

def constructCustomerAliasesDict(cur, namesIDsTups):
  
  aliasesDict = {}

  for id, name in namesIDsTups:

    customerAliases = getCustomerAliases(cur, id)

    aliasesDict[name] = customerAliases

  return aliasesDict