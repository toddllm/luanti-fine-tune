#!/usr/bin/env python3
"""
Baseline inference evaluation for GPT-OSS:20B
EXACT implementation as specified - no deviations
"""

import json
import argparse
import random
from pathlib import Path
from typing import Dict, List
import torch

# Import validation functions
import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '../prompts'))

from static_checks import validate_family
from apply_patch import apply_patch
from formatter import format_for_inference

def load_model_and_tokenizer(model_name: str):
    """
    Load GPT-OSS:20B model using Unsloth 4-bit
    CRITICAL: This must run on Linux RTX 3090, not Mac
    """
    try:
        from unsloth import FastLanguageModel
        
        print(f"📥 Loading {model_name} (4-bit)...")
        
        # Load exactly as specified
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_name,
            max_seq_length=2048,
            dtype=None,
            load_in_4bit=True,
            local_files_only=True,
        )
        
        # Set for inference
        FastLanguageModel.for_inference(model)
        
        print("✅ Model loaded successfully")
        return model, tokenizer
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        print("CRITICAL: This evaluation must run on Linux RTX 3090 with Unsloth")
        raise

def generate_candidates(model, tokenizer, prompt: str, k: int = 5, 
                       temperature: float = 0.2, top_p: float = 0.9, 
                       max_new_tokens: int = 300) -> List[str]:
    """
    Generate k candidates using exact specified parameters
    """
    candidates = []
    
    # Tokenize input
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
        
        # Decode and extract response
        full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = full_text[len(prompt):].strip()
        candidates.append(response)
    
    return candidates

def evaluate_item(item: Dict, model, tokenizer, k: int = 5, **gen_kwargs) -> Dict:
    """
    Evaluate a single item with k candidates
    """
    # Format prompt for inference using exact IIR template
    prompt = format_for_inference(item["instruction"], item.get("input", ""))
    
    # Generate candidates
    candidates = generate_candidates(model, tokenizer, prompt, k, **gen_kwargs)
    
    # Evaluate each candidate
    results = []
    for i, candidate in enumerate(candidates):
        
        if item["family"] == "repair":
            # For repair: apply patch to input, then validate
            base_code = item.get("input", "")
            patched_code = apply_patch(base_code, candidate)
            
            if patched_code.startswith("ERROR:"):
                valid = False
            else:
                # Check if patched code is valid Lua and has required patterns
                valid = validate_family(patched_code, "scaffold")  # Check as node registration
        else:
            # For scaffold/doc: validate output directly
            valid = validate_family(candidate, item["family"])
        
        results.append({
            "candidate_id": i,
            "output": candidate,
            "valid": valid
        })
    
    # Calculate pass@k metrics
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

def run_evaluation(model_name: str, eval_file: str, template_file: str, 
                  output_file: str, k: int = 5, seed: int = 3407, **gen_kwargs) -> None:
    """
    Run baseline evaluation with exact parameters as specified
    """
    # Set random seed
    random.seed(seed)
    torch.manual_seed(seed)
    
    print(f"🎯 Starting baseline evaluation")
    print(f"   Model: {model_name}")
    print(f"   Eval file: {eval_file}")
    print(f"   k: {k}, seed: {seed}")
    print(f"   Generation params: {gen_kwargs}")
    
    # Load model
    model, tokenizer = load_model_and_tokenizer(model_name)
    
    # Load evaluation data
    eval_items = []
    with open(eval_file, 'r') as f:
        for line in f:
            eval_items.append(json.loads(line))
    
    print(f"📊 Loaded {len(eval_items)} evaluation items")
    
    # Count by family
    family_counts = {}
    for item in eval_items:
        family_counts[item['family']] = family_counts.get(item['family'], 0) + 1
    print(f"   Family distribution: {family_counts}")
    
    # Evaluate each item
    results = []
    for i, item in enumerate(eval_items):
        print(f"   Evaluating {i+1}/{len(eval_items)}: {item['family']}")
        
        result = evaluate_item(item, model, tokenizer, k, **gen_kwargs)
        results.append(result)
    
    # Calculate overall metrics
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
    
    # Create final results
    final_results = {
        "model_name": model_name,
        "eval_file": eval_file,
        "generation_params": gen_kwargs,
        "seed": seed,
        "k": k,
        "timestamp": "",  # Will be filled by caller
        "overall_metrics": {
            "total_items": total_items,
            "pass_at_1": pass_at_1_total / total_items,
            "pass_at_k": pass_at_k_total / total_items
        },
        "family_metrics": family_metrics,
        "detailed_results": results
    }
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    # Print summary
    print(f"\n📊 BASELINE EVALUATION COMPLETE")
    print(f"   Overall pass@1: {pass_at_1_total}/{total_items} = {pass_at_1_total/total_items:.2%}")
    print(f"   Overall pass@{k}: {pass_at_k_total}/{total_items} = {pass_at_k_total/total_items:.2%}")
    
    for family, metrics in family_metrics.items():
        count = metrics['count']
        p1 = metrics['pass_at_1'] 
        pk = metrics['pass_at_k']
        print(f"   {family}: pass@1={p1:.2%}, pass@{k}={pk:.2%} (n={count})")
    
    print(f"💾 Results saved to: {output_file}")

def main():
    """Main evaluation function - exact CLI as specified"""
    parser = argparse.ArgumentParser(description="Baseline GPT-OSS:20B evaluation")
    parser.add_argument("--base", required=True, help="Base model name")
    parser.add_argument("--eval", required=True, help="Evaluation JSONL file") 
    parser.add_argument("--template", required=True, help="Template file")
    parser.add_argument("--out", required=True, help="Output JSON file")
    parser.add_argument("--k", type=int, default=5, help="Number of candidates")
    parser.add_argument("--temperature", type=float, default=0.2, help="Generation temperature")
    parser.add_argument("--top_p", type=float, default=0.9, help="Top-p sampling")
    parser.add_argument("--max_new_tokens", type=int, default=300, help="Max new tokens")
    parser.add_argument("--seed", type=int, default=3407, help="Random seed")
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    
    # Run evaluation with exact parameters
    run_evaluation(
        model_name=args.base,
        eval_file=args.eval,
        template_file=args.template,
        output_file=args.out,
        k=args.k,
        seed=args.seed,
        temperature=args.temperature,
        top_p=args.top_p,
        max_new_tokens=args.max_new_tokens
    )

if __name__ == "__main__":
    main()