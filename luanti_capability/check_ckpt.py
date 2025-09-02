import sys, glob, json, os
from unsloth import FastLanguageModel
from peft import PeftModel
base="unsloth/gpt-oss-20b-unsloth-bnb-4bit"
for ckpt in sorted(glob.glob("outputs_luanti_safe/checkpoint-*")):
    try:
        m,t = FastLanguageModel.from_pretrained(model_name=base, load_in_4bit=True, dtype=None)
        PeftModel.from_pretrained(m, ckpt)
        print(json.dumps({"checkpoint": ckpt, "status":"ok"}))
    except Exception as e:
        print(json.dumps({"checkpoint": ckpt, "status":"fail","err":str(e)}))
