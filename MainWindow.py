from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import sys
from math import *
from tokenize import *  
from numpy import *

import tokenize
from cStringIO import StringIO
import re
import numpy as np
from collections import deque

# import numexpr as ne
from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSignal as Signal
from PyQt4.QtGui import (QApplication, QDialog, QLineEdit, QTextBrowser,
                         QVBoxLayout, QHBoxLayout, QKeySequence, QSizePolicy)

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# TODO:
#   Add variables and functions for constants and vectors
#   Text area instead of text line for input
#   Command line history
#   Matplotlib window call
#   hdf5 data import
#   compiled scripts
#   raw file import
#   IPC port
#   Display controls

# Consider:
#  In [143]: import numexpr as ne
#  In [146]: ne.evaluate('2*a*(b/c)**2', local_dict=var)
#  Out[146]: array([ 0.88888889,  0.44444444,  4.        ])

# TRY ne
# instead


class Form(QDialog):

  def __init__(self, parent=None):
    super(Form, self).__init__(parent)
    self.resize(720, 320)
    self.browser = QTextBrowser()
    self.history = QTextBrowser()
    self.sc      = MyStaticMplCanvas(self, width=2.5, height=2, dpi=100)
    self.lineedit = lineEditHist("Type an expression and press Enter")
    # self.lineedit = QLineEdit("Type an expression and press Enter")
    self.lineedit.selectAll()
    
    self.topLayout = QHBoxLayout()
    self.topLayout.addWidget(self.browser)

    self.topLayout.addWidget(self.sc)    
    # self.topLayout.addWidget(self.history)
    
    layout = QVBoxLayout()
    layout.addLayout(self.topLayout)
    layout.addWidget(self.lineedit)
    
    self.setLayout(layout)
    self.lineedit.setFocus()
    self.lineedit.returnPressed.connect(self.updateUi)
    
    self.setWindowTitle("Post Processor")
    
    # TODO: Set a delegate in the command interpreter.
    # Might be able to do this by putting the plot into a global space
    # and eval-ing the calls to it.

  def updateUi(self):
    cmdText = unicode(self.lineedit.text())
    # Command history goes here
    self.lineedit.history.append('')
    evaluator= engEvaluate()
    print("Command: " + cmdText)
    
    regex= re.match(r'^gr (.*)', cmdText)
    if regex is not None:
      plotExpr= regex.group(1)
      print("Replot " + cmdText)
      res= arange(10)
      t= arange(10)
      _globals= globals()
      _globals['t']= t    
      res, success= evaluator.runEval(cmdText, res, plotExpr)
      if success:  
        self.sc.axes.plot(t,res)
        self.sc.draw()
      else:
        print("Oopsie evaluating plot expression: " + cmdText)
    else:
      message= evaluator.evaluate(cmdText)
      self.browser.append(message)
      self.lineedit.clear()
      self.lineedit.resetHistoryPosition()
    

