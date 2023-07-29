from __future__ import annotations

import base64
import dataclasses
import datetime
import hashlib
import inspect
import io
import json
import pickle
from enum import Enum
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def pickle_encode(obj: Any, protocol=None, fix_imports=True) -> bytes:
    """
    Encode object to pickle bytes

    >>> by = pickle_encode({'function': pickle_encode})
    >>> len(by)
    57
    >>> decoded = pickle_decode(by)
    >>> by = decoded['function']({'meow': 565656})
    >>> pickle_decode(by)
    {'meow': 565656}
    """
    with io.BytesIO() as bio:
        pickle.dump(obj, bio, protocol=protocol, fix_imports=fix_imports)
        return bio.getvalue()


def pickle_decode(by: bytes) -> Any:
    """
    Decode pickle bytes to object
    """
    with io.BytesIO(by) as bio:
        return pickle.load(bio)


def infer(o: object) -> object | None:
    # Support encoding dataclasses
    # https://stackoverflow.com/a/51286749/7346633
    if dataclasses.is_dataclass(o):
        return dataclasses.asdict(o)

    # Simple namespace
    if isinstance(o, SimpleNamespace):
        return o.__dict__

    # Support encoding datetime
    if isinstance(o, (datetime.datetime, datetime.date)):
        return o.isoformat()

    # Support for sets
    # https://stackoverflow.com/a/8230505/7346633
    if isinstance(o, set):
        return list(o)

    # Support for Path
    if isinstance(o, Path):
        return str(o)

    # Support for byte arrays (encode as base64 string)
    if isinstance(o, bytes):
        return base64.b64encode(o).decode()

    # Enums
    if isinstance(o, Enum):
        return o.name

    return None


class EnhancedJSONEncoder(json.JSONEncoder):
    """
    An improvement to the json.JSONEncoder class, which supports:
    encoding for dataclasses, encoding for datetime, and sets
    """
    def default(self, o: object) -> object:
        return infer(o) or super().default(o)


class ForceJSONEcoder(EnhancedJSONEncoder):
    """
    A json encoder that can serialize almost everything (including custom classes, byte arrays)
    """
    def default(self, o: object) -> object:
        infer_result = infer(o)
        if infer_result:
            return infer_result

        # # Support EnumType
        # if isinstance(o, EnumType):
        #     return {i.name: i.value for i in o}

        # Support for custom classes (get dict values)
        if hasattr(o, '__dict__') and not inspect.isclass(o):
            return dict(vars(o))

        return super().default(o)


def json_stringify(obj: object, forced: bool = True, **kwargs) -> str:
    """
    Serialize json string with support for dataclasses and datetime and sets and with custom
    configuration.

    Preconditions:
        - obj != None

    :param obj: Objects
    :param forced: Whether to force the conversion of classes and byte arrays
    :return: Json strings
    """
    args = dict(ensure_ascii=False, cls=ForceJSONEcoder if forced else EnhancedJSONEncoder)
    args.update(kwargs)
    return json.dumps(obj, **args)


class SafeNamespace(SimpleNamespace):
    def __getattr__(self, attr):
        try:
            return super().__getattr__(attr)
        except AttributeError:
            return None


def jsn(s: str) -> SafeNamespace:
    return json.loads(s, object_hook=lambda d: SafeNamespace(**d))


def ensure_dir(path: Path | str) -> Path:
    """
    Ensure that the directory exists (and create if not)

    :returns The directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_parent(path: Path | str) -> Path:
    """
    Ensure that the parent directory of a path exists (and create if not)

    :return: The directory
    """
    path = Path(path)
    ensure_dir(path.parent)
    return path


def write(fp: Path | str, data: bytes | str):
    """
    Make sure the directory exists, and then write data, either in bytes or string.

    Also forces utf-8 encoding for strings.
    """
    fp = ensure_parent(fp)

    if isinstance(data, str):
        return fp.write_text(data, 'utf-8')
    if isinstance(data, bytes):
        return fp.write_bytes(data)


def read(file: Path | str) -> str:
    """
    Read file content, force utf-8

    :param file: File path
    :return: File content
    """
    return Path(file).read_text('utf-8')


def write_json(fp: Path | str, data: Any, **kwargs):
    write(fp, json_stringify(data, **kwargs))


def parse_date_time(iso: str) -> datetime.datetime:
    """
    Parse date faster. Running 1,000,000 trials, this parse_date function is 4.03 times faster than
    python's built-in dateutil.parser.isoparse() function.

    Preconditions:
        - iso is the output of datetime.isoformat() (In a format like "2021-10-20T23:50:14")
        - iso is a valid date (this function does not check for the validity of the input)

    :param iso: Input date
    :return: Datetime object
    """
    return datetime.datetime(int(iso[:4]), int(iso[5:7]), int(iso[8:10]),
                             int(iso[11:13]), int(iso[14:16]), int(iso[17:19]))


def parse_date_only(iso: str) -> datetime.datetime:
    """
    Parse date faster.

    Preconditions:
        - iso starts with the format of "YYYY-MM-DD" (e.g. "2021-10-20" or "2021-10-20T10:04:14")
        - iso is a valid date (this function does not check for the validity of the input)

    :param iso: Input date
    :return: Datetime object
    """
    return datetime.datetime(int(iso[:4]), int(iso[5:7]), int(iso[8:10]))


def md5(file: Path | str) -> str:
    """
    Compute md5 of a file

    :param file: File path
    :return: md5 string
    """
    file = Path(file)
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
