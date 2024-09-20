from PIL import ImageFont
import os
import sys

def genFontPath(fileName):

  if getattr(sys, 'frozen', False):
    font_dir = os.path.join(sys._MEIPASS, "fonts", fileName)
  else:
    font_dir = f"./fonts/{fileName}"

  return font_dir

def getCellWidth(str, font, denom):

  return font.getmask(str).getbbox()[2]/denom