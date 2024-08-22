from PIL import ImageFont

def genFontPath(fileName):

  return f"./fonts/{fileName}"

def getCellWidth(str, font, demon):

  return font.getmask(str).getbbox()[2]/demon