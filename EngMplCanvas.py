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
from matplotlib.ticker import EngFormatter

 #TODO: Use engineering notation for marker annotation
 #       Remove space between number and engineering letter
 #       Greek mu is missing
 #TODO: Add more measurements
         #Risetime
         #Overshoot
         #3dB bandwidth of bandpass
         #3dB bandwidth of lowpass
         #Shape factor
         #Ringing frequency
         #Oscillator frequency
         #Delay
         #Resampling to fixed time steps with various interpolators
         #Windowing functions
         #FFT
 #TODO: Marker that follows mouse pointer

class EngMplCanvas(FigureCanvas):
  """A QWidget that implements Matplotlib"""
  def __init__(self, parent=None, width=5, height=4, dpi=72):

    self.yauto= True
    self.ylimlow= -16.0
    self.ylimhigh= 16.0
    self.xauto= True
    self.xlimlow= 0.0
    self.xlimhigh= 0.02
    self.fsz= 12
    self.xlabel= 'X'
    self.ylabel= 'Y'
    self.title= 'title'
    self.name= ''
    # self.xvar stores the name of the Command Interpreter's variable for the x-axis.
    # This is used so that the graphing window contains the graph state
    # needed by the CommandInterp, which might vary from graph to graph.
    self.xvar= 't'

    self.commandDelegate= None

    self.fig = Figure(figsize=(width, height), dpi=dpi)
    self.plt = self.fig.add_subplot(111)

    FigureCanvas.__init__(self, self.fig)

    self.fig.tight_layout(pad=1.5, w_pad=0.0, h_pad=0.0)

    FigureCanvas.setSizePolicy(self,
                               QSizePolicy.Expanding,
                               QSizePolicy.Expanding)
    FigureCanvas.updateGeometry(self)

    self.mpl_connect('axes_enter_event', self.inGraphingArea)
    self.mpl_connect('axes_leave_event', self.outGraphingArea)
    self.mpl_connect('figure_enter_event', self.inGraphingMargin)
    self.mpl_connect('figure_leave_event', self.outGraphingMargin)

    self.pickpoints= None
    self.pickline= None
    self.pick_event_id= None
    self.button_press_event_id= None
    self.scroll_event_id= None
    self.figure_scroll_event_id= None

    self.formatter = EngFormatter(unit='', places=1)

  def plotYList(self, res, arg, title):
    if len(res) == 0:
      print("No data found for " + str(title))
      return    
    self.plt.plot(res)
    self.plt.set_xlabel('Index', fontsize=self.fsz,picker=5)
    self.plt.set_ylabel(arg, fontsize=self.fsz)
    self.plt.set_title(title, fontsize=self.fsz)
    self.setAutoscale()
    self.plt.xaxis.set_major_formatter(self.formatter)
    self.plt.yaxis.set_major_formatter(self.formatter)
    self.draw()
    self.show()

  def plotXYList(self, x, y, xlabel, ylabel, title):
    if len(y) == 0:
      print("No data found for " + str(ylabel))
      return    
    self.plt.plot(x, y, picker=5)
    self.plt.set_xlabel(xlabel, fontsize=self.fsz)
    self.plt.set_ylabel(ylabel, fontsize=self.fsz)
    self.plt.set_title(title, fontsize=self.fsz)
    self.plt.xaxis.set_major_formatter(self.formatter)
    self.plt.yaxis.set_major_formatter(self.formatter)
    self.setAutoscale()
    self.draw()
    self.show()

  def setAutoscale(self):
    if self.yauto:
      self.plt.set_autoscaley_on(True)
      self.ylimlow, self.ylimhigh= self.plt.get_ylim()
    else:
      self.plt.set_autoscaley_on(False)
      self.ylimlow, self.ylimhigh= self.plt.set_ylim(self.ylimlow, self.ylimhigh)
    if self.xauto:
      self.plt.set_autoscalex_on(True)
      self.xlimlow, self.xlimhigh= self.plt.get_xlim()
    else:
      self.plt.set_autoscalex_on(False)
      self.xlimlow, self.xlimhigh= self.plt.set_xlim(self.xlimlow, self.xlimhigh)

  def inGraphingArea(self, event):
    self.pick_event_id= self.mpl_connect('pick_event', self.onPick)
    self.button_press_event_id= self.mpl_connect('button_press_event', self.onClick)
    self.scroll_event_id= self.mpl_connect('scroll_event', self.onScroll)
    self.mpl_disconnect(self.figure_scroll_event_id)

  def outGraphingArea(self, event):
    self.mpl_disconnect(self.pick_event_id)
    self.mpl_disconnect(self.button_press_event_id)
    self.mpl_disconnect(self.scroll_event_id)
    self.figure_scroll_event_id= self.mpl_connect('scroll_event', self.onFigureScroll)

  def inGraphingMargin(self, event):
    self.figure_scroll_event_id= self.mpl_connect('scroll_event', self.onFigureScroll)

  def outGraphingMargin(self, event):
    self.xlimlow, self.xlimhigh= self.plt.get_xlim()
    self.ylimlow, self.ylimhigh= self.plt.get_ylim()
    self.mpl_disconnect(self.figure_scroll_event_id)

  def onFigureScroll(self, event):
    """
    The Y axis is scrolled on the margin outside the graph area.
    The top and bottom areas cause graph panning.
    The middle areas on the sides cause zooming.
    """
    yratio= event.y/self.height()
    if (abs(event.step) > 0):
      if yratio < 0.2:
        self.plt.yaxis.pan(event.step)
      elif yratio > 0.8:
        self.plt.yaxis.pan(event.step)
      else:
        self.plt.yaxis.zoom(event.step)
      self.fig.canvas.draw()

  def onScroll(self, event):
    """
    This X axis is scrolled on the graph.
    Scroll commands on the left and right side of the graph cause panning.
    Scroll commands on the center of the graph cause zooming.
    """
    x= event.xdata
    y= event.ydata
    xbound= self.plt.get_xbound()
    ybound= self.plt.get_ybound()
    if (x is None or y is None or xbound is None or ybound is None):
      return None
    if (xbound[0] == xbound[1] or ybound[0] == ybound[1]):
      return None
    xratio= abs((x-xbound[0])/(xbound[1] - xbound[0]))
    # yr= abs((y-ybound[0])/(ybound[1] - ybound[0]))
    if (event.step > 0):
      if (xratio < 0.25):
        self.plt.xaxis.pan(-1)
      elif (xratio > 0.75):
        self.plt.xaxis.pan(1)
      else:
        self.plt.xaxis.zoom(1)
    elif (event.step < 0):
      if (xratio < 0.25):
        self.plt.xaxis.pan(1)
      elif (xratio > 0.75):
        self.plt.xaxis.pan(-1)
      else:
        self.plt.xaxis.zoom(-1)
    self.fig.canvas.draw()
    return None

  def onPick(self, event):
    """
    The pick event causes a selection of nearby points to be selected.
    However, the exact location of the pick is not known.
    The onClick method is used to find the exact location, and the closest
    point is chosen from the list provided by onPick()
    """
    pickline = event.artist
    pickLineData = pickline.get_xydata()
    self.pickpoints= pickLineData[event.ind]

  def onClick(self, event):
    if event.button == 1:
      xe = event.xdata
      ye = event.ydata
      if (xe is None or ye is None):
        return None
      print("Click at " + str(xe) + ', ' + str(ye))
      value= (xe,ye)
      if self.pickpoints is None:
        return None
      x,y = self.find_nearest_pt(self.pickpoints, value)
      if (x is None):
        return None
      self.plt.text(x, y, '.')
      self.plt.annotate(str(x)+","+str(y), xy=(x,y), xytext=(x,y+1), arrowprops=dict(arrowstyle="->"))
      print("Snap to " + str(x) + ', ' + str(y))
      l= self.plt.axvline(x=event.xdata, linewidth=1, color='b')
      self.fig.canvas.draw()
      if self.commandDelegate.get_markerX() is not None:
        self.commandDelegate.set_deltaMarkerX(x - self.commandDelegate.get_markerX())
      if self.commandDelegate.get_markerY() is not None:
        self.commandDelegate.set_deltaMarkerY(y - self.commandDelegate.get_markerY())
      self.commandDelegate.set_markerX(x)
      self.commandDelegate.set_markerY(y)
      self.pickpoints= None
    return None

  def find_nearest_pt(self, array, value):
    mindist= abs(array[0][0]-value[0])
    x= array[0][0]
    y= array[0][1]
    idx= 0
    minidx= idx
    for pt in array:
      dist= abs(pt[0]-value[0])
      if dist < mindist:
        minidx= idx
        mindist= dist
        x= pt[0]
        y= pt[1]
      idx += 1
    if (idx == 0):
      return None, None
    return x, y


  # This allows the graph to send changes back to the controller.

  def setCommandDelegate(self, obj):
    self.commandDelegate= obj

  # These methods implement delegating graphics calls.
  # They get/set the state variables

  def get_xauto(self):
    return self.xauto

  def get_yauto(self):
    return self.yauto

  def get_xlimlow(self):
    return self.xlimlow

  def get_xlimhigh(self):
    return self.xlimhigh

  def get_ylimlow(self):
    return self.ylimlow

  def get_ylimhigh(self):
    return self.ylimhigh

  def get_xlabel(self):
    return self.xlabel

  def get_ylabel(self):
    return self.ylabel

  def get_title(self):
    return self.title

  def get_xvar(self):
    return self.xvar

  def get_name(self):
    return self.name


  def set_xauto(self, s):
    self.xauto= s

  def set_yauto(self, s):
    self.yauto= s

  def set_xlimlow(self, s):
    self.xlimlow= s

  def set_xlimhigh(self, s):
    self.xlimhigh= s

  def set_ylimlow(self, s):
    self.ylimlow= s

  def set_ylimhigh(self, s):
    self.ylimhigh= s

  def set_xlabel(self, s):
    self.xlabel= s

  def set_ylabel(self, s):
    self.ylabel= s

  def set_title(self, s):
    self.title= s

  def set_xvar(self, s):
    self.xvar= s
