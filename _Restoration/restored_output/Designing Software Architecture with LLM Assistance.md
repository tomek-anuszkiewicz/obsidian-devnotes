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
---

## The Core Engineering Reality

LLMs accelerate early-stage architectural exploration, but they cannot guarantee structural completeness. 

Used correctly, they are exceptional tools for:
- Mapping out unfamiliar technology stacks and evaluating integration patterns.
- Generating distinct, viable design alternatives.
- Extracting hard constraints from scattered requirements and architecture decision records (ADRs).
- Stress-testing trade-offs between competing approaches.
- Generating throwaway prototypes and proof-of-concept harnesses.
- Spotting well-known failure modes and edge cases.
- Performing adversarial reviews on an existing design document.

Where they fail is in the gaps between the code and reality:
- Discovering constraints that exist nowhere in the written record.
- Formulating the critical unknown-unknown questions that neither you nor the model have surfaced yet.
- Distinguishing a hard invariant from an accidental implementation quirk in legacy code.
- Capturing the tribal knowledge, political compromises, and operational habits running inside your engineers' heads.
- Raising a flag when the problem description is fundamentally underspecified.

The primary hazard when designing systems with an LLM is rarely pure hallucination. The real trap is **plausible completion**: when given an incomplete problem statement, an LLM quietly backfills the missing context with standard industry defaults. It hands you a coherent, elegant, and well-justified architecture that falls apart in production because it rests on unverified assumptions about your environment.

This creates a dangerous illusion of completeness.

---

## Plausible Answers vs. Missing Knowledge

When you feed an LLM an incomplete system description, it does not stop to demand clarification. Its training pushes it to complete the narrative. 

In system design, that means the model silently assumes:
- Eventual consistency is completely fine for the business workflow.
- Every mutating network call can be made safely idempotent.
- Messages can be retried indefinitely without out-of-order execution or duplicate billing.
- State machines are strictly linear with no messy back-transitions or manual overrides.
- No legacy reporting system or shadow ETL pipeline reads directly from your production database.
- A standard relational database engine can absorb the target write throughput.
- Zero-downtime rolling deployments will not trigger dual-version schema compatibility bugs.

In a textbook greenfield scenario, those assumptions might be reasonable. In your actual production environment, half of them are likely false. 

The dangerous part is that an answer built on false assumptions looks identical to an evidence-based design. The model will effortlessly hand you:
- Clean component diagrams and boundary definitions.
- Detailed justifications citing enterprise architecture patterns.
- Migration runbooks and sequence diagrams.
- Production-ready infrastructure-as-code and service boilerplate.
- Balanced lists of pros and cons.

Because the artifact looks professional, engineers are tempted to sign off on it without inspecting the structural assumptions underpinning the design. 

> Never treat a fluent, internally consistent response as evidence that the model actually understood your system's operational realities.

---

## Constraints Originate in the Domain

Technical constraints do not exist in a vacuum; they trace directly back to business domain invariants. 

Your reasoning chain should always move from domain rules to technical mechanisms:

```text
Business Rule
  └──> Required System Invariant
        └──> Architectural Constraint
              └──> Concrete Technology Choice
```

Look at how these map in real systems:

```text
Business Rule:
"A customer must never be billed twice for the same checkout intent."

Required System Invariant:
Payment processing must be strictly idempotent and safe against network-level retries.

Architectural Constraint:
Mutations require deterministic idempotency keys, distributed transaction boundaries, 
or strict database-level deduplication before reaching payment gateways.
```

```text
Business Rule:
"A passenger must know immediately whether their seat reservation was secured."

Required System Invariant:
The booking confirmation path cannot rely on eventual consistency or background queues.

Architectural Constraint:
The reservation workflow requires an immediate, strongly consistent synchronous commit path; 
a purely asynchronous message-driven topology is unacceptable here.
```

