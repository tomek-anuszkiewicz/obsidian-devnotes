---
trigger: always_on
description: Mandatory granular git commits with intent-driven messages after modifying or refactoring notes
---

# Git Commit Discipline & Granularity Rule

Whenever creating, modifying, updating, or refactoring notes, documentation, rules, or schemas in this Obsidian vault, the agent must systematically record changes via Git.

## Core Requirements & Operating Principles

1. **Mandatory Post-Modification Commits**:
   - Immediately after completing any batch of edits or new note creations, perform a git commit.
   - Never leave modified or newly created files uncommitted in the working tree across conversation turns.

2. **Granular, Atomic Commits (Split Logical Changes)**:
   - When multiple files or logical changes exist on staging or in the working tree, **split them into separate, atomic commits** rather than bundling everything into one monolithic commit.
   - Stage and commit individual files or logical concerns separately (e.g., commit an individual note creation separately from rule updates, link wiring commits, or hub updates).
   - If a refactoring involves both content updates and cross-vault link repairs, separate the content edit commit from the link-wiring commit whenever feasible.

3. **Intent-Driven, Meaningful Commit Messages**:
   - Every commit message must clearly explain **why** the change was made and what architectural, epistemological, or structural purpose it fulfills.
   - Use clear conventional-style prefixes where applicable:
     - `feat(notes): ...` for new architectural or conceptual notes.
     - `refactor(links): ...` for graph wiring, bidirectional linking, or hub alignments.
     - `docs(vault): ...` for updating existing conceptual frameworks or expanding sections.
     - `chore(rules): ...` for updating or adding agent rules and workflows.
   - Never use vague or lazy commit messages (e.g., avoid "update notes", "minor fixes", or "commit changes").
