#!/usr/bin/env bash
# One try, the same for every loop: run the solver for at most 2 minutes, then let the official judge score it.
#
#     ./run.sh              solver/solve.py writes submission.csv; metric.py prints side per n and TOTAL
#
# Exit code: 0 valid, 1 INVALID or solver error, 124 solver timeout. A timeout leaves submission.csv
# as it was. Keep or revert with git: better -> git commit, worse -> git reset --hard.
set -u
cd "$(dirname "$0")"
PY=""                                   # python3 on macOS/Linux, python on Windows (Git Bash); PYTHON=... overrides
for c in "${PYTHON:-}" python3 python; do
  [ -n "$c" ] && "$c" -c "import sys" >/dev/null 2>&1 && PY="$c" && break
done
[ -n "$PY" ] || { echo "run.sh: no python found (activate the venv)"; exit 1; }
LIMIT=120

"$PY" - "$PY" "$LIMIT" <<'EOF'
import subprocess, sys, time
py, limit = sys.argv[1], float(sys.argv[2])
t0 = time.time()
try:
    rc = subprocess.call([py, "solver/solve.py"], timeout=limit)
except subprocess.TimeoutExpired:
    print(f"run.sh: solver stopped after {limit:.0f} s (timeout); submission.csv unchanged")
    sys.exit(124)
print(f"run.sh: solver finished in {time.time() - t0:.1f} s, exit code {rc}")
sys.exit(0 if rc == 0 else 1)
EOF
rc=$?
[ $rc -ne 0 ] && exit $rc
"$PY" metric.py submission.csv
