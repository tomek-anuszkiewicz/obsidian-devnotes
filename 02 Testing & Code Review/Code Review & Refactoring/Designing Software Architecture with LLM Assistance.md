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

## Ask for the whole solution space, not only several technologies

When asked for “a few options,” the model may generate several variations of the same idea.

Instead, request options from different strategic categories:

- the simplest solution,
    
- a solution using existing infrastructure,
    
- an incremental solution,
    
- a reversible experiment,
    
- a conservative solution,
    
- a long-term target architecture,
    
- a less obvious but realistic option,
    
- a non-technical process change,
    
- changing or removing the requirement,
    
- doing nothing for now.
    

For every option, require:

- applicability conditions,
    
- assumptions,
    
- benefits,
    
- risks,
    
- operational cost,
    
- migration path,
    
- rollback difficulty,
    
- validation method,
    
- information that could change its evaluation.
    

---

## The model may prefer solutions it can implement comfortably

Even when the user asks a neutral question and does not suggest an answer, the resulting recommendation is not necessarily neutral.

An LLM tends to favor solutions that are:

- common in its training data,
- well documented,
- represented by many public examples,
- easy to explain using familiar patterns,
- easy for the model to turn into plausible code.

The model does not have to consciously decide, “I will choose this because I can implement it.” The bias arises indirectly:

```text
Familiar and high-probability approach
→ proposed more often
→ justified more fluently
→ implemented more successfully by the same model
```

This correlation is useful, because implementability matters. However, it can also narrow the solution space.

> The solution the model can describe and generate most confidently is not necessarily the solution that best fits the problem.

### Earlier context can anchor the recommendation

The bias can be triggered by merely mentioning a technology earlier in the conversation.

For example, if SQL Server, Kafka, Temporal, Kubernetes, microservices, or event sourcing appeared anywhere in the preceding discussion, the model may assign that technology more importance than it deserves. It may interpret the mention as:

- an implicit preference,
- an available part of the infrastructure,
- a constraint that should be preserved,
- evidence that the user expects the technology to be used,
- or the intended direction of the conversation.

This can happen even when the technology was mentioned only as an example, comparison point, rejected idea, or unrelated background detail.

The effect is a form of contextual anchoring:

```text
Technology appears in the context
→ becomes more available during generation
→ shapes the alternatives and evaluation criteria
→ is more likely to be recommended
```

Therefore, a neutral-sounding question asked after discussing a specific technology is not fully context-neutral. The model may produce a high-quality answer to the solution space implied by the conversation rather than reconsidering the entire solution space from first principles.

To reduce contextual anchoring:

- state explicitly that previously mentioned technologies are examples, not requirements,
- ask the model to solve the problem once without using any technologies already mentioned,
- request alternatives derived only from confirmed requirements,
- ask which recommendations would disappear if the earlier technology names were removed from the conversation,
- use a fresh context or an independent reviewer for important decisions,
- distinguish technologies that are required, available, preferred, merely considered, and explicitly rejected.

A useful instruction is:

> Treat every previously mentioned technology as non-binding unless it appears in the confirmed constraints. Derive the required system properties first, then generate alternatives without privileging technologies already present in the conversation.

A particularly risky workflow is:

```text
The model selects the criteria
→ selects the technology
→ justifies its own selection
→ implements it
→ reviews its own result
```

The entire chain may be internally consistent while optimizing for an unverified interpretation of the problem. A convincing implementation can then be mistaken for evidence that the architectural choice was correct.

To reduce this bias:

- separate solution selection from implementation,
- ask for alternatives from genuinely different strategic categories,
- require the model to distinguish problem fit from its confidence in implementation,
- explicitly include less familiar or harder-to-generate approaches when they may fit the constraints,
- let a human define or approve the evaluation criteria,
- use an independent review that does not inherit the original recommendation as a fact,
- evaluate the architecture before showing how easily code can be generated for it.

A useful question is:

> Is this solution recommended because it best satisfies the confirmed constraints, or because it is popular, well documented, and easy for the model to implement?

The model cannot perfectly inspect its own internal reasoning, so its answer should not be treated as proof. The question is still valuable because it forces an explicit comparison between problem fit, ecosystem familiarity, and implementation confidence.

