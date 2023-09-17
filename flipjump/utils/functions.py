from __future__ import annotations

import json
import lzma
import os
from pathlib import Path
from typing import List, Dict, Tuple, Union

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


def get_file_tuples(files: List[str], *, no_stl: bool = False) -> List[Tuple[str, Path]]:
    """
    get the list of .fj files to be assembled (stl + files).
    @param files: the list of fj-code files.
    @param no_stl: if True: don't include the standard library.
    @return: a list of file-tuples - (file_short_name, file_path)
    """
    file_tuples = []

    if not no_stl:
        for i, stl_path in enumerate(get_stl_paths(), start=1):
            file_tuples.append((f"s{i}", stl_path))

    for i, file in enumerate(files, start=1):
        file_tuples.append((f"f{i}", Path(file)))

    return file_tuples


def get_temp_directory_suffix(files: List[Union[Path, str]]) -> str:
    """
    create a suffix for the temp directory name, using args.
    @param files: the list of fj-code files.
    @return: the suffix
    """
    return f'__{"_".join(map(os.path.basename, files))}__temp_directory'
