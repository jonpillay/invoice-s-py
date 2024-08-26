from PIL import ImageFont

def genFontPath(fileName):

  return f"./fonts/{fileName}"

def getCellWidth(str, font, denom):

  return font.getmask(str).getbbox()[2]/denom