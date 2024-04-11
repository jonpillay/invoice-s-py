from isp_csv_helpers import getFilename
from isp_db_upload_handlers import handleInvoiceUpload

def handleInvoiceUploadClick():
  filename = getFilename()
  handleInvoiceUpload(filename)