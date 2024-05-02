from isp_db_helpers import getCustomerAliases, getCustomerID

def constructCustomerAliasesDict(cur, namesIDsTups):
  
  aliasesDict = {}

  for id, name in namesIDsTups:

    customerAliases = getCustomerAliases(cur, id)

    aliasesDict[name] = customerAliases

  return aliasesDict

def constructCustomerIDict(cur, aliasesDict):

  customerIDict = {}

  for customerName, aliases in aliasesDict:
    customerID = getCustomerID(cur, customerName)

    namesList = aliases.append(customerName)

    customerIDict[customerID] = namesList

  return customerIDict