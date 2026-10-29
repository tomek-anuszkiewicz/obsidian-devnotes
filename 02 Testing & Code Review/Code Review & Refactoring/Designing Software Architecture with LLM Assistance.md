---
title: Designing Software Architecture with LLM Assistance
tags:
  - software-architecture
  - system-design
  - ai-agents
  - llm
  - decision-making
  - tradeoff-analysis
aliases:
  - LLM-Assisted Software Architecture
  - Architecture Exploration with AI
  - Validating the Model of Reality
  - The Plausible Completeness Illusion
  - Reversible Architectural Experimentation
---

A fluent architecture proposal can be consistent with the prompt and still depend on assumptions the real system does not satisfy. Before selecting a database, transport, or deployment model, establish which business constraints and runtime facts make a choice acceptable.

This article follows constraint discovery and the separation of facts, inferences, assumptions, and unknowns. [[Comparing and Validating Architecture Options with LLMs]] develops solution-space exploration, recommendation bias, specialist challenge, prototypes, and the transition from an experiment to a decision. Earlier discussion and implementation familiarity can narrow the options a model proposes, so discovery should preserve questions that could reverse the recommendation.

## Core idea

LLMs can significantly accelerate architectural exploration, but they are not reliable guarantees of completeness.

They are good at:

- exploring unfamiliar technologies,

- generating design alternatives,

- extracting constraints from available context,

- comparing trade-offs,

- producing prototypes,

- identifying common risks,

- reviewing an existing proposal.

They are weaker at:

- discovering constraints that were never documented,

- recognizing questions that neither the user nor the model knows should be asked,

- distinguishing a true requirement from an accidental property of the current implementation,

- understanding organizational and domain knowledge that exists only in people’s heads,

- reliably signaling that the problem description is incomplete.

The main risk is not only hallucination.

A more subtle risk is that the model fills missing information with a plausible, typical scenario. The result may be coherent and professionally justified, even though it depends on assumptions that were never confirmed.

This creates an illusion of completeness.

The most deceptive failure mode is cognitive silence: the model rarely warns you that a prompt lacks critical operational invariants. Instead of stopping to ask whether the workload demands read-your-writes consistency, what the p99 latency budget looks like, or how connection pools tolerate spikes, it silently defaults to a textbook pattern and designs an entire system around it.

---

## The model may provide a plausible answer instead of revealing missing knowledge

When the description is incomplete, an LLM tends to complete the story.

For example, it may implicitly assume that:

- eventual consistency is acceptable,

- operations are idempotent,

- messages may be retried safely,

- status transitions are linear,

- no external system reads the database directly,

- a relational database is suitable,

- rolling deployments do not create compatibility problems.

These assumptions may be reasonable in a typical system, but they may be false in the actual one.

The dangerous part is that a reasonable answer can look like an evidence-based answer.

A model can generate:

- a clean architecture,

- a detailed justification,

- diagrams,

- migration steps,

- code,

- a list of advantages and disadvantages.

This can make the user accept the proposal without examining the assumptions behind it.

Therefore:

> A fluent and internally consistent answer should not be treated as evidence that the problem was understood completely.

---

## Constraints may come from business logic

Technical constraints often originate in business requirements.

The reasoning chain should be:

```text
Business requirement
→ required system property
→ architectural constraint
→ technology choice
```

Examples:

```text
Business rule:
A customer must never be charged twice.

Required property:
Duplicate execution must be safe or prevented.

Architectural consequence:
Idempotency, deduplication, transactional boundaries, or unique operation identifiers are required.
```

```text
Business rule:
The user must immediately know whether a reservation succeeded.

Required property:
The result cannot rely only on eventual consistency.

Architectural consequence:
A purely asynchronous workflow may be insufficient.
```

```text
Business rule:
The organization must reconstruct why a decision was made years later.

Required property:
Historical state and decision inputs must be preserved.

Architectural consequence:
Audit records, versioning, immutable logs, or event history may be required.
```

A technology choice such as a database type may therefore be derived from the domain rather than being a purely technical preference.

At the same time, a stated constraint such as “we must use SQL Server” should be questioned.

It may represent:

- a real organizational standard,

- existing expertise,

- licensing constraints,

- integration dependencies,

- transactional requirements,

- direct reporting access,

- or only historical habit.

The model should ask what underlying requirement makes the constraint necessary.

---

## Categories of constraints

It is useful to divide constraints into three groups.

### Explicit constraints

These are written in:

- requirements,

- tickets,

- documentation,

- ADRs,

- contracts,

- security policies.

The model can usually handle them well if they are clearly provided.

### Discoverable constraints

These are not explicitly documented, but can be inferred from:

- code,

- tests,

- schemas,

- deployment manifests,

- integrations,

- production data,

- telemetry,

- incident history.

Finding them requires a dedicated discovery phase.

### Hidden constraints

These exist only in:

- people’s experience,

- manual processes,

- informal agreements,

- organizational politics,

- undocumented customer behavior,

- historical exceptions.

The model cannot discover them unless some trace of them is available.

This is the most dangerous category.

---

## Do not start with architecture selection

A weak process is:

```text
Problem description
→ architecture proposal
→ implementation
```

A stronger process is:

```text
Problem description
→ confirmed facts
→ missing information
→ assumptions
→ required system properties
→ design alternatives
→ attempt to invalidate alternatives
→ conditional recommendation
→ implementation
```

The first phase should be constraint discovery, not solution generation.

The model should first identify:

- what is known,

- what is inferred,

- what is assumed,

- what is unknown,

- what can be interpreted in multiple ways,

- what information could reverse the decision.

Only then should it propose technologies or architecture.

---

## Separate facts, inferences, assumptions, and unknowns

Important design analysis should not be presented as one continuous narrative.

A useful classification is:

### Confirmed fact

Supported by a trusted source.

Example:

> Deployments are rolling and old instances may run for up to thirty minutes.

### Inference

Logically derived from confirmed facts.

Example:

> Database changes must remain compatible with both application versions.

### Assumption

Used temporarily because information is missing.

Example:

> No external reporting system reads the modified table directly.

### Unknown

Not yet established.

Example:

> Whether message ordering must be preserved across all customers.

### Typical practice

A common recommendation that may not apply here.

Example:

> Using a message broker for long-running operations.

This classification prevents plausible assumptions from silently becoming requirements.

---

## Ask what could reverse the recommendation

One of the most valuable questions is:

> Which missing information could make your recommendation completely different?

Other useful questions include:

- Under what conditions is this solution wrong?

- Which assumption has the greatest effect on the decision?

- What did you assume even though I did not provide it?

- What must be true for this design to work?

- Which of those conditions have not been verified?

- What system property would make another alternative preferable?

- Which parts of the recommendation come from my context, and which come from generic best practices?

A good recommendation should be conditional.

For example:

> If delayed consistency is acceptable, operations are idempotent, and the team can operate the broker, asynchronous messaging is a strong option. If the user requires an immediate authoritative result, a synchronous transactional path may be more appropriate.

This is more useful than declaring one architecture universally best.

---

## The best role of the model

The model should not be treated as an authority that produces the architecture.

It is better used as an accelerator for:

- knowledge exploration,

- question generation,

- constraint discovery,

- option generation,

- trade-off analysis,

- prototype creation,

- adversarial review,

- documentation,

- verification planning.

The human remains responsible for confirming the model of reality on which the architecture depends.

The most important question is not:

> Did the model produce a reasonable solution?

It is:

> Is the solution based on confirmed properties of this system, or on plausible defaults borrowed from typical systems?

---

## Reusable prompt: discovery before design

```text
Help me analyze this architecture problem, but do not propose a solution yet.

First, separate the available information into:

- confirmed facts,
- conclusions derived from those facts,
- working assumptions,
- missing information,
- typical practices that may not apply to this system.

Do not fill missing information with standard assumptions without labeling them explicitly.

Identify all important dimensions of the problem, including dimensions I may not know to ask about:

- business rules and invariants,
- data and consistency,
- transactions and concurrency,
- ordering, retries, and idempotency,
- partial failures,
- integrations,
- performance and scale,
- security and privacy,
- audit and retention,
- deployment, migration, and rollback,
- observability and operations,
- cost and team expertise.

Prepare the questions whose answers could materially change the architecture decision. Rank them by impact.

Also identify:

- assumptions you would otherwise make from the description,
- the riskiest assumptions,
- missing information that could completely reverse the recommendation,
- questions that an inexperienced person might not know to ask.

Stop after the problem analysis and questions. Do not select technologies or architecture yet.
```

---

## Reusable prompt: assumption extraction protocol

```text
Analyze your previous architecture proposal. 
List every single assumption you made that was NOT explicitly stated in my original requirements.

Group your analysis into:
1. Concurrency, ordering, and transaction boundaries.
2. Network reliability, retry behavior, and partial failure recovery.
3. Operational complexity, infrastructure management, and team capacity.
4. Data volume, growth rate, query access patterns, and latency profiles.

For each assumption:
- Explain how the architecture fails if this assumption is completely false.
- Describe how we can verify this assumption against our production code, database, or telemetry.
```

---

## Final mental model

An LLM answer is not the architecture.

It is a proposal generated from a model of the system.

That model contains:

- facts,

- inferred consequences,

- assumptions,

- omissions,

- generic patterns.

The first task is therefore not to validate the proposed technology.

The first task is to validate the model of reality that produced the proposal.

LLMs make it possible to explore more options, learn faster, and run cheaper experiments. They should increase the amount of reversible experimentation, not the amount of irreversible architectural risk (see [[The Minimal Frame Pattern - Proving System Topology on Atomic Slices]] and [[Designing Software for AI Agents]]).

## Related Notes

- [[The Minimal Frame Pattern - Proving System Topology on Atomic Slices]] — Proving system topology through minimal, verifiable architectural slices.
- [[AI, Averaged Decisions, and Premature Convergence on Solutions]] — Avoiding generic, median architectural designs generated by models.
- [[Negative Knowledge and Explicit Architectural Dissents]] — Documenting rejected options and architectural dissenting views.
- [[Designing Software for AI Agents]] — Structuring codebases so future agents respect architectural invariants.
