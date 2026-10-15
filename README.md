# loop-a — autoresearch

One long Claude Code session in auto mode that keeps trying until you stop it, in the spirit of
Karpathy's autoresearch. The agent writes its own solver in solver/, judges every try with ./run.sh,
keeps what helps (git commit), throws away what does not (git reset --hard), and logs one line per try.

Challenge: pack n hats into the smallest square for n = 1..25, 50 and 100; score = Σ s_n² / n, lower is
better. Rules in one page: [CHALLENGE.md](CHALLENGE.md).

## Setup (5 minutes)

```
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q                                              # all tests pass -> ready
./run.sh                                               # starting solver: TOTAL 904.727
```

Then `claude` once in this folder, accept the "trust this workspace" dialog, `/exit`. Without that,
Claude Code ignores the permission list in .claude/settings.json.

## Run

`claude --permission-mode auto`, then type `Run START.md` (add "for 60 minutes" for a longer run).
The agent reads [START.md](START.md), writes START_TIME and keeps time itself. Stop early with Ctrl+C and `/exit`.
While it runs, watch `git log --oneline` and LOG.md; `python plot.py submission.csv` draws the current
packings into plots/.

## What the agent follows

- [CLAUDE.md](CLAUDE.md): goal, may, may not, the four steps of a try, and a "Strategy (edit this)"
  section the agent rewrites as it learns. Edit the strategy before you start if you have a plan.
- Protected by a hook: metric.py, tile.py, bounds.py, run.sh, tests/. Web search is allowed.

## Submit

`./run.sh` must print a TOTAL line, then upload submission.csv on the leaderboard page:
https://claude.ai/artifact/4Q5dpvegXqeUFfzgnC2XhV

## Files on this branch

| file | what |
|---|---|
| solver/solve.py | the solver; starts as a plain grid |
| run.sh | one try: solver (2-minute limit), then the judge |
| LOG.md | one line per try |
| submission.csv | the current best |
| metric.py, tile.py, bounds.py, baseline.py, plot.py | the shared foundation, same on every branch |
