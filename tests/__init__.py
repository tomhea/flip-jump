"""
the flipjump test package.
registers pytest assert-rewriting for the quickstart module so that assertion failures
inside the flipjump test-helpers show their detailed mismatch values.
"""

import pytest

pytest.register_assert_rewrite("flipjump.flipjump_quickstart")
