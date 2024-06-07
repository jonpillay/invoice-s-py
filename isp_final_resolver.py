from isp_noMatch_list import noMatchList
from isp_data_handlers import groupDataClassObjsByAttribute


# Sort noMatch list of Transactions into sublists orderd by customer_id
noMatchGroups = groupDataClassObjsByAttribute(noMatchList, 'customer_id')