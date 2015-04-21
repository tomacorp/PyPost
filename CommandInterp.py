import PyQt4.QtCore
from PyQt4.QtCore import QProcess, QObject, SIGNAL

from math import *
from tokenize import *
from numpy import *
from numpy.fft import *
import re
import numpy as np

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
# set xl 0 10
# set yl 0 10
# set xl auto
# set yl auto
# label x-axis, y-axis, title, subtitle, time, date
# ticks, etc.

# TODO: Check for presence of raw data in r before substituting and graphing with v(v1)
#       implement Python program output as transcript
#       implement save-all as ascii
#       implement restore-all as ascii
#       save state from one run to the next
#       reset state to default
#       save command-line history across sessions
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

# Layout for canvas: http://matplotlib.org/users/tight_layout_guide.html

class CommandInterp:
  def __init__(self):
    self._globals= globals()
    self.evaluator= EngEvaluate.EngEvaluate(self._globals)
    self.sve= SpiceVarExpr.SpiceVarExpr()
    self.xvar= 't'
    self.rawFileName= ''
    self.spiceFileName= ''
    self.simulationBaseName= ''
    return

  def executeCmd(self, cmdText):
    print("Command: " + cmdText)
    message= ''
    longCmd= re.match(r'^(ci|gr|gs|set|si) (.*)', cmdText)
    shortCmd= re.match(r'^(ci|gr|gs|set|si)', cmdText)
    if longCmd is not None:
      message= self.executeLongCommand(longCmd, cmdText)
    elif shortCmd is not None:
      message= self.executeShortCommand(shortCmd)
    else:
      cmdText= self.sve.fixWaveFormVariableNames(cmdText)
      message= self.evaluator.evaluate(cmdText)

    return message

  def executeShortCommand(self, shortCmd):
    message= ''
    cmd= shortCmd.group(1)
    if cmd == 'ci':
      if self.simulationBaseName == '':
        message= "No simulation specified"
      else:
        message= "Circuit is: " + self.simulationBaseName
    elif cmd == 'set':
      message= "Parameters are: (dump not implemented yet!)"
    if cmd == 'si':
      if self.simulationBaseName != '':
        message= self.simulate('')
        self.readRawFile()
      else:
        message= "Circuit name has not been set yet"
    return message

  def executeLongCommand(self, longCmd, cmdText):
    cmd= longCmd.group(1)
    arg= longCmd.group(2)
    message= ''
    if cmd == 'si':
      message= self.setCircuitName(arg)
      message= message + "\n" + self.simulate(arg)
    if cmd == 'ci':
      message= self.setCircuitName(arg)
      self.readRawFile()
    elif cmd == 'gr':
      self.sc.plt.hold(False)
      self.graphExpr(arg, cmdText)
    elif cmd == 'gs':
      self.sc.plt.hold(True)
      self.graphExpr(arg, cmdText)
    elif cmd == 'set':
      self.setPostParameter(arg)
    return message

  def setCircuitName(self, arg):
    if (arg != ''):
      self.simulationBaseName= arg
      self.rawFileName= arg + ".raw"
      self.spiceFileName= arg + ".cki"
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
    res= arange(10)
    fsz= 12
    plotExpr= self.sve.fixWaveFormVariableNames(plotExpr)

    res, success= self.evaluator.runEval(cmdText, res, plotExpr)
    if success:

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
        self.sc.plt.plot(res)
        self.sc.plt.set_xlabel('Index', fontsize=fsz)
        self.sc.plt.set_ylabel(arg, fontsize=fsz)
        self.sc.plt.set_title('Title', fontsize=fsz)
        self.sc.draw()
        self.sc.show()
      else:
        if xAxisPts == yAxisPts:
          self.sc.plt.plot(self._globals[self.xvar],res)
          self.sc.plt.set_xlabel(self.xvar, fontsize=fsz)
          self.sc.plt.set_ylabel(arg, fontsize=fsz)
          self.sc.plt.set_title('Title', fontsize=fsz)
          self.sc.draw()
          self.sc.show()
        else:
          plX= 'point' if xAxisPts == 1 else 'points'
          plY= 'point' if yAxisPts == 1 else 'points'
          message = "Error: X-axis has " + str(xAxisPts) + " " + plX + " and Y-axis has " + str(yAxisPts) + " " + plY
    else:
      message= "Error evaluating plot expression: " + cmdText

  def setPostParameter(self, arg):
    regexSet= re.match(r'^(xname) (.*)', arg)
    if regexSet is not None:
      setcmd= regexSet.group(1)
      setarg= regexSet.group(2)
      if setcmd == 'xname':
        self.xvar = setarg
        message = "Set x variable to " + str(self.xvar)
      else:
        message = "Unrecognized set command: " + setcmd
    else:
      message= "Unrecognized setting: " + arg

  def setGraphicsDelegate(self, sc):
    self.sc= sc