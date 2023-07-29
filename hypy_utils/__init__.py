from __future__ import annotations

__version__ = "1.0.19"

import time
from typing import Callable

from .color_utils import *
from .serializer import *


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
