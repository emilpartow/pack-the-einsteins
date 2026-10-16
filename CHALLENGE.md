# Pack the einsteins — the rules

**Task.** For every n in {1, 2, …, 25, 50, 100}, place n copies of the hat monotile in the plane so that
no two overlap. s_n is the side of the smallest axis-aligned square containing all n hats.

**Score.** `score = Σ_n s_n² / n`, summed over the 27 values of n. Lower is better.
The official judge is `python metric.py submission.csv`. Nothing else counts.

**The hat.** `tile.py`: 13 vertices, kite edges 1 and √3, area 8√3 ≈ 13.856, diameter 6.
(x, y) is the centroid. deg rotates counter-clockwise in degrees. flip = 1 is the mirror image,
applied before the rotation. Reflected hats are allowed and needed for dense packings.

**Submission.** CSV with columns `id,x,y,deg,flip` and exactly 475 rows: ids `001_0 … 025_24`,
`050_0 … 050_49`, `100_0 … 100_99` (n as three digits, underscore, hat index). Plain decimals.
Coordinates within ±100. Row order and extra columns do not matter.

**Validity.** Two hats overlap when their intersection area exceeds 10⁻⁹. Touching is allowed.
One overlapping pair, one bad, missing or duplicate id, one non-finite number: the whole file is invalid
and scores nothing.

**Lower bounds.** `python bounds.py`. s_1 ≥ 5.16310 is certified (optimum ≈ 5.1631 at 36.46°);
for n ≥ 2 only the area bound s_n ≥ √(n · 8√3) is known.

**Not allowed.** Editing metric.py, tile.py, bounds.py, run.sh or tests/ (a hook blocks it), or
submitting a file you did not produce with your own solver.
