#!/usr/bin/env python3
"""
QLoRA Training for GPT-OSS:20B - Luanti Capability
EXACT implementation following specifications - NO DEVIATIONS
"""

import yaml
import json
import argparse
import logging
import re
from pathlib import Path
from datetime import datetime
import sys
import torch

# Add prompts to path for formatter
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../prompts'))
from formatter import format_for_training

from unsloth import FastLanguageModel
from datasets import Dataset
from trl import SFTTrainer
from transformers import TrainingArguments, BitsAndBytesConfig
import wandb

# ==== CRITICAL FIX: Force eager + no compilers ====
os.environ["TORCHDYNAMO_DISABLE"] = "1"
os.environ["TORCHINDUCTOR_DISABLE"] = "1"
os.environ["PYTORCH_TRITON_DISABLE"] = "1"
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

# ==== CRITICAL FIX: Force FP16 globally ====
torch.set_default_dtype(torch.float32)
torch.backends.cuda.matmul.allow_tf32 = True
DT = torch.float16

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LuantiQLoRATrainer:
    """QLoRA trainer with exact specifications"""
    
    def __init__(self, config_path: str):
        """Load configuration exactly as specified"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        logger.info("📋 Configuration loaded:")
        logger.info(f"   Base model: {self.config['base']}")
        logger.info(f"   LoRA config: {self.config['lora']}")
        logger.info(f"   Target layers: {self.config['layers']}")
    
    def load_base_model(self):
        """Load GPT-OSS:20B base model via Unsloth 4-bit - EXACT GATE B PATTERN"""
        logger.info("📥 Loading GPT-OSS:20B base model (4-bit)...")
        
        # --- begin: canonical loader with FP16 fix ---
        import os
        BASE_REPO = "unsloth/gpt-oss-20b-unsloth-bnb-4bit"   # DO NOT change to filesystem path
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        
        # FP16 BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=DT,
            bnb_4bit_use_double_quant=True,
        )
        
        print("[A] from_pretrained(fp16)…", flush=True)
        # Exact call pattern with FP16 fix:
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=BASE_REPO,
            max_seq_length=self.config['max_len'],
            load_in_4bit=True,
            dtype=DT,  # CRITICAL: Force FP16
            local_files_only=True,
            quantization_config=bnb_config,
        )
        print("[A1] base dtype:", model.config.torch_dtype, flush=True)
        # --- end: canonical loader ---
        
        logger.info("✅ Base model loaded")
        return model, tokenizer
    
    def setup_lora(self, model):
        """Setup LoRA with EXACT specifications - attention only, specific layers"""
        logger.info("🔧 Setting up LoRA - ATTENTION ONLY, LAYERS 19-23")
        
        print("[B] get_peft_model(fp16 attn-only)…", flush=True)
        # Add LoRA adapters (attention-only; leave MoE alone)
        model = FastLanguageModel.get_peft_model(
            model,
            r=self.config['lora']['r'],
            lora_alpha=self.config['lora']['alpha'],
            lora_dropout=self.config['lora']['dropout'],
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # EXACTLY attention-only
            bias="none",
            use_gradient_checkpointing=False,  # Keep OFF for first successful run
            random_state=3407,
        )
        
        # CRITICAL FIX: Force LoRA params to FP16
        for n, m in model.named_modules():
            if hasattr(m, "lora_A"):
                for k in m.lora_A.keys():
                    m.lora_A[k].weight.data = m.lora_A[k].weight.data.to(DT)
                    m.lora_B[k].weight.data = m.lora_B[k].weight.data.to(DT)
        
        # Ensure all trainable params are FP16
        for p in model.parameters():
            if p.requires_grad and p.dtype != DT:
                p.data = p.data.to(DT)
        
        print("[B1] LoRA dtypes fixed to FP16", flush=True)
        
        # CRITICAL: Freeze adapters outside layers 19-23
        logger.info("🔒 Freezing adapters outside layers 19-23...")
        target_layers = set(self.config['layers'])
        
        frozen_count = 0
        kept_count = 0
        
        for name, param in model.named_parameters():
            if 'lora_' in name:
                # Extract layer number from parameter name
                layer_match = re.search(r'\.layers\.(\d+)\.', name)
                if layer_match:
                    layer_num = int(layer_match.group(1))
                    if layer_num not in target_layers:
                        param.requires_grad = False
                        frozen_count += 1
                    else:
                        kept_count += 1
                else:
                    # If we can't determine layer, freeze it to be safe
                    param.requires_grad = False
                    frozen_count += 1
        
        logger.info(f"   Kept trainable: {kept_count} LoRA parameters")
        logger.info(f"   Frozen: {frozen_count} LoRA parameters")
        
        # ASSERT: No MoE components are trainable
        dangerous_patterns = ['.experts.', '.router', '.gate', '.switch']
        for name, param in model.named_parameters():
            if param.requires_grad and any(pattern in name for pattern in dangerous_patterns):
                raise RuntimeError(f"CRITICAL: MoE component {name} is trainable! This violates safety constraints.")
        
        logger.info("✅ LoRA setup complete - MoE safety verified")
        return model
    
    def load_dataset(self, train_file: str):
        """Load and format training dataset"""
        logger.info(f"📚 Loading training dataset: {train_file}")
        
        # Load JSONL data
        data = []
        with open(train_file, 'r') as f:
            for line in f:
                item = json.loads(line)
                # Format using exact IIR template
                formatted_text = format_for_training(item)
                data.append({"text": formatted_text})
        
        # Convert to HuggingFace dataset
        dataset = Dataset.from_list(data)
        
        logger.info(f"✅ Dataset loaded: {len(dataset)} items")
        return dataset
    
    def setup_training_args(self, output_dir: str):
        """Setup training arguments from config"""
        trainer_config = self.config['trainer']
        optim_config = self.config['optim']
        
        args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            
            # Exact parameters from config.yaml
            per_device_train_batch_size=trainer_config['per_device_train_batch_size'],
            gradient_accumulation_steps=trainer_config['gradient_accumulation_steps'],
            max_steps=trainer_config['max_steps'],
            
            # Optimizer settings
            learning_rate=optim_config['lr'],
            warmup_ratio=optim_config['warmup_ratio'],
            max_grad_norm=optim_config['grad_clip'],
            
            # Logging and saving
            logging_steps=trainer_config['logging_steps'],
            save_steps=trainer_config['save_steps'],
            save_total_limit=trainer_config['save_total_limit'],
            
            # Precision (exact from config)
            fp16=trainer_config['fp16'],
            bf16=trainer_config['bf16'],
            
            # Other settings
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            seed=3407,
            data_seed=3407,
            
            # Disable unnecessary features
            evaluation_strategy="no",
            save_strategy="steps",
            report_to=[],  # No wandb for now
            
            # Memory optimization
            dataloader_pin_memory=True,
            remove_unused_columns=False,
        )
        
        return args
    
    def train(self, train_file: str, output_dir: str):
        """Execute training with exact specifications"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Load base model
        model, tokenizer = self.load_base_model()
        
        # Setup LoRA
        model = self.setup_lora(model)
        
        # Load dataset
        dataset = self.load_dataset(train_file)
        
        # Setup training arguments
        training_args = self.setup_training_args(str(output_path))
        
        # Create trainer
        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=dataset,
            args=training_args,
            dataset_text_field="text",
            max_seq_length=self.config['max_len'],
            packing=False,  # Keep sequences separate
        )
        
        logger.info("🚀 Starting QLoRA training...")
        logger.info(f"   Effective batch size: {training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps}")
        logger.info(f"   Total steps: {training_args.max_steps}")
        logger.info(f"   Save every: {training_args.save_steps} steps")
        
        # Train
        trainer.train()
        
        # Save final adapter
        final_path = output_path / "final"
        trainer.save_model(str(final_path))
        
        logger.info(f"✅ Training complete! Adapters saved to {output_path}")
        
        return str(output_path)

def main():
    """Main training function with exact CLI"""
    parser = argparse.ArgumentParser(description="Luanti QLoRA Training")
    parser.add_argument("--config", required=True, help="Config YAML file")
    parser.add_argument("--train", required=True, help="Training JSONL file")
    parser.add_argument("--out", required=True, help="Output directory for adapters")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not Path(args.config).exists():
        raise FileNotFoundError(f"Config file not found: {args.config}")
    if not Path(args.train).exists():
        raise FileNotFoundError(f"Training file not found: {args.train}")
    
    # Initialize trainer
    trainer = LuantiQLoRATrainer(args.config)
    
    # Execute training
    trainer.train(args.train, args.out)

if __name__ == "__main__":
    main()