from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import sys
from numpy import *
from collections import deque

from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from PySide.QtCore import Signal
from PySide.QtGui import (QApplication, QDialog, QLineEdit, QTextBrowser,
                          QVBoxLayout, QHBoxLayout, QKeySequence, QSizePolicy,
                          QToolBar, QMenuBar, QMenu, QAction, QMainWindow, QWidget)

import matplotlib
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# BUG: After panning and zooming, gs command resets view to original.
#      Should be sending messages back to graphics limits so that they are similar
#      to what would happen manually.

class EngMplCanvas(FigureCanvas):
  """A QWidget that implements Matplotlib"""
  def __init__(self, parent=None, width=5, height=4, dpi=100):

    self.yauto= True
    self.ylimlow= -16.0
    self.ylimhigh= 16.0
    self.xauto= True
    self.xlimlow= 0.0
    self.xlimhigh= 0.02
    self.fsz= 12
    
    self.commandDelegate= None

    fig = Figure(figsize=(width, height), dpi=dpi)
    self.plt = fig.add_subplot(111)

    FigureCanvas.__init__(self, fig)

    fig.tight_layout(pad=1.5, w_pad=0.0, h_pad=0.0)

    FigureCanvas.setSizePolicy(self,
                               QSizePolicy.Expanding,
                               QSizePolicy.Expanding)
    FigureCanvas.updateGeometry(self)

  def plotYList(self, res, arg, title):
    self.plt.plot(res)
    self.plt.set_xlabel('Index', fontsize=self.fsz,picker=5)
    self.plt.set_ylabel(arg, fontsize=self.fsz)
    self.plt.set_title(title, fontsize=self.fsz)
    self.setAutoscale()
    self.draw()
    self.show()

  def plotXYList(self, x, y, xlabel, ylabel, title):
    self.plt.plot(x, y, picker=5)
    self.plt.set_xlabel(xlabel, fontsize=self.fsz)
    self.plt.set_ylabel(ylabel, fontsize=self.fsz)
    self.plt.set_title(title, fontsize=self.fsz)
    self.setAutoscale()
    self.draw()
    self.show()

  def setAutoscale(self):
    if self.yauto:
      self.plt.set_autoscaley_on(True)
    else:
      self.plt.set_autoscaley_on(False)
      self.ylimlow, self.ylimhigh= self.plt.set_ylim(self.ylimlow, self.ylimhigh)
    if self.xauto:
      self.plt.set_autoscalex_on(True)
    else:
      self.plt.set_autoscalex_on(False)
      self.xlimlow, self.xlimhigh= self.plt.set_xlim(self.xlimlow, self.xlimhigh)
      
  def setCommandDelegate(self, obj):
    self.commandDelegate= obj
    
  