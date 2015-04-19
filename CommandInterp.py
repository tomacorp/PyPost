from math import *
from tokenize import *
from numpy import *
from numpy.fft import *
import re
import numpy as np
import EngEvaluate
import ReadSpiceRaw
import SpiceVarExpr

class CommandInterp:
  def __init__(self):
    self._globals= globals()
    self.evaluator= EngEvaluate.EngEvaluate(self._globals)
    self.sve= SpiceVarExpr.SpiceVarExpr()
    self.xvar= 't'
    return

  def executeCmd(self, cmdText):
    print("Command: " + cmdText)
    message= ''

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

    regexCmd= re.match(r'^(ci|gr|set) (.*)', cmdText)
    if regexCmd is not None:
      cmd= regexCmd.group(1)
      arg= regexCmd.group(2)

      if cmd == 'ci':
        rawFileName= arg
        rawReader= ReadSpiceRaw.spice_read(rawFileName)
        if rawReader is not None:
          rawReader.loadSpiceVoltages()
          self._globals['r']= rawReader
          self.xvar= 't'
          self._globals['t']= r.t()
        else:
          message= "Could not read raw file " + rawFileName

      elif cmd == 'gr':
        plotExpr= arg
        print("graph " + plotExpr)
        res= arange(10)

        plotExpr= self.sve.fixWaveFormVariableNames(plotExpr)

        res, success= self.evaluator.runEval(cmdText, res, plotExpr)
        if success:

          typeXAxis= str(type(self._globals[self.xvar]))
          if "<type 'numpy.ndarray'>" in typeXAxis:
            xAxisPts= len(self._globals[self.xvar])
          else:
            xAxisPts= 1

          typeYAxis= str(type(res))
          if "<type 'numpy.ndarray'>" in typeYAxis:
            yAxisPts= len(res)
          else:
            yAxisPts= 1

          if xAxisPts == yAxisPts:
            self.sc.plt.plot(self._globals[self.xvar],res)
            self.sc.plt.set_xlabel("X label")
            self.sc.plt.set_ylabel("Y label")
            self.sc.draw()
            self.sc.show()
          else:
            plX= 'point' if xAxisPts == 1 else 'points'
            plY= 'point' if yAxisPts == 1 else 'points'
            message = "Error: X-axis has " + str(xAxisPts) + " " + plX + " and Y-axis has " + str(yAxisPts) + " " + plY
        else:
          message= "Error evaluating plot expression: " + cmdText

      elif cmd == 'set':
        regexSet= re.match(r'^(xname) (.*)', arg)
        if regexCmd is not None:
          setcmd= regexSet.group(1)
          setarg= regexSet.group(2)
          if setcmd == 'xname':
            self.xvar = setarg
            message = "Set x variable to " + str(self.xvar)
          else:
            message = "Unrecognized set command: " + setcmd
        else:
          message= "Unrecognized setting: " + arg


    else:
      cmdText= self.sve.fixWaveFormVariableNames(cmdText)
      message= self.evaluator.evaluate(cmdText)

    return message

  def setGraphicsDelegate(self, sc):
    self.sc= sc