```text
Business Rule:
"The business must be able to audit and reconstruct the exact inputs to an automated underwriting decision years later."

Required System Invariant:
Point-in-time domain state and operational inputs must be permanently preserved and reproducible.

Architectural Constraint:
The persistence layer requires immutable append-only ledgers, event sourcing, or bi-temporal audit tables.
```

Technology choices—such as selecting a specific storage engine or messaging topology—are direct derivatives of domain requirements, not stylistic preferences.

By the same token, whenever a stated constraint surfaces—such as *"We must use SQL Server"*—interrogate it immediately. That statement might represent:
- A genuine organizational compliance and support boundary.
- Deep, battle-tested operational expertise within the reliability team.
- Substantial sunk licensing investments.
- Rigid third-party integrations running Change Data Capture (CDC) pipelines directly off transaction logs.
- Hard ACID transaction requirements across shared domain tables.
- A fragile, external enterprise reporting tool querying schemas directly.
- Or nothing more than team habit and historical inertia.

Make the model peel back the constraint. Have it identify which underlying system property actually demands that technical choice.

---

## The Three Categories of Constraints

To prevent blind spots, segment system constraints into three operational categories:

### 1. Explicit Constraints
These are clearly documented in the project context:
- Product requirements documents (PRDs) and Jira tickets.
- Architecture Decision Records (ADRs) and design RFCs.
- Internal documentation, API schemas, and service contracts.
- Explicit security, compliance, and regulatory policies.

LLMs parse and incorporate explicit constraints effectively if you keep them within the active context window.

### 2. Discoverable Constraints
These are undocumented, but they leave hard traces in your environment:
- Existing codebases, build pipelines, and configuration files.
- Unit, integration, and end-to-end test assertions.
- Production database schemas, foreign keys, and indexes.
- Deployment manifests, Helm charts, and Terraform state.
- Network routing, API gateway configs, and reverse proxy rules.
- Production telemetry, APM traces, and query execution plans.
- Incident post-mortems and bug tracker histories.

An LLM cannot guess these out of thin air. Surfacing them requires an explicit discovery phase where you feed relevant code, schemas, and metrics directly into the prompt context.

### 3. Hidden Constraints
These leave zero trace in the repository:
- Tribal knowledge retained by two senior engineers who survived the last rewrite.
- Undocumented, manual operational interventions performed during off-hours.
- Informal agreements and back-channel handoffs between teams.
- Internal organizational politics and budget boundaries.
- Wild, undocumented customer workarounds that rely on unintended system behaviors.
- Legacy edge-case exceptions grandfathered into the system years ago.

An LLM cannot discover hidden constraints. Unless you deliberately extract this information from stakeholders and add it to the prompt, the model will design around a clean abstraction that does not exist. This is where architectures fail.

---

## Stop Starting with Architecture Selection

The default, low-signal engineering pattern looks like this:

```text
Problem Description ──> Architecture Proposal ──> Implementation
```

This workflow invites disaster because it skips the discovery phase entirely. A resilient, professional design workflow forces validation before generation:

```text
Problem Description
  └──> Confirmed Production Facts
        └──> Missing System Information
              └──> Explicit Working Assumptions
                    └──> Required System Invariants
                          └──> Design Alternatives
                                └──> Adversarial Invalidation Passes
                                      └──> Conditional Recommendations
                                            └──> Implementation
```

Your initial phase must focus on **constraint discovery, not solution generation**. 

Before the model is permitted to recommend a single technology, framework, or architectural pattern, require it to surface:
- What is definitively known about the environment.
- What is being logically deduced from the input.
- What assumptions are being introduced to plug information gaps.
- What critical operational data is completely unknown.
- Which requirements are open to conflicting interpretations.
- What specific discoveries would immediately invalidate the preferred design.

Only after this baseline is locked down should the conversation shift toward system topology and tooling.

---

## Separate Facts, Inferences, Assumptions, and Unknowns

Never let an LLM present architectural reasoning as an unbroken narrative. When you allow continuous prose, assumptions blend into verifiable facts, and standard practices masquerade as firm requirements.

Force the model to categorize every key claim into five clear buckets:

