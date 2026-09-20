---
name: vault-note-authoring
description: Canonical 6-phase workflow for authoring, refactoring, and verifying notes in the vault, culminating in the mandatory Terminal Audit Gate.
---

# Vault Note Authoring Workflow Skill

This skill guides the autonomous agent through the end-to-end authoring and refactoring pipeline defined in `.agents/workflows/note-authoring.md`.

## Workflow Phases & Required Actions

1. **Phase 0: Dialectical Exploration & Scoping**:
   - Spar as technical peer; challenge assumptions; zero echoing; zero unsolicited plans.
   - GATE: Explicit user mandate ("ready to write").
2. **Phase 1: Reconnaissance & Topology Discovery**:
   - Inspect existing domain notes via `grep_search` and `list_dir`. Identify 2–4 peers.
3. **Phase 2: Inverted Pyramid Authoring**:
   - Load `information-hierarchy`, `practitioner-voice`, and `language-agnostic-architecture`.
   - Write 100% English, lead with hook in lines 1–50, maintain unhurried causal depth.
4. **Phase 3: Dual-Layer Graph Wiring**:
   - Load `vault-linking`.
   - Add 2–5 inline piped links (`[[Note|text]]`) and 3–6 curated links in `## Related Notes`.
   - Wire inbound links in 2–3 peer notes.
5. **Phase 4: MANDATORY TERMINAL AUDIT GATE**:
   - Execute:
     ```powershell
     python scripts/audit_workflow.py [path/to/note.md]
     ```
   - Must return `ALL GATES PASSED [100% CLEAN]`.
   - Perform mental Coffee & Tech Talk test.
6. **Phase 5: Atomic Git Ledger Recording**:
   - Commit with conventional taxonomy (`feat(notes): ...` or `refactor(notes): ...`).
   - Confirm clean working tree (`git status`).
