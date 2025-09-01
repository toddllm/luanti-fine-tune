#!/usr/bin/env python3
"""
Adapter Testing Pipeline - Test multiple checkpoints at multiple scales
EXACT implementation as specified
"""

import json
import argparse
import torch
from pathlib import Path
from typing import Dict, List
import sys

# Import validation and formatting
from static_checks import validate_family
from apply_patch import apply_patch
sys.path.append('../prompts')
from formatter import format_for_inference

from unsloth import FastLanguageModel
from peft import PeftModel

def load_base_with_adapter(base_model_name: str, adapter_path: str, scale: float = 1.0):
    """
    Load base model + adapter at specified scale
    
    Args:
        base_model_name: Base model identifier
        adapter_path: Path to adapter checkpoint
        scale: LoRA scaling factor (0.25, 0.5, 1.0)
    """
    # Load base model
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=base_model_name,
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
    )
    
    # Load adapter
    model = PeftModel.from_pretrained(model, adapter_path)
    
    # Apply scaling if not 1.0
    if scale != 1.0:
        print(f"🎛️  Applying LoRA scale: {scale}")
        for name, module in model.named_modules():
            if hasattr(module, 'lora_B'):
                for adapter_name in module.lora_B:
                    if not hasattr(module.lora_B[adapter_name], 'original_weight'):
                        module.lora_B[adapter_name].original_weight = module.lora_B[adapter_name].weight.data.clone()
                    module.lora_B[adapter_name].weight.data = module.lora_B[adapter_name].original_weight * scale
    
    # Set for inference
    FastLanguageModel.for_inference(model)
    
    return model, tokenizer

def generate_candidates(model, tokenizer, prompt: str, k: int = 5, 
                       temperature: float = 0.2, top_p: float = 0.9, 
                       max_new_tokens: int = 300) -> List[str]:
    """Generate k candidates - identical to baseline evaluation"""
    candidates = []
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    for i in range(k):
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        
        full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = full_text[len(prompt):].strip()
        candidates.append(response)
    
    return candidates

def evaluate_item(item: Dict, model, tokenizer, k: int = 5, **gen_kwargs) -> Dict:
    """Evaluate single item - identical logic to baseline"""
    prompt = format_for_inference(item["instruction"], item.get("input", ""))
    candidates = generate_candidates(model, tokenizer, prompt, k, **gen_kwargs)
    
    results = []
    for i, candidate in enumerate(candidates):
        
        if item["family"] == "repair":
            base_code = item.get("input", "")
            patched_code = apply_patch(base_code, candidate)
            
            if patched_code.startswith("ERROR:"):
                valid = False
            else:
                valid = validate_family(patched_code, "scaffold")
        else:
            valid = validate_family(candidate, item["family"])
        
        results.append({
            "candidate_id": i,
            "output": candidate,
            "valid": valid
        })
    
    pass_at_1 = 1 if len(results) > 0 and results[0]["valid"] else 0
    pass_at_k = 1 if any(r["valid"] for r in results) else 0
    
    return {
        "instruction": item["instruction"],
        "input": item.get("input", ""),
        "family": item["family"],
        "candidates": results,
        "pass_at_1": pass_at_1,
        "pass_at_k": pass_at_k
    }

