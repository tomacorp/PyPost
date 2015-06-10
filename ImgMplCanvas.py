from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import sys
import os.path
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

class buttonActions:
  def __init__(self):
    self.status= 1
    self.deltaMode= False
    self.statusBarParent= None

  def actionRemoveImg(self):
    print("Removing Image")
    self.img= np.zeros(shape(self.img))
    self.axes.imshow(self.img)
    self.canvas.draw()

  def actionMarker(self):
    print("Add image")
    self.img = skimage.data.imread(self.fn)
    self.axes.imshow(self.img)
    self.canvas.draw()

  def actionClear(self):
    print("By setting a breakpoint here, the image can be manipulated interactively in the debugger")

  def actionMouse(self, event):
    x= event.xdata
    y= event.ydata
    if (x is None or y is None):
      return
    xint= int(x + 0.5)
    yint= int(y + 0.5)
    if self.deltaMode:
      dx= xint - self.zx
      dy= yint - self.zy
      dred= np.int32(self.img[yint][xint][0]) - self.zred
      dgreen= np.int32(self.img[yint][xint][1]) - self.zgreen
      dblue= np.int32(self.img[yint][xint][2]) - self.zblue
      if self.statusBarParent:
        self.statusBarParent.statusBar().showMessage("Abs XY " + str(xint) + ', ' + str(yint) + ', ' + "Delta XY " + str(dx) + ', ' + str(dy) + ': [' + str(dred) + ',' + str(dgreen) + ',' + str(dblue) + ']')
    else:
      if self.statusBarParent:
        self.statusBarParent.statusBar().showMessage(str(xint) + ', ' + str(yint) + ': ' + str(self.img[yint][xint]))

  def actionPickCoords(self, event):
    x= event.xdata
    y= event.ydata
    if (x is None or y is None):
      return
    xint= int(x + 0.5)
    yint= int(y + 0.5)
    if self.statusBarParent:
      self.statusBarParent.statusBar().showMessage(str(xint) + ', ' + str(yint) + ': ' + str(self.img[yint][xint]))
    if event.button == 1:
      if not self.deltaMode:
        print("XY " + str(xint) + ', ' + str(yint) + ': ' + str(self.img[yint][xint]))
      else:
        dx= xint - self.zx
        dy= yint - self.zy
        dred= np.int32(self.img[yint][xint][0]) - self.zred
        dgreen= np.int32(self.img[yint][xint][1]) - self.zgreen
        dblue= np.int32(self.img[yint][xint][2]) - self.zblue
        print("Delta XY " + str(dx) + ', ' + str(dy) + ': [' + str(dred) + ',' + str(dgreen) + ',' + str(dblue) + ']')
    elif event.button == 3:
      if not self.deltaMode:
        print("Zero delta XY is at:" + str(xint) + ', ' + str(yint) + ': ' + str(self.img[yint][xint]))
        self.zx= xint
        self.zy= yint
        self.zred= np.int32(self.img[yint][xint][0])
        self.zgreen= np.int32(self.img[yint][xint][1])
        self.zblue= np.int32(self.img[yint][xint][2])
        self.deltaMode= True
      else:
        self.deltaMode= False

  # This draws a graph on top of the bitmap.
  # Since the axes are what is being drawn, not really the data,
  # Redrawing the bitmap does not cover up the graph, which is drawn
  # in after the bitmap, and so the graph is on top.
  def actionPlot(self):
    print("Plot")
    x= linspace(0,2*pi,100)*20
    y= sin(x/20)*30+40
    self.axes.plot(x, y)
    # self.axes.set_title("Graph", fontsize=12)
    self.canvas.draw()
    self.canvas.show()

  # These delegates connect the callbacks to the program data
  def set_img(self, img):
    self.img= img

  def set_canvas(self, canv):
    self.canvas= canv

  def set_axes(self, ax):
    self.axes= ax

  def set_fn(self, fn):
    self.fn= fn

  def set_fig(self, fig):
    self.fig= fig

  def set_statusBarParent(self, main):
    self.statusBarParent= main


