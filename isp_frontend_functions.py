from isp_csv_helpers import getCSVfile
from isp_db_upload_handlers import handleInvoiceUpload

def handleInvoiceUploadClick():
  CSVEntries = getCSVfile()
  handleInvoiceUpload(CSVEntries)