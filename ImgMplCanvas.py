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

import skimage
from skimage import data, io
import imghdr
import ntpath

class ImgMplCanvas(FigureCanvas):
  def __init__(self, parent=None, width=5, height=4, dpi=100):
    pass
  
class Post(QMainWindow):
  def __init__(self, parent=None):
    super(Post, self).__init__(parent)

    self.graphs= MplCanvasDict.MplCanvasDict()

    self.table = MainWin(self)
    self.setCentralWidget(self.table)

    self.createActions()
    self.createMenus()

    self.setWindowTitle('PyPost')

    self.resize(1200, 420)
    self.statusBar().showMessage('Ready')  
  
if __name__ == "__main__":
  
  import os.path
  from matplotlib import pyplot as plt
  
  print("ImgMplCanvas class test")
  img= ImgMplCanvas(parent=None, width=5, height=4, dpi=100)  
  
  fn= 't/yellow.png'
  if not os.path.isfile(fn):
    print("File " + str(fn) + " not found. Bailing out.")
    
  useTk= False
  useFrame= True

  fileType= imghdr.what(fn)
  fileExtension= '.' + fileType
  if (fn.endswith(fileExtension)):
    imageName= ntpath.basename(fn)
    imageName, extension= os.path.splitext(imageName)
  else:
    imageName= 'image1'
  img= skimage.data.imread(fn)
  
  if useTk:
    print("Display image: " + str(fn) + " using Tk")
    plt.imshow(img)
    plt.show()
    
  elif useFrame:
    print("Display image: " + str(fn) + " with frame and label using PySide")
  
    app = QApplication(sys.argv)
      
    height, width, depth= shape(img)   
    fig = Figure(figsize=(width, height), dpi=100)
    
    axes = fig.add_subplot(111)
    axes.set_xlim(0, width)
    axes.set_ylim(0, height)
    axes.imshow(img)
    
    main = QtGui.QMainWindow()
    main.setGeometry(0, 100, 200+int(width*1.4), 200+int(height*1.4))
    main.setWindowTitle(imageName)  
    
    frame= QtGui.QFrame()
    frame.setFrameShape(QtGui.QFrame.StyledPanel)
    frame.setParent(main)
    
    canvas = FigureCanvas(fig)
    canvas.setParent(frame)
    canvas.setMinimumSize(100+int(width*1.4), 100+int(height*1.4))
    
    label= QtGui.QLabel()
    label.setText(imageName)   # If it is a string, it must be in unicode eg u"myname"
    label.setAlignment(Qt.AlignHCenter)
    label.setParent(frame)
    
    layout = QtGui.QVBoxLayout()
    layout.addWidget(canvas)
    layout.addWidget(label)
    
    layout.setStretchFactor(canvas, 1.0)

    frame.setLayout(layout)
    frame.show()
    
    main.setCentralWidget(frame)
    main.show()
    
    sys.exit(app.exec_())
    
  else:
    print("Display image: " + str(fn) + " using PySide")
  
    app = QApplication(sys.argv)
      
    height, width, depth= shape(img)   
    fig = Figure(figsize=(width, height), dpi=100)
    
    axes = fig.add_subplot(111)
    axes.set_xlim(0, width)
    axes.set_ylim(0, height)
    axes.imshow(img)
    
    main = QtGui.QMainWindow()
    # Without setGeometry the window will have a default position and size
    main.setGeometry(0, 100, 200+int(width*1.4), 200+int(height*1.4))
    main.setWindowTitle(imageName)  
    
    canvas = FigureCanvas(fig)
    canvas.setParent(main)
    # setMinimumSize prevents the window from becoming tiny and crushing the axes
    canvas.setMinimumSize(100+int(width*1.4), 100+int(height*1.4))
    
    main.setCentralWidget(canvas)
    main.show()
    
    sys.exit(app.exec_())    
