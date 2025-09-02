# scripts/promote_best.py
import json, sys, re, os, shutil, torch
from pathlib import Path
from peft import PeftModel
from unsloth import FastLanguageModel

ROOT = Path.home() / "luanti_capability"
BASE = "unsloth/gpt-oss-20b-unsloth-bnb-4bit"
ADIR = ROOT/"outputs_luanti_safe"
RDIR = ROOT/"eval/results"
OUT  = ROOT/"outputs_luanti_best"   # baked best adapter here

def best_result():
    best = None
    for f in RDIR.glob("*.json"):
        try:
            js = json.loads(f.read_text())
        except Exception:
            continue
        # expect {"overall_metrics":{"pass_at_5":...},"scale":...,"adapter_path":"..."}, ...}
        scale = js.get("scale")
        ckpt  = js.get("adapter_path")
        p5    = js.get("overall_metrics",{}).get("pass_at_5")
        if None in (scale, ckpt, p5): continue
        if (best is None) or (p5 > best["pass5"]):
            best = {"scale": float(scale), "ckpt": ckpt, "pass5": float(p5), "file": str(f)}
    if not best:
        raise SystemExit("No eval JSONs with scale/checkpoint found in eval/results.")
    return best

def bake_scale(peft_dir, scale, out_dir):
    model, tok = FastLanguageModel.from_pretrained(model_name=BASE, load_in_4bit=True, dtype=None, max_seq_length=2048)
    model = PeftModel.from_pretrained(model, peft_dir)
    dt = next(p for p in model.parameters() if p.is_floating_point()).dtype
    # scale LoRA B weights permanently
    n=0
    for _, m in model.named_modules():
        if hasattr(m, "lora_B"):
            for k in list(m.lora_B.keys()):
                with torch.no_grad():
                    m.lora_B[k].weight.data = (m.lora_B[k].weight.data * scale).to(dt)
                n += 1
    out_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(out_dir)
    (out_dir/"META.json").write_text(json.dumps({"scale": scale, "dtype": str(dt)}, indent=2))
    return n

if __name__ == "__main__":
    best = best_result()
    ckpt_dir = Path(best["ckpt"])
    print(f"[+] Best eval: pass@5={best['pass5']:.2f} scale={best['scale']} ckpt={best['ckpt']}")
    if not ckpt_dir.exists():
        raise SystemExit(f"Missing checkpoint dir: {ckpt_dir}")
    if OUT.exists():
        shutil.rmtree(OUT)
    n = bake_scale(ckpt_dir, best["scale"], OUT)
    print(f"[+] Baked {n} LoRA matrices into {OUT}")