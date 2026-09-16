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

# Designing Software Architecture with LLM Assistance

When you ask an LLM to design an architecture for a new system, it can generate a clean, professional document in seconds. It will readily propose microservices, event streaming pipelines, caching strategies, and well-defined component boundaries. It will produce sequence diagrams, migration roadmaps, and plausible code snippets.

The risk is rarely outright hallucination. The real danger is far more subtle: **the proposal will sound completely plausible while resting on unverified assumptions.**

An LLM's architecture proposal is not an authoritative design. It is a working hypothesis generated from an incomplete model of your system. Because language models are trained on public documentation, open-source repositories, and standard patterns, they silently fill gaps in your requirements with industry defaults. 

Our job as architects is not to choose between the technologies the model proposes. Our job is to validate the model of reality that produced the proposal in the first place.

---

## Where Models Excel and Where They Struggle

LLMs are effective accelerators during the early phases of architectural exploration, but they cannot guarantee completeness.

```text
┌──────────────────────────────────────────┐  ┌──────────────────────────────────────────┐
│              MODEL STRENGTHS             │  │             MODEL WEAKNESSES             │
├──────────────────────────────────────────┤  ├──────────────────────────────────────────┤
│ • Exploring unfamiliar technology stacks │  │ • Discovering undocumented constraints   │
│ • Generating orthogonal trade-off sets   │  │ • Knowing what questions to ask when     │
│ • Rapidly drafting exploratory spikes    │  │   neither side knows the domain quirk    │
│ • Extracting constraints from text       │  │ • Separating true domain requirements    │
│ • Identifying common distributed hazards │  │   from accidental legacy implementation  │
│ • Adversarially reviewing proposals      │  │ • Grasping tribal, unwritten context     │
│ • Reviewing existing ADRs for gaps       │  │ • Flagging that requirements are missing │
└──────────────────────────────────────────┘  └──────────────────────────────────────────┘
```

The most deceptive behavior of an LLM is cognitive silence: **the model rarely tells you that your prompt lacks the information needed to make an architectural decision.** Instead of stopping to ask whether your workloads require read-your-writes consistency or what your p99 latency target is, it assumes a reasonable default and generates an entire system on top of it.

---

## The Plausibility Trap

When a problem description is underspecified, an LLM completes the narrative using generic best practices. It will routinely assume:

- Eventual consistency is completely acceptable.
- Network operations and downstream webhooks are inherently idempotent.
- Messages can be safely retried without out-of-order execution or duplicate side effects.
- Domain status transitions are strictly linear.
- No external legacy system or reporting engine reads your database directly.
- A standard relational database or an out-of-the-box Kafka cluster matches your operational capabilities.
- Rolling deployments will not introduce schema or protocol compatibility issues.
- Database connection pools can absorb bursts without deadlock or starvation.

In a greenfield system built by an experienced platform team, those assumptions might be reasonable. In an established enterprise codebase with complex invariants and constrained operational budgets, any one of them can sink a project.

```text
Underspecified Problem Statement
               │
               ▼
[ Model Fills Gaps with Plausible Tropes ]
(Assumes linear state transitions, eventual consistency, cheap transactions)
               │
               ▼
Polished, Highly Plausible Architecture Proposal
               │
    ┌──────────┴───────────────────────────────────────────┐
    ▼                                                       ▼
Unexamined Acceptance                               Rigorous Reality Testing
Assumptions accepted as fact                        1. Extract implicit assumptions
Cascading failures in production                    2. Map business rules to invariants
                                                    3. Force multi-vector divergence
                                                    4. Run cheap empirical spikes
```

A fluent, beautifully formatted, and internally consistent response is not evidence that the model understood your problem. It is only evidence that the model is good at generating fluent, internally consistent text.

---

## Business Requirements Dictate Technical Constraints

Technical constraints rarely start in the infrastructure layer; they originate in core business rules. 

A reliable reasoning chain moves from the domain downward:

```text
Business requirement
→ required system property
→ architectural constraint
→ technology choice
```

Consider how domain invariants dictate concrete infrastructure choices:

```text
Business rule:
A customer must never be charged twice for the same purchase.

Required system property:
Duplicate execution must be impossible or provably safe.

Architectural consequence:
Strict transactional boundaries, client-generated idempotency keys, 
and database-level deduplication are mandatory.
```

```text
Business rule:
A user must receive immediate confirmation whether a seat reservation succeeded.

Required system property:
The operation cannot rely on eventual consistency.

Architectural consequence:
A purely asynchronous message queue is insufficient; 
the write path must be synchronous and strongly consistent.
```

```text
Business rule:
Compliance auditors must be able to reconstruct the exact state of an account 
and the inputs to an underwriting decision seven years after the fact.

Required system property:
Historical state, decision inputs, and mutation sequences must be immutable.

Architectural consequence:
Audit logs, append-only ledgers, or an event-sourced audit trail 
must be designed into the persistence layer.
```

When an engineering team says, "We must use PostgreSQL" or "We need Kafka," treat that statement with healthy skepticism. That requirement might reflect:

- A hard operational standard supported by platform tooling.
- Existing operational expertise and runbooks.
- Strict licensing or regulatory boundaries.
- Tight integration dependencies with existing reporting pipelines.
- Fundamental transactional requirements.
- Or simply institutional habit.

Before locking down an architecture, prompt the model to analyze what underlying operational or domain requirement actually justifies the technical constraint.

---

## The Three Categories of Constraints

When reviewing an architecture with an LLM, group the constraints into three distinct buckets:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. EXPLICIT CONSTRAINTS                                                │
│    Documented in ADRs, tickets, specs, SLAs, and security policies.   │
│    The model handles these well if you paste them into the context.    │
├────────────────────────────────────────────────────────────────────────┤
│ 2. DISCOVERABLE CONSTRAINTS                                            │
│    Unwritten, but present in code, database schemas, CI/CD manifests,  │
│    telemetry dashboards, and historical incident post-mortems.         │
│    Requires deliberate discovery and repository analysis.             │
├────────────────────────────────────────────────────────────────────────┤
│ 3. HIDDEN CONSTRAINTS                                                  │
│    Exist only in institutional memory, unwritten team agreements,      │
│    undocumented client quirks, and legacy operational workarounds.     │
│    The model cannot guess these. You must actively uncover them.      │
└────────────────────────────────────────────────────────────────────────┘
```

Hidden constraints represent the highest architectural risk. If an LLM is unaware that a third-party billing gateway drops connections under load, or that your database handles batch analytical queries over the primary replica every midnight, its architectural proposal will look brilliant on paper and fall apart on deployment.

---

## The Design Process: Discovery Before Selection

A common anti-pattern when collaborating with LLMs is jumping straight from a high-level prompt to an architectural pattern:

```text
Weak Process:
Problem description → Architecture proposal → Implementation
```

This bypasses the critical analytical phase. A resilient process forces constraint extraction and falsification before evaluating solutions:

```text
Strong Process:
Problem description
→ Confirmed facts
→ Missing information
→ Working assumptions
→ Required system properties
→ Divergent design alternatives
→ Adversarial invalidation pass
→ Conditional recommendation
→ Disposable spike / empirical validation
→ Implementation
```

The initial phase must focus on problem discovery, not solution selection. Before drafting component diagrams, make the model state:

- What is known as a confirmed fact.
- What has been inferred from those facts.
- What is being assumed to make progress.
- What critical information is completely unknown.
- What requirements can be interpreted in multiple ways.
- What discovered detail would completely invalidate the proposal.

---

## Separate Facts, Inferences, Assumptions, and Unknowns

To prevent plausible assumptions from silently hardening into concrete requirements, force the model to categorize its inputs and outputs using strict epistemological boundaries:

### Confirmed Fact
Supported by trusted, verifiable project evidence.
> *"Deployments use a rolling strategy where old and new service instances run concurrently for up to 30 minutes."*

### Inference
A direct logical consequence derived from confirmed facts.
> *"Database migrations must remain backward-compatible with both service versions throughout the 30-minute deployment window."*

### Assumption
A temporary working hypothesis adopted because information is missing.
> *"No legacy reporting jobs query the modified table directly during write operations."*

### Unknown
A critical variable that has not yet been established.
> *"Whether message ordering must be strictly preserved across all customer tenants, or only within a single tenant boundary."*

### Typical Practice
An industry-standard recommendation that might be unnecessary or inappropriate here.
> *"Deploying an external distributed task orchestrator like Temporal to manage long-running checkout flows."*

By forcing this separation in the prompt context, you immediately identify where the design is grounded in your actual codebase and where it is leaning on generic industry habits.

---

## Ask What Reverses the Recommendation

The most useful question you can ask an LLM about an architectural design is:

> *"Which missing piece of information would make your current recommendation completely wrong?"*

Other high-leverage falsification questions include:

- Under what specific workload or failure conditions does this design break?
- Which of your working assumptions carries the highest blast radius if false?
- What did you assume about our operational infrastructure that I did not provide?
- What must be true about our network, storage, and concurrency patterns for this to succeed?
- Which system property would immediately make an alternative approach superior?
- Which specific recommendations stem directly from my provided context, and which are generic industry defaults?

Good architectural recommendations are always conditional:

> *"If read latency under 15ms is required, write volume is under 200 operations per second, and your team does not have dedicated infrastructure engineers, a vertically scaled relational database with an in-memory cache is optimal. If writes exceed 10,000 operations per second and cross-region active-active persistence is mandatory, an asynchronous event-streamed pipeline becomes necessary—despite its operational complexity."*

Conditional recommendations provide clear operational boundaries. Blanket recommendations provide a false sense of security.

---

## Forcing Divergence: The 8 Solution Categories

When you ask an LLM for "a few design options," it will typically offer minor variations of the exact same distributed pattern: one using Kafka, one using RabbitMQ, and one using AWS SQS.

To prevent premature convergence (see [[AI, Averaged Decisions, and Premature Convergence on Solutions]]), force the model to produce options across genuinely orthogonal strategies:

```text
                                Architectural Request
                                          │
    ┌──────────────┬──────────────┬───────┴──────┬──────────────┬──────────────┐
    ▼              ▼              ▼              ▼              ▼              ▼
