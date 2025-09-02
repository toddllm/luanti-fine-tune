import torch
from unsloth import FastLanguageModel  # must be first to let Unsloth patch
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../eval'))
from loader_gateb import load_gateb_model

print("[A] load_gateb_model()", flush=True)
model, tokenizer = load_gateb_model()
dtype = next(p for p in model.parameters() if p.is_floating_point()).dtype
print(f"[A1] dtype: {dtype}", flush=True)

print("[B] attach LoRA (attn-only)", flush=True)
model = FastLanguageModel.get_peft_model(
    model, r=8, lora_alpha=16, lora_dropout=0.05,
    target_modules=["q_proj","k_proj","v_proj","o_proj"],
    bias="none", use_gradient_checkpointing=False, random_state=3407,
)
for _, m in model.named_modules():
    if hasattr(m, "lora_A"):
        for k in m.lora_A.keys():
            m.lora_A[k].weight.data = m.lora_A[k].weight.data.to(dtype)
            m.lora_B[k].weight.data = m.lora_B[k].weight.data.to(dtype)
print("[B1] LoRA cast ->", dtype, flush=True)

print("[C] fwd/bwd", flush=True)
tok = tokenizer("### Instruction:\nCreate a Luanti node that emits light.\n\n### Response:\n",
                return_tensors="pt").to("cuda")
out = model(**tok, labels=tok["input_ids"]); print("loss:", float(out.loss))
out.loss.backward(); print("[D] backward OK", flush=True)