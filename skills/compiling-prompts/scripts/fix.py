#!/usr/bin/env python3
"""
CherryStudio Prompt JSON Fixer

Automatically fixes common issues in CherryStudio prompt JSON files.
Can run standalone or be used as a module by other scripts.

Usage:
    python fix.py <json_file> [output_file]
    python fix.py broken.json fixed.json --dry-run
    python fix.py broken.json --validate-after

Requirements:
    - Python 3.6+ (standard library only, no external dependencies)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


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


# Emoji mapping for fixing missing/invalid emojis
EMOJI_FIXES = {
    # Business & Product
    "product manager": "👨‍💼",
    "pm": "👨‍💼",
    "business": "👨‍💼",
    "strategy": "👨‍💼",
    "marketing": "👨‍💼",
    "startup": "🚀",
    "founder": "🚀",

    # Development
    "developer": "👨‍💻",
    "engineer": "👨‍💻",
    "coding": "👨‍💻",
    "programming": "👨‍💻",
    "software": "👨‍💻",
    "debug": "👨‍💻",
    "frontend": "💻",
    "backend": "💻",
    "devops": "💻",

    # Design & Creative
    "design": "🎨",
    "creative": "🎨",
    "ui": "🎨",
    "ux": "🎨",
    "writer": "✍️",
    "writing": "✍️",
    "content": "✍️",

    # Analytics & Data
    "analytic": "📊",
    "data": "📊",
    "metric": "📊",
    "statistics": "📊",

    # Communication
    "chat": "💬",
    "support": "💬",
    "communication": "💬",
    "customer": "💬",

    # Education
    "teacher": "📚",
    "education": "📚",
    "learning": "📚",
    "tutorial": "📚",

    # Finance
    "finance": "💰",
    "money": "💰",
    "trading": "💰",

    # Science & Research
    "science": "🔬",
    "research": "🔬",

    # Tools & Utilities
    "assistant": "🤖",
    "helper": "🤖",
    "copilot": "🤖",
    "automation": "⚙️",
}

DEFAULT_EMOJI = "🔧"


class FixResult:
    """Result of a fix operation."""

    def __init__(self):
        self.fixes_applied: List[str] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []


class PromptFixer:
    """Fixes common issues in CherryStudio prompt JSON files."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.result = FixResult()

    def add_fix(self, prompt_id: str, field: str, action: str) -> None:
        """Record a fix that was applied."""
        self.result.fixes_applied.append(f"{prompt_id}.{field}: {action}")

    def add_error(self, prompt_id: str, field: str, error: str) -> None:
        """Record an error that occurred."""
        self.result.errors.append(f"{prompt_id}.{field}: {error}")

    def add_warning(self, prompt_id: str, field: str, warning: str) -> None:
        """Record a warning."""
        self.result.warnings.append(f"{prompt_id}.{field}: {warning}")

    def fix_id(self, prompt: Dict[str, Any], index: int) -> bool:
        """
        Fix ID field - ensure sequential numeric strings.

        Returns:
            True if a fix was applied.
        """
        current_id = prompt.get("id")
        expected_id = str(index + 1)

        if current_id != expected_id:
            prompt["id"] = expected_id
            self.add_fix(str(current_id), "id", f"Changed to '{expected_id}'")
            return True

        # Ensure ID is a string
        if isinstance(current_id, int):
            prompt["id"] = str(current_id)
            self.add_fix(str(current_id), "id", "Converted to string")
            return True

        return False

    def fix_name(self, prompt: Dict[str, Any]) -> bool:
        """
        Fix name field - ensure non-empty string.

        Returns:
            True if a fix was applied.
        """
        name = prompt.get("name", "")
        pid = prompt.get("id", "unknown")

        if not name or not isinstance(name, str):
            # Try to extract name from prompt content
            prompt_content = prompt.get("prompt", "")
            new_name = self._extract_name_from_content(prompt_content)

            if new_name:
                prompt["name"] = new_name
                self.add_fix(pid, "name", f"Extracted from content: '{new_name}'")
            else:
                prompt["name"] = f"prompt-{pid}"
                self.add_fix(pid, "name", f"Generated default: 'prompt-{pid}'")
            return True

        return False

    def _extract_name_from_content(self, content: str) -> Optional[str]:
        """Try to extract a meaningful name from prompt content."""
        # Look for title pattern (# Title)
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            # Convert to kebab-case
            title = title_match.group(1).strip()
            return re.sub(r"[\s_]+", "-", title.lower()).strip()

        return None

    def fix_emoji(self, prompt: Dict[str, Any]) -> bool:
        """
        Fix emoji field - ensure valid emoji based on semantic analysis.

        Returns:
            True if a fix was applied.
        """
        emoji = prompt.get("emoji", "")
        pid = prompt.get("id", "unknown")
        description = prompt.get("description", "")
        name = prompt.get("name", "")

        # Check if emoji is missing or invalid
        if not emoji or not self._is_valid_emoji(emoji):
            # Generate new emoji based on description
            new_emoji = self._generate_emoji(description, name)
            prompt["emoji"] = new_emoji
            self.add_fix(pid, "emoji", f"Generated '{new_emoji}' from description")
            return True

        return False

    def _is_valid_emoji(self, text: str) -> bool:
        """Check if text contains a valid emoji."""
        if not text or len(text) > 4:
            return False

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

    def _generate_emoji(self, description: str, name: str) -> str:
        """Generate emoji based on semantic analysis."""
        text = f"{description} {name}".lower()

        # Look for matching patterns
        for pattern, emoji in EMOJI_FIXES.items():
            if pattern in text:
                return emoji

        return DEFAULT_EMOJI

    def fix_group(self, prompt: Dict[str, Any]) -> bool:
        """
        Fix group field - ensure array with at least one element.

        Returns:
            True if a fix was applied.
        """
        group = prompt.get("group")
        pid = prompt.get("id", "unknown")

        # Missing group
        if group is None:
            prompt["group"] = ["General"]
            self.add_fix(pid, "group", "Added default: ['General']")
            return True

        # String instead of array
        if isinstance(group, str):
            prompt["group"] = [group]
            self.add_fix(pid, "group", f"Converted string to array: ['{group}']")
            return True

        # Not an array
        if not isinstance(group, list):
            prompt["group"] = ["General"]
            self.add_fix(pid, "group", f"Converted {type(group).__name__} to array: ['General']")
            return True

        # Empty array
        if len(group) == 0:
            prompt["group"] = ["General"]
            self.add_fix(pid, "group", "Added default to empty array: ['General']")
            return True

        # Filter out invalid entries
        fixed_group = []
        for g in group:
            if isinstance(g, str) and g.strip():
                fixed_group.append(g.strip())
            elif g is not None:
                self.add_warning(pid, "group", f"Removed invalid entry: {g}")

        if len(fixed_group) == 0:
            prompt["group"] = ["General"]
            self.add_fix(pid, "group", "Replaced invalid array with: ['General']")
            return True

        if len(fixed_group) != len(group):
            prompt["group"] = fixed_group
            self.add_fix(pid, "group", f"Removed {len(group) - len(fixed_group)} invalid entries")
            return True

        return False

    def fix_description(self, prompt: Dict[str, Any]) -> bool:
        """
        Fix description field - ensure string type.

        Returns:
            True if a fix was applied.
        """
        description = prompt.get("description")
        pid = prompt.get("id", "unknown")

        if description is None:
            prompt["description"] = ""
            self.add_fix(pid, "description", "Added empty string")
            return True

        if not isinstance(description, str):
            prompt["description"] = str(description)
            self.add_fix(pid, "description", "Converted to string")
            return True

        return False

    def fix_prompt(self, prompt: Dict[str, Any]) -> bool:
        """
        Fix prompt content field - ensure non-empty string with YAML frontmatter.

        Returns:
            True if a fix was applied.
        """
        prompt_content = prompt.get("prompt", "")
        pid = prompt.get("id", "unknown")
        name = prompt.get("name", "")
        description = prompt.get("description", "")
        group = prompt.get("group", ["General"])

        # Empty prompt
        if not prompt_content:
            # Generate minimal prompt with YAML frontmatter
            yaml_frontmatter = self._generate_minimal_frontmatter(name, description, group)
            prompt["prompt"] = f"{yaml_frontmatter}\n\n# {name}\n\nYour prompt content here."
            self.add_fix(pid, "prompt", "Generated minimal prompt with YAML frontmatter")
            return True

        # Not a string
        if not isinstance(prompt_content, str):
            prompt["prompt"] = str(prompt_content)
            self.add_fix(pid, "prompt", "Converted to string")
            return True

        # Missing YAML frontmatter
        if not prompt_content.strip().startswith("---"):
            yaml_frontmatter = self._generate_minimal_frontmatter(name, description, group)
            prompt["prompt"] = f"{yaml_frontmatter}\n\n{prompt_content}"
            self.add_fix(pid, "prompt", "Added YAML frontmatter")
            return True

        return False

    def _generate_minimal_frontmatter(
        self, name: str, description: str, group: List[str]
    ) -> str:
        """Generate minimal YAML frontmatter."""
        category = group[0] if group else "General"
        return (
            "---\n"
            f"description: {description}\n"
            f"category:\n"
            f"  - {category}\n"
            "---"
        )

    def fix_prompt_object(self, prompt: Dict[str, Any], index: int) -> bool:
        """
        Fix all issues in a single prompt object.

        Returns:
            True if any fixes were applied.
        """
        fixes = 0

        fixes += 1 if self.fix_id(prompt, index) else 0
        fixes += 1 if self.fix_name(prompt) else 0
        fixes += 1 if self.fix_description(prompt) else 0
        fixes += 1 if self.fix_emoji(prompt) else 0
        fixes += 1 if self.fix_group(prompt) else 0
        fixes += 1 if self.fix_prompt(prompt) else 0

        return fixes > 0

    def fix_file(self, json_file: Path, output_file: Optional[Path] = None) -> bool:
        """
        Fix all issues in a JSON file.

        Returns:
            True if successful, False otherwise.
        """
        if output_file is None:
            output_file = json_file

        # Read JSON file
        try:
            content = json_file.read_text(encoding="utf-8")
            prompts = json.loads(content)
        except FileNotFoundError:
            print_color(f"Error: File not found: {json_file}", "red")
            return False
        except json.JSONDecodeError as e:
            print_color(f"Error: Invalid JSON - {e}", "red")
            return False

        # Check if it's an array
        if not isinstance(prompts, list):
            print_color("Error: Root element must be an array", "red")
            return False

        if len(prompts) == 0:
            print_color("Warning: Empty array - nothing to fix", "yellow")
            return True

        # Fix each prompt
        print(f"\nFixing {len(prompts)} prompt(s)...\n")

        for i, prompt in enumerate(prompts):
            self.fix_prompt_object(prompt, i)

        # Write output
        if not self.dry_run:
            output_file.write_text(
                json.dumps(prompts, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        else:
            print_color("Dry run mode - changes not written", "yellow")

        return True

    def print_summary(self) -> None:
        """Print fix summary."""
        print_header("Fix Summary")
        print(f"Fixes applied: {len(self.result.fixes_applied)}")
        print(f"Errors: {len(self.result.errors)}")
        print(f"Warnings: {len(self.result.warnings)}")

        if self.result.fixes_applied:
            print("\nFixes applied:")
            for fix in self.result.fixes_applied[:20]:
                print(f"  ✓ {fix}")
            if len(self.result.fixes_applied) > 20:
                print(f"  ... and {len(self.result.fixes_applied) - 20} more")


def main():
    # Enable ANSI colors on Windows
    enable_ansi_colors()

    parser = argparse.ArgumentParser(
        description="Fix common issues in CherryStudio prompt JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s broken.json
  %(prog)s broken.json fixed.json
  %(prog)s broken.json --dry-run
  %(prog)s broken.json --validate-after
        """,
    )
    parser.add_argument("json_file", type=str, help="JSON file to fix")
    parser.add_argument(
        "output_file",
        type=str,
        nargs="?",
        help="Output file (default: overwrites input file)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes",
    )
    parser.add_argument(
        "--validate-after",
        action="store_true",
        help="Run validation after fixing (requires validate.py)",
    )

    args = parser.parse_args()

    json_file = Path(args.json_file)
    if not json_file.is_file():
        print_color(f"Error: File not found: {json_file}", "red")
        sys.exit(1)

    output_file = Path(args.output_file) if args.output_file else json_file

    # Print header
    print_color("CherryStudio Prompt Fixer", "bold")
    print(f"Fixing {json_file}")

    # Fix
    fixer = PromptFixer(dry_run=args.dry_run)
    success = fixer.fix_file(json_file, output_file)

    if not success:
        sys.exit(1)

    # Print summary
    fixer.print_summary()

    # Validate after fixing
    if args.validate_after:
        print_color("\nRunning validation...", "cyan")

        # Import and run validate
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from validate import PromptValidator

            validator = PromptValidator(verbose=True)
            validator.validate_file(output_file if not args.dry_run else json_file)
            validator.print_report()
        except ImportError:
            print_color("Warning: Could not import validate.py", "yellow")

    if fixer.result.errors:
        sys.exit(1)

    print_color(f"\nSuccessfully fixed {len(fixer.result.fixes_applied)} issue(s)!", "green")


if __name__ == "__main__":
    main()