class MyMplCanvas(FigureCanvas):
  """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
  def __init__(self, parent=None, width=5, height=4, dpi=100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    self.axes = fig.add_subplot(111)
    # We want the axes cleared every time plot() is called
    self.axes.hold(False)

    self.compute_initial_figure()

    FigureCanvas.__init__(self, fig)
    self.setParent(parent)

    FigureCanvas.setSizePolicy(self,
                               QSizePolicy.Expanding,
                               QSizePolicy.Expanding)
    FigureCanvas.updateGeometry(self)

  def compute_initial_figure(self):
    pass
    
class MyStaticMplCanvas(MyMplCanvas):
  """Simple canvas with a sine plot."""
  def compute_initial_figure(self):
    t = arange(0.0, 3.0, 0.01)
    s = sin(2*pi*t)
    self.axes.plot(t, s)    
    
class lineEditHist(QLineEdit):
  def __init__(self, initialMessage):
    self.history= deque([''])
    self.historyPointer= -1
    super(lineEditHist, self).__init__(initialMessage)
    
  # FIXME: This loses the last character while editing the current line,
  # then going back in history, and then back to the current line.
  def keyPressEvent(self, evt):
    key=evt.key()
    if key == Qt.Key_Up:
      self.historyUp()
    elif key == Qt.Key_Down:
      self.historyDown()
    else:
      self.history[-1] = unicode(self.text())
    # print("Key pressed" + str(evt.key()))
    return super(lineEditHist, self).keyPressEvent(evt)
  
  def resetHistoryPosition(self):
    self.historyPointer = -1
    
  def historyUp(self):
    if -self.historyPointer < len(self.history):
      self.historyPointer -= 1
      lastCommand= self.history[self.historyPointer]
      self.setText(lastCommand)  
      
  def historyDown(self):
    print("Down")
    if self.historyPointer < -1:
      self.historyPointer += 1
      lastCommand= self.history[self.historyPointer] 
      self.setText(lastCommand)    

class engEvaluate():    
  def __init__(self):
    self.debug= False
    self.unrecognizedEngrNotation= -999
    return;
 
  # FIXME: This probably doesn't work when given non-expressions or assignments,
  # such as 'import numexpr as ne' 
  # Want these chunks of python code to just work.
  # The problem is that the whitespace is removed.
  def evaluate(self, cmdText):
    if self.debug:
      self.pyTok(cmdText)
      
    try:
      cmdText= self.pyFromVec(cmdText)
    except:
      print("Oops in pyFromVec: " + cmdText)
      
    try:
      cmdText= self.pyFromEng(cmdText)
    except:
      print("Oops in pyFromEng: " + cmdText)
      
    varName, rhs= self.getAssignment(cmdText)
    res, success= self.runEval(cmdText, varName, rhs)
    message= self.displayResult(cmdText, varName, rhs, res, success)    
    return message
    
  def runEval(self, cmdText, varName, rhs): 
    _globals= globals()
    if self.debug:
      print("Assign:" + varName + " to rhs:" + rhs)
    try:
      result= eval(str(rhs), _globals, _globals)
      _globals[str(varName)]= result
      success= True
    except:
      result= 0
      success= False
    return result, success
  
  def displayResult(self, cmdText, varName, rhs, res, success):  
    if success:
      message= "<b>{1}</b><br/> {0} = {2}".format(varName, cmdText, res)
    else:
      message= "Could not evaluate expression: <br/>{0}".format(rhs)
    return message

  def getAssignment(self,cmdText):
    assignmentMatch= re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=(.*)", cmdText)
    if (assignmentMatch):
      varName= assignmentMatch.group(1)
      rhs= assignmentMatch.group(2)
    else:
      varName= 'res'
      rhs= cmdText
    return varName, rhs
  
  def nameTokenToExponent(self, expression):
    if re.match(r'^a$', expression, flags=re.IGNORECASE):
      return -18
    elif re.match(r'^f$', expression, flags=re.IGNORECASE):
      return -15
    elif re.match(r'^p$', expression, flags=re.IGNORECASE):
      return -12
    elif re.match(r'^n$', expression, flags=re.IGNORECASE):
      return -9
    elif re.match(r'^u$', expression, flags=re.IGNORECASE):
      return -6
    elif re.match(r'^m$', expression):
      return -3
    elif re.match(r'^k$', expression, flags=re.IGNORECASE):
      return 3
    elif re.match(r'^meg$', expression, flags=re.IGNORECASE):
      return 6
    elif re.match(r'^M$', expression):
      return 6 
    elif re.match(r'^G$', expression, flags=re.IGNORECASE):
      return 9   
    elif re.match(r'^T$', expression, flags=re.IGNORECASE):
      return 12
    return self.unrecognizedEngrNotation

  def pyFromEng(self, txtEng): 
    deEngExpr= ''
    lastToknum= 0
    g = generate_tokens(StringIO(txtEng).readline)
    for toknum, tokval, _, _, _  in g:
      if lastToknum == NUMBER and toknum == NAME:
        engExp= self.nameTokenToExponent(tokval)
        if engExp == self.unrecognizedEngrNotation:
          print("Error: unexpected string at " + str(deEngExpr) + ": " + tokval)
        else:
          deEngExpr= deEngExpr + 'e' + str(engExp)
      else:
        deEngExpr= deEngExpr + tokval
      lastToknum= toknum
    if self.debug:
      print("Translated: " + deEngExpr)
    return deEngExpr
  
  def pyTok(self, txt): 
    deEngExpr= ''
    lastToknum= 0
    g = generate_tokens(StringIO(txt).readline)
    for toknum, tokval, _, _, _  in g:
      print(str(toknum) + ' ' + str(tokval)) 
      
  def pyFromVec(self, txt): 
    pyExpr= ''
    lastToknum= 0
    invec= False
    g = generate_tokens(StringIO(txt).readline)
    for toknum, tokval, _, _, _  in g:
      if (toknum == OP and tokval == '['):
        vec= 'np.array(['
        invec= True
      elif (invec and toknum == OP and tokval == ','):
        vec= vec + lastToken + ','
      elif (invec and toknum == OP and tokval == ']'):
        invec= False
        vec = vec + lastToken + '])'
        pyExpr = pyExpr + vec
      elif (invec):
        lastToken= tokval
      else:
        pyExpr = pyExpr + tokval
    if self.debug:
      print("Vector expr:" + str(pyExpr))
    return pyExpr
  

if __name__ == "__main__":
  app = QApplication(sys.argv)
  form = Form()
  form.show()
  app.exec_()
