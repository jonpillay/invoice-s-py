from isp_csv_helpers import getFilename
from isp_db_upload_handlers import handleInvoiceUpload, handleTransactionUpload

def handleInvoiceUploadClick(root):
  filename = getFilename()
  handleInvoiceUpload(root, filename)

def handleTransactionUploadClick(root):
  filename = getFilename()
  handleTransactionUpload(root, filename)