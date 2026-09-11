---
name: information-hierarchy
description: Principles, rules, and workflows for organizing notes, documentation, and architectural artifacts using the Inverted Pyramid model, cognitive hierarchy, and reader engagement. Use when authoring, refactoring, restructuring, or reviewing notes in this Obsidian vault.
---

# Information Hierarchy and the Inverted Pyramid Model

This skill governs how notes, architectural frameworks, and technical documents are structured within this Obsidian vault. It enforces top-down **cognitive hierarchy** and **reader engagement**, ensuring that the most valuable, transformative, and decisive insights lead the document rather than being buried at the bottom.

---

## 1. The Core Philosophy: The Inverted Pyramid

Readers absorb information in a top-down narrative. When opening a note, the reader's attention and cognitive energy are at their peak. 

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. THE HOOK & CORE THESIS                                   │
│    The bold paradigm shift, economic inversion, or          │
│    decisive architectural conclusion.                       │
├─────────────────────────────────────────────────────────────┤
│ 2. STRATEGIC & PSYCHOLOGICAL DIMENSIONS                     │
│    Root problems, human bottlenecks, systemic traps         │
│    (e.g., Learned Helplessness, Frankenstein Phase).        │
├─────────────────────────────────────────────────────────────┤
│ 3. CORE ARCHITECTURAL PATTERNS & SOLUTIONS                  │
│    The primary mechanisms that solve the dilemma            │
│    (e.g., Shadow-Twin, Exploratory Pruning, Explicit Code). │
├─────────────────────────────────────────────────────────────┤
│ 4. SUBSTRATE & MECHANICAL SYMPATHY                          │
│    Hardware realities, cache lines (L1i vs D-cache),        │
│    compiler optimization, memory layout (DOD/SoA).          │
├─────────────────────────────────────────────────────────────┤
│ 5. TACTICAL EXECUTION & DEVELOPER WORKFLOWS                 │
│    Granular commit sequences, review rules, operational     │
│    checklists, and implementation recipes.                  │
├─────────────────────────────────────────────────────────────┤
│ 6. SYNTHESIS & RELATIONSHIP TO THE KNOWLEDGE GRAPH          │
│    Summary principles and dual-layer curated wikilinks.     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Preventing the "Bottom-Heavy Accumulation Trap"

During collaborative discussions and iterative note expansion, an agent naturally tends to append newly introduced insights, corrections, and profound realizations to the bottom of the active document.

Over time, this creates a toxic **inverted pyramid**:
- Older, generic, or lower-signal introductory prose sits at the top.
- The freshest, deepest, and most impactful conclusions (e.g., *Exploratory Pruning*, *The Ship of Theseus Alienation*, *Inverted Code Economics*) get trapped at the bottom as appendices.

### The Re-Hierarchization Rule:
Whenever integrating new insights or refactoring an existing note:
1. **Analyze Conceptual Rank**: Does the new thought represent a foundational thesis, a psychological shift, a core pattern, or a tactical detail?
2. **Promote Immediately**:
   - If it is a **Core Thesis / Paradigm Shift** $\rightarrow$ weave it into the opening 20–50 lines.
   - If it is a **Reconnaissance / First Step Pattern** (e.g. Exploratory Pruning) $\rightarrow$ place it at the beginning of the technical methodology (Phase 1).
   - If it is an **Operational Detail** (e.g. commit rules) $\rightarrow$ place it in the downstream tactical execution section.
3. **Never Append as an Afterthought**: If a concept feels critical, it belongs in the top half of the document.

---

## 3. 100% Content and Thought Preservation Standard

Re-hierarchizing a document for reader engagement **must never destroy content**:
- **Zero Loss of Meaning**: Preserve all substantive thoughts, edge-case nuances, architectural trade-offs, and conceptual insights.
- **Preserve Formalisms**: Keep all mathematical equations (e.g., $\Delta = \text{Response}_{\text{Legacy}} - \text{Response}_{\text{Shadow}}$), ASCII architecture diagrams, code examples, and citation references.
- **Preserve and Enhance Links**: Ensure all inline contextual wikilinks (`[[Target Note|phrase]]`) and bottom referential sections remain intact, unbroken, and bidirectionally linked.
- The goal is **reorganizing, repositioning, and polishing the narrative flow**, not truncating or simplifying.

---

## 4. Practical Workflow for Auditing and Restructuring a Note

When reviewing or refactoring an existing note for information hierarchy:

1. **Step 1: Outline Extraction**
   Read the file and extract all headings (`#`, `##`, `###`). Identify the conceptual progression.
2. **Step 2: Identify Buried Treasures**
   Scan the bottom 30% of the document. Ask:
   - *Is there a profound economic inversion here?* (e.g. $Cost(500\text{ lines}) \approx 0$).
   - *Is there a critical psychological barrier explained here?* (e.g. Learned Helplessness).
   - *Is there a prerequisite workflow here that must happen first?* (e.g. Exploratory Pruning before Shadow-Twin).
   - *Is there a golden mental model or decision matrix here?* (e.g. Reusable Implementation vs Repeatable Instruction).
3. **Step 3: Restructure Top-Down**
   Re-order sections so that the reader encounters the highest-signal concepts first:
   - Hook $\rightarrow$ Strategic Stakes $\rightarrow$ Core Mechanisms $\rightarrow$ Mechanical Sympathy $\rightarrow$ Tactical Rules $\rightarrow$ Graph.
4. **Step 4: Verify Substantive Completeness**
   Perform a line-by-line diff to confirm that zero insights or technical details were dropped.
5. **Step 5: Atomic Git Commit**
   Commit the restructuring with a descriptive, intent-driven message:
   `refactor(structure): re-hierarchize [Note Title] for top-down reader engagement`.
