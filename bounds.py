"""Rigorous lower bounds on the side of the smallest square holding n hats.

    python bounds.py            # prints a table for n in N_VALUES (1..25, 50, 100)

area_bound(n)  : side >= sqrt(n * 8*sqrt(3)), since n hats need area n*8*sqrt(3).
n1_bound()     : (lower, upper, best_deg) for one hat. side(theta) = max(width, height) of the
                 rotated hat is scanned on a grid of step STEP_DEG; side(theta) is Lipschitz with
                 constant <= DIAMETER (it is a max of functions (p_i - p_j) . u(theta)), hence
                 min side >= grid_min - DIAMETER * step_rad / 2.  upper = grid_min is attained.
lower_bound(n) : max(n1 lower bound, area_bound(n)); the area bound already wins for n >= 2.
best_known(path): optional organiser-maintained CSV "n,side" (missing file -> {}).
"""
import csv
import os
from functools import lru_cache

import numpy as np

from tile import AREA, DIAMETER, HAT

N_VALUES = list(range(1, 26)) + [50, 100]     # the same 27 groups as metric.N_VALUES
STEP_DEG = 0.001


def area_bound(n: int) -> float:
    return float(np.sqrt(n * AREA))


def side_of_rotation(deg) -> np.ndarray:
    """Side of the bounding square of the hat rotated by `deg` (scalar or array)."""
    t = np.radians(np.atleast_1d(deg).astype(float))
    xs = np.outer(np.cos(t), HAT[:, 0]) - np.outer(np.sin(t), HAT[:, 1])
    ys = np.outer(np.sin(t), HAT[:, 0]) + np.outer(np.cos(t), HAT[:, 1])
    return np.maximum(np.ptp(xs, axis=1), np.ptp(ys, axis=1))


@lru_cache(maxsize=None)
def n1_bound() -> tuple[float, float, float]:
    """(rigorous lower bound, attained upper bound, angle in degrees of the upper bound)."""
    grid = np.arange(0.0, 180.0, STEP_DEG)
    sides = side_of_rotation(grid)
    k = int(np.argmin(sides))
    upper = float(sides[k])
    lower = upper - DIAMETER * np.radians(STEP_DEG) / 2
    return lower, upper, float(grid[k])


def lower_bound(n: int) -> float:
    return max(n1_bound()[0], area_bound(n))


def score_bound(n_values=N_VALUES) -> float:
    """Lower bound on the total score sum_n side_n^2 / n over the given groups."""
    return sum(lower_bound(n) ** 2 / n for n in n_values)


def best_known(path: str = "best_known.csv") -> dict[int, float]:
    if not os.path.exists(path):
        return {}
    with open(path, newline="") as f:
        return {int(r["n"]): float(r["side"]) for r in csv.DictReader(f)}


if __name__ == "__main__":
    lo, up, deg = n1_bound()
    known = best_known()
    print(f"n=1 exact: side in [{lo:.5f}, {up:.5f}], attained at {deg:.3f} deg (step {STEP_DEG} deg)")
    print(f"{'n':>3} {'area bound':>11} {'lower bound':>12} {'bound^2/n':>10} {'best known':>11}")
    for n in N_VALUES:
        b = lower_bound(n)
        bk = f"{known[n]:.4f}" if n in known else "-"
        print(f"{n:>3} {area_bound(n):>11.4f} {b:>12.4f} {b * b / n:>10.3f} {bk:>11}")
    print(f"score lower bound: {score_bound():.3f}")
