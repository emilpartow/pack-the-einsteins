#!/usr/bin/env python3
"""PreToolUse hook with two jobs.

1. Judge guard: refuses every edit to metric.py, tile.py, bounds.py, run.sh, tests/ and .claude/.
   Edit/Write/MultiEdit/NotebookEdit are checked by path; Bash commands by segment (split at && || ; |):
   a segment is blocked if it redirects into a protected path, or names one together with sed -i, rm,
   mv, cp, tee, patch, git restore/checkout, or a Python write call.
2. Branch guard: the agent works on its own branch and must not look at other teams' branches.
   Blocked: git checkout/switch/show/log/diff/merge/rebase/cherry-pick/reset/restore/archive/ls-tree/
   cat-file with another team's branch name (also origin/<name>, name:path, name~2), `--all`, every
   `git branch` listing and `git worktree`, and any read of .git/ (Bash, Read, Grep, Glob).
   Allowed: everything on the current branch (status, add, commit, log, diff, reset --hard, checkout --
   <file>, stash), creating your own branch (`git checkout -b team-x main`, `git switch -c team-x`),
   and reading main, which is the shared foundation and nobody's work.
   The organiser disables the branch guard locally with the file .claude/organiser (gitignored).

Claude Code pipes the tool call as JSON on stdin. Exit 2 blocks the call and shows stderr to the agent.
Guard rail for a cooperative agent, not a sandbox.
"""
import json
import os
import re
import subprocess
import sys

PROTECTED = ("metric.py", "tile.py", "bounds.py", "run.sh", "tests/", ".claude/")
WRITE_CMD = re.compile(r"\b(sed\s+-i|rm|mv|cp|tee|truncate|patch|chmod|git\s+(checkout|restore|rm|mv|clean|reset))\b")
PY_WRITE = re.compile(r"""open\([^)]*['"][wax]|write_text|write_bytes|to_csv|savefig|shutil\.""")
ROOT = os.path.abspath(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())

PEEK_SUBCMDS = {"checkout", "switch", "show", "log", "diff", "merge", "rebase", "cherry-pick", "reset",
                "restore", "archive", "ls-tree", "cat-file", "rev-parse", "describe", "fetch", "pull", "push"}
BRANCH_LIKE = re.compile(r"^(origin/)?(main|master|loop-[a-z]|team-[\w.-]+)$")
ORGANISER_MARKER = os.path.join(ROOT, ".claude", "organiser")


def protected(path: str) -> str | None:
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    rel = os.path.relpath(os.path.abspath(full), ROOT).replace(os.sep, "/")
    for p in PROTECTED:
        if rel == p.rstrip("/") or rel.startswith(p):
            return rel
    return None


def block(what: str, why: str) -> None:
    sys.stderr.write(f"BLOCKED by .claude/hooks/protect.py: {why} ('{what}').\n")
    sys.exit(2)


JUDGE_WHY = ("this file is protected: metric.py, tile.py, bounds.py, run.sh and tests/ are the judge, .claude/ is "
             "the harness; nobody edits them during the challenge. Write your code in solver/")
PEEK_WHY = "other branches are other teams' work; stay on your own branch, read only its files and history"


# ---- judge guard -------------------------------------------------------------------------------------
def check_bash_judge(cmd: str) -> None:
    for segment in re.split(r"&&|\|\||;|\|", cmd):
        for target in re.findall(r">>?\s*([^\s;&|]+)", segment):
            if protected(target):
                block(target, JUDGE_WHY)
        mentioned = [t for t in re.findall(r"[\w./\\-]+", segment) if protected(t)]
        if mentioned and (WRITE_CMD.search(segment) or PY_WRITE.search(segment)):
            block(mentioned[0], JUDGE_WHY)


# ---- branch guard ------------------------------------------------------------------------------------
def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def branch_guard_active() -> bool:
    return not os.path.exists(ORGANISER_MARKER) or os.environ.get("PROTECT_TEST") == "1"


def other_branches() -> tuple[str, set[str]]:
    current = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    names = set()
    for ref in git("for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes").split():
        names.add(ref)
        names.add(ref.split("/", 1)[1] if "/" in ref else ref)
    names.discard(current)
    names.discard("origin/" + current)
    names.discard("origin/HEAD")
    return current, names


SHARED = {"main", "origin/main", "master", "origin/master", "HEAD", "origin/HEAD"}   # the foundation: readable by all


def is_other_branch(token: str, current: str, others: set[str]) -> bool:
    base = re.split(r"[:~^@]", token, 1)[0]            # main:solver/solve.py, loop-b~2, origin/loop-c^
    if not base or base == current or base == "origin/" + current or base in SHARED:
        return False
    return base in others or bool(BRANCH_LIKE.match(base))


def check_bash_branch(cmd: str) -> None:
    if ".git/" in cmd or re.search(r"(^|[\s/])\.git($|\s)", cmd):
        block(".git", PEEK_WHY)
    for segment in re.split(r"&&|\|\||;|\|", cmd):
        words = segment.split()
        if "git" not in words:
            continue
        args = words[words.index("git") + 1:]
        while args and (args[0] == "-C" or args[0].startswith("--git-dir") or args[0].startswith("--work-tree")):
            args = args[2:] if args[0] in ("-C", "--git-dir", "--work-tree") else args[1:]
        if not args:
            continue
        sub = args[0]
        if sub == "worktree":
            block(segment.strip(), PEEK_WHY)
        if sub == "branch":
            if any(a in ("--show-current", "--show-current") for a in args[1:]) and len(args) == 2:
                continue
            block(segment.strip(), PEEK_WHY)
        if sub not in PEEK_SUBCMDS:
            continue
        if "--all" in args or "-a" in args and sub in ("log", "show", "diff"):
            block(segment.strip(), PEEK_WHY)
        current, others = other_branches()
        new_branch = {args[i + 1] for i, a in enumerate(args[:-1]) if a in ("-b", "-B", "-c", "-C", "--orphan")}
        for a in args[1:]:
            if a.startswith("-") or a in new_branch:          # the branch being created is the agent's own
                continue
            if is_other_branch(a, current, others):
                block(a, PEEK_WHY)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    tool, inp = data.get("tool_name", ""), data.get("tool_input") or {}
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        path = inp.get("file_path") or inp.get("notebook_path") or ""
        if path and protected(path):
            block(protected(path), JUDGE_WHY)
    elif tool in ("Read", "Grep", "Glob"):
        path = inp.get("file_path") or inp.get("path") or ""
        if branch_guard_active() and path and re.search(r"(^|/)\.git(/|$)", path.replace(os.sep, "/")):
            block(path, PEEK_WHY)
    elif tool == "Bash":
        cmd = inp.get("command") or ""
        check_bash_judge(cmd)
        if branch_guard_active():
            check_bash_branch(cmd)


if __name__ == "__main__":
    main()
