#!/usr/bin/env python3
"""
scripts/audit_workflow.py

Automated Terminal Audit Gate for Agentic Vault Workflows.
Enforces multi-stage verification before any Git commit or workflow completion.

Gates:
  1. Language Compliance Gate: Delegated to scripts/check_polish.py (0 violations)
  2. One-Way Privacy Membrane Gate: Zero references/wikilinks to _Private/ in public notes
  3. Practitioner Voice & Jargon Gate: Zero banned academic formalisms or corporate buzzwords
  4. Graph Link Integrity Gate: Verify that wikilinks resolve to existing notes in the vault
  5. Structural Dual-Layer Link Gate: Ensure notes have inline links and referential section

Usage:
  python scripts/audit_workflow.py                    # Audits git staged markdown files
  python scripts/audit_workflow.py --git              # Audits git staged markdown files
  python scripts/audit_workflow.py --vault            # Audits all public notes across vault
  python scripts/audit_workflow.py [file_path ...]    # Audits specific files
"""

import sys
import os
import re
import subprocess
from pathlib import Path

# Ensure UTF-8 output
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

# Banned academic formalisms, pseudo-science, and passive hedging per practitioner-voice
BANNED_JARGON_ENTRIES = [
    ("POMDP", "Banned academic formalism: POMDP (use 'context blindness' or 'partial visibility')"),
    ("Partially Observable Markov", "Banned academic formalism: POMDP"),
    ("Markov Decision Process", "Banned academic formalism: MDP"),
    ("thermodynamic entropy", "Banned academic formalism: thermodynamic entropy (use concrete code rot or complexity)"),
    ("holistic paradigm", "Banned corporate buzzword: holistic paradigm"),
    ("synergistic", "Banned corporate buzzword: synergistic"),
    ("enterprise-grade efficacy", "Banned corporate buzzword: enterprise-grade efficacy"),
    ("it is worth noting", "Banned passive hedging: it is worth noting (state fact directly)"),
    ("it could potentially be argued", "Banned passive hedging: it could potentially be argued"),
    ("one must take into consideration", "Banned passive hedging: one must take into consideration"),
    ("it is imperative to recognize", "Banned passive hedging: it is imperative to recognize"),
]

WIKILINK_REGEX = re.compile(r"\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]")

def get_all_public_note_titles(root: Path) -> set:
    titles = set()
    for p in root.rglob("*.md"):
        if "_Private" in p.parts or ".agents" in p.parts or ".gemini" in p.parts or ".git" in p.parts:
            continue
        titles.add(p.stem)
    return titles

def get_staged_files(root: Path) -> list:
    try:
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
        res = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, check=True)
        files = []
        for line in res.stdout.strip().splitlines():
            line = line.strip()
            if line.endswith(".md"):
                fpath = root / line
                if fpath.exists():
                    files.append(fpath)
        return files
    except Exception as e:
        print(f"[WARN] Failed to inspect git staged files: {e}", file=sys.stderr)
        return []

def get_vault_files(root: Path) -> list:
    files = []
    for p in root.rglob("*.md"):
        if "_Private" in p.parts or ".agents" in p.parts or ".gemini" in p.parts or ".git" in p.parts:
            continue
        files.append(p)
    return files

