# CherryStudio JSON Schema Reference

Complete specification for the CherryStudio Remote Prompt JSON format.

## JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["id", "name", "description", "emoji", "group", "prompt"],
    "properties": {
      "id": {
        "type": "string",
        "description": "Sequential unique identifier starting from '1'",
        "pattern": "^[0-9]+$"
      },
      "name": {
        "type": "string",
        "description": "Prompt name derived from filename without .md extension",
        "minLength": 1
      },
      "description": {
        "type": "string",
        "description": "Brief description from YAML frontmatter",
        "default": ""
      },
      "emoji": {
        "type": "string",
        "description": "Single emoji character semantically matched to description",
        "minLength": 1,
        "maxLength": 4
      },
      "group": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Category classification array",
        "minItems": 1,
        "default": ["General"]
      },
      "prompt": {
        "type": "string",
        "description": "Complete Markdown content including YAML frontmatter",
        "minLength": 1
      }
    },
    "additionalProperties": false
  }
}
```

## Field Requirements

| Field | Type | Required | Default | Constraints |
|-------|------|----------|---------|-------------|
| id | string | Yes | None | Must be numeric string, sequential |
| name | string | Yes | None | Non-empty, filename without extension |
| description | string | Yes | `""` | Can be empty string |
| emoji | string | Yes | None | Single emoji character |
| group | array | Yes | `["General"]` | At least one element |
| prompt | string | Yes | None | Non-empty, includes YAML frontmatter |

## Validation Examples

### Valid Prompt Object

```json
{
  "id": "1",
  "name": "pm-copilot",
  "description": "Product manager assistant",
  "emoji": "👨‍💼",
  "group": ["Template", "Product"],
  "prompt": "---\nauthor: Galen\n---\n\n# PM Assistant"
}
```

### Invalid Examples

**Missing required field:**
```json
{
  "id": "1",
  "name": "test",
  "emoji": "🔧",
  "group": ["General"]
  // Missing: description, prompt
}
```

**Invalid group type (string instead of array):**
```json
{
  "id": "1",
  "name": "test",
  "description": "Test",
  "emoji": "🔧",
  "group": "Template",  // Should be: ["Template"]
  "prompt": "..."
}
```

**Empty prompt content:**
```json
{
  "id": "1",
  "name": "test",
  "description": "Test",
  "emoji": "🔧",
  "group": ["General"],
  "prompt": ""  // Should contain content
}
```
