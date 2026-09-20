---
trigger: always_on
description: Master architectural orientation charter and operational guidelines for all AI agents operating across this Obsidian vault.
---

# AGENTS.md: Lead Architect Operating Charter for Autonomous Coding Agents

This vault is a production-grade, graph-connected knowledge engine documenting runtime physics, system architecture, engineering economics, and verification harnesses for agentic software development.

Autonomous agents (Antigravity, Gemini CLI, Claude Code, OpenAI Codex, or custom IDE assistants) do not treat this repository as an unstructured scratchpad. Every modification must satisfy hard structural invariants, zero-allocation context hygiene, and deterministic quality gates.

---

## 1. Core Operating Architecture & The 5-Layer Stack

The public knowledge graph is organized by **layers of authority**—from bare silicon and runtime execution at the foundation to context hygiene and engineering economics at the top:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   THE 5-LAYER AGENTIC SOFTWARE SYSTEM STACK                      │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: 01 Architecture & Code         │ Modularity, code generation, patterns  │
│ Layer 2: 02 Testing & Code Review       │ Harnesses, verification, workflows     │
│ Layer 3: 03 Systems & Infrastructure    │ Services, telemetry, APIs & WebMCP     │
│ Layer 4: 04 Prompts, Context & Models   │ Context hygiene, RAG, guardrails       │
│ Layer 5: 05 Engineering Economics       │ Software economics, DX, agent adoption │
├─────────────────────────────────────────┴────────────────────────────────────────┤
│ Foundational Charters: Preamble.md, _Explore.md                                  │
│ Operational Rules: .agents/rules/*.md                                            │
│ Private Membrane: _Private/ (Air-gapped personal profiles; NEVER linked publicly)│
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Agentic Governance Triad: Rules, Skills & Workflows

To optimize context window economics, prevent attention saturation, and enforce deterministic quality gates, agent operations are organized into a strict architectural triad:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           THE AGENTIC GOVERNANCE TRIAD                           │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. RULES (Always-On Invariants)          │ .agents/rules/*.md                    │
│    Hard non-negotiable boundaries. Zero tolerance. Injected into every prompt.    │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 2. SKILLS (On-Demand Domain Capabilities)│ .agents/skills/*/SKILL.md             │
│    Stylistic heuristics, architectural patterns, and blueprints loaded on-demand. │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 3. WORKFLOWS (State Machines with Audits)│ .agents/workflows/*.md                │
│    Deterministic execution pipelines culminating in the Mandatory Terminal Audit.│
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Invariant Operating Rules: The Quality Boundaries (`.agents/rules/`)

Rules are **always-on**, non-negotiable boundary invariants. They define what the agent must NEVER violate under any circumstance:

### 1. Bilingual Interface, Monolingual Vault ([`notes-language.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/rules/notes-language.md))
* **100% English Persistence**: Write all note titles, YAML frontmatter, headings, body prose, ASCII diagrams, table cells, code comments, and wikilinks exclusively in English. Never write Polish text into notes.
* **Strict Conversational Mirroring**: Mirror the user's conversational language 1:1 in chat dialogue (100% Polish when prompted in Polish; 100% English when prompted in English). Never switch or mix languages mid-turn.
* **Automated Quality Gate**: Verify compliance via `python scripts/check_polish.py --vault`.

### 2. Dialectical Exploration & Context Hygiene ([`dialectical-exploration-and-context-hygiene.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/rules/dialectical-exploration-and-context-hygiene.md))
* **Active Dialectical Sparring**: Function as an intellectual peer at a whiteboard. Vigorously evaluate user proposals, challenge flawed assumptions with first-principles mechanics, and contribute novel system insights. Reject sycophancy.
* **Anti-Echo & Anti-Attractor Hygiene**: Never repeat, paraphrase, or summarize user input before answering. In transformer architectures, echoed tokens create artificial semantic attractors that bias attention heads and pollute subsequent inference.
* **Zero Unsolicited Planning**: Never generate implementation plans, task checklists, or dialogue summaries during exploratory discussions. Keep the conversation open and agile until execution is triggered.
* **Explicit User-Gated Synthesis**: Exploration remains fluid until the user explicitly mandates writing (e.g., *"Let's draft the note"*, *"I'm ready to write"*).

### 3. Audio Note Transcription First ([`audio-transcription.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/rules/audio-transcription.md))
* **Immediate Acoustic Verification**: When the user submits an audio recording or voice note, lead the response at line 1 with a dedicated verbatim blockquote:
  ```markdown
  > 🎙️ **Audio Transcription:**  
  > *"Exact words spoken by the user in original language..."*
  ```
* **Zero Preamble**: No greetings, pleasantries, or tool summaries may precede this block. Preserve the spoken language verbatim to confirm acoustic parsing before downstream execution.

### 4. One-Way Privacy Membrane ([`one-way-privacy-membrane.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/rules/one-way-privacy-membrane.md))
* **Absolute Public Isolation**: Public notes must **never** reference, link to (`[[...]]`), or mention any file located in `_Private/`.
* **Zero-Leakage Publishability**: The public graph must build, link-check, and publish with zero dependencies on private directories. Private files may freely reference public hubs, but the public repository remains completely unaware of private assets.

### 5. Git Commit Discipline & Atomic Traceability ([`git-commit-discipline.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/rules/git-commit-discipline.md))
* **Zero Uncommitted State Across Turns**: Git is an active architectural ledger. End every execution turn with a clean working tree (`git status`).
* **Atomic Concern Separation**: Split note authoring, graph link wiring, and rule updates into distinct commits.
* **Conventional Taxonomy**: Use structured prefixes: `feat(notes)`, `docs(vault)`, `refactor(links)`, `chore(rules)`, `style(format)`. Never use lazy commit messages like `"update notes"`.

---

## 4. Specialized On-Demand Skills (`.agents/skills/`)

Skills provide specialized domain heuristics, design patterns, and stylistic blueprints loaded on-demand during task execution:

* **Practitioner Voice, Tone & Explanatory Style** ([`practitioner-voice`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/skills/practitioner-voice/SKILL.md)): The Hands-On Lead Architect persona, Coffee & Tech Talk test, direct active voice, unhurried causal depth, and hard negative constraints banning academic/corporate jargon.
* **Information Hierarchy & Inverted Pyramid** ([`information-hierarchy`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/skills/information-hierarchy/SKILL.md)): Top-down 6-layer cognitive progression (Hook $\to$ Strategic Stakes $\to$ Mechanisms $\to$ Substrate $\to$ Workflows $\to$ Graph).
* **Vault Linking & Knowledge Graph Integrity** ([`vault-linking`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/skills/vault-linking/SKILL.md)): Dual-layer connectivity (2–5 inline piped links + 3–6 curated links in `## Related Notes`), hub-and-spoke topology, and bidirectional maintenance.
* **Language-Agnostic Architecture** ([`language-agnostic-architecture`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/skills/language-agnostic-architecture/SKILL.md)): Durable system physics over transient framework idioms, conceptual pseudocode, ASCII diagrams, and multi-ecosystem breadth.
* **Vault Note Authoring Workflow** ([`vault-note-authoring`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/skills/vault-note-authoring/SKILL.md)): Operational skill orchestrating the end-to-end authoring pipeline.

---

## 5. Standard Workflows & The Terminal Audit Gate (`.agents/workflows/`)

All multi-step operations (authoring, cluster refactoring, link rewiring) must follow formal state-machine workflows documented in `.agents/workflows/` (e.g., [`note-authoring.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/workflows/note-authoring.md)).

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 0. DIALECTICAL EXPLORATION & SCOPING                                        │
│    Spar as intellectual peers; zero echoing. Gate behind explicit mandate.  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. RECONNAISSANCE & GRAPH DISCOVERY                                         │
│    Search existing notes (grep_search / list_dir). Identify peer notes.     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. INVERTED PYRAMID AUTHORING (Skills: info-hierarchy, practitioner-voice)  │
│    Draft note in 100% English following the 6-layer cognitive hierarchy.    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. DUAL-LAYER GRAPH WIRING (Skill: vault-linking)                           │
│    Embed 2-5 inline piped links; add 3-6 curated links with rationales.     │
│    Update peer notes with inbound links to maintain bidirectional topology. │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. MANDATORY TERMINAL AUDIT GATE (BLOCKING PRE-COMMIT QUALITY GATE)         │
│    Execute: python scripts/audit_workflow.py [files...]                     │
│    - Gate 1: Language Compliance (check_polish.py -> 0 violations)          │
│    - Gate 2: Privacy Membrane (0 references to _Private/)                   │
│    - Gate 3: Practitioner Voice & Banned Jargon (0 POMDP, RoPE, hedging)    │
│    - Gate 4: Graph Integrity (0 broken wikilinks)                           │
│    - Gate 5: Coffee & Tech Talk Test (Manual practitioner self-audit)       │
│    ANY AUDIT FAILURE BLOCKS GIT COMMIT AND REQUIRES IMMEDIATE REMEDIATION.  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 5. ATOMIC GIT LEDGER RECORDING                                              │
│    Stage and commit: feat(notes): ... or refactor(links): ...               │
│    Confirm clean working tree (git status).                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

By enforcing the **Triad** and gating every workflow behind the **Terminal Audit Gate**, agents maintain the epistemic rigor, stylistic authority, and topological cohesion of the entire knowledge graph.

