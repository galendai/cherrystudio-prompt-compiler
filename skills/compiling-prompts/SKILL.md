---
name: compiling-prompts
description: Compile local Markdown LLM prompts to CherryStudio-compatible Remote JSON format with batch processing support. Use when user wants to convert prompts, batch process Markdown files, prepare prompts for CherryStudio import, or mentions CherryStudio, prompt compilation, or JSON conversion. Supports semantic emoji matching and optional GitHub Gist sync.
version: 1.1.0
author: Galen Dai
---

# CherryStudio Prompt Compiler Skill

## Overview

This skill compiles local Markdown-formatted LLM prompts into CherryStudio-compatible Remote JSON format using Claude Code's native model capabilities.

**Key Features:**
- Zero external dependencies - uses only Claude Code built-in tools
- Intelligent semantic emoji generation based on description content
- Batch processing for entire folders
- Complete preservation of YAML frontmatter and Markdown content

## When to Use

Activate this skill when:
- User wants to compile Markdown prompts to JSON format
- User needs to batch process an entire folder of prompt files
- User asks about CherryStudio prompt format requirements
- User wants to sync prompts to GitHub Gist
- User mentions "prompt compiler", "CherryStudio", or "compile prompts"

## Quick Start

```
User: Compile all prompts in ./prompts/ folder
```

The skill will:
1. Run `compile.py` to scan and compile prompts
2. Run `validate.py` to verify the output
3. Report the results

## Compilation Process

### Step 1: Execute Compilation Script

Use the `RunCommand` tool to execute the Python compilation script. This script handles file scanning, parsing, and JSON generation efficiently.

```bash
python skills/compiling-prompts/scripts/compile.py <input_dir> [output_file]
```

Default output file is `cherry-studio-prompts.json`.

### Step 2: Validate Output

Run the validation script to ensure the generated JSON meets CherryStudio requirements.

```bash
python skills/compiling-prompts/scripts/validate.py <output_file>
```

### Step 3: Auto-Fix (If needed)

If validation fails, use the fix script to resolve common issues automatically.

```bash
python skills/compiling-prompts/scripts/fix.py <output_file>
```

### Step 4: Final Report

Report the location of the compiled file and the number of prompts compiled.

## Emoji Generation Guidelines

Use semantic understanding to match emojis to descriptions based on the meaning and context of the description text:

| Description Pattern | Emoji |
|-------------------|-------|
| Product manager, PM, business, strategy | 👨‍💼 |
| Developer, engineer, coding, programming | 👨‍💻 |
| Writer, content, copy, writing | ✍️ |
| Designer, creative, art, UI/UX | 🎨 |
| Analytics, data, metrics, analysis | 📊 |
| Assistant, helper, copilot, aid | 🤖 |
| Chat, support, communication | 💬 |
| Teacher, education, learning | 📚 |
| Finance, money, trading | 💰 |
| Science, research, lab | 🔬 |
| General/default | 🔧 |

**Tips for better emoji matching:**
- Consider the primary role/function described
- Look for domain-specific keywords
- Match the tone of the description
- When in doubt, use the default 🔧

## Error Handling

### Missing YAML Frontmatter

**Action**: Use defaults
- Description: Empty string `""`
- Group: `["General"]`
- Emoji: Default based on filename or content analysis

### Malformed YAML

**Action**: Log warning and skip file
- Report the specific file and error
- Continue processing remaining files
- Include error summary in final report

### Empty Description

**Action**: Generate generic emoji based on:
1. Filename analysis
2. Content keywords
3. Default to 🔧 if no clear pattern

### File Read Errors

**Action**: Report specific file and continue
- Log the file path and error type
- Continue with remaining files
- Include count of failed files in summary

## Output Schema (CherryStudio)

Each compiled prompt must follow this structure:

