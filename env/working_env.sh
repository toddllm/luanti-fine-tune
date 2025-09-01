#!/bin/bash
# Working Environment Setup - PROVEN TO WORK
# Use this exact setup for all gates

# CRITICAL: Use miniconda3 (not miniconda) and gptoss environment
export PATH=$HOME/miniconda3/bin:$PATH
source $(conda info --base)/etc/profile.d/conda.sh
conda activate gptoss

# Cache setup that works
export HF_HOME="$PWD/.cache/hf"
export TRANSFORMERS_CACHE="$PWD/.cache/hf"
export CUDA_VISIBLE_DEVICES=0

# Python interpreter path that works
export PY="/home/tdeshane/miniconda3/envs/gptoss/bin/python"

echo "🎯 WORKING ENVIRONMENT ACTIVATED"
echo "   Environment: gptoss (proven working)"
echo "   Python: $PY"
echo "   Cache: $HF_HOME"
echo "   CUDA device: $CUDA_VISIBLE_DEVICES"

# Verify environment
$PY /home/tdeshane/luanti_capability/env/assert_working_env.py