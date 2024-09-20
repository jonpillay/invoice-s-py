from tkinter import *
from ttkbootstrap.constants import *
import ttkbootstrap as tkb

from isp_db_setup_functs import checkDBStatus
from isp_render_app import renderMain

import sqlite3
import os

def startApp():

  basedir = os.path.dirname(__file__)

  try:
      from ctypes import windll  # Only exists on Windows.

      myappid = "mycompany.myproduct.subproduct.version"
      windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
  except ImportError:
      pass

  conn = sqlite3.connect(os.getenv("DB_NAME"))
  cur = conn.cursor()

  checkDBStatus(cur, conn)

  cur.close()
  conn.close()

  root = tkb.Window(themename="cosmo")

  renderMain(root)

  root.mainloop()

  return root

if __name__ == "__main__":
  startApp()