### Confirmed Fact
Verified against production, source code, or binding engineering standards.
> *"Deployments use a rolling update strategy across Kubernetes pods; old and new application instances run concurrently for up to thirty minutes."*

### Inference
A strict logical deduction derived directly from confirmed facts.
> *"Any database schema migration introduced in this release must maintain backward compatibility with both the N and N-1 application versions simultaneously."*

### Assumption
A temporary working placeholder introduced because actual system context is missing.
> *"No external reporting engines or analytics workers are executing raw SQL queries directly against this table."*

### Unknown
A critical gap in domain or technical reality that has not yet been resolved.
> *"It is unknown whether message ordering must be strictly preserved across all tenants globally, or only per tenant account."*

### Typical Practice
A common industry default that may or may not fit the operational reality of this system.
> *"Placing an asynchronous message broker between the intake API and the execution worker."*

Rigidly enforcing this classification prevents plausible defaults from quietly hardening into production requirements.

---

## Interrogate What Could Invalidate the Recommendation

The single most useful prompt you can give an LLM during an architectural review is:

> *"What specific information or undiscovered system property would completely invalidate your recommendation?"*

Push the model further with questions designed to expose structural fragility:
- Under what specific traffic shapes, data volumes, or failure modes is this design the wrong choice?
- Which single assumption carries the highest risk of breaking this architecture if proven false?
- What implicit operational defaults did you assume that I never explicitly stated?
- What operational guarantees must our infrastructure provide for this system to survive? Which of those remain unverified?
- What exact property would make an alternative pattern (e.g., synchronous transactions vs. event-driven workers) the superior choice?
- Which specific components of your proposal are directly driven by my documented constraints, and which are generic industry defaults?

A production-grade recommendation is always **conditional**:

> *"If eventual consistency of up to five seconds is acceptable to the domain, mutations are guaranteed to be idempotent, and the team has the operational capacity to manage and monitor a distributed event broker, asynchronous messaging is the recommended path. If the business invariant demands an immediate, authoritative reservation confirmation to prevent overbooking, a synchronous path backed by strict database-level isolation is required."*

Conditional recommendations force engineering trade-offs into the open. Blanket recommendations obscure them.

---

## Force Exploration of the Entire Solution Space

When you ask an LLM for "a few options," it almost always returns minor variations of the exact same design pattern—like proposing Kafka, RabbitMQ, and AWS SQS for a problem that might not even need an asynchronous queue.

Demand solutions drawn from fundamentally different architectural categories:
- **The simplest possible implementation:** The lowest-complexity approach that solves the problem.
- **The zero-new-infrastructure option:** Solving the problem entirely within the existing stack (e.g., using Postgres transactional locks or `SKIP LOCKED` instead of deploying an external broker).
- **The incremental migration:** A step-by-step evolution that avoids high-risk cutovers.
- **The reversible experiment:** An implementation designed to be feature-flagged, benchmarked, and easily rolled back.
- **The conservative baseline:** The boring, battle-tested pattern with predictable operational profiles.
- **The target-state architecture:** The unconstrained, long-term ideal assuming migration costs were zero.
- **The non-obvious alternative:** An atypical but viable technical approach that challenges standard defaults.
- **The process or domain change:** Solving the problem upstream by tweaking business rules or operational processes, eliminating the technical challenge entirely.
- **The "do nothing" baseline:** Documenting the real operational and financial cost of leaving the current implementation alone.

For every proposed option, require the model to explicitly detail:
1. Prerequisites and operational conditions.
2. Underlying assumptions.
3. Quantifiable architectural benefits.
4. Concrete failure modes and operational risks.
5. Infrastructure and maintenance overhead.
6. Migration mechanics.
7. Rollback complexity if the approach fails.
8. A cheap, fast experiment to validate core assumptions.
9. Missing data points that could immediately change its evaluation.

---

## Implementation Bias and Contextual Anchoring

Even when prompted with a neutral tone, an LLM's recommendations are structurally biased.

