---
name: note-structure
description: Structure engineering notes with a reader-first hierarchy, durable architectural mechanics, and purposeful code examples without rigid templates.
---

# Note Structure

Structure engineering notes so a reader can understand the point immediately, trace the underlying mechanism, and evaluate the trade-offs without digging through formal setup first.

## Reader-First Information Hierarchy

- **Start where the reader needs to start**: Open with the concrete problem, incident, decision, or operational mechanism rather than historical preamble or abstract introductions.
- **Scannable outline**: Use clear, descriptive headings that summarize the argument and let readers jump directly to relevant sections.
- **Purposeful sections**: Include context, operational details, measurements, failure modes, and trade-offs only when they clarify the core claim. Short notes do not need artificial filler sections.
- **Revising outlines**: When updating an existing note, reorganize sections only when the current flow obscures an important dependency, constraint, or conclusion. Preserve concrete evidence and working details.

## Notes as Cross-Sections

Treat each note as a self-contained cross-section of a larger subject. A note should answer one reader question or present one coherent causal argument from its own point of view. It is not merely the canonical storage location for a set of isolated facts.

Repeat a mechanism, constraint, or conclusion when another cross-section needs it to remain understandable on its own. Adapt the explanation to the local argument instead of replacing it with a link or avoiding useful repetition. Links connect the cross-sections; they do not substitute for the context each one needs.

Create a separate note when the material supports a new reader question, causal chain, or useful point of view with its own beginning and conclusion. Parts of that material may already appear in several notes. That is not a reason to avoid the new note, and the existence of the new note is not a reason to remove those parts from their original cross-sections.

Do not create a new note merely because the same topic appears in several places. The deciding question is whether the proposed note tells a distinct, useful story rather than whether its individual claims are unique.

## Durable Architectural Mechanics

When explaining architecture or engineering patterns:

- **Focus on durable mechanics first**: Explain who owns state, where data moves, what initiates a transaction, how failure and retries are handled, and what limits throughput or scalability.
- **Concrete implementations over generic pseudocode**: Use a specific language, framework, or runtime when it makes the mechanism concrete or when the note investigates that technology directly. Do not replace working code with vague pseudocode merely to appear general.
- **Avoid artificial multi-ecosystem lists**: Do not pad notes with superficial examples across multiple languages just to balance a list. Pick the cleanest representative example that demonstrates the mechanism.
- **Purpose-driven representations**: Choose diagrams, real source code snippets, benchmarks, or state machines based on what best illustrates the runtime behavior and invariants. Clearly distinguish general principles from platform-specific quirks.
