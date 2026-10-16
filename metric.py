"""Official judge for "Pack the einsteins": parses, validates and scores a submission.

    python metric.py submission.csv       # per-n table + TOTAL, or "INVALID: <reason>" and exit 1

Submission CSV, columns id,x,y,deg,flip (extra columns ignored, row order irrelevant):
    id   = "<n:03d>_<i>" for n in N_VALUES (1..25, 50, 100) and i = 0..n-1, e.g. 003_2, 100_0;
           exactly these 475 ids once each
    x, y = centroid of the hat, finite decimals in [-COORD_LIMIT, COORD_LIMIT]
    deg  = rotation in degrees, counter-clockwise, any finite real
    flip = 0 or 1 (1 = mirror image)
Validity: in each group n, two hats overlap iff they intersect, do not merely touch, and their
intersection area exceeds EPS_AREA. Touching along edges or at points is allowed.
Score: side_n = max(width, height) of the bounding box of all hats of group n;
    total = sum_n side_n^2 / n   (lower is better; as in Kaggle Santa 2025).
Library: load(path) -> {n: [EinsteinHat]}, validate(hats_by_n), side_length(hats),
         score(hats_by_n) -> (total, {n: side}), score_file(path) -> (total, {n: side}).
"""
import csv
import math
import sys
from decimal import Decimal, InvalidOperation

from shapely.ops import unary_union
from shapely.strtree import STRtree

import bounds
from tile import AREA, EinsteinHat

N_VALUES = list(range(1, 26)) + [50, 100]     # the 27 groups, in id order
COORD_LIMIT = 100.0
EPS_AREA = 1e-9          # intersection area up to this counts as touching
COLUMNS = ["id", "x", "y", "deg", "flip"]


class InvalidSubmission(Exception):
    pass


def expected_ids() -> list[str]:
    return [f"{n:03d}_{i}" for n in N_VALUES for i in range(n)]


def _number(value: str, field: str, hat_id: str) -> float:
    try:
        d = Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        d = Decimal("nan")
    if not d.is_finite() or not math.isfinite(float(d)):
        raise InvalidSubmission(f"{field} of {hat_id} is not a finite number: '{value}'")
    return float(d)


def load(path: str) -> dict[int, list[EinsteinHat]]:
    """Parse and format-check a submission; returns hats grouped by n, in index order."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        for c in COLUMNS:
            if c not in header:
                raise InvalidSubmission(f"missing column '{c}'")
        rows = list(reader)
    wanted = set(expected_ids())
    seen, hats = {}, {n: [None] * n for n in N_VALUES}
    for r in rows:
        hat_id = (r["id"] or "").strip()
        if hat_id not in wanted or hat_id in seen:
            raise InvalidSubmission(f"unknown or duplicate id '{hat_id}'")
        seen[hat_id] = True
        x = _number(r["x"], "x", hat_id)
        y = _number(r["y"], "y", hat_id)
        deg = _number(r["deg"], "deg", hat_id)
        if not (-COORD_LIMIT <= x <= COORD_LIMIT and -COORD_LIMIT <= y <= COORD_LIMIT):
            raise InvalidSubmission(f"x and/or y of {hat_id} outside -{COORD_LIMIT:g}..{COORD_LIMIT:g}")
        flip = _number(r["flip"], "flip", hat_id)
        if flip not in (0.0, 1.0):
            raise InvalidSubmission(f"flip of {hat_id} must be 0 or 1")
        n, i = (int(s) for s in hat_id.split("_"))
        hats[n][i] = EinsteinHat(x, y, deg, flip == 1.0)
    for n in N_VALUES:
        missing = [f"{n:03d}_{i}" for i, h in enumerate(hats[n]) if h is None]
        if missing:
            raise InvalidSubmission(f"missing ids for n={n}: {', '.join(missing)}")
    return hats


def overlapping_pairs(hats: list[EinsteinHat]) -> list[tuple[int, int, float]]:
    """All (i, j, area) with i < j whose hats overlap by more than EPS_AREA."""
    polys = [h.polygon for h in hats]
    tree = STRtree(polys)
    bad = []
    for i, p in enumerate(polys):
        for j in tree.query(p):
            j = int(j)
            if j <= i:
                continue
            q = polys[j]
            if p.intersects(q) and not p.touches(q):
                area = p.intersection(q).area
                if area > EPS_AREA:
                    bad.append((i, j, area))
    return bad


def validate(hats_by_n: dict[int, list[EinsteinHat]]) -> None:
    for n, hats in hats_by_n.items():
        bad = overlapping_pairs(hats)
        if bad:
            i, j, area = bad[0]
            raise InvalidSubmission(f"Overlapping hats in group {n:03d}: ids {n:03d}_{i} and {n:03d}_{j} "
                                    f"(area {area:.4g}); {len(bad)} overlapping pair(s)")


def side_length(hats: list[EinsteinHat]) -> float:
    minx, miny, maxx, maxy = unary_union([h.polygon for h in hats]).bounds
    return max(maxx - minx, maxy - miny)


def score(hats_by_n: dict[int, list[EinsteinHat]]) -> tuple[float, dict[int, float]]:
    sides = {n: side_length(hats) for n, hats in hats_by_n.items()}
    return sum(s * s / n for n, s in sides.items()), sides


def score_file(path: str) -> tuple[float, dict[int, float]]:
    hats_by_n = load(path)
    validate(hats_by_n)
    return score(hats_by_n)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__.splitlines()[2].strip())
        return 2
    try:
        total, sides = score_file(argv[0])
    except InvalidSubmission as e:
        print(f"INVALID: {e}")
        return 1
    print(f"{argv[0]}   (EPS_AREA = {EPS_AREA:g})")
    for n, s in sorted(sides.items()):
        b = bounds.lower_bound(n)
        print(f"n={n:>2}  side={s:>8.4f}  side^2/n={s * s / n:>7.3f}  density={n * AREA / s / s:.3f}"
              f"  bound={b:>7.4f}  gap={100 * (s / b - 1):+.1f}%")
    print(f"TOTAL {total:.3f}   (lower bound {bounds.score_bound():.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
