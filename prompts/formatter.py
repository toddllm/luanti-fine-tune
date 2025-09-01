#!/usr/bin/env python3
"""
IIR Template Formatter - NO DEVIATIONS
Implements exact conditional logic for Input block
"""

import re
from pathlib import Path

def load_template() -> str:
    """Load the IIR template"""
    template_path = Path(__file__).parent / "iir_template.txt"
    with open(template_path, 'r') as f:
        return f.read()

def format_prompt(instruction: str, input_text: str = "", output: str = "") -> str:
    """
    Format prompt using exact IIR template logic
    
    Args:
        instruction: The instruction text
        input_text: Input text (empty string if no input)
        output: Response text (for training data)
        
    Returns:
        Formatted prompt string
    """
    template = load_template()
    
    # Handle conditional INPUT_BLOCK
    if input_text and input_text.strip():
        # Input exists - include the input section
        template = template.replace("{{INPUT_BLOCK}}", ", some of which is provided as input")
        template = template.replace("{{IF_INPUT}}", "").replace("{{END_IF_INPUT}}", "")
    else:
        # No input - remove input section entirely
        template = template.replace("{{INPUT_BLOCK}}", "")
        # Remove the entire input section
        template = re.sub(r'{{IF_INPUT}}.*?{{END_IF_INPUT}}', '', template, flags=re.DOTALL)
    
    # Format with values
    formatted = template.format(
        instruction=instruction,
        input=input_text,
        output=output
    )
    
    # Strip trailing spaces but preserve code formatting
    lines = formatted.split('\n')
    cleaned_lines = [line.rstrip() for line in lines]
    
    return '\n'.join(cleaned_lines)

def format_for_training(item: dict) -> str:
    """Format a training item with response"""
    return format_prompt(
        instruction=item["instruction"],
        input_text=item.get("input", ""),
        output=item["output"]
    )

def format_for_inference(instruction: str, input_text: str = "") -> str:
    """Format for inference (no output)"""
    formatted = format_prompt(instruction, input_text, "")
    # Remove the trailing "### Response:\n" for inference
    if formatted.endswith("### Response:\n"):
        formatted = formatted[:-15] + "### Response:"
    return formatted

# Unit tests to verify identical formatting between train and eval
def test_formatter():
    """Test cases to ensure train/eval formatting is identical"""
    
    # Test case 1: No input
    item1 = {
        "instruction": "Register a simple node in Luanti",
        "input": "",
        "output": "minetest.register_node('mymod:simple', {description = 'Simple Node'})"
    }
    
    train_format = format_for_training(item1)
    infer_format = format_for_inference(item1["instruction"], item1["input"])
    
    # Check they match up to the response
    assert infer_format + item1["output"] == train_format.rstrip()
    
    # Test case 2: With input
    item2 = {
        "instruction": "Fix this Lua code",
        "input": "minetest.register_node('broken', {tiles = })",
        "output": "minetest.register_node('fixed', {tiles = {'default_stone.png'}})"
    }
    
    train_format2 = format_for_training(item2)
    infer_format2 = format_for_inference(item2["instruction"], item2["input"])
    
    assert infer_format2 + item2["output"] == train_format2.rstrip()
    
    print("✅ Formatter tests passed - train/eval formatting is identical")

if __name__ == "__main__":
    test_formatter()