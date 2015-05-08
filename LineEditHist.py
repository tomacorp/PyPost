from collections import deque
from PySide.QtCore import Qt
from PySide.QtCore import Signal
from PySide.QtGui import (QLineEdit, QKeySequence)
import sqlite3
import os.path

class lineEditHist(QLineEdit):
  def __init__(self, initialMessage):
    self.history= deque([''])
    super(lineEditHist, self).__init__(initialMessage)
    self.historyPointer= -1
    self.historyDBFile= 'history.sqlite'
    self.conn = sqlite3.connect(self.historyDBFile)
    self.createDBTables()
    # super(lineEditHist, self).__init__(initialMessage)
    self.loadHistoryDB()

  # FIXME: This loses the last character while editing the current line,
  # then going back in history, and then back to the current line.
  def keyPressEvent(self, evt):
    key=evt.key()
    if key == Qt.Key_Up:
      self.historyUp()
    elif key == Qt.Key_Down:
      self.historyDown()
    else:
      cmd= unicode(self.text())
      self.history[-1] = cmd

    # print("Key pressed" + str(evt.key()))
    return super(lineEditHist, self).keyPressEvent(evt)

  def resetHistoryPosition(self):
    self.historyPointer = -1

  def historyUp(self):
    if -self.historyPointer < len(self.history):
      self.historyPointer -= 1
      lastCommand= self.history[self.historyPointer]
      self.setText(lastCommand)
    else:
      historyLen= len(self.history)

  def historyDown(self):
    if self.historyPointer < -1:
      self.historyPointer += 1
      lastCommand= self.history[self.historyPointer]
      self.setText(lastCommand)

  def getHistory(self):
    sql = """SELECT rowid, cmd FROM CmdHistory ORDER BY rowid DESC LIMIT ?"""
    c = self.conn.cursor()
    for row in c.execute(sql, 3):
      print str(row)

  def loadHistoryDB(self):
    sql = """SELECT cmd FROM CmdHistory ORDER BY rowid"""
    c = self.conn.cursor()
    for row in c.execute(sql):
      self.history.append(row[0])

  def addCommandToDB(self, cmd, pycmd):
    # print "Add command to db"
    sql= """INSERT INTO CmdHistory(cmd, pycmd) VALUES(?, ?)"""
    c = self.conn.cursor()
    c.execute(sql, (cmd,pycmd))
    self.conn.commit()

  def createDBTables(self):
    sql= """CREATE TABLE IF NOT EXISTS "CmdHistory" ("cmd" TEXT, "pycmd" TEXT);"""

    c = self.conn.cursor()
    c.execute(sql)

    sql= """CREATE TABLE IF NOT EXISTS "Version" (
    "version" INTEGER
    );"""

    c.execute(sql)
