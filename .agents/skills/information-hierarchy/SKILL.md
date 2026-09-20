---
name: information-hierarchy
description: The 6-layer cognitive hierarchy and inverted pyramid model for structuring vault notes from hook and economic inversion down to technical mechanics.
---

# Information Hierarchy & Inverted Pyramid Skill

Whenever creating, modifying, updating, or refactoring notes and architectural documentation in this Obsidian vault, the agent must strictly structure content according to the **Inverted Pyramid model** and **top-down cognitive hierarchy**. This ensures that the most valuable, transformative, and decisive insights lead the document rather than being buried at the bottom.

---

## Core Architecture: The Inverted Pyramid

Readers absorb information in a top-down narrative. When opening a note, reader attention and cognitive energy are at their peak. 

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

## Core Operating Principles

1. **Lead with the High-Impact Hook & Core Thesis**:
   - The opening 20–50 lines of every note must deliver the most decisive, paradigm-shifting conclusion, economic inversion, or conceptual breakthrough.
   - Never bury foundational conclusions, core decision matrixes, or defining mental models at the bottom of a document. Engage the reader immediately with high-signal value.

2. **Top-Down Cognitive Progression**:
   Structure notes following a consistent, logical descent through the 6-layer cognitive hierarchy shown above:
   - **Layer 1: The Hook & Core Thesis** (Paradigm shifts, economic inversions, the central dilemma).
   - **Layer 2: Strategic & Psychological Dimensions** (Root problems, human bottlenecks, systemic traps like Learned Helplessness or the Frankenstein Phase).
   - **Layer 3: Core Architectural Patterns & Solutions** (The primary mechanisms that solve the problem, e.g. Exploratory Pruning, Shadow-Twin, Explicit Code).
   - **Layer 4: Substrate & Mechanical Sympathy** (Hardware realities, L1i vs D-cache dynamics, compiler inlining, memory layouts).
   - **Layer 5: Tactical Execution & Developer Workflows** (Granular commit sequences, review rules, operational checklists).
   - **Layer 6: Synthesis & Knowledge Graph Relationships** (Summary axioms and dual-layer curated wikilinks).

3. **Eliminating the "Bottom-Heavy Accumulation Trap"**:
   - When integrating user feedback, corrections, or newly introduced insights during conversations, **never default to simply appending them to the bottom of the document**.
   - Analyze where the new insight belongs hierarchically:
     - If it represents a **Core Thesis / Paradigm Shift** $\rightarrow$ weave it into the opening 20–50 lines.
     - If it represents a **Reconnaissance / First Step Pattern** (e.g. Exploratory Pruning) $\rightarrow$ place it at the beginning of the technical methodology (Phase 1).
     - If it represents an **Operational Detail** (e.g. commit rules) $\rightarrow$ place it in the downstream tactical execution section.
   - Never append critical concepts as an afterthought.

4. **100% Content & Thought Preservation Standard**:
   - Re-hierarchization must be purely structural. **Never discard or dilute existing substantive thoughts, technical nuances, code blocks, ASCII diagrams, or mathematical formulas**.
   - Rearrange, re-order, and polish the narrative flow while preserving 100% of the conceptual substance.

---

## Practical Note Auditing & Restructuring Workflow

When reviewing or refactoring an existing note for information hierarchy:

1. **Step 1: Outline Extraction**: Read the file and extract all headings (`#`, `##`, `###`). Map the conceptual progression.
2. **Step 2: Identify Buried Treasures**: Scan the bottom 30% of the document. Identify profound economic inversions, critical psychological barriers, prerequisite workflows, or golden mental models that are languishing in appendices or trailing sections.
3. **Step 3: Restructure Top-Down**: Re-order sections to encounter the highest-signal concepts first:
   $\text{Hook} \rightarrow \text{Strategic Stakes} \rightarrow \text{Core Mechanisms} \rightarrow \text{Mechanical Sympathy} \rightarrow \text{Tactical Rules} \rightarrow \text{Graph}$.
4. **Step 4: Verify Substantive Completeness**: Perform a diff to confirm zero insights, formulas, code snippets, or links were lost.
5. **Step 5: Atomic Git Commit**: Commit the restructuring with a descriptive, intent-driven message:
   `refactor(structure): re-hierarchize [Note Title] for top-down reader engagement`.
