# START — loop-a (autoresearch)

**Human:** in this folder run `claude --permission-mode auto` and type `Run START.md`.
Add "for 60 minutes" to that message if the workshop gives you more time. Everything below is for the agent.
To stop early: Ctrl+C, then `/exit`.

**Agent:** you are the session that runs this loop. Do not start another `claude`. Do not ask questions.

1. Run `date > START_TIME`. The duration is 30 minutes unless the human's message says otherwise.
2. Read CLAUDE.md and follow it: `./run.sh` is try 0, then one try after another, one commit per try,
   one LOG.md line per try, until the deadline. Nothing else stops you.
3. In the last 3 minutes: `git status` (if a try is half done, `git reset --hard`), `./run.sh`, confirm
   that submission.csv is valid, write the final log line, commit, stop, and report the final TOTAL.

Afterwards the human uploads submission.csv on the leaderboard page.

Checked against `claude --help` of Claude Code 2.1.241: `--permission-mode auto` lets the session act
without asking (choices are acceptEdits, auto, bypassPermissions, manual, dontAsk, plan). The hook and
the deny rules in .claude/settings.json protect metric.py, tile.py, bounds.py, run.sh and tests/ in every mode.