Large language models inherently favor architectures that are:
- Heavily represented across public GitHub repositories and technical blogs.
- Extensively documented in open-source ecosystems.
- Easy to explain using textbook architectural patterns.
- Straightforward to generate as plausible, self-contained code snippets.

This is not conscious reasoning; it is a statistical reality of generative models:

```text
High-Probability Pattern in Training Data
  └──> Proposed More Frequently
        └──> Justified More Fluently
              └──> Implemented More Cleanly by the Model
```

While high implementability is a legitimate engineering consideration, it can warp architectural decisions. 

> The design pattern an LLM can generate and defend most easily is often not the design pattern that best fits your production constraints.

### The Danger of Contextual Anchoring

This bias worsens when technologies are casually dropped into the prompt history. If Kafka, Temporal, Kubernetes, MongoDB, or Event Sourcing appear anywhere in earlier turns of the conversation, the model routinely over-indexes on them. It treats those mentions as:
- An implicit architectural preference.
- Pre-approved, available infrastructure.
- A constraint that must be preserved.
- A hint about what the engineer wants to hear.

This happens even if you mentioned the technology strictly as a counter-example, a failed past experiment, or an unrelated operational detail.

```text
Technology Mentioned in Context
  └──> Token Weights Elevated in Attention Mechanism
        └──> Distorts Invariant Extraction and Trade-Off Analysis
              └──> Biases Final Architecture Recommendation
```

A question asked after discussing a specific technology is rarely context-neutral. The model will optimize for the narrative established by the conversation rather than evaluating the system from first principles.

### Countering Implementation Bias and Anchoring
- Explicitly instruct the model that previously mentioned tools are examples, not requirements.
- Demand that the model design a solution that explicitly bans the technologies already discussed.
- Require system invariants to be derived entirely from domain rules before evaluating any tooling.
- Ask the model directly: *"Which of your recommendations would change if we stripped every technology name from our conversation history?"*
- Spin up fresh, isolated conversation contexts when transitioning from brainstorming to formal architectural reviews.
- Formally categorize mentioned technologies as: **Required**, **Available**, **Preferred**, **Under Consideration**, or **Explicitly Rejected**.

Use an explicit steering prompt:

> *"Treat every previously discussed technology as non-binding unless it is listed in the confirmed system constraints. Derive the required system invariants first, then evaluate solution options without giving preference to tools already mentioned in the chat."*

The most dangerous workflow is the unvalidated feedback loop:

```text
Model Defines Evaluation Criteria
  └──> Model Selects Technology
        └──> Model Justifies Selection
              └──> Model Generates Implementation
                    └──> Model Reviews Its Own Code
```

This loop produces a completely self-consistent, beautifully documented, non-viable system. To break it, enforce human checkpoints and decouple the evaluation stages:
- Decouple design selection from code generation.
- Force options across radically different complexity tiers.
- Demand the model distinguish domain fit from its own generation confidence.
- Make human engineers approve the evaluation scorecard.
- Audit the architecture thoroughly before asking the model for a single line of implementation code.

Use this evaluation framework for critical decisions:

| Evaluation Dimension | Core Architectural Question |
| :--- | :--- |
| **Problem Fit** | How precisely does this design satisfy our confirmed domain rules and operational constraints? |
| **Evidence Quality** | Which components are backed by verified production data, and which rely on standard industry assumptions? |
| **Implementation Confidence** | How reliably can this design be implemented, tested, and maintained by the actual team? |
| **Ecosystem Familiarity** | Is this tool recommended because it is truly optimal, or because public training data for it is ubiquitous? |
| **Decision Uncertainty** | What missing metrics, production realities, or business changes would immediately invalidate this choice? |

Implementation confidence matters, but it must be an explicit, conscious trade-off—not a hidden bias steering your systems.

---

## Review the System Across Real Engineering Dimensions

Do not let the model limit its analysis to component diagrams and technology selections. Force it to evaluate the proposal across concrete systems engineering dimensions:

