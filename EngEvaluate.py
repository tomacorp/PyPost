from tokenize import *
from io import StringIO
import re
import sys
from math import *
from numpy import *
import numpy as np

class EngEvaluate():
  def __init__(self, _globals):
    self.debug= False
    self.unrecognizedEngrNotation= -999
    self.logPyCode= ''
    self._globals= _globals
    return;

  # FIXME: This probably doesn't work when given non-expressions or assignments,
  # such as 'import numexpr as ne'
  # Want these chunks of python code to just work.
  # The problem is that the whitespace is removed.

  def evaluate(self, cmdText):
    if self.debug:
      self.pyTok(cmdText)
    varName, rhs= self.getAssignment(cmdText)
    res, success= self.runEval(cmdText, varName, rhs)
    message= self.displayResult(cmdText, varName, rhs, res, success)
    return message

  def err_handler(self, type, flag):
    print("Floating point error (%s), with flag %s" % (type, flag))

  def runEval(self, cmdText, varName, rhs):
    """runEval() does the eval and returns the result,
       which is used for graphing."""

    _globals= self._globals

    self.logPyCode= '# Error: ' + str(varName) + '=' + str(rhs)
    try:
      rhs= self.pyFromVec(rhs)
    except:
      print("Error: runEval at pyFromVec: " + rhs)

    try:
      rhs= self.pyFromEng(rhs)
    except:
      print("Error: runEval at pyFromEng: " + rhs)

    saved_handler = np.seterrcall(self.err_handler)
    save_err = np.seterr(divide='call', over='call', under='call',
                        invalid='call')

    if varName:
      self.logPyCode= str(varName) + '=' + str(rhs)
    else:
      self.logPyCode= str(rhs)

    try:
      result= eval(str(rhs), _globals, _globals)
      _globals[str(varName)]= result
      success= True
    except:
      self.logCommandRHS= '# Error: ' + self.logPyCode
      result= 0
      success= False
    np.seterrcall(saved_handler)
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
    try:
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
    except:
      print("Could not parse " + txtEng)
    if self.debug:
      print("Translated: " + deEngExpr)
    return deEngExpr

  def pyTok(self, txt):
    deEngExpr= ''
    lastToknum= 0
    g = generate_tokens(StringIO(txt).readline)
    try:
      for toknum, tokval, _, _, _  in g:
        print(str(toknum) + ' ' + str(tokval))
    except:
      print("Could not parse " + txtEng)

  """This routine substitutes a Numpy array for Python array.
    For example:
    pyFromVec([a,b,c])
    returns np.array([a,b,c])
    However, a numpy reference like x[1,3] should not be turned into np.array(x[1,3])
  """
  def pyFromVec(self, txt):
    pyExpr= ''
    lastToken= ''
    lastToknum= 0
    invec= False
    inNumpyVar= False
    inNumpyVector= False
    g = generate_tokens(StringIO(txt).readline)
    try:
      for toknum, tokval, _, _, _  in g:
        if (toknum == OP and tokval == '['):
          if inNumpyVar:
            inNumpyVector= True
            pyExpr = pyExpr + '['
          else:
            vec= 'np.array(['
          invec= True
        elif (invec and toknum == OP and tokval == ','):
          if inNumpyVector:
            pyExpr = pyExpr + lastToken + ','
          else:
            vec= vec + lastToken + ','
          lastToken= ''
        elif (invec and toknum == OP and tokval == ']'):
          if inNumpyVector:
            inNumpyVector= False
            inNumpyVar= False
            pyExpr = pyExpr + lastToken + ']'
          else:
            vec = vec + lastToken + '])'
            pyExpr = pyExpr + vec
          invec= False
          lastToken= ''
        elif (invec):
          lastToken += str(tokval)
        elif (toknum == NAME):
          if tokval in self._globals:
            inNumpyVar= True
          pyExpr = pyExpr + tokval
            # All bets are off, just return the input
            # return txt
        else:
          inNumpyVar= False
          pyExpr = pyExpr + tokval
    except:
      print("Could not parse " + txtEng)
    if self.debug:
      print("Vector expr:" + str(pyExpr))
    return pyExpr
