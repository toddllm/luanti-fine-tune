# Luanti Capability Dataset Schema

## JSONL Format
Each line contains exactly these fields:

```json
{
  "instruction": "<string>",
  "input": "<string or empty string>",
  "output": "<string>", 
  "family": "scaffold|repair|doc"
}
```

## Family Definitions

### `scaffold` - Node Registration
**Task**: Register a Luanti node with required fields
**Required in output**:
- `minetest.register_node`
- `light_source=\d+` (if lighting)
- `tiles={` (array format)

**Forbidden**: malformed syntax, missing required fields

### `repair` - Code Fixing
**Task**: Given broken Lua code, output unified diff that fixes it
**Input**: Broken Luanti code
**Output**: Unified diff format (`--- a/file.lua`, `+++ b/file.lua`, etc.)
**Required**: Valid unified diff that applies cleanly

### `doc` - Documentation-Grounded Code
**Task**: Given API documentation, generate correct usage
**Input**: Short API snippet or documentation
**Output**: Correct Luanti code using that API
**Required**: Valid Lua syntax, correct API usage

## Validation Rules
- All `output` fields must parse as valid Lua (if `luac` available)
- `repair` outputs must be valid unified diff format
- `scaffold` outputs must contain required patterns
- All fields are required (no null/missing values)
- `family` must be exactly one of the three values