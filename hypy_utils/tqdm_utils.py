"""
Importing this file requires installing tqdm.
"""
from __future__ import annotations

import os
from functools import partial
from typing import Callable, Iterable

import tqdm
from tqdm.contrib.concurrent import process_map, thread_map


def smap(fn: Callable, lst: Iterable, *args, **kwargs) -> list:
    return [fn(i) for i in tqdm.tqdm(lst, position=0, leave=True, *args, **kwargs)]


def pmap(fn: Callable, lst: Iterable, *args, **kwargs) -> list:
    tqdm_args = dict(position=0, leave=True, chunksize=1, tqdm_class=tqdm.tqdm, max_workers=os.cpu_count())
    tqdm_args.update(kwargs)
    return process_map(fn, lst, *args, **tqdm_args)


def tmap(fn: Callable, lst: Iterable, *args, **kwargs) -> list:
    tqdm_args = dict(position=0, leave=True, chunksize=1, tqdm_class=tqdm.tqdm, max_workers=os.cpu_count())
    tqdm_args.update(kwargs)
    return thread_map(fn, lst, *args, **tqdm_args)


def tq(it: Iterable, desc: str, *args, **kwargs) -> tqdm:
    tqdm_args = dict(position=0, leave=True)
    return tqdm.tqdm(it, desc, *args, **{**tqdm_args, **kwargs})


def patch_tqdm():
    tqdm_args = dict(chunksize=1, position=0, leave=True, tqdm_class=tqdm.tqdm, max_workers=os.cpu_count())
    tq: Callable[[Iterable], tqdm.tqdm] = partial(tqdm.tqdm, position=0, leave=True)
    pmap = partial(process_map, **tqdm_args)
    tmap = partial(thread_map, **tqdm_args)
    return tq, pmap, tmap
