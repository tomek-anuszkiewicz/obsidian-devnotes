#!/usr/bin/env python3
"""
scripts/check_frontmatter.py

Validates Obsidian YAML frontmatter (properties) at the top of vault markdown notes.
Ensures every note begins with valid YAML frontmatter containing:
  - title: non-empty string
  - tags: list of kebab-case strings
  - aliases: list of non-empty strings

Usage:
  python scripts/check_frontmatter.py [file_path ...]
  python scripts/check_frontmatter.py --git
  python scripts/check_frontmatter.py --vault
"""

import sys
import os
import re
import argparse
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files/directories to exclude from vault frontmatter validation
EXCLUDED_PATTERNS = [
    ".git",
    ".agents",
    ".system_generated",
    "scripts",
    "TODO.md",
    "AGENTS.md",
    "GEMINI.md",
]

KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def is_excluded(path: Path) -> bool:
    rel_parts = path.resolve().relative_to(REPO_ROOT).parts
    for part in rel_parts:
        if part in EXCLUDED_PATTERNS:
            return True
    return False


def validate_note_frontmatter(file_path: Path) -> list[str]:
    """Validates the frontmatter of a markdown file. Returns list of error messages."""
    errors = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return [f"Unable to read file: {e}"]

    lines = content.splitlines()
    if not lines:
        return ["File is empty"]

    if lines[0].strip() != "---":
        return ["Note does not start with YAML frontmatter delimiter '---' at line 1"]

    # Find closing delimiter
    closing_idx = -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            closing_idx = idx
            break

    if closing_idx == -1:
        return ["Unclosed YAML frontmatter: missing closing '---'"]

    yaml_text = "\n".join(lines[1:closing_idx])
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        return [f"YAML parsing error: {e}"]

    if not isinstance(data, dict):
        return ["Frontmatter is not a YAML mapping / dictionary"]

    # Check title
    title = data.get("title")
    if title is None:
        errors.append("Missing required property: 'title'")
    elif not isinstance(title, str) or not title.strip():
        errors.append("Property 'title' must be a non-empty string")

    # Check tags
    tags = data.get("tags")
    if tags is None:
        errors.append("Missing required property: 'tags'")
    elif not isinstance(tags, list):
        errors.append("Property 'tags' must be a list of strings")
    elif len(tags) == 0:
        errors.append("Property 'tags' list is empty")
    else:
        for tag in tags:
            tag_str = str(tag).strip()
            if not tag_str:
                errors.append("Empty tag entry in 'tags'")
            elif not KEBAB_CASE_RE.match(tag_str):
                errors.append(f"Tag '{tag_str}' is not valid kebab-case (use lowercase and hyphens)")

    # Check aliases
    aliases = data.get("aliases")
    if aliases is None:
        errors.append("Missing required property: 'aliases'")
    elif not isinstance(aliases, list):
        errors.append("Property 'aliases' must be a list of strings")
    elif len(aliases) == 0:
        errors.append("Property 'aliases' list is empty")
    else:
        for alias in aliases:
            if not isinstance(alias, (str, int, float)) or not str(alias).strip():
                errors.append("Empty or invalid alias entry in 'aliases'")

    return errors


def get_git_staged_files() -> list[Path]:
    try:
        res = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        files = []
        for line in res.stdout.splitlines():
            line = line.strip()
            if line.endswith(".md"):
                p = REPO_ROOT / line
                if p.is_file() and not is_excluded(p):
                    files.append(p)
        return files
    except Exception as e:
        print(f"Error checking git staged files: {e}", file=sys.stderr)
        return []


def get_all_vault_files() -> list[Path]:
    files = []
    for p in REPO_ROOT.rglob("*.md"):
        if p.is_file() and not is_excluded(p):
            files.append(p)
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description="Validate Obsidian YAML frontmatter properties.")
    parser.add_argument("files", nargs="*", help="Specific files to validate")
    parser.add_argument("--git", action="store_true", help="Validate git staged markdown files")
    parser.add_argument("--vault", action="store_true", help="Validate all markdown files in the vault")

    args = parser.parse_args()

    target_files = []
    if args.git:
        target_files = get_git_staged_files()
        if not target_files:
            print("[INFO] No staged markdown notes found to check.")
            sys.exit(0)
    elif args.vault:
        target_files = get_all_vault_files()
    elif args.files:
        for f in args.files:
            p = Path(f).resolve()
            if p.is_file():
                target_files.append(p)
            else:
                print(f"[WARN] File not found: {f}", file=sys.stderr)
    else:
        parser.print_help()
        sys.exit(0)

    total_files = len(target_files)
    failed_files = 0

    for file_path in target_files:
        rel_path = file_path.relative_to(REPO_ROOT) if file_path.is_relative_to(REPO_ROOT) else file_path
        errors = validate_note_frontmatter(file_path)
        if errors:
            failed_files += 1
            print(f"[FAIL] {rel_path}")
            for err in errors:
                print(f"       - {err}")
        else:
            # Verbose success can be printed if single file or few files
            if total_files <= 5:
                print(f"[PASS] {rel_path}")

    print("\n----------------------------------------")
    if failed_files == 0:
        print(f"[CLEAN] All {total_files} file(s) passed frontmatter validation.")
        sys.exit(0)
    else:
        print(f"[VIOLATIONS] {failed_files} of {total_files} file(s) failed frontmatter validation.")
        sys.exit(1)


if __name__ == "__main__":
    main()
