#!/usr/bin/env python3
"""
_Restoration/verify_restoration_stats.py

Statistical Quality Gate & Anomaly Detection for Restored Notes.
Compares restored notes against their original ChatGPT baselines (commit f909d7a)
and current versions, detecting anomalies in:
- Word counts & shrinkage
- Code block preservation (catches dropped code)
- Gemini degradation markers (buzzwords, rigid templates, shouting ASCII)
- Formatting integrity
"""

import os
import re
import json
import glob
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESTORATION_DIR = REPO_ROOT / "_Restoration"
MAPPING_JSON = RESTORATION_DIR / "vault_to_original_mapping.json"
REPORT_MD = RESTORATION_DIR / "restoration_statistical_report.md"

PROHIBITED_BUZZWORDS = [
    "mechanical exoskeleton", "stochastic substrate", "epistemic dialectic",
    "TOXIC AMBIENT MAGIC", "NAIVE ACCEPTANCE", "Core Invariants", "Axiom:"
]


def load_mapping():
    if MAPPING_JSON.exists():
        try:
            return json.loads(MAPPING_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def count_code_blocks(text: str) -> int:
    return text.count("```") // 2


def check_degradation_markers(text: str) -> list:
    found = []
    for b in PROHIBITED_BUZZWORDS:
        if b.lower() in text.lower():
            found.append(b)
    if re.search(r"^\s*>\s*\[!(IMPORTANT|CAUTION)\]\s*\n\s*>\s*\*\*The .* Axiom", text, re.MULTILINE):
        found.append("Axiom Callout")
    return found


def verify_notes(restored_dir: Path):
    mappings = {Path(m["current_path"]).name: m for m in load_mapping()}
    restored_files = sorted(list(restored_dir.glob("*.md")))

    records = []

    for rf in restored_files:
        filename = rf.name
        mapping = mappings.get(filename, {})
        
        rest_text = rf.read_text(encoding="utf-8", errors="ignore")
        rest_words = len(rest_text.split())
        rest_code = count_code_blocks(rest_text)
        rest_markers = check_degradation_markers(rest_text)

        orig_words = mapping.get("original_words", 0)
        orig_code = 0
        orig_path = mapping.get("f909_path")

        if orig_path:
            try:
                orig_text = subprocess.check_output(["git", "show", f"f909d7a:{orig_path}"], encoding="utf-8", errors="ignore")
                orig_code = count_code_blocks(orig_text)
                if orig_words == 0:
                    orig_words = len(orig_text.split())
            except Exception:
                pass

        # Anomaly scoring
        status = "PASS"
        flags = []

        # Code loss check
        if orig_code > 0:
            if rest_code < orig_code * 0.5:
                status = "FAIL"
                flags.append(f"Significant code loss ({orig_code} -> {rest_code} blocks)")
            elif rest_code < orig_code:
                if status != "FAIL":
                    status = "WARN"
                flags.append(f"Code consolidation ({orig_code} -> {rest_code} blocks)")

        # Word count check
        if orig_words > 0:
            ratio = rest_words / orig_words
            if ratio < 0.65:
                status = "FAIL"
                flags.append(f"Severe truncation ({ratio*100:.0f}% of original)")
            elif ratio < 0.85:
                if status != "FAIL": status = "WARN"
                flags.append(f"Slight shrinkage ({ratio*100:.0f}% of original)")

        # Degradation markers check
        if rest_markers:
            status = "FAIL"
            flags.append(f"Degradation markers: {', '.join(rest_markers)}")

        records.append({
            "filename": filename,
            "status": status,
            "orig_words": orig_words,
            "rest_words": rest_words,
            "orig_code": orig_code,
            "rest_code": rest_code,
            "flags": flags
        })

    return records


def generate_report(records, output_file: Path):
    md = []
    md.append("# Statistical Restoration Audit & Quality Gate Report\n")
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
    md.append("> Automated statistical sanity check comparing restored notes against their original ground-truth baselines.")
    md.append("> Flags: code block drop, severe shrinkage (<65%), and presence of prohibited degradation markers.\n")

    pass_count = sum(1 for r in records if r["status"] == "PASS")
    warn_count = sum(1 for r in records if r["status"] == "WARN")
    fail_count = sum(1 for r in records if r["status"] == "FAIL")

    md.append(f"**Total Audited**: {len(records)} | 🟢 **PASS**: {pass_count} | 🟡 **WARN**: {warn_count} | 🔴 **FAIL**: {fail_count}\n")
    md.append("---\n")

    md.append("| Status | Note Title | Original Words | Restored Words | Code Blocks (Orig -> Rest) | Diagnostic Flags |")
    md.append("| :---: | :--- | :---: | :---: | :---: | :--- |")

    for r in records:
        if r["status"] == "PASS":
            s_icon = "🟢 PASS"
        elif r["status"] == "WARN":
            s_icon = "🟡 WARN"
        else:
            s_icon = "🔴 FAIL"

        flags_str = "<br>".join(r["flags"]) if r["flags"] else "*(All quality metrics healthy)*"
        orig_words_str = str(r["orig_words"]) if r["orig_words"] > 0 else "-"
        code_str = f"{r['orig_code']} -> {r['rest_code']}" if r["orig_words"] > 0 else f"{r['rest_code']}"

        md.append(f"| {s_icon} | **{r['filename']}** | {orig_words_str} | {r['rest_words']} | {code_str} | {flags_str} |")

    output_file.write_text("\n".join(md), encoding="utf-8")
    print(f"[SUCCESS] Written statistical report to: {output_file}")


def main():
    restored_dir = RESTORATION_DIR / "restored_output"
    if not restored_dir.exists():
        print(f"Error: {restored_dir} does not exist", file=sys.stderr)
        return

    records = verify_notes(restored_dir)
    generate_report(records, REPORT_MD)


if __name__ == "__main__":
    main()