def test_single_adapter(base_model: str, adapter_path: str, eval_file: str, 
                       scale: float, k: int, seed: int, output_file: str, **gen_kwargs):
    """Test a single adapter at a specific scale"""
    
    print(f"🧪 Testing adapter: {adapter_path} at scale {scale}")
    
    # Set seeds
    torch.manual_seed(seed)
    
    # Load model with adapter
    model, tokenizer = load_base_with_adapter(base_model, adapter_path, scale)
    
    # Load eval data
    eval_items = []
    with open(eval_file, 'r') as f:
        for line in f:
            eval_items.append(json.loads(line))
    
    # Evaluate all items
    results = []
    for i, item in enumerate(eval_items):
        print(f"   Item {i+1}/{len(eval_items)}: {item['family']}")
        result = evaluate_item(item, model, tokenizer, k, **gen_kwargs)
        results.append(result)
    
    # Calculate metrics
    total_items = len(results)
    pass_at_1_total = sum(r["pass_at_1"] for r in results)
    pass_at_k_total = sum(r["pass_at_k"] for r in results)
    
    # Per-family metrics
    family_metrics = {}
    for family in ['scaffold', 'repair', 'doc']:
        family_results = [r for r in results if r['family'] == family]
        if family_results:
            family_pass_1 = sum(r["pass_at_1"] for r in family_results)
            family_pass_k = sum(r["pass_at_k"] for r in family_results)
            family_metrics[family] = {
                "count": len(family_results),
                "pass_at_1": family_pass_1 / len(family_results),
                "pass_at_k": family_pass_k / len(family_results)
            }
    
    # Save results
    final_results = {
        "adapter_path": adapter_path,
        "scale": scale,
        "base_model": base_model,
        "eval_file": eval_file,
        "generation_params": gen_kwargs,
        "seed": seed,
        "k": k,
        "overall_metrics": {
            "total_items": total_items,
            "pass_at_1": pass_at_1_total / total_items,
            "pass_at_k": pass_at_k_total / total_items
        },
        "family_metrics": family_metrics,
        "detailed_results": results
    }
    
    with open(output_file, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"✅ Results saved: {output_file}")
    print(f"   pass@1: {pass_at_1_total}/{total_items} = {pass_at_1_total/total_items:.2%}")
    print(f"   pass@{k}: {pass_at_k_total}/{total_items} = {pass_at_k_total/total_items:.2%}")

def main():
    """Main adapter testing function - exact CLI as specified"""
    parser = argparse.ArgumentParser(description="Test adapters at multiple scales")
    parser.add_argument("--base", required=True, help="Base model name")
    parser.add_argument("--adapters_dir", required=True, help="Directory containing adapter checkpoints")
    parser.add_argument("--eval", required=True, help="Evaluation JSONL file")
    parser.add_argument("--template", required=True, help="Template file")
    parser.add_argument("--k", type=int, default=5, help="Number of candidates")
    parser.add_argument("--temperature", type=float, default=0.2, help="Generation temperature")
    parser.add_argument("--top_p", type=float, default=0.9, help="Top-p sampling")
    parser.add_argument("--max_new_tokens", type=int, default=300, help="Max new tokens")
    parser.add_argument("--scales", nargs="+", type=float, default=[0.25, 0.5, 1.0], help="LoRA scales to test")
    parser.add_argument("--seed", type=int, default=3407, help="Random seed")
    parser.add_argument("--out_dir", required=True, help="Output directory for results")
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    
    # Find all adapter checkpoints
    adapters_dir = Path(args.adapters_dir)
    checkpoint_dirs = [d for d in adapters_dir.iterdir() if d.is_dir() and d.name.startswith('ckpt-')]
    checkpoint_dirs.sort()  # Process in order
    
    if not checkpoint_dirs:
        raise FileNotFoundError(f"No checkpoint directories found in {adapters_dir}")
    
    print(f"🔍 Found {len(checkpoint_dirs)} adapter checkpoints")
    print(f"🎯 Testing {len(args.scales)} scales: {args.scales}")
    
    # Test each checkpoint at each scale
    for checkpoint_dir in checkpoint_dirs:
        for scale in args.scales:
            checkpoint_name = checkpoint_dir.name
            output_file = Path(args.out_dir) / f"{checkpoint_name}__scale-{scale}.json"
            
            test_single_adapter(
                base_model=args.base,
                adapter_path=str(checkpoint_dir),
                eval_file=args.eval,
                scale=scale,
                k=args.k,
                seed=args.seed,
                output_file=str(output_file),
                temperature=args.temperature,
                top_p=args.top_p,
                max_new_tokens=args.max_new_tokens
            )
    
    print(f"\n🎉 All adapter tests complete!")
    print(f"📁 Results in: {args.out_dir}")

if __name__ == "__main__":
    main()