"""
the flipjump unit-tests package.

register_assert_rewrite makes pytest show the detailed assertion-diffs from inside
flipjump.flipjump_quickstart.run_test_output (mirrors tests/__init__.py).
"""

import pytest

pytest.register_assert_rewrite('flipjump.flipjump_quickstart')
