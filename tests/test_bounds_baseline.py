"""Baseline validity and the lower bounds."""
import numpy as np

import baseline
import bounds
import metric
from tile import EinsteinHat


N_VALUES = list(range(1, 26)) + [50, 100]
GRID_TOTAL = 844.981           # old grid baseline for n = 1..25, kept as baseline.grid_layout
GREEDY_TOTAL_25 = 622.252      # greedy over n = 1..25, pinned to 3 decimals so regressions are caught
GREEDY_TOTAL = 668.907         # greedy over N_VALUES (adds 23.570 for n = 50 and 23.085 for n = 100)


def test_n_values_everywhere():
    assert metric.N_VALUES == bounds.N_VALUES == baseline.N_VALUES == N_VALUES
    assert len(N_VALUES) == 27 and N_VALUES[-2:] == [50, 100]
    assert not hasattr(metric, "N_MAX") and not hasattr(bounds, "N_MAX") and not hasattr(baseline, "N_MAX")


def test_grid_layout_valid_and_total_844_98():
    hats = {n: baseline.grid_layout(n) for n in range(1, 26)}
    metric.validate(hats)
    assert abs(metric.score(hats)[0] - GRID_TOTAL) < 5e-4


def test_baseline_valid_beats_grid_and_total_pinned(tmp_path):
    total, sides = metric.score_file(baseline.write(str(tmp_path / "sample_submission.csv")))
    assert len(sides) == 27 and list(sides) == N_VALUES
    assert abs(total - GREEDY_TOTAL) < 5e-4
    small = sum(s * s / n for n, s in sides.items() if n <= 25)
    assert small < GRID_TOTAL and abs(small - GREEDY_TOTAL_25) < 5e-4
    for n in (50, 100):                                    # the big groups must not be a trivial grid
        assert sides[n] ** 2 / n < 30 and bounds.lower_bound(n) <= sides[n]


def test_bounds_below_baseline(tmp_path):
    _, sides = metric.score_file(baseline.write(str(tmp_path / "sample_submission.csv")))
    for n, side in sides.items():
        assert bounds.lower_bound(n) <= side
    assert bounds.score_bound() < GREEDY_TOTAL
    assert abs(bounds.score_bound() - sum(bounds.lower_bound(n) ** 2 / n for n in N_VALUES)) < 1e-9
    assert abs(bounds.score_bound(range(1, 26)) - sum(bounds.lower_bound(n) ** 2 / n for n in range(1, 26))) < 1e-9
    assert abs(bounds.score_bound() - bounds.score_bound(range(1, 26)) - 2 * 8 * np.sqrt(3)) < 1e-9
    assert abs(bounds.area_bound(2) - np.sqrt(16 * np.sqrt(3))) < 1e-12
    assert abs(bounds.area_bound(25) - np.sqrt(200 * np.sqrt(3))) < 1e-12
    assert abs(bounds.area_bound(100) - np.sqrt(800 * np.sqrt(3))) < 1e-12
    assert bounds.lower_bound(100) == bounds.area_bound(100) > bounds.lower_bound(50) > bounds.lower_bound(25)


def test_bound_n1_brackets_bruteforce():
    lower, upper, deg = bounds.n1_bound()
    brute = min(metric.side_length([EinsteinHat(0, 0, d)]) for d in np.arange(0, 180, 0.05))
    assert lower <= brute and upper <= brute + 1e-9       # upper is attained, so it beats a coarser scan
    assert upper - lower < 1e-4
    assert abs(metric.side_length([EinsteinHat(0, 0, deg)]) - upper) < 1e-9
    assert 5.16309 <= lower <= upper <= 5.16316      # PLAN.md: side in [5.16310, 5.16315]
