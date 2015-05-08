import numpy
import string
import sys
import re
import os.path

"""
pt=h["spiceplot/therm.asc"]['therm.asc']
pt[11][0]
0.10000000000000001

"""
class readHDF5(object):
  def __init__(self):
    self.hdf5Var= {}
    return
  
  def hdf5_read(self, fn):
    print("Read hdf5 file: " + fn)
    if os.path.isfile(fn):
      self._globals['h']= h5py.File(fn, "r")   
    return
  
  def loadHDF5Data(self):
    return
  
  def h(self, varName):
    return self.hdf5Var[varName]  
  
if __name__ == "__main__":
  reader= hdf5_read('hdf5ex_dat.hdf5')
  reader.loadHDF5Data()
  s= reader.h('sampleValues')
  print str(s)
  lin= reader.i('lin')
  print str(lin)
  
