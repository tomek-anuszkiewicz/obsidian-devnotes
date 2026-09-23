#!/usr/bin/env python3
"""
scripts/check_paths.py

Detects and repairs machine-specific absolute file paths and file protocol URIs
in Obsidian vault markdown files.
Enforces .agents/rules/no-absolute-paths.md.

Usage:
  python scripts/check_paths.py [file_path ...]
  python scripts/check_paths.py --git
  python scripts/check_paths.py --vault
  python scripts/check_paths.py --vault --fix
  python scripts/check_paths.py --vault --fix --dry-run
"""

import sys
import os
import re
import argparse
import subprocess
import urllib.parse
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

REPO_ROOT = Path(__file__).resolve().parent.parent

EXCLUDED_DIRS = {
    ".git",
    ".system_generated",
    "__pycache__",
    ".pytest_cache",
    ".vscode",
    ".idea",
}

# Regex to detect file protocol URIs (e.g., file:///C:/path or file:///d:/path)
FILE_URI_PATTERN = re.compile(
    r"file://(?:localhost)?/?[A-Za-z]:/[^\s\)\]\}\>\"']+|file://(?:localhost)?/[^\s\)\]\}\>\"']+",
    re.IGNORECASE,
)

# Windows drive paths (e.g., C:\..., D:/...)
WIN_DRIVE_PATTERN = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z]:[\\/][^\s\)\]\}\>\"',;]+)")

# Unix user home absolute paths (e.g. /home/user or /Users/user)
UNIX_HOST_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])(/(?:home|Users|private)/[^\s\)\]\}\>\"',;]+)"
)

# Markdown link: [text](target) or ![alt](target) - supports paths with spaces inside parens
MD_LINK_PATTERN = re.compile(
    r"(!?\[([^\]]*)\])\((<[^>]+>|[^)\n]+)\)"
)

# Obsidian wikilink: [[target]] or [[target|label]]
WIKILINK_PATTERN = re.compile(r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]")

# Known synthetic placeholders in explanatory anti-pattern text
ILLUSTRATIVE_SUBSTRINGS = [
    "...",
    "c:\\users\\username",
    "c:/users/username",
    "c:\\users\\runner",
    "c:/users/runner",
    "/home/developer",
    "c:\\users\\",
    "c:/users/",
    "`/home/`",
    "`c:\\users\\`",
    "<username>",
    "<user>",
]


