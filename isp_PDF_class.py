from fpdf import FPDF
from fpdf.enums import XPos, YPos

from datetime import datetime

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
    self.cell(0, 10, f"#{invoiceNum}", border=0, new_y=YPos.NEXT)

  def printCategoryTitle(self, title):
    self.set_font('special-elite', '', 16)
    self.set_x(12)
    self.cell(0, 8, f"{title}:", border=0, new_y=YPos.NEXT)

  def printInlineDescription(self, str):
    self.set_font('rajdhani', '', 10)
    self.set_x(20)
    self.cell(0, 4, f"{str}")

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

    self.printInlineDescription(f"Invoice # {invoice.invoice_num} dated {invoice.date_issued.strftime('%d/%m/%Y')} for £{invoice.amount}")
    self.printInlineDescription(f"Dated")


    self.cell(20, 5, f"Invoice # {invoice.invoice_num} dated {invoice.date_issued.strftime('%d/%m/%Y')} for £{invoice.amount}", border=0, new_y=YPos.NEXT)
    self.cell(0, 5, f"Paid for by Transaction dated {transaction.paid_on.strftime('%d/%m/%Y')} for {transaction.amount}", border=0, new_y=YPos.NEXT)
    self.ln(2)

  def printcorrectedErrorsReport(self, correctedError):

    transaction = correctedError[0][0]
    invoice = correctedError[0][1]
    dummyTransaction = correctedError[1]

    self.set_font("times", '', 10)
    self.set_x(20)

    self.cell(10, 5, f"Invoice # {invoice.invoice_num} dated {invoice.date_issued.strftime('%d/%m/%Y')} for £{invoice.amount}", border=0, new_x=XPos.LEFT, new_y=YPos.NEXT)
    self.cell(0, 5, f"Paid for by Transaction dated {transaction.paid_on.strftime('%d/%m/%Y')} for {transaction.amount}", border=0, new_x=XPos.LEFT, new_y=YPos.NEXT)
    self.ln(2)
    self.cell(0, 5, f"Corrected by {dummyTransaction.amount}", border=0, new_x=XPos.LEFT, new_y=YPos.NEXT)





    

  def printResults(self, category, resultsList):

    self.set_font('times', 10)
    self.set_x(20)
    self.cell(0, 10, f'KFS Transaction Upload Report {resultsList}', border=0, new_y=YPos.NEXT)