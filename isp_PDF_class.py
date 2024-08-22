from fpdf import FPDF
from fpdf.enums import XPos, YPos

from PIL import ImageFont

from datetime import datetime

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
    self.cell(getCellWidth(str, font, 2.5), 3, f"{str}", ln=0)

  def printInlineBold(self, str):
    font = ImageFont.truetype(genFontPath('Rajdhani-Bold.ttf'), 12)
    self.set_font('rajdhani', 'B', 12)
    self.cell(getCellWidth(str, font, 2.6), 3, f"{str}", ln=0)


  def printCorrectionMessage(self, amount):

    if amount < 0:

      self.printInlineDescription("Customer overpayed by ")
      self.set_text_color(0, 255, 0)
      self.printInlineBold(str(0-amount))
      self.set_text_color(0, 0, 0)

    else:
      self.printInlineDescription("Customer underpayed by ")
      self.set_text_color(255, 0, 0)
      self.printInlineBold(str(0-amount))
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

    # self.printInlineDescription(f"Invoice # {invoice.invoice_num} dated {invoice.date_issued.strftime('%d/%m/%Y')} for £{invoice.amount}")
    # self.printInlineDescription(f"Dated")


    self.printInlineDescription("Issued on ")
    self.printInlineBold(invoice.date_issued.strftime('%d/%m/%Y'))
    self.printInlineDescription("to ")
    self.printInlineBold(f" {invoice.issued_to}")
    self.printInlineDescription("for ")
    self.printInlineBold(f" £{invoice.amount}")
    self.ln(5)
    self.set_x(20)

    self.printInlineDescription("Paid on ")
    self.printInlineBold(f"{invoice.date_issued.strftime('%d/%m/%Y')}")
    self.printInlineDescription("by ")
    self.printInlineBold(f" {transaction.paid_by}")
    self.printInlineDescription("Transaction Database ID =")
    self.printInlineBold(str(transaction.transaction_id))



    # self.cell(2, 5, f"Paid for by Transaction dated {transaction.paid_on.strftime('%d/%m/%Y')} for {transaction.amount}", border=0, new_y=YPos.NEXT)
    self.ln(8)

  def printcorrectedErrorsReport(self, correctedError):

    transaction = correctedError[0][0]
    invoice = correctedError[0][1]
    dummyTransaction = correctedError[1]

    self.printInvoiceNumber(invoice.invoice_num)

    self.set_x(20)


    self.printInlineDescription("Issued on ")
    self.printInlineBold(invoice.date_issued.strftime('%d/%m/%Y'))
    self.printInlineDescription("to ")
    self.printInlineBold(f" {invoice.issued_to}")
    self.printInlineDescription("for ")
    self.printInlineBold(f" £{invoice.amount}")
    self.ln(5)

    self.set_x(20)

    self.printInlineDescription("Paid on ")
    self.printInlineBold(f"{invoice.date_issued.strftime('%d/%m/%Y')}")
    self.printInlineDescription("by ")
    self.printInlineBold(f" {transaction.paid_by}")
    self.printInlineDescription("for ")
    self.printInlineBold(f" £{str(transaction.amount)}")
    self.printInlineDescription("Transaction Database ID =")
    self.printInlineBold(str(transaction.transaction_id))
    self.ln(5)

    self.set_x(18)

    self.printCorrectionMessage(round(invoice.amount - transaction.amount, 2))

    self.ln(8)


    

  def printResults(self, category, resultsList):

    self.set_font('times', 10)
    self.set_x(20)
    self.cell(0, 10, f'KFS Transaction Upload Report {resultsList}', border=0, new_y=YPos.NEXT)