```json
{
  "id": "string",      // Required: Sequential number
  "name": "string",    // Required: Filename without extension
  "description": "string",  // Required: From YAML or empty
  "emoji": "string",   // Required: Single emoji character
  "group": ["string"], // Required: Array of category strings
  "prompt": "string"   // Required: Full Markdown content
}
```

## Example Workflow

```
User: /compile-prompts ./my-prompts/

1. Glob: ./my-prompts/**/*.md → [file1.md, file2.md, file3.md]

2. Read: file1.md
   → Extract YAML frontmatter
   → Extract full content
   → Generate emoji based on description

3. Generate: JSON object with fields mapped
   {
     "id": "1",
     "name": "file1",
     "description": "...",
     "emoji": "👨‍💼",
     "group": ["Template"],
     "prompt": "---\n...\n---\n\n# Content"
   }

4. Repeat for all files (file2.md → id: "2", file3.md → id: "3")

5. Write: cherry-studio-prompts.json
   [
     { "id": "1", ... },
     { "id": "2", ... },
     { "id": "3", ... }
   ]

6. Report: "Compiled 3 prompts successfully to cherry-studio-prompts.json"
```

## Scripts Reference

The `scripts/` directory within this skill provides Python utilities for automated workflows:

### compile.py

Batch compile Markdown prompts to CherryStudio JSON format.

```bash
python scripts/compile.py <input_dir> [output_file]
```

**Features:**
- Recursive directory scanning
- Intelligent emoji generation based on semantic analysis
- YAML frontmatter parsing with error handling
- Rich terminal output with progress bars

**Example:**
```bash
python scripts/compile.py ./prompts/ cherry-studio-prompts.json
```

### validate.py

Validate JSON files against CherryStudio schema.

```bash
python scripts/validate.py <json_file> [--verbose]
```

**Features:**
- JSON schema validation
- Sequential ID verification
- Emoji validity checking
- Group format validation
- Prompt content verification
- Detailed error reporting with suggestions

**Example:**
```bash
python scripts/validate.py cherry-studio-prompts.json --verbose
```

### fix.py

Automatically fix common issues in JSON files.

```bash
python scripts/fix.py <json_file> [output_file] [--dry-run] [--validate-after]
```

**Features:**
- Fix sequential IDs
- Generate missing emojis based on description
- Convert string groups to arrays
- Add missing YAML frontmatter
- Fix missing required fields
- Self-healing with validation loop

**Examples:**
```bash
# Fix in place
python scripts/fix.py cherry-studio-prompts.json

# Dry run to see what would be fixed
python scripts/fix.py broken.json --dry-run

# Fix and validate after
python scripts/fix.py broken.json fixed.json --validate-after
```

### Auto-Fix Workflow

For a complete automated workflow with self-healing:

```bash
# 1. Compile
python scripts/compile.py ./prompts/ output.json

# 2. Fix and validate (repeat until validation passes)
python scripts/fix.py output.json --validate-after

# 3. If validation still fails, iterate
while ! python scripts/validate.py output.json; do
    python scripts/fix.py output.json
done
```

## Reference Documentation

For more detailed information, see:

- [CherryStudio Schema Reference](reference/cherry-studio-schema.md) - Complete JSON Schema specification
- [Field Mapping Rules](reference/field-mapping.md) - Detailed field mapping logic and edge cases
- [Emoji Generation Strategy](reference/emoji-generation.md) - Advanced emoji matching patterns
- [Error Handling Guide](reference/error-handling.md) - Error types and recovery strategies

## Next Steps for User

After compilation:
1. Review the generated `cherry-studio-prompts.json` file
2. Verify all prompts are correctly formatted
3. Import the JSON file into CherryStudio
4. Optionally sync to GitHub Gist for cloud access

## Troubleshooting

**Problem**: Some prompts are missing emojis
- **Solution**: Check description field in YAML frontmatter

**Problem**: Category is not being recognized
- **Solution**: Ensure `category` field exists in YAML frontmatter

**Problem**: JSON output is empty
- **Solution**: Verify the source directory contains `.md` files
