def compareCustomerToAliasesDict(customer, aliasesDict):
  for customerDB in aliasesDict:
    if customer.upper() == customerDB.upper():
        return True
    elif customer.upper() in aliasesDict[customerDB]:
        return True