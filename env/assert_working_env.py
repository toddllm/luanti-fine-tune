#!/usr/bin/env python3
"""
Working Environment Verifier - Checks exact versions that work
Aborts early with clear message if anything drifts
"""

import sys
import importlib

def check_version(module_name, expected_version=None, check_attr=True):
    """Check if module exists and optionally version"""
    try:
        mod = importlib.import_module(module_name)
        if check_attr and hasattr(mod, '__version__'):
            version = mod.__version__
            print(f"✅ {module_name}: {version}")
            if expected_version and version != expected_version:
                print(f"⚠️  Expected {expected_version}, got {version}")
                return False
        else:
            print(f"✅ {module_name}: imported successfully")
        return True
    except ImportError as e:
        print(f"❌ {module_name}: MISSING ({e})")
        return False

def main():
    """Verify working environment versions"""
    print("🔍 Verifying Working Environment (gptoss)")
    print("=" * 50)
    
    # Critical versions that work
    checks = [
        ("torch", "2.5.0+cu124"),
        ("unsloth", "2025.8.7"), 
        ("bitsandbytes", "0.47.0"),
        ("transformers", None),  # 4.56.0.dev0 - variable
        ("xformers", "0.0.28.post2"),
        ("peft", None),
        ("trl", None),
        ("unidiff", None),
    ]
    
    all_good = True
    
    for module, expected in checks:
        if not check_version(module, expected):
            all_good = False
    
    # Torch-specific checks
    try:
        import torch
        print(f"✅ CUDA available: {torch.cuda.is_available()}")
        print(f"✅ CUDA version: {torch.version.cuda}")
        print(f"✅ GPU count: {torch.cuda.device_count()}")
        if torch.cuda.is_available():
            print(f"✅ GPU name: {torch.cuda.get_device_name(0)}")
    except Exception as e:
        print(f"❌ Torch CUDA check failed: {e}")
        all_good = False
    
    # Test critical imports
    try:
        from unsloth import FastLanguageModel
        print("✅ Unsloth FastLanguageModel import OK")
    except Exception as e:
        print(f"❌ Unsloth import failed: {e}")
        all_good = False
    
    try:
        import bitsandbytes as bnb
        bnb.nn.Linear4bit(10, 10)
        print("✅ BitsAndBytes 4bit OK")
    except Exception as e:
        print(f"❌ BitsAndBytes 4bit failed: {e}")
        all_good = False
    
    print("=" * 50)
    if all_good:
        print("🎉 ENVIRONMENT VERIFIED - Ready for GPT-OSS:20B fine-tuning!")
        return 0
    else:
        print("🚨 ENVIRONMENT ISSUES DETECTED")
        print("Use the working 'gptoss' environment instead")
        return 1

if __name__ == "__main__":
    sys.exit(main())