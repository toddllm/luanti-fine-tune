#!/bin/bash
# Tmux environment setup - source this in each session
# Keeps all environment variables consistent

export PATH=$HOME/miniconda/bin:$PATH
export HF_HOME="$PWD/.cache/hf"
export TRANSFORMERS_CACHE="$PWD/.cache/hf" 
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=128

# Activate conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate luanti_gptoss

echo "🍎 Environment activated for tmux session"
echo "   CUDA device: $CUDA_VISIBLE_DEVICES"
echo "   Cache location: $HF_HOME"
echo "   Conda env: luanti_gptoss"