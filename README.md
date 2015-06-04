# PyPost
**Graph and post process simulator data**

For now this program is intended to be a replacement for Nutmeg,
which is the post processor for data created by NGSpice and other circuit simulators.
The advantage of this program is that it uses Qt and does not require X-Windows.
It is written in Python and uses matplotlib.
A Python REPL loop is the expression evaluator.

__ci <fn>__
Stands for 'circuit is: '.
Sets the name of the circuit to be sent to the simulator.
<fn> is the base name of the simulation deck.

__<expr>__
Evaluates an expression. Expressions have access to simulator results.
Voltages are v(netname) and currents are i(devicename).
The time axis is the variable t
Expressions can also be vectors or other numpy expressions.
Expressions can have side effects, since much of the Python language and numpy is available.

__gr <expr>__
Graphs and expression versus xname. If there is no x-axis, a list of integers starting at 0 are used instead.

__gs__
Graph using the same axes.

__<var>=<expr>__
Set a variable <var> to the expression <expr>.
Example:
set xname x
n=201
x=linspace(0, 2*pi, n)
gr sin(10*x)*hanning(n)

__set__
Shows the current values of the plot settings

__set yl <number> <number>__
Sets the y limits of the graph.

__set yl auto__
Sets the y axis to use autoranging.

__set xl <number> <number>__
Sets the x limits of the graph.

__set xl auto__
Sets the x axis to use autoranging.

__set xname <var>__
Sets the sweep variable (x axis) to the variable <var>
Example:
set xname x

__si__
Runs the circuit simulator on the current simulation deck.

__si <filename>__
Runs the circuit simulator on the specified file.

__ci <basename>__
Sets the simulator base file name to <basename>.
This example sets the simulation basename to ngtest in the directory t:
ci t/ngtest
The simulator uses the basename to create file names.
For NGSpice, the input file will be
t/ngtest.cki
The output file will be
t/ngtest.raw

__ci__
Displays the current simulation base file name

__history__
Show past commands.

__readh5__
Not implemented yet.

__include <filename>__
Reads the file at <filename> and executes it as a list of commands as if they were typed in.

__. <filename>__
Synonym for include. Saves typing.

__di__
Displays the simulation variables that are available to be plotted or used in expressions.