- **Domain Invariants:** How the design prevents invalid business states from persisting.
- **State Machine Topology:** Whether transitions are strictly deterministic, and how invalid or partial transitions are handled.
- **Data Ownership and Boundaries:** Which service is the single source of truth for every write, and whether schemas are leaking across boundaries.
- **Consistency Models:** Where strong consistency is non-negotiable versus where eventual consistency is acceptable.
- **Isolation and Concurrency:** How the system behaves under high write contention (optimistic locking, pessimistic locking, serializable transactions).
- **Network Boundaries and Transports:** Where synchronous REST/gRPC boundaries introduce latency chains versus where asynchronous messaging decouples them.
- **Message Semantics and Idempotency:** How consumers handle duplicate deliveries, out-of-order execution, and poison-pill messages.
- **Failure Domains and Retries:** Backoff intervals, circuit breakers, jitter strategies, and dead-letter queues.
- **Distributed Failure Modes:** Handling network partitions, split-brain scenarios, cascading timeouts, and downstream degraded states.
- **API and Contract Evolution:** Backward and forward compatibility, schema registries, protobuf/JSON migrations, and deprecation paths.
- **Deployment Mechanics:** Dual-version application coexistence during rolling or canary deployments.
- **Database Schema Migrations:** Expanding and contracting columns without locking production tables, handling historical data backfills.
- **Rollback Complexity:** What happens when a deployment fails mid-migration, and whether data written by the new version breaks the old version.
- **Security Boundaries:** Zero-trust network segmentation, token propagation, authentication, and authorization checkpoints.
- **Data Privacy and Governance:** PII isolation, data masking, encryption in transit and at rest, and hard deletion compliance (e.g., GDPR/CCPA).
- **Audit Trails and Lineage:** Tamper-evident logging, temporal tracking of state changes, and long-term regulatory retention.
- **Throughput, Latency, and Scalability:** P99 SLA targets, hot-spotting on shard keys, connection pool exhaustion, and CPU vs. I/O bottlenecks.
- **Telemetry and Debuggability:** Distributed trace propagation, contextual structured logging, and metric cardinality.
- **Operational Ergonomics:** Disaster recovery runbooks, automated health checks, manual operational overrides, and alert noise.
- **Cost Realities:** Network egress fees, managed service compute tiers, storage tiering, and operational licensing.
- **Team Topology and Skills:** Whether the engineering team can realistically operate, debug, and patch this stack at 3:00 AM.
- **Reversibility Score:** The blast radius and financial/time cost of unwinding this architectural choice twelve months from now.

The goal is not to fill out an exhaustive 22-point scorecard for every micro-decision. It is to quickly identify which specific dimensions pose fatal risks to this particular system.

---

## Use the Model in Specialized Adversarial Roles

An LLM asked to play generic "architect" produces generic, uncontroversial answers. To get real depth, force the model into specialized personas that mimic a complete, adversarial architectural review board.

```text
                         Architecture Proposal
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
   Domain Analyst               Skeptic                 Site Operator
  (Invariants/Rules)      (Assumptions/Failures)      (Runbooks/Deploys)
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
  Security Reviewer                                  Migration Engineer
(Trust Boundaries/Auth)                              (Rollbacks/Dual-Runs)
```

- **The Domain Analyst:** Extracts strict business invariants, domain actors, valid state lifecycles, exception pathways, and semantic ambiguities from requirements.
- **The Lead Architect:** Generates concrete design alternatives, balances structural trade-offs, and defines component boundaries.
- **The Skeptic:** Hunts for unsupported assumptions, unstated constraints, edge cases, cascading failure cascades, and conditions that break the design.
- **The Site Reliability Engineer / Operator:** Interrogates deployment topology, observability, metric cardinality, runbooks, failure recovery, failover automation, and operational maintenance burdens.
- **The Security Engineer:** Maps attack surfaces, zero-trust boundaries, sensitive data handling, least-privilege access, authorization leakage, and compliance constraints.
- **The Database / Migration Engineer:** Evaluates schema expansion and contraction, concurrent version execution, database locking behavior, asynchronous data backfills, rollback safety, and legacy integrations.

