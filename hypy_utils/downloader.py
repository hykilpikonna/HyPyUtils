from __future__ import annotations

import os
from pathlib import Path

import requests
import tqdm


def download_file(url: str, file: str | Path, progress: bool = True):
    """
    Helper method handling downloading large files from `url` to `filename`.
    Returns a pointer to `filename`.
    https://stackoverflow.com/a/42071418/7346633
    """
    file = Path(file)
    if file.is_file():
        return file

    chunk_size = 1024

    try:
        term_len = os.get_terminal_size().columns
        bar_len = int(term_len * 0.4)
    except Exception:
        term_len = 60
        bar_len = 20

    tqdm_args = dict()
    r = requests.get(url, stream=True)
    if 'content-length' in r.headers:
        tqdm_args['total'] = int(r.headers['content-length']) / 1024 / 1024

    with open(file, 'wb') as f:
        pbar = None
        if progress:
            pbar = tqdm.tqdm(unit=" MB", ncols=term_len,
                             bar_format='{desc} {rate_noinv_fmt} {remaining} [{bar}] {percentage:.0f}%', ascii=' #',
                             desc=file.name[:bar_len].ljust(bar_len), **tqdm_args)

        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                if pbar:
                    pbar.update(len(chunk) / 1024 / 1024)
                f.write(chunk)

    return file
