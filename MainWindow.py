from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import sys
from numpy import *
from collections import deque

from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSignal as Signal
from PyQt4.QtGui import (QApplication, QDialog, QLineEdit, QTextBrowser,
                         QVBoxLayout, QHBoxLayout, QKeySequence, QSizePolicy)

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import CommandInterp
import LineEditHist

# TODO:
#   Add variables and functions for constants and vectors
#   hdf5 data import
#   compiled scripts
#   HTTP/IPC port, web server
#   Display controls
#   Save/Recall entire state in database
#   Program launch from file that contains state
#   Graphical SVG output, esp useful over HTTP as web page

#   gr somevector
#     should plot the vector versus its index if the x-axis is otherwise undefined.
#   Need a command to set the x-axis variable.
#   gr somevector histo
#     should draw a histogram
#   gr scalar
#     should draw a flat line horizontally across the screen at y-value of scalar
#   ma scalar
#     should draw a straight vertical line at x-value of scalar
#   Could implement these with a base command that draws a straight line segment.

# Need gr x .vs y
# Need eval on Qtplot command in case it fails
# Need to check Qtplot for x and y different dimensions in plot
# Create a transcript file with command line history in it.
# Create a transcript file with evaluated Python in it.
#   This will be the basis for script generation.

# Consider:
#  In [143]: import numexpr as ne
#  In [146]: ne.evaluate('2*a*(b/c)**2', local_dict=var)
#  Out[146]: array([ 0.88888889,  0.44444444,  4.        ])

# TRY ne
# instead


class Form(QDialog):

  def __init__(self, parent=None):
    super(Form, self).__init__(parent)
    self.resize(720, 320)
    self.browser = QTextBrowser()
    self.sc      = MyStaticMplCanvas(self, width=2.5, height=2, dpi=100)
    self.lineedit = LineEditHist.lineEditHist("Type an expression and press Enter")
    self.lineedit.selectAll()

    self.topLayout = QHBoxLayout()
    self.topLayout.addWidget(self.browser)
    self.topLayout.addWidget(self.sc)

    layout = QVBoxLayout()
    layout.addLayout(self.topLayout)
    layout.addWidget(self.lineedit)

    self.setLayout(layout)
    self.lineedit.setFocus()
    self.lineedit.returnPressed.connect(self.updateUi)

    self.commandInterp= CommandInterp.CommandInterp()
    self.commandInterp.setGraphicsDelegate(self.sc)

    self.setWindowTitle("PyCalc")
    self.show()
    self.activateWindow()
    self.raise_()

  def updateUi(self):
    cmdText = unicode(self.lineedit.text())
    self.lineedit.history.append('')

    # Add command to database:
    self.lineedit.addCommandToDB(cmdText)

    message= self.commandInterp.executeCmd(cmdText)
    self.browser.append(message)
    self.lineedit.clear()
    self.lineedit.resetHistoryPosition()

class MyMplCanvas(FigureCanvas):
  """A QWidget that implements Matplotlib"""
  def __init__(self, parent=None, width=5, height=4, dpi=100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    self.plt = fig.add_subplot(111)

    # We want the axes cleared every time plot() is called
    # self.plt.hold(False)

    # self.compute_initial_figure()

    FigureCanvas.__init__(self, fig)

    self.setParent(parent)

    fig.tight_layout(pad=1.0, w_pad=1.0, h_pad=2.0)

    FigureCanvas.setSizePolicy(self,
                               QSizePolicy.Expanding,
                               QSizePolicy.Expanding)
    FigureCanvas.updateGeometry(self)

  def compute_initial_figure(self):
    pass

class MyStaticMplCanvas(MyMplCanvas):
  """ Empty plot """
  def compute_initial_figure(self):
    pass

if __name__ == "__main__":
  app = QApplication(sys.argv)
  form = Form()
  form.show()
  app.exec_()
