# 🔍 Training Monitoring Guide

## Quick Status Commands

### **Health Check**
```bash
bash scripts/health.sh
```

### **Current Progress**
```bash
# Last 3 training metrics
grep -E "step|loss|grad_norm" outputs_luanti_safe/training.log | tail -3

# Current step
grep -o '[0-9]*/1500' outputs_luanti_safe/training.log | tail -1

# GPU status
nvidia-smi --query-gpu=memory.used,utilization.gpu,temperature.gpu --format=csv,noheader
```

### **Live Monitoring**
```bash
# Training log (Ctrl+C to exit)
tail -f outputs_luanti_safe/training.log

# GPU utilization
watch -n 5 'nvidia-smi | head -15'

# Checkpoint watch (every 15 seconds)
bash scripts/watch_checkpoints.sh
```

## Expected Milestones

### **Training Progress**
- **First checkpoint**: Step 500 (~6.9 hours)
- **Training complete**: Step 1500 (~20.6 hours)
- **Loss target**: Expect continued decrease from 1.0273

### **Success Indicators**
- ✅ **Steps advancing**: Should see consistent progress
- ✅ **Loss decreasing**: Trend from 2.209 → 1.8967 → 1.0273
- ✅ **GPU engaged**: 13+ GB memory, 65%+ utilization
- ✅ **Stable performance**: ~8s/step consistently

### **Warning Signs**
- ❌ **Steps stalled**: No progress for >10 minutes
- ❌ **Loss spiking**: Sudden increase in loss values
- ❌ **GPU idle**: Memory drops below 10GB
- ❌ **Temperature high**: GPU >80°C for extended periods

## Recovery Commands

### **If Training Stalls**
```bash
# Check process status
ps aux | grep train_luanti_cosmic

# Check tmux session
tmux list-sessions
tmux attach -t luanti_final_training

# Restart if needed
bash run_gateb_train.sh
```

### **If Checkpoint Issues**
```bash
# Verify checkpoint structure
ls -la outputs_luanti_safe/checkpoint-*/
du -sh outputs_luanti_safe/checkpoint-*/

# Check adapter files
ls -la outputs_luanti_safe/checkpoint-*/adapter_*
```

## Gate D Preparation

When first checkpoint appears:
```bash
# Gate D: Adapter Testing
tmux new -s luanti_eval
source "$HOME/miniconda3/etc/profile.d/conda.sh" && conda activate gptoss
PY="/home/tdeshane/miniconda3/envs/gptoss/bin/python"
HF_HUB_OFFLINE= TOKENIZERS_PARALLELISM=false TORCHDYNAMO_DISABLE=1 \
stdbuf -oL -eL "$PY" -u -m eval.test_adapter \
  --base unsloth/gpt-oss-20b-unsloth-bnb-4bit \
  --adapters_dir outputs_luanti_safe \
  --eval data/eval/luanti_eval.jsonl \
  --template prompts/iir_template.txt \
  --k 5 --temperature 0.2 --top_p 0.9 --max_new_tokens 300 \
  --scales 0.25 0.5 1.0 --seed 3407 \
  --out_dir eval/results/ | tee eval/results/test_adapter.log
```