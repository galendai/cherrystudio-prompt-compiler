#!/usr/bin/env python3
"""
CherryStudio Prompt JSON Validator

Validates generated JSON files against CherryStudio Remote Prompt schema.
Provides detailed error reporting and suggestions for fixing common issues.

Usage:
    python validate.py <json_file>
    python validate.py cherry-studio-prompts.json --verbose

Requirements:
    - Python 3.6+ (standard library only, no external dependencies)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def enable_ansi_colors() -> bool:
    """Enable ANSI colors on Windows."""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return True


def print_color(text: str, color: str = "") -> None:
    """Print colored text to terminal (works on Windows, Mac, Linux)."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bold": "\033[1m",
        "reset": "\033[0m",
    }

    color_code = colors.get(color, "")
    reset_code = colors["reset"]
    print(f"{color_code}{text}{reset_code}")


def print_header(text: str) -> None:
    """Print section header."""
    print()
    print("=" * 50)
    print(text)
    print("=" * 50)


class ValidationIssue:
    """Represents a single validation issue."""

    def __init__(
        self,
        level: str,
        prompt_id: str,
        field: str,
        message: str,
        suggestion: Optional[str] = None,
    ):
        self.level = level  # "error", "warning", "info"
        self.prompt_id = prompt_id
        self.field = field
        self.message = message
        self.suggestion = suggestion


