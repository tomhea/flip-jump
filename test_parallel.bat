:: This script executes the flipjump tests in parallel; first compiles the programs, then runs
:: them, and finally runs the assembler/interpreter unit-tests.
:: - Each phase is parallelized with the optimal number of threads.
:: - Each phase is called with the given command-line arguments/flags.

pytest --compile -n auto --ignore=tests/unit %*
pytest --run -n auto --ignore=tests/unit %*
pytest tests/unit --unit-tests -n auto %*
