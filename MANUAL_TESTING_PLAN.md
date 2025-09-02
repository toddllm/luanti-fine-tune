# 🧪 Manual Testing Plan: Step-by-Step Validation

**Status**: Ready for execution with outstanding quantitative results  
**Best Config**: checkpoint-500 @ scale=1.0 (98.3% pass@1, **100% pass@5**)  
**Approach**: Qualitative validation while maintaining GPU availability for future evaluation

## 🎯 **Testing Strategy**

### **Phase 1: Static Validation (No GPU Required)**
Test code quality, syntax, and API correctness without model loading

### **Phase 2: Generation Testing (GPU Required)**  
Load best model and generate fresh examples across task categories

### **Phase 3: Behavioral Validation (Local/Optional)**
Test generated code in actual Luanti environment

## 📋 **Phase 1: Static Validation**

### **1.1 Review Existing Evaluation Outputs**
```bash
# Extract sample outputs from best performing evaluation
ssh tdeshane@toddllm 'cd ~/luanti_capability &&
python - <<PY
import json
with open("eval/results/local_checkpoint-500_scale_1.0.json") as f:
    data = json.load(f)

print("=== SAMPLE OUTPUTS FROM 100% PASS@5 EVALUATION ===")
for i, item in enumerate(data["items"][:5]):
    print(f"\\n--- Sample {i+1} ---")
    print(f"Prompt: {item[\"prompt\"][:80]}...")
    if item.get("gens"):
        print(f"Generated: {item[\"gens\"][0][:200]}...")
        print(f"Pass status: {item.get(\"passes\", [False])[0]}")
    print("-" * 50)
PY'
```

### **1.2 Syntax Validation**
```bash
# Create syntax checker for generated Lua code
ssh tdeshane@toddllm 'cd ~/luanti_capability &&
cat > scripts/validate_lua_syntax.py <<PY
import re, sys

def validate_lua_code(code):
    """Basic Lua syntax validation"""
    issues = []
    
    # Check balanced braces
    braces = {"(": ")", "{": "}", "[": "]"}
    stack = []
    for char in code:
        if char in braces:
            stack.append(braces[char])
        elif char in braces.values():
            if not stack or stack.pop() != char:
                issues.append("Unbalanced braces/parentheses")
                break
    if stack:
        issues.append("Unclosed braces/parentheses")
    
    # Check for common syntax errors
    if re.search(r"\\{\\s*,", code):
        issues.append("Empty table entry (starts with comma)")
    if re.search(r",\\s*}", code):
        issues.append("Trailing comma before closing brace")
    if re.search(r"=\\s*,", code):
        issues.append("Assignment to comma")
    
    # Check Minetest API usage
    if not re.search(r"minetest\\.(register_\\w+|\\w+)", code):
        issues.append("No minetest API calls found")
    
    # Check for proper quotes
    if re.search(r"minetest\\.register_\\w+\\s*\\(\\s*[^'\"']", code):
        issues.append("Missing quotes around node/item name")
    
    return len(issues) == 0, issues

if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else input("Enter Lua code: ")
    valid, issues = validate_lua_code(code)
    print(f"Valid: {valid}")
    if issues:
        for issue in issues:
            print(f"  ✗ {issue}")
    else:
        print("  ✓ No syntax issues detected")
PY

chmod +x scripts/validate_lua_syntax.py'
```

### **1.3 API Correctness Check**
```bash
# Create Minetest API validator
ssh tdeshane@toddllm 'cd ~/luanti_capability &&
cat > scripts/validate_minetest_api.py <<PY
import re, sys

def validate_minetest_api(code):
    """Validate Minetest API usage"""
    score = 0
    details = []
    
    # Check for proper registration call
    if re.search(r"minetest\\.register_(node|tool|craftitem|entity|craft)\\s*\\(", code):
        score += 25
        details.append("✓ Proper minetest.register_* call")
    else:
        details.append("✗ No valid minetest.register_* call")
    
    # Check for required properties
    props = {
        "description": r"description\\s*=",
        "tiles": r"tiles\\s*=", 
        "groups": r"groups\\s*=",
        "light_source": r"light_source\\s*=",
        "drop": r"drop\\s*="
    }
    
    found_props = []
    for prop, pattern in props.items():
        if re.search(pattern, code):
            found_props.append(prop)
    
    if len(found_props) >= 2:
        score += 25
        details.append(f"✓ Has {len(found_props)} properties: {found_props}")
    else:
        details.append(f"✗ Only {len(found_props)} properties found")
    
    # Check for proper table structure
    if re.search(r"\\{[^{}]*description\\s*=.*?\\}", code, re.DOTALL):
        score += 25
        details.append("✓ Proper table structure")
    else:
        details.append("✗ Invalid table structure")
    
    # Check for valid values
    if re.search(r"light_source\\s*=\\s*(\\d+)", code):
        match = re.search(r"light_source\\s*=\\s*(\\d+)", code)
        light_val = int(match.group(1))
        if 0 <= light_val <= 14:
            score += 25
            details.append(f"✓ Valid light_source value: {light_val}")
        else:
            details.append(f"✗ Invalid light_source value: {light_val} (should be 0-14)")
    
    return score, details

if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else input("Enter Minetest code: ")
    score, details = validate_minetest_api(code)
    print(f"API Score: {score}/100")
    for detail in details:
        print(f"  {detail}")
PY

chmod +x scripts/validate_minetest_api.py'
```

