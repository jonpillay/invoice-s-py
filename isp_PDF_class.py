from fpdf import FPDF
from fpdf.enums import XPos, YPos

from output_test import outputDict as testOutputDict

class TransactionUploadPDF(FPDF):

  # def __init__(self, customerResultsDictionary, *args, **kwargs):
  #   super().__init__(*args, **kwargs)
  #   self.customerResultsDictionary = customerResultsDictionary

  def header(self):

    self.set_font('times', 'BU', 25)
    self.set_x(20)
    self.cell(0, 15, 'KFS Transaction Upload Report', border=0, new_y=YPos.NEXT)
    self.ln(-2)
    self.set_font('times', 'b', 15)
    self.set_x(25)
    self.cell(0, 7, f'This is some holder text')
    self.ln(10)

  def printCustomerName(self, customer):
    self.set_font('times', 'U', 17)
    self.set_x(20)
    self.cell(0, 10, f"{customer}", border=0, new_y=YPos.NEXT)

  def printCategoryTitle(self, title):
    self.set_font('times', 'U', 14)
    self.set_x(20)
    self.cell(0, 8, f"{title}", border=0, new_y=YPos.NEXT)


  def printMatchedSingles(self, matchedSinglePair):
    
    transaction = matchedSinglePair[0]
    invoice = matchedSinglePair[1]

    self.set_font("times", '', 10)

    self.set_x(20)

    self.cell(10, 5, f"{invoice.amount}", border=0, new_x=XPos.LEFT, new_y=YPos.NEXT)
    self.cell(0, 5, f"{transaction.amount}", border=0, new_x=XPos.LEFT, new_y=YPos.NEXT)
    self.ln(2)






  def printResults(self, category, resultsList):

    self.set_font('times', 10)
    self.set_x(20)
    self.cell(0, 10, f'KFS Transaction Upload Report {resultsList}', border=0, new_y=YPos.NEXT)

# results = TransactionUploadPDF('P', 'mm', 'A4')

# results.add_page()

# results.printResults(testOutputDict)

# results.output('../test.pdf')