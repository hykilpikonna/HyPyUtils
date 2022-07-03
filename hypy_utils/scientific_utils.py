"""
Importing this file requires numpy, matplotlib, and numba
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

import numpy as np
from matplotlib import pyplot as plt
from numba import njit


@dataclass
class Statistics:
    mean: float
    median: float
    lower_quartile: float
    upper_quartile: float
    iqr: float
    minimum: float
    maximum: float
    count: int
    total: float

    def get_metric_6(self) -> tuple[float, float, float, float, float, float]:
        return self.mean, self.median, self.minimum, self.maximum, self.lower_quartile, self.upper_quartile


@njit(cache=True)
def _calc_col_stats_helper(col: np.ndarray) -> tuple[float, float, float, float, float, float, float, int, float]:
    q1 = np.quantile(col, 0.25)
    q3 = np.quantile(col, 0.75)
    return (
        float(np.mean(col)),
        float(np.median(col)),
        float(q1),
        float(q3),
        float(q3 - q1),
        float(np.min(col)),
        float(np.max(col)),
        len(col),
        float(np.sum(col))
    )


def calc_col_stats(col: np.ndarray | list) -> Statistics:
    """
    Compute statistics for a data column

    :param col: Input column (tested on 1D array)
    :return: Statistics
    """
    if isinstance(col, list):
        col = np.array(col)
    return Statistics(*_calc_col_stats_helper(col))


def plot(**kwargs) -> plt:
    """
    Pyplot configurator shorthand

    Example: plt_cfg(xlabel="X", ylabel="Y") is equivalent to plt.xlabel("X"); plt.ylabel("Y")
    """
    for k, args in kwargs.items():
        if isinstance(args, dict):
            getattr(plt, k)(**args)
        else:
            getattr(plt, k)(args)
    return plt

