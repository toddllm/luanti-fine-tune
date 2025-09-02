# 🚀 Luanti-Voyager Revival Plan

**Context**: Outstanding Luanti code generation results (96.7% pass@5) create perfect timing to revive luanti-voyager with modern verifiers/prime-rl integration.

## 🎯 **10-Day "Revive & Ship" Plan**

### **Day 0–1: Stabilize & Label**
- Create milestone: `v0.2 – Revival`
- Triage/label existing issues: `needs-repro`, `good first issue`, `blocked`, `docs`
- Add status labels: `revival:now`, `revival:queued`

### **Day 1–2: Dev UX & CI**
- Add pre-commit (ruff/black/isort), codespell
- GitHub Actions CI: `pytest -q` on Ubuntu + macOS (Python 3.11/3.12)
- Add `Makefile` targets: `make setup`, `make test`, `make run`, `make playground`

### **Day 2–3: Model Client (Luanti Code-Gen)**
Drop in thin client supporting:
- Local HF pipeline (text-gen)  
- Tuned GPT-OSS:20B + LoRA adapter endpoint (OpenAI-compatible)
- Small prompt library for scaffold/repair/refactor tasks

### **Day 3–4: Verifiers Shim**
- Add **vf-luanti** environment adapter (same spec as upstream PR)
- 10-item task pack for local smoke tests
- CLI: `python -m luanti_voyager.verifiers.run --env vf-luanti --model http://localhost:11434`

### **Day 4–5: PrimeIntellect Pack**
- Add 10–15 scenario JSONLs (pi_scenarios.jsonl style)
- `scripts/prime_run.sh` integration script

### **Day 5–6: Docs Refresh**
- Rewrite README "Quick Start" (Linux focus)
- Add "Do-This-Now" operator guide
- Link verifiers/prime guides, add architecture diagram
- Add **CONTRIBUTING.md** and **SECURITY.md**

### **Day 6–7: Examples**
- `examples/01_scaffold_node.py` (generate + apply + reload world)
- `examples/02_repair_mod.py` (fix broken code snippet)  
- `examples/03_multi_agent_build.py` (voyager-style teamwork)

### **Day 7–8: Mod/World Smoke Tests**
- `tests/behaviors/test_scaffold_node.py` (LLM mocked)
- `tests/integration/test_apply_mod.py` (file-based command bridge)
- Make "headless" world script for CI

### **Day 9–10: Release & Outreach**
- Tag `v0.2.0`, publish release notes
- Update issues with "help wanted"
- Cross-link to verifiers PR #288 and prime-environments PR #94
- Add comparison table with other Minetest AI projects

## 🔧 **Ready-to-Drop Code Stubs**

### **Makefile** (targets)
```make
.PHONY: setup test run lint fmt playground
setup:
\tpython -m venv .venv && . .venv/bin/activate && pip install -U pip
\tpip install -e ".[dev]"
\tpre-commit install
test:
\tpytest -q
lint:
\truff check .
fmt:
\truff check --fix .; black .; isort .
run:
\tpython -m luanti_voyager --name VoyagerBot
playground:
\tpython -m luanti_voyager.playground --port 8080
```

### **LuantiCodeGenClient** (model integration)
```python
from __future__ import annotations
import os, json, requests
from typing import List, Dict, Optional

DEFAULT_SYSTEM = (
  "You are a Luanti (Minetest) modding assistant. "
  "Return only Lua code blocks unless asked otherwise."
)

class LuantiCodeGenClient:
    def __init__(self, endpoint: str | None = None, api_key: Optional[str] = None):
        self.endpoint = endpoint or os.getenv("LLM_ENDPOINT", "http://localhost:8000/v1")
        self.api_key = api_key or os.getenv("LLM_API_KEY")

    def generate(self, prompt: str, n: int = 1, temperature: float = 0.2, max_tokens: int = 300) -> List[str]:
        body = {
            "model": os.getenv("LLM_MODEL", "tuned-luanti-20b"),
            "messages": [{"role": "system", "content": DEFAULT_SYSTEM},
                         {"role": "user", "content": prompt}],
            "n": n, "temperature": temperature, "max_tokens": max_tokens,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        r = requests.post(f"{self.endpoint}/chat/completions", json=body, headers=headers, timeout=120)
        r.raise_for_status()
        return [c["message"]["content"] for c in r.json()["choices"]]

    @staticmethod
    def prompt_scaffold_node(name: str, light: int = 14) -> str:
        return (f'Create a Luanti node that emits light_source={light} and drops itself when dug.\\n'
                f'Use minetest.register_node("{name}", {{ ... }}) with valid fields.\\n'
                f'Return only Lua.')
```

