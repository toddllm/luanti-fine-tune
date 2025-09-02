import os, torch
from unsloth import FastLanguageModel
from transformers import BitsAndBytesConfig

# kill compilers / keep eager
os.environ["TORCHDYNAMO_DISABLE"]="1"
os.environ["TORCHINDUCTOR_DISABLE"]="1"
os.environ["PYTORCH_TRITON_DISABLE"]="1"
os.environ["CUDA_LAUNCH_BLOCKING"]="1"
os.environ.setdefault("HF_HUB_OFFLINE","1")
os.environ.setdefault("TRANSFORMERS_OFFLINE","1")
os.environ["XFORMERS_DISABLED"]="1"   # avoid a separate kernel path

# ---- compute in FP32 (Unsloth warns it will anyway) ----
DT = torch.float32
bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=DT,   # <<< align compute to FP32
    bnb_4bit_use_double_quant=True,
)

BASE = "unsloth/gpt-oss-20b-unsloth-bnb-4bit"

print("[A] from_pretrained(fp32 compute)…", flush=True)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=BASE,
    load_in_4bit=True,
    dtype=DT,                    # <<< request FP32 compute path
    local_files_only=True,
    quantization_config=bnb,
    max_seq_length=2048,
)

print("[A1] base dtype:", model.config.torch_dtype, flush=True)

print("[B] attach LoRA (attn-only, cast FP32)…", flush=True)
model = FastLanguageModel.get_peft_model(
    model,
    r=8, lora_alpha=16, lora_dropout=0.05,
    target_modules=["q_proj","k_proj","v_proj","o_proj"],
    bias="none",
    use_gradient_checkpointing=False,
    random_state=3407,
)

# ensure LoRA tensors are FP32 to match compute
for _, m in model.named_modules():
    if hasattr(m, "lora_A"):
        for k in m.lora_A.keys():
            m.lora_A[k].weight.data = m.lora_A[k].weight.data.to(DT)
            m.lora_B[k].weight.data = m.lora_B[k].weight.data.to(DT)

print("[C] tiny train step…", flush=True)
prompt = ("Below is an instruction that describes a task.\n\n"
          "### Instruction:\nCreate a simple Luanti node that emits light.\n\n"
          "### Response:\n")
tok = tokenizer(prompt, return_tensors="pt").to("cuda")
out = model(**tok, labels=tok["input_ids"])
print("loss:", float(out.loss))
out.loss.backward()
print("[D] backward OK", flush=True)