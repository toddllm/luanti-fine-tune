#!/usr/bin/env python3
"""
Unified diff patch applier - NO ASSUMPTIONS
Applies unified diff patches to strings exactly as specified
"""

import re
from typing import Union
from unidiff import PatchSet

def apply_patch(base_text: str, diff_text: str) -> Union[str, str]:
    """
    Apply a unified diff to a base string
    
    Args:
        base_text: Original text to patch
        diff_text: Unified diff format patch
        
    Returns:
        Patched text if successful, or error message starting with "ERROR:"
    """
    try:
        # Parse the unified diff
        patch = PatchSet(diff_text)
        
        if len(patch) == 0:
            return "ERROR: No patches found in diff"
        
        if len(patch) > 1:
            return "ERROR: Multiple files in diff not supported"
        
        patched_file = patch[0]
        
        # Split base text into lines
        lines = base_text.split('\n')
        
        # Apply each hunk
        for hunk in patched_file:
            # Find the starting line (1-indexed in diff, 0-indexed in list)
            start_line = hunk.source_start - 1
            
            if start_line < 0 or start_line >= len(lines):
                return f"ERROR: Hunk start line {hunk.source_start} out of range"
            
            # Collect changes
            new_lines = []
            old_line_idx = start_line
            
            for line in hunk:
                if line.line_type == ' ':  # Context line
                    new_lines.append(line.value.rstrip('\n'))
                    old_line_idx += 1
                elif line.line_type == '-':  # Removed line
                    old_line_idx += 1
                elif line.line_type == '+':  # Added line
                    new_lines.append(line.value.rstrip('\n'))
                    
            # Replace the lines
            end_line = start_line + hunk.source_length
            lines[start_line:end_line] = new_lines
        
        return '\n'.join(lines)
        
    except Exception as e:
        return f"ERROR: {str(e)}"

def test_apply_patch():
    """Unit tests - 3 examples as specified"""
    
    print("🧪 Testing patch applier...")
    
    # Test 1: Simple addition
    base1 = '''minetest.register_node('mymod:test', {
    description = 'Test Node'
})'''
    
    diff1 = '''--- a/file.lua
+++ b/file.lua
@@ -1,3 +1,4 @@
 minetest.register_node('mymod:test', {
-    description = 'Test Node'
+    description = 'Test Node',
+    tiles = {'stone.png'}
 })'''
    
    result1 = apply_patch(base1, diff1)
    assert not result1.startswith("ERROR:"), f"Test 1 failed: {result1}"
    assert "tiles = {'stone.png'}" in result1, "Test 1: tiles not added"
    
    # Test 2: Syntax fix
    base2 = '''minetest.register_tool('mymod:pick' {
    description = 'Pickaxe'
})'''
    
    diff2 = '''--- a/file.lua
+++ b/file.lua
@@ -1,3 +1,3 @@
-minetest.register_tool('mymod:pick' {
+minetest.register_tool('mymod:pick', {
     description = 'Pickaxe'
 })'''
    
    result2 = apply_patch(base2, diff2)
    assert not result2.startswith("ERROR:"), f"Test 2 failed: {result2}"
    assert "'mymod:pick', {" in result2, "Test 2: comma not added"
    
    # Test 3: Invalid diff should return error
    invalid_diff = '''not a real diff'''
    result3 = apply_patch("some text", invalid_diff)
    assert result3.startswith("ERROR:"), "Test 3: invalid diff should return error"
    
    print("✅ All patch applier tests passed!")

if __name__ == "__main__":
    test_apply_patch()