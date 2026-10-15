# loop-b — Ralph loop

Goal: produce the valid submission.csv with the lowest official score, `./run.sh`, the sum over
n in {1..25, 50, 100} of s_n² / n, and keep improving it until you are stopped.

## Two roles, decide which one you are
- The human asked you to "Run START.md": you are the DRIVER. Follow START.md only: start one fresh
  headless session per try, never solve, never edit solver/, never write LOG.md yourself.
- You were started headless with PROMPT.md: you are ONE TRY. The rest of this file is for you.

## How this loop runs
The driver starts a fresh headless session for every try, for 30 minutes (see START.md). You have
no memory of earlier sessions: LOG.md and `git log` are your memory. Read them, make exactly one try,
log, exit. Nobody answers questions. Keep the try small: one change, a few minutes.

## You may
- write any code in solver/ (new files, any method, any architecture); numpy, scipy, shapely and the
  repo modules tile, metric, bounds, baseline are available
- run ./run.sh, python, pytest, git; search the web for ideas
- read every file: CHALLENGE.md has the rules, bounds.py the lower bounds, plot.py draws a file

## You may not
- touch metric.py, tile.py, bounds.py, run.sh, tests/ or the leaderboard page; a hook blocks the files
- make two changes in one try, make a second try, or skip the log line
- submit anything your solver did not produce

## Each try
0. `git status`: uncommitted changes mean the previous session was cut off. `git reset --hard`, log it
   as reverted. If LOG.md has no entries yet, run `./run.sh` and log the starting score as try 0.
1. One change, one hypothesis, continuing the plan in the Strategy section.
2. `./run.sh` — the TOTAL line is the score. INVALID or exit code 124 (2-minute limit) count as worse.
3. Better than the last kept total in LOG.md: write the LOG.md line (time = minutes since
   `cat START_TIME`), then `git add -A && git commit -m "try N: <change> -> <total>"` (one commit holds
   code, submission.csv and log line, so a cut-off session never leaves a half-recorded try).
4. Worse or INVALID: `git reset --hard` first, then write the LOG.md line and `git commit -am "try N: reverted"`.
   Then exit.

## Strategy (edit this)
`python metric.py submission.csv` prints the gap per n; work on the biggest gaps. Ideas, in order:
1. Replace the grid by `baseline.greedy_layout(n)` and improve from there.
2. Rows of hats at 36.46° (the n = 1 optimum) interlock; try shifted rows and alternating flips.
3. Local search: move, rotate or flip one hat, accept when the square shrinks and nothing overlaps.
4. For n ≥ 25 cut clusters out of the hat tiling: reflected hats, angles in multiples of 60°.
Rewrite this section when you learn something; the next session reads it.
