#!/bin/sh
# Runs protect.py with whatever Python exists: python3 on macOS and Linux, python on Windows (Git Bash).
# A Windows Store alias named python3 fails the import probe and is skipped.
for c in python3 python; do
  if "$c" -c "import sys" >/dev/null 2>&1; then exec "$c" "$(dirname "$0")/protect.py"; fi
done
echo "protect.sh: no python found; blocking the call to be safe" >&2
exit 2
