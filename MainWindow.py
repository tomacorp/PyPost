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

# from twisted.application import reactors

import CommandInterp
import LineEditHist

# conda install pyside
# pip install fysom
# conda remove pyqt

# Project->Project Properties
# Custom python: /Users/toma/Library/Enthought/Canopy_64bit/User/bin/python
# Or: /Users/toma/python278i/bin/python
# Or: /Users/toma/anaconda/bin/python

# TODO:
#   Add a 2-D plot function. Look at code from therm.py, incorporate this in an
#     interactive way, both with png and hdf5 data.
#
#   Add markers. Markers need to support both 1D and 2D.
#
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

# Make an installer for Windows with http://pythonhosted.org/PyInstaller/
#
# Might need http://winpython.github.io in addition or instead.
# Or http://www.py2exe.org

# Plotting
# http://www.jeffreytratner.com/example-pandas-docs/series-str-2013-10-6/visualization.html
# http://www.physics.ucdavis.edu/~dwittman/Matplotlib-examples/

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


class Post(QMainWindow):
  def __init__(self, parent=None):
    super(Post, self).__init__(parent)

    self.table = Form(self)
    self.setCentralWidget(self.table)

    self.resize(1200, 420)
    self.createActions()
    self.createMenus()

    self.setWindowTitle('PyPost')
    self.statusBar().showMessage('Ready')

  def newFile(self):
    self.statusBar().showMessage("Invoked File|New")
    print("Invoked File|New")

  def open_(self):
    self.statusBar().showMessage("Invoked File|Open")
    print("Invoked File|Open")

  def save(self):
    self.statusBar().showMessage("Invoked File|Save")
    print("Invoked File|Save")

  def print_(self):
    self.statusBar().showMessage("Invoked File|Print")
    print("Invoked File|Print")

  def about(self):
    #self.statusBar().showMessage("Invoked Help|About")
    #print("Invoked Help|About")
    QtGui.QMessageBox.about(self, "About PyPost",
                                  "<b>PyPost</b> is an interactive dataset visualizer " +
                                  "for electronic and thermal engineering.")

  def aboutQt(self):
    print("Invoked <b>Help|About Qt</b>")

  def prev(self):
    self.table.lineedit.historyUp()

  def next_(self):
    self.table.lineedit.historyDown()

  def createMenus(self):
    menubar= self.menuBar()

    self.fileMenu = menubar.addMenu("File")
    self.fileMenu.addAction(self.newAct)
    self.fileMenu.addAction(self.openAct)
    self.fileMenu.addAction(self.saveAct)
    self.fileMenu.addSeparator()
    self.fileMenu.addAction(self.printAct)

    # FIXME: TODO: Looks like a bug in PySide:
    # One of the next two lines needs to be present in order for the
    # Help menu to show up.
    # Also, there is an unexpected search box in the help.
    # It looks like there is some interference from OSX.

    self.fileMenu.addAction(self.aboutAct)
    self.fileMenu.addAction(self.aboutQtAct)

    self.cmdMenu = menubar.addMenu("Command")
    self.cmdMenu.addAction(self.previousAct)
    self.cmdMenu.addAction(self.nextAct)

    self.helpMenu = menubar.addMenu("&Help")
    self.helpMenu.addAction(self.aboutAct)
    self.helpMenu.addAction(self.aboutQtAct)

  def createActions(self):
    self.newAct = QtGui.QAction("&New", self,
                                shortcut=QtGui.QKeySequence.New,
                                statusTip="Create a new file", triggered=self.newFile)

    self.openAct = QtGui.QAction("&Open...", self,
                                 shortcut=QtGui.QKeySequence.Open,
                                 statusTip="Open an existing file", triggered=self.open_)

    self.saveAct = QtGui.QAction("&Save", self,
                                 shortcut=QtGui.QKeySequence.Save,
                                 statusTip="Save the document to disk", triggered=self.save)

    self.printAct = QtGui.QAction("&Print...", self,
                                  shortcut=QtGui.QKeySequence.Print,
                                  statusTip="Print the document", triggered=self.print_)

    self.aboutAct = QtGui.QAction("About", self,
                                  statusTip="About PyPost", triggered=self.about)

    self.aboutQtAct = QtGui.QAction("About &Qt", self,
                                    statusTip="Show the Qt library's About box",
                                    triggered=self.aboutQt)
    self.aboutQtAct.triggered.connect(QtGui.qApp.aboutQt)

    self.previousAct = QtGui.QAction("Previous", self,
                                     shortcut=QtGui.QKeySequence.NextChild,
                                     statusTip="Previous Command", triggered=self.prev)

    self.nextAct = QtGui.QAction("Next", self,
                                     shortcut=QtGui.QKeySequence.PreviousChild,
                                     statusTip="Next Command", triggered=self.next_)

class Form(QWidget):

  def __init__(self, mainWindow):
    super(Form, self).__init__()

    # self.mainWindow= mainWindow
    self.resize(720, 320)
    self.browser = QTextBrowser()

    self.sc      = MyStaticMplCanvas(self, width=2.5, height=2, dpi=100)
    self.lineedit = LineEditHist.lineEditHist("")
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

    message= self.commandInterp.executeCmd(cmdText)
    pyCode= self.commandInterp.pyCode;
    print("cmdText: " + cmdText + "\nPython code: " + str(pyCode))
    self.lineedit.addCommandToDB(cmdText, pyCode)

    self.browser.append(message)
    self.lineedit.clear()
    self.lineedit.resetHistoryPosition()

    # self.mainWindow.statusBar().showMessage('Next')

class MyMplCanvas(FigureCanvas):
  """A QWidget that implements Matplotlib"""
  def __init__(self, parent=None, width=5, height=4, dpi=100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    self.plt = fig.add_subplot(111)
    # We want the axes cleared every time plot() is called
    # self.plt.hold(False)

    # self.compute_initial_figure()

    FigureCanvas.__init__(self, fig)

    # self.setParent(parent)

    fig.tight_layout(pad=1.5, w_pad=0.0, h_pad=0.0)

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

  main = Post()
  main.show()

  sys.exit(app.exec_())
