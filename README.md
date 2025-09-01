# 🎯 Luanti Fine-tuning with GPT-OSS:20B

A complete pipeline for fine-tuning GPT-OSS:20B to become a Luanti (Minetest) expert using QLoRA on RTX 3090.

[![Model](https://img.shields.io/badge/Model-GPT--OSS%3A20B-blue)](https://huggingface.co/unsloth/gpt-oss-20b-unsloth-bnb-4bit)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-yellow)](https://www.python.org/)
[![Unsloth](https://img.shields.io/badge/Powered%20by-Unsloth%20🦥-orange)](https://unsloth.ai)

## 🎪 **Current Progress**

### ✅ **Phase 1: Data Collection & Quality Analysis (COMPLETE)**
- **2,920 Luanti packages** collected from ContentDB
- **2,592 packages with repositories** analyzed for code quality
- **License separation**: Commercial-safe (1,387) vs Complete (2,592) datasets
- **Quality analysis**: No AI-generated code detected, high-quality Lua patterns
- **Repository distribution**: GitHub (64%), Codeberg (11%), GitLab (8%)

### ✅ **Phase 2: Environment Setup & Troubleshooting (COMPLETE)**
- **Working environment identified**: `gptoss` (Unsloth 2025.8.7, Torch 2.5.0+cu124)
- **Local model cache**: 12.6GB GPT-OSS:20B model cached locally
- **RTX 3090 verified**: CUDA 13.0 driver, 24GB memory available

### 🔄 **Phase 3: Baseline Evaluation (IN PROGRESS)**
- **Gate A2 PASSED**: CUDA + Unsloth + BitsAndBytes working
- **Gate B RUNNING**: Baseline evaluation in progress  
  - **Progress**: 11/60 items evaluated (18.3% complete)
  - **GPU usage**: 12.7GB memory, 59% utilization
  - **Performance**: Model loaded successfully, evaluation advancing steadily

### ⏳ **Phase 4: QLoRA Training (READY)**
- **Training config**: Layers 19-23, LoRA r=8, attention-only
- **Dataset ready**: 600 training items (scaffold, repair, doc tasks)
- **Environment verified**: Working setup locked and documented

### ⏳ **Phase 5: Evaluation & Decision (PENDING)**
- **Success threshold**: +15pp improvement in pass@5
- **Multi-scale testing**: LoRA scales 0.25, 0.5, 1.0
- **Decision framework**: Automated comparison and recommendations

---

## 📊 **Datasets**

### **Luanti Package Collection**
- **📁 Complete Dataset**: [ToddLLM/luanti-complete-dataset](https://huggingface.co/datasets/ToddLLM/luanti-complete-dataset) (2,592 packages)
- **🏢 Commercial Dataset**: [ToddLLM/luanti-commercial-dataset](https://huggingface.co/datasets/ToddLLM/luanti-commercial-dataset) (1,387 packages, MIT/BSD/Apache)
- **⚖️ Copyleft Dataset**: [ToddLLM/luanti-copyleft-dataset](https://huggingface.co/datasets/ToddLLM/luanti-copyleft-dataset) (1,073 packages, GPL/LGPL)

### **Fine-tuning Datasets** 
- **🎯 Capability Dataset**: [ToddLLM/luanti-capability-training](https://huggingface.co/datasets/ToddLLM/luanti-capability-training) (600 training items)
- **📊 Evaluation Dataset**: [ToddLLM/luanti-capability-eval](https://huggingface.co/datasets/ToddLLM/luanti-capability-eval) (60 test items)

---

## 🚀 **Quick Start**

### **Environment Setup (Working Configuration)**
```bash
# Use proven working environment
conda activate gptoss  # Pre-existing environment with correct versions

# Required versions (locked-in):
# - Unsloth: 2025.8.7
# - Torch: 2.5.0+cu124  
# - CUDA Toolkit: 12.4
# - xformers: 0.0.28.post2
```

### **Run Baseline Evaluation**
```bash
cd ~/luanti_capability
source env/working_env.sh  # Sets all required environment variables

# Gate B - Baseline (currently running)
PY="/home/tdeshane/miniconda3/envs/gptoss/bin/python"
PYTHONUNBUFFERED=1 stdbuf -oL -eL \
"$PY" -u -m eval.run_eval \
  --base unsloth/gpt-oss-20b-unsloth-bnb-4bit \
  --eval data/eval/luanti_eval.jsonl \
  --template prompts/iir_template.txt \
  --out eval/results/baseline.json \
  --k 5 --temperature 0.2 --top_p 0.9 --max_new_tokens 300 --seed 3407 \
  2>&1 | tee eval/results/baseline.log
```

### **QLoRA Training (After Baseline Completes)**
```bash
# Gate C - Training
tmux new -s luanti_training
cd ~/luanti_capability
export HF_HOME="$PWD/.cache/hf" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
PY="/home/tdeshane/miniconda3/envs/gptoss/bin/python"
PYTHONUNBUFFERED=1 stdbuf -oL -eL \
"$PY" -u training/train_luanti_gptoss_qlora.py \
  --config training/config.yaml \
  --train data/train/luanti_train.jsonl \
  --out adapters/ | tee training.log
```

---

## 📋 **Project Structure**

```
luanti_capability/
├── env/
│   ├── working_env.sh          ✅ Proven working environment setup
│   ├── assert_working_env.py   ✅ Version verification tool
│   ├── conda_list_gptoss.txt   ✅ Frozen working conda packages
│   └── pip_freeze_gptoss.txt   ✅ Frozen working pip packages
├── data/
│   ├── eval/luanti_eval.jsonl  ✅ 60 test items (20 scaffold, 20 repair, 20 doc)
│   ├── train/luanti_train.jsonl ✅ 600 training items
│   └── schemas.md              ✅ Data format specification
├── prompts/
│   ├── iir_template.txt        ✅ Instruction/Input/Response template
│   └── formatter.py            ✅ Template formatter (tested)
├── training/
│   ├── config.yaml             ✅ QLoRA config (layers 19-23, r=8)
│   └── train_luanti_gptoss_qlora.py ✅ Training script
├── eval/
│   ├── static_checks.py        ✅ Lua validation + regex checks
│   ├── apply_patch.py          ✅ Unified diff applier
│   ├── run_eval.py             ✅ Baseline evaluation
│   ├── test_adapter.py         ✅ Multi-scale adapter testing
│   ├── compare.py              ✅ +15pp decision framework
│   └── results/                🔄 Evaluation results (baseline running)
└── adapters/                   ⏳ Training checkpoints (pending)
```

---

## 🔬 **Technical Approach**

### **Fine-tuning Strategy**
- **Base Model**: GPT-OSS:20B (Mixture of Experts, 20.9B parameters)
- **Method**: QLoRA (4-bit quantization + LoRA adapters)
- **Target**: Attention layers only (19-23), no MoE experts
- **Safety**: MoE-safe training (no expert/router modifications)

### **Evaluation Framework**
- **Task Families**: Scaffold (node registration), Repair (code fixing), Doc (API usage)
- **Metrics**: pass@1 and pass@5 with automatic validation
- **Success Threshold**: +15 percentage points improvement in pass@5
- **Validation**: Lua syntax checking + regex pattern matching

### **Working Environment (Proven)**
```bash
Environment: gptoss (miniconda3/envs/gptoss)
Unsloth: 2025.8.7       ✅ Critical - newer versions hang
Torch: 2.5.0+cu124      ✅ Works with RTX 3090
CUDA Toolkit: 12.4     ✅ Compatible with driver 580
xformers: 0.0.28.post2  ✅ Required for efficiency
BitsAndBytes: 0.47.0    ✅ 4-bit quantization
```

---

## 📊 **Current Results**

### **Data Collection Results**
| Metric | Value |
|--------|-------|
| **Total packages** | 2,920 |
| **With repositories** | 2,592 (89%) |
| **Commercial-safe** | 1,387 (53.5%) |
| **Code quality** | High (no AI-generated code) |
| **Repository platforms** | GitHub (1,855), Codeberg (308), GitLab (227) |

### **Gate Progress**
| Gate | Status | Details |
|------|--------|---------|
| **A2** | ✅ PASSED | CUDA + RTX 3090 + BitsAndBytes verified |
| **B** | 🔄 RUNNING | 11/60 items (18.3%), 12.7GB GPU, 59% util |
| **C** | ⏳ READY | Training config verified, 600 items ready |
| **D** | ⏳ READY | Multi-scale testing prepared |
| **E** | ⏳ READY | +15pp decision framework ready |

### **Environment Troubleshooting**
| Issue | Solution |
|-------|----------|
| Unsloth 2025.8.10 hanging | ✅ Use Unsloth 2025.8.7 |
| Version conflicts | ✅ Use pre-existing `gptoss` environment |
| Model download loops | ✅ Local cache + filesystem paths |
| Tmux conda activation | ✅ Direct python interpreter paths |

---

## 🛠️ **Installation**

### **Prerequisites**
- Linux with NVIDIA GPU (RTX 3090 tested)
- CUDA 12.4+ compatible drivers
- 24GB+ GPU memory
- 50GB+ disk space

### **Environment Setup**
```bash
# Clone repository
git clone https://github.com/toddllm/luanti-fine-tune.git
cd luanti-fine-tune

# Use working environment (critical - don't create new)
conda activate gptoss  

# Verify environment
python env/assert_working_env.py

# Set cache variables
source env/working_env.sh
```

---

## 🎯 **Usage**

### **Gate B: Baseline Evaluation** 
```bash
tmux new -s luanti_baseline_local
cd ~/luanti_capability
PY="/home/tdeshane/miniconda3/envs/gptoss/bin/python"
PYTHONUNBUFFERED=1 stdbuf -oL -eL \
"$PY" -u -m eval.run_eval \
  --base unsloth/gpt-oss-20b-unsloth-bnb-4bit \
  --eval data/eval/luanti_eval.jsonl \
  --template prompts/iir_template.txt \
  --out eval/results/baseline.json \
  --k 5 --temperature 0.2 --top_p 0.9 --max_new_tokens 300 --seed 3407 \
  2>&1 | tee eval/results/baseline.log
```

### **Gate C: QLoRA Training**
```bash
tmux new -s luanti_training
cd ~/luanti_capability
export HF_HOME="$PWD/.cache/hf" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
PY="/home/tdeshane/miniconda3/envs/gptoss/bin/python"
PYTHONUNBUFFERED=1 stdbuf -oL -eL \
"$PY" -u training/train_luanti_gptoss_qlora.py \
  --config training/config.yaml \
  --train data/train/luanti_train.jsonl \
  --out adapters/ | tee training.log
```

### **Gate D: Adapter Testing**
```bash
tmux new -s luanti_eval
cd ~/luanti_capability
export HF_HOME="$PWD/.cache/hf" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
PY="/home/tdeshane/miniconda3/envs/gptoss/bin/python"
PYTHONUNBUFFERED=1 stdbuf -oL -eL \
"$PY" -u -m eval.test_adapter \
  --base unsloth/gpt-oss-20b-unsloth-bnb-4bit \
  --adapters_dir adapters/ \
  --eval data/eval/luanti_eval.jsonl \
  --template prompts/iir_template.txt \
  --k 5 --temperature 0.2 --top_p 0.9 --max_new_tokens 300 \
  --scales 0.25 0.5 1.0 --seed 3407 \
  --out_dir eval/results/ | tee eval/results/test_adapter.log
```

### **Gate E: Decision**
```bash
PY="/home/tdeshane/miniconda3/envs/gptoss/bin/python"
"$PY" -m eval.compare \
  --baseline eval/results/baseline.json \
  --results_dir eval/results/ | tee eval/results/deltas.txt
```

---

## 📈 **Success Criteria**

### **Gate Progression**
1. **Gate A2**: CUDA + Unsloth working ✅
2. **Gate B**: Baseline evaluation complete 🔄
3. **Gate C**: Training produces MB-sized adapters ⏳
4. **Gate D**: Multi-scale adapter testing ⏳
5. **Gate E**: +15pp improvement in pass@5 ⏳

### **Technical Metrics**
- **pass@1**: Percentage of items where first candidate passes validation
- **pass@5**: Percentage of items where any of 5 candidates passes
- **Families**: scaffold (node registration), repair (code fixes), doc (API usage)
- **Validation**: Lua syntax + regex pattern matching

---

## 🔧 **Configuration**

### **QLoRA Settings**
```yaml
base: unsloth/gpt-oss-20b-unsloth-bnb-4bit
lora:
  r: 8                    # Conservative rank for MoE stability
  alpha: 16               # Scale factor = 2.0
  dropout: 0.1            # Stability
  target_modules: [q_proj, k_proj, v_proj, o_proj]  # Attention only
layers: [19,20,21,22,23]  # Freeze adapters outside these layers
optim:
  lr: 5e-5                # Conservative learning rate
  warmup_ratio: 0.05      # 5% warmup
  grad_clip: 0.3          # Gradient clipping
trainer:
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 8  # Effective batch = 16
  max_steps: 3000
```

### **Environment Variables**
```bash
# Cache configuration
HF_HOME="$PWD/.cache/hf"
TRANSFORMERS_CACHE="$PWD/.cache/hf"

# Offline mode (prevents downloads)
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1

# CUDA configuration
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=128
```

---

## 🎪 **Key Features**

### **Luanti Expertise Tasks**
- **Scaffold**: Register nodes with required fields (tiles, light_source, description)
- **Repair**: Fix broken Lua code using unified diff format
- **Doc**: Generate correct API usage from documentation

### **Safety & Quality**
- **MoE-safe training**: Only attention layers, no expert modifications
- **Code validation**: Lua syntax checking with `luac` when available
- **License compliance**: Separate commercial and open-source datasets
- **Quality filtered**: No AI-generated code, security-vetted

### **Proven Working Setup**
- **Environment**: Pre-existing `gptoss` with verified versions
- **Local caching**: 12.6GB model cached to prevent re-downloads  
- **Tmux persistence**: Training survives SSH disconnects
- **Unbuffered logging**: Real-time progress monitoring

---

## 📖 **Documentation**

### **Core Documents**
- [**WORKING_ENV_SETUP.md**](WORKING_ENV_SETUP.md) - Proven environment configuration
- [**TMUX_RUNBOOK.md**](TMUX_RUNBOOK.md) - Complete execution guide
- [**data/schemas.md**](data/schemas.md) - Dataset format specification

### **Environment Tools**
- [`env/working_env.sh`](env/working_env.sh) - Environment setup script
- [`env/assert_working_env.py`](env/assert_working_env.py) - Version verification
- [`env/conda_list_gptoss.txt`](env/conda_list_gptoss.txt) - Frozen conda packages
- [`env/pip_freeze_gptoss.txt`](env/pip_freeze_gptoss.txt) - Frozen pip packages

---

## 🔬 **Research & Analysis**

### **Luanti Ecosystem Analysis**
- **Code Quality**: 72.4/100 average quality score across repositories  
- **No AI Code**: Zero AI-generated patterns detected in analysis
- **License Distribution**: 44.5% MIT, 8.6% GPL-3.0, 7.7% LGPL-2.1
- **Repository Quality**: Inverse correlation between popularity and code quality

### **Technical Innovations**
- **License-aware datasets**: Automatic separation for commercial vs open-source use
- **Quality filtering**: Automated code quality analysis and filtering
- **MoE-safe training**: Attention-only LoRA to avoid destabilizing experts
- **Validated evaluation**: Lua syntax + regex validation for technical accuracy

---

## 🚦 **Monitoring**

### **Progress Tracking**
```bash
# Monitor Gate B baseline evaluation
tail -f eval/results/baseline.log

# Monitor training (Gate C)
tail -f training.log
watch -n 10 'nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv'

# Check adapter sizes (should be MB, not GB)
du -sh adapters/ckpt-*
```

### **Success Indicators**
- **Gate B**: baseline.json created with family metrics
- **Gate C**: MB-sized checkpoints in adapters/ directory
- **Gate D**: ckpt-XXXX__scale-Y.json files with test results
- **Gate E**: +15pp improvement in pass@5 metric

---

## 🤝 **Contributing**

### **Current Status**
This project is under active development with live training runs on RTX 3090.

### **Areas for Contribution**
- Extended Luanti task families (crafting, world generation, server admin)
- Multi-language Luanti content (German, French, Spanish communities)
- Integration with Luanti development tools
- Performance optimizations for different GPU configurations

---

## 📄 **License**

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

### **Dataset Licensing**
- **Commercial Dataset**: MIT/BSD/Apache licensed content - safe for commercial use
- **Complete Dataset**: Mixed licenses including GPL - requires license compliance
- **Training Code**: Apache 2.0 - freely usable

---

## 🙏 **Acknowledgments**

### **Special Thanks**
- **[Unsloth](https://unsloth.ai)** for making 20B parameter fine-tuning possible on consumer hardware
- **Luanti Community** for creating the rich ecosystem of mods and games
- **ContentDB** for providing comprehensive package metadata
- **GPT-OSS** team for the excellent 20B parameter base model

---

## 📊 **Live Status**

**Last Updated**: September 1, 2025
**Current Phase**: Gate B baseline evaluation (11/60 items, 18.3% complete)
**Next Milestone**: Complete baseline → Start QLoRA training
**ETA**: Training completion within 4-6 hours

---

*This README will be updated as the training progresses through Gates C→D→E.*