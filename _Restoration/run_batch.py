#!/usr/bin/env python3
"""
_Restoration/run_batch.py

Runs the restoration process on a slice of notes from vault_to_original_mapping.json
using restore_notes.py with --with-original.
Then runs verify_restoration_stats.py to produce the quality audit report.
"""

import sys
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAPPING_JSON = REPO_ROOT / "_Restoration" / "vault_to_original_mapping.json"
RESTORE_SCRIPT = REPO_ROOT / "_Restoration" / "restore_notes.py"
VERIFY_SCRIPT = REPO_ROOT / "_Restoration" / "verify_restoration_stats.py"
OUT_DIR = REPO_ROOT / "_Restoration" / "restored_output"


def main():
    start_idx = 0
    count = 10
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    if len(sys.argv) > 2:
        start_idx = int(sys.argv[2])

    with open(MAPPING_JSON, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    target_slice = mapping[start_idx : start_idx + count]
    print(f"============================================================")
    print(f"Running Restoration Batch for {len(target_slice)} notes (indices {start_idx} to {start_idx + count - 1})")
    print(f"============================================================")

    for i, item in enumerate(target_slice, start=start_idx + 1):
        rel_path = item["current_path"]
        abs_path = REPO_ROOT / rel_path
        status = item["status"]
        print(f"\n[{i}/{start_idx + count}] Processing: {abs_path.name}")
        print(f"    Path: {rel_path}")
        print(f"    Baseline Status: {status}")

        cmd = [
            sys.executable,
            str(RESTORE_SCRIPT),
            "--file", str(abs_path),
            "--output-dir", str(OUT_DIR),
            "--with-original"
        ]

        ret = subprocess.run(cmd)
        if ret.returncode != 0:
            print(f"    [FAIL] Process exited with code {ret.returncode}", file=sys.stderr)

    print("\n============================================================")
    print("Running Statistical Quality Gate & Audit...")
    print("============================================================")
    subprocess.run([sys.executable, str(VERIFY_SCRIPT)])


if __name__ == "__main__":
    main()
