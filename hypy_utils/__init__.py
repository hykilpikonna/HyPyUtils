from __future__ import annotations

__version__ = "1.0.27"

import time
import logging
from typing import Callable

from .color_utils import *
from .serializer import *


log = logging.getLogger(__name__)


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


def safe(func: Callable, on_error: Callable[[Exception], Any] = None) -> Callable:
    """
    Wrapper for safely executing a function and returning the result of on_error if an exception occurs

    If on_error is None, it will return None on error

    Example Usage:
    >>> safe(lambda x: 1 / x)(0)
    None
    >>> safe(lambda x: 1 / x)(2)
    0.5

    :param func: Function that needs safe execution
    :param on_error: Function to execute when an error occurs
    :return: Wrapped function
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if on_error:
                return on_error(e)
            else:
                log.exception(e)
            return None

    return wrapper

