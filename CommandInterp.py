import os.path
import PySide.QtCore
from PySide.QtCore import QProcess, QObject, SIGNAL

from math import *
from tokenize import *
from numpy import *
from numpy.fft import *
import skimage
from skimage import data
import imghdr
import ntpath

import re
import numpy as np
import h5py

import EngEvaluate
import ReadSpiceRaw
import SpiceVarExpr
import ImgMplCanvas

# di     show available vars from raw file
# show   list user-assigned variables
# push   go into raw file subcircuit
# pop    exit subcircuit
# gs     graph on same axes

# set ylin
# set ylog
# set xl 1k 10k
# label time, date
# ticks, grid, number of divisions

# TODO: Look at how subcircuits are implemented for di and voltage graphing, consider push/pop

# TODO: 
#       implement HDF5 file reader
#       implement Python program output as transcript
#       implement save-all as ascii
#       implement restore-all as ascii
#       save state from one run to the next
#       command to reset state to default
#       implement gr x .vs y
#       implement freq instead of time as an axis, vdb, idb, vm, im
#       AC analysis - complex numbers from raw file
#       2D plots for thermal solutions
#       Add web server to inject remote commands via http
#       gr 3
#         Can't get length of integer.
#         Needs to check that expr is an array, or better extend int to array.
#       NGSpice raw file has all the waveform names in lower case.
#         Would like option to make graphing them case insensitive.
#       Path to NGSpice should be configured in a pull-down from the Main Window.

# Layout for canvas: http://matplotlib.org/users/tight_layout_guide.html

