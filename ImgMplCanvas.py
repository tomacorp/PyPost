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
  def __init__(self, parent=None, width=5, height=4, dpi=72):
    pass


if __name__ == "__main__":

  import os.path
  from matplotlib import pyplot as plt
  import numpy as np

  def getImageName(fn):

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

  # gist
  def displayImagePyplot(fn, imageName='image'):
    """
    This is the easy pyplot way to display an image.
    It also has some nice features, like panning and zooming.
    It is not as extensible as PySide,
    but it makes a nice reference for debugging.
    """
    print("Display image: " + str(fn) + " using pyplot")
    img= skimage.data.imread(fn)
    plt.imshow(img)
    plt.show()

  # gist
  def displayImagePySide(fn, imageName='image'):
    """
    This is the simplest way to use PySide to display an image in a Figure subplot.
    There is no layout code, other than hand-coding the FigureCanvas size and
    QMainWindow size based on the size of the image.
    """
    print("Display image: " + str(fn) + " using PySide")
    img= skimage.data.imread(fn)

    app = QApplication(sys.argv)

    height, width, depth= shape(img)
    fig = Figure(figsize=(width, height), dpi=72)

    axes = fig.add_subplot(111)
    # The next two lines are equivalent to the default axes settings
    #   axes.set_xlim(0, width)
    #   axes.set_ylim(0, height)
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

  # gist
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
    # when calling QtGui.QLabel.setText() with a string, must use unicode eg u"myname"
    label.setText(imageName)
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


    """
      This adds a QFrame and QLabel to the PySide interface, and a simple layout.

      It also adds buttons to manipulate the image.

      Once there are buttons, simple things like exiting or printing can be done as long
      as they don't need much interaction program variables.
      If there are actions that work on variables, objects and classes are needed.

      This is the explosion of complexity that accompanies the manipulation of
      program state.

      Will an inner class will work to keep the example tidy?
      Yes, if lots of delegates counts as tidy.
    """


  def displayImagePySideFrameButtons(fn, imageName='image'):
    print("Display image: " + str(fn) + " with frame and label using PySide")

    """
      These definitions can be local inside the function like this or outside.
      Both work.
    """
    class buttonActions:
      def __init__(self):
        self.status= 1

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
        main.statusBar().showMessage(str(xint) + ', ' + str(yint))

      def actionPickCoords(self, event):
        x= event.xdata
        y= event.ydata
        if (x is None or y is None):
          return
        xint= int(x + 0.5)
        yint= int(y + 0.5)
        main.statusBar().showMessage(str(xint) + ', ' + str(yint))
        if event.button == 1:
          print("XY " + str(xint) + ', ' + str(yint))


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

      def set_main(self, main):
        self.main= main

    img= skimage.data.imread(fn)

    app = QApplication(sys.argv)

    height, width, depth= shape(img)
    fig = Figure(figsize=(width, height), dpi=72)

    axes = fig.add_subplot(111)
    axes.set_xlim(0, width)
    axes.set_ylim(0, height)
    axes.set_title("Layout", fontsize=12)
    axes.imshow(img)

    main = QtGui.QMainWindow()
    main.setGeometry(0, 100, 200+int(width*1.4), 200+int(height*1.4))
    main.setWindowTitle(imageName)
    main.statusBar().showMessage('Loading...')

    frame= QtGui.QFrame()
    frame.setFrameShape(QtGui.QFrame.StyledPanel)
    frame.setParent(main)

    """
    This adds a QFrame and QLabel to the PySide interface, and a simple layout.
    It also adds buttons to manipulate the image.
    """

    canvas = FigureCanvas(fig)
    canvas.setParent(frame)
    canvas.setMinimumSize(100+int(width*1.4), 100+int(height*1.4))

    label= QtGui.QLabel()
    # when calling QtGui.QLabel.setText() with a string, must use unicode eg u"myname"
    label.setText(imageName)
    label.setAlignment(Qt.AlignHCenter)
    label.setParent(frame)

    # Buttons
    groupBox = QtGui.QGroupBox("Canvas Control Buttons")
    button1= QtGui.QPushButton("Remove")
    button2= QtGui.QPushButton("Restore")
    button3= QtGui.QPushButton("Clear")
    button4= QtGui.QPushButton("Plot")
    bActions= buttonActions()
    bActions.set_img(img)
    bActions.set_canvas(canvas)
    bActions.set_axes(axes)
    bActions.set_fn(fn)
    bActions.set_fig(fig)
    bActions.set_main(main)
    button1.clicked.connect(bActions.actionRemoveImg)
    button2.clicked.connect(bActions.actionMarker)
    button3.clicked.connect(bActions.actionClear)
    button4.clicked.connect(bActions.actionPlot)
    vbox = QHBoxLayout()
    vbox.addWidget(button1)
    vbox.addWidget(button2)
    vbox.addWidget(button3)
    vbox.addWidget(button4)
    vbox.addStretch(1)
    groupBox.setLayout(vbox)
    # End of Buttons

    canvas.mpl_connect('motion_notify_event', bActions.actionMouse)
    canvas.mpl_connect('button_release_event', bActions.actionPickCoords)

    layout = QtGui.QVBoxLayout()
    layout.addWidget(canvas)
    layout.addWidget(label)
    layout.addWidget(groupBox)

    layout.setStretchFactor(canvas, 1.0)

    frame.setLayout(layout)
    frame.show()

    main.setCentralWidget(frame)
    main.statusBar().showMessage('Ready')
    main.show()

    sys.exit(app.exec_())


  # The test starts here
  print("ImgMplCanvas class test")

  # The file is in a subdirectory of the run directory.
  fn= 't/yellow.png'

  name = getImageName(fn)
  if name == None:
    print("File " + str(fn) + " not okay. Bailing out.")
    sys.exit()

  useTk= False
  useFrame= False
  useNoFrame= False

  if useTk:
    displayImagePyplot(fn, imageName=name)
  elif useFrame:
    displayImagePySideFrame(fn, imageName=name)
  elif useNoFrame:
    displayImagePySide(fn, imageName=name)
  else:
    displayImagePySideFrameButtons(fn, imageName=name)

