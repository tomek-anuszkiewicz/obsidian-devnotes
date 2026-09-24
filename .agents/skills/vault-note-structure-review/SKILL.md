---
name: vault-note-structure-review
description: Review Obsidian notes to recommend merges, splits, and deliberate duplication that makes each note a self-contained engineering story.
---

# Vault Note Structure Review

Use this skill when the user asks which existing notes should be merged, split, or share deliberately duplicated knowledge. Review the scope the user gives; do not edit notes, create links, or move content unless the user separately asks for implementation.

Treat each note as a standalone story for a reader with a specific engineering question. Duplication is not a defect when repeating a necessary mechanism, constraint, example, or decision lets more than one note answer that question without requiring background reading.

Think of notes as cross-sections through a larger subject. The same mechanism can appear in several cross-sections because it explains a different consequence in each one. Preserve enough local explanation for every cross-section to stand on its own; a link can connect the stories but should not replace the repeated context.

Recommend a new note when ideas distributed across existing notes form another coherent reader question or causal argument with its own useful conclusion. The new note does not become the exclusive home of those ideas. Keep or copy the relevant parts in the existing notes when their local stories still need them. Conversely, repeated subject matter alone does not justify extraction if it does not form an independent story.

Recommend a merge when notes answer substantially the same question and divide one argument, evidence set, or operational workflow without giving the reader a useful independent stopping point. Recommend a split when distinct sections answer different questions, need different context, or make the note harder to find and use as one story. Recommend copying knowledge when another note needs a compact, accurate version of it to stand on its own; keep the surrounding story specific to its reader rather than duplicating an entire note by default.

## When to consider a split

Use length as a signal to review structure, never as an automatic split rule. Frontmatter, code blocks, tables, and examples can inflate line counts without adding another argument.

- **Inspect:** Around 300–500 lines of note content, identify the one reader question that holds the sections together and look for independent detours. No split recommendation is required if the note still tells one coherent story.
- **Recommend:** Around 600 lines or more, if two or more sections answer distinct reader questions and can stand on their own, propose a concrete split. Name what moves, what stays, and what context each note must retain. If the long note still has one clear argument, explain why it should stay together.
- **Strongly recommend:** At any length, recommend restructuring when distinct sections need different context, have their own conclusions, and keeping them together makes either story difficult to find or use. The evidence is the independent arguments, not the line count.

At roughly 800–1000 lines, perform an explicit structural review before recommending further expansion, even if no split is ultimately justified. State the decision and its reason; do not cut a note merely to get below a threshold.

Base recommendations on the notes' actual claims and sections, not similar titles, shared words, folder placement, or a preference for fewer notes. For each recommendation, name the affected notes and sections, state whether the content should be merged, moved, or copied, and explain the reader benefit and the substance that must remain intact. If the evidence is weak, say so rather than inventing a restructuring proposal.

When a copied explanation could drift, call out the shared claim that must stay consistent. Do not treat links as a substitute for enough local context, and do not prescribe a minimum number of recommendations.
