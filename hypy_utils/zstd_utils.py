import pickle
from pathlib import Path

import zstandard as zstd
import orjson

from . import write

zstd_d = zstd.ZstdDecompressor()
zstd_c = zstd.ZstdCompressor(level=5, write_checksum=True, threads=-1)


def load_json_zst(file_path: str | Path) -> dict | list:
    """
    Load a .json.zst file and return its parsed content.

    Parameters:
        file_path (str): The path to the .json.zst file.

    Returns:
        dict or list: The parsed JSON content.
    """
    with Path(file_path).open('rb') as f:
        return orjson.loads(zstd_d.stream_reader(f).read())


def write_json_zst(file_path: str | Path, data: dict | list, **kwargs):
    """
    Dump data to a .json.zst file.

    Parameters:
        file_path (str): The path to the .json.zst file.
        data (dict or list): The data to dump.
    """
    write(file_path, zstd_c.compress(orjson.dumps(data, **kwargs)))


def load_pickle_zst(file_path: str | Path):
    with Path(file_path).open('rb') as f:
        return pickle.loads(zstd_d.stream_reader(f).read())


def write_pickle_zst(file_path: str | Path, data):
    write(file_path, zstd_c.compress(pickle.dumps(data)))


if __name__ == '__main__':
    write_pickle_zst('test.pickle.zst', {'a': 1, 'b': 2})
    assert load_pickle_zst('test.pickle.zst') == {'a': 1, 'b': 2}
    write_json_zst('test.json.zst', {'a': 1, 'b': 2})
    assert load_json_zst('test.json.zst') == {'a': 1, 'b': 2}
