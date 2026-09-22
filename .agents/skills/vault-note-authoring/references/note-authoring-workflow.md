# Faithful Rewrite Workflow

Use this workflow after the user has asked to rewrite an existing public note.

## Use only the supplied source

Read the target note. This workflow contains the rewrite prompt. Do not inspect nearby notes, search the vault, add links, or change other files.

## Preserve the note's substance

Retain the existing ideas, claims, examples, and structure. Make only the wording changes needed to remove academic or AI-generated style. Prefer concrete descriptions, direct verbs, and natural engineering language. Do not add concepts, jargon, evidence, examples, links, summaries, or recommendations.

Do not invoke other vault skills unless the user explicitly expands the task.

## Rewrite the prose

Rewrite without changing the note's ideas, claims, examples, or structure unless a small structural change is necessary for readability. The job is to remove academic or AI-generated style, not to make the note sound more sophisticated.

For every paragraph, ask:

- Would a senior engineer actually say this?
- Is there a simpler way to say the same thing?
- Did I introduce terminology the reader does not need?
- Does the paragraph explain a mechanism, or merely give it a fancy name?
- Does it sound like an engineering conversation rather than a paper?

Replace abstract terminology with concrete descriptions whenever possible. The result should be natural, direct, confident, technical, and grounded—slightly informal rather than academic.

## Check the result

For a changed public note, run:

```powershell
python scripts/audit_workflow.py <note-path>
```

Resolve language and broken-public-link failures. Then compare the result with the source: it should preserve the same substance while sounding natural, direct, confident, and grounded. Commit only when the user asks.
