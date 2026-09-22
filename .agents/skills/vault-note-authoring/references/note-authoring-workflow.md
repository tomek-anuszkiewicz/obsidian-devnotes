# Public Note Workflow

Use this workflow for a new public note or a substantial revision after the user has asked to write.

## Find the useful context

Read the target note and search the nearby area of the vault. Identify an existing hub or peer only if it helps position the note, avoid duplication, or gives the reader a useful next step.

## Write for the subject

Use plain English and explain the mechanism before naming it. Let the subject choose the shape: a short operational note, an incident analysis, a comparison, or a longer explanation can all be appropriate. Add headings, examples, diagrams, summaries, and links when they improve understanding.

Keep public content independent of `_Private/`. Use `vault-linking` for meaningful links and `language-agnostic-architecture` when the lesson should not depend on one ecosystem.

## Check the result

For a changed public note, run:

```powershell
python scripts/audit_workflow.py <note-path>
```

Resolve language, privacy, and broken-public-link failures. Then read the note as an engineer: it should state what happens, why it matters, and any relevant trade-off without academic or ceremonial padding. Commit only when the user asks.
