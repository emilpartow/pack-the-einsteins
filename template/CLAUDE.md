# team-<name> — <your loop in three words>

Goal: produce the valid submission.csv with the lowest official score, `./run.sh`, the sum over
n in {1..25, 50, 100} of s_n² / n, and keep improving it until you are stopped.

## How this loop runs
<Describe your loop in two or three sentences: one long session, or a fresh session per try, or a
planner with subagents, or something new. Say who decides, who writes code, who judges, and how
the loop knows what happened before (LOG.md, git log, PLAN.md).>
Nobody answers questions. Never declare yourself done early.

## Time
The start message names the duration (30 minutes unless it says otherwise); START_TIME holds the
start (`cat START_TIME`). Check `date` before every try. Start no try that cannot finish before the
deadline. In the last 3 minutes: `./run.sh` once more, make sure submission.csv is valid, write the
final log line, commit, and stop.

## You may
- write any code in solver/ (new files, any method, any architecture); numpy, scipy, shapely and the
  repo modules tile, metric, bounds, baseline are available
- run ./run.sh, python, pytest, git; search the web for ideas
- read every file: CHALLENGE.md has the rules, bounds.py the lower bounds, plot.py draws a file

## You may not
- touch metric.py, tile.py, bounds.py, run.sh, tests/ or the leaderboard page; a hook blocks the files
- look at other teams' branches; the hook blocks that too
- make two changes in one try, or skip the log line
- submit anything your solver did not produce

## Each try
1. One change, one hypothesis.
2. `./run.sh` — the TOTAL line is the score. INVALID or exit code 124 (2-minute limit) count as worse.
3. Better than the last kept total: write the LOG.md line, then `git add -A && git commit -m "try N: <change> -> <total>"`
   (one commit holds code, submission.csv and log line, so nothing is ever half-recorded).
4. Worse or INVALID: `git reset --hard` first, then write the LOG.md line and `git commit -am "try N: reverted"`.

## Strategy (edit this)
`python metric.py submission.csv` prints the gap per n; work on the biggest gaps. Ideas, in order:
1. Replace the grid by `baseline.greedy_layout(n)` and improve from there.
2. Rows of hats at 36.46° (the n = 1 optimum) interlock; try shifted rows and alternating flips.
3. Local search: move, rotate or flip one hat, accept when the square shrinks and nothing overlaps.
4. For n ≥ 25 cut clusters out of the hat tiling: reflected hats, angles in multiples of 60°.
Rewrite this section when you learn something.
