#!/usr/bin/env python3
"""
_Restoration/audit_all_links.py
Audits all wikilinks in:
1. The 5 public directories (01 to 05)
2. The _Private directory
Checks for broken targets, old note titles, and leaks.
"""

import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def run_audit():
    vault_dirs = [
        "01 Architecture & Code",
        "02 Testing & Code Review",
        "03 Systems & Infrastructure",
        "04 Prompts, Context & Models",
        "05 Engineering Economics & Future"
    ]

    public_notes = {}
    public_aliases = {}
    
    for vd in vault_dirs:
        dir_path = REPO_ROOT / vd
        if not dir_path.exists():
            continue
        for root, dirs, files in os.walk(dir_path):
            for f in files:
                if f.endswith(".md"):
                    base = f[:-3]
                    p = Path(root) / f
                    public_notes[base] = p
                    content = p.read_text(encoding="utf-8", errors="ignore")
                    m = re.search(r'aliases:\s*\n((?:\s*-\s*.*\n)+)', content)
                    if m:
                        for line in m.group(1).splitlines():
                            a = line.strip().lstrip("-").strip().strip('"\'')
                            if a:
                                public_aliases[a] = base

    private_notes = {}
    private_aliases = {}
    priv_dir = REPO_ROOT / "_Private"
    if priv_dir.exists():
        for root, dirs, files in os.walk(priv_dir):
            for f in files:
                if f.endswith(".md"):
                    base = f[:-3]
                    p = Path(root) / f
                    private_notes[base] = p
                    content = p.read_text(encoding="utf-8", errors="ignore")
                    m = re.search(r'aliases:\s*\n((?:\s*-\s*.*\n)+)', content)
                    if m:
                        for line in m.group(1).splitlines():
                            a = line.strip().lstrip("-").strip().strip('"\'')
                            if a:
                                private_aliases[a] = base

    # Root notes
    root_notes = {}
    for f in os.listdir(REPO_ROOT):
        if f.endswith(".md"):
            base = f[:-3]
            root_notes[base] = REPO_ROOT / f

    print(f"Public notes in 5 pillars: {len(public_notes)}, Aliases: {len(public_aliases)}")
    print(f"Private notes: {len(private_notes)}, Aliases: {len(private_aliases)}")
    print(f"Root notes: {len(root_notes)}")

    all_public_valid = set(public_notes.keys()) | set(public_aliases.keys()) | set(root_notes.keys())
    all_private_valid = set(private_notes.keys()) | set(private_aliases.keys())
    all_valid_for_private = all_public_valid | all_private_valid

    # 1. Audit Public Notes
    public_broken = []
    public_to_private = []

    for base, p in public_notes.items():
        content = p.read_text(encoding="utf-8", errors="ignore")
        # Find all [[wikilinks]]
        links = re.findall(r'\[\[([^\|\]#]+)(?:#[^\|\]]+)?(?:\|[^\]]+)?\]\]', content)
        for target in links:
            t = target.strip()
            if not t:
                continue
            if t in ["wikilinks", "^\]", "Target File", "...", "Note Title", "Target Note", "Hub Title"]:
                continue
            if t in all_private_valid:
                public_to_private.append((p.relative_to(REPO_ROOT).as_posix(), t))
            elif t not in all_public_valid:
                public_broken.append((p.relative_to(REPO_ROOT).as_posix(), t))

    print(f"\n--- Public 5 Pillars Audit ---")
    print(f"Public -> Private leaks (STRICTLY FORBIDDEN): {len(public_to_private)}")
    for src, tgt in public_to_private:
        print(f"  [LEAK] {src} -> [[{tgt}]]")

    print(f"Broken links in Public 5 pillars: {len(public_broken)}")
    for src, tgt in public_broken:
        print(f"  [BROKEN] {src} -> [[{tgt}]]")

    # 2. Audit Private Notes
    private_broken = []
    private_to_old_public = []

    for base, p in private_notes.items():
        content = p.read_text(encoding="utf-8", errors="ignore")
        links = re.findall(r'\[\[([^\|\]#]+)(?:#[^\|\]]+)?(?:\|[^\]]+)?\]\]', content)
        for target in links:
            t = target.strip()
            if not t:
                continue
            if t in ["wikilinks", "^\]", "Target File", "...", "Note Title", "Target Note", "Hub Title"]:
                continue
            if t not in all_valid_for_private:
                private_broken.append((p.relative_to(REPO_ROOT).as_posix(), t))

    print(f"\n--- _Private Directory Audit ---")
    print(f"Broken links in _Private: {len(private_broken)}")
    for src, tgt in private_broken:
        print(f"  [BROKEN IN PRIVATE] {src} -> [[{tgt}]]")


def fix_private_links():
    from apply_renames_and_fix_links import RENAMES
    priv_dir = REPO_ROOT / "_Private"
    if not priv_dir.exists():
        return
    sorted_renames = sorted(RENAMES.items(), key=lambda x: len(x[0]), reverse=True)
    modified_count = 0
    replacement_count = 0

    for root, dirs, files in os.walk(priv_dir):
        for f in files:
            if f.endswith(".md"):
                p = Path(root) / f
                orig = p.read_text(encoding="utf-8")
                mod = orig
                for old_base, new_base in sorted_renames:
                    # Piped
                    mod, n1 = re.subn(r'\[\[' + re.escape(old_base) + r'\|([^\]]+)\]\]', f'[[{new_base}|\\1]]', mod)
                    # Unpiped
                    mod, n2 = re.subn(r'\[\[' + re.escape(old_base) + r'\]\]', f'[[{new_base}]]', mod)
                    replacement_count += (n1 + n2)

                if mod != orig:
                    p.write_text(mod, encoding="utf-8")
                    modified_count += 1
                    print(f"Updated links in private note: {p.name}")

    print(f"Repaired {replacement_count} links across {modified_count} private notes.")


if __name__ == "__main__":
    fix_private_links()
    run_audit()
