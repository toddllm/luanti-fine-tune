"""
Luanti Code Generation Environment for Verifiers

This environment evaluates Luanti (Minetest) code generation capabilities
across scaffold, repair, refactor, and documentation tasks.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from verifiers import SingleTurnEnv, Rubric


@dataclass
class LuantiTask:
    """Single Luanti coding task"""
    id: str
    prompt: str
    expected_patterns: List[str] = None
    forbidden_patterns: List[str] = None
    task_type: str = "scaffold"  # scaffold, repair, refactor, documentation


class LuantiRubric(Rubric):
    """Rubric for evaluating Luanti code generations"""
    
    def __init__(self):
        super().__init__()
        
    def evaluate(self, task: LuantiTask, response: str) -> Dict[str, Any]:
        """Evaluate a Luanti code generation response"""
        score = 0.0
        details = {}
        
        # Extract just the code part (remove prompt echo)
        code = self._extract_code(response)
        
        # 1. Syntax validation (25 points)
        syntax_score, syntax_details = self._check_syntax(code)
        score += syntax_score * 0.25
        details["syntax"] = syntax_details
        
        # 2. API correctness (35 points)  
        api_score, api_details = self._check_api_usage(code, task)
        score += api_score * 0.35
        details["api_usage"] = api_details
        
        # 3. Task completion (25 points)
        task_score, task_details = self._check_task_completion(code, task)
        score += task_score * 0.25
        details["task_completion"] = task_details
        
        # 4. Code quality (15 points)
        quality_score, quality_details = self._check_code_quality(code)
        score += quality_score * 0.15
        details["code_quality"] = quality_details
        
        return {
            "score": min(1.0, max(0.0, score)),
            "details": details,
            "extracted_code": code
        }
    
    def _extract_code(self, response: str) -> str:
        """Extract Lua code from response"""
        if "### Response:" in response:
            response = response.split("### Response:")[-1]
        
        # Look for code blocks or minetest patterns
        lua_patterns = [
            r'```(?:lua)?\n(.*?)```',
            r'minetest\.register_\w+\([^}]+}\)',
            r'function\s+\w+.*?end'
        ]
        
        for pattern in lua_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        return response.strip()
    
    def _check_syntax(self, code: str) -> tuple[float, dict]:
        """Check basic Lua/Luanti syntax"""
        details = {"valid_lua": False, "balanced_braces": False, "no_syntax_errors": False}
        score = 0.0
        
        # Basic Lua patterns
        if re.search(r'minetest\.(register_\w+|\w+)', code):
            details["valid_lua"] = True
            score += 0.4
        
        # Balanced braces/parentheses
        if self._check_balanced_braces(code):
            details["balanced_braces"] = True
            score += 0.3
        
        # No obvious syntax errors
        common_errors = [r'\{\s*,', r',\s*}', r'=\s*,', r',,']
        if not any(re.search(err, code) for err in common_errors):
            details["no_syntax_errors"] = True
            score += 0.3
            
        return score, details
    
    def _check_api_usage(self, code: str, task: LuantiTask) -> tuple[float, dict]:
        """Check correct Minetest API usage"""
        details = {"correct_register_call": False, "valid_properties": False, "proper_structure": False}
        score = 0.0
        
        # Correct registration call
        if re.search(r'minetest\.register_(node|tool|craftitem|entity|craft)\s*\(', code):
            details["correct_register_call"] = True
            score += 0.4
        
        # Valid properties (check for common ones)
        valid_props = ["description", "tiles", "groups", "light_source", "drop", "sounds", "paramtype"]
        found_props = sum(1 for prop in valid_props if prop in code)
        if found_props >= 2:
            details["valid_properties"] = True
            score += 0.4
        
        # Proper table structure
        if re.search(r'\{[^{}]*description\s*=.*?\}', code, re.DOTALL):
            details["proper_structure"] = True
            score += 0.2
            
        return score, details
    
    def _check_task_completion(self, code: str, task: LuantiTask) -> tuple[float, dict]:
        """Check if the task was completed correctly"""
        details = {"addresses_prompt": False, "includes_required_elements": False}
        score = 0.0
        
        # Check expected patterns if provided
        if task.expected_patterns:
            matches = sum(1 for pattern in task.expected_patterns if re.search(pattern, code, re.IGNORECASE))
            if matches > 0:
                details["addresses_prompt"] = True
                score += 0.6
                
        # Check for forbidden patterns  
        if task.forbidden_patterns:
            violations = sum(1 for pattern in task.forbidden_patterns if re.search(pattern, code, re.IGNORECASE))
            if violations == 0:
                details["includes_required_elements"] = True
                score += 0.4
        else:
            details["includes_required_elements"] = True
            score += 0.4
            
        return score, details
    
    def _check_code_quality(self, code: str) -> tuple[float, dict]:
        """Check general code quality"""
        details = {"readable": False, "consistent_style": False, "appropriate_length": False}
        score = 0.0
        
        # Readable (has proper spacing, not too condensed)
        if len(code.split('\n')) > 1 and '=' in code:
            details["readable"] = True
            score += 0.4
            
        # Consistent style (proper indentation hints)
        if '    ' in code or '\t' in code:  # Some indentation present
            details["consistent_style"] = True
            score += 0.3
            
        # Appropriate length (not too short, not too verbose)
        if 20 <= len(code) <= 1000:
            details["appropriate_length"] = True
            score += 0.3
            
        return score, details
    
    def _check_balanced_braces(self, code: str) -> bool:
        """Check if braces/parentheses are balanced"""
        stack = []
        pairs = {'(': ')', '{': '}', '[': ']'}
        
        for char in code:
            if char in pairs:
                stack.append(pairs[char])
            elif char in pairs.values():
                if not stack or stack.pop() != char:
                    return False
        
        return len(stack) == 0


class LuantiEnvironment(SingleTurnEnv):
    """Luanti code generation environment"""
    
    def __init__(self, dataset_path: Optional[str] = None):
        self.dataset_path = dataset_path or "data/eval/luanti_eval.jsonl"
        self.rubric = LuantiRubric()
        self._load_dataset()
    
    def _load_dataset(self):
        """Load the Luanti evaluation dataset"""
        self.tasks = []
        
        dataset_file = Path(self.dataset_path)
        if not dataset_file.exists():
            # Create a small sample dataset for testing
            self.tasks = self._create_sample_tasks()
            return
        
        with open(dataset_file, 'r') as f:
            for i, line in enumerate(f):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    task = LuantiTask(
                        id=f"item_{i}",
                        prompt=data.get("prompt", data.get("instruction", "")),
                        expected_patterns=self._extract_expected_patterns(data),
                        task_type=self._classify_task(data.get("prompt", data.get("instruction", "")))
                    )
                    self.tasks.append(task)
                except json.JSONDecodeError:
                    continue
    
    def _create_sample_tasks(self) -> List[LuantiTask]:
        """Create sample tasks for testing"""
        return [
            LuantiTask(
                id="sample_node",
                prompt="Create a Luanti node that emits light level 10 and drops itself when dug.",
                expected_patterns=[r"light_source\s*=\s*10", "minetest\.register_node"],
                task_type="scaffold"
            ),
            LuantiTask(
                id="sample_repair", 
                prompt="Fix this broken node code: minetest.register_node('test', {description = 'Test'})",
                expected_patterns=[r"tiles\s*=", r"groups\s*="],
                task_type="repair"
            )
        ]
    
    def _extract_expected_patterns(self, data: dict) -> List[str]:
        """Extract expected patterns from dataset item"""
        patterns = []
        
        # Check for explicit validation fields
        if "any_of" in data:
            patterns.extend(data["any_of"])
        if "must_contain" in data:
            patterns.extend(data["must_contain"])
            
        # Infer from prompt
        prompt = data.get("prompt", data.get("instruction", "")).lower()
        if "light" in prompt:
            patterns.append("light_source")
        if "node" in prompt:
            patterns.append(r"minetest\.register_node")
        if "tool" in prompt:
            patterns.append(r"minetest\.register_tool")
        if "craft" in prompt:
            patterns.append(r"minetest\.register_craft")
            
        return patterns
    
    def _classify_task(self, prompt: str) -> str:
        """Classify the task type based on prompt"""
        prompt_lower = prompt.lower()
        if "fix" in prompt_lower or "repair" in prompt_lower or "broken" in prompt_lower:
            return "repair"
        elif "modify" in prompt_lower or "change" in prompt_lower or "update" in prompt_lower:
            return "refactor"  
        elif "documentation" in prompt_lower or "explain" in prompt_lower:
            return "documentation"
        else:
            return "scaffold"
    
    def get_tasks(self) -> List[LuantiTask]:
        """Get all tasks"""
        return self.tasks
    
    def evaluate_response(self, task: LuantiTask, response: str) -> Dict[str, Any]:
        """Evaluate a response to a task"""
        return self.rubric.evaluate(task, response)


def load_environment() -> LuantiEnvironment:
    """Entry point for verifiers framework"""
    return LuantiEnvironment()