# START — loop-b (Ralph loop)

**Human:** in this folder run `claude --permission-mode auto` and type `Run START.md`.
Add "for 60 minutes" to that message if the workshop gives you more time. Everything below is for the agent.
To stop early: Ctrl+C, then `/exit`.

**Agent:** you are the DRIVER of this loop, not a solver. You never edit solver/, never run `./run.sh`
yourself during the loop, never write LOG.md. Every try is made by a fresh headless session that has
no memory of the previous ones and gets its instructions from PROMPT.md. Do not ask questions.

1. Run `date > START_TIME`. The duration is 30 minutes unless the human's message says otherwise.
2. Until the deadline, repeat: run exactly this command (one session; it ends by itself after its one
   try, usually within a few minutes; give the Bash tool a timeout of 10 minutes), then print the last
   line of LOG.md and `git log --oneline -1`:

   ```
   claude -p "$(cat PROMPT.md)" --permission-mode acceptEdits --allowedTools 'Bash(python:*)' 'Bash(python3:*)' 'Bash(./run.sh)' 'Bash(./run.sh:*)' 'Bash(bash:*)' 'Bash(sh:*)' 'Bash(git:*)' 'Bash(pytest:*)' 'Bash(pytest)' 'Bash(ls:*)' 'Bash(cat:*)' 'Bash(head:*)' 'Bash(tail:*)' 'Bash(grep:*)' 'Bash(wc:*)' 'Bash(date:*)' 'Bash(echo:*)' 'Bash(mkdir:*)' WebSearch WebFetch
   ```

   If a session is cut off mid-try (the Bash tool's timeout), the next session resets what it left
   behind (step 0 in CLAUDE.md). Start no session after the deadline.
3. After the deadline: `git status`; if anything is modified, `git reset --hard`; then `./run.sh` once,
   confirm that submission.csv is valid, and report the final TOTAL and the number of sessions.

Afterwards the human uploads submission.csv on the leaderboard page.

Why the flags (Claude Code 2.1.241): `-p` runs one prompt without the interactive UI and never asks.
`--permission-mode acceptEdits` accepts file edits (solver/, LOG.md). `--allowedTools` repeats the
permission list of .claude/settings.json, because Claude Code ignores that list in a folder that has
not been trusted yet (it prints "Ignoring N permissions.allow entries"); the hook and the deny rules
protecting the judge files are active either way, verified in a headless probe.
