import numpy
import string
import sys
import re
import os.path

class spice_vector(object):
  """
  Contains a single spice vector with it's data and it's attributes.
  The vector is numpy.array, either real or complex.
  The attributes are:
    * name: vector name
    * type: frequency, voltage or current
  """

  def __init__(self, vector=numpy.array([]), **kwargs):
    self.data = vector
    self.name = ""
    self.type = ""
    self.set_attributes(**kwargs)

  def set_attributes(self, **kwargs):
    """
    Set the attribues of the vector "name" and "type"
    """
    for k,v in kwargs.items():
      if hasattr(self,k):
        if type(getattr(self,k)) == type(v):
          setattr(self,k,v)
        else:
          print("Warning: attribute has wrong type: " \
                + type(v) + " ignored!")
      else:
        print("Warning: unknown attribute" + k + " Ignored!")

  def set_data(self, data_array):
    """
    set a new numpy.array as data vector
    """
    self.data = data_array

  def get_data(self):
    """
    returns the data vector as numpy.array
    """
    return self.data


class spice_plot(object):
  """
  This class holds a single spice plot
  It contains one scale vector and a list of several data vectors.
  The plot may have some attributes like "title", "date", ...
  """

  def __init__(self, scale=None ,data=None, **kwargs):
    """
    Initialize a new spice plot.
    Scale may be an spice_vector and data may be a list of spice_vectors.
    The attributes are provided by **kwargs.
    """
    self.title = "title undefined"
    self.date = "date undefined"
    self.plotname = "plotname undefined"
    self.plottype = "plottype undefined"
    self.dimensions = []

    ## a single scale vector
    if scale == None:
      scale=numpy.array([])
    else:
      self.scale_vector = scale

    ## init the list of spice_vector
    if data == None:
      self.data_vectors = []
    else:
      self.data_vectors = data

    self.set_attributes(**kwargs)

  def set_attributes(self, **kwargs):
    """
    Set the attributes of a plot.
    """
    for k,v in kwargs.items():
      if hasattr(self, k):
        if type(getattr(self,k)) == type(v):
          setattr(self,k,v)
        else:
          print("Warning: attribute has wrong type: " \
                + type(v) + " ignored!")
      else:
        print("Warning: unknown attribute \"" + k + "\". Ignored!")

  def set_scalevector(self, spice_vector):
    """
    Set a spice_vector as the scale_vektor.
    """
    self.scale_vector = spice_vector

  def set_datavectors(self, spice_vector_list):
    """
    Set a list of spice_vector as data of spice_plot
    """
    self.data_vectors = spice_vector_list

  def append_datavector(self, spice_vector):
    """
    Append a single spice_vector to the data section
    """
    self.data_vectors.append(spice_vector)

  def get_scalevector(self):
    """
    returns the scale vector as a spice_vector
    """
    return self.scale_vector

  def get_datavector(self,n):
    """
    returns the n-th data vector as a spice_vector
    """
    return self.data_vectors[n]

  def get_datavectors(self):
    """
    return a list of all spice_vectors of the plot
    """
    return self.data_vectors


