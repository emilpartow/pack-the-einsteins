# loop-c — subagent team

Goal: produce the valid submission.csv with the lowest official score, `./run.sh`, the sum over
n in {1..25, 50, 100} of s_n² / n, and keep improving it until you are stopped.

## How this loop runs
One session in auto mode; you are the planner. Write PLAN.md first (one screen: ideas, order, who
does what), then delegate to the three subagents in .claude/agents/ and update PLAN.md as you learn.
Nobody answers questions. Never declare yourself done early.
- researcher: ideas from geometry, packing and the hat tiling; may search the web; writes no code
- implementer: turns one idea into code in solver/ and runs ./run.sh
- critic: re-runs ./run.sh on every claimed result, checks it against the lower bounds, never edits code

## Time
The start message names the duration (30 minutes unless it says otherwise); START_TIME holds the
start (`cat START_TIME`). Check `date` before every try. A try (implementer, then critic) takes up
to 6 minutes, so start no try that cannot finish before the deadline. In the last 3 minutes: let the
critic run `./run.sh` once more, make sure submission.csv is valid, write the final log line, commit,
and stop. Nothing else stops you.

## You may
- edit PLAN.md and LOG.md, run ./run.sh, python, pytest, git, read every file
- let the implementer write any code in solver/ (any method, any architecture); numpy, scipy, shapely
  and the repo modules tile, metric, bounds, baseline are available

## You may not
- write solver code yourself; the implementer does that, the critic verifies
- touch metric.py, tile.py, bounds.py, run.sh, tests/ or the leaderboard page; a hook blocks the files
- keep a total the critic has not confirmed, or make two changes in one try

## Each try
1. One idea from PLAN.md, one hypothesis, one implementer task (one change).
2. The critic runs `./run.sh` itself and answers PASS or FAIL with the TOTAL line. Its run is the one
   that counts. INVALID or exit code 124 (2-minute limit) is FAIL.
3. PASS and better than the last kept total: write the LOG.md line, then `git add -A && git commit -m "try N: <change> -> <total>"`
   (one commit holds code, submission.csv and log line, so nothing is ever half-recorded).
4. Otherwise `git reset --hard` first, then write the LOG.md line and `git commit -am "try N: reverted"`.

## Strategy (edit this)
`python metric.py submission.csv` prints the gap per n; work on the biggest gaps. Ideas, in order:
1. Replace the grid by `baseline.greedy_layout(n)` and improve from there.
2. Rows of hats at 36.46° (the n = 1 optimum) interlock; try shifted rows and alternating flips.
3. Local search: move, rotate or flip one hat, accept when the square shrinks and nothing overlaps.
4. For n ≥ 25 cut clusters out of the hat tiling: reflected hats, angles in multiples of 60°.
Ask the researcher for better ideas than these and rewrite this section when you learn something.
