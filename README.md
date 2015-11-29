# PyPost

**Graph and post process simulator data**

PyPost is a replacement for NGNutmeg, which is the post processor for data created by NGSpice and other circuit simulators. The advantage of this program is that it uses Qt and does not require X-Windows. It is written in Python and uses matplotlib. A Python REPL loop is the expression evaluator. This brings in a large number of commands from Python, Numpy, and other modules.

PyPost is an iPython alternative designed for engineers working with simulators. If you are not interacting with a circuit simulator, you should probably use iPython instead.

## Setting the circuit name

`ci <fn>`

Stands for 'circuit is: '. It sets the name of the circuit to be sent to the simulator. `<fn>` is the base name of the simulation deck.

## Expressions

`<expr>`

Evaluates an expression. Expressions have access to simulator results. Voltages are ```v(netname)``` and currents are ```i(devicename)``` or ```i(devicename.pin)```. The time axis is stored in the variable ```t```. Expressions can also be vectors or other numpy expressions. Expressions can have side effects. Much of the Python language and numpy is available.

## Drawing graphs

`gr <expr>`

Graphs and expression versus xname. If there is no x-axis, a list of integers starting at 0 are used instead. If the expression is an image, the image is displayed. For now it is not possible to display an image on top of an existing graph. Use the `set graphdev` command to create a new graph using the same axes.

`gs <expr>`

`<var>=<expr>`

Set a variable `<var>` to the expression `<expr>`.

_Example:_

```
set xname x
n=201
x=linspace(0, 2*pi, n)
gr sin(10*x)*hanning(n)
```

## Set Commands

`set`

Shows the current values of the plot settings

`set yl <number> <number>`

Sets the y limits of the graph.

`set yl auto`

Sets the y axis to use autoranging.

`set xl <number> <number>`

Sets the x limits of the graph.

`set xl auto`

Sets the x axis to use autoranging.

`set xname <var>`

Sets the sweep variable (x axis) to the variable <var>
_Example:_

`
set xname x
`

`set graphdev winname`

If the window winname already exists, the set graphdev command sets this window to the active graph. If the window with this name does not exist yet, it creates a new window for drawing graphs or images. The window will appear when a graph or image is drawn on it. The name of the the default graph which appears in the PyPost interface is PyPost_1. It is not yet possible to draw an image in this area.

## Simulator Commands

`si`

Runs the circuit simulator on the current simulation deck.

`si <filename>`

Runs the circuit simulator on the specified file.

`ci <basename>`

Sets the simulator base file name to <basename>. This example sets the simulation basename to ngtest in the directory t:

`ci t/ngtest`

The simulator uses the basename to create file names.

For NGSpice, the input file will be `t/ngtest.cki`

The output file will be `t/ngtest.raw`

`ci`
Displays the current simulation base file name

`history`
Show past commands entered into the post processor. The arrow keys also work to recall previous commands.

`readh5`
Not implemented yet.

`img <filename>`
Reads an image file into a variable. The name of the variable is the basename of the file.
_Example:_

```
img t/yellow.png
```
reads the file in the subdirectory `t` into the variable `yellow`.

## Running scripts

```
include <filename>
```
Reads the file at `<filename>` and executes it as a list of commands as if they were typed in.

```
. <filename>
```
The '.' is a synonym for the include command to save typing.

```
di
```
Displays the simulation variables that are available to be plotted or used in expressions.

```
autoscale
```
Displays the last waveform again and autoscales it. This is useful when the plot range gets messed up by errant pointer manipulation. It is also useful when the gs command is results in a plot that would have been better served by an autoscaled gr command.

## Mouse commands

The mouse scroll-wheel provides zooming and panning for graphs. Depending on where the mouse pointer is located, the wheel has different actions.

Inside the graph area, panning and zooming occurs on the X-axis. In the left and right sides of the graph, the scroll-wheel provides panning. In the middle area of the graph, the scroll-wheel provides zooming.

Outside the graph area, panning and zooming occurs on the Y-axis. In the top and bottom area outside of the graph, the scroll-wheel provides panning. In the middle area outside of the graph, the scroll-wheel provides zooming.

Clicking on a waveform in the graph sets a marker at the X position of the mouse pointer, and it reports the value of the waveform at the Y position corresponding to this X position.

## Bugs

