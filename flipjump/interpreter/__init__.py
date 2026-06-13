"""
the interpreter subpackage.
runs (and debugs) compiled .fjm programs, and exposes the run() entry point and the
TerminationStatistics result class.
"""

from flipjump.interpreter.fjm_run import TerminationStatistics, run

__all__ = [
    'TerminationStatistics',
    'run',
]
