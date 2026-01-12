#!/usr/bin/env python3
"""
CherryStudio Prompt Compiler

Compiles local Markdown LLM prompts to CherryStudio-compatible Remote JSON format.
Supports batch processing, intelligent emoji generation, and YAML frontmatter parsing.

Usage:
    python compile.py <input_dir> [output_file]
    python compile.py ./prompts/ cherry-studio-prompts.json

Requirements:
    - Python 3.6+ (standard library only, no external dependencies)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Emoji mapping based on semantic patterns
EMOJI_PATTERNS = {
    # Business & Product
    r"(product\s*manager|pm|business|strategy|roadmap|pric(?:ing|e)|market(?:ing)?)": "👨‍💼",
    r"(startup|founder|entrepreneur|ceo|cto|leadership)": "🚀",

    # Development
    r"(developer|engineer|coding|programming|software|debug(?:ging)?|code)": "👨‍💻",
    r"(frontend|backend|full[-\s]?stack|devops|api|rest|graphql)": "💻",
    r"(python|javascript|typescript|java|golang|rust|cpp|c\+\+)": "🐍",

    # Design & Creative
    r"(design(?:er)?|creative|art|ui|ux|figma|sketch|visual)": "🎨",
    r"(writer|writing|copy(?:writing)?|content|blog|article)": "✍️",
    r"(video|photo|image|media|editing|film)": "🎬",

    # Analytics & Data
    r"(analytic|data|metric|statistics|insight|report|dashboard)": "📊",
    r"(sql|database|query|etl|pipeline|warehouse)": "🗄️",
    r"(machine\s*learning|ml|ai|artificial\s*intelligence|model|training)": "🤖",

    # Communication
    r"(chat|support|communication|customer|service|help)": "💬",
    r"(email|newsletter|marketing|outreach|campaign)": "📧",

    # Education
    r"(teacher|education|learning|tutorial|course|mentor|coach)": "📚",
    r"(student|academic|research|paper|thesis|study)": "🎓",

    # Finance
    r"(finance|money|trading|investment|crypto|bitcoin|stock)": "💰",
    r"(accounting|budget|invoice|payment)": "💵",

    # Science & Research
    r"(science|research|lab|experiment|discovery|biology|chemistry)": "🔬",
    r"(math|physics|calculation|formula|equation)": "🧮",

    # Tools & Utilities
    r"(assistant|helper|copilot|aid|tool|utility)": "🤖",
    r"(automation|workflow|script|batch|process)": "⚙️",
    r"(security|privacy|encrypt|protect|auth)": "🔒",

    # Documents & Files
    r"(document|pdf|word|excel|spreadsheet|presentation)": "📄",
    r"(file|folder|directory|storage|backup|sync)": "📁",

    # Web & Internet
    r"(web|website|html|css|browser|internet|url|link)": "🌐",
    r"(seo|search|google|index|ranking)": "🔍",

    # General / Default
    r"(general|default|universal|common)": "🔧",
}

# Default emoji fallback
DEFAULT_EMOJI = "🔧"


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
    # ANSI color codes
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


def parse_yaml_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Extract YAML frontmatter from Markdown content.
    Simple parser that handles basic YAML structure.

    Returns:
        Tuple of (frontmatter_dict, full_content_with_frontmatter)
    """
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)

    if not frontmatter_match:
        return {}, content

    yaml_text = frontmatter_match.group(1)
    body = frontmatter_match.group(2)

    try:
        frontmatter = simple_yaml_parse(yaml_text)
        return frontmatter, f"---\n{yaml_text}\n---\n\n{body}".strip()
    except Exception:
        return {}, content


def simple_yaml_parse(text: str) -> Dict[str, Any]:
    """
    Simple YAML parser for basic frontmatter.
    Handles key-value pairs, lists, and basic nested structures.

    This is a basic implementation that covers common frontmatter cases
    without requiring the pyyaml library.
    """
    result: Dict[str, Any] = {}
    lines = text.split("\n")

    for line in lines:
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Check for key-value pair
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if not value:
                # Empty value, skip
                continue
            elif value.startswith('"') and value.endswith('"'):
                # Quoted string
                result[key] = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                # Single quoted string
                result[key] = value[1:-1]
            elif value.lower() == "true":
                result[key] = True
            elif value.lower() == "false":
                result[key] = False
            elif value.isdigit():
                result[key] = int(value)
            else:
                # String value (may have trailing comment)
                if "#" in value:
                    value = value.split("#")[0].strip()
                result[key] = value

        # Check for list item (indented with -)
        elif stripped.startswith("- ") and "|" not in stripped:
            # Find the key this list belongs to
            # Look at previous line to determine the key
            value = stripped[2:].strip().strip('"').strip("'")
            # For simple frontmatter, we'll just skip list items
            # as they're less common for basic use cases
            pass

    # Handle multi-line lists (categories, tags)
    # Parse lines starting with "- " that follow certain keys
    current_key = None
    result_with_lists: Dict[str, Any] = {}

    for line in lines:
        stripped = line.strip()

        if ":" in line and not line.startswith(" "):
            # Top-level key
            key = line.split(":", 1)[0].strip()
            current_key = key
            result_with_lists[key] = None
        elif current_key and stripped.startswith("- "):
            # List item
            value = stripped[2:].strip().strip('"').strip("'")
            if result_with_lists[current_key] is None:
                result_with_lists[current_key] = [value]
            else:
                if isinstance(result_with_lists[current_key], list):
                    result_with_lists[current_key].append(value)
        elif current_key and result_with_lists[current_key] is None:
            # Single value for key
            if ":" in line:
                value = line.split(":", 1)[1].strip().strip('"').strip("'")
                result_with_lists[current_key] = value

    # Merge results, preferring the list-aware version
    for key, value in result_with_lists.items():
        if value is not None:
            result[key] = value

    return result


