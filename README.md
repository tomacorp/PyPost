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

__expr__
Evaluates an expression. Expressions have access to simulator results.
Voltages are v(netname) and currents are i(devicename).
The time axis is the variable t
Expressions can also be vectors or other numpy expressions.
Expressions can have side effects, since much of the Python language is available.

__gr expr__
Graphs and expression versus xname. If there is no x-axis, a list of integers starting at 0 are used instead.

__gs__
Graph using the same axes.

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

__si__
Runs the circuit simulator on the current simulation deck.

__si <filename>__
Runs the circuit simulator on the specified file.

__history__
Show past commands.

__readh5__
Not implemented yet.

__include <filename>__
Reads the file for and executes it as a list of commands.

__. <filename>__
Synonym for include. Saves typing.

__di__
Displays the simulation variables that are available to be plotted or used in expressions.
