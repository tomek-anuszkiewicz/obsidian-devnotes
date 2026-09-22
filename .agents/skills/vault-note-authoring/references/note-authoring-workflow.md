# Faithful Rewrite Workflow

Use this workflow after the user has asked to rewrite an existing public note.

## Use only the supplied source

Read the target note and [Rewrite prompt.md](../../../../Rewrite%20prompt.md). Do not inspect nearby notes, search the vault, add links, or change other files.

## Preserve the note's substance

Retain the existing ideas, claims, examples, and structure. Make only the wording changes needed to remove academic or AI-generated style. Prefer concrete descriptions, direct verbs, and natural engineering language. Do not add concepts, jargon, evidence, examples, links, summaries, or recommendations.

Do not invoke other vault skills unless the user explicitly expands the task.

## Check the result

For a changed public note, run:

```powershell
python scripts/audit_workflow.py <note-path>
```

Resolve language, privacy, and broken-public-link failures. Then compare the result with the source: it should preserve the same substance while sounding natural, direct, confident, and grounded. Commit only when the user asks.
