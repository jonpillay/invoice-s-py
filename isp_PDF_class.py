from fpdf import FPDF
from fpdf.enums import XPos, YPos

from PIL import ImageFont

from datetime import datetime

from isp_dataframes import Transaction, Invoice
from isp_printer_helpers import getCellWidth, genFontPath

class TransactionUploadPDF(FPDF):

  def register_fonts(self):
    self.add_font("alpha-slab", fname="./fonts/AlfaSlabOne-Regular.ttf")
    self.add_font("jersey10", fname="./fonts/Jersey10-Regular.ttf")
    self.add_font("special-elite", fname="./fonts/SpecialElite-Regular.ttf")
    self.add_font("ultra", fname="./fonts/Ultra-Regular.ttf")
    self.add_font("rajdhani", fname="./fonts/Rajdhani-Regular.ttf")
    self.add_font("rajdhani", style='B', fname="./fonts/Rajdhani-Bold.ttf")


  def header(self):

    self.set_font('times', 'BU', 25)
    self.set_x(20)
    self.cell(0, 15, 'KFS Transaction Upload Report', border=0, new_y=YPos.NEXT)
    self.set_font('times', 'b', 15)
    self.set_x(25)
    self.cell(0, 7, f'This is some holder text')
    self.ln(10)

  def printCustomerName(self, customer):
    self.set_font('ultra', 'U', 20)
    self.set_x(8)
    self.cell(0, 10, f"{customer}", border=0, new_y=YPos.NEXT)

  def printInvoiceNumber(self, invoiceNum):
    self.set_font('alpha-slab', '', 15)
    self.set_x(15)
    self.cell(0, 8, f"#{invoiceNum}", border=0, new_y=YPos.NEXT)

  def printCategoryTitle(self, title):
    self.set_font('special-elite', '', 16)
    self.set_x(12)
    self.cell(10, 10, f"{title}:", border=0, new_y=YPos.NEXT)

  def printInlineDescription(self, str):
    font = ImageFont.truetype(genFontPath('Rajdhani-Regular.ttf'), 10)
    self.set_font('rajdhani', '', 10)
    self.cell(getCellWidth(str, font, 2.5), 4, f"{str}", ln=0)

  def printInlineBold(self, str):
    font = ImageFont.truetype(genFontPath('Rajdhani-Bold.ttf'), 12)
    self.set_font('rajdhani', 'B', 12)
    self.cell(getCellWidth(str, font, 2.6), 4, f"{str}", ln=0)

  def printCorrectionNumber(self, str):
    font = ImageFont.truetype(genFontPath('Rajdhani-Bold.ttf'), 15)
    self.set_x(63)
    self.set_font('rajdhani', 'B', 15)
    self.cell(getCellWidth(str, font, 2.9), 4, f"{str}", ln=0)

  def printInvoice(self, invoice):
    self.printInlineDescription("-")
    self.printInlineBold(f" £{invoice.amount} ")
    self.printInlineDescription("Issued on ")
    self.printInlineBold(invoice.date_issued.strftime('%d/%m/%Y'))
    self.printInlineDescription("to ")
    self.printInlineBold(f" {invoice.issued_to}")

  def printTransaction(self, transaction):
    self.printInlineDescription("-")
    self.printInlineBold(f" £{transaction.amount} ")
    self.printInlineDescription("Paid on ")
    self.printInlineBold(f"{transaction.paid_on.strftime('%d/%m/%Y')}")
    self.printInlineDescription("by ")
    self.printInlineBold(f" {transaction.paid_by}")
    self.printInlineDescription("Transaction Database ID =")
    self.printInlineBold(str(transaction.transaction_id))


  def printCorrectionMessage(self, amount):

    if amount < 0:

      self.printInlineBold("Customer overpayed by ")
      self.set_text_color(4, 168, 30)
      self.set_x(20)
      self.printCorrectionNumber(f"£{str(0-amount)}")
      self.set_text_color(0, 0, 0)

    else:
      self.printInlineBold("Customer underpayed by ")
      self.set_text_color(255, 0, 0)
      self.set_x(20)
      self.printCorrectionNumber(f"£{str(0-amount)}")
      self.set_text_color(0, 0, 0)


  # write print inline normal

  # write print inline amount

  # write print error notes

  # write print normal inline

  # write a resolution message print


  def printMatchedSingles(self, matchedSinglePair):
    
    transaction = matchedSinglePair[0]
    invoice = matchedSinglePair[1]

    self.printInvoiceNumber(invoice.invoice_num)

    self.set_x(20)

    self.printInvoice(invoice)

    self.ln(5)
    self.set_x(20)

    self.printTransaction(transaction)

    self.ln(8)

  def printCorrectedErrorsReport(self, correctedError):

    transaction = correctedError[0][0]
    invoice = correctedError[0][1]
    dummyTransaction = correctedError[1]

    self.printInvoiceNumber(invoice.invoice_num)

    self.set_x(20)

    self.printInvoice(invoice)
    self.ln(5)

    self.set_x(20)

    self.printTransaction(transaction)
    self.ln(5)

    self.set_x(20)

    self.printCorrectionMessage(round(invoice.amount - transaction.amount, 2))

    self.ln(8)


  # collection of functions for printing out the different outputs of printcorrectionTransactionError

  def printErrorMatchedToSingleInvoice(self, singleErrorCorrectionTransaction):

    transaction = singleErrorCorrectionTransaction[0][0]
    invoice = singleErrorCorrectionTransaction[0][1]
    matchedUnpaidInvoice = singleErrorCorrectionTransaction[1]

    ogError = transaction.amount - invoice.amount

    self.printInlineDescription(f"Incoming Transaction's Error ")
    self.printInlineBold(f"(£{ogError})")
    self.printInlineDescription(f" Pays For Unpaid Transaction")

    self.ln(7)

    self.printInvoice(invoice)
    self.ln(5)
    self.printTransaction(transaction)
    self.ln(5)

    self.printInlineDescription("Transaction pays for previous unpaid Invoice ")
    self.printInlineBold(f"#{matchedUnpaidInvoice.invoice_num}")
    self.printInlineDescription(" for ")
    self.printInlineBold(f"{matchedUnpaidInvoice.amount}")

    self.ln(5)
  
  
  def printErrorMatchedToInvoiceGroup(self, multiErrorCorrectionTransaction):

    transaction = multiErrorCorrectionTransaction[0][0]
    invoice = multiErrorCorrectionTransaction[0][1]
    invoiceGroup = multiErrorCorrectionTransaction[1]

    ogError = transaction.amount - invoice.amount

    invoiceGroupTotal = sum(invoiceGroup.amout)

    self.printInlineDescription(f"Incoming Transaction's Error ")
    self.printInlineBold(f"(£{ogError})")
    self.printInlineDescription(f" Pays For Unpaid Transaction Group")

    self.ln(7)

    self.printInvoice(invoice)
    self.ln(5)
    self.printTransaction(transaction)
    self.ln(5)

    self.printInlineDescription("Transaction pays for previous unpaid Invoices between => ")
    self.printInlineBold(f"{invoiceGroup[0].invoice_num} and {invoiceGroup[-1].invoice_num}")
    self.ln(5)

    self.set_x(30)

    for matchedInvoice in invoiceGroup:

      self.printInvoice(matchedInvoice)
      self.ln(2)

    self.set_x(25)

    self.printInlineDescription("Transaction Error ")
    self.printInlineBold(f"£{ogError}")
    self.printInlineDescription(" = ")
    self.printInlineBold(f"£{invoiceGroupTotal}")

    self.ln(8)
    self.set_x(20)

  def printErrorMatchedToPreviousError(self, multiErrorCorrectionTransaction):

    transaction = multiErrorCorrectionTransaction[0][0]
    invoice = multiErrorCorrectionTransaction[0][1]

    previousDummyTransaction = multiErrorCorrectionTransaction[1]

    ogError = transaction.amount - invoice.amount

    self.printInlineDescription(f"Incoming Transaction's Error ")
    self.printInlineBold(f"(£{ogError})")
    self.printInlineDescription(f" Corrects Previous Error")

    self.ln(7)

    self.printInvoice(invoice)
    self.ln(5)
    self.printTransaction(transaction)
    self.ln(5)

    self.printCorrectionMessage(ogError)
    self.ln(5)

    self.printInlineDescription("Mispayment is correction on Error from Invoice ")
    self.printInlineBold(f"{previousDummyTransaction.invoice_num}")

    self.ln(8)



  def printCorrectionTransactionError(self, correctionTransaction):
    
    # first task is to distinguish between the different types of reamtched transactions and invoices we have

    if isinstance(correctionTransaction[1], list):
      # the element is a report on an error transaction that was matched to a group of unpaid invoices
      self.printErrorMatchedToInvoiceGroup(correctionTransaction)
    elif isinstance(correctionTransaction[1], Invoice):
      # the element is a report on an error that has been matched to a single invoices
      self.printErrorMatchedToSingleInvoice(correctionTransaction)
    elif isinstance(correctionTransaction[1], Transaction):
      # the element is a report on an error that has been matched to correct a previous error
      pass
    else:
      print("we should not reach here")



    # The list shouold have 3 different lists of rematched errors in it.

    # One list represent an error transaction whose error has been matched to paying for an entire invoice => list [transaction, [invoice, previousPaidInvoice]] to [[transaction, invoice], prevPaidInvoice]

    # a second list refers to an error transaction whose error have been found to pay for a group of unpaid invoices => list [transaction, invoice, [invoiceGroup]] to [[transaction, invoice], invoiceGroup]

    # a third list referes to transactions that correct past error payments => list [transaction, [dummyTransaction, prevDummyTransaction]] to [[transaction, invoice], previousDummyTransaction]

    # need to find a way to distinguish between them