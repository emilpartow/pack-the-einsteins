"""The judge: score formula, touching vs overlap, and validator rejections."""
import csv

import pytest

import baseline
import metric
from metric import EPS_AREA, InvalidSubmission, EinsteinHat


def test_n_values_27_groups_and_475_ids():
    assert metric.N_VALUES == list(range(1, 26)) + [50, 100] and len(metric.N_VALUES) == 27
    ids = metric.expected_ids()
    assert len(ids) == 475 and len(set(ids)) == 475
    assert ids[0] == "001_0" and ids[1] == "002_0" and ids[324] == "025_24"
    assert ids[325] == "050_0" and ids[375] == "100_0" and ids[-1] == "100_99"
    assert sum(1 for i in ids if i.startswith("025_")) == 25
    assert sum(1 for i in ids if i.startswith("050_")) == 50
    assert sum(1 for i in ids if i.startswith("100_")) == 100
    assert not any(i.startswith(("026_", "030_", "049_", "099_")) for i in ids)


def test_metric_n1_unrotated_scores_36():
    assert abs(metric.side_length([EinsteinHat()]) - 6.0) < 1e-12
    total, sides = metric.score({1: [EinsteinHat()]})
    assert abs(total - 36.0) < 1e-12 and abs(sides[1] - 6.0) < 1e-12


def test_metric_matches_formula_sum_side2_over_n():
    hats = {1: [EinsteinHat(0, 0, 90)], 2: [EinsteinHat(0, 0), EinsteinHat(0, 10)]}
    total, sides = metric.score(hats)
    assert abs(sides[1] - 6.0) < 1e-9        # 90 degrees swaps width 6.0 and height 4.33; side = max
    assert abs(sides[2] - (10 + 4.330127018922193)) < 1e-9
    assert abs(total - (sides[1] ** 2 / 1 + sides[2] ** 2 / 2)) < 1e-12


def test_touching_allowed():
    hats = [EinsteinHat(0, 0), EinsteinHat(6.0, 0)]      # share exactly one vertex
    assert hats[0].polygon.touches(hats[1].polygon)
    assert metric.overlapping_pairs(hats) == []
    metric.validate({2: hats})


def test_touching_along_edge_allowed():
    hats = [EinsteinHat(0, 0), EinsteinHat(0, 2 * 3 ** 0.5)]   # lattice translation: share the 2+sqrt(3) edge
    inter = hats[0].polygon.intersection(hats[1].polygon)
    assert abs(inter.length - (2 + 3 ** 0.5)) < 1e-9 and inter.area <= EPS_AREA
    assert metric.overlapping_pairs(hats) == []
    metric.validate({2: hats})


def test_overlap_rejected():
    with pytest.raises(InvalidSubmission, match="Overlapping hats in group 002"):
        metric.validate({2: [EinsteinHat(0, 0), EinsteinHat(0, 0)]})


def test_overlap_below_eps_allowed():
    hats = [EinsteinHat(0, 0), EinsteinHat(6.0 - 1e-6, 0)]
    area = hats[0].polygon.intersection(hats[1].polygon).area
    assert 0 < area <= EPS_AREA                           # documents what EPS_AREA tolerates
    metric.validate({2: hats})
    hats = [EinsteinHat(0, 0), EinsteinHat(6.0 - 1e-2, 0)]
    assert hats[0].polygon.intersection(hats[1].polygon).area > EPS_AREA
    with pytest.raises(InvalidSubmission):
        metric.validate({2: hats})


def _rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _write(path, rows, columns=metric.COLUMNS):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


@pytest.fixture(scope="module")
def baseline_rows(tmp_path_factory):
    return _rows(baseline.write(str(tmp_path_factory.mktemp("base") / "ok.csv")))


@pytest.mark.parametrize("name, mutate, message", [
    ("missing column", lambda r: ("drop flip", None), "missing column 'flip'"),
    ("bad id", lambda r: r[0].update(id="026_0"), "unknown or duplicate id '026_0'"),
    ("bad id 30", lambda r: r[0].update(id="030_0"), "unknown or duplicate id '030_0'"),
    ("bad id 100_100", lambda r: r[0].update(id="100_100"), "unknown or duplicate id '100_100'"),
    ("duplicate id", lambda r: r[1].update(id="001_0"), "unknown or duplicate id '001_0'"),
    ("missing id", lambda r: r.pop(), "missing ids for n=100: 100_99"),
    ("missing id 25", lambda r: r.pop(324), "missing ids for n=25: 025_24"),
    ("missing id 50", lambda r: r.pop(325), "missing ids for n=50: 050_0"),
    ("nan", lambda r: r[3].update(x="nan"), "x of 003_0 is not a finite number: 'nan'"),
    ("out of range", lambda r: r[3].update(y="100.5"), "x and/or y of 003_0 outside -100..100"),
    ("flip=2", lambda r: r[3].update(flip="2"), "flip of 003_0 must be 0 or 1"),
])
def test_validator_rejects(tmp_path, baseline_rows, name, mutate, message):
    rows = [dict(r) for r in baseline_rows]
    assert len(rows) == 475 and rows[324]["id"] == "025_24" and rows[325]["id"] == "050_0"
    assert rows[375]["id"] == "100_0" and rows[-1]["id"] == "100_99"
    bad = str(tmp_path / "bad.csv")
    if name == "missing column":
        _write(bad, rows, columns=["id", "x", "y", "deg"])
    else:
        mutate(rows)
        _write(bad, rows)
    with pytest.raises(InvalidSubmission, match=message):
        metric.score_file(bad)
