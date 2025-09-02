#!/usr/bin/env bash
set -euo pipefail
LOG=outputs_luanti_safe/training.log
PID=$(pgrep -f "train_luanti_cosmic.py" || true)
[ -z "$PID" ] && echo "no training PID" && exit 0

# 1) NaN/Inf guard
if grep -E "nan|NaN|inf|Inf" -i -m1 "$LOG" >/dev/null; then
  echo "❌ NaN/Inf detected — stopping PID $PID"
  kill -INT "$PID" || true
  exit 1
fi

# 2) stale log guard (no new bytes in 10 min)
NOW=$(date +%s)
MTIME=$(stat -c %Y "$LOG")
if [ $((NOW-MTIME)) -gt 600 ]; then
  echo "⚠️  Log stale >10m — check tmux session / GPU"
fi
