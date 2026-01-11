# Error Handling Guide

Comprehensive error types, recovery strategies, and logging practices.

## Error Categories

### 1. File System Errors

#### File Not Found
**Scenario**: Glob pattern returns no files

**Action**:
- Report: "No Markdown files found in {directory}"
- Check: Directory exists and contains .md files
- Suggestion: Verify path is correct

**Example Output**:
```
No Markdown files found in ./prompts/
Please verify:
- The directory exists
- It contains .md files
- The path is correct
```

#### Permission Denied
**Scenario**: Cannot read file due to permissions

**Action**:
- Log: "Permission denied: {filepath}"
- Continue: Process remaining files
- Report: Count of permission errors in summary

### 2. Parsing Errors

#### Missing YAML Frontmatter
**Scenario**: File starts without `---` markers

**Severity**: Warning (not fatal)

**Action**:
- Log: "No YAML frontmatter in {filename}, using defaults"
- Use: `description = ""`, `group = ["General"]`
- Continue: Process file normally

**Example**:
```
Warning: pm-assistant.md has no YAML frontmatter
Using defaults: description="", group=["General"]
```

#### Malformed YAML
**Scenario**: YAML syntax error between `---` markers

**Severity**: Error (file skipped)

**Action**:
- Log: "YAML parsing failed in {filename}: {error_details}"
- Skip: Do not include this file in output
- Count: Increment error counter

**Example**:
```
Error: Malformed YAML in code-review.md
Line 5: Unexpected indentation
Skipping file...
```

#### Incomplete YAML Delimiters
**Scenario**: Only one `---` marker found

**Severity**: Error (file skipped)

**Action**:
- Log: "Incomplete YAML frontmatter in {filename}"
- Skip: Do not include this file in output

### 3. Content Errors

#### Empty File
**Scenario**: File has no content after YAML

**Severity**: Error (file skipped)

**Action**:
- Log: "Empty file: {filename}"
- Skip: File requires non-empty prompt content

#### Invalid Category Type
**Scenario**: `category` field is neither string nor array

**Action**:
- Log: "Invalid category type in {filename}, using default"
- Use: `group = ["General"]`

### 4. Output Errors

#### JSON Serialization Failure
**Scenario**: Cannot serialize output to JSON

**Severity**: Fatal (stops compilation)

**Action**:
- Log: "JSON serialization failed: {error}"
- Report: Last successful checkpoint if available
- Exit: Stop compilation

#### File Write Failure
**Scenario**: Cannot write to output file

**Severity**: Fatal (stops compilation)

**Action**:
- Log: "Failed to write {filepath}: {error}"
- Check: Disk space, permissions, directory existence
- Exit: Stop compilation

## Error Recovery Strategy

### Continue-On-Error Approach

The compiler should:
1. **Log** each error with context
2. **Continue** processing remaining files
3. **Report** summary at the end

### Error Summary Format

```
Compilation complete with errors:

Successfully compiled: 7 files
Skipped due to errors: 2 files

Errors:
1. code-review.md: Malformed YAML (line 5)
2. empty.md: Empty file content

Output saved to: cherry-studio-prompts.json
```

### Success Report Format

```
Compilation successful!

Processed: 10 files
Output: cherry-studio-prompts.json
Prompts generated: 10

All prompts validated successfully.
```

## Logging Best Practices

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| Info | Normal operations | "Processing: pm-assistant.md" |
| Warning | Non-fatal issues | "No YAML frontmatter, using defaults" |
| Error | File skipped | "YAML parsing failed, skipping file" |
| Fatal | Process stops | "Cannot write output file" |

### Log Message Format

```
[{LEVEL}] {FILENAME}: {MESSAGE}
```

**Examples:**
```
[INFO] pm-assistant.md: Processing...
[WARNING] code-review.md: Missing description field
[ERROR] invalid.md: Malformed YAML
[FATAL] Output: Disk full
```

## Validation Before Output

Before writing the JSON file, verify:

1. **Array non-empty**: At least one prompt compiled
2. **All required fields**: Each prompt has id, name, description, emoji, group, prompt
3. **Unique IDs**: No duplicate id values
4. **Valid JSON**: Output is valid JSON
5. **Sequential IDs**: IDs are "1", "2", "3", ... with no gaps

### Validation Checklist

```python
def validate_output(prompts):
    # Array non-empty
    if not prompts:
        return False, "No prompts compiled"

    # Required fields
    required = ["id", "name", "description", "emoji", "group", "prompt"]
    for prompt in prompts:
        for field in required:
            if field not in prompt:
                return False, f"Missing field: {field}"

    # Unique sequential IDs
    ids = [p["id"] for p in prompts]
    expected = [str(i) for i in range(1, len(prompts) + 1)]
    if ids != expected:
        return False, f"Non-sequential IDs: {ids}"

    return True, "Validation passed"
```

## User Communication

### Error Messages to User

**Do:**
- Be specific about what failed
- Provide actionable suggestions
- Show the file/line causing issues

**Don't:**
- Use technical jargon without explanation
- Show raw stack traces
- Hide important context

### Example Error Communication

**Good:**
```
Error in pm-assistant.md:
The YAML frontmatter has a syntax error on line 8.
Expected a string for 'description' but found a list.

Fix the YAML format and try again.
```

**Bad:**
```
YAML parse error: line 8 col 15
```
