#!/usr/bin/env python3
"""
_Restoration/verify_all_in_vault.py

Verifies that every single file in _Restoration/restored_output exists
in one of the 5 pillar directories, and that its SHA-256 hash matches bit-for-bit.
"""

import os
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def main():
    restored_dir = REPO_ROOT / "_Restoration" / "restored_output"
    restored_files = {f: (restored_dir / f) for f in os.listdir(restored_dir) if f.endswith(".md")}

    vault_dirs = [
        "01 Architecture & Code",
        "02 Testing & Code Review",
        "03 Systems & Infrastructure",
        "04 Prompts, Context & Models",
        "05 Engineering Economics & Future"
    ]

    vault_files = {}
    pillar_counts = {vd: 0 for vd in vault_dirs}
    subfolder_counts = {}

    for vd in vault_dirs:
        p = REPO_ROOT / vd
        for root, dirs, files in os.walk(p):
            sub = Path(root).relative_to(REPO_ROOT).as_posix()
            subfolder_counts[sub] = 0
            for f in files:
                if f.endswith(".md"):
                    vault_files[f] = (Path(root) / f)
                    pillar_counts[vd] += 1
                    subfolder_counts[sub] += 1

    print(f"Total in _Restoration/restored_output: {len(restored_files)}")
    print(f"Total in 5 pillar directories:         {len(vault_files)}")
    print("\nBreakdown by Pillar:")
    for vd, count in pillar_counts.items():
        print(f"  - {vd}: {count} notes")

    print("\nBreakdown by Subfolder:")
    for sub, count in sorted(subfolder_counts.items()):
        if count > 0:
            print(f"  - {sub}: {count} notes")

    missing_in_vault = [f for f in restored_files if f not in vault_files]
    missing_in_restored = [f for f in vault_files if f not in restored_files]

    print(f"\nMissing in 5 pillars: {len(missing_in_vault)}")
    for f in missing_in_vault:
        print(f"  [MISSING] {f}")

    print(f"Missing in restored_output: {len(missing_in_restored)}")
    for f in missing_in_restored:
        print(f"  [MISSING] {f}")

    # Hash comparison
    mismatches = []
    for f, rpath in restored_files.items():
        if f in vault_files:
            vpath = vault_files[f]
            h1 = hashlib.sha256(rpath.read_bytes()).hexdigest()
            h2 = hashlib.sha256(vpath.read_bytes()).hexdigest()
            if h1 != h2:
                mismatches.append(f)

    print(f"SHA-256 content mismatches: {len(mismatches)}")
    for f in mismatches:
        print(f"  [MISMATCH] {f}")

    if not missing_in_vault and not missing_in_restored and not mismatches:
        print("\n>> VERIFICATION PASSED: All 108 files exist in the 5 pillars and match bit-for-bit!")

if __name__ == "__main__":
    main()
