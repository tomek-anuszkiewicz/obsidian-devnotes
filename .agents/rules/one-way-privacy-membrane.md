---
trigger: always_on
description: Strictly prohibit linking from public notes to private notes (_Private/) to prevent data leakage and broken links
---

# One-Way Privacy Membrane & Note Isolation Rule

Whenever creating, modifying, editing, or refactoring notes across this Obsidian vault, the agent must strictly enforce the boundary between public knowledge base notes and private operational files. The vault operates a strict **one-way privacy membrane**.

---

## 1. Core Operating Architecture: The One-Way Membrane

The public knowledge base is designed to be completely self-contained, reproducible, and publishable without dependencies on private operational documents:

```text
       PUBLIC KNOWLEDGE GRAPH                        PRIVATE VAULT
    ┌───────────────────────────┐             ┌───────────────────────────┐
    │ 01 Architecture & Code    │             │ _Private/                 │
    │ 02 Testing & Code Review  │             │ - Strategic Profiles      │
    │ 03 Systems & Infras.      │             │ - Meeting Playbooks       │
    │ 04 Prompts & Context      │             │ - Cognitive Telemetry     │
    │ 05 Engineering Economics  │             │ - Career Positioning      │
    └─────────────▲─────────────┘             └─────────────┬─────────────┘
                  │                                         │
                  │              (ALLOWED REFERENCE)        │
                  └─────────────────────────────────────────┘
                   (STRICT PROHIBITION: Public NEVER links to Private)
```

---

## 2. Invariant Rules & Directionality Matrix

### 1. Absolute Prohibition: Public Notes Never Reference Private Notes
- **NEVER** insert an Obsidian wikilink (`[[...]]`), markdown link, or explicit reference from any public note to any note located in `_Private/` or any gitignored operational directory.
- Public notes comprise all files in:
  - `01 Architecture & Code/`
  - `02 Testing & Code Review/`
  - `03 Systems & Infrastructure/`
  - `04 Prompts, Context & Models/`
  - `05 Engineering Economics & Future/`
  - Root navigational notes (e.g., `_Explore.md`, `Preamble.md`, `The 5-Layer System Stack for Agentic Software Engineering.md`).
- Even mentioning the title of a private note inside double brackets (`[[...]]`) in a public file is strictly prohibited.

### 2. Allowed Link Directionality Matrix

| Source Directory | Target Directory | Allowed? | Architectural Rationale |
| :--- | :--- | :---: | :--- |
| `Public Notes` | `_Private/` | ❌ **STRICTLY FORBIDDEN** | Leaks private titles, creates broken links in public git clones / publishing targets. |
| `_Private/` | `Public Notes` | ✅ **ALLOWED** | Private strategies and profiles ground themselves in canonical public frameworks. |
| `_Private/` | `_Private/` | ✅ **ALLOWED** | Private documents freely cross-link across personal profiles and playbooks. |
| `Public Notes` | `Public Notes` | ✅ **ALLOWED** | Standard dual-layer graph linking across the 5-Layer System Stack. |

---

## 3. Verification Protocol on Every Edit

Whenever creating or modifying any public note, execute this 3-step verification:
1. **Target Inspection**: Verify that every wikilink (`[[...]]`) points exclusively to an existing public note within the 5-Layer Stack or root charters.
2. **Zero Information Leakage**: Confirm no personal psychological traits, proprietary career details, or private filenames appear in public frontmatter, body prose, or referential lists.
3. **Graph Independence**: The public knowledge graph must build, link-check, and publish with zero dangling dependencies when `_Private/` is ignored or absent.
