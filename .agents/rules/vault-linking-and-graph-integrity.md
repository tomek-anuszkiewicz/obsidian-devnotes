---
trigger: always_on
description: Automatically maintain bidirectional semantic linking and knowledge graph topology whenever notes are created or edited
---

# Vault Linking and Graph Integrity Rule

Whenever creating, modifying, or refactoring notes in this Obsidian vault, the agent must actively and systematically maintain the knowledge graph structure.

## Core Objectives & Operating Principles

1. **Automatic Post-Edit Linking (Bidirectional)**:
   - **Outbound Linking**: When creating or modifying a note, identify the **2 to 4 most conceptually relevant peer notes** across the vault (`01 Architecture & Systems/`, `02 Engineering Practice/`, `03 LLM Theory & Cognition/`, `04 Human & Future Landscape/`) and link to them directly.
   - **Inbound Linking**: Evaluate the primary peer notes. If the newly created or updated note provides a direct prerequisite, logical continuation, or counterpoint to an existing note, update that existing note to link back.

2. **Semantic Inline Linking Over "Hairball" Sprawl**:
   - **Quality over Quantity**: Do not turn the vault into a fully connected graph ($K_n$) where "everything links to everything." Dense meshes degrade the signal of the knowledge graph.
   - **Target Density**: Maintain a healthy "small-world network" topology (typically 4 to 7 high-signal links per note).
   - **Inline Contextual Links**: Prioritize links embedded naturally into the prose (`[[Target Note|natural phrase]]`) explaining *why* the connection exists, rather than appending large associative link lists at the end of files.

3. **Zero Broken Links & Zero Orphans**:
   - Wikilinks must strictly match existing note file titles (excluding the `.md` extension).
   - Never leave an orphaned note: every note must have at least one meaningful inbound link and at least one outbound link.
   - When a note introduces a foundational concept or high-level pillar, ensure it is surfaced in `_Explore.md`.

4. **Graph Pruning & Entropy Control**:
   - If a note refactoring renders certain associative links obsolete or duplicative, prune them to keep graph connections sharp and high-signal.
