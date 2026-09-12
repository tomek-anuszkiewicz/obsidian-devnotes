#!/usr/bin/env python3
"""
scripts/lint_attractors.py

Automated Linter for Linguistic Attractors, High-Register Jargon,
Hardware Domain Leaks, and Graph Integrity across the Obsidian Vault.

Exit codes:
  0: Clean / Passed
  1: Lint violations found (in strict mode)
"""

import os
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

VAULT_ROOT = Path(__file__).resolve().parent.parent

# 1. Banned / Quarantined Jargon across ALL public notes
QUARANTINED_JARGON = [
    (r"\bepistemic\w*\b", "Replace academic 'epistemic' with standard engineering terms (e.g. knowledge drift, cognitive burden, authoritative validation, knowledge diff)."),
    (r"\bteleological\w*\b", "Avoid inflated philosophical term 'teleological'; describe intentionality or design goals directly."),
]

# 2. Hardware terms quarantined to Layer 1 (Substrate & Mechanical Sympathy)
HARDWARE_TERMS = [
    r"\bL1i\b",
    r"\bL1\s+cache\b",
    r"\bL1i?\s+cache\s+thrashing\b",
    r"\bcache\s+lines?\b",
    r"\bbranch\s+predictors?\b",
    r"\bTLB\s+miss\w*\b",
    r"\bmicro-ops?\b",
]

# Files allowed to mention hardware terms
HARDWARE_ALLOWLIST_SUBSTRINGS = [
    os.path.normpath("01 Substrate & Mechanical Sympathy"),
    os.path.normpath("The 5-Layer System Stack for Agentic Software Engineering.md"),
    os.path.normpath("Context Attractors and Recency Bias in Long-Horizon Agent Sessions.md"),
    os.path.normpath(".agents/rules/information-hierarchy.md"),
    os.path.normpath(".agents/rules/vocabulary-and-attractor-discipline.md"),
    os.path.normpath(".agents/rules/language-agnostic-architecture.md"),
    os.path.normpath("scripts/"),
]

# C4 Model False Positive Exclusions (e.g. "Query L1 Context", "L2 Container")
C4_MODEL_EXCLUSION = re.compile(r"\[Query\s+L[1-4]\s+(?:Context|Container|Component|Code)\]", re.IGNORECASE)

# 2b. Polish / Non-English Language Detection (notes-language.md enforcement)
POLISH_DIACRITICS = re.compile(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]")
POLISH_INDICATORS = re.compile(
    r"\b(jak\s+na\s+ta[sś]mie|oraz|poniewa[zż]|notatk\w*|jestem|b[eę]dzie|dla|przez|mo[zż]emy|wstawi[cć]|rozmow\w*|innym|b[yye]ł\w*)\b",
    re.IGNORECASE
)

# 3. Canonical Hubs that must be piped if embedded inline in body prose
CANONICAL_HUBS = [
    "Software Entropy and the Zero-Friction Trap",
    "Testing in the Model, Agent, LLM Era",
    "Agentic Coding Harness and Controlled Development Workflows",
    "Embedding LLMs in Runtime Decision Paths and Operational Telemetry",
    "Retrieval-Augmented Generation and Context Architecture",
    "Developer Satisfaction, Identity, and Burnout in the Age of Coding Agents",
    "Competitive advantage in the age of commodity AI",
    "Software Engineering May Shift Toward Code Optimized for Agents",
]

# Notes exempt from unpiped hub links (charters and nav hubs that formally introduce the hubs)
CHARTER_NOTES = [
    os.path.normpath("The 5-Layer System Stack for Agentic Software Engineering.md"),
    os.path.normpath("_Explore.md"),
    os.path.normpath("Preamble.md"),
]

# Notes and folders allowed to reference 'mechanical sympathy'
MECHANICAL_SYMPATHY_ALLOWLIST = [
    os.path.normpath("01 Substrate & Mechanical Sympathy"),
    os.path.normpath("The 5-Layer System Stack for Agentic Software Engineering.md"),
    os.path.normpath("_Explore.md"),
    os.path.normpath("Preamble.md"),
    os.path.normpath("scripts/"),
]

