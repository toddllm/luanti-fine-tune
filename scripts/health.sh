#!/usr/bin/env bash
set -euo pipefail
LOG=outputs_luanti_safe/training.log
echo "== GPU =="
nvidia-smi | sed -n '1,15p'
echo "== Last log lines =="
tail -n 60 "$LOG" || echo "No log yet."
echo "== Checkpoints =="
ls -1d outputs_*/checkpoint-* 2>/dev/null | tail -n 10 || echo "No checkpoints yet."
