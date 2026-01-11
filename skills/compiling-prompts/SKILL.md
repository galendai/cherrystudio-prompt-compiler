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
1. Scan for all `.md` files in the specified directory
2. Parse YAML frontmatter from each file
3. Generate CherryStudio-compatible JSON with semantic emojis
4. Output to `cherry-studio-prompts.json`

## Compilation Process

### Step 1: Scan for Markdown Files

Use the `Glob` tool to find all `.md` files in the target directory:

```
Glob pattern: **/*.md in the specified path
```

**Verification checklist:**
- [ ] All Markdown files found in target directory
- [ ] File paths are properly formatted (use forward slashes `/`)
- [ ] Exclude any non-Markdown files

### Step 2: Read and Parse Each File

Use the `Read` tool to read each Markdown file. Extract:

**1. YAML Frontmatter** (between `---` markers):
   - `description`: Assistant description
   - `category`: Group classification (default: `["General"]`)
   - Other metadata (author, version, tags, etc.)

**2. Full Content**: Include the complete Markdown content (frontmatter + body)

**Verification checklist:**
- [ ] YAML frontmatter properly extracted
- [ ] Full content preserved (including YAML markers)
- [ ] Description field retrieved (or marked as missing)
- [ ] Category field retrieved (or set to default)

### Step 3: Field Mapping

Map extracted data to CherryStudio JSON format:

| CherryStudio Field | Source | Notes |
|-------------------|--------|-------|
| `id` | Auto-generated | Sequential numbers: "1", "2", "3"... |
| `name` | Filename | Without `.md` extension |
| `description` | YAML `description` | Fallback to empty string if missing |
| `emoji` | **AI-generated** | Use semantic understanding of description to pick relevant emoji |
| `group` | YAML `category` | Convert to array if string; default to `["General"]` |
| `prompt` | Full content | Include YAML frontmatter + Markdown body |

**Verification checklist:**
- [ ] All required fields mapped
- [ ] ID is sequential starting from "1"
- [ ] Name derived from filename (no extension)
- [ ] Group is always an array

### Step 4: Generate JSON Array

Output a JSON array with all compiled prompts:

```json
[
  {
    "id": "1",
    "name": "example-prompt",
    "description": "A helpful AI assistant",
    "emoji": "🤖",
    "group": ["Template"],
    "prompt": "---\nauthor: ...\n---\n\n# Content here"
  }
]
```

**Verification checklist:**
- [ ] Valid JSON array format
- [ ] All prompts have required fields
- [ ] Prompt content preserves original formatting
- [ ] Emoji is a single character

### Step 5: Write Output File

Use the `Write` tool to save the result as `cherry-studio-prompts.json`.

**Verification checklist:**
- [ ] File successfully written
- [ ] JSON is valid and properly formatted
- [ ] File is in expected location

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