# Regex for unpiped wikilinks: [[Hub Name]] without '|' and not inside headings or bullet-lists at the end
UNPIPED_HUB_PATTERNS = {
    hub: re.compile(r"(?<!#\s)(?<!\*\s)\[\[" + re.escape(hub) + r"\]\]")
    for hub in CANONICAL_HUBS
}


def is_public_note(path: Path) -> bool:
    rel = path.relative_to(VAULT_ROOT)
    parts = rel.parts
    if not parts:
        return False
    # Exclude internal / private folders and agent configurations
    if any(p.startswith(".git") or p.startswith(".obsidian") or p.startswith(".smart-env") or p.startswith(".agents") or p.startswith(".antigravity") or p == "_Private" for p in parts):
        return False
    return path.suffix.lower() == ".md"


def scan_vault(verbose: bool = False):
    violations = defaultdict(list)
    note_count = 0
    
    # Collect all markdown files
    md_files = []
    for root, dirs, files in os.walk(VAULT_ROOT):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in [".git", ".obsidian", ".smart-env", ".agents", ".antigravity", "_Private"]]
        for f in files:
            if f.endswith(".md"):
                md_files.append(Path(root) / f)
                
    note_count = len(md_files)
    
    for filepath in md_files:
        rel_path = filepath.relative_to(VAULT_ROOT)
        rel_str = str(rel_path)
        
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        is_hw_allowed = any(allowed in rel_str for allowed in HARDWARE_ALLOWLIST_SUBSTRINGS)
        is_charter = any(charter in rel_str for charter in CHARTER_NOTES)
        in_code_block = False

        for line_num, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()

            # Track code block fence
            if line.startswith("```"):
                in_code_block = not in_code_block
                continue

            # Skip frontmatter markers
            if line == "---" and line_num in [1, 2]:
                continue

            # 1. Quarantined Jargon Check
            for pattern, recommendation in QUARANTINED_JARGON:
                matches = re.findall(pattern, line, re.IGNORECASE)
                if matches:
                    violations[rel_str].append({
                        "line": line_num,
                        "type": "QUARANTINED_JARGON",
                        "match": matches[0],
                        "message": recommendation,
                        "snippet": line[:100]
                    })

            # 2. Hardware Leakage Check
            if not is_hw_allowed:
                # Check if it's C4 model notation
                clean_line = C4_MODEL_EXCLUSION.sub("", line)
                for hw_pat in HARDWARE_TERMS:
                    hw_matches = re.findall(hw_pat, clean_line, re.IGNORECASE)
                    if hw_matches:
                        violations[rel_str].append({
                            "line": line_num,
                            "type": "HARDWARE_LEAKAGE",
                            "match": hw_matches[0],
                            "message": "Hardware execution term leaked outside Layer 1 (Substrate). Generalize to system-level abstraction (e.g. instruction locality, working set size).",
                            "snippet": line[:100]
                        })

            # 3. Unpiped Hub Wikilink in Prose Check
            # Check if an unpiped canonical hub link is used mid-paragraph (not in charter, not in bullet, heading, or quote)
            if not is_charter and not line.startswith("*") and not line.startswith("-") and not line.startswith("#") and not line.startswith(">") and not line.startswith('"'):
                for hub, hub_regex in UNPIPED_HUB_PATTERNS.items():
                    if hub_regex.search(line):
                        violations[rel_str].append({
                            "line": line_num,
                            "type": "UNPIPED_HUB_LINK",
                            "match": f"[[{hub}]]",
                            "message": f"Avoid unpiped canonical hub link in body prose; pipe with natural context e.g. [[{hub}|descriptive phrase]].",
                            "snippet": line[:100]
                        })

            # 4. One-Way Privacy Membrane Leak Check
            if "[[_Private" in line or "[_Private" in line:
                violations[rel_str].append({
                    "line": line_num,
                    "type": "PRIVACY_LEAK",
                    "match": "_Private",
                    "message": "Public note references private directory. Violates one-way privacy membrane.",
                    "snippet": line[:100]
                })

            # 5. Mechanical Sympathy Heading Check
            if line.startswith("#"):
                if re.search(r"\bmechanical sympathy\b", line, re.IGNORECASE):
                    # Only allow canonical layer definition heading in The 5-Layer System Stack
                    is_stack_charter_layer1_heading = (
                        "The 5-Layer System Stack for Agentic Software Engineering.md" in rel_str
                        and re.match(r"^##\s+Layer\s+1:\s+Substrate\s+&\s+Mechanical\s+Sympathy$", line, re.IGNORECASE)
                    )
                    if not is_stack_charter_layer1_heading:
                        violations[rel_str].append({
                            "line": line_num,
                            "type": "HEADING_ATTRACTOR",
                            "match": "mechanical sympathy",
                            "message": "Do not use 'mechanical sympathy' in headings. Use specific engineering terms (e.g. 'Hardware Realities', 'Execution Efficiency', 'Substrate Alignment').",
                            "snippet": line[:100]
                        })

            # 6. Mechanical Sympathy Layer Quarantine Check
            is_mech_sympathy_allowed = any(allowed in rel_str for allowed in MECHANICAL_SYMPATHY_ALLOWLIST)
            if not is_mech_sympathy_allowed:
                if re.search(r"\bmechanical sympathy\b", line, re.IGNORECASE):
                    violations[rel_str].append({
                        "line": line_num,
                        "type": "LAYER_QUARANTINE_VIOLATION",
                        "match": "mechanical sympathy",
                        "message": "'mechanical sympathy' is quarantined strictly to Layer 1 (Substrate) and system charters. Generalize to hardware reality, systems efficiency, or low-level comprehension.",
                        "snippet": line[:100]
                    })

            # 7. Non-English / Polish Language Leak Check (notes-language.md enforcement)
            if not in_code_block:
                pol_diacritics = POLISH_DIACRITICS.findall(line)
                pol_phrases = POLISH_INDICATORS.findall(line)
                if pol_diacritics or pol_phrases:
                    match_str = "".join(sorted(set(pol_diacritics))) if pol_diacritics else pol_phrases[0]
                    violations[rel_str].append({
                        "line": line_num,
                        "type": "POLISH_LANGUAGE_LEAK",
                        "match": match_str,
                        "message": "Polish characters or words detected in public note. Violates notes-language.md (all vault notes must be exclusively in English).",
                        "snippet": line[:100]
                    })

    return note_count, violations


