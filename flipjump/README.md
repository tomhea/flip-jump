# FlipJump Source Code

## The FlipJump Macro-Assembler

The assembler has 4 steps:
- parsing the .fj text files into a dictionary of macros and their ops ([fj_parser.py](assembler/fj_parser.py)).
- resolving (unwinding) the macros (and reps) to get a straight stream of ops ([preprocessor.py](assembler/preprocessor.py)).
- resolving the label values and getting the ops binary data ([assembler.py](assembler/assembler.py)). 
- writing the binary data into the executable ([fjm.py](fjm/fjm_reader.py)).

The whole process is executed within the [assemble()](assembler/assembler.py) function.
![Assembly of calc.fj](../res/calc__asm.jpg)

- The [ops.py](inner_classes/ops.py) file contains the classes of the different ops.
- The [expr.py](inner_classes/expr.py) file contains the expression class (Expr), used to maintain a mathematical expression based on numbers and labels.

## The FlipJump Interpreter

The Interpreter ([fjm_run.py](interpretter/fjm_run.py)) stores the entire memory in a dictionary {address: value}, and supports unaligned-word access. 

The whole interpretation is done within the [run()](interpretter/fjm_run.py) function (also uses [fjm.py](fjm/fjm_reader.py) to read the fjm file).
![Running the compiled calculator](../res/calc__run.jpg)

The Interpreter has a built-in debugger, and it's activated by specifying breakpoints when called (via the [BreakpointHandler](debugging/breakpoints.py)).
The debugger can stop on the next breakpoint, or on a fixed number of executed ops after the current breakpoint.
In order to call the debugger with the right labels, get familiar with the [generating label names](README.md#Generated-Label-Names) (and see the debugger-image there).

The [macro_usage_graph.py](debugging/macro_usage_graph.py) file allows presenting the macro-usage in a graph:
![The macro-usage statistics of calc.fj](../res/calc_stats.png)

### FJM versions

The .fjm file currently has 4 versions:

- Version 0: The basic version
- Version 1: The normal version (more configurable than the basic version)
- Version 2: The relative-jumps version (good for further compression)
- Version 3: The compressed version

You can specify the version you want with the `-v VERSION` flag.<br>
The assembler chooses **by default** version **3** if the `--outfile` is specified, and version **1** if it isn't. 

### Generated Label Names

The generated label string is a concatenation of the macro call tree, each separated by '---', and finish with the label local-name.

Each macro call string is as follows:\
short_file_name **:** line **:** macro_called

So if a->bit.b->hex.c->my_label: (a, bit.b called from file f2 lines 3,5; hex.c from file s1, line 72), the label's name will be:\
f2:3:a---f2:5:bit.b---s1:72:hex.c---my_label

On a rep-call (on index==i), the macro call string is:\
short_file_name : line : rep{i} : macro_called\
for example: f1:32:rep6:hex.print---f2:17:print_bit---print_label

the short_file_name is (by default) s1,s2,s3,.. for the standard library files (in the order of [stl/conf.json - all](stl/conf.json)),
and f1,f2,f3,.. for the compiled .fj files, in the order they are mentioned to the compiler (or appear in the test-line).

You can place breakpoints to stop on specific labels using the `-d`, followed by a  `-b` and a label name (or `-B` and a part of a label name). For example:
![Debugging Demo](../res/breakpoint.jpg)

## More Files

- The [fj.py](fj.py) file is the main FlipJump cli-script. run with --help to see its capabilities.
- The [fjm.py](fjm/fjm_reader.py) file helps to read and write a .fjm file.
- The [defs.py](utils/constants.py) file contains functionality used across the source files, and the project's definitions.
- The [exceptions.py](inner_classes/exceptions.py) file contains exceptions definitions.
- The [io_devices/](io_devices) folder contains modules for different Input/Output-handling classes. The standard one is [StandardIO.py](io_devices/StandardIO.py), and the tests uses the [FixedIO.py](io_devices/FixedIO.py).


# Read More

The FlipJump source is built in a way that allows simple addition of new features.

Every addition should be supported from the parsing level to the phase that is disappears, in the progression found in assemble() in [assembler](assembler/assembler.py).

For example, if you want to add a new operation a@b that calculates a^2+b^2 or a! for factorial(a), it is simple as adding a parsing rule in [fj_parser.py](assembler/fj_parser.py), then adding the function to the op_string_to_function() in [expr.py](inner_classes/expr.py).

