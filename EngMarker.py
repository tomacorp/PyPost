
import numpy as np

# This is a controller that translates mouse events into actions
# for markers, zoom, and scrolling.

# TODO: Use engineering notation for marker annotation
# TODO: Add more measurements
#         Risetime
#         Overshoot
#         3dB bandwidth of bandpass
#         3dB bandwidth of lowpass
#         Shape factor
#         Ringing frequency
#         Oscillator frequency
#         Delay
# TODO: Marker that follows mouse pointer

class EngMarker:
  def __init__(self, canvas):
    self.sc = canvas

    self.sc.mpl_connect('axes_enter_event', self.inGraphingArea)
    self.sc.mpl_connect('axes_leave_event', self.outGraphingArea)
    self.sc.mpl_connect('figure_enter_event', self.inGraphingMargin)
    self.sc.mpl_connect('figure_leave_event', self.outGraphingMargin)

    self.fig = self.sc.figure
    self.retVal= {}
    #self.markerX= None
    #self.markerY= None

    self.markerDelegate= None

    self.pickpoints= None
    self.pickline= None
    self.pick_event_id= None
    self.button_press_event_id= None
    self.scroll_event_id= None
    self.figure_scroll_event_id= None

  def inGraphingArea(self, event):
    self.pick_event_id= self.sc.mpl_connect('pick_event', self.onPick)
    self.button_press_event_id= self.sc.mpl_connect('button_press_event', self.onClick)
    self.scroll_event_id= self.sc.mpl_connect('scroll_event', self.onScroll)
    self.sc.mpl_disconnect(self.figure_scroll_event_id)

  def outGraphingArea(self, event):
    self.sc.mpl_disconnect(self.pick_event_id)
    self.sc.mpl_disconnect(self.button_press_event_id)
    self.sc.mpl_disconnect(self.scroll_event_id)
    self.figure_scroll_event_id= self.sc.mpl_connect('scroll_event', self.onFigureScroll)

  def inGraphingMargin(self, event):
    self.figure_scroll_event_id= self.sc.mpl_connect('scroll_event', self.onFigureScroll)

  def outGraphingMargin(self, event):
    self.sc.mpl_disconnect(self.figure_scroll_event_id)

  def onFigureScroll(self, event):
    """
    The Y axis is scrolled on the margin outside the graph area.
    The top and bottom areas cause graph panning.
    The middle areas on the sides cause zooming.
    """
    yratio= event.y/self.sc.height()
    if (abs(event.step) > 0):
      if yratio < 0.2:
        self.sc.plt.yaxis.pan(event.step)
      elif yratio > 0.8:
        self.sc.plt.yaxis.pan(event.step)
      else:
        self.sc.plt.yaxis.zoom(event.step)
      self.fig.canvas.draw()

  def onScroll(self, event):
    """
    This X axis is scrolled on the graph.
    Scroll commands on the left and right side of the graph cause panning.
    Scroll commands on the center of the graph cause zooming.
    """
    x= event.xdata
    y= event.ydata
    xbound= self.sc.plt.get_xbound()
    ybound= self.sc.plt.get_ybound()
    if (x is None or y is None or xbound is None or ybound is None):
      return None
    if (xbound[0] == xbound[1] or ybound[0] == ybound[1]):
      return None
    xratio= abs((x-xbound[0])/(xbound[1] - xbound[0]))
    # yr= abs((y-ybound[0])/(ybound[1] - ybound[0]))
    if (event.step > 0):
      if (xratio < 0.25):
        self.sc.plt.xaxis.pan(-1)
      elif (xratio > 0.75):
        self.sc.plt.xaxis.pan(1)
      else:
        self.sc.plt.xaxis.zoom(1)
    elif (event.step < 0):
      if (xratio < 0.25):
        self.sc.plt.xaxis.pan(1)
      elif (xratio > 0.75):
        self.sc.plt.xaxis.pan(-1)
      else:
        self.sc.plt.xaxis.zoom(-1)
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
      self.sc.plt.text(x, y, '.')
      self.sc.plt.annotate(str(x)+","+str(y), xy=(x,y), xytext=(x,y+1), arrowprops=dict(arrowstyle="->"))
      print("Snap to " + str(x) + ', ' + str(y))
      l= self.sc.plt.axvline(x=event.xdata, linewidth=1, color='b')
      self.fig.canvas.draw()
      if self.sc.commandDelegate.get_markerX() is not None:
        self.sc.commandDelegate.set_deltaMarkerX(x - self.sc.commandDelegate.get_markerX())
      if self.sc.commandDelegate.get_markerY() is not None:
        self.sc.commandDelegate.set_deltaMarkerY(y - self.sc.commandDelegate.get_markerY())
      self.sc.commandDelegate.set_markerX(x)
      self.sc.commandDelegate.set_markerY(y)
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
