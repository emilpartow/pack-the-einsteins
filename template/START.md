# START — team-<name>

**Human:** in this folder run `claude --permission-mode auto` and type `Run START.md`.
Add "for 60 minutes" to that message if you want a longer run. Everything below is for the agent.
To stop early: Ctrl+C, then `/exit`.

Keep one of the two agent blocks below and delete the other. Both were dry-run for 30 minutes
on 15 Oct 2026; scores then: autoresearch 577.8, Ralph loop 545.3 (grid start 904.7).

## Agent block A: you are the loop (autoresearch)

**Agent:** you are the session that runs this loop. Do not start another `claude`. Do not ask questions.
1. Run `date > START_TIME`. The duration is 30 minutes unless the human's message says otherwise.
2. Read CLAUDE.md and follow it: `./run.sh` is try 0, then one try after another, one commit per try,
   one LOG.md line per try, until the deadline.
3. In the last 3 minutes: `git status` (if a try is half done, `git reset --hard`), `./run.sh`, confirm
   that submission.csv is valid, write the final log line, commit, stop, and report the final TOTAL.

## Agent block B: you are the driver of fresh sessions (Ralph loop)

Write PROMPT.md first (what one headless session does: read CLAUDE.md, LOG.md and git log, one try,
one commit, exit).

**Agent:** you are the DRIVER, not a solver: never edit solver/, never run `./run.sh` during the loop,
never write LOG.md. Do not ask questions.
1. Run `date > START_TIME`. The duration is 30 minutes unless the human's message says otherwise.
2. Until the deadline, repeat this command (one session; it ends by itself after its one try, give
   the Bash tool a timeout of 10 minutes), then print the last line of LOG.md:
   ```
   claude -p "$(cat PROMPT.md)" --permission-mode acceptEdits --allowedTools 'Bash(python:*)' 'Bash(python3:*)' 'Bash(./run.sh)' 'Bash(./run.sh:*)' 'Bash(bash:*)' 'Bash(sh:*)' 'Bash(git:*)' 'Bash(pytest:*)' 'Bash(pytest)' 'Bash(ls:*)' 'Bash(cat:*)' 'Bash(head:*)' 'Bash(tail:*)' 'Bash(grep:*)' 'Bash(wc:*)' 'Bash(date:*)' 'Bash(echo:*)' 'Bash(mkdir:*)' WebSearch WebFetch
   ```
3. After the deadline: `git status`; if modified, `git reset --hard`; `./run.sh`; report the final TOTAL.

Permission modes in Claude Code 2.1.241: acceptEdits, auto, bypassPermissions, manual, dontAsk, plan.
The hook and the deny rules in .claude/settings.json protect the judge files in every mode.
