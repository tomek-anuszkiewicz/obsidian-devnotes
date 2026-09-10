---
trigger: always_on
description: Automatically maintain dual-layer bidirectional semantic linking and knowledge graph topology whenever notes are created or edited
---

# Vault Linking and Graph Integrity Rule

Whenever creating, modifying, or refactoring notes in this Obsidian vault, the agent must actively and systematically maintain the knowledge graph structure.

## Core Objectives & Operating Principles

1. **Mandatory Dual-Linking Standard (Dual-Layer Architecture)**:
   Every note in the vault must maintain two distinct, complementary layers of connectivity:
   - **Layer 1: Inline Contextual Wikilinks (`[[Target Note|natural phrase]]`)**: 2 to 5 links embedded directly into body paragraphs at the precise moments concepts are introduced, compared, or synthesized.
   - **Layer 2: Structural Referential Section (`## Related Notes` / `## Relationship to the Knowledge Graph`)**: 3 to 6 curated links at the bottom of the document with 1-sentence analytical rationales explaining the architectural or conceptual relationship.
   - *Single-layer notes are strictly non-compliant*: relegating all links to a bottom list produces detached prose; omitting the bottom section destroys quick scannability.

2. **Hub-and-Spoke Topology & Canonical Authorities**:
   - The vault is organized around high-authority canonical hub notes anchoring each directory and domain pillar.
   - Satellite notes must link upward to their primary domain hub and laterally to 2 to 3 closely related peer concepts.
   - Hub notes must systematically catalog and contextually link downward to their member concepts and cross-link to adjacent hubs.

3. **Automatic Bidirectional Maintenance**:
   - **Outbound Linking**: When creating or modifying a note, identify the **2 to 4 most conceptually relevant peer notes** across the vault (`01 Architecture & Systems/`, `02 Engineering Practice/`, `03 LLM Theory & Cognition/`, `04 Human & Future Landscape/`) and link to them directly both inline and referentially.
   - **Inbound Linking**: If a newly created or updated note provides a prerequisite, logical continuation, or counterpoint to an existing note, update that peer note to link back.

4. **Zero Broken Links & Zero Orphans**:
   - Wikilinks must strictly match existing note file titles (or recognized aliases) excluding the `.md` extension.
   - Never leave an orphaned note: every note must have at least one meaningful inbound link and at least one outbound link.
   - Foundational pillars and canonical hubs must be registered in `_Explore.md`.

5. **Semantic Inline Linking Over "Hairball" Sprawl**:
   - **Quality over Quantity**: Do not turn the vault into a fully connected mesh ($K_n$) where "everything links to everything." Maintain a healthy "small-world network" topology (typically 4 to 7 high-signal links per note).
   - Graph connections must be sharp, intentional, and high-signal. Prune obsolete or redundant links during refactorings.