class ImgMplCanvas(FigureCanvas):
  def __init__(self, parent=None, imageName='Image', width=5, height=4, dpi=72):
    self.parent= parent
    self.frame= QtGui.QFrame()
    self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
    self.frame.setParent(self.parent)
    self.statusBar= None

  def getImageName(self, fn):

    """I like a lot of error checking on files.
       getImageName gets the string 'yellow' 'for t/yellow.png'.
       It also checks to see that the file extension matches the file type
       that Python knows how to infer."""

    errmessage= ''
    if not os.path.isfile(fn):
      errmessage="File " + str(fn) + " not found. Bailing out."
      return None
    fileType= imghdr.what(fn)
    fileExtension= '.' + fileType
    if (fn.endswith(fileExtension)):
      imageName= ntpath.basename(fn)
      imageName, extension= os.path.splitext(imageName)
    else:
      errmessage= "File extension " + str(fileExtension) + " does not match file type " + str(fileType)
      return None
    return imageName

  def displayImagePySideFrame(fn, imageName='image'):
    """
    This adds a QFrame and QLabel to the PySide interface, and a simple layout.
    """
    print("Display image: " + str(fn) + " with frame and label using PySide")
    img= skimage.data.imread(fn)

    app = QApplication(sys.argv)

    height, width, depth= shape(img)
    fig = Figure(figsize=(width, height), dpi=72)

    axes = fig.add_subplot(111)
    axes.set_xlim(0, width - 1)
    axes.set_ylim(0, height - 1)
    axes.imshow(img)

    main = QtGui.QMainWindow()
    main.setGeometry(0, 100, 200+int(width*1.4), 200+int(height*1.4))
    main.setWindowTitle(imageName)

    self.frame= QtGui.QFrame()
    self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
    self.frame.setParent(main)

    canvas = FigureCanvas(fig)
    canvas.setParent(frame)
    canvas.setMinimumSize(100+int(width*1.4), 100+int(height*1.4))

    label= QtGui.QLabel()
    # when calling QtGui.QLabel.setText() with a string, must use unicode eg u"myname"
    label.setText(imageName)
    label.setAlignment(Qt.AlignHCenter)
    label.setParent(frame)

    layout = QtGui.QVBoxLayout()
    layout.addWidget(canvas)
    layout.addWidget(label)

    layout.setStretchFactor(canvas, 1.0)

    self.frame.setLayout(layout)
    self.frame.show()

    main.setCentralWidget(frame)
    main.show()

    sys.exit(app.exec_())

  def displayImagePySideFrameButtons(self, fn, imageName='image'):
    print("Display image: " + str(fn) + " with frame and label using PySide")
    img= skimage.data.imread(fn)
    height, width, depth= shape(img)
    fig = Figure(figsize=(width, height), dpi=72)

    axes = fig.add_subplot(111)
    axes.set_xlim(0, width - 1)
    axes.set_ylim(0, height - 1)
    axes.set_title("Layout", fontsize=12)
    axes.imshow(img)

    """
      This adds a QFrame and QLabel to the PySide interface, and a simple layout.
      It also adds buttons to manipulate the image.
    """

    canvas = FigureCanvas(fig)
    canvas.setParent(self.frame)
    canvas.setMinimumSize(100+int(width*1.4), 100+int(height*1.4))

    label= QtGui.QLabel()
    # when calling QtGui.QLabel.setText() with a string, must use unicode eg u"myname"
    label.setText(imageName)
    label.setAlignment(Qt.AlignHCenter)
    label.setParent(self.frame)

    # Buttons
    groupBox = QtGui.QGroupBox("Canvas Control Buttons")
    button1= QtGui.QPushButton("Remove")
    button2= QtGui.QPushButton("Restore")
    button3= QtGui.QPushButton("Clear")
    button4= QtGui.QPushButton("Plot")
    # Button actions need to be in self to keep a reference to them.
    # The reference in mpl_connect must be weak, I guess.
    self.bActions= buttonActions()
    self.bActions.set_img(img)
    self.bActions.set_canvas(canvas)
    self.bActions.set_axes(axes)
    self.bActions.set_fn(fn)
    self.bActions.set_fig(fig)
    if self.statusBar:
      self.bActions.set_statusBarParent(self.statusBar)
    button1.clicked.connect(self.bActions.actionRemoveImg)
    button2.clicked.connect(self.bActions.actionMarker)
    button3.clicked.connect(self.bActions.actionClear)
    button4.clicked.connect(self.bActions.actionPlot)
    vbox = QHBoxLayout()
    vbox.addWidget(button1)
    vbox.addWidget(button2)
    vbox.addWidget(button3)
    vbox.addWidget(button4)
    vbox.addStretch(1)
    groupBox.setLayout(vbox)
    # End of Buttons

    canvas.mpl_connect('motion_notify_event', self.bActions.actionMouse)
    canvas.mpl_connect('button_release_event', self.bActions.actionPickCoords)

    layout = QtGui.QVBoxLayout()
    layout.addWidget(canvas)
    layout.addWidget(label)
    layout.addWidget(groupBox)

    layout.setStretchFactor(canvas, 1.0)

    self.frame.setLayout(layout)
    self.frame.show()

  def setStatusBar(self, main):
    self.statusBar= main

# The test starts here
if __name__ == "__main__":
  from matplotlib import pyplot as plt
  import numpy as np
  print("ImgMplCanvas class test")

  app = QApplication(sys.argv)

  main = QtGui.QMainWindow()

  # The file is in a subdirectory of the run directory.
  fn= 't/yellow.png'
  imgCanvas= ImgMplCanvas(parent=main)
  name = imgCanvas.getImageName(fn)
  if name == None:
    print("File " + str(fn) + " not okay. Bailing out.")
    sys.exit()

  width= 400
  height=300

  main.setGeometry(0, 100, 200+int(width*1.4), 200+int(height*1.4))
  main.setWindowTitle(name)
  main.statusBar().showMessage('Loading...')

  imgCanvas.setStatusBar(main)
  imgCanvas.displayImagePySideFrameButtons(fn, imageName=name)

  main.setCentralWidget(imgCanvas.frame)
  main.statusBar().showMessage('Ready')
  main.show()

  sys.exit(app.exec_())
