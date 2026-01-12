[中文](./README_CN.md)

# CherryStudio Prompt Compiler

> A Claude Code Skill for compiling local Markdown LLM prompts into CherryStudio-compatible Remote JSON format.

## Overview

The CherryStudio Prompt Compiler is a zero-dependency tool that converts local Markdown-formatted LLM prompts into the JSON format required by [CherryStudio](https://github.com/CherryHQ/cherry-studio). It uses Claude Code's native model capabilities to intelligently parse YAML frontmatter, generate semantic emojis, and batch-process entire folders of prompt files.

## Features

- **Zero External Dependencies**: Uses only Claude Code built-in tools (Read, Glob, Write, Bash)
- **Intelligent Emoji Generation**: Leverages Claude's semantic understanding to match emojis to prompt descriptions
- **Batch Processing**: Process entire folders of Markdown files in one operation
- **Complete Content Preservation**: Retains YAML frontmatter and all Markdown formatting
- **Error Tolerance**: Continues processing even if individual files have issues

## Installation

### Prerequisites

- [Claude Code](https://claude.ai/code) installed
- A project folder with Markdown prompt files

### Setup

1. Clone or copy this repository to your local machine
2. Ensure the skill directory structure is in place:

```
cherrystudio-prompt-compiler/
└── skills/
    └── compiling-prompts/
        ├── SKILL.md
        ├── reference/
        └── examples/
```

3. The skill will be automatically discovered by Claude Code

## Quick Start

### Basic Usage

Simply ask Claude Code to compile your prompts:

```
Compile all prompts in ./prompts/ folder
```

Or use the skill trigger:

```
/compiling-prompts ./my-prompts/
```

### Input Format

Your Markdown files should include YAML frontmatter:

```markdown
---
author: Your Name
version: 1.0
description: A helpful assistant for coding tasks
category:
  - Development
tags:
  - coding
  - programming
---

# Code Assistant

You are a helpful coding assistant...
```

### Output

The compiler generates `cherry-studio-prompts.json`:

```json
[
  {
    "id": "1",
    "name": "code-assistant",
    "description": "A helpful assistant for coding tasks",
    "emoji": "👨‍💻",
    "group": ["Development"],
    "prompt": "---\nauthor: ...\n---\n\n# Code Assistant\n..."
  }
]
```

## Field Mapping

| CherryStudio Field | Source | Notes |
|-------------------|--------|-------|
| `id` | Auto-generated | Sequential: "1", "2", "3"... |
| `name` | Filename | Without `.md` extension |
| `description` | YAML `description` | Empty string if missing |
| `emoji` | AI-generated | Semantic matching |
| `group` | YAML `category` | `["General"]` if missing |
| `prompt` | Full content | YAML + Markdown body |

## Usage Examples

### Compile a Single Folder

```
Compile prompts in ./my-prompts/
```

### Specify Output Location

```
Compile prompts in ./prompts/ and save to ./output/prompts.json
```

### Handle Errors Gracefully

The compiler will continue processing even if some files have issues:

```
Compilation complete with warnings:
- missing-yaml.md: No frontmatter found, using defaults
Successfully compiled: 5 files
Output: cherry-studio-prompts.json
```

## Emoji Generation

The compiler uses semantic understanding to match emojis to your prompt descriptions:

| Description Keywords | Emoji |
|---------------------|-------|
| Product manager, PM, business | 👨‍💼 |
| Developer, engineer, coding | 👨‍💻 |
| Writer, content, writing | ✍️ |
| Designer, creative, art | 🎨 |
| Analytics, data, metrics | 📊 |
| Assistant, helper, copilot | 🤖 |
| Chat, support, communication | 💬 |
| Teacher, education, learning | 📚 |

## Directory Structure

```
skills/compiling-prompts/
├── SKILL.md                    # Main skill file
├── reference/                  # Detailed documentation
│   ├── cherry-studio-schema.md # JSON Schema specification
│   ├── field-mapping.md        # Field mapping rules
│   ├── emoji-generation.md     # Emoji generation strategy
│   └── error-handling.md       # Error handling guide
└── examples/                   # Example files
    ├── basic-prompt.md         # Simple prompt example
    ├── advanced-prompt.md      # Complex prompt example
    └── example-output.json     # Expected output format
```

## Importing to CherryStudio

1. Run the compiler to generate `cherry-studio-prompts.json`
2. Open CherryStudio
3. Go to Settings → Prompts
4. Click "Import" and select the JSON file
5. Your prompts will be available in CherryStudio

## Advanced Usage

### Custom Category Handling

If your prompts use non-standard category formats:

```yaml
# String format (will be converted to array)
category: Template

# Array format (used as-is)
category:
  - Template
  - Product
```

### Handling Missing Metadata

Files without YAML frontmatter will use sensible defaults:
- `description`: Empty string
- `group`: `["General"]`
- `emoji`: Based on filename or content analysis

## Troubleshooting

**Problem**: No Markdown files found
- **Solution**: Verify the directory path contains `.md` files

**Problem**: Some prompts are missing emojis
- **Solution**: Add a `description` field to your YAML frontmatter

**Problem**: Category is not being recognized
- **Solution**: Ensure `category` field exists in YAML frontmatter

**Problem**: JSON output is empty
- **Solution**: Check that source files are valid Markdown with content

## Technical Specifications

For detailed technical information, see:
- [Product Requirements Document](docs/PRD：CherryStudio%20提示词编译器（Prompt%20Compiler）.md)
- [Technical Specification](docs/Tech-Spec：CherryStudio%20提示词编译器（Prompt%20Compiler）.md)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Author

Created by Galen Dai

## Version

1.1.0
