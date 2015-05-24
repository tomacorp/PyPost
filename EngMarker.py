
import numpy as np

class EngMarker:
  def __init__(self, canvas, _globals):
    self.sc = canvas
    self.sc.mpl_connect('axes_enter_event', self.inAxis)
    self.sc.mpl_connect('axes_leave_event', self.outAxis)
    self.sc.mpl_connect('figure_enter_event', self.inFigure)
    self.sc.mpl_connect('figure_leave_event', self.outFigure)
    self.fig = self.sc.figure
    self.retVal= {}
    self.markerX= None
    self.markerY= None
    self._globals= _globals;
    self.pickpoints= None
    self.pickline= None
    self.pick_event_id= None
    self.button_press_event_id= None
    self.scroll_event_id= None
    self.figure_scroll_event_id= None

  def inAxis(self, event):
    self.pick_event_id= self.sc.mpl_connect('pick_event', self.onPick)
    self.button_press_event_id= self.sc.mpl_connect('button_press_event', self.onClick)
    self.scroll_event_id= self.sc.mpl_connect('scroll_event', self.onScroll)
    self.sc.mpl_disconnect(self.figure_scroll_event_id)

  def outAxis(self, event):
    self.sc.mpl_disconnect(self.pick_event_id)
    self.sc.mpl_disconnect(self.button_press_event_id)
    self.sc.mpl_disconnect(self.scroll_event_id)
    self.figure_scroll_event_id= self.sc.mpl_connect('scroll_event', self.onFigureScroll)
    # print("inFigure")

  def inFigure(self, event):
    self.figure_scroll_event_id= self.sc.mpl_connect('scroll_event', self.onFigureScroll)
    # print("inFigure")

  def outFigure(self, event):
    self.sc.mpl_disconnect(self.figure_scroll_event_id)
    # print("outFigure")

  def onFigureScroll(self, event):
    yr= event.y/self.sc.height()
    # print("onFigure scroll " + str(yr))
    if (abs(event.step) > 0):
      if yr < 0.2:
        self.sc.plt.yaxis.pan(event.step)
      elif yr > 0.8:
        self.sc.plt.yaxis.pan(event.step)
      else:
        self.sc.plt.yaxis.zoom(event.step)
      self.fig.canvas.draw()

  def onScroll(self, event):
    x= event.xdata
    y= event.ydata
    xbound= self.sc.plt.get_xbound()
    ybound= self.sc.plt.get_ybound()
    if (x is None or y is None or xbound is None or ybound is None):
      return None
    if (xbound[0] == xbound[1] or ybound[0] == ybound[1]):
      return None
    xr= abs((x-xbound[0])/(xbound[1] - xbound[0]))
    yr= abs((y-ybound[0])/(ybound[1] - ybound[0]))
    # print("x: "+ str(x) + "y: " + str(y))
    # print("xr: " + str(xr) + ' yr: ' + str(yr))
    if (event.step > 0):
      # print("Zoom in from " + str(xr) + ", " + str(yr))
      if (xr < 0.25):
        self.sc.plt.xaxis.pan(-1)
      elif (xr > 0.75):
        self.sc.plt.xaxis.pan(1)
      else:
        self.sc.plt.xaxis.zoom(1)
    elif (event.step < 0):
      # print("Zoom out from " + str(xr) + ", " + str(yr))
      if (xr < 0.25):
        self.sc.plt.xaxis.pan(1)
      elif (xr > 0.75):
        self.sc.plt.xaxis.pan(-1)
      else:
        self.sc.plt.xaxis.zoom(-1)
    self.fig.canvas.draw()
    return None

  def onPick(self, event):
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
      self.markerX= x
      self.markerY= y
      self._globals['markerX']= x
      self._globals['markerY']= y
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
