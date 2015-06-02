from fysom import Fysom
from tokenize import *
from cStringIO import StringIO

class SpiceVarExpr:

  def __init__(self):
    self.outExpr= ''
    self.waveType= ''
    self.waveName= ''
    self.datasetName= 'r'
    self.fsm = Fysom({'initial': 'looking',
                      'events':
                        [
                          {'name': 'seeWaveVar', 'src':'looking', 'dst':'openParen'},
                          {'name': 'seeOpenParen', 'src':'openParen', 'dst':'inWaveVar'},
                          {'name': 'getWaveVar', 'src':'inWaveVar', 'dst':'closeParen'},
                          {'name': 'seeCloseParen', 'src':'closeParen', 'dst':'looking'},
                          {'name': 'reset', 'src':['looking', 'openParen', 'inWaveVar', 'closeParen'], 'dst':'looking'}
                          ],
                        'callbacks':{
                          'onseeWaveVar': self.onseeWaveVar,
                          'ongetWaveVar': self.ongetWaveVar,
                          'onseeCloseParen': self.onseeCloseParen,
                        }
                      })

  def datasetName(self, datasetName):
    self.dataset= datasetName

  def onseeWaveVar(self, e):
    self.waveType= e.msg

  def ongetWaveVar(self, e):
    self.waveName= e.msg

  def onseeCloseParen(self, e):
    self.outExpr += self.datasetName + "." + self.waveType + "('" + self.waveName + "')"


  # The state machine makes sure that the voltage or current expression follows the syntax.
  # If it doesn't, the machine backtracks and resets.
  # The non-matching text passes through.

  # Backtracking could be implemented with untokenize()

  # Problem: the tokenizer is not returning x1.3, it is returning x1.
  # Then the closing parenthesis, which is expected next, is not found.
  # This causes the state machine to backtrack and not translate to r['x1.3'] as it should.
  # Need to either fix the generate_tokens or the state machine to know to be able to
  # take more tokens to add to the state 'inWaveVar' before the closing paren.
  # Since generate_tokens is a big complicated module that someone else did,
  # need to handle the states here.
  #
  #
  def fixWaveFormVariableNames(self, txt):
    self.outExpr= ''
    lastToknum= 0
    g = generate_tokens(StringIO(txt).readline)

    try:
      for toknum, tokval, _, _, _  in g:

        if self.fsm.current == "looking":
          if toknum == NAME and (tokval == 'v' or tokval == 'i'):
            self.fsm.seeWaveVar(msg=tokval)
            continue

        elif self.fsm.current == "openParen":
          if toknum == OP and tokval == '(':
            self.fsm.seeOpenParen(msg=tokval)
            continue
          else:
            self.outExpr += self.waveType
            self.fsm.reset()

        elif self.fsm.current == 'inWaveVar':
          if toknum == NAME or toknum == NUMBER:
            self.fsm.getWaveVar(msg=tokval)
            continue
          else:
            self.outExpr += self.waveType + '('
            self.fsm.reset()

        # This appends subcircuit extended net names while still inside parens.
        elif self.fsm.current == 'closeParen' and tokval != ')':
          self.waveName += tokval
          continue

        elif self.fsm.current== 'closeParen':
          if toknum == OP and tokval == ')':
            self.fsm.seeCloseParen(msg=tokval)
            continue
          else:
            self.outExpr += self.waveType + '(' + self.waveName
            self.fsm.reset()

        self.outExpr += tokval

        if toknum == ENDMARKER:
          return self.outExpr

      else:
        print "Unexpected end of token parsing."
        return txt
    except:
      print "Parsing failed"
      return txt

if __name__ == "__main__":

  sve= SpiceVarExpr()

  inputExpression= 'v(1a)+2+v(v1)+av(v2)+vi(i)+i(i)'
  outputExpression= sve.fixWaveFormVariableNames(inputExpression)
  print "Input: " + inputExpression
  print "Output: " + outputExpression
  print "-----"

  inputExpression= '3.04m+v1+v(a)+v(b)+i(r1)*10k'
  outputExpression= sve.fixWaveFormVariableNames(inputExpression)
  print "Input: " + inputExpression
  print "Output: " + outputExpression

  inputExpression= ')'
  outputExpression= sve.fixWaveFormVariableNames(inputExpression)
  print "Input: " + inputExpression
  print "Output: " + outputExpression

  inputExpression= 'v(x1.3)'
  outputExpression= sve.fixWaveFormVariableNames(inputExpression)
  print "Input: " + inputExpression
  print "Output: " + outputExpression

  inputExpression= 'i(l.x1.l1)'
  outputExpression= sve.fixWaveFormVariableNames(inputExpression)
  print "Input: " + inputExpression
  print "Output: " + outputExpression