def main():
    parser = argparse.ArgumentParser(description="Lint Obsidian Vault for Linguistic Attractors & Jargon.")
    parser.add_argument("--strict", action="store_true", help="Exit with non-zero code on violations.")
    parser.add_argument("--verbose", action="store_true", help="Print verbose details.")
    args = parser.parse_args()

    print("=" * 70)
    print("[INFO] RUNNING VAULT ATTRACTOR & JARGON LINTER")
    print(f"       Root: {VAULT_ROOT}")
    print("=" * 70)

    note_count, violations = scan_vault(verbose=args.verbose)

    total_violations = sum(len(v) for v in violations.values())

    print(f"\nScanned: {note_count} public markdown files.")
    print(f"Files with violations: {len(violations)}")
    print(f"Total violations found: {total_violations}\n")

    if violations:
        print("[FAILED] LINT VIOLATIONS DETECTED:\n")
        for file_path, items in violations.items():
            print(f"  File: {file_path} ({len(items)} issues):")
            for item in items:
                print(f"    Line {item['line']:<4} [{item['type']}]: '{item['match']}'")
                print(f"      ↳ {item['message']}")
                print(f"      ↳ Context: \"{item['snippet']}\"\n")

        print("=" * 70)
        print("Status: FAILED")
        if args.strict:
            sys.exit(1)
        else:
            sys.exit(0)
    else:
        print("[PASSED] ALL CHECKS PASSED: Zero attractors, hardware leaks, or unpiped hub links detected!")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
