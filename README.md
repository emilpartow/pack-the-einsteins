# loop-b — Ralph loop

A driver session starts a fresh headless Claude Code session for every try, for 30 minutes. Each
try-session has no memory: it reads LOG.md and `git log`, makes exactly one change in solver/, judges it
with ./run.sh, commits or resets, writes one line to LOG.md and exits. The driver starts the next one
and never solves anything itself.

Challenge: pack n hats into the smallest square for n = 1..25, 50 and 100; score = Σ s_n² / n, lower is
better. Rules in one page: [CHALLENGE.md](CHALLENGE.md).

## Setup (5 minutes)

```
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q                                              # all tests pass -> ready
./run.sh                                               # starting solver: TOTAL 904.727 (Windows: bash run.sh)
```

Optional: `claude` once in this folder, accept the "trust this workspace" dialog, `/exit`. Until then
Claude Code ignores the permission list in .claude/settings.json and prints a warning; the loop in
START.md passes the same list on the command line, so it runs either way.

## Run

`claude --permission-mode auto`, then type `Run START.md` (add "for 60 minutes" for a longer run).
This session is only the driver: [START.md](START.md) tells it to start one headless session per try,
each of which receives [PROMPT.md](PROMPT.md). Stop early with Ctrl+C and `/exit`.
While it runs, `git log --oneline` and LOG.md show what each session did.

## What the agent follows

- [CLAUDE.md](CLAUDE.md): goal, may, may not, the steps of a try including the reset after a cut-off
  session, and a "Strategy (edit this)" section the sessions pass on to each other.
- Protected by a hook: metric.py, tile.py, bounds.py, run.sh, tests/. Web search is allowed.

## Submit

`./run.sh` must print a TOTAL line, then upload submission.csv on the leaderboard page:
https://claude.ai/artifact/4Q5dpvegXqeUFfzgnC2XhV

## Files on this branch

| file | what |
|---|---|
| solver/solve.py | the solver; starts as a plain grid |
| run.sh | one try: solver (2-minute limit), then the judge |
| PROMPT.md | the prompt every session gets |
| LOG.md | one line per try |
| submission.csv | the current best |
| metric.py, tile.py, bounds.py, baseline.py, plot.py | the shared foundation, same on every branch |