PyPost does not yet handle: 
  - Complex numbers for frequency-domain analysis
  - Multiple datasets in one file
  - There should be a function in ReadSpiceRaw to find the sweep variable,

These are in development, not working yet:
  - Switch back and forth between graphs and images.
  - Arbitrary rawing on top of images.
  - When there is RGBA in the image, it looks like it will not erase. It looks like erasing is perhaps just overwriting, and the black erased image comes through with no alpha?
  - Closing an image window and then asking for an image window again with the same   name ends up with an incorrectly drawn window.
    
See http://stackoverflow.com/questions/9899409/pyside-removing-a-widget-from-a-layout
  
## To Do

Multilayer images with display controls. The existing canvas is mostly just a demo of partially implemented results.

The image canvas should have its own command line for image processing commands, layer commands, markers, etc. Extraction commands could cut 2D slices that would be fed to the plotting commands. The different commands could be done by either prompt, but the shortcuts would be specific to one prompt.

There should also be a 3D canvas that can work on a synthesized stack of 2D layers. This could also have its own command line. This is analogous to the list of waveforms, which are 1D instead of 2D. The 2D layers have the additional requirements of having a stacking order. The 2D waveforms can also be images with more than one color. Color schemes can be generated by a mapping of three layers to RGB values, or a value in a single layer to RGB values. The mappings can be a blue to red for temperature, or blue to yellow for color blind users.

There should also be a launcher that would know how to fire off these different canvases. There needs to be a global space for their communication, and more than one window for results.

A 2D plotting routine can be a projection of 1D data into a 2D vector or raster graphics space. A 3D plotting routine can be a projection of 2D data into a 3D vector graphics space. Different projections are possible, for example a meter can be a projection of 1D data into a position, color, or number that changes over time.

The shortcuts for working with a genre of data such as simulation results in 2D plots makes a good set of commands for a post processor. The question is how to enhance the shortcuts for handling the different data type of 2D and 3D mechanical data for thermal analysis. This could be done by making either:
 - Make the commands coexist without interference
 - Having interface modes
 - Having different command lines

For example, the MagNet program from Infolytica is an electromagnetics program with a programmable calculator having different stacks for the different dimensionalities. For example, dot product pops the bottom two entries from the vector stack and pushes the dot product to the scalar stack. This is clever but has daunting complexity.

Matlab and iPython have one prompt and a rich language, but don't have post processor style shortcuts.

## Install instructions

### Set up git
After installing git don't forget to configure git with your name and email:

```bash
git config --global user.name "Your Name"
git config --global user.email your_name@example.com
```

Install conda from http://continuum.io/downloads

### Create a virtual environment

```bash
virtualenv pypostenv
```

### Install the Python modules

After setting up a virtual environment using conda,
the project can be downloaded and the dependencies installed with

```bash
conda remove pyqt
conda install pyside
conda install matplotlib
pip install fysom
```

### Installing Conda and the modules on Ubuntu

```bash
conda remove pyqt
conda install pyside
conda install matplotlib
conda install anaconda-client
conda install -c auto fysom
```
Next make a virtual conda environment for PyPost

conda create -n pypostenv scipy pandas numpy 
conda install -n pypostenv PySide
conda install -n pypostenv matplotlib
conda install -n pypostenv scikit-image
conda install -n pypostenv h5py
conda install -n pypostenv -c auto fysom

### List the available virtual environments
```bash
conda env list
```

### Install the PyPost python spice post processor
mkdir -p ~/Developer/Python
cd ~/Developer/Python
git clone https://github.com/tomacorp/PyPost.git
cd PyPost

### Use the virtual environment for this project
```bash
source activate pypostenv
```

### Run in the virtual environment
```bash
python ~/shared/PyPost/PyPost/PyPost.py
```

### Running outside of the virtual environment

```bash
~/shared/PyPost/PyPost/pypostenv/bin/python ~/shared/PyPost/PyPost/PyPost.py
```

### Capture a snapshot of the virtual environment
```bash
conda list -e > requirements.txt
```
Have to remove fysom from the requirements.txt, since it comes from an
external server.

### Create a new virtual environment with
conda create -n pypostenv2 --file requirements.txt
conda install -n pypostenv2 -c auto fysom

# List conda virtual environments with
conda info -e

# Select a virtual environment with
source activate pypostenv2

# Remove a conda virtual environment with
conda remove -n pypostenv
