---
trigger: always_on
description: Mandatory granular git commits with intent-driven messages after modifying or refactoring notes
---

# Git Commit Discipline & Granularity Rule

Whenever creating, modifying, updating, or refactoring notes, documentation, rules, or schemas across this Obsidian vault, the agent must systematically record changes via Git. Version control in this knowledge base is an active architectural ledger, not a sporadic backup mechanism.

---

## 1. Core Operating Principles: Atomic Traceability

Uncommitted state across conversation turns introduces context fragmentation, increases rollback blast radiuses, and obscures architectural provenance:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. SINGLE LOGICAL CHANGE (ATOMIC SCOPE)                     │
│    Isolate note edit, link repair, or rule update.          │
├─────────────────────────────────────────────────────────────┤
│ 2. PRE-COMMIT VALIDATION CHECK                              │
│    Verify English compliance (check_polish.py) & links.     │
├─────────────────────────────────────────────────────────────┤
│ 3. INTENT-DRIVEN CONVENTIONAL COMMIT                        │
│    Record precise prefix and architectural rationale.       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Mandatory Commit Standards

### 1. Mandatory Post-Modification Commits
- Immediately after completing any batch of edits or new note creations, perform a git commit.
- **Never leave modified or newly created files uncommitted in the working tree across conversation turns.**
- Complete execution turns with a clean `git status` unless an ongoing multi-step operation is explicitly in flight.

### 2. Granular, Atomic Commits (Split Logical Concerns)
- When multiple files or logical changes exist on staging or in the working tree, **split them into separate, atomic commits** rather than bundling everything into one monolithic commit.
- Stage and commit individual files or logical concerns separately:
  - Commit new note creations separately from rule updates.
  - Separate content refactoring commits from cross-vault link-wiring commits whenever feasible.
  - Commit navigational hub alignments separately from satellite note edits.

### 3. Intent-Driven Conventional Commit Taxonomy
Every commit message must clearly explain **why** the change was made and what architectural, epistemological, or structural purpose it fulfills. Use standard conventional prefixes:

| Commit Type | Scope | Usage & Intent |
| :--- | :--- | :--- |
| `feat(notes)` | New Notes | Adding new architectural notes, conceptual frameworks, or canonical hubs. |
| `refactor(links)` | Knowledge Graph | Graph wiring, repairing broken wikilinks, bidirectional link alignments. |
| `docs(vault)` | Existing Notes | Expanding sections, refining technical models, improving information hierarchy. |
| `chore(rules)` | Agent Customizations | Updating agent rules, system prompts, verification scripts, or workflow schemas. |
| `style(format)` | Typography & Layout | Frontmatter formatting, table alignments, or markdown linting without semantic changes. |

### 4. Prohibited Commit Behaviors
- **Zero Vague Messages**: Never use lazy or non-descriptive messages such as `"update notes"`, `"minor fixes"`, `"cleanup"`, or `"commit changes"`.
- **Zero Accidental Staging**: Do not run indiscriminate `git add .` if untracked temporary files, scratch artifacts, or private secrets exist outside intended targets. Verify staging with `git status` before committing.
- **Zero Broken Hooks**: If a git hook fails (e.g., language check), resolve the underlying cause immediately rather than bypassing verification with `--no-verify`.