Running these prompts does not guarantee correctness, but it strips away the polite agreement that causes standard LLM outputs to gloss over production risks.

---

## Exploration Mode vs. Commitment Mode

LLMs drastically lower the cost of technical spikes. They allow teams to:
- Quickly prototype integrations against unfamiliar SDKs or frameworks.
- Generate disposable proof-of-concept services and mock harnesses.
- Run comparative simulations between competing database access patterns.
- Stress-test alternative data serialization formats.
- Scaffold out migration scripts and data transformation pipelines.

This unlocks a tight, iterative learning loop:

```text
Hypothesis ──> Cheap Prototype ──> Profiling / Testing ──> Adversarial Critique ──> Architectural Commitment
```

However, high development velocity is not the same as architectural comprehension. 

An LLM can generate a functioning prototype for an event-driven CQRS system in ten minutes. It does not equally compress the time required to understand:
- How the system behaves when the event store drops connections under load.
- The operational headache of handling out-of-order event projections.
- How to debug subtle data drift between the write and read models.
- The organizational cost of training developers to reason about eventual consistency.

To protect systems from unvetted technical debt, draw a hard line between two operational modes:

### Exploration Mode
*Objective: Maximize learning velocity and test hypotheses cheaply.*
- Generate multiple divergent design spikes.
- Prototype with unfamiliar tools and patterns.
- Accept explicitly labeled, provisional assumptions.
- Write disposable, single-use test scripts and harness code.
- Ignore enterprise-grade completeness in favor of validating technical unknowns.
- Ensure all experiments are fully isolated and easily discarded.

### Commitment Mode
*Objective: Guarantee production stability, operational safety, and system reversibility.*
- Validate all explicit, discoverable, and hidden constraints.
- Cross-reference design assumptions against authoritative vendor documentation and source code.
- Subject the design to chaos testing, concurrency checks, and failure-mode drills.
- Finalize runbooks, monitoring, and operational alerting strategies.
- Eliminate all unverified working assumptions.
- Design and dry-run rolling schema migrations and emergency rollback procedures.
- Document trade-offs in a formal ADR approved by human engineers.

The most catastrophic failure mode occurs when an exploratory spike is quietly pushed to production as permanent architecture.

---

## The Correct Role for the Model

An LLM is not an authoritative chief architect. It is an interactive, high-bandwidth accelerator for:
- Mapping unfamiliar technical terrain.
- Surfacing neglected operational questions.
- Extracting discoverable constraints from code and logs.
- Generating diverse, non-obvious alternatives.
- Stress-testing trade-offs under varying operational conditions.
- Rapidly assembling proof-of-concept harnesses.
- Conducting adversarial peer reviews.
- Drafting structured documentation and runbooks.
- Designing targeted verification suites.

The human engineering team owns final accountability for confirming the model of reality upon which the architecture depends.

When evaluating an LLM's architecture proposal, the primary question is never:
> *"Did the model produce a clean, reasonable design?"*

The primary question is always:
> *"Does this design reflect the confirmed, messy constraints of our specific production environment, or did the model quietly substitute a textbook default that will fail under load?"*

---

## The Six-Phase Architectural Workflow

To get reliable, high-signal results from an LLM during system design, follow this structured six-phase pattern:

```text
Phase 1: Discovery    ──> Force the model to inventory facts, gaps, and invariants.
Phase 2: Verification ──> Validate assumptions against production reality.
Phase 3: Generation   ──> Solicit distinct, structurally diverse design options.
Phase 4: Adversarial  ──> Assume proposals are broken; stress-test edge cases.
Phase 5: Decision     ──> Produce conditional, trade-off-driven recommendations.
Phase 6: Handoff      ──> Pass hard constraints and boundary contracts to implementers.
```

