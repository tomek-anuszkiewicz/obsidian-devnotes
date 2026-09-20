---
trigger: manual
description: Standard operating workflow for researching, drafting, wiring, and verifying new or significantly refactored notes across the Obsidian vault.
---

# Standard Operating Workflow: Note Authoring & Synthesis

This workflow defines the invariant, multi-phase execution pipeline for creating or deeply revising notes across the 5-Layer System Stack. Every phase must be completed in order. **Workflows must never be considered complete until the Mandatory Terminal Audit Gate returns 100% clean PASS.**

---

## The 6-Phase Pipeline Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 0: DIALECTICAL EXPLORATION & SCOPING                                  │
│ - Spar as technical peers; zero echoing of user input.                      │
│ - Challenge weak assumptions; inject systems mechanics.                     │
│ - GATE: Explicit user mandate ("ready to write", "let's draft the note").   │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 1: RECONNAISSANCE & GRAPH TOPOLOGY DISCOVERY                          │
│ - Search existing notes (grep_search / list_dir).                           │
│ - Identify 2-4 peer notes for lateral wiring and canonical domain hub.      │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 2: INVERTED PYRAMID AUTHORING (Skills: info-hierarchy, practitioner)  │
│   - Draft note in 100% English following the 6-layer cognitive hierarchy.   │
│   - Lead with high-impact hook and economic inversion in lines 1-50.        │
│   - Apply Practitioner Voice: plain language, mechanisms over terminology.  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. DUAL-LAYER GRAPH WIRING (Skill: vault-linking)                           │
│   Embed 2-5 inline piped links; add 3-6 curated links with rationales.      │
│   Update peer notes with inbound links to maintain bidirectional topology.  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. MANDATORY TERMINAL AUDIT GATE (BLOCKING PRE-COMMIT VERIFICATION)         │
│   - Run: python scripts/audit_workflow.py [files...]                        │
│     Gate 1: Language Compliance (check_polish.py -> 0 violations)           │
│     Gate 2: Privacy Membrane (0 references to _Private/)                    │
│     Gate 3: Practitioner Voice & Jargon (0 formalisms, 0 hedging, 0 jargon) │
│     Gate 4: Graph Integrity (0 broken wikilinks to non-existent notes)      │
│     Gate 5: Whiteboard / Peer Conversation Test (Manual self-audit)         │
│   - ANY FAILURE BLOCKS COMMIT AND MANDATES IMMEDIATE IN-PLACE REMEDIATION.  │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 5: ATOMIC GIT LEDGER RECORDING                                        │
│ - Stage target files: git add [files...]                                    │
│ - Atomic commit with conventional taxonomy: feat(notes): ...                │
│ - Confirm clean working tree (git status).                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase Breakdown & Execution Mechanics

### Phase 0: Dialectical Exploration & Scoping
* **Peer-Level Sparring**: Critique user proposals, evaluate trade-offs, and inject concrete systems mechanics (caches, query plans, concurrency bottlenecks).
* **Anti-Echo & Context Hygiene**: Never repeat user statements or generate unsolicited task plans.
* **Gated Synthesis**: Do not create or edit files until the user explicitly mandates writing.

### Phase 1: Reconnaissance & Graph Topology Discovery
* Scan the vault (`list_dir`, `grep_search`) to locate existing notes in the domain pillar.
* Map where the new concept sits within the 5-Layer Stack:
  - Layer 1: Architecture & Code
  - Layer 2: Testing & Code Review
  - Layer 3: Systems & Infrastructure
  - Layer 4: Prompts, Context & Models
  - Layer 5: Engineering Economics
* Identify the primary canonical hub and 2 to 4 lateral peer notes.

### Phase 2: Inverted Pyramid Authoring
* Load and apply skills:
  - `.agents/skills/information-hierarchy/SKILL.md`
  - `.agents/skills/practitioner-voice/SKILL.md`
  - `.agents/skills/language-agnostic-architecture/SKILL.md`
* Structure content top-down:
  1. *Hook & Core Thesis* (Bold paradigm shift or economic inversion in lines 1–50)
  2. *Strategic & Psychological Dimensions* (Systemic traps, failure modes)
  3. *Core Architectural Patterns & Solutions* (Primary mechanisms)
  4. *Substrate & Mechanical Sympathy* (Hardware realities, memory, runtime)
  5. *Tactical Execution & Developer Workflows* (Playbooks, recipes)
  6. *Synthesis & Knowledge Graph Relationships*
* Language: Strictly 100% English across frontmatter, prose, tables, diagrams, and comments.

### Phase 3: Dual-Layer Graph Wiring
* Load and apply skill:
  - `.agents/skills/vault-linking/SKILL.md`
* **Layer 1**: Embed 2 to 5 inline piped links (`[[Target Note|natural phrase]]`) in body paragraphs.
* **Layer 2**: Populate `## Related Notes` with 3 to 6 curated links, each accompanied by a 1-sentence analytical rationale explaining the conceptual relationship.
* **Bidirectional Links**: Update 2 to 3 peer notes with inbound references pointing to the new note.

### Phase 4: Mandatory Terminal Audit Gate (Non-Negotiable)
Before any git commit, run the automated workflow audit:
```powershell
python scripts/audit_workflow.py [path/to/note.md]
```
The script evaluates five deterministic gates:
1. **Language Compliance**: Must return 0 Polish words or phrases.
2. **One-Way Privacy Membrane**: Must have 0 references or links to `_Private/`.
3. **Practitioner Writing Style**: Must have 0 academic formalisms, 0 corporate hedging phrases, 0 manufactured jargon, and 0 stacked abstractions.
4. **Graph Link Integrity**: Every wikilink `[[Target Note]]` must resolve to an existing public note file in the vault.
5. **The Whiteboard / Peer Conversation Audit**: Perform a final qualitative read:  
   *“Could I say this sentence naturally to a senior engineer sitting next to me? Does it explain the underlying mechanics clearly instead of hiding behind terminology?”*

> [!CAUTION]
> If any audit check fails, **stop immediately**. Remediate the violations in-place and re-run the audit. Never bypass this gate.

### Phase 5: Atomic Git Ledger Recording
* Stage only the logically related files for this unit of work.
* Commit with structured conventional prefixes per `.agents/rules/git-commit-discipline.md`:
  - `feat(notes): add [Note Title]`
  - `refactor(links): wire bidirectional graph links for [Note Title]`
* Verify working tree is completely clean:
  ```powershell
  git status
  ```
