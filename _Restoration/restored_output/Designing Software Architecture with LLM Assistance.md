# LLM-Assisted Systems Design

LLMs generate plausible architectures but miss undocumented boundaries.
Models fill unstated requirements with typical defaults.
They implicitly assume eventual consistency, idempotent endpoints, or linear states.
These defaults often fail in production systems.
Never accept fluent output as proof of technical accuracy.
Audit core assumptions before picking technologies or writing code.

---

## Deriving Constraints from Invariants

Technical choices stem from business invariants.
Always trace choices through this derivation chain:

```text
Business Rule -> System Invariant -> Architecture Constraint -> Technology Choice
```

Examples:
- **Rule**: Never double-charge a customer.
  - **Invariant**: Operations require duplicate execution prevention.
  - **Constraint**: Enforce idempotency keys with unique database constraints.
- **Rule**: Deliver immediate booking confirmations.
  - **Invariant**: The user path cannot rely on asynchronous convergence.
  - **Constraint**: Use synchronous ACID transactions over eventual consistency.
- **Rule**: Audit decision inputs five years later.
  - **Invariant**: Preserve point-in-time state transitions and inputs.
  - **Constraint**: Implement an immutable, append-only event log.

Challenge arbitrary mandates like "must use PostgreSQL".
Extract the underlying driver: license limits, reporting tools, DBA skills, or legacy habit.

---

## Constraint Taxonomy

Classify constraints into three operational groups:

- **Explicit**: Exists in ADRs, tickets, specifications, and schemas. Models parse these well.
- **Discoverable**: Exists in codebases, configs, migrations, and telemetry. Extract these with targeted prompts.
- **Hidden**: Exists in tribal memory, manual runbooks, and informal agreements. Humans must supply this context.

---

## Discovery-First Architecture Workflow

Do not jump directly to stack selection.

Flawed pipeline:
```text
Problem -> Tech Stack -> Code
```

Pragmatic pipeline:
```text
Problem -> Facts -> Gaps -> Invariants -> Alternatives -> Invalidation -> Stack Choice
```

Structure context into five explicit categories:
1. **Confirmed Fact**: Verified property backed by code, tests, or production metrics.
2. **Inference**: Logical deduction derived directly from confirmed facts.
3. **Assumption**: Temporary placeholder filling a context gap.
4. **Unknown**: Unresolved variable requiring investigation.
5. **Common Practice**: Industry default that might fail your specific workload.

---

## Bias and Context Anchoring

Models suffer from contextual anchoring.
Mentioning a tool primes the model to recommend it.
The model designs around mentioned tools, even when unsuited for the workload.
Reset context windows when evaluating critical architectural forks.
Instruct the model to solve the problem without previously mentioned technologies.

Models also favor patterns frequent in public training data.
Easy generation does not indicate correct architecture.
Evaluate proposals against this matrix:

| Dimension | Evaluation Focus |
| :--- | :--- |
| **Problem Fit** | Satisfies verified business invariants |
| **Grounding** | Draws from project telemetry or code |
| **Operational Risk** | Quantifies failure modes, rollouts, and rollback costs |
| **Availability Bias** | Over-indexes on boilerplate code and documentation |

---

## Strategic Solution Exploration

Reject homogeneous technology options.
Force alternatives across distinct strategic archetypes:
- **Simplest viable**: Minimum moving parts.
- **Existing stack**: Zero new operational dependencies.
- **Reversible experiment**: High-leverage feature flag or adapter pattern.
- **Non-technical change**: Policy shift or dropped requirement.
- **Long-term architecture**: Eventual target state under sustained scale.

Require explicit failure modes, operational burdens, and rollback mechanics for every option.

---

## Dual Operating Modes

Run architecture work in two separate modes:

### Exploration Mode
- Prioritize discovery speed.
- Build quick spikes.
- Test unfamiliar libraries.
- Accept labeled assumptions.
- Write throwaway prototypes.

### Commitment Mode
- Prioritize correctness and reversibility.
- Verify edge cases.
- Audit failure domains.
- Write migration scripts.
- Eliminate hidden assumptions.
- Require human sign-off.

Never promote an exploration prototype directly to production.

---

## Review Roles and System Dimensions

Prompt the model through distinct operational personas:
- **Domain Analyst**: Extract business invariants, actors, state transitions, and edge cases.
- **Architect**: Map tradeoffs, state boundaries, component coupling, and blast radiuses.
- **Skeptic**: Find broken assumptions, scale limits, poison messages, and race conditions.
- **Operator**: Review deployment mechanics, zero-downtime rollouts, observability, and disaster recovery.
- **Security Lead**: Audit trust boundaries, auth models, data retention, and compliance limits.

Audit every proposal across these technical vectors:
- **State**: Concurrency, idempotency keys, ordering guarantees, transactional boundaries.
- **Failure**: Partial outages, cascading failures, backoff retries, dead-letter queues.
- **Operations**: Dual-write avoidance, backward schema compatibility, telemetry, rollback cost.

---

## Core Architecture Prompts

### Discovery Prompt
```text
Analyze this system problem. Do not propose solutions yet.

Separate the input into:
- Confirmed facts
- Inferences derived from facts
- Working assumptions
- Missing information
- Generic defaults that might fail here

Highlight business invariants, concurrency models, transactional boundaries, and failure states.
List questions whose answers could reverse the architectural direction.
Rank questions by impact.
Stop here.
```

### Alternatives Prompt
```text
Generate distinct architectural options using only confirmed facts and explicit assumptions.

Include these archetypes:
- Simplest viable design
- Zero-new-infrastructure design (existing stack only)
- Reversible experiment
- Non-technical or process-level fix
- Long-term target architecture

For each option detail:
1. Required system properties
2. Operational cost and blast radius
3. Failure modes
4. Migration and rollback strategy
5. Information that invalidates this choice

Do not declare any option universally superior.
```

### Adversarial Invalidation Prompt
```text
Assume this proposed solution fails in production.

Identify:
- Unstated assumptions
- Latent race conditions and concurrency failures
- Partial outage behaviors
- Deployment or backward-compatibility traps
- Production costs hidden during prototyping

Answer:
1. What unverified condition breaks this system?
2. What findings reverse this decision?
3. What benchmarks or tests prove this design?
