from isp_csv_helpers import getFilename
from isp_db_upload_handlers import handleInvoiceUpload, handleTransactionUpload

def handleInvoiceUploadClick():
  filename = getFilename()
  handleInvoiceUpload(filename)

def handleTransactionUploadClick():
  filename = getFilename()
  handleTransactionUpload(filename)