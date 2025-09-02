#!/usr/bin/env bash
set -euo pipefail
cd ~/luanti_capability
STEP=$(grep -o '[0-9]*/1500' outputs_luanti_safe/training.log | tail -1 | cut -d/ -f1)
OUTDIR="eval/smoke/step_${STEP}"
mkdir -p "$OUTDIR"

# Sample 10 eval items for quick qualitative check
head -10 data/eval/luanti_eval.jsonl > "$OUTDIR/sample_10.jsonl"

source "$HOME/miniconda3/etc/profile.d/conda.sh" && conda activate gptoss
PY="/home/tdeshane/miniconda3/envs/gptoss/bin/python"
export HF_HOME="$PWD/.cache/hf" TRANSFORMERS_CACHE="$PWD/.cache/hf"
unset HF_HUB_OFFLINE

# Quick eval with current training state (no checkpoints needed)
echo "🧪 Smoke eval at step $STEP"
HF_HUB_OFFLINE= TOKENIZERS_PARALLELISM=false TORCHDYNAMO_DISABLE=1 \
"$PY" -u -m eval.run_eval \
  --base unsloth/gpt-oss-20b-unsloth-bnb-4bit \
  --eval "$OUTDIR/sample_10.jsonl" \
  --template prompts/iir_template.txt \
  --out "$OUTDIR/smoke_results.json" \
  --k 3 --temperature 0.3 --top_p 0.9 --max_new_tokens 200 --seed 3407 \
  | tee "$OUTDIR/smoke_eval.log"

echo "📊 Smoke eval complete: $OUTDIR"