### Phase 1: Problem Discovery
Instruct the model that solutions are strictly prohibited. Demand:
- Confirmed production facts extracted from your prompt.
- Deductions logically derived from those facts.
- Explicit working assumptions introduced to bridge gaps.
- Missing operational and business context.
- Ambiguities in domain rules.
- High-impact questions ranked by their ability to change the design.

### Phase 2: Constraint Verification
Take the high-impact questions and assumptions generated in Phase 1 and validate them against reality:
- Search repositories, schemas, and pipeline definitions.
- Inspect telemetry, error budgets, and database query logs.
- Query domain experts, team leads, and product owners directly.
- Feed verified answers back to the model, converting assumptions into confirmed facts.

### Phase 3: Strategic Option Generation
Demand solution patterns drawn from fundamentally different architectural categories. Prohibit the model from naming an unconditional "winner."

### Phase 4: Adversarial Stress-Testing
Instruct the model to assume its proposed architectures are fatally flawed. Have it systematically hunt for:
- Domain invariants that break under edge cases.
- Cascading network failures, connection pool starvation, and race conditions.
- Direct database dependencies from unmonitored external systems.
- Zero-downtime deployment traps and schema lock contention.
- Operational cost explosions under non-linear data growth.
- Subtle differences between local prototype success and production failure.

### Phase 5: Conditional Recommendation
Require the model to deliver a conditional decision framework:
- The preferred option for specific operational profiles.
- The precise prerequisites under which that option remains valid.
- The production metrics or business shifts that would invalidate the choice.
- Unresolved operational risks that require runtime mitigation.
- The smallest, cheapest prototype required to validate unverified assumptions.

### Phase 6: Implementation Handoff
When handing off the approved design to an engineering team or a coding agent, provide an unambiguous operational specification:
- Core business objectives and throughput SLAs.
- Global domain invariants that must never be violated.
- Approved architectural topology and component boundaries.
- Contextual schemas and neighboring service contracts.
- Explicit working assumptions that remain in scope.
- Non-negotiable unit, integration, and concurrency tests.
- Prohibited changes (e.g., changes to legacy tables, introduced dependencies, bypassed gateways).

---

## Production-Ready Prompt Templates

Use these templates directly in your design workflows.

### Template 1: Discovery Before Design

```text
Analyze the architecture problem described below. You are strictly forbidden from proposing any solutions, patterns, or technologies in this step.

Perform a thorough constraint analysis on the input. Structure your response into these exact categories:

1. Confirmed Facts: Information explicitly stated in my description or directly verified by production evidence.
2. Inferred Deductions: Logical conclusions derived strictly from the confirmed facts.
3. Working Assumptions: Defaults, placeholders, or standard practices you are introducing to fill gaps in the description. Label these aggressively.
4. Unknown Information: Critical missing context regarding domain rules, data volumes, traffic shapes, team topologies, or legacy systems.
5. Typical Practices to Avoid: Common industry defaults (e.g., eventual consistency, microservices, asynchronous queues) that may not apply to this system.

Analyze this problem across every critical engineering dimension, explicitly including:
- Core business rules and domain invariants
- Data consistency models and transaction boundaries
- Concurrency, race conditions, and locking strategies
- Message ordering, retry semantics, and idempotency guarantees
- Partial failure modes, network splits, and downstream latency chains
- External integrations, direct database couplings, and contract schemas
- Throughput, p99 latency targets, data growth, and resource bottlenecks
- Security perimeters, authentication, trust boundaries, and compliance
- Auditability, event tracking, and regulatory retention policies
- Zero-downtime deployments, backward-compatible schema changes, and rollbacks
- Observability, trace propagation, metric cardinality, and operational debugging
- Infrastructure costs, vendor lock-in, and team operational capability

Provide a prioritized list of questions whose answers would materially alter the architectural design. Rank them by decision impact.

Surface the hidden assumptions you would normally make to design this system, identify which carry the highest operational risk, and highlight the questions an engineer might forget to ask.

Stop immediately after the analysis and questions. Propose no solutions.

[INSERT PROBLEM DESCRIPTION HERE]
```

