:: This script executes the flipjump tests in parallel; first compiles the program, and then runs them.
:: - Each phase is parallelized with the optimal number of threads.
:: - Each phase is called with the given command-line arguments/flags.

pytest --compile -n auto %*
pytest --run -n auto %*
