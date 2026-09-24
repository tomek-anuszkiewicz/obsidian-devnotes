---
name: vault-argument-crosscheck
description: Generate an independent English note from a neutral topic, compare its arguments with a devnotes note and the whole vault, integrate clear existing ideas, and surface new or disputed ideas for the author.
---

# Vault Argument Cross-Check

Use this skill when the author wants to test what an independent model would develop from the broad subject of one or more vault notes, then use the result to improve the vault. This is an argument-level comparison, not a rewrite of the source note or a search for duplicate wording. Process each target note separately.

## 1. Keep the independent draft separate

Before reading the target note's body, derive a short, neutral topic from its filename or user-provided topic. Remove any conclusion embedded in the title. Do not pass the title, path, tags, aliases, links, excerpts, examples, or claims from the vault to the generator. If even the topic cannot be derived without reading the note, ask the author for a broad topic.

Use a fresh agent with no inherited conversation turns when available (for example, a subagent with `fork_turns="none"`). Give it the neutral topic and these four fixed skill entrypoints as the only permitted workspace reads:

- `.agents/skills/practitioner-voice/SKILL.md` for direct engineering prose.
- `.agents/skills/note-structure/SKILL.md` for a reader-first, self-contained argument.
- `.agents/skills/obsidian-properties/SKILL.md` for English Markdown frontmatter (`title`, `tags`, `aliases`). It must choose these from the neutral topic and its own draft, without inspecting the vault's taxonomy or other notes.
- `.agents/skills/check-polish/SKILL.md` for the English-only requirement. The coordinating agent, not the generator, runs its validation script after saving the draft.

The generator may read those four `SKILL.md` files, but not their linked resources or any other file. It must not inspect the source note, browse the vault or web, use memory or prior conversations, or run other tools. Have it return Markdown in its message; the coordinating agent saves that output as a separate temporary `.md` artifact outside the vault's note collection. Do not put the draft in the corpus searched later. If a fresh agent is unavailable, prepare the prompt for a separate projectless task and wait for its output. Do not claim a same-context run is blind.

Generation request, substituting only the neutral topic:

> I have an idea for a note about **{neutral topic}**. Write a standalone Markdown note in English for experienced software engineers. Choose the important questions, arguments, mechanisms, examples, limitations, and practical conclusions yourself. Use `practitioner-voice`, `note-structure`, `obsidian-properties`, and `check-polish` only as style, structure, frontmatter, and English-language guidance. You may read only their four `SKILL.md` files at the paths supplied above; do not follow their links or run their scripts. Do not read any other workspace file or note, use memory or other conversations, or browse the internet. Base the substance solely on this prompt and your general knowledge. Return only the Markdown note.

Use the same four skill versions for every generated draft in a comparison batch, so style guidance does not change between notes. The four skills govern presentation, not which claims to make. This procedure limits visible context; it cannot prove that a model has no prior knowledge of the subject or that separate sessions share no hidden context. Record the prompt, skill versions, generator identity if known, and whether the allowed-file boundary was followed.

## 2. Compare with the target note

Read the generated draft and the current target note. Break each into substantive claims: questions answered, causal mechanisms, concrete examples, caveats, and recommendations. Mark each generated claim as already covered, a meaningful extension, a different framing, or apparently absent from the target. Do not count changes in wording, length, or examples of the same mechanism as new arguments. Record exact locations in both notes and state why each difference matters to the target's own argument.

Do not penalize broad coverage or deliberate repetition. The vault is a revisable record of the author's current thinking; a note may repeat a mechanism so that its own story makes sense. A link alone is insufficient if the reader needs the mechanism to understand the local argument.

## 3. Check the entire vault

For every meaningful argument apparently absent from the target, search all vault notes, not just the same folder or notes with similar titles. When the local `devnotes-rag` MCP server is available, use `devnotes_search` to find conceptually similar passages under different wording. Also search alternate terms and related consequences directly in the files, inspect plausible matches in context, and follow relevant Obsidian links. If RAG is unavailable or its index may be stale, continue the whole-vault check using files. Classify the argument as:

- **Present elsewhere:** the same substantive mechanism or conclusion is developed in another note.
- **Partially present or disputed:** related material exists, but the match or implication is uncertain.
- **New relative to this vault:** no substantive match was found after a reasonable whole-vault check.

Use note paths and section or line references from current files as evidence. Neither an empty RAG result nor a failed keyword search alone establishes absence. "New relative to this vault" says nothing about originality in the wider world or about who first conceived the idea.

## 4. Make changes and route decisions

For arguments present elsewhere, decide from the target note's reader question:

- Copy a concise, accurate explanation into the target and link to the fuller note when it closes a real gap in the target's reasoning.
- Add a contextual link when the other note is useful background but the target already stands on its own.
- Leave the target unchanged when the argument would pull it away from its subject or add no useful perspective.

When placement across notes is genuinely unclear, use `vault-note-structure-review` to assess the actual claims and sections: whether a compact explanation belongs in both notes, a link is enough, or the material forms a distinct reader question. Treat that skill as review guidance, not an instruction to merge or split notes automatically. When adding or repairing a link, use `vault-linking` to place it at the relevant claim and verify that its target resolves. These two skills belong to the coordinating agent after vault search; never send them to the independent generator.

Make clear, low-risk edits without asking for routine approval when the user has invoked this workflow to improve notes. Preserve the source note's claims, uncertainty, structure, and voice; do not move or delete the only copy of an idea. If the fit, interpretation, or author's stance is doubtful, leave the text unchanged and present the options to the author with the relevant excerpts.

Do not automatically insert arguments that are new relative to the entire vault. Give the author a decision list with each argument, why it could matter, where it might fit, and any factual or speculative uncertainty. Add it only after the author chooses it, unless that run explicitly delegates new-idea adoption to you. Never present a generated claim as the author's established view merely because it sounds plausible.

## 5. Verify and report

Review the actual diff against every intended addition and check that links resolve. Apply `obsidian-properties` when integrating an idea into an existing note, preserving accurate metadata. Run `check-polish` on the generated draft and any modified vault notes, plus the relevant frontmatter/Markdown checks and `git diff --check` on vault changes. Report missing validation dependencies rather than treating an unrun check as passed. Do not commit unless separately asked.

Report for each target: the neutral prompt and isolation status; arguments already in the target; arguments found elsewhere with source locations and the action taken; new-to-vault arguments awaiting the author's decision; disputed matches or edits; changed files and validation results. Keep the independent draft available as a separate Markdown artifact so the author can inspect the comparison.
