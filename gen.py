# gen.py
from unsloth import FastLanguageModel
from peft import PeftModel
import torch, sys

BASE="unsloth/gpt-oss-20b-unsloth-bnb-4bit"
PEFT="outputs_luanti_best"
prompt = sys.argv[1] if len(sys.argv)>1 else "Create a Luanti node that emits light level 14 and drops itself when dug."

model, tok = FastLanguageModel.from_pretrained(model_name=BASE, load_in_4bit=True, dtype=None, max_seq_length=2048)
model = PeftModel.from_pretrained(model, PEFT)
FastLanguageModel.for_inference(model)

x = tok(f"### Instruction:\n{prompt}\n\n### Response:\n", return_tensors="pt").to("cuda")
y = model.generate(**x, max_new_tokens=220, temperature=0.2, top_p=0.9)
print(tok.decode(y[0], skip_special_tokens=True).split("### Response:")[-1].strip())