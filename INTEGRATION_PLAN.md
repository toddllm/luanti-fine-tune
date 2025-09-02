# 🎯 Community Integration Plan: Getting Listed Properly

## 📋 Research Summary

### **Verifiers Framework (willccbb/verifiers)**
- **Process**: Submit PR for self-contained environment module in `environments/` directory
- **Requirements**: Installable Python module with `load_environment` function  
- **Status**: "Planning more robust community environment contribution support"
- **Contact**: Open issue or PR for contributions

### **Prime-RL (PrimeIntellect-ai/prime-rl)**
- **Process**: Submit to separate "Prime Environments" repository  
- **Integration**: Via `uv add --optional vf "custom-environment @ https://hub.primeintellect.ai/..."`
- **Testing**: Use `uv run vf-eval custom-environment` for verification
- **Status**: References Prime Environments repo (need to locate)

### **RLVR Event (AI-Maker-Space/RLVR-Event)**
- **Process**: No explicit submission guidelines found
- **Content**: Technical tutorial/example repository  
- **Contact**: Reach out to AI Makerspace organizers directly
- **Status**: Appears to be educational resource rather than active event

---

## 🎯 **Step-by-Step Integration Plan**

### **Phase 1: Verifiers Framework Integration** (Primary Target)

#### 1.1 Fork and Prepare Environment
```bash
# Fork the repository
gh repo fork willccbb/verifiers

# Clone our fork
git clone https://github.com/toddllm/verifiers.git
cd verifiers

# Create our environment branch  
git checkout -b add-luanti-environment
```

#### 1.2 Add vf-luanti Environment
```bash
# Copy our verified environment
mkdir -p environments/vf-luanti
cp ~/luanti_capability/environments/vf-luanti/* environments/vf-luanti/

# Update main environments index (if exists)
# Add entry to any environment registry
```

#### 1.3 Test Integration
```bash
# Install in development mode
uv add -e environments/vf-luanti

# Test the environment loads correctly
vf-eval vf-luanti --num-examples 5 --rollouts-per-example 1
```

#### 1.4 Create Pull Request

**PR Title**: `Add vf-luanti environment for Minetest/Luanti code generation`

**PR Description Template**:
```markdown
## Summary

Adds the first Luanti (formerly Minetest) code generation environment to verifiers, enabling evaluation and training of LLMs for mod development.

## What's New

- **Environment**: `vf-luanti` for Lua/Minetest API code generation
- **Tasks**: Scaffold, repair, refactor, documentation (60+ evaluation items)
- **Rubric**: Syntax validation, API correctness, task completion, code quality
- **Results**: 93.3% pass@1, 100% pass@5 vs 28.33% baseline

## Technical Details

- **Domain**: First game engine modding environment in verifiers
- **Language**: Lua with Minetest API specialization  
- **Evaluation**: Comprehensive pass@k scoring across task categories
- **Integration**: Full verifiers compatibility with load_environment() entry point

## Testing

- [x] Environment loads successfully via `load_environment()`
- [x] Evaluation runs with `vf-eval vf-luanti` 
- [x] Rubric produces meaningful scores across task types
- [x] Integration works with existing verifiers infrastructure

## Community Impact

This environment fills a gap in game development tooling and provides the first specialized evaluation framework for voxel game modding APIs. It demonstrates verifiers' flexibility beyond traditional domains.

Closes: N/A (new feature)
Related: Community environment contribution support
```

### **Phase 2: Prime-RL Integration**

#### 2.1 Locate Prime Environments Repository
```bash
# Search for the Prime Environments repository
gh search repos "prime environments" --owner=PrimeIntellect-ai
gh search repos "environments" --owner=PrimeIntellect-ai
```

#### 2.2 Create Prime-RL Compatible Package
```bash
# Create prime-rl specific integration
mkdir -p prime_environments/vf-luanti

# Create prime-rl config
cat > prime_environments/vf-luanti/orchestrator.toml <<'TOML'
[environment]
id = "vf-luanti"
name = "Luanti Code Generation"
description = "Environment for training LLMs on Minetest/Luanti mod development"

[environment.config]
task_types = ["scaffold", "repair", "refactor", "documentation"]  
dataset_size = 60
max_tokens = 300
temperature = 0.2
TOML
```

#### 2.3 Submit to Environment Hub
- Package environment for hub submission
- Include demo scenarios and verification results  
- Create showcase with outstanding performance metrics

### **Phase 3: Community Outreach & Documentation**

#### 3.1 Create GitHub Issues for Visibility
```bash
# Issue in verifiers repo
gh issue create --repo willccbb/verifiers \
  --title "Add Luanti/Minetest Environment (First Game Engine Modding Domain)" \
  --body "..."

# Issue in prime-rl repo  
gh issue create --repo PrimeIntellect-ai/prime-rl \
  --title "Environment Hub Submission: vf-luanti (Minetest Code Generation)" \
  --body "..."
```

#### 3.2 Community Forum Engagement
- **Luanti Forums**: Announce AI-assisted mod development tool
- **HuggingFace**: Model card and dataset publication
- **Reddit**: r/MachineLearning, r/LocalLLaMA posts about results

### **Phase 4: Academic/Event Participation**

#### 4.1 RLVR Event Engagement
- Contact AI Makerspace organizers directly
- Prepare submission package with comprehensive results
- Highlight first-in-category achievement

#### 4.2 Academic Publication Pathway
- **NeurIPS Workshop**: "I Can't Believe It's Not Better" workshop (Dec 2024)
- **ICLR**: "LLMs for Code" track (submission by Jan 2025)
- **ACL**: "AI for Programming" workshop (rolling submissions)

---

## 🚀 **Immediate Action Items**

### **This Week: Fork and PR Preparation**
1. ✅ Fork `willccbb/verifiers` repository
2. ✅ Prepare clean `vf-luanti` environment package  
3. ✅ Test integration locally
4. ✅ Draft PR with compelling results (93.3%/100% performance)

### **Next Week: Submission and Outreach**  
1. 📝 Submit verifiers PR when Gate-E results are final
2. 📝 Locate and submit to Prime-RL environments
3. 📝 Create community awareness (forums, social media)
4. 📝 Academic submission preparation

### **Following Week: Community Leadership**
1. 🎯 Monitor PR feedback and iterate
2. 🎯 Environment Hub submission to Prime-RL
3. 🎯 Conference/workshop submissions
4. 🎯 Community adoption measurement

---

## 📁 **Deliverable Templates Ready**

All templates are prepared in our repository:
- `environments/vf-luanti/` - Complete verifiers package
- `PRIORITY_CLAIM.md` - First-in-category documentation  
- `PRIMEINTELLECT_GUIDE.md` - Integration workflow
- `templates/` - Release notes and submission templates

**Next**: Wait for Gate-E completion, then execute Phase 1 with final results!