[ SIMPLEST ] [ EXISTING ]   [ INCREMENTAL] [ REVERSIBLE ]  [ CONSERVATIVE] [ TARGET ]
Monolith,    Current DB,    Adapter pattern, Small spike,  Boring tech,    Microservices,
single node  cron jobs      side-by-side    feature flag   proven ops      event sourcing
```

Require the model to span these specific categories:

1. **The Simplest Solution**: A single process, minimal moving parts, no distributed state, and simple data models.
2. **The Existing Infrastructure Solution**: Solves the problem entirely using tools, databases, and message buses your team already operates.
3. **The Incremental Solution**: An evolutionary change that delivers value without requiring an immediate, high-risk migration.
4. **The Reversible Experiment**: An implementation isolated behind an interface or adapter that can be discarded with minimal effort if it fails.
5. **The Conservative Solution**: Uses established, "boring" technology that your team has maintained for years.
6. **The Long-Term Target Architecture**: How the system would look if designed for 10x current scale with dedicated staffing.
7. **The Unorthodox Alternative**: A viable but less common architectural pattern (such as SQLite at the edge or static generation).
8. **The Non-Technical or Process Change**: Eliminates the engineering problem entirely by adjusting business rules, SLAs, or batch schedules.
9. **The Do-Nothing Option**: The operational, financial, and technical cost of leaving the current system as it is.

For every option generated, require the model to document:
- Core trade-offs optimized for.
- Mandatory conditions for success.
- Concrete failure modes where this option is a disaster.
- Operational cost and ongoing maintenance overhead.
- Migration complexity and rollback difficulty.
- A 24-hour empirical spike or benchmark to prove or disprove viability.

---

## Implementation Bias and Contextual Anchoring

Even when you write a neutral prompt, an LLM's recommendation is inherently skewed by two mechanical biases: **training distribution** and **contextual anchoring**.

### Implementation Bias

An LLM favors architectures that are heavily represented in its training data, thoroughly documented in open-source ecosystems, and simple to express in code.

```text
Common & highly represented approach
→ Generated more frequently
→ Justified with greater fluency
→ Implemented with fewer syntax errors by the model
```

A model will confidently recommend an out-of-the-box microservice pattern backed by Redis and Kafka not because it fits your operational footprint, but because it has millions of tokens of documentation, tutorials, and examples to draw from. Conversely, a clean, highly customized in-memory ring buffer or an idiosyncratic batch process may fit your workload better, but the model struggles to generate it reliably.

> **Do not confuse how easily an LLM can generate code for an architecture with how well that architecture fits your production reality.**

### Contextual Anchoring

Simply mentioning a technology earlier in your chat context anchors the model. If you mention Kafka, Kubernetes, DynamoDB, or Event Sourcing anywhere in the conversation—even as a casual comparison or a rejected idea—the model frequently interprets it as:

- An implicit architectural preference.
- Existing infrastructure that must be leveraged.
- A baseline constraint for the entire design.

To neutralize contextual anchoring:
- Explicitly state that mentioned technologies are hypothetical examples, not requirements.
- Instruct the model to draft at least one complete design that deliberately excludes every previously mentioned technology.
- Clear context windows or use fresh conversational threads when transitioning from brainstorming to architectural evaluation.
- Require the model to classify technologies as *Required*, *Available*, *Considered*, or *Explicitly Prohibited*.

When evaluating proposals, force the model to separate its assessment into these dimensions:

| Dimension | Critical Question |
| :--- | :--- |
| **Problem Fit** | How cleanly does this architecture satisfy confirmed business invariants and constraints? |
| **Evidence Quality** | What percentage of this proposal is derived from verified codebase facts versus generic patterns? |
| **Implementation Confidence** | How reliably can a coding agent generate and test this implementation without hallucinating? |
| **Ecosystem Familiarity** | Is this option recommended primarily because it is ubiquitous in open-source documentation? |
| **Decision Uncertainty** | What missing metric or operational constraint would instantly change the ranking? |

---

## The Multi-Dimensional Review

Before committing to an architecture, run the design through a comprehensive technical cross-examination. The goal is not to produce administrative paperwork; it is to locate points of structural failure.

Ensure the model reviews the proposal against these operational dimensions:

- **Invariants and State**: Are business status transitions strictly deterministic? What guarantees that illegal state transitions are prevented?
- **Data Ownership and Consistency**: Which component owns the authoritative record? Are we relying on distributed transactions, 2PC, or eventual consistency?
- **Concurrency and Contention**: What happens under high lock contention? Are there hot partitions or table-level locks on critical paths?
- **Idempotency and Retries**: If an upstream service retries an operation four times after a socket timeout, will it create duplicate side effects?
- **Partial Failure and Blast Radius**: If the cache cluster or message bus becomes unreachable, does the system fail gracefully, degrade reads, or suffer complete outage?
- **Deployment and Compatibility**: Can version $N$ and version $N+1$ run concurrently during a 45-minute canary rollout without breaking database schemas or API contracts?
- **Observability and Debuggability**: When a customer transaction fails silently, can an on-call engineer trace the execution path using correlation IDs across process boundaries?
- **Operational Burden**: Does the engineering team possess the tooling, runbooks, and domain knowledge to monitor, tune, and recover this infrastructure at 3:00 AM?

---

## Reviewing with Persona Roles

Prompting an LLM to evaluate an architecture from a single generic perspective often produces balanced, bland feedback. You get substantially sharper analysis by forcing the model to adopt adversarial operational roles:

### The Domain Analyst
Focuses strictly on business logic:
- Extracts core business rules, actors, states, and data ownership.
- Flags edge cases where real-world business workflows violate clean technical abstractions.
- Identifies missing invariants that the technical proposal ignored.

### The Systems Architect
Focuses on structural balance:
- Evaluates system boundaries, decoupling mechanisms, and protocol selections.
- Maps trade-offs between monolithic modularity and distributed services.
- Flags premature abstractions and unnecessary complexity.

### The Skeptic
Assumes the proposed architecture will fail:
- Identifies unstated assumptions and optimistic network assumptions.
- Locates race conditions, retry storms, and hidden failure cascades.
- Pinpoints requirements that would completely invalidate the technical choices.

### The Site Reliability Engineer
Evaluates operational realities:
- Analyzes deployment mechanics, blue-green compatibility, and zero-downtime database migrations.
- Evaluates runbook overhead, telemetry coverage, metrics volume, and alert fatigue.
- Inspects disaster recovery plans, backup restoration paths, and regional failover limits.

### The Security Reviewer
Inspects trust boundaries:
- Evaluates data exposure, authorization enforcement, and credential management.
- Maps attack surfaces, tenant isolation boundaries, and abuse vectors.
- Checks compliance footprints (PCI-DSS, HIPAA, GDPR) introduced by data replication.

### The Migration Reviewer
Focuses on the transition from the old state to the new:
- Evaluates parallel runs, dual-writing risks, data backfills, and cutover strategies.
- Assesses rollback triggers and recovery paths if data corruption is discovered 48 hours post-launch.

---

## Exploration Mode vs. Commitment Mode

LLMs dramatically lower the cost of code generation. Because an agent can spin up a prototype in an afternoon, engineers can fall into a dangerous trap: **mistaking a functional proof-of-concept for a viable production architecture.**

A working prototype does not prove that a design can scale, survive network partitions, handle zero-downtime migrations, or be debugged by on-call engineers.

To manage this, explicitly divide your work into two operational modes:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ EXPLORATION MODE                                                       │
│ Goal: Rapid learning and hypothesis validation                         │
│ • Generate wide solution spaces and test unorthodox stacks             │
│ • Build disposable spikes and run local performance benchmarks         │
│ • Accept explicitly labeled temporary assumptions                      │
│ • Write minimal test harnesses focused only on the hypothesis          │
│ • Optimize for speed of invalidation                                  │
└────────────────────────────────────────────────────────────────────────┘
                                   │
                     [ Formal Decision Gate ]
                     Does the spike prove the
                     operational assumptions?
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ COMMITMENT MODE                                                        │
│ Goal: Production reliability, maintainability, and safety              │
│ • Verify all primary platform documentation and hardware limits        │
│ • Remove all temporary working assumptions                             │
│ • Stress test network partitions, retries, and deadlocks               │
│ • Design zero-downtime migrations and verified rollback paths          │
│ • Formalize the ADR with clear conditional boundaries                  │
└────────────────────────────────────────────────────────────────────────┘
```

