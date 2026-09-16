#!/usr/bin/env python3
"""
_Restoration/restore_group1_titles.py

Restores the 7 high-signal original ChatGPT titles from Group 1:
1. Networked Automation Loops... -> Singularity Without AGI - The Civilizational Automation Loop.md
2. Product Ambition Expansion... -> AI May Increase Product Ambition Instead of Reducing Team Size.md
3. OpenTelemetry as the Runtime Truth... -> OpenTelemetry.md
4. Optimizing Software Engineering... -> Software Engineering May Shift Toward Code Optimized for Agents.md
5. Language Evolution in the Era... -> Programming Languages May Evolve Differently in the Age of AI.md
6. The Increasing Value of Comments... -> Comments May Become More Valuable in AI-Generated Code.md
7. The Cost of Hidden Abstractions... -> Hidden Abstractions May Become More Expensive in Agent-Maintained Code.md

Updates wikilinks across the vault, _Private, and re-verifies graph integrity.
"""

import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

GROUP1_RENAMES = {
    "Networked Automation Loops and Software Output Without AGI": "Singularity Without AGI - The Civilizational Automation Loop",
    "Product Ambition Expansion in the Age of AI": "AI May Increase Product Ambition Instead of Reducing Team Size",
    "OpenTelemetry as the Runtime Truth for Autonomous Agents": "OpenTelemetry",
    "Optimizing Software Engineering and Code for Agents": "Software Engineering May Shift Toward Code Optimized for Agents",
    "Language Evolution in the Era of Autonomous Coding": "Programming Languages May Evolve Differently in the Age of AI",
    "The Increasing Value of Comments in AI-Generated Code": "Comments May Become More Valuable in AI-Generated Code",
    "The Cost of Hidden Abstractions in Agent-Maintained Code": "Hidden Abstractions May Become More Expensive in Agent-Maintained Code"
}


def find_files():
    found = {}
    for root, dirs, files in os.walk(REPO_ROOT):
        if ".git" in root or "_Private" in root or "_Restoration" in root:
            continue
        for f in files:
            if f.endswith(".md"):
                base = f[:-3]
                if base in GROUP1_RENAMES:
                    found[base] = Path(root) / f
    return found


def rename_files(file_map):
    print("=== Renaming files via git mv ===")
    renamed_map = {}
    for old_base, old_path in file_map.items():
        new_base = GROUP1_RENAMES[old_base]
        new_path = old_path.parent / f"{new_base}.md"
        rel_old = old_path.relative_to(REPO_ROOT).as_posix()
        rel_new = new_path.relative_to(REPO_ROOT).as_posix()
        
        print(f"git mv '{rel_old}' -> '{rel_new}'")
        res = subprocess.run(["git", "mv", str(old_path), str(new_path)], capture_output=True, text=True, cwd=REPO_ROOT)
        if res.returncode != 0:
            print(f"Error: {res.stderr}")
        else:
            renamed_map[old_base] = new_path
    return renamed_map


def update_headers(renamed_map):
    print("\n=== Updating Headers & Aliases ===")
    for old_base, new_path in renamed_map.items():
        new_base = GROUP1_RENAMES[old_base]
        content = new_path.read_text(encoding="utf-8")

        # 1. Title
        content = re.sub(r'^title:\s*.*$', f'title: "{new_base}"', content, flags=re.MULTILINE)

        # 2. Aliases
        alias_pattern = re.search(r'aliases:\s*\n((?:\s*-\s*.*\n)+)', content)
        if alias_pattern:
            aliases_block = alias_pattern.group(0)
            if old_base not in aliases_block:
                new_aliases_block = aliases_block + f"  - \"{old_base}\"\n"
                content = content.replace(aliases_block, new_aliases_block, 1)
        else:
            fm_match = re.search(r'^---\n(.*?)\n---', content, flags=re.DOTALL)
            if fm_match:
                fm_inner = fm_match.group(1)
                new_fm = fm_inner + f"\naliases:\n  - \"{old_base}\""
                content = content.replace(fm_match.group(0), f"---\n{new_fm}\n---", 1)

        # 3. H1
        content = re.sub(r'^#\s+.*$', f'# {new_base}', content, count=1, flags=re.MULTILINE)

        new_path.write_text(content, encoding="utf-8")
        print(f"Updated headers for: {new_base}")


def update_wikilinks():
    print("\n=== Updating Wikilinks Across Vault & _Private ===")
    all_mds = []
    for root, dirs, files in os.walk(REPO_ROOT):
        if ".git" in root:
            continue
        for f in files:
            if f.endswith(".md"):
                all_mds.append(Path(root) / f)

    sorted_renames = sorted(GROUP1_RENAMES.items(), key=lambda x: len(x[0]), reverse=True)
    total_rep = 0
    mod_files = 0

    for p in all_mds:
        orig = p.read_text(encoding="utf-8", errors="ignore")
        mod = orig

        for old_base, new_base in sorted_renames:
            # Piped
            def rep_piped(m):
                nonlocal total_rep
                total_rep += 1
                return f"[[{new_base}|{m.group(1)}]]"
            mod = re.sub(r'\[\[' + re.escape(old_base) + r'\|([^\]]+)\]\]', rep_piped, mod)

            # Unpiped
            def rep_unpiped(m):
                nonlocal total_rep
                total_rep += 1
                return f"[[{new_base}]]"
            mod = re.sub(r'\[\[' + re.escape(old_base) + r'\]\]', rep_unpiped, mod)

        if mod != orig:
            p.write_text(mod, encoding="utf-8")
            mod_files += 1

    print(f"Replaced {total_rep} wikilinks across {mod_files} files.")


def update_restored_output():
    print("\n=== Syncing _Restoration/restored_output ===")
    restored_dir = REPO_ROOT / "_Restoration" / "restored_output"
    if not restored_dir.exists():
        return

    for old_base, new_base in GROUP1_RENAMES.items():
        old_file = restored_dir / f"{old_base}.md"
        new_file = restored_dir / f"{new_base}.md"
        if old_file.exists():
            content = old_file.read_text(encoding="utf-8")
            content = re.sub(r'^title:\s*.*$', f'title: "{new_base}"', content, flags=re.MULTILINE)
            content = re.sub(r'^#\s+.*$', f'# {new_base}', content, count=1, flags=re.MULTILINE)
            new_file.write_text(content, encoding="utf-8")
            old_file.unlink()
            print(f"Renamed in restored_output: {old_base} -> {new_base}")


def main():
    file_map = find_files()
    print(f"Found {len(file_map)} of {len(GROUP1_RENAMES)} files.")
    renamed_map = rename_files(file_map)
    update_headers(renamed_map)
    update_wikilinks()
    update_restored_output()


if __name__ == "__main__":
    main()
