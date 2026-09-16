#!/usr/bin/env python3
"""
_Restoration/build_vault_mapping.py

Constructs an authoritative mapping between every active note in the 5-Layer Stack
(01 to 05) and its historical ChatGPT baseline in commit f909d7a.
Traces git renames back through repository history.
"""

import os
import glob
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = REPO_ROOT / "_Restoration" / "vault_to_original_mapping.md"
MAPPING_JSON = REPO_ROOT / "_Restoration" / "vault_to_original_mapping.json"

VAULT_DIRS = [
    "01 Code Architecture & Hardware Execution",
    "02 Harness, Governance & Verification",
    "03 Runtime Mesh & Observability",
    "04 Context Architecture & Model Steering",
    "05 Developer Ergonomics & Software Economics"
]


def get_f909_files():
    """Retrieve all markdown files present in commit f909d7a."""
    raw = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "f909d7a"], encoding="utf-8")
    files = {}
    for line in raw.splitlines():
        line = line.strip()
        if line.endswith(".md") and not line.startswith("."):
            files[os.path.basename(line)] = line
    return files


def trace_git_history(current_rel_path: str, f909_map: dict):
    """
    Traces the git history of a file backwards to determine:
    1. If it originated in f909d7a (and its exact path at that time).
    2. If it was renamed.
    3. If it was created in a later commit.
    """
    posix_path = Path(current_rel_path).as_posix()
    base = os.path.basename(posix_path)

    # Direct basename match
    if base in f909_map:
        return {
            "status": "ORIGINAL_EXISTS",
            "f909_path": f909_map[base],
            "original_name": base,
            "match_type": "Direct Name Match"
        }

    # Trace via git log --follow
    try:
        out = subprocess.check_output(
            ["git", "log", "--follow", "--name-status", "--oneline", "-M20", "--", posix_path],
            encoding="utf-8", errors="ignore"
        )
    except Exception:
        out = ""

    lines = out.splitlines()
    
    # Check if any line in the history contains a path from f909_map
    for line in lines:
        for f_base, f_path in f909_map.items():
            if f_base in line:
                return {
                    "status": "ORIGINAL_EXISTS",
                    "f909_path": f_path,
                    "original_name": f_base,
                    "match_type": "Git Rename Traced"
                }

    # If not found in f909d7a, find creation commit
    creation_commit = "Unknown"
    for line in reversed(lines):
        if line and not any(line.startswith(c) for c in ["R", "M", "A", "D", "C"]):
            creation_commit = line.strip()
            break

    return {
        "status": "POST_F909_CREATION",
        "f909_path": None,
        "original_name": None,
        "match_type": f"Created in commit: {creation_commit}"
    }


def main():
    import json
    f909_map = get_f909_files()
    all_notes = []

    for vdir in VAULT_DIRS:
        for p in sorted(glob.glob(os.path.join(REPO_ROOT, vdir, "**", "*.md"), recursive=True)):
            rel = os.path.relpath(p, REPO_ROOT)
            all_notes.append(rel)

    print(f"Tracing git history for {len(all_notes)} vault notes...")
    results = []

    for rel_path in all_notes:
        trace = trace_git_history(rel_path, f909_map)
        posix_rel = Path(rel_path).as_posix()
        
        # Word counts
        with open(REPO_ROOT / rel_path, "r", encoding="utf-8", errors="ignore") as f:
            cur_words = len(f.read().split())

        orig_words = 0
        if trace["f909_path"]:
            try:
                orig_raw = subprocess.check_output(["git", "show", f"f909d7a:{trace['f909_path']}"], encoding="utf-8")
                orig_words = len(orig_raw.split())
            except Exception:
                orig_words = 0

        trace["current_path"] = posix_rel
        trace["current_words"] = cur_words
        trace["original_words"] = orig_words
        results.append(trace)

    # Save JSON mapping
    with open(MAPPING_JSON, "w", encoding="utf-8") as jf:
        json.dump(results, jf, indent=2)

    # Generate Markdown Table
    md = []
    md.append("# Vault Notes to Original ChatGPT Baseline Mapping\n")
    md.append("""<style>
table th, table td,
.markdown-rendered table td,
.markdown-rendered table th,
.cm-table-widget td,
.cm-table-widget th {
    vertical-align: top !important;
}
</style>
""")
    md.append("> [!NOTE]")
    md.append("> Complete mapping of all 108 notes across the 5-Layer Stack to their historical baseline in commit `f909d7a`.")
    md.append("> Traced via Git history (`git log --follow -M`).\n")

    orig_count = sum(1 for r in results if r["status"] == "ORIGINAL_EXISTS")
    new_count = len(results) - orig_count
    md.append(f"**Total Notes**: {len(results)} | **Originals in `f909d7a`**: {orig_count} ({orig_count/len(results)*100:.1f}%) | **New Notes (Post-`f909d7a`)**: {new_count}\n")
    md.append("---\n")

    current_layer = ""
    for r in results:
        layer = r["current_path"].split("/")[0]
        if layer != current_layer:
            current_layer = layer
            md.append(f"\n## {current_layer}\n")
            md.append("| Current Vault Note | Original in `f909d7a` | Match Status | Current Words | Original Words | Delta |")
            md.append("| :--- | :--- | :--- | :---: | :---: | :---: |")

        cur_title = Path(r["current_path"]).stem
        cur_link = f"[{cur_title}](file:///{REPO_ROOT.as_posix()}/{r['current_path']})"
        
        if r["status"] == "ORIGINAL_EXISTS":
            orig_title = Path(r["f909_path"]).stem
            orig_str = f"`{r['f909_path']}`"
            status_str = f"✅ {r['match_type']}"
            diff_words = r["current_words"] - r["original_words"]
            diff_str = f"{diff_words:+d}" if diff_words != 0 else "0"
            orig_words_str = str(r["original_words"])
        else:
            orig_str = "*(None - New Architectural Note)*"
            status_str = f"🆕 {r['match_type']}"
            orig_words_str = "-"
            diff_str = "-"

        md.append(f"| {cur_link} | {orig_str} | {status_str} | {r['current_words']} | {orig_words_str} | {diff_str} |")

    OUTPUT_FILE.write_text("\n".join(md), encoding="utf-8")
    print(f"[SUCCESS] Written mapping table to: {OUTPUT_FILE}")
    print(f"[SUCCESS] Written mapping JSON to: {MAPPING_JSON}")


if __name__ == "__main__":
    main()
