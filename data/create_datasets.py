#!/usr/bin/env python3
"""
Create minimal eval (60) and train (200-1k) datasets from Luanti collection
Uses the collected ContentDB data to generate realistic Luanti coding tasks
"""

import json
import random
from pathlib import Path
from typing import List, Dict

class LuantiDatasetBuilder:
    def __init__(self, luanti_data_path: str):
        """
        Initialize with path to collected Luanti data
        
        Args:
            luanti_data_path: Path to luanti_github_links.json
        """
        self.data_path = Path(luanti_data_path)
        self.packages = self.load_luanti_data()
        
    def load_luanti_data(self) -> List[Dict]:
        """Load the collected Luanti package data"""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Luanti data not found at {self.data_path}")
            
        with open(self.data_path, 'r') as f:
            return json.load(f)
    
    def create_scaffold_items(self, count: int) -> List[Dict]:
        """Create scaffold (node registration) items"""
        items = []
        
        scaffold_templates = [
            {
                "instruction": "Register a basic node called '{name}' with description '{desc}'",
                "input": "",
                "output": "minetest.register_node('{node_name}', {{\n    description = '{description}',\n    tiles = {{'default_stone.png'}}\n}})"
            },
            {
                "instruction": "Create a light-emitting node '{name}' with light level {light}",
                "input": "",
                "output": "minetest.register_node('{node_name}', {{\n    description = '{description}',\n    tiles = {{'default_torch.png'}},\n    light_source = {light_level}\n}})"
            },
            {
                "instruction": "Register a tool called '{name}' with specified capabilities",
                "input": "",
                "output": "minetest.register_tool('{tool_name}', {{\n    description = '{description}',\n    inventory_image = '{name}.png',\n    tool_capabilities = {{\n        full_punch_interval = 1.0,\n        max_drop_level = 1\n    }}\n}})"
            }
        ]
        
        for i in range(count):
            pkg = random.choice(self.packages)
            template = random.choice(scaffold_templates)
            
            # Extract clean name and description
            pkg_name = pkg.get('package', '').split('/')[-1]
            clean_name = pkg_name.replace('-', '_').replace(' ', '_').lower()[:15]
            desc = pkg.get('description', pkg.get('title', 'Node'))[:50]
            
            if 'light' in template['output']:
                output = template['output'].format(
                    node_name=f"mymod:{clean_name}",
                    description=desc,
                    light_level=random.choice([3, 7, 11, 14])
                )
            else:
                output = template['output'].format(
                    node_name=f"mymod:{clean_name}" if 'node' in template['output'] else f"mymod:{clean_name}",
                    tool_name=f"mymod:{clean_name}",
                    description=desc,
                    name=clean_name
                )
            
            items.append({
                "instruction": template['instruction'].format(
                    name=clean_name,
                    desc=desc,
                    light=random.choice([3, 7, 11, 14])
                ),
                "input": template['input'],
                "output": output,
                "family": "scaffold"
            })
        
        return items
    
    def create_repair_items(self, count: int) -> List[Dict]:
        """Create repair (unified diff) items"""
        items = []
        
        repair_templates = [
            {
                "instruction": "Fix the missing tiles field in this node registration",
                "input": "minetest.register_node('mymod:broken', {\n    description = 'Broken Node'\n})",
                "output": "--- a/file.lua\n+++ b/file.lua\n@@ -1,3 +1,4 @@\n minetest.register_node('mymod:broken', {\n     description = 'Broken Node',\n+    tiles = {'default_stone.png'}\n })"
            },
            {
                "instruction": "Add the missing light_source field to make this node emit light",
                "input": "minetest.register_node('mymod:lamp', {\n    description = 'Lamp',\n    tiles = {'default_torch.png'}\n})",
                "output": "--- a/file.lua\n+++ b/file.lua\n@@ -1,4 +1,5 @@\n minetest.register_node('mymod:lamp', {\n     description = 'Lamp',\n-    tiles = {'default_torch.png'}\n+    tiles = {'default_torch.png'},\n+    light_source = 11\n })"
            },
            {
                "instruction": "Fix the syntax error in this tool registration",
                "input": "minetest.register_tool('mymod:pick' {\n    description = 'Pickaxe'\n})",
                "output": "--- a/file.lua\n+++ b/file.lua\n@@ -1,3 +1,3 @@\n-minetest.register_tool('mymod:pick' {\n+minetest.register_tool('mymod:pick', {\n     description = 'Pickaxe'\n })"
            }
        ]
        
        for i in range(count):
            template = random.choice(repair_templates)
            items.append({
                "instruction": template['instruction'],
                "input": template['input'],
                "output": template['output'],
                "family": "repair"
            })
        
        return items
    
    def create_doc_items(self, count: int) -> List[Dict]:
        """Create doc-grounded (API usage) items"""
        items = []
        
        doc_templates = [
            {
                "instruction": "Using the provided API documentation, write code to register a node",
                "input": "minetest.register_node(name, definition)\n\nRegisters a node with the given name and definition table.\nRequired fields: description, tiles",
                "output": "minetest.register_node('mymod:example', {\n    description = 'Example Node',\n    tiles = {'default_dirt.png'}\n})"
            },
            {
                "instruction": "Use this API to create a tool with the specified properties",
                "input": "minetest.register_tool(name, definition)\n\ntool_capabilities = {\n    full_punch_interval = <number>,\n    max_drop_level = <number>\n}",
                "output": "minetest.register_tool('mymod:hammer', {\n    description = 'Hammer',\n    inventory_image = 'hammer.png',\n    tool_capabilities = {\n        full_punch_interval = 1.2,\n        max_drop_level = 2\n    }\n})"
            },
            {
                "instruction": "Implement a node that uses the light_source property from the documentation",
                "input": "Node definition fields:\n- light_source: integer from 0-14, amount of light emitted\n- tiles: array of texture names\n- description: human readable name",
                "output": "minetest.register_node('mymod:glowstone', {\n    description = 'Glowing Stone',\n    tiles = {'glowstone.png'},\n    light_source = 9\n})"
            }
        ]
        
        for i in range(count):
            template = random.choice(doc_templates)
            items.append({
                "instruction": template['instruction'],
                "input": template['input'],
                "output": template['output'],
                "family": "doc"
            })
        
        return items
    
    def create_eval_dataset(self, output_path: str) -> None:
        """Create the 60-item evaluation dataset"""
        eval_items = []
        
        # Exactly 20 of each family as specified
        eval_items.extend(self.create_scaffold_items(20))
        eval_items.extend(self.create_repair_items(20))
        eval_items.extend(self.create_doc_items(20))
        
        # Shuffle for good distribution
        random.shuffle(eval_items)
        
        # Save as JSONL
        with open(output_path, 'w') as f:
            for item in eval_items:
                f.write(json.dumps(item) + '\n')
        
        print(f"✅ Eval dataset created: {len(eval_items)} items at {output_path}")
        
        # Validate
        families = {}
        for item in eval_items:
            families[item['family']] = families.get(item['family'], 0) + 1
        
        print(f"   Family distribution: {families}")
    
    def create_train_dataset(self, output_path: str, size: int = 600) -> None:
        """Create training dataset (200-1k items)"""
        train_items = []
        
        # Distribute across families (more scaffold/doc, fewer repair for training)
        scaffold_count = int(size * 0.4)  # 40%
        doc_count = int(size * 0.4)       # 40% 
        repair_count = size - scaffold_count - doc_count  # 20%
        
        train_items.extend(self.create_scaffold_items(scaffold_count))
        train_items.extend(self.create_doc_items(doc_count))
        train_items.extend(self.create_repair_items(repair_count))
        
        # Shuffle for training
        random.shuffle(train_items)
        
        # Save as JSONL
        with open(output_path, 'w') as f:
            for item in train_items:
                f.write(json.dumps(item) + '\n')
        
        print(f"✅ Train dataset created: {len(train_items)} items at {output_path}")
        
        # Validate
        families = {}
        for item in train_items:
            families[item['family']] = families.get(item['family'], 0) + 1
        
        print(f"   Family distribution: {families}")

def main():
    """Create both datasets"""
    # Set random seed for reproducibility
    random.seed(42)
    
    # Path to collected Luanti data  
    luanti_data_path = "/Users/tdeshane/luanti_fine_tune/data/luanti_github_links.json"
    
    # Check if data exists
    if not Path(luanti_data_path).exists():
        print(f"❌ Luanti data not found at {luanti_data_path}")
        print("   Please ensure the Luanti collection is complete")
        return
    
    # Create builder
    builder = LuantiDatasetBuilder(luanti_data_path)
    
    # Create datasets
    builder.create_eval_dataset("data/eval/luanti_eval.jsonl") 
    builder.create_train_dataset("data/train/luanti_train.jsonl", size=600)
    
    print("\n🎯 Datasets created successfully!")
    print("📋 Next: Run validation to ensure JSONL format is correct")

if __name__ == "__main__":
    main()