#!/usr/bin/env python3
"""
scripts/audit_workflow.py

Checks changed public Markdown for the vault boundaries that can be verified
mechanically: English-only persistence and resolvable public wikilinks.

Usage:
  python scripts/audit_workflow.py                    # Audits staged Markdown files
  python scripts/audit_workflow.py --git              # Audits staged Markdown files
  python scripts/audit_workflow.py --vault            # Audits public Markdown files
  python scripts/audit_workflow.py [file_path ...]    # Audits specific Markdown files
"""

import re
import subprocess
import sys
from pathlib import Path

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
WIKILINK_REGEX = re.compile(r"\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]")


def is_public_markdown(path: Path) -> bool:
    return (
        path.suffix.lower() == ".md"
        and not any(part in path.parts for part in {".agents", ".gemini", ".git"})
        and path.name != "AGENTS.md"
    )


def get_all_public_note_titles(root: Path) -> set:
    return {path.stem for path in root.rglob("*.md") if is_public_markdown(path)}


def get_staged_files(root: Path) -> list:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception as error:
        print(f"[WARN] Could not inspect staged files: {error}", file=sys.stderr)
        return []

    files = []
    for name in result.stdout.splitlines():
        path = root / name.strip()
        if path.exists() and is_public_markdown(path):
            files.append(path)
    return files


def get_vault_files(root: Path) -> list:
    return [path for path in root.rglob("*.md") if is_public_markdown(path)]


def audit_file(file_path: Path, all_titles: set) -> list:
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as error:
        return [f"{file_path}: Failed to read file: {error}"]

    try:
        relative_path = file_path.relative_to(REPO_ROOT)
    except ValueError:
        relative_path = file_path

    violations = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        for target in WIKILINK_REGEX.findall(line):
            target = target.strip()
            if target in {"...", "Target Note", "Hub Title", "_Explore"}:
                continue
            if target.startswith("#") or target.startswith("http"):
                continue
            if target not in all_titles:
                violations.append(
                    f"{relative_path}:{line_number} [LINK] Public wikilink target not found: [[{target}]]"
                )

    return violations


def run_language_check(target_args: list) -> bool:
    checker = REPO_ROOT / "scripts" / "check_polish.py"
    if not checker.exists():
        print(f"[ERROR] Language checker not found: {checker}", file=sys.stderr)
        return False
    result = subprocess.run([sys.executable, str(checker), *target_args], cwd=str(REPO_ROOT))
    return result.returncode == 0


def main() -> int:
    args = sys.argv[1:]
    if "--vault" in args:
        mode = "vault"
        target_files = get_vault_files(REPO_ROOT)
        language_args = ["--vault"]
    elif "--git" in args or not args:
        mode = "staged"
        target_files = get_staged_files(REPO_ROOT)
        language_args = ["--git"]
    else:
        mode = "explicit"
        target_files = [Path(arg).resolve() for arg in args if Path(arg).is_file()]
        target_files = [path for path in target_files if is_public_markdown(path)]
        language_args = [str(path) for path in target_files]

    print(f"Public Markdown Audit ({mode}): {len(target_files)} file(s)")
    language_ok = run_language_check(language_args)
    titles = get_all_public_note_titles(REPO_ROOT)

    violations = []
    for path in target_files:
        violations.extend(audit_file(path, titles))

    if not language_ok:
        print("[FAIL] Language check failed.")
    if violations:
        for violation in violations:
            print(f"[FAIL] {violation}")

    if not language_ok or violations:
        return 1

    print("[PASS] Language, privacy, and public link checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
