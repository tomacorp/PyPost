

import sys
from numpy import *
from collections import deque

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QDialog, QLineEdit, QTextBrowser,
                             QVBoxLayout, QHBoxLayout, QSizePolicy,
                          QToolBar, QMenuBar, QMenu, QAction, QMainWindow, QWidget)
from PyQt5.QtGui import QKeySequence

"""from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from PySide.QtCore import Signal
from PySide.QtGui import (QApplication, QDialog, QLineEdit, QTextBrowser,
                          QVBoxLayout, QHBoxLayout, QKeySequence, QSizePolicy,
                          QToolBar, QMenuBar, QMenu, QAction, QMainWindow, QWidget)
                          """

import matplotlib
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import EngFormatter
import EngMplCanvas
import ImgMplCanvas

# TODO: Refactor to take more canvas types.

class MplCanvasDict():
    def __init__(self, parent=None, width=5, height=4, dpi=72):
        self.cd= {}
        self.active= ''
        self.parent= parent
        self.width= width
        self.height= height
        self.dpi= dpi

    def setActive(self, canvasName):
        if (canvasName in self.cd):
            self.active= canvasName
        else:
            print("Error: no canvas is named " + str(canvasName))
        return

    def getActiveCanvas(self):
        if (self.active in self.cd):
            return self.cd[self.active]
        else:
            print("Error: the active canvas " + str(canvasName) + " does not exist")

    def getActiveCanvasName(self):
        return self.active

    def create(self, canvasName='', parent=None, width=5, height=4, dpi=72):
        if canvasName == '':
            canvasCount= len(self.cd) + 1
            canvasName= "PyPost_" + str(canvasCount)
        c= EngMplCanvas.EngMplCanvas(parent=parent, width=width, height=height, dpi=dpi)
        c.setWindowTitle(canvasName)
        c.name= canvasName
        self.cd[canvasName]= c
        return canvasName

    def createImg(self, canvasName='', parent=None, width=5, height=4, dpi=72):
        if canvasName == '':
            canvasCount= len(self.cd) + 1
            canvasName= "PyPost_" + str(canvasCount)    
        c= ImgMplCanvas.ImgMplCanvas(parent=parent, width=width, height=height, dpi=dpi)
        # c.setWindowTitle(canvasName)
        c.name= canvasName
        self.cd[canvasName]= c
        return canvasName

    def remove(self, canvasName):
        if canvasName == 'PyPost_1':
            print("Can't delete main graph window PyPost_1")
            return
        if self.active == canvasName:
            self.active= 'PyPost_1'
        c= self.cd[canvasName]
        del(self.cd[canvasName])
        c.deleteLater()