The dangerous transition occurs when an exploratory spike built during Exploration Mode is slowly patched and deployed straight into production (see [[How AI Changes Prototyping and the Path from PoC to Production]]). 

Keep your prototypes explicitly disposable. Use them to collect latency, throughput, and error metrics, then design your production system with those concrete numbers in hand.

---

## Designing for Downstream Agent Maintenance

When designing software that will be maintained, extended, or refactored by coding agents, the system architecture itself must be structured to accommodate agent capabilities and context limits (see [[Designing Software for AI Agents]]):

1. **Focused 1:1 Module Boundaries**: Avoid large, sprawling files or "god classes" containing thousands of lines of mixed responsibilities. When an agent must ingest massive files to make a minor change, you waste context window space and increase the risk of hallucinated regressions. Keep domain logic decomposed into cohesive, single-purpose modules.
2. **Explicit Dependency Injection**: Avoid dynamic reflection, ambient global state, or hidden runtime auto-wiring. If an agent cannot trace where a service or repository is injected by inspecting the static Abstract Syntax Tree (AST), it cannot reliably reason about module behavior or write clean unit tests.
3. **Automated Verification Harnesses**: Every architectural boundary requires a fast, deterministic test harness (see [[Testing in the Model, Agent, LLM Era]]). An agent cannot safely refactor an architectural component unless it can execute a local test suite and get unambiguous, sub-second feedback on whether it broke an invariant.

