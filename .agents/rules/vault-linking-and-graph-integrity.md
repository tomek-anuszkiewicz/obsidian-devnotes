---
trigger: always_on
description: Automatically maintain dual-layer bidirectional semantic linking and knowledge graph topology whenever notes are created or edited
---

# Vault Linking & Knowledge Graph Integrity Rule

Whenever creating, modifying, or refactoring notes across this Obsidian vault, the agent must actively, systematically, and deterministically maintain the knowledge graph topology. A note is not complete until its dual-layer semantic wiring is fully established.

---

## 1. Core Operating Architecture: Dual-Layer Connectivity

To eliminate disconnected prose and prevent orphaned knowledge, every note in this vault must maintain two distinct, complementary layers of graph connectivity:

```text
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: INLINE CONTEXTUAL WIKILINKS                        │
│ 2 to 5 embedded piped links [[Target Note|natural phrase]]   │
│ integrated seamlessly into body paragraphs at concept point.│
├─────────────────────────────────────────────────────────────┤
│ LAYER 2: STRUCTURAL REFERENTIAL SECTION                     │
│ ## Related Notes (or ## Relationship to the Knowledge Graph)│
│ 3 to 6 curated links with 1-sentence analytical rationales. │
└─────────────────────────────────────────────────────────────┘
```

- **Single-layer notes are strictly non-compliant**: Relegating all links to a bottom list produces detached prose; omitting the bottom referential section destroys quick scannability and structural indexing.

---

## 2. Core Topological Principles

### 1. Hub-and-Spoke Topology & Canonical Authorities
- The vault is organized around high-authority canonical hub notes anchoring each directory and domain pillar.
- **Satellite notes** must link upward to their primary domain hub and laterally to 2 to 3 closely related peer concepts.
- **Hub notes** must systematically catalog and contextually link downward to their member concepts and cross-link laterally to adjacent domain hubs.

### 2. Automatic Bidirectional Maintenance
- **Outbound Linking**: When creating or modifying a note, identify the **2 to 4 most conceptually relevant peer notes** across the 5-Layer System Stack:
  - `01 Architecture & Code/`
  - `02 Testing & Code Review/`
  - `03 Systems & Infrastructure/`
  - `04 Prompts, Context & Models/`
  - `05 Engineering Economics & Future/`
  Link to them directly both inline and in the referential section.
- **Inbound Linking**: If a newly created or updated note introduces a prerequisite, logical continuation, or counterpoint to an existing note, update that peer note to link back.

### 3. Zero Broken Links & Zero Orphans
- **Exact Target Matching**: Wikilinks must strictly match existing note file titles (or recognized aliases) excluding the `.md` extension.
- **Zero Orphans**: Every note must have at least one meaningful inbound link and at least one outbound link.
- **Central Index Registration**: Foundational pillars and canonical hubs must be cataloged in `_Explore.md`.

### 4. Semantic Sparsity Over "Hairball" Sprawl
- **Quality Over Quantity**: Do not turn the vault into a fully connected mesh ($K_n$) where "everything links to everything." Maintain a healthy "small-world network" topology (typically 4 to 7 high-signal links per note).
- Graph connections must be sharp, intentional, and high-signal. Prune obsolete or redundant links during refactorings.

### 5. Piped Canonical Hub Wikilink Standard
When embedding inline wikilinks to canonical domain hubs in body prose:
- **Never Paste Raw Unpiped Hub Titles into Sentences**:
  - ❌ *Incorrect*: `This accelerates the decay described in [[Software Decay and the Hidden Costs of Frictionless AI Code]] across teams.`
- **Always Use Natural Piped Anchors (`[[Hub Title|natural phrase]]`)**:
  - ✅ *Correct*: `This accelerates the decay described in [[Software Decay and the Hidden Costs of Frictionless AI Code|analyses of generative code entropy]] across teams.`
- **Exceptions**: Raw unpiped links are permitted only in formal root charters (`_Explore.md`, `Preamble.md`) and dedicated referential sections (`## Related Notes`).

### 6. Strict Isolation of Private Notes (One-Way Privacy Membrane)
- **Absolute Prohibition on Public-to-Private Links**: Never insert a wikilink (`[[...]]`) or markdown link from any public note to any note located in `_Private/` or any gitignored operational folder per [`one-way-privacy-membrane.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/rules/one-way-privacy-membrane.md).
- Private notes may freely reference public canonical hubs, but public notes must remain completely self-contained and unaware of private files.

