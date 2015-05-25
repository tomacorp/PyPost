import os.path
import PySide.QtCore
from PySide.QtCore import QProcess, QObject, SIGNAL

from math import *
from tokenize import *
from numpy import *
from numpy.fft import *

import re
import numpy as np
import h5py

import EngEvaluate
import ReadSpiceRaw
import SpiceVarExpr

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

# TODO: Check for presence of raw data in r before substituting and graphing with v(v1)
#       implement HDF5 file reader
#       implement Python program output as transcript
#       implement save-all as ascii
#       implement restore-all as ascii
#       save state from one run to the next
#       reset state to default
#       implement gr x .vs y
#       implement freq instead of time as an axis, vdb, idb, vm, im
#       AC analysis - complex numbers from raw file
#       2D plots with thermal solutions
#       Add web server to inject remote commands via http
#       gr 3
#         Can't get length of integer.
#         Needs to check that expr is an array, or better extend int to array.
#       NGSpice raw file has all the waveform names in lower case.
#         Would like to make graphing them case insensitive.
#       Path to NGSpice should be configured in a pull-down from the Main Window.

# Layout for canvas: http://matplotlib.org/users/tight_layout_guide.html

class CommandInterp:
  def __init__(self):
    self._globals= globals()
    self.evaluator= EngEvaluate.EngEvaluate(self._globals)
    self.pyCode= ''
    self.sve= SpiceVarExpr.SpiceVarExpr()
    self.xvar= 't'
    self.yauto= True
    self.ylimlow= -16.0
    self.ylimhigh= 16.0
    self.xauto= True
    self.xlimlow= 0.0
    self.xlimhigh= 0.02
    self.rawFileName= ''
    self.spiceFileName= ''
    self.simulationBaseName= ''
    self.title=''
    return

  def executeCmd(self, cmdText):
    cmdText=cmdText.rstrip()
    cmdText=cmdText.lstrip()
    print("Command: " + cmdText)
    message= ''
    longCmd= re.match(r'^(ci|gr|gs|set|si|history|readh5) (.*)', cmdText)
    shortCmd= re.match(r'^(ci|set|si|history)$', cmdText)
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

    elif cmd == 'history':
      print "History not implemented yet."

    return message

  def showSettings(self):
    self.pyCode= ''
    message = "Parameters are:\n  Sweep variable: " + str(self.xvar)
    message += "\n  Title: " + str(self.title)

    xLimitsMessage= "auto"
    if not self.xauto:
      xLimitsMessage= str(self.xlimlow) + " " + str(self.xlimhigh)
    message += "\n  X Limits: " + xLimitsMessage

    yLimitsMessage= "auto"
    if not self.yauto:
      yLimitsMessage= str(self.ylimlow) + " " + str(self.ylimhigh)
    message += "\n  Y Limits: " + yLimitsMessage
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
    if cmd == 'ci':
      self.pyCode= "sim.setCircuitName(" + str(arg) + ")"
      message= self.setCircuitName(arg)
      self.readRawFile()
    elif cmd == 'gr':
      self.sc.plt.hold(False)
      message= self.graphExpr(arg, cmdText)
      if message == '':
        self.pyCode= "graph.graph("+ self.evaluator.logPyCode + ")"
      else:
        print(message)
        self.pyCode= "# " + message
    elif cmd == 'gs':
      self.sc.plt.hold(True)
      message= self.graphExpr(arg, cmdText)
      if message == '':
        self.pyCode= "graph.graphSameAxes("+ self.evaluator.logPyCode + ")"
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
    if (arg != ''):  # TODO Need similar for isEng and also engineerToFloat(string) to convert engr notation to float
      self.simulationBaseName= arg
      self.rawFileName= arg + ".raw"
      self.spiceFileName= arg + ".cki"
      self.getTitleLine()
      message= "Circuit is set to: " + arg
    else:
      message= "Circuit name has not been set"
    return message

  def readRawFile(self):
    rawReader= ReadSpiceRaw.spice_read(self.rawFileName)
    if rawReader is not None:
      rawReader.loadSpiceVoltages()
      self._globals['r']= rawReader
      self.xvar= 't'
      self._globals['t']= r.t()

  def readHDF5File(self):
    hdf5Reader = ReadHDF5.hdf5_read(self.hdf5FileName)
    if hdf5Reader is not None:
      hdf5Reader.loadHDF5Data()
      self._globals['h']= hdf5Reader

  def getTitleLine(self):
    if os.path.isfile(self.spiceFileName):
      with open(self.spiceFileName, 'r') as f:
        self.title = f.readline()
        self.title = self.title.replace('\n', '')
        self.title = self.title.replace('\r', '')

  # TODO: Move this to MainWindow so that the Qt calls aren't used here.
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

  def graphExpr(self, arg, cmdText):
    plotExpr= arg
    res= None
    fsz= 12
    message= ''
    plotExpr= self.sve.fixWaveFormVariableNames(plotExpr)

    res, success= self.evaluator.runEval(cmdText, res, plotExpr)
    if not success:
      return "Error evaluating plot expression: " + cmdText

    if self.xvar in self._globals:
      typeXAxis= str(type(self._globals[self.xvar]))
      if "<type 'numpy.ndarray'>" in typeXAxis:
        xAxisPts= len(self._globals[self.xvar])
      else:
        xAxisPts= 1
    else:
      typeXAxis= None

    typeYAxis= str(type(res))
    if "<type 'numpy.ndarray'>" in typeYAxis:
      yAxisPts= len(res)
    else:
      yAxisPts= 1

    if typeXAxis == None:
      self.sc.plotYList(res, arg, self.title)
    else:
      if xAxisPts == yAxisPts:
        self.sc.plotXYList(self._globals[self.xvar], res, self.xvar, arg, self.title)
      else:
        plX= 'point' if xAxisPts == 1 else 'points'
        plY= 'point' if yAxisPts == 1 else 'points'
        message = "Error: X-axis has " + str(xAxisPts) + " " + plX + " and Y-axis has " + str(yAxisPts) + " " + plY
    return message

  def setPostParameter(self, arg):
    regexSet= re.match(r'^(xname|title|xl|yl) (.*)', arg)
    if regexSet is not None:
      setcmd= regexSet.group(1)
      setarg= regexSet.group(2)
      if setcmd == 'xname':
        self.xvar = setarg
        self.pyCode= 'graph.xname('+ self.xname + ')'
        message = "Set x variable to " + str(self.xvar)
      elif setcmd == 'title':
        self.title= setarg
        self.pyCode= 'graph.title('+ self.title + ')'
      elif setcmd == 'yl':
        if str(setarg) == 'auto':
          self.yauto = True
          self.pyCode = 'graph.ylimAuto()'
        else:
          self.yauto = False
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
              self.ylimlow= lo
              self.ylimhigh= hi
              self.pyCode = 'graph.ylim(' + str(lo) + ',' + str(hi) + ')'
      elif setcmd == 'xl':
        if str(setarg) == 'auto':
          self.xauto = True
          self.pyCode = 'graph.xlimAuto()'
        else:
          self.xauto = False
          regexRange= re.match(r'^\s*(\S+)\s+(\S+)', setarg)
          if regexRange is not None:
            loflg, lo= self.isEngrNumber(regexRange.group(1))
            hiflg, hi= self.isEngrNumber(regexRange.group(2))
            if loflg and hiflg:
              self.xlimlow= lo
              self.xlimhigh= hi
            if loflg and hiflg:
              if (lo == hi):
                lo= lo * 0.99
                hi= lo * 1.01
              if (lo > hi):
                limtmp= lo
                lo= hi
                hi= limtmp
              self.xlimlow= lo
              self.xlimhigh= hi
              self.pyCode = 'graph.xlim(' + str(lo) + ',' + str(hi) + ')'
      else:
        message = "Unrecognized set command: " + setcmd
    else:
      message= "Unrecognized setting: " + arg

  def setGraphicsDelegate(self, sc):
    self.sc= sc
    # The graphics canvas send back data from markers in the form of globals.
    # self.sc._globals= self._globals
    # self.marker= EngMarker.EngMarker(self.sc)

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

  # Graphics limit delegate protocol implementation:
  def set_xlimitlow(self, val):
    self.xlimlow= val
    #  ... More methods ...