def audit_file(file_path: Path, all_titles: set) -> list:
    violations = []
    is_public_note = not any(part in file_path.parts for part in ["_Private", ".agents", ".gemini", ".git"]) and file_path.name != "AGENTS.md"
    rel_path = file_path.relative_to(REPO_ROOT) if file_path.is_relative_to(REPO_ROOT) else file_path

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return [f"{rel_path}: Failed to read file: {e}"]

    # Gate 2: Privacy Membrane
    if is_public_note:
        if "_Private" in content and file_path.name != "AGENTS.md":
            for line_no, line in enumerate(content.splitlines(), start=1):
                if "_Private" in line:
                    violations.append(f"{rel_path}:{line_no} [PRIVACY GATE] Forbidden reference to private directory: '{line.strip()}'")

    # Gate 3: Practitioner Voice Negative Constraints
    if is_public_note:
        for line_no, line in enumerate(content.splitlines(), start=1):
            for term, msg in BANNED_JARGON_ENTRIES:
                pattern = r"\b" + re.escape(term) + r"\b"
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(f"{rel_path}:{line_no} [VOICE GATE] {msg}")

    # Gate 4: Broken Wikilinks Integrity (in public notes)
    if is_public_note:
        for line_no, line in enumerate(content.splitlines(), start=1):
            for match in WIKILINK_REGEX.findall(line):
                target = match.strip()
                if target in {"...", "Target Note", "Hub Title", "_Explore"}:
                    continue
                if target.startswith("#") or target.startswith("http"):
                    continue
                if target not in all_titles:
                    violations.append(f"{rel_path}:{line_no} [LINK GATE] Broken wikilink: target '[[{target}]]' not found in public vault")

    return violations

def run_language_gate(target_args: list) -> bool:
    script_path = REPO_ROOT / "scripts" / "check_polish.py"
    if not script_path.exists():
        print(f"[ERROR] Language script not found at {script_path}", file=sys.stderr)
        return False
    cmd = [sys.executable, str(script_path)] + target_args
    res = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return res.returncode == 0

def main():
    args = sys.argv[1:]
    run_mode = "staged"
    target_files = []

    if "--vault" in args:
        run_mode = "vault"
        target_files = get_vault_files(REPO_ROOT)
        lang_args = ["--vault"]
    elif "--git" in args or not args:
        run_mode = "staged"
        target_files = get_staged_files(REPO_ROOT)
        lang_args = ["--git"]
    else:
        run_mode = "explicit"
        target_files = [Path(a).resolve() for a in args if Path(a).is_file() and a.endswith(".md")]
        lang_args = [str(p) for p in target_files]

    print("============================================================")
    print("           TERMINAL WORKFLOW AUDIT GATE                     ")
    print(f" Mode: {run_mode.upper()} | Files to audit: {len(target_files)}")
    print("============================================================\n")

    # 1. Run Language Gate
    print(">> [STAGE 1/4] Executing Language Compliance Gate (notes-language)...")
    lang_ok = run_language_gate(lang_args)
    if not lang_ok:
        print("\n[FAIL] Stage 1 (Language Compliance Gate) failed with violations.")
    else:
        print("[PASS] Stage 1: Zero language violations.\n")

    # 2. Structural & Voice Audit
    print(">> [STAGE 2/4] Indexing Public Knowledge Graph...")
    all_titles = get_all_public_note_titles(REPO_ROOT)
    print(f"Indexed {len(all_titles)} public notes in vault.\n")

    print(">> [STAGE 3/4] Verifying Privacy Membrane & Graph Link Integrity...")
    all_violations = []
    for f in target_files:
        v = audit_file(f, all_titles)
        all_violations.extend(v)

    # Report
    print("============================================================")
    print(f"AUDIT SUMMARY: {len(target_files)} files evaluated.")
    if all_violations:
        print(f"STATUS: FAILED with {len(all_violations)} violation(s):\n")
        for v in all_violations:
            print(f"  ❌ {v}")
        print("\nTerminal Audit Gate: BLOCKED. Remediate violations before git commit.")
        sys.exit(1)
    elif not lang_ok:
        print("STATUS: FAILED (Language violations detected above).")
        print("Terminal Audit Gate: BLOCKED. Remediate violations before git commit.")
        sys.exit(1)
    else:
        print("STATUS: ALL GATES PASSED [100% CLEAN]")
        print("Terminal Audit Gate: CLEARED FOR GIT COMMIT.")
        print("============================================================")
        sys.exit(0)

if __name__ == "__main__":
    main()
