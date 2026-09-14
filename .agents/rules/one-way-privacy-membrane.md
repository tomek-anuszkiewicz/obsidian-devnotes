---
trigger: always_on
description: Strictly prohibit linking from public notes to private notes (_Private/) to prevent data leakage and broken links
---

# One-Way Privacy Membrane & Note Isolation Rule

Whenever creating, modifying, editing, or refactoring notes across this Obsidian vault, the agent must strictly enforce the boundary between public knowledge base notes and private notes.

---

## Core Rule: Strict One-Way Privacy Membrane

### 1. Absolute Prohibition: Never Link from Public to Private
- **NEVER** insert a wikilink (`[[...]]`), markdown link, or explicit reference from any public note to any note located in `_Private/` or any other private/untracked directory.
- Public notes comprise all files in:
  - `01 Code Architecture & Hardware Execution/`
  - `02 Harness, Governance & Verification/`
  - `03 Runtime Mesh & Observability/`
  - `04 Context Architecture & Model Steering/`
  - `05 Developer Ergonomics & Software Economics/`
  - Root navigational notes (e.g., `_Explore.md`, `Preamble.md`, `The 5-Layer System Stack for Agentic Software Engineering.md`).
- Even mentioning the title of a private note inside double brackets (`[[...]]`) in a public file is strictly prohibited.

---

### 2. Allowed Link Directionality Matrix

| Source Directory | Target Directory | Allowed? | Rationale |
| :--- | :--- | :--- | :--- |
| `Public Notes` | `_Private/` | ❌ **STRICTLY FORBIDDEN** | Leaks private titles, creates broken links in public publish/git clones. |
| `_Private/` | `Public Notes` | ✅ **ALLOWED** | Private strategies and profiles can and should reference canonical public frameworks. |
| `_Private/` | `_Private/` | ✅ **ALLOWED** | Private documents may freely cross-link with each other. |
| `Public Notes` | `Public Notes` | ✅ **ALLOWED** | Normal dual-layer graph linking across the 5-Layer Stack. |

---

### 3. Verification Protocol on Every Edit
Whenever creating or editing any public note:
1. **Target Verification**: Ensure every wikilink targets exclusively an existing public note in the 5-Layer Stack.
2. **Zero Information Leakage**: Ensure no private concepts, personal diagnostic profiles, or private filenames appear in public note frontmatter, body, or referential sections.
3. **Graph Integrity**: Maintain the public knowledge graph as a 100% self-contained, publishable unit with zero broken dependencies.