class spice_read(object):
  """
  This class is reads a spice data file and returns a list of spice_plot
  objects.

  The file syntax is mostly taken from the function raw_write() from
  ngspice-rework-17 file ./src/frontend/rawfile.c
  """

  def __init__(self, filename):
    self.plots = []
    self.set_default_values()
    error = self.readfile(filename)
    self.spiceVoltage= {}
    self.spiceCurrent= {}
    self.spiceScale= {}
    if error:
      ## FIXME create an assertion
      return error

  def set_default_values(self):
    ## Set the default values for some options
    self.current_plot = spice_plot()
    self.nvars = 0
    self.npoints = 0
    self.numdims = 0
    self.padded = True
    self.real = True
    self.vectors = []

  def readfile(self,filename):
    if not os.path.isfile(filename):
      return
    f = open(filename, "rb")
    while (1):
      line = f.readline()
      linestr = line.decode('utf-8')
      if linestr == "":   ## EOF
        return

      tok = [t.strip() for t in linestr.split(":",1)]
      keyword = tok[0].lower()  ## don't care the case of the keyword entry

      if keyword == "title":
        self.current_plot.set_attributes(title=tok[1])
      elif keyword == "date":
        self.current_plot.set_attributes(date=tok[1])
      elif keyword == "plotname":  ## FIXME: incomplete??
        self.current_plot.set_attributes(plotname=tok[1])
      elif keyword == "flags":
        ftok= [t.lower().strip() for t in tok[1].split()]
        for flag in ftok:
          if flag == "real":
            self.real = True
          elif flag == "complex":
            self.real = False
          elif flag == "unpadded":
            self.padded = False
          elif flag == "padded":
            self.padded = True
          else:
            print('Warning: unknown flag: "' + f + '"')
      elif keyword == "no. variables":
        self.nvars = int(tok[1])
      elif keyword == "no. points":
        self.npoints = int(tok[1])
      elif keyword == "dimensions":
        if self.npoints == 0:
          print('Error: misplaced "Dimensions:" lineprint')
          continue
        print('Warning: "Dimensions" not supported yet')
        # FIXME: How can I create such simulation files?
        # numdims = int(tok[1])
      elif keyword == "command":
        print('Warning: "command" option not implemented yet')
        print('\t' + line)
        # FIXME: what is this command good for
      elif keyword == "option":
        print('Warning: "command" option not implemented yet')
        print('\t' + line)
        # FIXME: what is this command good for
      elif keyword == "variables":
        for i in range(self.nvars):
          line_bytes = f.readline()
          linestr = line_bytes.decode('utf-8')          
          line = linestr.split()
          if len(line) >= 3:
            number = int(line[0])
            var_name = line[1].replace('@', '')
            var_name = var_name.replace('[i]', '')
            curr_vector = spice_vector(name=var_name,
                                       type=line[2])
            self.vectors.append(curr_vector)
            if len(line) > 3:
              # print("Attributes: ", line[3:])
              dummy =1
              ## min=, max, color, grid, plot, dim
              ## I think only dim is useful and neccesary
          else:
            print("list of variables is too short")

      elif keyword in ["values","binary"]:
        # read the data
        if self.real:
          if keyword == "values":
            i = 0
            a = numpy.zeros(self.npoints*self.nvars, dtype="float64")
            while (i < self.npoints*self.nvars):
              line_bytes = f.readline()
              linestr = line_bytes.decode('utf-8')
              t = linestr.split("\t")
              if len(t) < 2:
                continue
              else:
                a[i] = float(t[1])
              i += 1
          else: ## keyword = "binary"
            a = numpy.frombuffer(f.read(self.nvars*self.npoints*8),
                                 dtype="float64")
          aa = a.reshape(self.npoints,self.nvars)
          self.vectors[0].set_data(aa[:,0])
          self.current_plot.set_scalevector(self.vectors[0])
          for n in range(1,self.nvars):
            self.vectors[n].set_data(aa[:,n])
            self.current_plot.append_datavector(self.vectors[n])

        else: # complex data
          if keyword == "values":
            i = 0
            a = numpy.zeros(self.npoints*self.nvars*2, dtype="float64")
            while (i < self.npoints*self.nvars*2):
              line_bytes = f.readline()
              linestr = line.decode('utf-8')
              t = linestr.split("\t")
              if len(t) < 2:  ## empty lines
                continue
              else:
                t = string.split(t[1],",")
                a[i] = string.atof(t[0])
                i += 1
                a[i] = string.atof(t[1])
                i += 1
          else: ## keyword = "binary"
            a = numpy.frombuffer(f.read(self.nvars*self.npoints*8*2),
                                 dtype="float64")
          aa = a.reshape(self.npoints, self.nvars*2)
          self.vectors[0].set_data(aa[:,0]) ## only the real part!
          self.current_plot.set_scalevector(self.vectors[0])
          for n in xrange(1,self.nvars):
            self.vectors[n].set_data(numpy.array(aa[:,2*n]+
                                                 1j*aa[:,2*n+1]))
            self.current_plot.append_datavector(self.vectors[n])

        # create new plot after the data
        self.plots.append(self.current_plot)
        self.set_default_values()

      elif keyword.strip() == "": ## ignore empty lines
        continue

      else:
        print('Error: strange line in rawfile:\n\t"'  \
              + str(line) + '"\n\t load aborted')
        return 0

  def get_plots(self):
    return self.plots

  def dumpSpiceData(self, rawfn):
    print('The file: "' + rawfn + '" contains the following plots:')
    for i,p in enumerate(spice_read(rawfn).get_plots()):
      print('  Plot', i, 'with the attributes')
      print('    Title: ' , p.title)
      print('    Date: ', p.date)
      print('    Plotname: ', p.plotname)
      print('    Plottype: ' , p.plottype)

      s = p.get_scalevector()
      print('    The Scale vector has the following properties:')
      print('      Name: ', s.name)
      print('      Type: ', s.type)
      v = s.get_data()
      print('      Vector-Length: ', len(v))
      print('      Vector-Type: ', v.dtype)

      for j,d in enumerate(p.get_datavectors()):
        print('    Data vector', j, 'has the following properties:')
        print('      Name: ', d.name)
        print('      Type: ', d.type)
        v = d.get_data()
        print('      Vector-Length: ', len(v))
        print('      Vector-Type: ', v.dtype)
        print(str(v))

  def loadSpiceVoltages(self):
    for i,p in enumerate(self.get_plots()):
      s = p.get_scalevector()
      self.spiceScale = s.get_data()

      for j,d in enumerate(p.get_datavectors()):
        v = d.get_data()
        variableName = d.name
        variableName = variableName.lower()

        voltageRE= re.match(r'[vV]\(([^\)]+)\)', variableName)
        if voltageRE:
          varName = voltageRE.group(1)
          self.spiceVoltage[str(varName)]= v
          print("Loading spice voltage name: " + str(varName))
          continue
        
        if ("[i]" in variableName) and ('@' in variableName):
          variableName = variableName.replace('[i]', '')
          variableName = variableName.replace('@', '')

        currentRE= re.match(r'[iI]\(([^\)]+)\)', variableName)
        if currentRE:
          varName = currentRE.group(1)
          self.spiceCurrent[str(varName)]= v
          continue   

        currentREXyce= re.match(r'([^#]+)#branch$', variableName)
        if currentREXyce:
          varName= currentREXyce.group(1)
          if ':' in varName:
            # print("Loading Xyce-style current name " + str(varName))
            subcktFields = varName.split(':')
            endIdx = len(subcktFields) - 1
            subcktFields[endIdx] = str(subcktFields[0]) + str(subcktFields[endIdx])
            varName = '.'.join(subcktFields)
            # print("Translated Xyce-style current name to " + str(varName))
          self.spiceCurrent[str(varName)] = v
          continue

        if ':' in variableName:
          varName= variableName.replace(':','.')
          self.spiceVoltage[str(varName)] = v
          continue

  def v(self, voltageName):
    if voltageName not in self.spiceVoltage:
      print("Error: voltage " + str(voltageName) + " not found in raw file")
      return ''
    else:
      return self.spiceVoltage[voltageName]

  def i(self, currentName):
    if currentName not in self.spiceCurrent:
      print("Error: current " + str(currentName) + " not found in raw file")
      return ''
    else:
      return self.spiceCurrent[currentName]

  def t(self):
    return self.spiceScale

  def getVoltageNames(self):
    return self.spiceVoltage.keys()

  def getCurrentNames(self):
    return self.spiceCurrent.keys()



