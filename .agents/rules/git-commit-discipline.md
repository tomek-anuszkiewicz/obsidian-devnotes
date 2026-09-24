---
trigger: always_on
description: Preserve the user's working tree and commit only with explicit authorization.
---

# Git Changes

- Do not discard or overwrite unrelated working-tree changes.
- Commit only when the user explicitly requests a commit.
- When asked to commit, use a concise conventional message that describes one coherent change and report the resulting status.
- Immediately after creating a commit, run `scripts/update_rag_index.ps1` to update the local RAG index, and report the indexing status alongside the commit status.
