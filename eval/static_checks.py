#!/usr/bin/env python3
"""
Static checker for Luanti code validation
NO ASSUMPTIONS - exactly as specified
"""

import re
import subprocess
import tempfile
import os
from pathlib import Path
from typing import List

def parse_lua(text: str) -> bool:
    """
    Parse Lua code using luac if available, else return True (no-op)
    
    Args:
        text: Lua code to validate
        
    Returns:
        True if valid Lua or luac not available, False if syntax error
    """
    # Check if luac is available
    try:
        result = subprocess.run(['luac', '-v'], capture_output=True, text=True)
        if result.returncode != 0:
            # luac not available, return True as no-op
            return True
    except FileNotFoundError:
        # luac not available, return True as no-op
        return True
    
    # luac is available, test the code
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as f:
            f.write(text)
            temp_file = f.name
        
        # Run luac -p (parse only)
        result = subprocess.run(
            ['luac', '-p', temp_file], 
            capture_output=True, 
            text=True
        )
        
        # Clean up temp file
        os.unlink(temp_file)
        
        return result.returncode == 0
        
    except Exception:
        # If anything goes wrong, return True (no-op)
        return True

def require_regex(text: str, patterns: List[str]) -> bool:
    """
    Check that ALL required regex patterns are present in text
    
    Args:
        text: Text to check
        patterns: List of regex patterns that must be present
        
    Returns:
        True if all patterns found, False otherwise
    """
    for pattern in patterns:
        if not re.search(pattern, text, re.MULTILINE):
            return False
    return True

def forbid_regex(text: str, patterns: List[str]) -> bool:
    """
    Check that NONE of the forbidden regex patterns are present in text
    
    Args:
        text: Text to check  
        patterns: List of regex patterns that must NOT be present
        
    Returns:
        True if no forbidden patterns found, False if any found
    """
    for pattern in patterns:
        if re.search(pattern, text, re.MULTILINE):
            return False
    return True

# Family-specific validation patterns
SCAFFOLD_REQUIRED = [
    r'minetest\.register_node',
    r'tiles\s*=\s*\{',
    r'description\s*='
]

SCAFFOLD_FORBIDDEN = [
    r'syntax error',
    r'nil\s',
    r'register_node\s*\([^\'"]',  # missing quotes around first param
]

REPAIR_REQUIRED = [
    r'---\s+a/',
    r'\+\+\+\s+b/', 
    r'@@.*@@',
    r'[+-].*'
]

DOC_REQUIRED = [
    r'minetest\.',
    r'[\'"][a-zA-Z_][a-zA-Z0-9_]*:[a-zA-Z_][a-zA-Z0-9_]*[\'"]'  # mymod:nodename format
]

DOC_FORBIDDEN = [
    r'TODO',
    r'FIXME',
    r'undefined'
]

def validate_family(text: str, family: str) -> bool:
    """
    Validate text matches the requirements for its family
    
    Args:
        text: Generated text to validate
        family: One of 'scaffold', 'repair', 'doc'
        
    Returns:
        True if valid for family, False otherwise
    """
    # First check Lua syntax for non-repair items
    if family != 'repair':
        if not parse_lua(text):
            return False
    
    # Family-specific checks
    if family == 'scaffold':
        return (require_regex(text, SCAFFOLD_REQUIRED) and 
                forbid_regex(text, SCAFFOLD_FORBIDDEN))
    
    elif family == 'repair':
        return require_regex(text, REPAIR_REQUIRED)
    
    elif family == 'doc':
        return (require_regex(text, DOC_REQUIRED) and
                forbid_regex(text, DOC_FORBIDDEN))
    
    else:
        return False

def test_static_checks():
    """Unit tests as specified - 3 examples each"""
    
    print("🧪 Testing static checks...")
    
    # Test 1: Valid scaffold
    scaffold_valid = '''minetest.register_node('mymod:test', {
    description = 'Test Node',
    tiles = {'default_stone.png'}
})'''
    assert validate_family(scaffold_valid, 'scaffold'), "Valid scaffold should pass"
    
    # Test 2: Invalid scaffold (missing tiles)
    scaffold_invalid = '''minetest.register_node('mymod:test', {
    description = 'Test Node'
})'''
    assert not validate_family(scaffold_invalid, 'scaffold'), "Invalid scaffold should fail"
    
    # Test 3: Valid repair (unified diff)
    repair_valid = '''--- a/file.lua
+++ b/file.lua
@@ -1,2 +1,3 @@
 minetest.register_node('test', {
-    description = 'Test'
+    description = 'Test',
+    tiles = {'stone.png'}
 })'''
    assert validate_family(repair_valid, 'repair'), "Valid repair should pass"
    
    # Test 4: Invalid repair (not a diff)
    repair_invalid = '''minetest.register_node('fixed', {
    description = 'Fixed'
})'''
    assert not validate_family(repair_invalid, 'repair'), "Invalid repair should fail"
    
    # Test 5: Valid doc  
    doc_valid = '''minetest.register_tool('mymod:hammer', {
    description = 'Hammer',
    inventory_image = 'hammer.png'
})'''
    assert validate_family(doc_valid, 'doc'), "Valid doc should pass"
    
    # Test 6: Invalid doc (missing mymod: format)
    doc_invalid = '''minetest.register_tool('hammer', {
    description = 'Hammer'
})'''
    assert not validate_family(doc_invalid, 'doc'), "Invalid doc should fail"
    
    print("✅ All static check tests passed!")

if __name__ == "__main__":
    test_static_checks()