from unsloth import FastLanguageModel
from peft import PeftModel
import re

print("=== REPAIR TASK TEST ===")
print("Loading model...")

base = "unsloth/gpt-oss-20b-unsloth-bnb-4bit"
model, tok = FastLanguageModel.from_pretrained(
    model_name=base, max_seq_length=4096, dtype=None, load_in_4bit=True,
    attn_implementation="eager", device_map="auto"
)
model = PeftModel.from_pretrained(model, "outputs_luanti_safe/checkpoint-500")
FastLanguageModel.for_inference(model)

broken_code = "minetest.register_node(mymod:broken_stone, { tiles = {'default_stone.png'} })"
prompt = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
Fix only the errors in this broken Luanti code and return valid Lua:
{broken_code}

### Response:
"""

print(f"Broken code: {broken_code}")
print("What's wrong: Missing quotes around node name, missing description")
print()
print("Generating fix...")

ids = tok([prompt], return_tensors="pt").to(model.device)
out = model.generate(**ids, max_new_tokens=200, temperature=0.2, top_p=0.9)
result = tok.decode(out[0], skip_special_tokens=True)

response = result.split("### Response:")[-1].strip()
print("=== RAW RESPONSE ===")
print(response[:300])

# Save the result
with open("manual_smoke/test2_repair_raw.txt", "w") as f:
    f.write(response)

# Extract code
m = re.search(r"(minetest\.register_node\([^}]+\}\))", response, re.S)
if m:
    repair_code = m.group(1).strip()
    print()
    print("=== EXTRACTED REPAIR CODE ===")
    print(repair_code)
    
    with open("manual_smoke/test2_repair.lua", "w") as f:
        f.write(repair_code)
        
    print()
    print("✅ Saved repair test results")
else:
    print("❌ Could not extract code from response")