---

## A Six-Phase Collaborative Workflow

To get the most out of an LLM during architectural design, use a phased conversation structure:

```text
Phase 1: Problem Discovery & Boundary Mapping
    │    Instruct the model not to design anything yet.
    │    Extract facts, inferences, assumptions, and unknowns.
    ▼
Phase 2: Constraint Verification
    │    Audit each assumption against real code, schemas, and metrics.
    │    Discard generic defaults that do not match production realities.
    ▼
Phase 3: Divergent Option Generation
    │    Force the model to propose genuinely orthogonal approaches.
    │    Span the simplest, incremental, conservative, and target options.
    ▼
Phase 4: Adversarial Post-Mortem & Red-Teaming
    │    Assume the preferred design failed catastrophically.
    │    Map cascading failure sequences, retry storms, and deadlocks.
    ▼
Phase 5: Conditional Recommendation & Spike Design
    │    Formulate the decision conditionally based on verified metrics.
    │    Design a 24-hour empirical spike to resolve remaining uncertainties.
    ▼
Phase 6: Implementation Specification
         Provide the downstream coding agent with explicit constraints:
         domain invariants, forbidden patterns, and contract tests.
```

---

## Reusable Architectural Prompts

Use these prompts directly in your development workflow.

### 1. Discovery Before Design

