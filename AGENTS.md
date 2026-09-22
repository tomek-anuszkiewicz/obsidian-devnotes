---
trigger: always_on
description: Minimal operating contract for agents working in this public engineering vault.
---

# AGENTS.md

This is a public Obsidian vault about software engineering. Write notes as a practitioner explaining real mechanisms, trade-offs, failures, and evidence.

## Non-negotiable boundaries

- Persist vault content in English. Mirror the user's language in chat.
- For an audio message, start the response with a faithful transcription in the original language before any other text.
- Public files must not mention, link to, or depend on `_Private/`.
- During exploration, challenge assumptions and add useful technical reasoning. Do not echo the user's words, create unsolicited plans, or write notes until the user explicitly asks to write.
- Commit only when the user explicitly asks. Keep unrelated working-tree changes intact.

## Writing and maintenance

Use `practitioner-voice` as the default style. Choose a structure that suits the note; explain the important mechanics before adding terminology. Links, summaries, diagrams, and examples are useful when they help the reader, not because a template requires them.

For a new or substantially revised public note, use `vault-note-authoring`. Use `vault-linking` when links need attention, `information-hierarchy` to improve order, and `language-agnostic-architecture` when an explanation should travel across ecosystems.

Run the relevant checks before handing off a changed public note. `scripts/check_polish.py` protects the English-only rule, and `scripts/audit_workflow.py` checks language, privacy, and public wikilinks. Automated checks do not replace a plain-language review.
