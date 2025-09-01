#!/bin/bash
# Complete deployment script for toddllm server
# Run this after transferring the package

set -e

echo "🎯 Luanti Fine-tuning Deployment Script"
echo "Target: Linux RTX 3090 (toddllm server)"

# Environment setup
export PATH=$HOME/miniconda/bin:$PATH
export HF_HOME="$PWD/.cache/hf"  
export TRANSFORMERS_CACHE="$PWD/.cache/hf"
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=128

# Create cache directories
mkdir -p .cache/hf

echo "📋 Environment setup complete"
echo "💡 Next steps:"
echo "   1. conda activate luanti_gptoss"
echo "   2. Follow TMUX_RUNBOOK.md for step-by-step execution"
echo "   3. Use tmux sessions for persistent training"

echo ""
echo "🚀 Quick start commands:"
echo "   # Health check:"
echo "   conda activate luanti_gptoss && python -c \"import torch; print('CUDA:', torch.cuda.is_available())\""
echo ""
echo "   # Start baseline in tmux:"
echo "   tmux new -s luanti_baseline"
echo "   conda activate luanti_gptoss"
echo "   python -m eval.run_eval --base unsloth/gpt-oss-20b-unsloth-bnb-4bit --eval data/eval/luanti_eval.jsonl --template prompts/iir_template.txt --out eval/results/baseline.json --k 5 --temperature 0.2 --top_p 0.9 --max_new_tokens 300 --seed 3407"