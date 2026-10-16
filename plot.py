"""Render a submission to PNG.

    python plot.py submission.csv              # plots/all.png (5x5 grid, n = 1..25) + plots/large.png (n = 50, 100)
    python plot.py submission.csv --n 5        # plots/n05.png (likewise --n 50 -> n50.png, --n 100 -> n100.png)
    python plot.py submission.csv --out dir/   # change the output directory

Colours as in Smith, Myers, Kaplan, Goodman-Strauss (2023): unflipped hats light blue,
flipped (mirror-image) hats dark blue, overlapping hats red, edges black.  The bounding
square is dashed, the title gives side and density.  The file only needs to parse; overlaps
are drawn, not rejected, so the plot can be used to debug an INVALID submission.
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon, Rectangle

import metric
from tile import AREA

COLOR_HAT, COLOR_FLIPPED, COLOR_OVERLAP = "#9ecae1", "#1f4e9e", "#d62728"


def draw(ax, n, hats):
    bad = {i for pair in metric.overlapping_pairs(hats) for i in pair[:2]}
    for i, h in enumerate(hats):
        color = COLOR_OVERLAP if i in bad else (COLOR_FLIPPED if h.flip else COLOR_HAT)
        ax.add_patch(MplPolygon(h.vertices, closed=True, facecolor=color, edgecolor="black", linewidth=0.8))
    minx, miny, maxx, maxy = metric.unary_union([h.polygon for h in hats]).bounds
    side = max(maxx - minx, maxy - miny)
    ax.add_patch(Rectangle((minx, miny), side, side, fill=False, linestyle="--", edgecolor="gray"))
    ax.set_xlim(minx - 0.5, minx + side + 0.5)
    ax.set_ylim(miny - 0.5, miny + side + 0.5)
    ax.set_aspect("equal")
    ax.set_title(f"n={n} side={side:.3f} density={n * AREA / side / side:.3f}" + ("  OVERLAP" if bad else ""))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("submission")
    p.add_argument("--n", type=int, default=None)
    p.add_argument("--out", default="plots")
    a = p.parse_args()
    hats_by_n = metric.load(a.submission)
    os.makedirs(a.out, exist_ok=True)
    if a.n is None:
        small = [n for n in sorted(hats_by_n) if n <= 25]
        large = [n for n in sorted(hats_by_n) if n > 25]
        fig, axes = plt.subplots(5, 5, figsize=(20, 20))
        for ax, n in zip(axes.flat, small):
            draw(ax, n, hats_by_n[n])
        save(fig, os.path.join(a.out, "all.png"))
        if large:
            fig, axes = plt.subplots(1, len(large), figsize=(10 * len(large), 10), squeeze=False)
            for ax, n in zip(axes.flat, large):
                draw(ax, n, hats_by_n[n])
            save(fig, os.path.join(a.out, "large.png"))
    else:
        if a.n not in hats_by_n:
            raise SystemExit(f"no group n={a.n}; choose one of {sorted(hats_by_n)}")
        fig, ax = plt.subplots(figsize=(6, 6) if a.n <= 25 else (10, 10))
        draw(ax, a.n, hats_by_n[a.n])
        save(fig, os.path.join(a.out, f"n{a.n:02d}.png"))


def save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    print("wrote", path)


if __name__ == "__main__":
    main()