For important decisions, ask the model to report these dimensions separately:

| Dimension | Question |
| --- | --- |
| Problem fit | How well does the option satisfy confirmed requirements and constraints? |
| Evidence quality | Which parts are supported by project evidence rather than generic practice? |
| Implementation confidence | How reliably can the model produce and test the implementation? |
| Ecosystem familiarity | Is the recommendation favored because examples and documentation are abundant? |
| Decision uncertainty | Which missing information could change the ranking? |

Implementation confidence is a legitimate criterion, but it should be visible and weighted deliberately rather than silently determining the architecture.

---


## Review the problem across multiple dimensions

A model should be asked to inspect the problem from several perspectives, not only technology selection.

Useful dimensions include:

- business rules and invariants,
    
- state transitions,
    
- data ownership,
    
- consistency,
    
- transactions,
    
- concurrency,
    
- ordering,
    
- duplication and idempotency,
    
- retries and timeouts,
    
- partial failures,
    
- integration contracts,
    
- version compatibility,
    
- deployment strategy,
    
- rollback,
    
- migration,
    
- security and trust boundaries,
    
- privacy,
    
- auditability,
    
- retention,
    
- performance,
    
- scale,
    
- observability,
    
- diagnostics,
    
- operational support,
    
- cost,
    
- team expertise,
    
- vendor lock-in,
    
- reversibility.
    

The purpose is not to generate an enormous checklist for every decision.

The purpose is to identify which dimensions can materially change this specific decision.

---

## Use the model in multiple roles

A single model can be prompted to perform different reviews.

### Domain analyst

Extracts:

- business rules,
    
- actors,
    
- invariants,
    
- states,
    
- exceptions,
    
- ambiguous behavior.
    

### Architect

Generates design alternatives and trade-offs.

### Skeptic

Searches for:

- hidden assumptions,
    
- missing constraints,
    
- failure scenarios,
    
- cases that invalidate the recommendation.
    

### Operator

Checks:

- deployment,
    
- monitoring,
    
- rollback,
    
- support procedures,
    
- failure recovery,
    
- maintenance cost.
    

### Security reviewer

Checks:

- trust boundaries,
    
- sensitive data,
    
- authorization,
    
- abuse scenarios,
    
- compliance implications.
    

### Migration reviewer

Checks:

- old and new versions running together,
    
- schema compatibility,
    
- staged rollout,
    
- backfill,
    
- rollback,
    
- external consumers.
    

Using multiple roles does not make the model automatically correct.

It forces the reasoning to be examined from different angles.

---

## Exploration mode and commitment mode

LLMs are especially valuable because they reduce the cost of experimentation.

They allow teams to:

- explore unfamiliar approaches,
    
- build prototypes quickly,
    
- compare several options,
    
- generate test harnesses,
    
- simulate migrations,
    
- investigate new libraries,
    
- prepare disposable proofs of concept.
    

This supports a more experimental architecture process:

```text
Hypothesis
→ cheap prototype
→ measurement
→ criticism
→ decision
```

However, fast implementation must not be confused with understanding.

The model greatly reduces the cost of entering a new solution, but may not equally reduce the cost of understanding:

- its failure model,
    
- operational complexity,
    
- long-term maintenance,
    
- migration difficulty,
    
- scaling behavior,
    
- guarantees and limitations,
    
- organizational impact.
    

Therefore it is useful to distinguish two modes.

### Exploration mode

Optimize for speed and learning.

- Generate many ideas.
    
- Try unfamiliar technologies.
    
- Accept explicitly labeled temporary assumptions.
    
- Build disposable prototypes.
    
- Avoid production-level completeness.
    
- Prefer reversible experiments.
    

### Commitment mode

Optimize for correctness and reversibility.

- Confirm constraints.
    
- Verify primary documentation.
    
- Test failures and edge cases.
    
- Review operational requirements.
    
- Remove hidden assumptions.
    
- Plan migration and rollback.
    
- Record the architecture decision.
    
- Require human approval.
    

The dangerous transition is when an exploration prototype silently becomes production architecture.

---

## Designing for downstream agent maintenance

When designing software that will be maintained, extended, or refactored by coding agents, the system architecture itself must be structured to accommodate agent capabilities and context limits:

