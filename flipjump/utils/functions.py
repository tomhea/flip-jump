from __future__ import annotations

import json
import lzma
from pathlib import Path
from typing import List, Dict

from flipjump.utils.constants import _debug_json_encoding, _debug_json_lzma_format, _debug_json_lzma_filters
from importlib.resources import path


def get_stl_paths() -> List[Path]:
    """
    @return: list of the ordered standard-library paths
    """
    with path('flipjump', 'stl') as stl_path:
        with open(stl_path / 'conf.json', 'r') as stl_json:
            stl_options = json.load(stl_json)
        return [stl_path / f'{lib}.fj' for lib in stl_options['all']]


def save_debugging_labels(debugging_file_path: Path, labels: Dict[str, int]) -> None:
    """
    save the labels' dictionary to the debugging-file as lzma2-compressed json
    @param debugging_file_path: the file's path
    @param labels: the labels' dictionary
    """
    if debugging_file_path:
        with open(debugging_file_path, 'wb') as f:
            data = json.dumps(labels).encode(_debug_json_encoding)
            compressed_data = lzma.compress(data, format=_debug_json_lzma_format, filters=_debug_json_lzma_filters)
            f.write(compressed_data)


def load_debugging_labels(debugging_file_path: Path) -> Dict[str, int]:
    """
    loads and decompresses the labels' dictionary from the lzma2-compressed debugging-file
    @param debugging_file_path: the file's path
    @return: the labels' dictionary
    """
    if debugging_file_path:
        with open(debugging_file_path, 'rb') as f:
            compressed_data = f.read()
            data = lzma.decompress(compressed_data, format=_debug_json_lzma_format, filters=_debug_json_lzma_filters)
            return json.loads(data.decode(_debug_json_encoding))
