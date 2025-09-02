#!/usr/bin/env bash
set -euo pipefail

# 1) conda activation (login shell semantics for tmux)
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate gptoss

# 2) cache locations — match Gate B (project-local cache)
export HF_HOME="$PWD/.cache/hf"
export TRANSFORMERS_CACHE="$HF_HOME"
export HF_DATASETS_CACHE="$HF_HOME"

# 3) offline behavior — start like Gate B
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

# 4) sanity prints (should mirror Gate B)
which python
python - <<'PY'
import torch, unsloth, transformers, os, sys
print("PY:", sys.executable)
print("torch:", torch.__version__)
print("unsloth:", getattr(unsloth, "__version__", "unknown"))
print("transformers:", transformers.__version__)
print("HF_HOME:", os.environ.get("HF_HOME"))
PY