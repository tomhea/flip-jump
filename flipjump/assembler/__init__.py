"""
the assembler subpackage.
compiles flipjump source files into a .fjm binary, and exposes the main assemble() entry
point.
"""

from flipjump.assembler.assembler import assemble


__all__ = [
    'assemble',
]