```text
Help me analyze this architecture problem, but do NOT propose a solution or select technologies yet.

First, categorize the information from my description into:
1. Confirmed Facts: Points directly verified by my description.
2. Derived Inferences: Logical consequences that follow from the facts.
3. Working Assumptions: Assumptions you must make to proceed, which I did not state.
4. Critical Unknowns: Missing information that prevents a reliable decision.
5. Generic Defaults: Standard industry practices that might be unnecessary or wrong here.

Next, analyze the problem across these architectural dimensions:
- Business invariants and state transitions
- Data ownership and consistency guarantees
- Transactions, concurrency, and locking boundaries
- Idempotency, retries, and network failure modes
- Deployment strategy, schema migrations, and backward compatibility
- Operational overhead, telemetry, and debugging ergonomics

Generate the top 8 critical questions whose answers would materially alter the technical approach, ranked by impact.

Stop here. Do not suggest architectures or technologies until we resolve these questions.
```

### 2. Forcing Divergent Alternatives

```text
Based strictly on our confirmed facts and validated assumptions, generate distinct architectural options across these specific categories:

1. The Simplest Option (minimal moving parts, single-node or monolithic focus)
2. The Existing Infrastructure Option (uses only tools and data stores we already run)
3. The Incremental Evolution (an evolutionary change to our current architecture)
4. The Reversible Experiment (isolated behind interfaces, simple to discard if it fails)
5. The Conservative Option (mature, boring, low-operational-risk technology)
6. The Long-Term Target Architecture (designed for high scale, assuming dedicated staffing)
7. The Process Alternative (resolves the issue by altering business rules or SLAs)

For each option, provide:
- Core trade-off optimized for
- Mandatory conditions required for this to work
- Fatal failure modes (when this is an absolute disaster)
- Operational burden and maintenance footprint
- Migration path and rollback difficulty
- A 24-hour empirical spike or benchmark to prove viability

Do not label any option as universally "best." State the explicit conditions under which each is preferred.
```

### 3. Assumption Extraction Protocol

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

### 4. Adversarial Failure Post-Mortem

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

## Final Mental Model

An LLM does not give you an architecture. It gives you a proposal generated from an incomplete model of your domain.

That internal model contains a mix of:
- Hard facts you provided.
- Inferences derived from those facts.
- Unstated working assumptions.
- Significant gaps in organizational context.
- Generic patterns learned from public codebases.

Your role as an architect is not to debate whether the model's suggested database or messaging queue is fashionable. Your role is to test and validate the model of reality that produced that proposal.

When used properly, LLMs make it remarkably cheap to explore design options, evaluate failure modes, and run fast, disposable spikes. They should dramatically expand your ability to run reversible experiments—without increasing your production risk.

---

## Related Notes

- [[Designing Software for AI Agents]]: Architectural principles that make codebases easy for autonomous agents to navigate, modify, and test.
- [[AI, Averaged Decisions, and Premature Convergence on Solutions]]: Why LLMs naturally default to conventional, averaged designs and how to force divergent thinking.
- [[How AI Changes Prototyping and the Path from PoC to Production]]: Using rapid disposable spikes to test architectural hypotheses before committing to production builds.
- [[Correcting AI Code - Patch, Regenerate, or Respecify]]: Deciding when to fix code locally versus revisiting foundational architectural decisions.
- [[Testing in the Model, Agent, LLM Era]]: Establishing automated, deterministic test harnesses to verify architectural invariants.