class CommandInterp:
  def __init__(self):

    # TODO: Move xvar to graphics delegate

    self._globals= globals()
    self.evaluator= EngEvaluate.EngEvaluate(self._globals)
    self.pyCode= ''
    self.sve= SpiceVarExpr.SpiceVarExpr()

    # Move to simulator delegate
    self.rawFileName= ''
    self.spiceFileName= ''
    self.simulationBaseName= ''
    
    self.lastGraphCommand1= ''
    self.lastGraphCommand2= ''

    # Move to graphics delegate
    #self.xvar= 't'
    #self.title=''
    return

  def executeCmd(self, cmdText):
    cmdText=cmdText.rstrip()
    cmdText=cmdText.lstrip()
    print("Command: " + cmdText)
    message= ''
    longCmd= re.match(r'^(ci|gr|gs|set|si|history|readh5|include|\.|img|delete) (.*)', cmdText)
    shortCmd= re.match(r'^(ci|set|si|di|history|autoscale)$', cmdText)
    if longCmd is not None:
      message= self.executeLongCommand(longCmd, cmdText)
    elif shortCmd is not None:
      message= self.executeShortCommand(shortCmd)
    else:
      cmdText= self.sve.fixWaveFormVariableNames(cmdText)
      message= self.evaluator.evaluate(cmdText)
      self.pyCode= self.evaluator.logPyCode
    return message

  def executeShortCommand(self, shortCmd):
    message= ''
    cmd= shortCmd.group(1)
    if cmd == 'ci':
      if self.simulationBaseName == '':
        message= "No simulation specified"
        self.pyCode= ''
      else:
        message= "Circuit is: " + self.simulationBaseName
        self.pyCode= "sim.setCircuitName(" + self.simulationBaseName + ")"

    elif cmd == 'set':
      message = self.showSettings()
      self.pyCode= ''

    elif cmd == 'si':
      if self.simulationBaseName != '':
        self.pyCode= "sim.simulate()"
        message= self.simulate('')
        self.readRawFile()
      else:
        message= "Circuit name has not been set yet"

    elif cmd == 'di':
      message = self.displaySweepVar()
      message = message + self.displayVoltages()
      message = message + self.displayCurrents()
      self.pyCode= "print(r.getVoltageNames())\nprint(r.getCurrentNames())"

    elif cmd == 'history':
      print "History not implemented yet."
      
    elif cmd == 'autoscale':
      print "Autoscale last curve on this graph"
      self.sc.setAutoscale()
      self.sc.plt.hold(False)
      if (self.lastGraphCommand1 != ""):
        self.graphExpr(self.lastGraphCommand1, self.lastGraphCommand2)
      self.pyCode= "graph.setAutoscale()\ngraphExpr('" + str(self.lastGraphCommand2) + "')"

    return message

  def showSettings(self):
    self.pyCode= ''
    message = "Parameters are:\n  Sweep variable: " + str(self.sc.get_xvar())
    message += "\n  Title: " + str(self.sc.get_title())

    xLimitsMessage= "auto"
    if not self.sc.get_xauto():
      xLimitsMessage= str(self.sc.get_xlimlow()) + " " + str(self.sc.get_xlimhigh())
    message += "\n  X Limits: " + xLimitsMessage

    yLimitsMessage= "auto"
    if not self.sc.yauto:
      yLimitsMessage= str(self.sc.get_ylimlow()) + " " + str(self.sc.get_ylimhigh())
    message += "\n  Y Limits: " + yLimitsMessage

    currentCanvasName= self.sc.get_name()
    message += "\n  Current graph name: " + str(currentCanvasName)

    return message

  def displaySweepVar(self):
    if self.sc.get_xvar() is not None:
      message= "Sweep variable: " + str(self.sc.get_xvar()) + "\n"
    else:
      message= "# No sweep variable\n"
    return message

  def displayVoltages(self):
    if 'r' in globals() and r is not None:
      message= ''
      for voltage in r.getVoltageNames():
        message= message + "v(" + str(voltage) + ")\n"
    else:
      message= "# No voltage variables\n"
    return message

  def displayCurrents(self):
    if 'r' in globals() and r is not None:
      message= ''
      for voltage in r.getCurrentNames():
        message = message + "i(" + str(voltage) + ")\n"
    else:
      message= "# No current variables\n"
    return message

  def executeLongCommand(self, longCmd, cmdText):
    cmd= longCmd.group(1)
    arg= longCmd.group(2)
    self.pyCode= ''
    message= ''
    if cmd == 'si':
      self.pyCode= "sim.setCircuitName(" + str(arg) + ")\nsim.simulate()"
      message= self.setCircuitName(arg)
      message= message + "\n" + self.simulate(arg)
    elif cmd == 'ci':
      self.pyCode= "sim.setCircuitName(" + str(arg) + ")"
      message= self.setCircuitName(arg)
      self.readRawFile()
    elif cmd == 'gr':
      self.sc.plt.hold(False)
      message= self.graphExpr(arg, cmdText)
      if message == '':
        self.pyCode= "graph.graph("+ self.evaluator.logPyCode + ")"
        self.lastGraphCommand1= str(arg)
        self.lastGraphCommand2= str(cmdText)
      else:
        print(message)
        self.pyCode= "# " + message
    elif cmd == 'gs':
      self.sc.plt.hold(True)
      message= self.graphExpr(arg, cmdText)
      if message == '':
        self.pyCode= "graph.graphSameAxes("+ self.evaluator.logPyCode + ")"
        self.lastGraphCommand1= str(arg)
        self.lastGraphCommand2= str(cmdText)
      else:
        print(message)
        self.pyCode= "# " + message
    elif cmd == 'set':
      self.setPostParameter(arg)
      # self.pyCode= "graph.set(" + arg + ")"
    elif cmd == 'history':
      print "History not implemented yet."
    elif cmd == 'readh5':
      print("Read hdf5 file: " + arg)
      if os.path.isfile(arg):
        self._globals['h']= h5py.File(arg, "r")
        self.pyCode= 'h= h5py.File(' + arg + ', "r")'
      else:
        message= 'file "' + arg + '" not found'
        print(message)
        self.pyCode= "# " + message
    elif cmd == 'include' or cmd == '.':
      if os.path.isfile(arg):
        self.include(arg)
        self.pyCode='includeFile(' + arg + ')'
      else:
        message= 'Include file "' + arg + '" not found in command: ' + str(cmdText)
        print(message)
        self.pyCode= "# " + message
    elif cmd == 'delete':
      print str(arg)
      self.graphs.remove(arg)
    elif cmd == 'img':
      canvasType= str(type(self.sc))
      if (canvasType != "<class 'ImgMplCanvas.ImgMplCanvas'>"):
        message= "Error: can't draw image except on an image canvas.\nTo create an image canvas see set imgdev."
        print(message)
      elif os.path.isfile(arg):
        print("Display image: " + str(arg))
        fileType= imghdr.what(arg)
        fileExtension= '.' + fileType
        if (arg.endswith(fileExtension)):
          varName= ntpath.basename(arg)
          varName, extension= os.path.splitext(varName)
        else:
          varName= 'image1'
        print("Image is in variable: " + str(varName))
        self._globals[varName]= skimage.data.imread(arg)
        # self.setPostParameter("graphdev " + str(varName))
        
        self.sc.displayImageWindow(arg, imageName=varName)        
        
        # self.sc.plt.imshow(self._globals[varName])
        # self.sc.show()
      else:
        message= 'Image file "' + arg + '" not found in command: ' + str(cmdText)
        print(message)
        self.pyCode= "# " + message
    return message

  def isEngrNumber(self, expression):
    if self.isfloat(expression):
      return True, float(expression)

    m= re.search(r'a$', expression, flags=re.IGNORECASE)
    if m is not None:
      return self.floatifyEngr(m, expression, 1e-18)

    m= re.search(r'f$', expression, flags=re.IGNORECASE)
    if m is not None:
      return self.floatifyEngr(m, expression, 1e-15)

    m= re.search(r'p$', expression, flags=re.IGNORECASE)
    if m is not None:
      return self.floatifyEngr(m, expression, 1e-12)

    m= re.search(r'n$', expression, flags=re.IGNORECASE)
    if m is not None:
      return self.floatifyEngr(m, expression, 1e-9)

    m= re.search(r'u$', expression, flags=re.IGNORECASE)
    if m is not None:
      return self.floatifyEngr(m, expression, 1e-6)

    m= re.search(r'm$', expression)
    if m is not None:
      return self.floatifyEngr(m, expression, 1e-3)

    m= re.search(r'k$', expression, flags=re.IGNORECASE)
    if m is not None:
      return self.floatifyEngr(m, expression, 1e3)

    m= re.search(r'meg$', expression, flags=re.IGNORECASE)
    if m is not None:
      return self.floatifyEngr(m, expression, 1e6)

    m= re.search(r'M$', expression)
    if m is not None:
      return self.floatifyEngr(m, expression, 1e6)

    m= re.search(r'G$', expression, flags=re.IGNORECASE)
    if m is not None:
      return self.floatifyEngr(m, expression, 1e9)

    m= re.search(r'T$', expression, flags=re.IGNORECASE)
    if m is not None:
      return self.floatifyEngr(m, expression, 1e12)

    return False, 0.0

  def isfloat(self, value):
    try:
      float(value)
      return True
    except ValueError:
      return False

  def floatifyEngr(self, m, expression, exponent):
    if m is not None:
      mantissa= expression[:m.start()]
      if self.isfloat(mantissa):
        value= float(mantissa) * exponent
        return True, value
      else:
        return False, 0.0

  def setCircuitName(self, arg):
    if (arg != ''):
      self.simulationBaseName= arg
      self.rawFileName= arg + ".raw"
      self.spiceFileName= arg + ".cki"
      self.getTitleLine()
      message= "Circuit is set to: " + arg
    else:
      message= "Circuit name has not been set"
    return message

  def readRawFile(self):
    # TODO: There should be a function in ReadSpiceRaw to find the proper value for the x variable,
    #       instead of assuming that it is named 't'
    #       After reading the raw file, emit a message such as 'sweep variable is t'.
    rawReader= ReadSpiceRaw.spice_read(self.rawFileName)
    if rawReader is None:
      print("file " + str(self.rawFileName) + " not found. File not read.")
    else:
      rawReader.loadSpiceVoltages()
      self._globals['r']= rawReader
      self.sc.set_xvar('t')
      self._globals['t']= r.t()

  def readHDF5File(self):
    hdf5Reader = ReadHDF5.hdf5_read(self.hdf5FileName)
    if hdf5Reader is not None:
      hdf5Reader.loadHDF5Data()
      self._globals['h']= hdf5Reader

  def getTitleLine(self):
    if os.path.isfile(self.spiceFileName):
      with open(self.spiceFileName, 'r') as f:
        title = f.readline()
        title = title.replace('\n', '')
        title = title.replace('\r', '')
        self.sc.set_title(title)

  # TODO: Move this to MainWindow so that the Qt calls aren't used here.
  # TODO: Make the simulator path and command configurable.
  # TODO: Should probably have a delegate for the simulator.
  
  # Xyce runtime command:  runxyce -r xtest.raw -a -gui ngtest.cki
  
  def simulate(self, arg):
    if arg != '':
      self.setCircuitName(arg)
    if self.spiceFileName != '':
      message= "Run simulator on " + self.spiceFileName + " to produce " + self.rawFileName
      self.process= QProcess()
      self.process.connect(self.process, SIGNAL("finished(int)"), self.processCompleted)
      self.process.start('/usr/local/bin/ngspice -r ' + self.rawFileName + ' -b ' + self.spiceFileName)
    else:
      message= "No simulation specified"
    return message

  def processCompleted(self):
    # self.ui.statusText.setText("Finished")
    print "Finished simulating"
    self.readRawFile()
    print "Finished reading raw file"

  def include(self, arg):
    print "Include file: " + str(arg)

    if not os.path.isfile(arg):
      print("Include file " + str(arg) + " not found")
      return

    with open(arg, 'r') as handle:
      for cmdText in handle:
        self.executeCmd(cmdText)

  # TODO: Might need two types of plots, one for images and one for graphs
  # There are bugs when one goes in place of the other.
  def graphExpr(self, arg, cmdText):
    userPlotExpr= arg
    res= None
    fsz= 12
    message= ''
    plotExpr= self.sve.fixWaveFormVariableNames(userPlotExpr)
    grPattern= re.compile(r"g[rs] ([iv]\([^)]+\))")
    res, success= self.evaluator.runEval(cmdText, res, plotExpr)
    if not success:
      badGraphCmd= grPattern.match(cmdText)
      if badGraphCmd:
        vfunction= badGraphCmd.group(1)
        return "Error: unrecognized waveform: " + str(vfunction)
      else:
        return "Error evaluating plot expression: " + cmdText

    if self.sc.get_xvar() in self._globals:
      typeXAxis= str(type(self._globals[self.sc.get_xvar()]))
      if "<type 'numpy.ndarray'>" in typeXAxis:
        xAxisPts= len(self._globals[self.sc.get_xvar()])
      else:
        xAxisPts= 1
    else:
      typeXAxis= None

    typeYAxis= str(type(res))
    if (typeYAxis == "<type 'numpy.ndarray'>" and len(shape(res))==3):
      message= "Graph image: " + str(userPlotExpr)
      self.sc.plt.imshow(res)
      self.sc.show()
      self.pyCode = 'graph.graphImage()'
      return message
    else:
      if "<type 'numpy.ndarray'>" in typeYAxis:
        yAxisPts= len(res)
      else:
        yAxisPts= 1

      if typeXAxis == None:
        self.sc.plotYList(res, arg, self.sc.get_title())
      else:
        if xAxisPts == yAxisPts:
          self.sc.plotXYList(self._globals[self.sc.get_xvar()], res, self.sc.get_xvar(), arg, self.sc.get_title())
        else:
          plX= 'point' if xAxisPts == 1 else 'points'
          plY= 'point' if yAxisPts == 1 else 'points'
          badGraphCmd= grPattern.match(cmdText)
          if badGraphCmd:
            vfunction= badGraphCmd.group(1)
            message= "Error: unrecognized waveform: " + str(vfunction)
          else:
            message =  "Error: X-axis: " + str(self.sc.get_xvar()) + " has " + str(xAxisPts) + " " + plX + "\n"
            message += "       Y-axis: " + str(cmdText) + " has " + str(yAxisPts) + " " + plY
      return message

  def setPostParameter(self, arg):
    if (self.setPostFlag(arg) == True):
      return
    regexSet= re.match(r'^(xname|title|xl|yl|graphdev|imgdev) (.*)', arg)
    if regexSet is not None:
      setcmd= regexSet.group(1)
      setarg= regexSet.group(2)
      if setcmd == 'xname':
        self.sc.set_xvar(setarg)
        self.pyCode= 'graph.xname("'+ self.sc.get_xvar() + '")'
        message = "Set x variable to " + str(self.sc.get_xvar())
      elif setcmd == 'title':
        self.sc.set_title(setarg)
        self.pyCode= 'graph.title("'+ self.sc.get_title() + '")'
      elif setcmd == 'yl':
        if str(setarg) == 'auto':
          self.sc.set_yauto(True)
          self.pyCode = 'graph.ylimAuto()'
        else:
          self.sc.set_yauto(False)
          regexRange= re.match(r'^\s*(\S+)\s+(\S+)', setarg)
          if regexRange is not None:
            loflg, lo= self.isEngrNumber(regexRange.group(1))
            hiflg, hi= self.isEngrNumber(regexRange.group(2))
            if loflg and hiflg:
              if (lo == hi):
                lo= lo * 0.99
                hi= lo * 1.01
              if (lo > hi):
                limtmp= lo
                lo= hi
                hi= limtmp
              self.sc.ylimlow= lo
              self.sc.ylimhigh= hi
              self.pyCode = 'graph.set_ylim(' + str(lo) + ',' + str(hi) + ')'
              self.sc.plt.set_ylim(lo, hi)
              self.sc.draw()
      elif setcmd == 'xl':
        if str(setarg) == 'auto':
          self.sc.set_xauto(True)
          self.pyCode = 'graph.xlimAuto()'
        else:
          self.sc.set_xauto(False)
          regexRange= re.match(r'^\s*(\S+)\s+(\S+)', setarg)
          if regexRange is not None:
            loflg, lo= self.isEngrNumber(regexRange.group(1))
            hiflg, hi= self.isEngrNumber(regexRange.group(2))
            if loflg and hiflg:
              self.sc.xlimlow= lo
              self.sc.xlimhigh= hi
            if loflg and hiflg:
              if (lo == hi):
                lo= lo * 0.99
                hi= lo * 1.01
              if (lo > hi):
                limtmp= lo
                lo= hi
                hi= limtmp
              self.sc.xlimlow= lo
              self.sc.xlimhigh= hi
              self.sc.plt.set_xlim(lo, hi)
              self.pyCode = 'graph.set_xlim(' + str(lo) + ',' + str(hi) + ')'
              self.sc.draw()
              
      elif setcmd == 'graphdev':
        currentCanvasName= self.sc.get_name()
        if setarg != currentCanvasName:
          if setarg not in self.graphs.cd:
            print "Need a new graph called " + str(setarg)
            self.graphs.create(canvasName=str(setarg))
          else:
            print "Need to set active graph to " + str(setarg)
          self.graphs.setActive(setarg)
          self.setGraphicsActiveDelegate(self.graphs.getActiveCanvas())
          
      elif setcmd == 'imgdev':
        currentCanvasName= self.sc.get_name()
        if setarg != currentCanvasName:
          if setarg not in self.graphs.cd:
            print "Need a new graph called " + str(setarg)
            self.graphs.createImg(canvasName=str(setarg))
          else:
            print "Need to set active graph to " + str(setarg)
          self.graphs.setActive(setarg)
          self.setGraphicsActiveDelegate(self.graphs.getActiveCanvas())

      else:
        message = "Unrecognized set command: " + setcmd
    else:
      message= "Unrecognized setting: " + arg
      
  def setPostFlag(self, arg):
    regexSet= re.match(r'^(xlog|xlin|ylog|ylin)$', arg)
    if regexSet is not None:
      setcmd= regexSet.group(1)
      if setcmd == False:
        return False
      if setcmd == 'xlog':
        print("Setting x-axis to log plot")
        self.sc.set_xlog(True)
      if setcmd == 'xlin':
        print("Setting x-axis to log plot")
        self.sc.set_xlog(False)
      if setcmd == 'ylog':
        print("Setting y-axis to log plot")
        self.sc.set_ylog(True)
      if setcmd == 'ylin':
        print("Setting y-axis to log plot")
        self.sc.set_ylog(False)        
      return True
    return False
    

  def setGraphicsActiveDelegate(self, sc):
    self.sc= sc
    # The graphics canvas sends back data from markers in the form of globals.
    # self.sc._globals= self._globals
    # self.marker= EngMarker.EngMarker(self.sc)

  def setGraphicsWindowsDelegate(self, graphs):
    self.graphs= graphs

  # Marker delegate protocol implementation:
  def setMarkerDelegate(self, obj):
    self.markerDelegate= obj

  def set_markerX(self, val):
    self._globals['markerX']= val

  def set_markerY(self, val):
    self._globals['markerY']= val

  def set_deltaMarkerX(self, val):
    self._globals['deltaMarkerX']= val

  def set_deltaMarkerY(self, val):
    self._globals['deltaMarkerY']= val

  def get_markerX(self):
    if 'markerX' in self._globals.keys():
      return self._globals['markerX']
    else:
      return None;

  def get_markerY(self):
    if 'markerY' in self._globals.keys():
      return self._globals['markerY']
    else:
      return None;
