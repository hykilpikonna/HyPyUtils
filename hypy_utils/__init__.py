from __future__ import annotations

__version__ = "1.0.10"

import dataclasses
import hashlib
import json
import time
from datetime import datetime, date
from pathlib import Path
from typing import Union, Callable


def ansi_rgb(r: int, g: int, b: int, foreground: bool = True) -> str:
    """
    Convert rgb color into ANSI escape code format

    :param r:
    :param g:
    :param b:
    :param foreground: Whether the color applies to forground
    :return: Escape code
    """
    c = '38' if foreground else '48'
    return f'\033[{c};2;{r};{g};{b}m'


replacements = ["&0/\033[0;30m", "&1/\033[0;34m", "&2/\033[0;32m", "&3/\033[0;36m", "&4/\033[0;31m",
                "&5/\033[0;35m", "&6/\033[0;33m", "&7/\033[0;37m", "&8/\033[1;30m", "&9/\033[1;34m",
                "&a/\033[1;32m", "&b/\033[1;36m", "&c/\033[1;31m", "&d/\033[1;35m", "&e/\033[1;33m",
                "&f/\033[1;37m",
                "&r/\033[0m", "&l/\033[1m", "&o/\033[3m", "&n/\033[4m", "&-/\n"]
replacements = [(r[:2], r[3:]) for r in replacements]


def color(msg: str) -> str:
    """
    Replace extended minecraft color codes in string

    :param msg: Message with minecraft color codes
    :return: Message with escape codes
    """
    for code, esc in replacements:
        msg = msg.replace(code, esc)

    while '&gf(' in msg or '&gb(' in msg:
        i = msg.index('&gf(') if '&gf(' in msg else msg.index('&gb(')
        end = msg.index(')', i)
        code = msg[i + 4:end]
        fore = msg[i + 2] == 'f'

        if code.startswith('#'):
            rgb = tuple(int(code.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        else:
            code = code.replace(',', ' ').replace(';', ' ').replace('  ', ' ')
            rgb = tuple(int(c) for c in code.split(' '))

        msg = msg[:i] + ansi_rgb(*rgb, foreground=fore) + msg[end + 1:]

    return msg


def printc(msg: str):
    """
    Print with color

    :param msg: Message with minecraft color codes
    """
    print(color(msg + '&r'))


def parse_date_time(iso: str) -> datetime:
    """
    Parse date faster. Running 1,000,000 trials, this parse_date function is 4.03 times faster than
    python's built-in dateutil.parser.isoparse() function.

    Preconditions:
        - iso is the output of datetime.isoformat() (In a format like "2021-10-20T23:50:14")
        - iso is a valid date (this function does not check for the validity of the input)

    :param iso: Input date
    :return: Datetime object
    """
    return datetime(int(iso[:4]), int(iso[5:7]), int(iso[8:10]),
                    int(iso[11:13]), int(iso[14:16]), int(iso[17:19]))


def parse_date_only(iso: str) -> datetime:
    """
    Parse date faster.

    Preconditions:
        - iso starts with the format of "YYYY-MM-DD" (e.g. "2021-10-20" or "2021-10-20T10:04:14")
        - iso is a valid date (this function does not check for the validity of the input)

    :param iso: Input date
    :return: Datetime object
    """
    return datetime(int(iso[:4]), int(iso[5:7]), int(iso[8:10]))


class EnhancedJSONEncoder(json.JSONEncoder):
    """
    An improvement to the json.JSONEncoder class, which supports:
    encoding for dataclasses, encoding for datetime, and sets
    """

    def default(self, o: object) -> object:

        # Support encoding dataclasses
        # https://stackoverflow.com/a/51286749/7346633
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)

        # Support encoding datetime
        if isinstance(o, (datetime, date)):
            return o.isoformat()

        # Support for sets
        # https://stackoverflow.com/a/8230505/7346633
        if isinstance(o, set):
            return list(o)

        return super().default(o)


def json_stringify(obj: object, indent: Union[int, None] = None) -> str:
    """
    Serialize json string with support for dataclasses and datetime and sets and with custom
    configuration.

    Preconditions:
        - obj != None

    :param obj: Objects
    :param indent: Indent size or none
    :return: Json strings
    """
    return json.dumps(obj, indent=indent, cls=EnhancedJSONEncoder, ensure_ascii=False)


def write(file: Union[str, Path], text: str) -> None:
    """
    Write text to a file

    Preconditions:
        - file != ''

    :param file: File path (will be converted to lowercase)
    :param text: Text
    :return: None
    """
    file = Path(file)
    file.parent.mkdir(parents=True, exist_ok=True)

    with file.open('w', encoding='utf-8') as f:
        f.write(text)


def read(file: Union[str, Path]) -> str:
    """
    Read file content

    Preconditions:
        - file != ''

    :param file: File path (will be converted to lowercase)
    :return: None
    """
    return file.read_text('utf-8')


def md5(file: Union[str, Path]) -> str:
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


class Timer:
    start: int

    def __init__(self):
        self.reset()

    def elapsed(self, reset: bool = True) -> float:
        t = (time.time_ns() - self.start) / 1000000
        if reset:
            self.reset()
        return t

    def log(self, *args):
        print(f'{self.elapsed():.0f}ms', *args)

    def reset(self):
        self.start = time.time_ns()


def mem(var: str):
    print(f'Memory usage for {var}: {eval(f"sys.getsizeof({var})") / 1024:.1f}KB')


def run_time(func: Callable, *args, **kwargs):
    name = getattr(func, '__name__', 'function')
    start = time.time_ns()
    iter = kwargs.pop('iter', 10)
    _ = [func(*args, **kwargs) for _ in range(iter)]
    ms = (time.time_ns() - start) / 1e6
    print(f'RT {name:30} {ms:6.1f} ms')