### **Verifiers Adapter** (vf-luanti integration)
```python
from dataclasses import dataclass
from typing import Dict, Any
from .rubrics import score_lua_syntax, score_api_usage
from ..models.luanti_codegen_client import LuantiCodeGenClient

@dataclass
class VFRequest:
    instruction: str
    category: str  # scaffold|repair|refactor|doc
    input_code: str | None = None

class VFLuantiEnv:
    def __init__(self, model: LuantiCodeGenClient | None = None):
        self.model = model or LuantiCodeGenClient()

    def step(self, req: VFRequest) -> Dict[str, Any]:
        prompt = self._build_prompt(req)
        completions = self.model.generate(prompt, n=5, temperature=0.2, max_tokens=300)
        best = self._pick_best(req, completions)
        scores = {
            "syntax": score_lua_syntax(best),
            "api": score_api_usage(best),
        }
        return {"completion": best, "scores": scores}
```

### **GitHub Actions CI** (basic)
```yaml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: ${{ matrix.python }} }
      - run: pip install -U pip
      - run: pip install -e ".[dev]"
      - run: pytest -q
```

## 🔗 **Integration Points**

### **Connection to Current Work**
- **Model**: Use our outstanding fine-tuned GPT-OSS 20B (96.7% pass@5)
- **Evaluation**: Leverage vf-luanti environment (verifiers PR #288)
- **Scenarios**: Integrate pi_scenarios.jsonl (prime-environments PR #94)
- **Automation**: Adapt our proven evaluation pipeline

### **Voyager Enhancement**
- **AI-Assisted Development**: Transform from manual to AI-driven mod creation
- **Real-world Testing**: Apply generated code in actual Luanti worlds
- **Multi-agent Collaboration**: Teams of agents working on complex mods
- **Interactive Learning**: Learn from success/failure in live environments

### **Community Value**
- **Developer Tool**: Practical AI assistance for mod creators
- **Educational Platform**: Learn Luanti development with AI guidance  
- **Research Platform**: Study AI-assisted game development workflows
- **Integration Example**: Template for other game engine AI tools

## 📋 **Immediate Actions**

### **This Week: Foundation**
1. **Fork luanti-voyager** from existing repository
2. **Create revival branch** with basic CI and dev UX
3. **Integrate model client** using our outstanding fine-tuned results
4. **Add verifiers adapter** leveraging approved environment

### **Next Week: Integration**
1. **Connect evaluation pipeline** from current outstanding work
2. **Add scenario packs** for practical demonstration
3. **Create automation scripts** following our proven patterns
4. **Update documentation** with modern integration guides

### **Following Week: Community**
1. **Cross-reference PRs** in verifiers/prime-environments
2. **Create demo videos** showing AI-assisted mod development
3. **Engage Luanti community** with practical tooling announcement
4. **Academic submissions** highlighting complete pipeline

## 🏆 **Success Metrics**

### **Technical**
- Working AI-assisted mod generation in live Luanti worlds
- Integration with verifiers/prime-rl ecosystems  
- Demonstrated improvement over manual development workflows
- Reproducible automation and comprehensive documentation

### **Community**
- Active usage by Luanti mod developers
- Integration examples for other game engines
- Academic citations and research collaborations
- Ecosystem leadership in game development AI tooling

## 🔄 **Timeline Synergy**

**Perfect Timing:**
- **Our evaluation**: Delivering outstanding 96.7% pass@5 results
- **Community PRs**: Active in major frameworks (verifiers, prime-environments)
- **Market position**: Established first-mover advantage
- **Documentation**: Complete guides and automation ready

The luanti-voyager revival can leverage all our current momentum and outstanding results to create the definitive AI-assisted game development platform.

---

**This revival plan transforms our outstanding evaluation results into practical tooling that will drive community adoption and ecosystem leadership in game development AI.**