def is_excluded(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(REPO_ROOT)
        for part in rel.parts:
            if part in EXCLUDED_DIRS:
                return True
    except ValueError:
        pass
    return False


def get_git_staged_files() -> list[Path]:
    try:
        output = subprocess.check_output(
            ["git", "diff", "--name-only", "--cached", "--diff-filter=ACMR"],
            cwd=REPO_ROOT,
            text=True,
        )
        files = []
        for line in output.splitlines():
            line = line.strip()
            if line.endswith(".md"):
                p = (REPO_ROOT / line).resolve()
                if p.is_file() and not is_excluded(p):
                    files.append(p)
        return files
    except Exception as e:
        print(f"[WARN] Failed to get git staged files: {e}", file=sys.stderr)
        return []


def get_all_vault_files() -> list[Path]:
    files = []
    for p in REPO_ROOT.rglob("*.md"):
        if p.is_file() and not is_excluded(p):
            files.append(p)
    return sorted(files)


def normalize_target_path(target: str) -> str:
    """Strips file:// and decodes URL encoding."""
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()

    # Strip optional trailing link title e.g. "title"
    m_title = re.match(r'^(.*?)\s+["\'].*?["\']$', target)
    if m_title:
        target = m_title.group(1).strip()

    if target.lower().startswith("file:///"):
        path_part = target[8:]
        if len(path_part) >= 3 and path_part[1] == ":" and (path_part[2] == "/" or path_part[2] == "\\"):
            target = path_part
        elif len(path_part) >= 2 and path_part[0] == "/" and path_part[2] == ":":
            target = path_part[1:]
        else:
            target = "/" + path_part.lstrip("/")
        target = urllib.parse.unquote(target)
    elif target.lower().startswith("file://"):
        target = urllib.parse.unquote(target[7:])

    return target


def is_absolute_target(target: str) -> bool:
    """Checks if target is an absolute filesystem path or file:// URI."""
    clean = target.strip()
    if clean.startswith("<") and clean.endswith(">"):
        clean = clean[1:-1].strip()
    m_title = re.match(r'^(.*?)\s+["\'].*?["\']$', clean)
    if m_title:
        clean = m_title.group(1).strip()

    if clean.lower().startswith("file://"):
        return True
    if re.match(r"^[A-Za-z]:[\\/]", clean):
        return True
    if clean.startswith(r"\\"):  # UNC path
        return True
    if re.match(r"^/(?:home|Users|private|tmp|var|opt)/", clean):
        return True
    return False


def resolve_vault_path(target_path_str: str) -> Path | None:
    """Attempts to resolve target_path_str to a Path inside REPO_ROOT."""
    clean = normalize_target_path(target_path_str)
    base_target = clean.split("#")[0]
    try:
        p = Path(base_target).resolve()
        p.relative_to(REPO_ROOT)
        return p
    except (ValueError, OSError):
        try:
            repo_str = str(REPO_ROOT).replace("\\", "/").lower()
            clean_str = clean.replace("\\", "/").lower()
            if clean_str.startswith(repo_str):
                sub = clean[len(repo_str):].lstrip("/\\")
                resolved = (REPO_ROOT / sub).resolve()
                return resolved
        except Exception:
            pass
    return None


def target_to_wikilink_or_rel(current_file: Path, target_str: str, link_text: str, is_image: bool) -> str | None:
    """
    Given an absolute link target, determines the portable replacement (wikilink or relative path).
    """
    clean = normalize_target_path(target_str)
    anchor = ""
    if "#" in clean:
        parts = clean.split("#", 1)
        clean = parts[0]
        anchor = "#" + parts[1]

    resolved_path = resolve_vault_path(clean)
    if not resolved_path:
        return None

    if resolved_path.suffix.lower() == ".md":
        note_name = resolved_path.stem
        target_ref = f"{note_name}{anchor}"
        if is_image:
            return f"![[{target_ref}]]"
        if not link_text or link_text.strip() == note_name:
            return f"[[{target_ref}]]"
        else:
            return f"[[{target_ref}|{link_text}]]"
    else:
        # Non-markdown asset (e.g. image, script)
        if is_image:
            return f"![[{resolved_path.name}]]"
        try:
            rel = os.path.relpath(resolved_path, current_file.parent)
            rel_forward = rel.replace("\\", "/")
            return f"[{link_text}]({rel_forward}{anchor})"
        except ValueError:
            return None


class Violation:
    def __init__(self, line_num: int, line_content: str, raw_match: str, fix_suggestion: str | None = None, is_link: bool = False):
        self.line_num = line_num
        self.line_content = line_content
        self.raw_match = raw_match
        self.fix_suggestion = fix_suggestion
        self.is_link = is_link


def is_illustrative_example(text: str) -> bool:
    lower = text.lower()
    for pattern in ILLUSTRATIVE_SUBSTRINGS:
        if pattern in lower:
            return True
    return False


def scan_and_repair_content(content: str, file_path: Path, check_code_blocks: bool = False) -> tuple[list[Violation], str]:
    """
    Scans content for absolute paths. If possible, computes replacements.
    Returns (violations, repaired_content).
    """
    lines = content.split("\n")
    violations: list[Violation] = []
    repaired_lines = []

    in_fence = False
    fence_delimiter = ""

    repo_str_forward = str(REPO_ROOT).replace("\\", "/")
    repo_str_backward = str(REPO_ROOT).replace("/", "\\")

    for idx, line in enumerate(lines):
        line_num = idx + 1
        stripped = line.strip()

        # Track fenced code blocks
        if stripped.startswith("```") or stripped.startswith("~~~"):
            delim = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_delimiter = delim
            elif stripped.startswith(fence_delimiter):
                in_fence = False
                fence_delimiter = ""
            repaired_lines.append(line)
            continue

        # In-line suppressions
        if "<!-- ignore-path -->" in line or "<!-- allow-path -->" in line:
            repaired_lines.append(line)
            continue

        # If inside code blocks, only check if explicitly requested or if it leaks REPO_ROOT
        if in_fence and not check_code_blocks:
            if repo_str_forward.lower() in line.lower() or repo_str_backward.lower() in line.lower():
                v = Violation(line_num, line, str(REPO_ROOT), None, False)
                violations.append(v)
            repaired_lines.append(line)
            continue

        repaired_line = line

        # 1. Check Markdown links [text](target) and ![alt](target)
        def replace_md_link(match):
            nonlocal line_num, line
            full_match = match.group(0)
            prefix = match.group(1)
            link_text = match.group(2)
            raw_target = match.group(3).strip()
            is_image = prefix.startswith("!")

            if is_absolute_target(raw_target):
                replacement = target_to_wikilink_or_rel(file_path, raw_target, link_text, is_image)
                violations.append(Violation(line_num, line, full_match, replacement, True))
                if replacement:
                    return replacement
            return full_match

        repaired_line = MD_LINK_PATTERN.sub(replace_md_link, repaired_line)

        # 2. Check Obsidian wikilinks [[target]]
        def check_wikilink(match):
            nonlocal line_num, line
            full_match = match.group(0)
            target = match.group(1).strip()
            label = match.group(2) or ""
            if is_absolute_target(target):
                resolved = resolve_vault_path(target)
                if resolved and resolved.suffix.lower() == ".md":
                    note_name = resolved.stem
                    rep = f"[[{note_name}|{label}]]" if label and label != note_name else f"[[{note_name}]]"
                    violations.append(Violation(line_num, line, full_match, rep, True))
                    return rep
                violations.append(Violation(line_num, line, full_match, None, True))
            return full_match

        repaired_line = WIKILINK_PATTERN.sub(check_wikilink, repaired_line)

        # 3. Check raw REPO_ROOT references in prose outside links
        for repo_prefix in [repo_str_forward, repo_str_backward]:
            if repo_prefix.lower() in repaired_line.lower():
                pattern = re.compile(re.escape(repo_prefix) + r"([\\/][^\s\)\]\}\>\"',;]*)?", re.IGNORECASE)
                def replace_repo_root(m):
                    nonlocal line_num, line
                    full_p = m.group(0)
                    sub_p = m.group(1) or ""
                    clean_sub = sub_p.replace("\\", "/").lstrip("/")
                    rep = clean_sub if clean_sub else "."
                    violations.append(Violation(line_num, line, full_p, rep, False))
                    return rep
                repaired_line = pattern.sub(replace_repo_root, repaired_line)

        # 4. Check for standalone file:// URIs not caught by links
        for m in FILE_URI_PATTERN.finditer(repaired_line):
            uri = m.group(0)
            if is_illustrative_example(uri) or is_illustrative_example(repaired_line):
                continue
            if any(v.raw_match == uri for v in violations):
                continue
            resolved = resolve_vault_path(uri)
            rep = None
            if resolved:
                if resolved.suffix.lower() == ".md":
                    rep = f"[[{resolved.stem}]]"
                else:
                    rel = os.path.relpath(resolved, file_path.parent).replace("\\", "/")
                    rep = rel
            violations.append(Violation(line_num, line, uri, rep, False))
            if rep:
                repaired_line = repaired_line.replace(uri, rep)

        # 5. Check for standalone Windows drive paths (outside links & illustrative examples)
        if not in_fence:
            for m in WIN_DRIVE_PATTERN.finditer(repaired_line):
                val = m.group(1)
                if is_illustrative_example(val) or is_illustrative_example(repaired_line):
                    continue
                if any(v.raw_match == val for v in violations):
                    continue
                resolved = resolve_vault_path(val)
                rep = None
                if resolved:
                    if resolved.suffix.lower() == ".md":
                        rep = f"[[{resolved.stem}]]"
                    else:
                        rep = os.path.relpath(resolved, file_path.parent).replace("\\", "/")
                violations.append(Violation(line_num, line, val, rep, False))
                if rep:
                    repaired_line = repaired_line.replace(val, rep)

        # 6. Check for standalone Unix host paths (outside links & illustrative examples)
        if not in_fence:
            for m in UNIX_HOST_PATTERN.finditer(repaired_line):
                val = m.group(1)
                if is_illustrative_example(val) or is_illustrative_example(repaired_line):
                    continue
                if any(v.raw_match == val for v in violations):
                    continue
                violations.append(Violation(line_num, line, val, None, False))

        repaired_lines.append(repaired_line)

    return violations, "\n".join(repaired_lines)


def process_file(file_path: Path, fix: bool = False, dry_run: bool = False, check_code_blocks: bool = False) -> tuple[int, int]:
    """
    Processes a single file.
    Returns (num_violations, num_fixes).
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"[ERROR] Unable to read {file_path}: {e}", file=sys.stderr)
        return 1, 0

    violations, repaired_content = scan_and_repair_content(content, file_path, check_code_blocks)

    rel_path = file_path.relative_to(REPO_ROOT) if file_path.is_relative_to(REPO_ROOT) else file_path

    if not violations:
        return 0, 0

    fixable = [v for v in violations if v.fix_suggestion is not None]

    print(f"[FAIL] {rel_path} ({len(violations)} violation(s))")
    for v in violations:
        fix_note = f" -> fix: {v.fix_suggestion}" if v.fix_suggestion else " (manual fix required)"
        print(f"       L{v.line_num}: `{v.raw_match}`{fix_note}")

    if fix and content != repaired_content:
        if dry_run:
            print(f"       [DRY-RUN] Would fix {len(fixable)} occurrence(s).")
        else:
            try:
                file_path.write_text(repaired_content, encoding="utf-8")
                print(f"       [FIXED] Applied {len(fixable)} replacement(s).")
            except Exception as e:
                print(f"       [ERROR] Failed to write changes: {e}", file=sys.stderr)

    return len(violations), len(fixable)


def main():
    parser = argparse.ArgumentParser(
        description="Detect and repair machine-specific absolute file paths and file URIs in vault notes."
    )
    parser.add_argument("files", nargs="*", help="Specific markdown file(s) to check")
    parser.add_argument("--git", action="store_true", help="Check git staged markdown files")
    parser.add_argument("--vault", action="store_true", help="Scan all markdown files in vault")
    parser.add_argument("--fix", action="store_true", help="Automatically repair resolvable absolute paths")
    parser.add_argument("--dry-run", action="store_true", help="Preview fixes without modifying files")
    parser.add_argument("--check-code-blocks", action="store_true", help="Also scan inside fenced code blocks")

    args = parser.parse_args()

    target_files = []
    if args.git:
        target_files = get_git_staged_files()
        if not target_files:
            print("[INFO] No staged markdown files found to check.")
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
    files_with_violations = 0
    total_violations = 0
    total_fixed = 0

    for file_path in target_files:
        v_count, f_count = process_file(file_path, fix=args.fix, dry_run=args.dry_run, check_code_blocks=args.check_code_blocks)
        if v_count > 0:
            files_with_violations += 1
            total_violations += v_count
            total_fixed += f_count

    print("\n----------------------------------------")
    if files_with_violations == 0:
        print(f"[CLEAN] All {total_files} file(s) passed absolute path check.")
        sys.exit(0)
    else:
        if args.fix and not args.dry_run and total_fixed == total_violations:
            print(f"[RESOLVED] Fixed {total_fixed} violation(s) across {files_with_violations} file(s).")
            sys.exit(0)
        print(f"[VIOLATIONS] Found {total_violations} violation(s) across {files_with_violations} of {total_files} file(s).")
        sys.exit(1)


if __name__ == "__main__":
    main()
