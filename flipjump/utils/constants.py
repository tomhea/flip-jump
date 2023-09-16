from __future__ import annotations

import lzma
from typing import List, Dict


MACRO_SEPARATOR_STRING = "---"
STARTING_LABEL_IN_MACROS_STRING = ':start:'
WFLIP_LABEL_PREFIX = ':wflips:'

LAST_OPS_DEBUGGING_LIST_DEFAULT_LENGTH = 10

io_bytes_encoding = 'raw_unicode_escape'

_debug_json_encoding = 'utf-8'
_debug_json_lzma_format = lzma.FORMAT_RAW
_debug_json_lzma_filters: List[Dict[str, int]] = [{"id": lzma.FILTER_LZMA2}]
