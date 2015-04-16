from tokenize import *
from cStringIO import StringIO
import re
import sys
from math import *
from numpy import *
import numpy as np

class EngEvaluate():
  def __init__(self, _globals):
    self.debug= False
    self.unrecognizedEngrNotation= -999
    self._globals= _globals
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
    _globals= self._globals
    #if self.debug:
      #print("Assign:" + varName + " to rhs:" + rhs)
    try:
      rhs= self.pyFromVec(rhs)
    except:
      print("Error: runEval at pyFromVec: " + rhs)

    try:
      rhs= self.pyFromEng(rhs)
    except:
      print("Error: runEval at pyFromEng: " + rhs)

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
      if self.debug:
        print('  ' + str(toknum) + ' ' + str(tokval))
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
