#!/usr/bin/env python3
"""
Comparison framework - Compare adapter results to baseline
Implements exact +15pp decision rule
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List

def load_results(file_path: str) -> Dict:
    """Load results JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def find_best_adapter(results_dir: str) -> Dict:
    """Find the best performing adapter across all checkpoints and scales"""
    
    results_path = Path(results_dir)
    result_files = list(results_path.glob("ckpt-*__scale-*.json"))
    
    if not result_files:
        raise FileNotFoundError(f"No adapter result files found in {results_dir}")
    
    best_adapter = None
    best_score = 0.0
    
    print(f"🔍 Analyzing {len(result_files)} adapter results...")
    
    for result_file in result_files:
        try:
            results = load_results(result_file)
            pass_at_k = results["overall_metrics"]["pass_at_k"]
            
            print(f"   {result_file.name}: pass@k = {pass_at_k:.2%}")
            
            if pass_at_k > best_score:
                best_score = pass_at_k
                best_adapter = {
                    "file": str(result_file),
                    "results": results,
                    "score": pass_at_k
                }
                
        except Exception as e:
            print(f"   ⚠️ Error loading {result_file}: {e}")
    
    if best_adapter:
        print(f"🏆 Best adapter: {Path(best_adapter['file']).name} ({best_score:.2%})")
    
    return best_adapter

def compare_to_baseline(baseline_file: str, results_dir: str) -> Dict:
    """
    Compare adapter results to baseline and apply +15pp decision rule
    """
    
    print("📊 Loading baseline results...")
    baseline = load_results(baseline_file)
    baseline_pass_1 = baseline["overall_metrics"]["pass_at_1"]
    baseline_pass_k = baseline["overall_metrics"]["pass_at_k"]
    
    print(f"📊 Baseline performance:")
    print(f"   pass@1: {baseline_pass_1:.2%}")
    print(f"   pass@k: {baseline_pass_k:.2%}")
    
    # Find best adapter
    best_adapter = find_best_adapter(results_dir)
    
    if not best_adapter:
        return {"decision": "FAIL", "reason": "No valid adapter results found"}
    
    # Calculate deltas
    adapter_results = best_adapter["results"]
    adapter_pass_1 = adapter_results["overall_metrics"]["pass_at_1"]
    adapter_pass_k = adapter_results["overall_metrics"]["pass_at_k"]
    
    delta_pass_1 = adapter_pass_1 - baseline_pass_1
    delta_pass_k = adapter_pass_k - baseline_pass_k
    
    print(f"\n🎯 Best adapter performance:")
    print(f"   pass@1: {adapter_pass_1:.2%} (Δ{delta_pass_1:+.1%})")
    print(f"   pass@k: {adapter_pass_k:.2%} (Δ{delta_pass_k:+.1%})")
    
    # Per-family comparison
    family_deltas = {}
    for family in ['scaffold', 'repair', 'doc']:
        if family in baseline["family_metrics"] and family in adapter_results["family_metrics"]:
            baseline_fam = baseline["family_metrics"][family]["pass_at_k"]
            adapter_fam = adapter_results["family_metrics"][family]["pass_at_k"]
            delta_fam = adapter_fam - baseline_fam
            family_deltas[family] = {
                "baseline": baseline_fam,
                "adapter": adapter_fam,
                "delta": delta_fam
            }
            print(f"   {family}: {adapter_fam:.2%} (Δ{delta_fam:+.1%})")
    
    # DECISION RULE: +15pp on pass@k
    SUCCESS_THRESHOLD = 0.15  # 15 percentage points
    
    if delta_pass_k >= SUCCESS_THRESHOLD:
        decision = "PROCEED"
        reason = f"pass@k improvement ({delta_pass_k:.1%}) meets +15pp threshold"
    else:
        decision = "ADJUST"
        reason = f"pass@k improvement ({delta_pass_k:.1%}) below +15pp threshold"
    
    print(f"\n🚦 DECISION: {decision}")
    print(f"   Reason: {reason}")
    
    if decision == "ADJUST":
        # Provide specific recommendations
        weak_family = min(family_deltas.items(), key=lambda x: x[1]["delta"])[0]
        print(f"\n💡 Recommendations:")
        print(f"   1. Increase '{weak_family}' representation in training data")
        print(f"   2. If still flat, raise LoRA rank to 16")
        print(f"   3. DO NOT change learning rate first")
    
    return {
        "decision": decision,
        "reason": reason,
        "baseline_metrics": {
            "pass_at_1": baseline_pass_1,
            "pass_at_k": baseline_pass_k
        },
        "best_adapter_metrics": {
            "pass_at_1": adapter_pass_1,
            "pass_at_k": adapter_pass_k,
            "adapter_file": best_adapter["file"]
        },
        "deltas": {
            "pass_at_1": delta_pass_1,
            "pass_at_k": delta_pass_k
        },
        "family_deltas": family_deltas,
        "threshold_met": delta_pass_k >= SUCCESS_THRESHOLD
    }

def main():
    """Main comparison function"""
    parser = argparse.ArgumentParser(description="Compare adapter results to baseline")
    parser.add_argument("--baseline", required=True, help="Baseline results JSON")
    parser.add_argument("--results_dir", required=True, help="Directory with adapter results")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not Path(args.baseline).exists():
        raise FileNotFoundError(f"Baseline file not found: {args.baseline}")
    if not Path(args.results_dir).exists():
        raise FileNotFoundError(f"Results directory not found: {args.results_dir}")
    
    # Run comparison
    comparison = compare_to_baseline(args.baseline, args.results_dir)
    
    # Save comparison results
    output_file = Path(args.results_dir) / "comparison_results.json"
    with open(output_file, 'w') as f:
        json.dump(comparison, f, indent=2)
    
    print(f"\n💾 Detailed comparison saved to: {output_file}")

if __name__ == "__main__":
    main()