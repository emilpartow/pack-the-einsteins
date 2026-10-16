"""The protect hook must block edits to the judge, block looks at other branches, and let normal work through."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, ".claude", "hooks", "protect.py")
SETTINGS = os.path.join(ROOT, ".claude", "settings.json")


def run_hook(tool: str, tool_input: dict) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_name": tool, "tool_input": tool_input, "cwd": ROOT})
    env = {**os.environ, "CLAUDE_PROJECT_DIR": ROOT, "PROTECT_TEST": "1"}   # PROTECT_TEST: ignore the organiser marker
    return subprocess.run([sys.executable, HOOK], input=payload, text=True, capture_output=True, env=env)


@pytest.mark.parametrize("tool, tool_input", [
    ("Edit", {"file_path": os.path.join(ROOT, "metric.py"), "old_string": "EPS_AREA = 1e-9", "new_string": "EPS_AREA = 1"}),
    ("Write", {"file_path": "metric.py", "content": ""}),
    ("Edit", {"file_path": "tile.py", "old_string": "a", "new_string": "b"}),
    ("MultiEdit", {"file_path": "bounds.py", "edits": []}),
    ("Write", {"file_path": os.path.join(ROOT, "tests", "test_new.py"), "content": ""}),
    ("Write", {"file_path": ".claude/settings.json", "content": "{}"}),
    ("Bash", {"command": "echo 'EPS_AREA = 1' >> metric.py"}),
    ("Bash", {"command": "sed -i '' 's/1e-9/1/' metric.py"}),
    ("Bash", {"command": "rm -rf tests/"}),
    ("Bash", {"command": "cp solver/mymetric.py metric.py"}),
    ("Bash", {"command": "git checkout -- tile.py"}),
    ("Bash", {"command": "python -c \"open('metric.py','w').write('')\""}),
    ("Edit", {"file_path": "run.sh", "old_string": "LIMIT=120", "new_string": "LIMIT=9999"}),
    ("Write", {"file_path": os.path.join(ROOT, "run.sh"), "content": ""}),
    ("Bash", {"command": "sed -i '' 's/LIMIT=120/LIMIT=600/' run.sh"}),
])
def test_hook_blocks_judge_edits(tool, tool_input):
    r = run_hook(tool, tool_input)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "protected" in r.stderr.lower()


@pytest.mark.parametrize("tool, tool_input", [
    ("Bash", {"command": "git checkout team-other"}),
    ("Bash", {"command": "git switch team-other"}),
    ("Bash", {"command": "git show origin/team-other:solver/solve.py"}),
    ("Bash", {"command": "git log --oneline team-other~3"}),
    ("Bash", {"command": "git diff team-other -- solver/"}),
    ("Bash", {"command": "git log --all --oneline"}),
    ("Bash", {"command": "git branch -a"}),
    ("Bash", {"command": "git branch"}),
    ("Bash", {"command": "git worktree add ../peek team-other"}),
    ("Bash", {"command": "git -C . show team-other:LOG.md"}),
    ("Bash", {"command": "cat .git/refs/heads/team-other"}),
    ("Bash", {"command": "ls .git"}),
    ("Read", {"file_path": os.path.join(ROOT, ".git", "HEAD")}),
    ("Grep", {"pattern": "solve", "path": os.path.join(ROOT, ".git")}),
])
def test_hook_blocks_looking_at_other_branches(tool, tool_input):
    r = run_hook(tool, tool_input)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "other branches" in r.stderr.lower()


@pytest.mark.parametrize("tool, tool_input", [
    ("Edit", {"file_path": "solver/solve.py", "old_string": "a", "new_string": "b"}),
    ("Write", {"file_path": os.path.join(ROOT, "solver", "pack.py"), "content": ""}),
    ("Write", {"file_path": "LOG.md", "content": ""}),
    ("Write", {"file_path": "PLAN.md", "content": ""}),
    ("Write", {"file_path": ".gitignore", "content": ""}),
    ("Read", {"file_path": os.path.join(ROOT, "CLAUDE.md")}),
    ("Grep", {"pattern": "def", "path": os.path.join(ROOT, "solver")}),
    ("Bash", {"command": "python metric.py submission.csv"}),
    ("Bash", {"command": "python metric.py submission.csv > run.log"}),
    ("Bash", {"command": "pytest -q tests/test_metric.py"}),
    ("Bash", {"command": "cat metric.py"}),
    ("Bash", {"command": "cat .gitignore && cat START_TIME && date"}),
    ("Bash", {"command": "./run.sh"}),
    ("Bash", {"command": "bash run.sh && git add -A && git commit -m 'try 3: rotate rows -> 640.1'"}),
    ("Bash", {"command": "git reset --hard"}),
    ("Bash", {"command": "git reset --hard HEAD~1"}),
    ("Bash", {"command": "git checkout -- README.md"}),
    ("Bash", {"command": "git status && git log --oneline -15"}),
    ("Bash", {"command": "git log -p -3 -- solver/solve.py"}),
    ("Bash", {"command": "git diff HEAD~1 -- LOG.md"}),
    ("Bash", {"command": "git branch --show-current"}),
    ("Bash", {"command": "git checkout -b team-mine main"}),
    ("Bash", {"command": "git switch -c team-mine"}),
    ("Bash", {"command": "git checkout -b team-mine origin/main"}),
    ("Bash", {"command": "git log --oneline main"}),
    ("Bash", {"command": "git diff main -- solver/solve.py"}),
    ("Bash", {"command": "git show main:CHALLENGE.md"}),
    ("Bash", {"command": "git commit -am 'log try 4, idea borrowed from the paper, not from team-other'"}),
    ("Bash", {"command": "cp submission.csv runs/best.csv && python metric.py runs/best.csv"}),
])
def test_hook_allows(tool, tool_input):
    r = run_hook(tool, tool_input)
    assert r.returncode == 0, r.stdout + r.stderr


def test_settings_register_hook_and_permissions():
    with open(SETTINGS) as f:
        s = json.load(f)
    groups = s["hooks"]["PreToolUse"]
    assert any("protect.sh" in h["command"] for g in groups for h in g["hooks"])
    for tool in ("Edit", "Write", "MultiEdit", "NotebookEdit", "Bash", "Read", "Grep", "Glob"):
        assert any(tool in g["matcher"] for g in groups), tool
    allow, deny = s["permissions"]["allow"], s["permissions"]["deny"]
    assert "WebSearch" in allow and "WebFetch" in allow and "WebSearch" not in deny
    for prefix in ("Bash(python", "Bash(pytest", "Bash(bash", "Bash(git", "Bash(./run.sh"):
        assert any(rule.startswith(prefix) for rule in allow), prefix
    for f in ("metric.py", "tile.py", "bounds.py", "run.sh", "tests/**", ".claude/**"):
        assert f"Edit({f})" in deny, f          # Edit(path) rules cover Write and every other file-editing tool
    assert not any(rule.startswith("Write(") for rule in deny)   # Write(path) deny rules are ignored by Claude Code


def test_shell_wrapper_finds_python_and_blocks():
    """The hook is registered through protect.sh, which picks python3 or python (Windows)."""
    payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": "metric.py", "old_string": "a", "new_string": "b"}})
    r = subprocess.run(["sh", os.path.join(ROOT, ".claude", "hooks", "protect.sh")], input=payload, text=True,
                       capture_output=True, env={**os.environ, "CLAUDE_PROJECT_DIR": ROOT, "PROTECT_TEST": "1"})
    assert r.returncode == 2 and "protected" in r.stderr.lower(), r.stdout + r.stderr
