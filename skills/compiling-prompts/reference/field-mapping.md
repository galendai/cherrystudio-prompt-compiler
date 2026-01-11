# Field Mapping Rules

Detailed rules for mapping Markdown frontmatter to CherryStudio JSON fields.

## Source to Target Mapping

### id

| Attribute | Value |
|-----------|-------|
| Source | Auto-generated |
| Type | string (numeric) |
| Format | Sequential starting from "1" |
| Increment | +1 for each prompt processed |

**Example:** Processing 3 files produces IDs: "1", "2", "3"

### name

| Attribute | Value |
|-----------|-------|
| Source | Filename |
| Transformation | Remove `.md` extension |
| Special chars | Preserve original (no sanitization needed) |

**Examples:**
- `pm-assistant.md` → `"pm-assistant"`
- `code_review.md` → `"code_review"`
- `My Prompt.md` → `"My Prompt"`

### description

| Attribute | Value |
|-----------|-------|
| Source | YAML frontmatter `description` field |
| Fallback | Empty string `""` if missing |
| Whitespace | Trim leading/trailing spaces |

**Edge Cases:**
- Missing field → `""`
- Multi-line description → Join with single space
- Empty string → Keep as `""`

### emoji

| Attribute | Value |
|-----------|-------|
| Source | AI-generated based on semantic understanding |
| Fallback | `🔧` if no clear match |
| Length | Single emoji character (1-4 bytes) |

**Priority for emoji generation:**
1. Description content (semantic analysis)
2. Filename keywords
3. Content body keywords
4. Default fallback

### group

| Attribute | Value |
|-----------|-------|
| Source | YAML frontmatter `category` field |
| Fallback | `["General"]` |
| Type | Always array |

**Transformations:**

| Input | Output |
|-------|--------|
| `category: Template` | `["Template"]` |
| `category: [Template, Product]` | `["Template", "Product"]` |
| (missing) | `["General"]` |
| `category: ""` | `["General"]` |

### prompt

| Attribute | Value |
|-----------|-------|
| Source | Complete file content |
| Includes | YAML frontmatter + Markdown body |
| Formatting | Preserve original exactly |

**Important:** The `---` YAML markers must be included in the prompt content.

## YAML Frontmatter Extraction

### Standard Format

```markdown
---
author: Galen Dai
version: 2.0
description: PM assistant for product management
category:
  - Template
  - Product
tags:
  - AI
  - Prompt
---

# Content here
```

### Extractable Fields

| Field | Mapped to | Required |
|-------|-----------|----------|
| description | description | No |
| category | group | No |
| author | (not used) | No |
| version | (not used) | No |
| tags | (not used) | No |

### Parsing Edge Cases

**No YAML frontmatter:**
```
# Content starts directly
```
→ Use defaults: `description = ""`, `group = ["General"]`

**Malformed YAML (only one `---`):**
```
---
author: Test

# Content
```
→ Log warning, skip file

**Empty YAML:**
```
---

# Content
```
→ Use defaults: `description = ""`, `group = ["General"]`

**Category as string vs array:**
```yaml
category: Template        # String → ["Template"]
category:                 # Array → ["Template", "Product"]
  - Template
  - Product
```

## Content Preservation Rules

1. **Line endings**: Preserve original (LF/CRLF)
2. **Whitespace**: Preserve exactly as in source
3. **Comments**: Include all content including comments
4. **Empty lines**: Preserve structure
5. **Special characters**: Preserve Unicode, emojis, etc.
