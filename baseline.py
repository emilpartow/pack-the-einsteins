"""Greedy baseline with rotations and flips (bottom-left greedy, as in the Kaggle Santa 2025 starter).

    python baseline.py [out.csv]        # default: sample_submission.csv; prints total and runtime

For each n in N_VALUES (1..25, 50, 100) the hats are placed one at a time.  The first hat goes to the origin in the pose
(deg, flip) with the smallest bounding square.  Each later hat tries every pose
deg in range(0, 360, ANGLE_STEP) x flip in {0, 1} on 2*K sliding lines: pushed in from the right
along K horizontal lines and from the top along K vertical lines spanning the current bounding
box, stopping (binary search, resolution TOL) as soon as it would come within GAP of a placed
hat, or at the left/bottom wall of the box.  The candidate with the smallest bounding square
wins, ties broken by bounding-box area.  Deterministic.  The judge (metric.overlapping_pairs)
re-checks every group.  grid_layout(n) is the old grid baseline, kept for reference.
The same parameters (ANGLE_STEP = 15, K = 8) serve every n, including n = 50 and 100: measured
on the organiser laptop, n = 50 takes about 2.5 s and n = 100 about 6.5 s, the whole run under 30 s.
"""
import csv
import sys
import time

import numpy as np
import shapely

import metric
from tile import HAT, EinsteinHat

N_VALUES = list(metric.N_VALUES)                 # 1..25, 50, 100
ANGLE_STEP = 15          # degrees
K = 8                    # sliding lines per direction
GAP = 1e-6               # minimum distance between hats (validity never relies on metric.EPS_AREA)
TOL = 1e-4               # binary-search resolution along a sliding line

POSES = [(deg, flip) for deg in range(0, 360, ANGLE_STEP) for flip in (0, 1)]
V = np.array([EinsteinHat(0, 0, d, f).vertices for d, f in POSES])      # (P, 13, 2), centroid at origin
LO, HI = V.min(axis=1), V.max(axis=1)                                    # (P, 2) extents per pose


def grid_layout(n):
    """Old reference baseline: hats on a grid, no rotation, no flips (total 844.981 for n = 1..25)."""
    w, h = np.ptp(HAT, axis=0) + 0.01
    cols = min(range(1, n + 1), key=lambda c: max(c * w, -(-n // c) * h))
    return [EinsteinHat((i % cols) * w - HAT[:, 0].min(), (i // cols) * h - HAT[:, 1].min()) for i in range(n)]


def _free(blocked, verts):
    """verts (M, 13, 2) -> bool (M,): True where the hat is farther than GAP from every placed hat."""
    if len(blocked) == 0:
        return np.ones(len(verts), bool)
    return ~shapely.intersects(blocked[:, None], shapely.polygons(verts)[None, :]).any(axis=0)


def _best_candidate(hats):
    """Slide every pose along 2*K lines into the box of `hats`; return the best EinsteinHat."""
    polys = np.array([h.polygon for h in hats])
    blocked = shapely.buffer(polys, GAP, join_style="mitre")
    shapely.prepare(blocked)
    minx, miny, maxx, maxy = shapely.total_bounds(polys)
    P = len(POSES)
    pose = np.repeat(np.arange(P), 2 * K)
    axis = np.tile(np.r_[np.zeros(K, int), np.ones(K, int)], P)        # 0: moves in x, 1: moves in y
    ys = np.linspace(miny - LO[:, 1], maxy - HI[:, 1], K, axis=1)       # horizontal lines (P, K)
    xs = np.linspace(minx - LO[:, 0], maxx - HI[:, 0], K, axis=1)       # vertical lines (P, K)
    fixed = np.concatenate([ys, xs], axis=1).reshape(-1)
    wall = np.where(axis == 0, minx - LO[pose, 0], miny - LO[pose, 1])
    far = np.where(axis == 0, maxx - LO[pose, 0], maxy - LO[pose, 1]) + 1.0

    def place(t):
        xy = np.where(axis[:, None] == 0, np.c_[t, fixed], np.c_[fixed, t])
        return xy, V[pose] + xy[:, None, :]

    lo, hi = wall, far
    hi = np.where(_free(blocked, place(lo)[1]), lo, hi)                 # nothing in the way: stop at the wall
    while (hi - lo).max() > TOL:
        mid = (lo + hi) / 2
        ok = _free(blocked, place(mid)[1])
        hi, lo = np.where(ok, mid, hi), np.where(ok, lo, mid)
    xy, verts = place(hi)
    ok = _free(blocked, verts)
    w, h = (np.maximum(verts.max(axis=1), [maxx, maxy]) - np.minimum(verts.min(axis=1), [minx, miny])).T
    best = np.lexsort((w * h, np.where(ok, np.maximum(w, h), np.inf)))[0]
    assert ok[best]
    return EinsteinHat(xy[best, 0], xy[best, 1], *POSES[pose[best]])


def greedy_layout(n):
    ext = HI - LO
    first = np.lexsort((ext.prod(axis=1), ext.max(axis=1)))[0]
    hats = [EinsteinHat(0, 0, *POSES[first])]
    while len(hats) < n:
        hats.append(_best_candidate(hats))
    assert not metric.overlapping_pairs(hats), f"greedy produced an overlap for n={n}"
    return hats


def write(path: str = "sample_submission.csv") -> str:
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "x", "y", "deg", "flip"])
        for n in N_VALUES:
            for i, h in enumerate(greedy_layout(n)):
                w.writerow([f"{n:03d}_{i}", f"{h.x:.9f}", f"{h.y:.9f}", f"{h.deg:g}", int(h.flip)])
    return path


if __name__ == "__main__":
    t0 = time.perf_counter()
    out = write(sys.argv[1] if len(sys.argv) > 1 else "sample_submission.csv")
    total, _ = metric.score_file(out)
    print(f"wrote {out}: total {total:.3f} in {time.perf_counter() - t0:.1f} s")
