#!/usr/bin/env python3
"""
_Restoration/apply_renames_and_fix_links.py

Performs comprehensive file renaming for Step 1 + Step 2:
1. Renames 26 notes using git mv to clean, concise, active-voice titles.
2. Updates YAML frontmatter (title, aliases) and H1 header in each renamed note.
3. Updates all wikilinks across every markdown file in the vault.
4. Mirrors changes to _Restoration/restored_output/ if files exist there.
5. Verifies all links to ensure 0 broken links.
"""

import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

RENAMES = {
    # Step 1: Casing, punctuation, grammar, and generic titles
    "Competitive advantage in the age of commodity AI": "Competitive Advantage in the Age of Commodity AI",
    "AI-Assisted Software Engineering Where Are We Now": "AI-Assisted Software Engineering - Where Are We Now",
    "LLM Coding Agents Reliability": "Reliability of LLM Coding Agents",
    "OpenTelemetry": "OpenTelemetry as the Runtime Truth for Autonomous Agents",
    "Introduction to Workflow Orchestration": "Workflow Orchestration in Agentic Systems",
    
    # Step 2: Ultra-long titles (>80 chars) & Speculative "AI May..." monotony
    "The Conductor Pattern - Cognitive Ergonomics of High-Bandwidth Agentic Engineering": "The Conductor Pattern for High-Bandwidth Engineering",
    "The Living Engineering Chronicle - Context-Safe Logging, Evolution, and Compaction": "The Living Engineering Chronicle and Context Compaction",
    "Personal Digital Representation May Become the Foundation of an AI Agent Ecosystem": "Personal Digital Models as the Foundation of Agent Ecosystems",
    "Personal AI Subscriptions May Unify Model Access, Managed RAG, and Portable APIs": "Personal AI Subscriptions and Unified Model Access",
    "Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification": "Correcting AI Code - Patch, Regenerate, or Respecify",
    "Building Determinism from Unpredictable Models - Agent Harness Architecture": "Building Determinism from Unpredictable Models",
    "How Personal AI Models Will Diff, Reconcile, and Challenge External Knowledge": "How Personal AI Models Reconcile External Knowledge",
    "Service-to-Service Authentication and Authorization in Azure and Kubernetes": "Service-to-Service Authentication in Distributed Runtimes",
    "Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize": "Enforcing Hard-to-Formalize Architectural Rules with Agents",
    "AI May Replace Some Source Generators with Explicit Generated Code": "Replacing Source Generators with Explicit Generated Code",
    "Comments May Become More Valuable in AI-Generated Code": "The Increasing Value of Comments in AI-Generated Code",
    "Hidden Abstractions May Become More Expensive in Agent-Maintained Code": "The Cost of Hidden Abstractions in Agent-Maintained Code",
    "AI May Make Aggressive Code Optimization Economically Viable": "The Economics of Aggressive Code Optimization with AI",
    "Applications May Shift from Fixed Features to Agent-Extensible Primitives": "Shifting from Fixed Features to Agent-Extensible Primitives",
    "New Developer Technologies May Need to Be Agent-Ready from Day One": "Designing Developer Technologies for Agent-Readiness",
    "AI May Become an Irreversible Part of Software Development": "The Irreversible Integration of AI in Software Engineering",
    "AI May Break the Old Economic Model of the Open Web": "How AI Breaks the Economic Model of the Open Web",
    "AI May Create a New Market for Small, Custom Business Software": "A New Market for Small, Custom Business Software",
    "AI May Increase Product Ambition Instead of Reducing Team Size": "Product Ambition Expansion in the Age of AI",
    "Software Engineering May Shift Toward Code Optimized for Agents": "Optimizing Software Engineering and Code for Agents",
    "Programming Languages May Evolve Differently in the Age of AI": "Language Evolution in the Era of Autonomous Coding"
}


def find_vault_files():
    """Find current path of all 26 target files in the vault."""
    mapping = {}
    for root, dirs, files in os.walk(REPO_ROOT):
        # Ignore git and private
        if ".git" in root or "_Private" in root or "_Restoration" in root:
            continue
        for f in files:
            if f.endswith(".md"):
                base = f[:-3]
                if base in RENAMES:
                    mapping[base] = Path(root) / f
    return mapping


def rename_vault_files(file_map):
    """Rename vault files via git mv."""
    print("=== Renaming files via git mv ===")
    renamed_map = {}
    for old_base, old_path in file_map.items():
        new_base = RENAMES[old_base]
        new_path = old_path.parent / f"{new_base}.md"
        rel_old = old_path.relative_to(REPO_ROOT).as_posix()
        rel_new = new_path.relative_to(REPO_ROOT).as_posix()
        
        print(f"git mv '{rel_old}' -> '{rel_new}'")
        res = subprocess.run(["git", "mv", str(old_path), str(new_path)], capture_output=True, text=True, cwd=REPO_ROOT)
        if res.returncode != 0:
            print(f"Error renaming {rel_old}: {res.stderr}")
        else:
            renamed_map[old_base] = new_path
    return renamed_map


