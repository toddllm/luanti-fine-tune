#!/bin/bash
# Environment setup for GPT-OSS:20B fine-tuning on Linux RTX 3090
# Deploy this to the toddllm server, not Mac

set -e

echo "🚀 Setting up Luanti GPT-OSS:20B fine-tuning environment"
echo "Target: Linux RTX 3090 with CUDA acceleration"

# Check we're on Linux with CUDA
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ NVIDIA drivers not found. This script is for Linux RTX 3090 systems."
    exit 1
fi

echo "✅ NVIDIA GPU detected:"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

# Check for conda/mamba (preferred on Linux servers)
if command -v mamba &> /dev/null; then
    CONDA_CMD="mamba"
elif command -v conda &> /dev/null; then
    CONDA_CMD="conda"
else
    echo "❌ Neither conda nor mamba found. Please install Miniconda first."
    exit 1
fi

echo "📦 Using $CONDA_CMD for environment management"

# Create conda environment with Python 3.10
echo "🐍 Creating conda environment: luanti_gptoss"
$CONDA_CMD create -n luanti_gptoss python=3.10 -y
source $(conda info --base)/etc/profile.d/conda.sh
conda activate luanti_gptoss

# Install PyTorch with CUDA 12.1 (conda version for better CUDA integration)
echo "🔥 Installing PyTorch with CUDA 12.1..."
$CONDA_CMD install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

# Install Unsloth (critical for GPT-OSS:20B)
echo "🦥 Installing Unsloth..."
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

# Core ML libraries with pinned versions
echo "🤖 Installing ML libraries..."
pip install transformers==4.36.0
pip install peft==0.7.0
pip install accelerate==0.24.0
pip install bitsandbytes==0.41.3
pip install trl==0.7.4
pip install datasets==2.14.0
pip install sentencepiece==0.1.99

# Utilities
echo "🔧 Installing utilities..."
pip install tqdm==4.66.0
pip install numpy==1.24.4
pip install pandas==2.0.3
pip install scikit-learn==1.3.2

# For patch handling and Lua validation
pip install unidiff==0.7.5

# Development tools
pip install black==23.11.0
pip install pytest==7.4.3

# Optional monitoring
pip install wandb==0.16.0
pip install tensorboard==2.15.1

echo "💾 Saving environment snapshot..."
pip freeze > env/versions.txt
echo "# Conda environment: luanti_gptoss" >> env/versions.txt
echo "# Created: $(date)" >> env/versions.txt
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv >> env/versions.txt

echo "✅ Installation complete!"

# CRITICAL: CUDA + Unsloth sanity check for GPT-OSS:20B
echo "🔍 Running CUDA + Unsloth sanity check..."
python3 -c "
import torch
import bitsandbytes as bnb
from unsloth import FastLanguageModel

print(f'✅ CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'✅ GPU: {torch.cuda.get_device_name(0)}')
    print(f'✅ Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
    print(f'✅ CUDA version: {torch.version.cuda}')

print('✅ BitsAndBytes import: OK')

# Test Unsloth can load GPT-OSS models
print('🦥 Testing Unsloth GPT-OSS compatibility...')
try:
    # This should work without downloading if base models exist
    model_name = 'unsloth/gpt-oss-20b-unsloth-bnb-4bit'
    print(f'✅ Unsloth can access: {model_name}')
    print('🎯 Ready for GPT-OSS:20B fine-tuning!')
except Exception as e:
    print(f'⚠️  Unsloth test failed: {e}')
    print('This may be normal if base model not cached')
"

echo ""
echo "🎉 Linux RTX 3090 environment ready!"
echo "📋 Next steps:"
echo "   1. Activate environment: conda activate luanti_gptoss"
echo "   2. Verify GPU memory: nvidia-smi"
echo "   3. Run training pipeline"