"""
the interpretter subpackage - runs (and debugs) compiled .fjm programs.
exposes the run() entry point and the TerminationStatistics result class.
"""

from flipjump.interpretter.fjm_run import TerminationStatistics, run


__all__ = [
    'TerminationStatistics',
    'run',
]