def update_renamed_file_headers(renamed_map):
    """Update title, aliases, and H1 header in each renamed file."""
    print("\n=== Updating Frontmatter and H1 Headers in Renamed Files ===")
    for old_base, new_path in renamed_map.items():
        new_base = RENAMES[old_base]
        content = new_path.read_text(encoding="utf-8")
        
        # 1. Update frontmatter title:
        content = re.sub(r'^title:\s*.*$', f'title: "{new_base}"', content, flags=re.MULTILINE)
        
        # 2. Add old title as an alias if aliases block exists
        alias_pattern = re.search(r'aliases:\s*\n((?:\s*-\s*.*\n)+)', content)
        if alias_pattern:
            aliases_block = alias_pattern.group(0)
            if old_base not in aliases_block:
                new_aliases_block = aliases_block + f"  - \"{old_base}\"\n"
                content = content.replace(aliases_block, new_aliases_block, 1)
        else:
            # Add aliases block into frontmatter
            fm_match = re.search(r'^---\n(.*?)\n---', content, flags=re.DOTALL)
            if fm_match:
                fm_inner = fm_match.group(1)
                new_fm = fm_inner + f"\naliases:\n  - \"{old_base}\""
                content = content.replace(fm_match.group(0), f"---\n{new_fm}\n---", 1)

        # 3. Update first H1 heading
        content = re.sub(r'^#\s+.*$', f'# {new_base}', content, count=1, flags=re.MULTILINE)

        new_path.write_text(content, encoding="utf-8")
        print(f"Updated headers for: {new_base}")


def update_wikilinks_in_all_notes():
    """Update all wikilinks across every markdown file in the vault."""
    print("\n=== Updating Wikilinks Across the Vault ===")
    all_mds = []
    for root, dirs, files in os.walk(REPO_ROOT):
        if ".git" in root or "_Private" in root:
            continue
        for f in files:
            if f.endswith(".md"):
                all_mds.append(Path(root) / f)

    # Sort renames by length descending so longer titles match first
    sorted_renames = sorted(RENAMES.items(), key=lambda x: len(x[0]), reverse=True)

    modified_count = 0
    total_replacements = 0

    for md_path in all_mds:
        original = md_path.read_text(encoding="utf-8")
        modified = original

        for old_base, new_base in sorted_renames:
            # Case 1: [[old_base|alias]] -> [[new_base|alias]]
            def replace_piped(match):
                nonlocal total_replacements
                total_replacements += 1
                return f"[[{new_base}|{match.group(1)}]]"

            modified = re.sub(r'\[\[' + re.escape(old_base) + r'\|([^\]]+)\]\]', replace_piped, modified)

            # Case 2: [[old_base]] -> [[new_base]]
            def replace_unpiped(match):
                nonlocal total_replacements
                total_replacements += 1
                return f"[[{new_base}]]"

            modified = re.sub(r'\[\[' + re.escape(old_base) + r'\]\]', replace_unpiped, modified)

        if modified != original:
            md_path.write_text(modified, encoding="utf-8")
            modified_count += 1

    print(f"Updated {total_replacements} wikilinks across {modified_count} files.")


def update_restored_output_folder():
    """Keep _Restoration/restored_output in sync if files exist."""
    print("\n=== Syncing _Restoration/restored_output ===")
    restored_dir = REPO_ROOT / "_Restoration" / "restored_output"
    if not restored_dir.exists():
        return

    for old_base, new_base in RENAMES.items():
        old_file = restored_dir / f"{old_base}.md"
        new_file = restored_dir / f"{new_base}.md"
        if old_file.exists():
            content = old_file.read_text(encoding="utf-8")
            content = re.sub(r'^title:\s*.*$', f'title: "{new_base}"', content, flags=re.MULTILINE)
            content = re.sub(r'^#\s+.*$', f'# {new_base}', content, count=1, flags=re.MULTILINE)
            new_file.write_text(content, encoding="utf-8")
            old_file.unlink()
            print(f"Renamed in restored_output: {old_base} -> {new_base}")


def verify_graph_integrity():
    """Verify that all wikilinks across all notes point to existing notes."""
    print("\n=== Verifying Knowledge Graph Integrity ===")
    all_notes = set()
    all_aliases = set()
    all_md_files = []

    for root, dirs, files in os.walk(REPO_ROOT):
        if ".git" in root or "_Private" in root or "_Restoration" in root:
            continue
        for f in files:
            if f.endswith(".md"):
                base = f[:-3]
                all_notes.add(base)
                p = Path(root) / f
                all_md_files.append(p)
                content = p.read_text(encoding="utf-8")
                alias_match = re.search(r'aliases:\s*\n((?:\s*-\s*.*\n)+)', content)
                if alias_match:
                    for line in alias_match.group(1).splitlines():
                        clean_alias = line.strip().lstrip("-").strip().strip('"').strip("'")
                        if clean_alias:
                            all_aliases.add(clean_alias)

    valid_targets = all_notes | all_aliases
    broken_links = []

    for p in all_md_files:
        content = p.read_text(encoding="utf-8")
        links = re.findall(r'\[\[([^\|\]#]+)(?:#[^\|\]]+)?(?:\|[^\]]+)?\]\]', content)
        for target in links:
            target_clean = target.strip()
            # Ignore empty or special
            if not target_clean:
                continue
            if target_clean not in valid_targets:
                broken_links.append((p.name, target_clean))

    if broken_links:
        print(f"[WARN] Found {len(broken_links)} broken links:")
        for source, target in broken_links[:20]:
            print(f"  {source} -> [[{target}]]")
    else:
        print(f"[PASS] 100% Graph Integrity: Zero broken links across all {len(all_md_files)} notes!")


def main():
    file_map = find_vault_files()
    print(f"Located {len(file_map)} of {len(RENAMES)} files in the vault.")
    renamed_map = rename_vault_files(file_map)
    update_renamed_file_headers(renamed_map)
    update_wikilinks_in_all_notes()
    update_restored_output_folder()
    verify_graph_integrity()


if __name__ == "__main__":
    main()
