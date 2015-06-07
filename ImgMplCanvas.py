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

if __name__ == "__main__":

  import os.path
  from matplotlib import pyplot as plt

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

  def displayImageTk(fn, imageName='image'):
    """
    This is the easy pyplot way to display an image.
    It also has some nice features, like panning and zooming.
    It is not the PySide way of doing things,
    but it makes a nice reference for debugging.
    """
    print("Display image: " + str(fn) + " using Tk")
    img= skimage.data.imread(fn)
    plt.imshow(img)
    plt.show()

  def displayImagePyside(fn, imageName='image'):
    """
    This is the simplest way to use PySide to display an image in a Figure subplot.
    There is no layout code, other than hand-coding based on the size of the image.
    """
    print("Display image: " + str(fn) + " using PySide")
    img= skimage.data.imread(fn)

    app = QApplication(sys.argv)

    height, width, depth= shape(img)
    fig = Figure(figsize=(width, height), dpi=100)

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

  def displayImagePysideFrame(fn, imageName='image'):
    """
    This adds a QFrame and QLabel to the PySide interface, and a simple layout.
    """
    print("Display image: " + str(fn) + " with frame and label using PySide")
    img= skimage.data.imread(fn)

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


  # The test starts here
  print("ImgMplCanvas class test")

  # Non-OO code, use a global error message:
  errmessage= ''

  # The file is in a subdirectory of the run directory.
  fn= 't/yellow.png'

  name = getImageName(fn)
  if name == None:
    print(errmessage)
    sys.exit()

  useTk= False
  useFrame= False

  if useTk:
    displayImageTk(fn, imageName=name)
  elif useFrame:
    displayImagePysideFrame(fn, imageName=name)
  else:
    displayImagePyside(fn, imageName=name)
