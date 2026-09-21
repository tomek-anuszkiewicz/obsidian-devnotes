# Note Authoring and Synthesis Workflow

Use this workflow for a new public note or a substantial refactor. It is complete only after the required audit passes.

## 1. Scope and graph discovery

Confirm that the user has asked for writing. Search the relevant vault area, identify the canonical domain hub, and select two to four lateral peers. Place the note in the five-layer system stack before choosing its title and location.

## 2. Draft from the top down

Use `information-hierarchy` and `practitioner-voice`. Lead with the core engineering claim and stakes, then explain mechanisms, substrate constraints, practical workflows, and graph relationships. Use `language-agnostic-architecture` when examples might otherwise depend on one language or framework.

Persist the note entirely in English: title, frontmatter, headings, prose, tables, diagrams, code comments, and wikilinks.

## 3. Wire the graph

Use `vault-linking` to add two to five inline piped links and three to six curated links in `## Related Notes`, each with a concise rationale. Update two to three relevant peers with inbound links when doing so improves the graph rather than creating ritual cross-links.

## 4. Audit before a requested commit

Run:

```powershell
python scripts/audit_workflow.py <note-path>
```

The audit must find no Polish-language violations, no `_Private/` references, no broken public wikilinks, and no prohibited style failures. Then perform a final practitioner review: each sentence should explain a concrete mechanism clearly enough to say to a senior engineer at a whiteboard.

Fix failures in place and rerun the audit. Do not commit unless the user asks for it.
