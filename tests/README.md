# The Testing Arena

## Run the tests:

run `pytest` to run the fast tests.

Run with `--compile` / `--run` for testing only the compilation / the run.

Add a combination of `--fast`, `--medium`, `--slow`, `--hexlib` to run tests of different types.<br>
Use `--all` to run all the tests. The default (no type flags) means `--fast`.

### Filter tests by their name 
Multiple flags will take the union of the relevant tests.
 * `--name n1 n2` only run tests with these names.
 * `--contains n1 n2` only run tests containing one of these names.
 * `--startswith n1 n2` only run tests starting with one of these names.
 * `--endswith n1 n2` only run tests ending with one of these names.

## Add your tests:

The .csv files in this directory specify which tests to run (and what parameters to use). 

To support more .csv files, update [conf.json](conf.json).<br>
The python test itself can be found on [test_fj.py](test_fj.py) (and [conftest.py](conftest.py)).

To add a new test, first choose the relevant csv file.<br>
The rule of thumb (for the sum of compile+run times, in seconds):

fast | medium | slow
---|---|---
0 &rarr; 0.5 | 0.5 &rarr; 5 | else

Then add a new line to the relevant compile-csv and run-csv files, according to the next formats.

### Compile CSVs format:

test name | .fj paths | out .fjm path | memory width | version | flags | use stl | treat warnings as errors
---|---|---|---|---|---|---|---
example_test | path/to/example_1.fj &#124; ... &#124; path/to/example_n.fj | path/to/compiled/example.fjm | 64 | 1 | 0 | True | True

### Run CSVs format:

test name | .fjm path | input file path | output file path | is input a binary file | is output a binary file
---|---|---|---|---|--- 
example_test | path/to/compiled/example.fjm | path/to/inputs/example.in | path/to/outputs/example.out | False | False
