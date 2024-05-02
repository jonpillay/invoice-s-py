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