def generate_emoji(description: str, filename: str) -> str:
    """Generate emoji based on semantic understanding of description."""
    text_to_analyze = (description or "" + " " + filename).lower()

    for pattern, emoji in EMOJI_PATTERNS.items():
        if re.search(pattern, text_to_analyze):
            return emoji

    return DEFAULT_EMOJI


def normalize_category(category: Any) -> List[str]:
    """Normalize category to array format."""
    if category is None:
        return ["General"]

    if isinstance(category, str):
        return [category]

    if isinstance(category, list):
        return [str(c) for c in category if c]

    return ["General"]


def compile_file(file_path: Path, errors: List[str], warnings: List[str]) -> Optional[Dict[str, Any]]:
    """
    Compile a single Markdown file to CherryStudio JSON format.

    Returns:
        Dictionary with compiled prompt data, or None if compilation failed.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(f"Failed to read {file_path.name}: {e}")
        return None

    frontmatter, full_content = parse_yaml_frontmatter(content)

    # Extract fields with defaults
    description = frontmatter.get("description", "")
    category = frontmatter.get("category", frontmatter.get("group"))
    group = normalize_category(category)

    # Generate emoji
    emoji = frontmatter.get("emoji") or generate_emoji(description, file_path.stem)

    return {
        "id": "",  # Will be assigned during batch processing
        "name": file_path.stem,
        "description": description,
        "emoji": emoji,
        "group": group,
        "prompt": full_content,
    }


def compile_directory(input_dir: Path, recursive: bool = True) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
    """
    Compile all Markdown files in a directory.

    Returns:
        Tuple of (compiled_prompts, errors, warnings)
    """
    pattern = "**/*.md" if recursive else "*.md"
    md_files = sorted(input_dir.glob(pattern))

    if not md_files:
        return [], [], []

    compiled_prompts = []
    errors = []
    warnings = []

    print(f"\nCompiling {len(md_files)} prompt(s)...\n")

    for i, md_file in enumerate(md_files, 1):
        if not md_file.is_file():
            continue

        print(f"[{i}/{len(md_files)}] {md_file.name}...", end=" ")

        prompt = compile_file(md_file, errors, warnings)
        if prompt:
            compiled_prompts.append(prompt)
            print_color("OK", "green")
        else:
            print_color("FAILED", "red")

    # Assign sequential IDs
    for idx, prompt in enumerate(compiled_prompts, 1):
        prompt["id"] = str(idx)

    return compiled_prompts, errors, warnings


def main():
    # Enable ANSI colors on Windows
    enable_ansi_colors()

    parser = argparse.ArgumentParser(
        description="Compile Markdown prompts to CherryStudio JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./prompts/
  %(prog)s ./prompts/ output.json
  %(prog)s ./prompts/ --no-recursive
        """,
    )
    parser.add_argument("input_dir", type=str, help="Directory containing Markdown files")
    parser.add_argument(
        "output_file",
        type=str,
        nargs="?",
        default="cherry-studio-prompts.json",
        help="Output JSON file (default: cherry-studio-prompts.json)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Do not search subdirectories recursively",
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        print_color(f"Error: {input_dir} is not a directory", "red")
        sys.exit(1)

    output_file = Path(args.output_file)

    # Print header
    print_color("CherryStudio Prompt Compiler", "bold")
    print(f"Compiling prompts from {input_dir}")

    # Compile
    prompts, errors, warnings = compile_directory(input_dir, recursive=not args.no_recursive)

    if not prompts:
        print_color("\nNo prompts compiled. Exiting.", "red")
        sys.exit(1)

    # Write output
    output_file.write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")

    # Print summary
    print_header("Compilation Summary")
    print(f"Prompts compiled: {len(prompts)}")
    print(f"Output file: {output_file}")

    if errors:
        print_color(f"\nErrors ({len(errors)}):", "red")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print_color(f"\nWarnings ({len(warnings)}):", "yellow")
        for w in warnings:
            print(f"  - {w}")

    if len(prompts) > 0 and not errors:
        print_color(f"\nSuccessfully compiled {len(prompts)} prompt(s)!", "green")


if __name__ == "__main__":
    main()
