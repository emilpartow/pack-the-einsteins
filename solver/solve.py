"""The starting solver: every group on a plain grid, no rotation, no flips. Clearly beatable. Replace it.

    python solver/solve.py            # writes submission.csv  (./run.sh does this and then scores it)

Rules of the game live in CHALLENGE.md; metric.py is the only judge. Keep the output format:
one row per hat, columns id,x,y,deg,flip, ids f"{n:03d}_{i}" for every n in metric.N_VALUES.
"""
import csv
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import metric
from tile import HAT, EinsteinHat

GAP = 0.01                                                   # so that grid neighbours never touch
W = float(HAT[:, 0].max() - HAT[:, 0].min()) + GAP           # hat bounding box at 0 degrees: 6.0 x 4.33
H = float(HAT[:, 1].max() - HAT[:, 1].min()) + GAP


def layout(n: int) -> list[EinsteinHat]:
    """Grid with the column count that gives the smallest bounding square."""
    cols = min(range(1, n + 1), key=lambda c: max(c * W, math.ceil(n / c) * H))
    return [EinsteinHat(W * (i % cols), H * (i // cols), 0.0, False) for i in range(n)]


def write(path: str = "submission.csv") -> None:
    with open(path, "w", newline="") as f:
        out = csv.writer(f)
        out.writerow(metric.COLUMNS)
        for n in metric.N_VALUES:
            for i, h in enumerate(layout(n)):
                out.writerow([f"{n:03d}_{i}", f"{h.x:.6f}", f"{h.y:.6f}", f"{h.deg:.6f}", int(h.flip)])
    print(f"wrote {path}")


if __name__ == "__main__":
    write(sys.argv[1] if len(sys.argv) > 1 else "submission.csv")
