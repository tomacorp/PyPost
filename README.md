# PyPost
**Graph and post process simulator data**

PyPost is intended to be a replacement for Nutmeg,
which is the post processor for data created by NGSpice and other circuit simulators.
The advantage of this program is that it uses Qt and does not require X-Windows.
It is written in Python and uses matplotlib.
A Python REPL loop is the expression evaluator.
This brings in a large number of commands from Python, Numpy, and other modules.

PyPost is an iPython alternative designed for engineers working with simulators.
If you are not interacting with a circuit simulator, you might prefer iPython.

## Setting the circuit name

`ci <fn>`

Stands for 'circuit is: '.
Sets the name of the circuit to be sent to the simulator.
`<fn>` is the base name of the simulation deck.

## Expressions

`<expr>`

Evaluates an expression. Expressions have access to simulator results.
Voltages are v(netname) and currents are i(devicename).
The time axis is the variable t
Expressions can also be vectors or other numpy expressions.
Expressions can have side effects, since much of the Python language and numpy is available.

## Drawing graphs

`gr <expr>`

Graphs and expression versus xname. If there is no x-axis, a list of integers starting at 0 are used instead.

`gs`

Graph using the same axes.

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

`set xname x`

## Simulator Commands

`si`

Runs the circuit simulator on the current simulation deck.

`si <filename>`

Runs the circuit simulator on the specified file.

`ci <basename>`

Sets the simulator base file name to <basename>.
This example sets the simulation basename to ngtest in the directory t:

`ci t/ngtest`

The simulator uses the basename to create file names.

For NGSpice, the input file will be `t/ngtest.cki`

The output file will be `t/ngtest.raw`

`ci`
Displays the current simulation base file name

`history`
Show past commands entered into the post processor.
The arrow keys also work to recall previous commands.

`readh5`
Not implemented yet.

## Running scripts

`include <filename>`
Reads the file at `<filename>` and executes it as a list of commands as if they were typed in.

`. <filename>`
Synonym for include. Saves typing.

`__di__`
Displays the simulation variables that are available to be plotted or used in expressions.
