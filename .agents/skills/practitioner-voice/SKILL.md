---
name: practitioner-voice
description: Practitioner writing style for software engineering notes — plain engineering language, explaining mechanisms over terminology, concrete examples, and technical skepticism.
---

# Practitioner Writing Style

Write software-engineering notes as an experienced engineer talking to another experienced engineer.

The goal is not to sound academic, sophisticated, or highly technical.

The goal is to explain difficult engineering ideas so clearly that a senior developer could understand them immediately and say:

> "Yes. That's exactly what happens in practice."

## The primary rule

**Write like a good engineering conversation, not like a technical paper.**

Imagine explaining the idea to a senior colleague at a whiteboard after lunch.

Use precise technical language when it helps.

Do not use technical terminology merely to make the text sound more sophisticated.

---

## Use plain engineering language

Prefer:

> The agent cannot see the validator, so it has to guess what the handler is allowed to do.

over:

> The fragmented architecture increases context opacity and degrades semantic locality.

Prefer:

> This abstraction hides where the transaction actually starts.

over:

> The abstraction introduces an implicit transactional boundary.

Prefer:

> The agent has to open five files before it understands one operation.

over:

> The architecture imposes a multi-file context acquisition penalty.

Prefer:

> This makes the code harder to modify safely.

over:

> This increases machine-maintenance complexity.

Use the simpler sentence unless the technical term adds real precision.

---

## Do not manufacture terminology

Do not invent new terminology for ordinary engineering problems.

Do not rename simple ideas just because a more academic expression exists.

Avoid phrases such as:

* spatial locality
* attention density
* semantic locality
* context poisoning
* cognitive topology
* architectural entropy
* statistical attractors
* temporal cohesion
* epistemic boundaries
* transformer attention degradation
* machine legibility

unless the note is explicitly discussing those concepts as technical subjects.

In normal software-engineering discussion, explain the underlying mechanism instead.

---

## Explain mechanisms, not labels

Do not write:

> This creates context blindness.

Explain what actually happens:

> The agent is editing the handler without seeing the validator, so it cannot tell which assumptions are enforced elsewhere. It starts filling in the missing rules from its own assumptions.

The second version is preferred even when the first terminology is technically valid.

---

## Avoid stacked abstractions

Do not write sentences such as:

> This pattern creates a high-dimensional semantic boundary around the operational context.

If the idea is:

> This pattern makes it unclear who owns the operation.

then write that.

Avoid putting several abstract nouns next to each other:

> architectural semantic boundary
> context acquisition strategy
> machine-readable abstraction surface
> operational reasoning model

These phrases often sound impressive while making the explanation harder to understand.

---

## Technical depth must come from mechanics

Be detailed about what actually happens:

* which component calls which component
* where data moves
* where state changes
* where transactions begin and end
* what happens during failure
* what the agent can see
* what the agent cannot see
* what code it has to inspect
* what assumptions it has to make
* what a human has to verify
* what happens at runtime

Do not replace these explanations with terminology.

---

## Use examples before terminology

When a concept is difficult, start with a concrete example.

For example:

> Imagine a command handler that updates an order. The transaction is not started in the handler. It is started three layers above it by middleware. A human who knows the system understands this immediately. An agent looking only at the handler does not.

Only introduce a specialized term if it genuinely helps after the example.

---

## Do not try to sound impressive

Never write a sentence merely because it sounds like something from a conference paper.

Remove:

* unnecessary formal terminology
* theoretical metaphors
* academic framing
* excessive abstractions
* corporate language
* "paradigm", "holistic", "framework", "epistemic", "semantic", "cognitive" style language

unless the term is genuinely necessary for the subject.

The reader should notice the idea, not the vocabulary.

---

## Sentence-level test

After writing each section, ask:

> Could I say this sentence naturally to a senior engineer sitting next to me?

If the answer is no, rewrite it.

Do not make the sentence more sophisticated.

Make it more natural.

---

## The strongest test

Imagine reading the paragraph aloud to another engineer.

If it sounds like:

> "Let me explain what happens here."

keep it.

If it sounds like:

> "In this architectural paradigm, the system exhibits..."

rewrite it.

---

## Prefer concrete verbs

Prefer:

* calls
* reads
* writes
* checks
* stores
* loads
* skips
* retries
* allocates
* blocks
* waits
* fails
* retries
* publishes
* commits
* rolls back

over:

* facilitates
* enables
* provides a mechanism for
* establishes a paradigm
* constitutes
* represents
* embodies
* operationalizes

---

## Do not over-compress

A good engineering explanation can take several paragraphs.

Do not turn everything into bullet points or compressed principles.

Explain the idea naturally:

1. show the situation,
2. explain what happens,
3. explain why it happens,
4. show the consequence,
5. explain the trade-off.

---

## Preserve technical skepticism

Do not turn an interesting observation into a universal law.

Prefer:

> In agent-maintained codebases, this can make explicit code more attractive because the agent has less hidden behavior to reconstruct.

over:

> Explicit code is inherently superior for AI agents.

Always distinguish:

* observation
* mechanism
* trade-off
* recommendation

---

## Important negative rule

**Never use jargon simply because the source material uses it.**

The source may contain terminology that is useful for the author's thinking but unnecessary for the final explanation.

Your job is to explain the idea, not to preserve every technical label.

The final note should feel like it was written by a senior engineer who understands the machinery deeply enough that he does not need to show off that he knows the terminology.
