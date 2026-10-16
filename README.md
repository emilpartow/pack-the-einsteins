# Pack the einsteins

Pack n copies of the hat monotile into the smallest square, for n = 1..25, 50 and 100.
Score = Σ s_n² / n, lower is better. The only judge is `python metric.py submission.csv`.
Rules in one page: [CHALLENGE.md](CHALLENGE.md).

## Setup (5 minutes)

1. Install Python 3.11 or newer, git, and Claude Code. Windows: install Git for Windows; Claude Code
   runs its commands in Git Bash, and in your own terminal you run the scripts as `bash run.sh`.
2. Clone and install:
   ```
   git clone https://github.com/emilpartow/pack-the-einsteins.git && cd pack-the-einsteins
   python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pytest -q                                              # all tests pass -> you are ready
   ./run.sh                                               # starting solver -> submission.csv and its score
   ```
3. Recommended: run `claude` once in this folder, accept the "trust this workspace" dialog, `/exit`.
   Until then Claude Code ignores the permission list in .claude/settings.json and prints a warning
   (the loops pass what they need on the command line, so they run either way; the hook and the
   deny rules that protect the judge files are active regardless).

## Pick a loop

Three ready-made ways to run Claude on the problem. Each branch has a CLAUDE.md (the rules for the agent),
a START.md (exactly how to start it) and an empty LOG.md; your first `./run.sh` writes submission.csv.

| branch | how the loop runs |
|---|---|
| loop-a | autoresearch: one long interactive session in auto mode, tries until you stop it |
| loop-b | Ralph loop: a shell loop starts a fresh headless session for every try, 30 minutes |
| loop-c | subagent team: a planner writes PLAN.md and delegates to researcher, implementer, critic |

```
git checkout loop-a              # or loop-b, loop-c
claude --permission-mode auto    # then type:  Run START.md
```

That one message starts the loop: the agent reads START.md, writes START_TIME and works for 30 minutes
(say "Run START.md for 60 minutes" for more). Stop early with Ctrl+C and `/exit`.

Build your own loop:

```
git checkout -b team-<name> main
cp template/CLAUDE.md CLAUDE.md && cp template/START.md START.md   # fill in the <...> parts
git add -A && git commit -m "team-<name>: my loop"
```

template/CLAUDE.md has the rules every loop shares (goal, may, may not, the steps of a try) and a
"How this loop runs" section to fill in; template/START.md shows the three start patterns.
Whatever the loop, every try is `./run.sh`: it runs solver/solve.py for at most 2 minutes, writes
submission.csv and prints the official score. Better: `git commit`. Worse: `git reset --hard`.

## Submit

Upload your submission.csv on the leaderboard page: https://claude.ai/artifact/4Q5dpvegXqeUFfzgnC2XhV
The page scores it in the browser with the same rules as metric.py and shows every team's best live.
Submit as often as you like; only your best counts.

## Files

| file | what it does |
|---|---|
| solver/solve.py | your solver; the starting version is a plain grid |
| run.sh | one try: solver, then judge |
| metric.py | the judge: validity and score |
| tile.py | the hat: `EinsteinHat(x, y, deg, flip)`, centroid at (x, y) |
| bounds.py | lower bounds per n |
| baseline.py | reference greedy with rotations and flips; its output is sample_submission.csv (score 668.907, a valid example) |
| plot.py | pictures: `python plot.py submission.csv` writes plots/ |
| LOG.md | one line per try; docs/example-log-loop-a.md shows a finished 30-minute log |

Two rules the hook enforces for every agent: no edits to the judge files, and no looking at other
branches (git checkout/show/log/diff of another branch, or anything under .git/, is refused).
Your agent works on its own branch and its own history only.

Protected by a hook: metric.py, tile.py, bounds.py, run.sh, tests/. Web search is allowed.