## 📋 **Phase 2: Generation Testing Plan**

### **2.1 Test Categories to Validate**

**A) Scaffold Tasks (Create New Code)**
```bash
# Test 1: Basic glowing node
"Create a Luanti node called 'glowing_crystal' that emits light level 12, uses texture 'crystal.png', and drops itself when dug."

# Test 2: Tool with uses  
"Create a Luanti tool called 'magic_pickaxe' with 100 uses that can dig cracky=3 nodes instantly."

# Test 3: Crafting recipe
"Create a crafting recipe for 'steel_sword' using 2 steel ingots vertically and 1 stick at the bottom."
```

**B) Repair Tasks (Fix Broken Code)**
```bash
# Test 4: Missing quotes
"Fix this broken code: minetest.register_node(mymod:stone, {description = 'Stone'})"

# Test 5: Missing properties
"Fix this node to make it drop itself: minetest.register_node('mymod:ore', {description = 'Ore', tiles = {'ore.png'}})"
```

**C) Refactor Tasks (Modify Existing)**
```bash
# Test 6: Change light level
"Modify this node to emit light level 14 instead of 8: minetest.register_node('mymod:lamp', {light_source = 8})"

# Test 7: Add groups
"Add cracky=2 to this node: minetest.register_node('mymod:stone', {description = 'Stone'})"
```

### **2.2 Generation Script Template**
```bash
# Safe generation script that works with GPU constraints
ssh tdeshane@toddllm 'cd ~/luanti_capability &&
cat > scripts/manual_generate.py <<PY
import sys
from unsloth import FastLanguageModel
from peft import PeftModel
import torch

def generate_luanti_code(prompt, adapter_path="adapters_best"):
    print(f"Loading model with adapter: {adapter_path}")
    
    # Use exact same loader settings that work in evaluation
    base = "unsloth/gpt-oss-20b-unsloth-bnb-4bit"
    model, tok = FastLanguageModel.from_pretrained(
        model_name=base,
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
        attn_implementation="eager",
        device_map="auto",
    )
    model = PeftModel.from_pretrained(model, adapter_path)
    FastLanguageModel.for_inference(model)
    
    # Format prompt like evaluation
    formatted_prompt = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{prompt}

### Response:
"""
    
    print("Generating code...")
    ids = tok([formatted_prompt], return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(
            **ids, 
            max_new_tokens=300,
            temperature=0.2,
            top_p=0.9,
            do_sample=True
        )
    
    result = tok.decode(out[0], skip_special_tokens=True)
    code = result.split("### Response:")[-1].strip()
    
    return code

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manual_generate.py \\"Your prompt here\\"")
        sys.exit(1)
    
    prompt = sys.argv[1]
    code = generate_luanti_code(prompt)
    
    print("=== GENERATED CODE ===")
    print(code)
    print("=== END ===")
PY

chmod +x scripts/manual_generate.py'
```

## 📋 **Phase 3: Execution Steps for Review**

### **Step 1: Environment Setup**
```bash
# Ensure GPU is clear and environment ready
ssh tdeshane@toddllm 'nvidia-smi | grep python || echo "GPU ready"'
ssh tdeshane@toddllm 'cd ~/luanti_capability && ls -la adapters_best'
```

### **Step 2: Generate Test Cases**  
```bash
# Test each category with our best model
ssh tdeshane@toddllm 'cd ~/luanti_capability && mkdir -p manual_tests && 
python scripts/manual_generate.py "Create a Luanti node called glowing_crystal that emits light level 12" > manual_tests/test1_scaffold.lua'
```

### **Step 3: Validate Outputs**
```bash
# Run static validation on generated code
ssh tdeshane@toddllm 'cd ~/luanti_capability &&
python scripts/validate_lua_syntax.py "$(cat manual_tests/test1_scaffold.lua)" &&
python scripts/validate_minetest_api.py "$(cat manual_tests/test1_scaffold.lua)"'
```

### **Step 4: Document Results**
```bash
# Create comprehensive manual test report
# Save outputs, validation results, and quality assessment
```

## 🛡️ **Safety & Constraints**

**✅ GPU Management:**
- Evaluation paused to free GPU memory
- Single model loading per test to avoid conflicts
- Clear cache between tests if needed

**✅ Test Isolation:**
- Each test is independent and repeatable  
- Results saved for review and documentation
- No impact on evaluation data or pipeline

**✅ Quality Focus:**
- Test the proven best configuration (100% pass@5)
- Focus on qualitative aspects not captured in pass@k
- Generate demo material for community integration

---

**🎯 This plan provides comprehensive manual validation of our outstanding quantitative results while maintaining the ability to resume evaluation when ready.**

**Ready for your review and step-by-step execution approval.**