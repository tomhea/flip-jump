# The Testing Arena

## Run the tests:

run `pytest src/` from the project's directory.

Run with `--compile` / `--run` for testing only the compilation / the run.

Add a combination of `--fast`, `--medium`, `--slow`, `--hexlib` to run tests of different types.
Use `--all` to run all the tests. The default (no type flags) means `--fast`.

## Add your tests:

The .csv files in this directory specify which tests to run (and what parameters to use). 

To support more .csv files, update [tests/conf.json](conf.json).<br>
The python test itself can be found on [src/test_fj.py](../src/test_fj.py) (and [src/conftest.py](../src/conftest.py)).

To add a new test, first choose the relevant csv file.<br>
The rule of thumb (for the sum of compile+run times, in seconds):

fast | medium | slow
---|---|---
0 &rarr; 0.5 | 0.5 &rarr; 5 | else

Then add a new line to the relevant compile-csv and run-csv files, according to the next formats.

### Compile CSVs format:

test name | .fj path | out .fjm path | memory width | version | flags | use stl | treat warnings as errors
---|---|---|---|---|---|---|---
example_test | path/to/example.fj | path/to/compiled/example.fjm | 64 | 1 | 0 | True | True

### Run CSVs format:

test name | .fjm path | input file path | output file path | is input a binary file | is output a binary file
---|---|---|---|---|--- 
example_test | path/to/compiled/example.fjm | path/to/inputs/example.in | path/to/outputs/example.out | False | False
