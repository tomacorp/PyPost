from matplotlib import pyplot
import numpy as np

class EngMarker:
  def __init__(self, canvas=None):
    if canvas != None:
      self.sc = canvas	
    else:
      print("No canvas found to initialize marker")
      return
    
    self.sc.mpl_connect('button_press_event', self.onClick)
    self.markers = []
    self.fig = self.sc.figure
    self.nSubPlots = len(self.fig.axes)  
    self.retVal= {}
    print("Number of subplot: " + str(self.nSubPlots))
      
  def onClick(self, event):
    print("Click!")
    if event.button == 1:				
      # self.clearMarker()
      for i in range(self.nSubPlots):
        # subPlot = self.selectSubPlot(i)
	thisfig= self.sc.plt.get_figure()
	
	# .plot(event.xdata, event.ydata, color='r') 							
        pyplot.axvline(event.xdata, 0, 1, linestyle='--', linewidth=2, color='gray')
        # self.markers.append(marker)
  
      self.fig.canvas.draw()
      # self.retVal['subPlot'] = subPlotNr
      self.retVal['subPlot'] = 0
      self.retVal['x'] = event.xdata
      self.retVal['y'] = event.ydata 
      
  def selectSubPlot(self, i):

    """
    Select a subplot

    Arguments:
    i -- the nr of the subplot to select
    
    Returns:
    A subplot
    """

    pyplot.subplot('%d1%d' % (self.nSubPlots, i+1))
    return self.fig.axes[i]  