class PromptValidator:
    """Validates CherryStudio prompt JSON files."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.issues: List[ValidationIssue] = []
        self.prompts: List[Dict[str, Any]] = []

    def add_issue(
        self,
        level: str,
        prompt_id: str,
        field: str,
        message: str,
        suggestion: Optional[str] = None,
    ) -> None:
        """Add a validation issue."""
        self.issues.append(ValidationIssue(level, prompt_id, field, message, suggestion))

    def check_required_fields(self) -> None:
        """Check that all required fields are present."""
        required_fields = ["id", "name", "description", "emoji", "group", "prompt"]

        for prompt in self.prompts:
            pid = prompt.get("id", "unknown")
            name = prompt.get("name", "unknown")

            for field in required_fields:
                if field not in prompt:
                    self.add_issue(
                        "error",
                        str(pid),
                        field,
                        f"Required field '{field}' is missing",
                        f"Add '{field}': <value> to the prompt object"
                    )

    def check_field_types(self) -> None:
        """Check that fields have correct types."""
        for prompt in self.prompts:
            pid = prompt.get("id", "unknown")

            # Check id is string
            if "id" in prompt and not isinstance(prompt["id"], str):
                self.add_issue(
                    "error",
                    str(pid),
                    "id",
                    f"ID must be a string, got {type(prompt['id']).__name__}",
                    "Convert ID to string format"
                )

            # Check name is string
            if "name" in prompt and not isinstance(prompt["name"], str):
                self.add_issue(
                    "error",
                    str(pid),
                    "name",
                    f"Name must be a string, got {type(prompt['name']).__name__}",
                    "Convert name to string"
                )

            # Check description is string
            if "description" in prompt and not isinstance(prompt["description"], str):
                self.add_issue(
                    "error",
                    str(pid),
                    "description",
                    f"Description must be a string, got {type(prompt['description']).__name__}",
                    "Convert description to string"
                )

            # Check emoji is string
            if "emoji" in prompt and not isinstance(prompt["emoji"], str):
                self.add_issue(
                    "error",
                    str(pid),
                    "emoji",
                    f"Emoji must be a string, got {type(prompt['emoji']).__name__}",
                    "Use a string for emoji"
                )

            # Check group is array
            if "group" in prompt and not isinstance(prompt["group"], list):
                self.add_issue(
                    "error",
                    str(pid),
                    "group",
                    f"Group must be an array, got {type(prompt['group']).__name__}",
                    "Use array format: ['Category1', 'Category2']"
                )

            # Check prompt is string
            if "prompt" in prompt and not isinstance(prompt["prompt"], str):
                self.add_issue(
                    "error",
                    str(pid),
                    "prompt",
                    f"Prompt must be a string, got {type(prompt['prompt']).__name__}",
                    "Convert prompt content to string"
                )

    def check_id_sequence(self) -> None:
        """Check that IDs are sequential starting from '1'."""
        id_set = set()

        for i, prompt in enumerate(self.prompts, 1):
            pid = prompt.get("id")

            if pid is None:
                continue

            # Check if ID is numeric string
            if isinstance(pid, str) and not pid.isdigit():
                self.add_issue(
                    "error",
                    str(pid),
                    "id",
                    f"ID must be numeric string, got '{pid}'",
                    "Use numeric values like '1', '2', '3'..."
                )
                continue

            # Check for duplicates
            if pid in id_set:
                self.add_issue(
                    "error",
                    str(pid),
                    "id",
                    f"Duplicate ID found: '{pid}'",
                    "Assign unique sequential IDs"
                )
            id_set.add(pid)

            # Check if sequential
            expected_id = str(i)
            if isinstance(pid, str) and pid != expected_id:
                self.add_issue(
                    "warning",
                    str(pid),
                    "id",
                    f"ID is not sequential: expected '{expected_id}', got '{pid}'",
                    "Use sequential IDs starting from '1'"
                )

    def check_emoji_validity(self) -> None:
        """Check emoji validity and suggest improvements."""
        for prompt in self.prompts:
            emoji = prompt.get("emoji", "")
            pid = prompt.get("id", "unknown")
            desc = prompt.get("description", "")

            # Check emoji length
            if not emoji:
                self.add_issue(
                    "error",
                    pid,
                    "emoji",
                    "Emoji is missing",
                    "Add a relevant emoji based on description"
                )
                continue

            # Check if it looks like an emoji
            if not self._looks_like_emoji(emoji):
                self.add_issue(
                    "warning",
                    pid,
                    "emoji",
                    f"'{emoji}' may not be a valid emoji",
                    "Use a single emoji character"
                )

            # Check for semantic mismatch
            if self.verbose and desc:
                suggested = self._suggest_better_emoji(desc, emoji)
                if suggested and suggested != emoji:
                    self.add_issue(
                        "info",
                        pid,
                        "emoji",
                        f"Current: {emoji}",
                        f"Consider: {suggested}"
                    )

    def _looks_like_emoji(self, text: str) -> bool:
        """Check if text looks like an emoji."""
        emoji_ranges = [
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
            (0x1F680, 0x1F6FF),  # Transport and Map
            (0x1F1E0, 0x1F1FF),  # Flags
            (0x2600, 0x26FF),    # Misc symbols
            (0x2700, 0x27BF),    # Dingbats
            (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
            (0x1FA00, 0x1FA6F),  # Chess Symbols
            (0x1FA70, 0x1FAFF),  # Symbols and Pictographs Extended-A
            (0x231A, 0x23FF),    # Miscellaneous Technical
            (0x2B50, 0x2B55),    # Stars
            (0x203C, 0x3299),    # Miscellaneous Symbols
        ]

        for char in text:
            code = ord(char)
            if any(start <= code <= end for start, end in emoji_ranges):
                return True
        return False

    def _suggest_better_emoji(self, desc: str, current: str) -> Optional[str]:
        """Suggest a better emoji based on description."""
        desc_lower = desc.lower()

        emoji_suggestions = {
            "👨‍💼": ["pm", "product manager", "business", "strategy"],
            "👨‍💻": ["developer", "engineer", "coding", "programming", "software"],
            "✍️": ["writer", "writing", "copy", "content"],
            "🎨": ["design", "creative", "art", "ui", "ux"],
            "📊": ["analytic", "data", "metric", "analysis"],
            "🤖": ["assistant", "helper", "copilot", "ai"],
            "💬": ["chat", "support", "communication"],
            "📚": ["teacher", "education", "learning"],
            "💰": ["finance", "money", "trading"],
            "🔬": ["science", "research", "lab"],
        }

        for emoji, keywords in emoji_suggestions.items():
            if emoji != current and any(kw in desc_lower for kw in keywords):
                return emoji

        return None

    def check_group_format(self) -> None:
        """Check that group field is an array with at least one element."""
        for prompt in self.prompts:
            group = prompt.get("group")
            pid = prompt.get("id", "unknown")

            if group is None:
                continue

            if isinstance(group, str):
                self.add_issue(
                    "error",
                    pid,
                    "group",
                    f"Group is a string, should be array. Got: '{group}'",
                    f"Change to 'group': ['{group}']"
                )
                continue

            if isinstance(group, list):
                if len(group) == 0:
                    self.add_issue(
                        "error",
                        pid,
                        "group",
                        "Group array is empty",
                        "Add at least one category: ['General']"
                    )

                # Check for empty strings in group
                for i, g in enumerate(group):
                    if not isinstance(g, str):
                        self.add_issue(
                            "warning",
                            pid,
                            "group",
                            f"group[{i}] is not a string: {g}",
                            "Use string values for group categories"
                        )
                    elif not g.strip():
                        self.add_issue(
                            "warning",
                            pid,
                            "group",
                            f"group[{i}] is an empty string",
                            "Remove empty group entries"
                        )

    def check_prompt_content(self) -> None:
        """Check prompt content validity."""
        for prompt in self.prompts:
            prompt_content = prompt.get("prompt", "")
            pid = prompt.get("id", "unknown")

            if not prompt_content:
                self.add_issue(
                    "error",
                    pid,
                    "prompt",
                    "Prompt content is empty",
                    "Add the actual prompt content including YAML frontmatter"
                )
                continue

            # Check for YAML frontmatter
            if not prompt_content.strip().startswith("---"):
                self.add_issue(
                    "warning",
                    pid,
                    "prompt",
                    "Prompt may be missing YAML frontmatter",
                    "Add YAML frontmatter starting with '---'"
                )

            # Check for common YAML frontmatter fields
            if "---" in prompt_content:
                frontmatter_match = re.match(
                    r"^---\s*\n(.*?)\n---",
                    prompt_content,
                    re.DOTALL
                )
                if frontmatter_match:
                    yaml_text = frontmatter_match.group(1)

                    if "description:" not in yaml_text:
                        self.add_issue(
                            "info",
                            pid,
                            "prompt",
                            "YAML frontmatter missing 'description' field",
                            "Add 'description: <brief description>'"
                        )

                    if "category:" not in yaml_text and "group:" not in yaml_text:
                        self.add_issue(
                            "info",
                            pid,
                            "prompt",
                            "YAML frontmatter missing 'category' field",
                            "Add 'category: [CategoryName]'"
                        )

    def validate_file(self, json_file: Path) -> bool:
        """
        Validate a JSON file against CherryStudio schema.

        Returns:
            True if validation passes (no errors), False otherwise.
        """
        # Read and parse JSON
        try:
            content = json_file.read_text(encoding="utf-8")
            self.prompts = json.loads(content)
        except FileNotFoundError:
            print_color(f"Error: File not found: {json_file}", "red")
            return False
        except json.JSONDecodeError as e:
            print_color(f"Error: Invalid JSON - {e}", "red")
            return False

        # Check if it's an array
        if not isinstance(self.prompts, list):
            print_color("Error: Root element must be an array", "red")
            return False

        if len(self.prompts) == 0:
            print_color("Warning: Empty array - no prompts to validate", "yellow")
            return True

        # Run all validations
        self.check_required_fields()
        self.check_field_types()
        self.check_id_sequence()
        self.check_emoji_validity()
        self.check_group_format()
        self.check_prompt_content()

        return True

    def print_report(self) -> Tuple[int, int, int]:
        """
        Print validation report.

        Returns:
            Tuple of (error_count, warning_count, info_count)
        """
        errors = [i for i in self.issues if i.level == "error"]
        warnings = [i for i in self.issues if i.level == "warning"]
        infos = [i for i in self.issues if i.level == "info"]

        print_header("Validation Summary")
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")
        print(f"Info: {len(infos)}")

        if errors:
            self._print_issues("Errors", errors, "red")
        if warnings and self.verbose:
            self._print_issues("Warnings", warnings, "yellow")
        if infos and self.verbose:
            self._print_issues("Info", infos, "blue")

        return len(errors), len(warnings), len(infos)

    def _print_issues(self, title: str, issues: List[ValidationIssue], color: str) -> None:
        """Print issues."""
        print()
        print_color(title, color)
        print("-" * len(title))

        for i in issues[:20]:  # Limit to first 20 issues
            print(f"\n{i.prompt_id} - {i.field}")
            print(f"  {i.message}")
            if i.suggestion:
                print(f"  💡 {i.suggestion}")

        if len(issues) > 20:
            print(f"\n... and {len(issues) - 20} more")


def main():
    # Enable ANSI colors on Windows
    enable_ansi_colors()

    parser = argparse.ArgumentParser(
        description="Validate CherryStudio prompt JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s cherry-studio-prompts.json
  %(prog)s cherry-studio-prompts.json --verbose
        """,
    )
    parser.add_argument("json_file", type=str, help="JSON file to validate")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show warnings and info messages",
    )

    args = parser.parse_args()

    json_file = Path(args.json_file)
    if not json_file.is_file():
        print_color(f"Error: File not found: {json_file}", "red")
        sys.exit(1)

    # Print header
    print_color("CherryStudio Prompt Validator", "bold")
    print(f"Validating {json_file}")

    # Validate
    validator = PromptValidator(verbose=args.verbose)
    validator.validate_file(json_file)
    errors, warnings, infos = validator.print_report()

    # Final result
    if errors == 0:
        print_color("\n✓ Validation passed!", "green")
    else:
        print_color(f"\n✗ Validation failed with {errors} error(s)", "red")

    # Exit code based on error count
    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
