def compareCustomerToAliasesDict(customer, aliasesDict):
  for customerDB in aliasesDict:
    if customer.upper() == customerDB.upper():
        return True
    elif customer.upper() in aliasesDict[customerDB]:
        return True
    

def findCustomerIDInTup(customerName, customerTup):
  for id, name in customerTup:
    if name.upper() == customerName.upper():
      return id
    
def getCustomerDBName(aliasDict, name):
  for customer in aliasDict:
    if name == customer:
      return customer
    elif name in aliasDict[customer]:
      return customer
    

def checkIfTransactionErrorIsCorrection():
  pass