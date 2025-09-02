# RUNBOOK — Luanti QLoRA (GPT-OSS:20B) on RTX 3090

## Start (Gate-B parity env)
tmux new -s luanti_training -A
bash ~/luanti_capability/run_gateb_train.sh

## Must-see log beacons
- "Loading checkpoint shards: 100%"
- "LoRA placement verified" (attention-only)
- "Aligned 96 LoRA matrices to dtype=torch.bfloat16"
- "Preflight eager step OK (loss=…)"
- "Dataset: … (lines=600)"
- "Starting training..." + steps ticking up

## Env switches required
- HF_HUB_OFFLINE **unset**
- HF_HOME=$PWD/.cache/hf
- TORCHDYNAMO_DISABLE=1
- TOKENIZERS_PARALLELISM=false
- import unsloth **before** transformers

## Where things land
- Logs: outputs_luanti_safe/training.log
- Checkpoints: outputs_*/checkpoint-*/
- Eval: eval/results/* (Gate D)

## Troubleshooting
- Stuck at load → verify env versions + unset offline
- "accelerator_scaler" → clear ~/.cache/unsloth_compiled_cache and use project .unsloth_cache
- Dataset path → set LUANTI_TRAIN_PATH=/abs/path
