import json, os, re, time
from pathlib import Path
from unsloth import FastLanguageModel  
from peft import PeftModel

OUT = Path("manual_smoke"); OUT.mkdir(exist_ok=True)

def load_model(adapters="outputs_luanti_safe/checkpoint-500"):
    print(f"Loading model with adapter: {adapters}")
    base = "unsloth/gpt-oss-20b-unsloth-bnb-4bit"
    model, tok = FastLanguageModel.from_pretrained(
        model_name=base,
        max_seq_length=4096,
        dtype=None,
        load_in_4bit=True,
        attn_implementation="eager",
        device_map="auto",
    )
    model = PeftModel.from_pretrained(model, adapters)
    FastLanguageModel.for_inference(model)
    print("✅ Model loaded successfully")
    return model, tok

def generate(model, tok, prompt, max_new_tokens=300, temperature=0.2, top_p=0.9):
    ids = tok([prompt], return_tensors="pt").to(model.device)
    out = model.generate(**ids, max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p)
    text = tok.decode(out[0], skip_special_tokens=True)
    return text

def extract_lua_block(text):
    # Prefer fenced or first register_node block
    m = re.search(r"```lua(.*?)```", text, re.S|re.I)
    if m: return m.group(1).strip()
    m = re.search(r"(minetest\.register_[^`]+?\})", text, re.S)
    return m.group(1).strip() if m else text.strip()

print("=== LIVE GENERATION TEST 1: SCAFFOLD TASK ===")
model, tok = load_model("outputs_luanti_safe/checkpoint-500")

prompt1 = ("Create a Luanti node 'mymod:beacon' that emits light_source=14, "
          "uses tiles={'default_torch.png'}, drops itself when dug, and belongs to groups cracky=1, level=2. "
          "Return only valid Lua.")

print(f"Prompt: {prompt1}")
print("\nGenerating...")
result1 = generate(model, tok, prompt1)

print("\n=== RAW OUTPUT ===")
print(result1[:400])
print("..." if len(result1) > 400 else "")

lua1 = extract_lua_block(result1)
(OUT / "test1_scaffold.lua").write_text(lua1)

print("\n=== EXTRACTED LUA CODE ===")
print(lua1)
print("\n" + "="*60)

# Save both versions
(OUT / "test1_scaffold_raw.txt").write_text(result1)

print(f"✅ Saved to manual_smoke/test1_scaffold.lua and test1_scaffold_raw.txt")