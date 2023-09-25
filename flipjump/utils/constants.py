from __future__ import annotations

import lzma
from typing import List, Dict


MACRO_SEPARATOR_STRING = "---"
STARTING_LABEL_IN_MACROS_STRING = ':start:'
WFLIP_LABEL_PREFIX = ':wflips:'

LAST_OPS_DEBUGGING_LIST_DEFAULT_LENGTH = 10
DEFAULT_MAX_MACRO_RECURSION_DEPTH = 1000

IO_BYTES_ENCODING = 'raw_unicode_escape'

DEBUG_JSON_ENCODING = 'utf-8'
DEBUG_JSON_LZMA_FORMAT = lzma.FORMAT_RAW
DEBUG_JSON_LZMA_FILTERS: List[Dict[str, int]] = [{"id": lzma.FILTER_LZMA2}]
