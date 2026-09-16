#!/usr/bin/env python3
"""
scripts/check_practitioner_tone.py

Automated Quality Gate for Enforcing Practitioner Voice, Technical Tone,
and Grounded Nomenclature across Vault Notes, File Titles, and Directories.
Enforces .agents/rules/practitioner-voice-and-tone.md.

Checks:
  1. Directory Naming: Flags theatrical, mythical, or academic folder names.
  2. File Naming: Flags dissertation structures, neologisms, and stacked abstractions.
  3. Headings & Callouts: Flags academic labels (e.g. 'Executive Architectural Thesis',
     'Working Hypothesis', 'Central thesis', 'Core thesis').
  4. Academic Jargon: Flags banned high-register synthetic attractors
     ('epistemic', 'teleological', 'hermeneutic', 'desiderata', etc.).

Usage:
  python scripts/check_practitioner_tone.py           # Default vault audit
  python scripts/check_practitioner_tone.py --vault   # Explicit full vault audit
  python scripts/check_practitioner_tone.py --git     # Check staged files and directories
  python scripts/check_practitioner_tone.py [file ...] # Check specific files
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

REPO_ROOT = Path(__file__).resolve().parent.parent

EXCLUDED_DIRS = {
    ".git", ".obsidian", ".agents", ".vscode", "scripts", "_Private"
}

# 1. Directory Checks: Banned tokens in folder names
BANNED_DIRECTORY_PATTERNS = [
    (re.compile(r"\bironclad\b", re.IGNORECASE), "Theatrical neologism 'ironclad' in directory name"),
    (re.compile(r"\bThe Ironclad Oracle\b", re.IGNORECASE), "Theatrical folder name 'The Ironclad Oracle' (use 'Deterministic Test Oracles')"),
    (re.compile(r"\bModel Cognition\b", re.IGNORECASE), "Academic cognitive science 'Model Cognition' in directory name (use 'Context Architecture & Model Steering')"),
    (re.compile(r"\bLatent Space\b", re.IGNORECASE), "Academic math 'Latent Space' in directory name (use 'Context Architecture & Model Steering')"),
    (re.compile(r"\bOperator Psychology\b", re.IGNORECASE), "Academic department 'Operator Psychology' in directory name (use 'Developer Ergonomics & Software Economics')"),
    (re.compile(r"\bMacro-Economics\b", re.IGNORECASE), "Academic department 'Macro-Economics' in directory name (use 'Developer Ergonomics & Software Economics')"),
    (re.compile(r"\bSolution Spaces\b", re.IGNORECASE), "Academic math 'Solution Spaces' in directory name (use 'Context Windows & Attention')"),
    (re.compile(r"\bAutonomous Horizons\b", re.IGNORECASE), "Speculative essay title 'Autonomous Horizons' in directory name (use 'Autonomous Systems & Workflows')"),
    (re.compile(r"\bSemantic Telemetry\b", re.IGNORECASE), "Neologism 'Semantic Telemetry' in directory name (use 'Observability & Runtime Telemetry')"),
    (re.compile(r"\bIndustry Shifts & Moats\b", re.IGNORECASE), "Academic title 'Industry Shifts & Moats' in directory name (use 'Software Economics & Competitive Moats')"),
    (re.compile(r"\bepistemic\b", re.IGNORECASE), "Academic jargon 'epistemic' in directory name"),
    (re.compile(r"\bteleological\b", re.IGNORECASE), "Academic jargon 'teleological' in directory name"),
    (re.compile(r"\bsanctum\b", re.IGNORECASE), "Theatrical label 'sanctum' in directory name"),
    (re.compile(r"\bcitadel\b", re.IGNORECASE), "Theatrical label 'citadel' in directory name"),
]

# 2. File Name Checks: Academic / dissertation patterns in filenames
BANNED_FILENAME_PATTERNS = [
    (re.compile(r"\b(and the negative proof dilemma)\b", re.IGNORECASE), "Academic dissertation subtitle '...and the Negative Proof Dilemma'"),
    (re.compile(r"\b(zero-friction trap)\b", re.IGNORECASE), "Theatrical neologism 'Zero-Friction Trap'"),
    (re.compile(r"\b(crystallize insight)\b", re.IGNORECASE), "Synthetic academic phrase 'Crystallize Insight' in filename"),
    (re.compile(r"\b(civilizational automation loop)\b", re.IGNORECASE), "Speculative sci-fi title 'Civilizational Automation Loop' in filename"),
    (re.compile(r"\b(suppression of grassroots)\b", re.IGNORECASE), "Sociological dissertation phrasing in filename"),
    (re.compile(r"\b(stochastic foundations)\b", re.IGNORECASE), "Academic paper jargon 'Stochastic Foundations' in filename (use 'Unpredictable Models' or 'Unreliable Components')"),
    (re.compile(r"\b(probabilistic substrates?)\b", re.IGNORECASE), "Academic paper jargon 'Probabilistic Substrate' in filename (use 'Unpredictable Models')"),
    (re.compile(r"-\s\s+", re.IGNORECASE), "Double-space artifact around dash in filename"),
]

# 3. Heading & Callout Checks
BANNED_HEADING_PATTERNS = [
    (re.compile(r"^#+\s+.*(executive architectural thesis)", re.IGNORECASE), "Dissertation tag 'Executive Architectural Thesis' in heading"),
    (re.compile(r"^#+\s+.*(working hypothesis)\b", re.IGNORECASE), "Academic 'Working Hypothesis' in heading"),
    (re.compile(r"^#+\s+.*(central thesis)\b", re.IGNORECASE), "Academic 'Central thesis' in heading"),
    (re.compile(r"^#+\s+.*(final thesis)\b", re.IGNORECASE), "Academic 'Final Thesis' in heading"),
    (re.compile(r"^#+\s+.*(core thesis)\b", re.IGNORECASE), "Academic 'Core thesis' in heading (use direct descriptive title)"),
    (re.compile(r"^#+\s+.*(stochastic foundations)\b", re.IGNORECASE), "Paper jargon 'Stochastic Foundations' in heading (use 'Unpredictable Models')"),
    (re.compile(r"^#+\s+.*(mechanical autonomy flags)\b", re.IGNORECASE), "Cliché 'mechanical autonomy flags' in heading (use 'Runtime Autonomy Flags')"),
]

BANNED_CALLOUT_PATTERNS = [
    (re.compile(r"executive\s+architectural\s+thesis", re.IGNORECASE), "Academic callout label 'Executive Architectural Thesis'"),
]

# 4. Forbidden Synthetic Academic Jargon & Model Clichés in Body Text
BANNED_VOCABULARY_PATTERNS = [
    (re.compile(r"\b(epistemic)\b", re.IGNORECASE), "Synthetic academic attractor 'epistemic'"),
    (re.compile(r"\b(teleological)\b", re.IGNORECASE), "Synthetic academic attractor 'teleological'"),
    (re.compile(r"\b(ontological)\b", re.IGNORECASE), "Synthetic academic attractor 'ontological'"),
    (re.compile(r"\b(hermeneutic)\b", re.IGNORECASE), "Synthetic academic attractor 'hermeneutic'"),
    (re.compile(r"\b(desiderata)\b", re.IGNORECASE), "Academic Latinate 'desiderata'"),
    (re.compile(r"\b(mechanical exoskeleton)\b", re.IGNORECASE), "Model cliché 'mechanical exoskeleton' (use 'execution environment' or 'runtime harness')"),
    (re.compile(r"\b(mechanically imposed)\b", re.IGNORECASE), "Model cliché 'mechanically imposed' (use 'enforced programmatically')"),
    (re.compile(r"\b(mechanical sophistication)\b", re.IGNORECASE), "Model cliché 'mechanical sophistication' (use 'runtime architecture')"),
]


def is_excluded_path(p: Path) -> bool:
    try:
        rel = p.relative_to(REPO_ROOT)
    except ValueError:
        return True
    parts = rel.parts
    for ex in EXCLUDED_DIRS:
        if ex in parts:
            return True
    return False


def check_directories(root: Path):
    violations = []
    for dirpath, dirnames, _ in os.walk(root):
        dpath = Path(dirpath)
        if is_excluded_path(dpath):
            continue
        for dirname in dirnames:
            subpath = dpath / dirname
            if is_excluded_path(subpath):
                continue
            for pattern, desc in BANNED_DIRECTORY_PATTERNS:
                if pattern.search(dirname):
                    violations.append({
                        "type": "DIRECTORY",
                        "path": str(subpath.relative_to(REPO_ROOT)),
                        "line": 0,
                        "desc": desc,
                        "match": dirname,
                    })
    return violations


def check_file_name(file_path: Path):
    violations = []
    fname = file_path.name
    for pattern, desc in BANNED_FILENAME_PATTERNS:
        m = pattern.search(fname)
        if m:
            violations.append({
                "type": "FILENAME",
                "path": str(file_path.relative_to(REPO_ROOT)),
                "line": 0,
                "desc": desc,
                "match": m.group(0),
            })
    return violations


def check_file_content(file_path: Path):
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [{"type": "ERROR", "path": str(file_path), "line": 0, "desc": str(e), "match": ""}]

    lines = content.splitlines()
    in_code_block = False

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # Check Headings
        if stripped.startswith("#"):
            for pattern, desc in BANNED_HEADING_PATTERNS:
                m = pattern.search(stripped)
                if m:
                    violations.append({
                        "type": "HEADING",
                        "path": str(file_path.relative_to(REPO_ROOT)),
                        "line": idx,
                        "desc": desc,
                        "match": stripped,
                    })

        # Check Callouts
        if stripped.startswith(">"):
            for pattern, desc in BANNED_CALLOUT_PATTERNS:
                m = pattern.search(stripped)
                if m:
                    violations.append({
                        "type": "CALLOUT",
                        "path": str(file_path.relative_to(REPO_ROOT)),
                        "line": idx,
                        "desc": desc,
                        "match": stripped[:100],
                    })

        # Check Banned Jargon in body
        for pattern, desc in BANNED_VOCABULARY_PATTERNS:
            m = pattern.search(line)
            if m:
                violations.append({
                    "type": "VOCABULARY",
                    "path": str(file_path.relative_to(REPO_ROOT)),
                    "line": idx,
                    "desc": desc,
                    "match": m.group(0),
                })

    return violations


def get_git_staged_files():
    try:
        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=REPO_ROOT,
            text=True
        )
        files = []
        for line in out.splitlines():
            line = line.strip()
            if line and line.endswith(".md"):
                p = REPO_ROOT / line
                if p.is_file() and not is_excluded_path(p):
                    files.append(p)
        return files
    except Exception:
        return []


def main():
    parser = argparse.ArgumentParser(description="Check practitioner voice, naming, and tone standards.")
    parser.add_argument("--vault", action="store_true", help="Audit all public vault directories and files.")
    parser.add_argument("--git", action="store_true", help="Audit git staged files.")
    parser.add_argument("files", nargs="*", help="Specific files to audit.")
    args = parser.parse_args()

    all_violations = []

    # 1. Directory check
    all_violations.extend(check_directories(REPO_ROOT))

    # 2. Determine files to check
    target_files = []
    if args.git:
        target_files = get_git_staged_files()
    elif args.files:
        for f in args.files:
            p = Path(f).resolve()
            if p.is_file() and not is_excluded_path(p):
                target_files.append(p)
    else:
        # Default or --vault: scan all markdown files
        for p in REPO_ROOT.rglob("*.md"):
            if not is_excluded_path(p):
                target_files.append(p)

    for fpath in target_files:
        all_violations.extend(check_file_name(fpath))
        all_violations.extend(check_file_content(fpath))

    if not all_violations:
        print("[PASS] All directories, files, headings, and contents comply with practitioner-voice-and-tone.md.")
        sys.exit(0)

    print(f"\n[VIOLATIONS DETECTED] Found {len(all_violations)} issue(s) violating practitioner-voice-and-tone.md:\n")
    for v in all_violations:
        loc = f"{v['path']}:{v['line']}" if v['line'] > 0 else v['path']
        print(f"  [{v['type']}] {loc}")
        print(f"      Problem: {v['desc']}")
        if v['match']:
            print(f"      Matched: \"{v['match']}\"")
        print()

    sys.exit(1)


if __name__ == "__main__":
    main()
