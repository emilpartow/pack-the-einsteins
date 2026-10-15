# loop-c — subagent team

One Claude Code session in auto mode where the main agent is a planner: it writes PLAN.md first,
then delegates every try to three subagents. The researcher proposes layouts from the geometry of the
hat (and may search the web), the implementer writes the code in solver/, the critic re-runs ./run.sh
and checks the result against the lower bounds. Only critic-confirmed totals are kept.

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
The planner reads [START.md](START.md), writes START_TIME and keeps time itself. Stop early with Ctrl+C and `/exit`.
While it runs, PLAN.md shows the plan, LOG.md the tries, `git log --oneline` what was kept.

## What the agents follow

- [CLAUDE.md](CLAUDE.md): the planner's goal, may, may not, the steps of a try (implementer, then
  critic, then commit or reset), and a "Strategy (edit this)" section.
- [.claude/agents/](.claude/agents/): researcher (read and web only), implementer (read, edit, write,
  bash), critic (read and bash). Each one's tools are restricted to its role.
- Protected by a hook for all of them: metric.py, tile.py, bounds.py, run.sh, tests/.

## Submit

`./run.sh` must print a TOTAL line, then upload submission.csv on the leaderboard page:
https://claude.ai/artifact/4Q5dpvegXqeUFfzgnC2XhV

## Files on this branch

| file | what |
|---|---|
| solver/solve.py | the solver; starts as a plain grid, written by the implementer |
| run.sh | one try: solver (2-minute limit), then the judge |
| PLAN.md | written by the planner at the start, updated as it learns |
| LOG.md | one line per try |
| submission.csv | the current best |
| metric.py, tile.py, bounds.py, baseline.py, plot.py | the shared foundation, same on every branch |
