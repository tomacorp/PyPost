from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import sys
from numpy import *
from collections import deque

# import numexpr as ne
from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSignal as Signal
from PyQt4.QtGui import (QApplication, QDialog, QLineEdit, QTextBrowser,
                         QVBoxLayout, QHBoxLayout, QKeySequence, QSizePolicy)

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import CommandInterp

# TODO:
#   Add variables and functions for constants and vectors
#   hdf5 data import
#   compiled scripts
#   IPC port, web server
#   Display controls

# Need gr x .vs y
# Need eval on Qtplot command in case it fails
# Need to check Qtplot for x and y different dimensions in plot
# Create a transcript file with command line history in it.
# Create a transcript file with evaluated Python in it.

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
    self.lineedit = lineEditHist("Type an expression and press Enter")
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

    self.setWindowTitle("Post Processor")

  def updateUi(self):
    cmdText = unicode(self.lineedit.text())
    self.lineedit.history.append('')
    message= self.commandInterp.executeCmd(cmdText)
    self.browser.append(message)
    self.lineedit.clear()
    self.lineedit.resetHistoryPosition()

class MyMplCanvas(FigureCanvas):
  """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
  def __init__(self, parent=None, width=5, height=4, dpi=100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    self.axes = fig.add_subplot(111)
    # We want the axes cleared every time plot() is called
    self.axes.hold(False)

    self.compute_initial_figure()

    FigureCanvas.__init__(self, fig)
    self.setParent(parent)

    FigureCanvas.setSizePolicy(self,
                               QSizePolicy.Expanding,
                               QSizePolicy.Expanding)
    FigureCanvas.updateGeometry(self)

  def compute_initial_figure(self):
    pass

class MyStaticMplCanvas(MyMplCanvas):
  """Simple canvas with a sine plot."""
  def compute_initial_figure(self):
    t = arange(0.0, 3.0, 0.01)
    s = sin(2*pi*t)
    self.axes.plot(t, s)

class lineEditHist(QLineEdit):
  def __init__(self, initialMessage):
    self.history= deque([''])
    self.historyPointer= -1
    super(lineEditHist, self).__init__(initialMessage)

  # FIXME: This loses the last character while editing the current line,
  # then going back in history, and then back to the current line.
  def keyPressEvent(self, evt):
    key=evt.key()
    if key == Qt.Key_Up:
      self.historyUp()
    elif key == Qt.Key_Down:
      self.historyDown()
    else:
      self.history[-1] = unicode(self.text())
    # print("Key pressed" + str(evt.key()))
    return super(lineEditHist, self).keyPressEvent(evt)

  def resetHistoryPosition(self):
    self.historyPointer = -1

  def historyUp(self):
    if -self.historyPointer < len(self.history):
      self.historyPointer -= 1
      lastCommand= self.history[self.historyPointer]
      self.setText(lastCommand)

  def historyDown(self):
    print("Down")
    if self.historyPointer < -1:
      self.historyPointer += 1
      lastCommand= self.history[self.historyPointer]
      self.setText(lastCommand)

if __name__ == "__main__":
  app = QApplication(sys.argv)
  form = Form()
  form.show()
  app.exec_()