if __name__ == "__main__":

  # TODO: Should include the netlists inline, and test with the
  # modules to run the available simulators on all the netlists.

  reader1= spice_read('ngtest.raw')
  if reader1 is None:
    print("file ngtest.raw not found, bailing out")
    exit
  reader1.loadSpiceVoltages()
  r1v2= reader1.v('v2')
  print(str(r1v2))
  r1lin= reader1.i('lin')
  print(str(r1lin))
  print("Voltages")
  print(reader1.getVoltageNames())
  print("Currents")
  print(reader1.getCurrentNames())

  reader2= spice_read('t/t1.raw')
  if reader2 is None:
    print("file t/t1.raw not found, bailing out")
    exit  
  reader2.loadSpiceVoltages()
  r2v2= reader2.v('3')
  print(str(r2v2))
  r2x1_3= reader2.v('x1.3')
  print(str(r2x1_3))
  print("Voltages")
  print(reader2.getVoltageNames())
  print("Currents")
  print(reader2.getCurrentNames())

  print('Xyce example 1')
  reader3= spice_read('t/x1.raw')
  reader3.loadSpiceVoltages()
  r3v2= reader3.v('3')
  print(str(r3v2))
  r3x1_3= reader3.v('x1.3')
  print(str(r3x1_3))
  print("Voltages")
  print(reader3.getVoltageNames())
  print("Currents")
  print(reader3.getCurrentNames())

  print('Xyce example 2')
  reader3= spice_read('t/xx1.raw')
  reader3.loadSpiceVoltages()
  r3v2= reader3.v('3')
  print(str(r3v2))
  r3x1_3= reader3.v('x1.3')
  print(str(r3x1_3))
  print("Voltages")
  print(reader3.getVoltageNames())
  print("Currents")
  print(reader3.getCurrentNames())