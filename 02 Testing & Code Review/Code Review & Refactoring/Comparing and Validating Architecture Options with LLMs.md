---
title: "Comparing and Validating Architecture Options with LLMs"
tags:
  - software-architecture
  - llm
  - decision-making
  - prototyping
  - tradeoff-analysis
aliases:
  - "LLM-Assisted Architecture Option Evaluation"
  - "Architecture Experiments and Conditional Decisions"
  - "Challenging Model Architecture Recommendations"
---

The team has a set of architectural constraints and several plausible designs. Asking an LLM to recommend one can produce a confident answer without showing whether it considered a simpler solution, reused existing infrastructure, or favored a technology it can implement comfortably.

Compare strategies against explicit conditions before committing. Explore different categories of solutions, ask which missing fact would reverse the ranking, and design small experiments that can discriminate between the options. The model can take several analytical roles, but agreement among generated reviews is still a proposal to check against evidence.

[[Designing Software Architecture with LLM Assistance]] develops the prior work of establishing constraints and separating knowledge from assumptions. This article follows option generation, bias, cross-disciplinary review, experimentation, and the point at which an approved decision begins governing implementation. The reusable prompts stay beside the stages they support.

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

Keep the decision conditional on the properties actually verified. Preserve rejected alternatives and the observations that would justify reopening them, then give implementation the chosen constraints and evidence rather than an unexplained technology preference.

## Related Notes

- [[Designing Software Architecture with LLM Assistance]] — Discovering business constraints and distinguishing facts from plausible defaults.
- [[The Minimal Frame Pattern - Proving System Topology on Atomic Slices]] — Testing a consequential architectural path with a small running slice.
- [[Negative Knowledge and Explicit Architectural Dissents]] — Keeping rejected assumptions and alternatives available to later work.
