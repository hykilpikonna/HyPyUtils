from __future__ import annotations

from pathlib import Path

import requests
import tqdm


def download_file(url: str, file: str | Path):
    """
    Helper method handling downloading large files from `url` to `filename`.
    Returns a pointer to `filename`.
    https://stackoverflow.com/a/42071418/7346633
    """
    file = Path(file)
    if file.is_file():
        return file

    chunk_size = 1024
    r = requests.get(url, stream=True)
    with open(file, 'wb') as f:
        pbar = tqdm.tqdm(unit=" MB", total=int(r.headers['Content-Length']) / 1024 / 1024,
                         bar_format='{desc} {rate_fmt} {remaining} [{bar}] {percentage:.0f}%', ascii=' #', desc=file.name[:bar_len].ljust(bar_len))
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                pbar.update(len(chunk) / 1024 / 1024)
                f.write(chunk)
    return file