### Template 2: Generating Distinct Architectural Alternatives

```text
Review the confirmed facts, invariants, and explicitly validated assumptions below. 

Propose viable architectural solutions drawn from structurally distinct categories. Do not give me minor variations of the same pattern.

You must provide options from these categories:
1. The Simplest Solution: Minimal complexity, zero accidental engineering.
2. Zero-New-Infrastructure: Solves the problem purely using our existing production stack.
3. The Incremental Evolution: Low-risk, step-by-step transition with no big-bang cutovers.
4. The Reversible Spike: Optimized for rapid validation, instrumentation, and easy rollback.
5. The Conservative Standard: Boring, predictable, battle-tested enterprise architecture.
6. The Long-Term Target: The unconstrained ideal architecture assuming zero migration drag.
7. The Non-Obvious Alternative: An unusual but structurally viable design pattern.
8. The Process/Domain Alternative: A non-technical change to upstream business logic or operations that eliminates the engineering problem entirely.

For each option, provide:
- Core Mechanism: How it fundamentally works.
- Prerequisites: What must be true about our infrastructure, team, and systems for this to work.
- Underlying Assumptions: What this design assumes about traffic, consistency, and operations.
- Best Fit: The precise conditions where this option is optimal.
- Worst Fit: The conditions where this option fails catastrophically.
- Engineering and Operational Risks: Failure modes, concurrency bottlenecks, and operational debt.
- Deployment and Rollback Mechanics: How this is released without downtime, and how it is unwound if it fails.
- Validation Spike: The cheapest, fastest prototype or experiment to prove its viability.
- Invalidation Triggers: Discoveries that would remove this option from consideration.

Do not declare any option unconditionally superior. Present the trade-offs objectively.

[INSERT CONFIRMED FACTS, INVARIANTS, AND ASSUMPTIONS HERE]
```

### Template 3: Adversarial Review

```text
Assume the proposed architectural design below is fundamentally flawed and will fail in production. 

Perform an adversarial review to expose its failure modes. Specifically interrogate:
- Undocumented assumptions masquerading as confirmed facts.
- Unstated domain constraints that break the core model.
- Concurrency limits, race conditions, write skew, and deadlocks.
- Distributed failure modes: network partitions, connection starvation, cascading timeouts.
- Idempotency leaks, duplicate mutations, out-of-order message delivery, and poison pills.
- Zero-downtime rolling update incompatibilities and database migration locks.
- Operational maintenance burdens, debugging obscurity, and runbook complexity.
- Cross-team organizational friction, skill gaps, and unowned dependencies.
- Subtleties where this pattern succeeds in a local proof-of-concept but degrades under production scale.

Answer these questions directly:
1. What non-negotiable operational conditions must hold for this architecture to survive?
2. Which of those conditions are currently unverified in our context?
3. What specific piece of missing information would instantly invalidate this recommendation?
4. What exact tests, benchmarks, metric analyses, schema queries, or stakeholder reviews are required to validate the working assumptions?
5. Which parts of this design are directly derived from our explicit context, and which are generic industry defaults imported by the model?

Be ruthlessly specific. Point to concrete runtime mechanisms, network boundaries, and data layouts.

[INSERT PROPOSED ARCHITECTURE HERE]
```

---

## The Mental Model

An LLM output is not an architecture. It is an unverified projection generated from an incomplete mental model of your system.

That internal projection is composed of:
- A handful of verified facts you remembered to supply.
- Deductions the model drew from those inputs.
- Unverified assumptions introduced to smooth over missing context.
- Glaring real-world omissions hidden behind professional prose.
- Statistical industry averages lifted from public repositories.

Your first responsibility as an engineer is not to review the proposed technology stack. It is to **interrogate and validate the model of reality that produced that proposal**.

LLMs give us the leverage to explore wider design spaces, run faster prototyping spikes, and spot failure modes earlier than ever before. Use them to aggressively expand cheap, reversible experimentation—never to introduce irreversible architectural risk into your production systems.
