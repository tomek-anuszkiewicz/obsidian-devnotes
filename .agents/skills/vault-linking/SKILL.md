---
name: vault-linking
description: Add, maintain, and repair useful Obsidian links (both inline within prose and in related-notes sections) across vault subfolders without turning notes into graph spam.
---

# Vault Linking

Connect notes where another document provides concrete prerequisite context, operational mechanisms, verification evidence, or a meaningful architectural contrast. Link at the exact point of need for the reader.

## 1. Prioritize Inline Links in Prose

The primary way to link notes is **inline within the body text**, right where the concept, rule, or trade-off is discussed. Do not relegate all connections to a list at the bottom.

### Common Inline Patterns

- **Parenthetical citation `(see [[Target Note]])`**: The standard pattern when a sentence makes an assertion, defines a constraint, or describes a failure mode elaborated elsewhere:
  > Markdown can still be misunderstood. Compilation, static type checks, and automated tests have to check the resulting code (see [[Testing in the Model, Agent, LLM Era]]).
  > A more reliable approach pairs wide implementation freedom with rigid negative boundaries (see [[Negative Knowledge and Explicit Architectural Dissents]]).

- **Multiple citations `(see [[Note A]] and [[Note B]])`**: When a point touches complementary mechanisms:
  > ...rules that previously required human interpretation (see [[LLMs as a Code Review Team]] and [[Reviewing AI-Generated Code]]).

- **Direct grammatical weave `[[Target Note]]`**: When the note title flows directly into the sentence:
  > Instrument the services with [[OpenTelemetry]] and propagate `traceparent` through HTTP, gRPC, and Kafka envelopes...

- **Piped links `[[Target Note|anchor text]]`**: When grammar or sentence flow requires an alternate surface label:
  > ...gives the agent a clear target (see [[Testing in the Model, Agent, LLM Era|disposable code rewrites]]).

### Finding Inline Opportunities Across Vault Folders

- **Search across subfolders**: Do not limit searches to the note's immediate directory. Vault notes in `01 Architecture & Code`, `02 Testing & Code Review`, `03 Systems & Infrastructure`, `04 Prompts, Context & Models`, and `05 Engineering Economics & Future` constantly interact.
- **Discover related ideas**: When the local `devnotes-rag` MCP server is available, try `devnotes_search` for concepts that may be phrased differently across notes. Use file search for exact titles and terms, then read likely notes before choosing a link. If RAG is unavailable or stale, continue with direct vault searches.
- **Identify substantive assertions**: Look for sentences discussing system boundaries, failure modes, test verification, context economics, model behavior, or architectural patterns.
- **Search existing note titles**: Check if the vault contains a note dedicated to that specific mechanism or tool.
- **Embed at the claim**: Place `(see [[Target Note]])` immediately adjacent to the claim it supports or clarifies.

## 2. Complement with Related Notes Sections

Use a `## Related notes` section at the end of a note for broader continuations, peer notes, or domain hubs that do not attach cleanly to a single sentence in the prose.

- **Always annotate**: Give each entry a concise explanation of the relationship:
  ```markdown
  ## Related notes

  - **[[Testing in the Model, Agent, LLM Era]]** — How compilers and tests verify the implementation behind a Markdown specification.
  - **[[Reviewing AI-Generated Code]]** — How engineers combine short design notes with focused diff reviews.
  ```
- **Do not use as a substitute for inline links**: An end-of-note list does not replace contextual inline citations in the body text.

## 3. Linking Discipline and Verification

- **Verify target resolution**: Always verify that every linked note actually exists in the vault before adding or keeping a link. Obsidian resolves `[[Note Title]]` globally across folders.
- **Repair or prune broken links**: When reviewing or editing a note, inspect existing links for dead or unresolved targets:
  - If the target note was renamed or split, update the link to point to the current valid note title or alias.
  - If the target note does not exist in the vault and has no replacement:
    - In inline prose: remove the orphan parenthetical citation `(see [[Dead Link]])`, or unwrap `[[Dead Link|display text]]` / `[[Dead Link]]` to plain text so sentence grammar remains intact.
    - In `## Related notes`: delete the bullet entry pointing to the missing note.
- **Substance over keywords**: Only link when the target note genuinely deepens the mechanism, explains the trade-off, or provides verification. Never link random common words (e.g., avoid linking every occurrence of "agent", "testing", or "architecture").
- **Avoid link density clutter**: Keep prose natural and readable. A single well-placed `(see [[Target Note]])` on a key sentence is more effective than hyperlinking every noun.
- **Bidirectional hygiene**: When adding a strong relationship that materially improves a peer note, consider updating that peer note; otherwise, avoid ritual or symmetrical cross-linking.