1. **Focused 1:1 Module Boundaries**: Avoid sprawling files or "god classes" containing thousands of lines of mixed responsibilities. When an agent must ingest massive files to make a minor change, you burn context window budget and increase the risk of hallucinated regressions. Keep domain logic decomposed into cohesive, single-purpose modules.
2. **Explicit Dependency Injection**: Avoid dynamic reflection, ambient global state, or hidden runtime auto-wiring. If an agent cannot trace where a service or repository is injected by inspecting the static Abstract Syntax Tree (AST), it cannot reliably reason about module behavior or write clean unit tests.
3. **Automated Verification Harnesses**: Every architectural boundary requires a fast, deterministic test harness. An agent cannot safely refactor an architectural component unless it can execute a local test suite and get unambiguous, sub-second feedback on whether it broke an invariant.

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

## Practical conversation pattern

### Phase 1: problem discovery

Ask the model not to design anything yet.

Request:

- confirmed facts,
    
- inferred consequences,
    
- assumptions,
    
- unknowns,
    
- ambiguities,
    
- missing dimensions,
    
- questions ranked by decision impact.
    

### Phase 2: constraint verification

For each important claim, identify:

- its source,
    
- confidence,
    
- effect on the architecture,
    
- method of verification.
    

### Phase 3: option generation

Generate alternatives from meaningfully different categories.

Do not allow an unconditional recommendation.

### Phase 4: adversarial review

Assume each proposal is wrong.

Search for:

- domain properties that invalidate it,
    
- partial failure scenarios,
    
- hidden consumers,
    
- deployment problems,
    
- migration traps,
    
- operational costs,
    
- POC-to-production gaps.
    

### Phase 5: conditional recommendation

State:

- the preferred option,
    
- the assumptions under which it is preferred,
    
- the conditions that would change the recommendation,
    
- unresolved risks,
    
- required experiments or measurements.
    

### Phase 6: implementation

Provide the implementing agent with:

- business goal,
    
- global invariants,
    
- approved architecture,
    
- local module context,
    
- neighboring contracts,
    
- known assumptions,
    
- required tests,
    
- prohibited changes.
    

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

## Reusable prompt: generating alternatives

```text
Based only on confirmed facts and explicitly stated assumptions, generate meaningfully different solution options.

Include:

- the simplest option,
- an option using the current system,
- an incremental option,
- a reversible option,
- a conservative option,
- a long-term target option,
- a less obvious but realistic option,
- changing the requirement or avoiding a technical solution.

For each option, provide:

1. What it solves.
2. The conditions it requires.
3. Its assumptions.
4. When it is a good choice.
5. When it is a bad choice.
6. Costs and risks.
7. Operational consequences.
8. Migration and rollback difficulty.
9. A cheap experiment that could validate it.
10. Missing information that could change its evaluation.

Do not present any option as unconditionally best.
```

---

## Reusable prompt: adversarial review

```text
Assume the proposed solution is wrong.

Find:

- hidden assumptions,
- missing constraints,
- edge cases,
- unusual domain properties,
- concurrency problems,
- partial failures,
- retry and duplication issues,
- migration and deployment risks,
- operational costs,
- organizational dependencies,
- cases where the solution works in a proof of concept but fails in production.

Then answer:

1. What must be true for the solution to work?
2. Which of those conditions have not been verified?
3. What could completely reverse the recommendation?
4. What tests, measurements, documents, code analysis, or stakeholder conversations would verify the assumptions?
5. Which parts come from the actual context, and which come only from generic best practices?
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

## Reusable prompt: adversarial failure post-mortem

```text
Assume we adopted your recommended architecture and deployed it to multi-tenant production. 
Six months later, during a major traffic surge, the system suffers an unrecoverable 4-hour outage.

Write the post-mortem report:
1. Document the exact cascading failure sequence (e.g., connection pool exhaustion, unhandled retry storm, distributed deadlocks, backpressure failure).
2. Which component failed because of an unstated assumption about our workload?
3. Why did standard health checks and observability dashboards fail to catch the root cause early?
4. What fundamental architectural trade-off was violated?
5. How should the architecture be modified to make this failure mode structurally impossible?
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
