#!/usr/bin/env python3
"""
scripts/extract_originals.py

Extracts the original ChatGPT baseline versions of vault notes from commit f909d7a
(and db19239) and saves them alongside their current counterparts with the
suffix ' - original.md'.
"""

import os
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# 1. Base mappings from historical analysis in git (041d272~1:_Restoration/vault_to_original_mapping.json)
def get_base_mapping():
    raw_map = subprocess.check_output(
        ['git', 'show', '041d272~1:_Restoration/vault_to_original_mapping.json'],
        encoding='utf-8'
    )
    data = json.loads(raw_map)
    mapping = {}
    for d in data:
        if d['status'] == 'ORIGINAL_EXISTS':
            mapping[os.path.normpath(d['current_path'])] = ('f909d7a', d['f909_path'])
    return mapping

# 2. Add verified renamed / spaced notes
MANUAL_ADDITIONS = [
    ('01 Architecture & Code/Modularity & System Design/Designing Internal Packages as an Explicit, Composable Framework.md',
     'f909d7a', 'Architecture Guidelines/Designing Internal NuGet Packages as an Explicit, Composable Framework.md'),
    ('01 Architecture & Code/Modularity & System Design/Internal Shared Packages vs Agent-Generated Code.md',
     'f909d7a', 'Architecture Guidelines/Internal NuGet Packages vs Agent-Generated Code.md'),
    ('03 Systems & Infrastructure/Services & Security/Service-to-Service Communication - How Service A Should Call Service B.md',
     'f909d7a', 'Architecture Guidelines/Service-to-Service Communication -  How Service A Should Call Service B.md'),
    ('05 Engineering Economics & Future/Autonomous Workflows/Proactive Software - From Reactive Systems to Autonomous Agents.md',
     'f909d7a', 'Future/Proactive Software -  From Reactive Systems to Autonomous Agents.md'),
    ('05 Engineering Economics & Future/Autonomous Workflows/Singularity Without AGI - The Civilizational Automation Loop.md',
     'f909d7a', 'Future/Singularity Without AGI -  The Civilizational Automation Loop.md'),
    ('02 Testing & Code Review/Harnesses & Workflows/Agent Advantage - Relentless, Methodical Work.md',
     'f909d7a', 'LLM Using/Agent Advantage -  Relentless, Methodical Work.md'),
    ('03 Systems & Infrastructure/APIs & Integrations/Shifting from Fixed Features to Agent-Extensible Primitives.md',
     'db19239', 'Future/Applications May Shift from Fixed Features to Agent-Extensible Primitives.md'),
    ('01 Architecture & Code/Modularity & System Design/Data Access Economics with Coding Agents - ORMs vs Explicit SQL.md',
     'f909d7a', 'Architecture Guidelines/Agentic Coding with EF Core and SQL Server.md')
]

RAG_SOURCES = [
    'RAG/Introduction to RAG.md',
    'RAG/Advanced RAG Architectures.md',
    'RAG/RAG Ingestion and Chunking Strategies.md',
    'RAG/RAG Retrieval and Search.md'
]

def main():
    mapping = get_base_mapping()
    for cur_path, commit_ref, orig_path in MANUAL_ADDITIONS:
        mapping[os.path.normpath(cur_path)] = (commit_ref, orig_path)

    # All active notes in 5 pillars
    dirs = [
        '01 Architecture & Code',
        '02 Testing & Code Review',
        '03 Systems & Infrastructure',
        '04 Prompts, Context & Models',
        '05 Engineering Economics & Future'
    ]

    all_notes = []
    for d in dirs:
        for root, _, files in os.walk(REPO_ROOT / d):
            for f in files:
                if f.endswith('.md') and not f.endswith(' - original.md') and not f.endswith(' - Practitioner Rewrite.md'):
                    rel_p = os.path.normpath(os.path.relpath(os.path.join(root, f), REPO_ROOT))
                    all_notes.append(rel_p)

    extracted = []
    unmapped = []

    print(f"Total active notes in vault: {len(all_notes)}")

    for rel_path in sorted(all_notes):
        norm_p = os.path.normpath(rel_path)
        dest_path = REPO_ROOT / norm_p.replace('.md', ' - original.md')

        if norm_p in mapping:
            commit_ref, orig_path = mapping[norm_p]
            raw_bytes = subprocess.check_output(
                ['git', 'show', f'{commit_ref}:{orig_path}'],
                cwd=REPO_ROOT
            )
            content = raw_bytes.decode('utf-8')
            with open(dest_path, 'w', encoding='utf-8') as out_f:
                out_f.write(content)

            words = len(content.split())
            extracted.append((norm_p, orig_path, commit_ref, words))
        elif 'Retrieval-Augmented Generation and Context Architecture' in norm_p:
            # Special consolidation of 4 original RAG notes
            rag_combined = ["# Original RAG Notes Baseline (Commit f909d7a)\n"]
            total_words = 0
            for r_src in RAG_SOURCES:
                r_bytes = subprocess.check_output(['git', 'show', f'f909d7a:{r_src}'], cwd=REPO_ROOT)
                r_text = r_bytes.decode('utf-8')
                total_words += len(r_text.split())
                rag_combined.append(f"<!-- Source: {r_src} -->\n\n{r_text}\n\n---\n")

            combined_str = "\n".join(rag_combined)
            with open(dest_path, 'w', encoding='utf-8') as out_f:
                out_f.write(combined_str)

            extracted.append((norm_p, "4 RAG consolidated notes", "f909d7a", total_words))
        else:
            unmapped.append(norm_p)

    print(f"\n[SUCCESS] Extracted originals: {len(extracted)}")
    print(f"[INFO] Post-baseline notes without original: {len(unmapped)}")

    # Return data for reporting
    return extracted, unmapped

if __name__ == '__main__':
    main()
