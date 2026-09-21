---
name: vault-note-authoring
description: Create or substantially revise public Obsidian vault notes with graph discovery, English-first engineering prose, link wiring, and the required audit. Use for new notes and deep note refactors, not small typo fixes.
---

# Vault Note Authoring

Create a public, graph-connected note that is useful to a practicing software engineer and remains publishable without private context.

## Procedure

1. Read [the detailed workflow](references/note-authoring-workflow.md) before authoring or deeply refactoring a note.
2. Discover the relevant hub and lateral peers before choosing the note's position in the graph.
3. Apply `information-hierarchy` and `practitioner-voice`; use `language-agnostic-architecture` when it clarifies durable system mechanics.
4. Apply `vault-linking` to add useful outbound links and maintain relevant inbound links.
5. Ensure persisted content is English-only and contains no reference to `_Private/`.
6. Before a requested commit, run `python scripts/audit_workflow.py <note-path>` and resolve every failure. Commit only when the user asks.

## Boundaries

- Preserve unrelated working-tree changes.
- Do not treat a passing automated audit as a substitute for checking whether the note explains mechanisms in plain engineering language.
