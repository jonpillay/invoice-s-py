from fpdf import FPDF
from fpdf.enums import XPos, YPos

from PIL import ImageFont

from datetime import datetime

from isp_dataframes import Transaction, Invoice
from isp_printer_helpers import getCellWidth, genFontPath

class TransactionUploadPDF(FPDF):

  def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)

      self.set_auto_page_break(auto=True, margin=10) 

  def register_fonts(self):
    self.add_font("alpha-slab", fname="./fonts/AlfaSlabOne-Regular.ttf")
    self.add_font("jersey10", fname="./fonts/Jersey10-Regular.ttf")
    self.add_font("special-elite", fname="./fonts/SpecialElite-Regular.ttf")
    self.add_font("ultra", fname="./fonts/Ultra-Regular.ttf")
    self.add_font("rajdhani", fname="./fonts/Rajdhani-Regular.ttf")
    self.add_font("rajdhani", style='B', fname="./fonts/Rajdhani-Bold.ttf")


  def header(self):

    if self.page_no() == 1:

      self.set_font('times', 'BU', 25)
      self.set_x(20)
      self.cell(0, 15, f"KFS Report {datetime.today().strftime('%d/%m/%Y')}", border=0, new_y=YPos.NEXT)
      self.set_font('times', 'b', 15)
      self.set_x(25)
      self.cell(0, 7, f'This is some holder text')
      self.ln(10)

    else:
      self.set_x(20)
      self.set_y(15)

  def printCustomerName(self, customer):
    self.set_font('ultra', 'U', 20)
    self.set_x(8)
    self.cell(0, 10, f"{customer}", border=0, new_y=YPos.NEXT)

  def printInvoiceNumber(self, invoiceNum):
    self.set_font('alpha-slab', '', 15)
    self.set_x(15)
    self.cell(0, 8, f"#{invoiceNum}", border=0, new_y=YPos.NEXT)

  def printInvoiceNumberInline(self, invoiceNum):
    font = ImageFont.truetype(genFontPath('AlfaSlabOne-Regular.ttf'), 10)
    self.set_font('alpha-slab', '', 10)
    self.cell(getCellWidth(f"# {str(invoiceNum)} ", font, 2.9), 4, f"#{invoiceNum} ", border=0)

  def printMultiInvoiceNumber(self, lowInvoiceNum, highInvoiceNum):
    self.set_font('alpha-slab', '', 15)
    self.set_x(15)
    self.cell(0, 8, f"#{lowInvoiceNum} - {highInvoiceNum}", border=0, new_y=YPos.NEXT)

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
      self.printCorrectionNumber(f"£{abs(amount)}")
      self.set_text_color(0, 0, 0)

    else:
      self.printInlineBold("Customer underpayed by ")
      self.set_text_color(255, 0, 0)
      self.set_x(20)
      self.printCorrectionNumber(f"£{abs(amount)}")
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

  def printInvoiceNumCorrectedReport(self, invoiceNumCorrected):

    transaction = invoiceNumCorrected[0]
    errorInvoice = invoiceNumCorrected[1]
    correctInvoice = invoiceNumCorrected[2]

    self.printInvoiceNumber(correctInvoice.invoice_num)

    self.set_x(15)

    self.printInlineDescription(f"Incoming Transaction Had Errornous Invoice Number")
    self.set_x(90)
    self.printInlineBold(f"{errorInvoice.invoice_num} ")
    self.printInlineDescription(" (now corrected)")

    self.ln(5)
    self.set_x(20)

    self.printTransaction(transaction)

    self.ln(5)
    self.set_x(15)

    self.printInlineDescription(f"Does Not Match")

    self.ln(5)
    self.set_x(20)

    self.printInvoice(errorInvoice)

    self.ln(5)
    self.set_x(15)

    self.printInlineDescription(f"Matches amount on invoice # {correctInvoice.invoice_num} via amount {correctInvoice.amount}")

    self.ln(5)
    self.set_x(20)

    self.printInvoice(correctInvoice)

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


  # collection of functions for printing out the different outputs of printCorrectionTransactionError

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

    invoiceGroupTotal = sum(multiInvoice.amout for multiInvoice in invoiceGroup)

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
      self.printErrorMatchedToPreviousError(correctionTransaction)
    else:
      print("we should not reach here")


  def printInCompExactMatch(self, inCompMatch):

    transaction = inCompMatch[0]
    invoice = inCompMatch[1]
    
    self.printInvoiceNumber(invoice.invoice_num)

    self.set_x(20)

    self.printInvoice(invoice)

    self.ln(5)
    self.set_x(20)

    self.printTransaction(transaction)

    self.ln(8)


  def printIncompCloseMatch(self, inCompMatch):

    transaction = inCompMatch[0]
    invoice = inCompMatch[1]
    errorAmount = inCompMatch[2]
    
    self.printInvoiceNumber(invoice.invoice_num)

    self.ln(1)

    self.set_x(18)

    self.printInlineBold("Transaction matches to Invoice with Error.")

    self.ln(8)

    self.set_x(20)

    self.printInvoice(invoice)

    self.ln(5)
    self.set_x(20)

    self.printTransaction(transaction)

    self.ln(5)
    self.set_x(19)

    self.printCorrectionMessage(errorAmount)

    self.ln(8)


  def printInCompMatchedPair(self, inCompMatch):
    
    if len(inCompMatch) == 2:
      self.printInCompExactMatch(inCompMatch)
    else:
      self.printIncompCloseMatch(inCompMatch)


  def printIncompErrorExactMatch(self, inCompErrorMatch):
    
    invoice = inCompErrorMatch[0]
    transaction = inCompErrorMatch[1]
    prevErrorTransaction = inCompErrorMatch[2]

    self.printInlineDescription(f"Mispayment on Invoice ")
    self.printInlineBold(f"{invoice.invoice_num}")
    self.printInlineDescription("is correction for past error payment on invoice ")
    self.printInlineBold(f"{prevErrorTransaction.invoice_num}")

    self.printInvoiceNumber(invoice.invoice_num)

    self.set_x(20)

    self.printInvoice(invoice)

    self.ln(5)
    self.set_x(20)

    self.printTransaction(transaction)


    

  def printInCompErrorCloseMatch(self, inCompErrorMatch):
    
    invoice = inCompErrorMatch[0]
    transaction = inCompErrorMatch[1]
    prevErrorTransaction = inCompErrorMatch[2]
    difference = inCompErrorMatch[3]

    self.printInlineDescription(f"Mispayment on Invoice ")
    self.printInlineBold(f"{invoice.invoice_num}")
    self.printInlineDescription("is correction for past error payment on invoice ")
    self.printInlineBold(f"{prevErrorTransaction.invoice_num} ")

    self.printInvoiceNumber(invoice.invoice_num)

    self.set_x(20)

    self.printInvoice(invoice)

    self.ln(5)
    self.set_x(20)

    self.printTransaction(transaction)

    self.printCorrectionMessage(difference)


  def printIncompErrorCorrectionMatched(self, inCompErrorMatch):

    if len(inCompErrorMatch) == 3:
      self.printIncompErrorExactMatch(inCompErrorMatch)
    if len(inCompErrorMatch) == 4:
      self.printInCompErrorCloseMatch(inCompErrorMatch)




  def printMultiInvoiceTransactionMatch(self, multiInvoiceTransactionMatch):
    
    parentTransaction = multiInvoiceTransactionMatch[0][0]
    matchedInvoiceList = multiInvoiceTransactionMatch[1]

    totalInvoiced = round(sum(invoiced.amount for invoiced in matchedInvoiceList), 2)

    self.printMultiInvoiceNumber(parentTransaction.invoice_num, parentTransaction.high_invoice)

    self.set_x(15)

    self.printInlineBold("Multi Invoice Transaction Match")
    self.ln(8)

    self.set_x(15)

    self.printTransaction(parentTransaction)
    self.ln(8)
    
    self.set_x(20)

    self.printInlineBold("Pays For:")
    self.ln(8)


    for invoice in matchedInvoiceList:

      self.set_x(25)
      self.printInvoiceNumberInline(invoice.invoice_num)
      self.printInvoice(invoice)
      self.ln(5)

    self.ln(8)
    self.set_x(15)
    self.printInlineDescription("Total Invoiced =")
    self.printInlineBold(f"£{str(totalInvoiced)}")
    self.printInlineDescription("  Total Paid =")
    self.printInlineBold(f"£{str(parentTransaction.amount)}")
    self.ln(10)



  def printMultiInvoiceTransactionError(self, multiInvoiceTransactionError):
    
    parentTransaction = multiInvoiceTransactionError[0][0]
    errorInvoiceList = multiInvoiceTransactionError[1]

    totalInvoiced = round(sum(invoiced.amount for invoiced in errorInvoiceList), 2)

    self.printMultiInvoiceNumber(parentTransaction.invoice_num, parentTransaction.high_invoice)

    self.set_x(15)

    self.printInlineBold("Multi Invoice Transaction Match")
    self.ln(8)

    self.set_x(15)

    self.printTransaction(parentTransaction)
    self.ln(8)
    
    self.set_x(20)

    self.printInlineBold("Pays For:")
    self.ln(8)


    for invoice in errorInvoiceList:

      self.set_x(25)
      self.printInvoiceNumberInline(invoice.invoice_num)
      self.printInvoice(invoice)
      self.ln(5)

    self.ln(8)
    self.set_x(15)
    self.printInlineDescription("Total Invoiced =")
    self.printInlineBold(f"£{str(totalInvoiced)}")
    self.printInlineDescription("  Total Paid =")
    self.printInlineBold(f"£{str(parentTransaction.amount)}")
    self.ln(10)

    self.printCorrectionMessage(round(parentTransaction.amount - totalInvoiced, 2))


  def printNoMatchTransaction(self, transaction):

    self.set_x(20)

    self.printTransaction(transaction)

    if transaction.error_notes != None:
      self.ln(4)
      self.printInlineBold("Notes: ")
      self.printInlineDescription(transaction.error_notes)

    self.ln(10)

  def printNewCustomerTransaction(self, transaction):

    self.set_x(20)

    self.printTransaction(transaction)

    self.ln(8)