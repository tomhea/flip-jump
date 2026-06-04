"""
the fjm subpackage.
reads and writes the .fjm (FlipJump Memory) binary file format, and exposes the FJ_MAGIC
constant and the FJMVersion enum.
"""

from flipjump.fjm.fjm_consts import FJ_MAGIC, FJMVersion

__all__ = [
    'FJ_MAGIC',
    'FJMVersion',
]
