# FlipJump Source Code

## The FlipJump Macro-Assembler

The assembler has 4 steps:
- parsing the .fj text files into a dictionary of macros and their ops ([fj_parser.py](fj_parser.py)).
- resolving the macros (and reps) to get a straight stream of ops ([preprocessor.py](preprocessor.py)).
- resolving the labels values and getting the ops binary data ([assembler.py](assembler.py)). 
- writing the binary data into the executable ([fjm.py](fjm.py)).

The whole process is executed within the [assemble()](assembler.py) function.

- The [ops.py](ops.py) file contains the classes of the different ops.
- The [expr.py](expr.py) file contains the expression class (Expr), used to maintain a mathematical expression based on numbers and labels.

## The FlipJump Interpreter

The Interpreter ([fjm_run.py](fjm_run.py)) stores the entire memory in a dictionary {address: value}, and supports unaligned-word access.

The Interpreter has a built-in debugger, and it's activated by specifying breakpoints when called (via a [BreakpointHandler](breakpoints.py)).
The debugger can stop on the next breakpoint, or on a fixed number of executed ops after the current breakpoint.
In order to call the debugger with the right labels, get familiar with the [generating label names](README.md#Generated-Label-Names).

The whole interpretation is done within [run()](fjm_run.py) function.


### Generated Label Names

The generated label string is a concatenation of the macro call tree, each separated by '---', and finish with the label local-name.

Each macro call string is as follows:\
short_file_name : line : macro_called

So if a->bit.b->hex.c->my_label (a,bit.b called from file f2 lines 3,5; hex.c from file s1, line 72), the label's name will be:\
f2:3:a---f2:5:bit.b---s1:72:hex.c---my_label

On a rep-call (on index==i), the macro call string is:\
short_file_name : line : rep{i} : macro_called\
for example: f1:32:rep6:hex.print---print_label


## More Files

- The [fj.py](fj.py) file is the main FlipJump script. run with --help to see its capabilities.
- The [fjm.py](fjm.py) file helps to read and write a .fjm file.
- The [defs.py](defs.py) file contains functionality used across source, and project's definitions.
- The [exceptions.py](exceptions.py) file contains exceptions definitions.




# Read More
