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
   - **Outbound Linking**: When creating or modifying a note, identify the **2 to 4 most conceptually relevant peer notes** across the 5-Layer System Stack (`01 Code Architecture & Hardware Execution/`, `02 Harness, Governance & Verification/`, `03 Runtime Mesh & Observability/`, `04 Model Cognition & Latent Space/`, `05 Operator Psychology & Macro-Economics/`) and link to them directly both inline and referentially.
   - **Inbound Linking**: If a newly created or updated note provides a prerequisite, logical continuation, or counterpoint to an existing note, update that peer note to link back.

4. **Zero Broken Links & Zero Orphans**:
   - Wikilinks must strictly match existing note file titles (or recognized aliases) excluding the `.md` extension.
   - Never leave an orphaned note: every note must have at least one meaningful inbound link and at least one outbound link.
   - Foundational pillars and canonical hubs must be registered in `_Explore.md`.

5. **Semantic Inline Linking Over "Hairball" Sprawl**:
   - **Quality over Quantity**: Do not turn the vault into a fully connected mesh ($K_n$) where "everything links to everything." Maintain a healthy "small-world network" topology (typically 4 to 7 high-signal links per note).
   - Graph connections must be sharp, intentional, and high-signal. Prune obsolete or redundant links during refactorings.

6. **Strict Isolation of Private Notes (Zero Public-to-Private Links)**:
   - **Absolute Prohibition on Outbound Public-to-Private Links**: Never, under any circumstances, insert a wikilink (`[[...]]`) or markdown link from a public note (any note in the 5-Layer Stack, root directories, or public hubs) to a private note located in `_Private/` or any other gitignored/private directory.
   - **One-Way Privacy Membrane**:
     - `_Private/` $\rightarrow$ `_Private/`: **Allowed**. Private notes may freely cross-link with each other.
     - `_Private/` $\rightarrow$ `Public Notes`: **Allowed**. Private playbooks and strategies can and should link out to canonical public architectural hubs.
     - `Public Notes` $\rightarrow$ `_Private/`: **STRICTLY FORBIDDEN**. Public notes must remain completely self-contained and unaware of private notes.
     - `Public Notes` $\rightarrow$ `Public Notes`: **Allowed**. Standard dual-layer graph connectivity.
   - **Rationale**:
     - *Leak Prevention*: Prevents private note titles, cognitive profiles, personal strategies, or confidential topics from leaking into public graph views, Obsidian Publish deployments, or open-source repositories.
     - *Broken Link Prevention*: In cloned or published versions of the vault where `_Private/` is gitignored, any outbound link to a private note renders as an orphaned, broken link, violating Principle 4 (*Zero Broken Links*).

7. **Piped Canonical Hub Wikilink Standard**:
   - When embedding inline wikilinks to canonical domain hubs in body prose:
     - **Never Paste Raw Unpiped Hub Titles into Sentences**:
       - ❌ *Incorrect*: `This accelerates the decay described in [[Software Entropy and the Zero-Friction Trap]] across teams.`
     - **Always Use Natural Piped Anchors (`[[Hub Title|natural phrase]]`)**:
       - ✅ *Correct*: `This accelerates the decay described in [[Software Entropy and the Zero-Friction Trap|analyses of generative code entropy]] across teams.`
     - **Exceptions**: Raw unpiped links are permitted only in formal root charters (`_Explore.md`, `Preamble.md`) and dedicated referential sections (`## Related Notes` / `## Relationship to the Knowledge Graph`).

