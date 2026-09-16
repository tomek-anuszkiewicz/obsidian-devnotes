---
title: LLMs as a Code Review Team
tags:
  - code-review
  - ai-agents
  - software-engineering
  - multi-agent
  - quality-assurance
  - testing
aliases:
  - Multi-Agent Code Review
  - Continuous Engineering Verification with LLMs
  - Continuous Falsification Engine
  - Specialized Reviewer Topologies
  - Adversarial Review Pipeline
---

# LLMs as a Code Review Team

Most engineering teams approach AI code review with a naive architecture: a single prompt passes an entire pull request diff to a single language model and asks it for an opinion. 

```text
Review this pull request.
```

In practice, this fails immediately. Asking one model instance to simultaneously reason about security boundaries, database query plans, asynchronous cancellation propagation, and domain invariants blows out the context window and dilutes the model's attention. The result is predictable: shallow feedback, pedantic style nits, hallucinated syntax errors, and silence on critical race conditions.

A far more effective architecture treats automated code review as a distributed system of specialized agents coordinated by deterministic verification tools:

```text
Proposed Pull Request Diff
           │
           ▼
   [ Review Router ] ──► Classifies Diff (API, Database, Concurrency, Hot Path)
           │
     ┌─────┴───────────────────────────┬───────────────────────────┐
     ▼                                 ▼                           ▼
[ Security Specialist ]       [ Database Specialist ]     [ Performance Specialist ]
"Forms vulnerability thesis"  "Inspects query plans"      "Generates benchmark"
     │                                 │                           │
     └────────────────────────┬────────┴───────────────────────────┘
                              │
                              ▼
        [ Tool Execution & Hypothesis Verification ]
        (Test Runners / Static Analysis / Profilers / Query Plans)
                              │
                              ▼
            [ Finding Synthesizer & Noise Filter ]
            (Deduplication, confidence gating, test proofs)
                              │
                              ▼
       HUMAN ARCHITECT REVIEWS HIGH-SIGNAL FINDINGS
```

The goal is not to have an AI rubber-stamp code or replace human judgment. The goal is **continuous engineering verification**: deploying a panel of specialized, relentless agents that actively attempt to falsify the pull request before a human engineer ever looks at the diff.

---

## Relentlessness as an Architectural Advantage

The most valuable property of an automated reviewer is not raw intelligence. It is procedural relentlessness.

Human review capacity degrades predictably over time:
- Attention drops off sharply after the fifth pull request of the day.
- A 150-file refactoring diff triggers fatigue, causing reviewers to skim rather than analyze.
- Repetitive mechanical checks (such as verifying that every ASP.NET endpoint propagates a `CancellationToken` or that every multi-tenant query includes an explicit tenant filter) are consistently skipped under delivery pressure.
- Checklists containing forty items inevitably collapse into five remembered rules.
- Edge-case defects that manifest once every few thousand changes are easily dismissed as unlikely.

An automated agent has no cognitive fatigue:

- It runs the exact same validation routine on the hundredth file as it did on the first.
- It executes a 40-point verification checklist on Friday evening with the exact same rigor as Monday morning.
- It never skims a diff because the change appears mechanical or tedious.
- It consistently audits rare failure modes across every single commit.

A senior engineer understands the rules: validate all untrusted inputs, propagate cancellation tokens, maintain backward compatibility on public DTOs, emit structured telemetry, and write regression tests. Knowing those rules is different from consistently executing them across every line of code under real-world sprint deadlines. 

Automating that consistency frees human engineers to focus on architectural trade-offs, system boundaries, and business intent.

---

## Deconstructing the Monolithic Reviewer

Rather than asking a single general-purpose prompt to review an entire pull request, a resilient review pipeline uses a lightweight router to inspect the abstract syntax tree (AST) diff, map the modified components, and dispatch targeted, domain-specific review agents.

```text
                             Pull Request Diff
                                     │
                                     ▼
                           [ Review Router ]
                                     │
         ┌───────────────────┬───────┴───────────┬───────────────────┐
         ▼                   ▼                   ▼                   ▼
[ Correctness Reviewer ] [ Test Reviewer ] [ Security Reviewer ] [ Specialized Reviewers ]
(Always Active)          (Always Active)   (Auth / Tokens / Web) (Conditionally Routed)
                                                                     │
                                                   ┌─────────────────┼─────────────────┐
                                                   ▼                 ▼                 ▼
                                             [ Database ]     [ Performance ]    [ Public API ]
                                             (ORM / SQL / DDL) (Allocations)      (Contracts / DTOs)
```

Not every reviewer needs to run on every commit. The router evaluates file paths, modified symbols, and dependency graphs to trigger specialists conditionally:

```text
DTO / controller / public contract changed
        -> API Compatibility Reviewer

EF / SQL / migration / schema changed
        -> Database Reviewer

authentication / authorization / crypto changed
        -> Security Reviewer

hot-path execution loops / low-level memory allocations
        -> Performance Reviewer
```

Correctness and test reviewers run universally, while expensive reasoning models are reserved for specialized domains. This keeps both token budgets and review latency under tight control.

---

## Specialist Playbooks

Each specialized agent operates under an explicit, narrow domain playbook rather than a generic prompt.

### Database Reviewer
- Evaluates query counts per transaction to catch N+1 query generation.
- Checks execution plans via deterministic `EXPLAIN` queries against realistic table statistics.
- Verifies index coverage for modified `WHERE`, `JOIN`, and `ORDER BY` clauses.
- Audits transaction boundaries, lock escalation risks, and deadlocking vectors.
- Flags excessive client-side in-memory filtering and unbounded table scans.
- Ensures migration scripts contain safe, non-blocking DDL (such as adding nullable columns or creating indexes concurrently).

### API Compatibility Reviewer
- Analyzes contract changes for backward-incompatible schema updates.
- Catches field renames, type mutations, and serialization attribute alterations.
- Audits changes from optional to required parameters in request payloads.
- Validates enum additions against clients that may not handle unmapped values gracefully.
- Verifies standard HTTP status code semantics and idempotency guarantees for `PUT` and `DELETE` routes.
- Enforces explicit contract versioning rules.

### Performance Reviewer
- Traces heap allocations in performance-critical code paths.
- Flags unnecessary boxing, reflection, or LINQ queries executed within hot loops.
- Detects repeated string parsing or redundant deserialization.
- Identifies lock contention, thread-pool starvation, or improper synchronization primitives.
- Monitors database connection utilization and unnecessary over-fetching of data.

### Correctness Reviewer
- Focuses purely on state invariants, edge cases, and control flow.
- Identifies missing boundary condition checks (such as empty collections, zero values, and off-by-one errors).
- Validates nullability contracts and defensive error handling across failure paths.
- Identifies broken assumptions introduced by refactored internal interfaces.

Dividing the review domain into modular playbooks makes the system maintainable. When an agent produces false positives or misses an edge case, you tune a single specialized playbook rather than destabilizing a massive global prompt.

---

## The Hypothesis-Verification Protocol

The fastest way to destroy developer trust is to deploy an AI bot that litters pull requests with speculative, unverified comments like:

> *"This code might be slow."*  
> *"This could potentially cause a concurrency bug."*

Speculative comments force engineers to waste time disproving hallucinations. To prevent this, the review architecture must follow a strict verification protocol: **the LLM generates a failure hypothesis, and deterministic tools verify it before any comment is posted.**

```text
Reviewer Suspects a Bug
           │
           ▼
Formulate Concrete Hypothesis
"The new batch handler creates O(n²) memory allocation when processing large lists."
           │
           ▼
Synthesize Reproducer Test or Benchmark
           │
           ▼
Run Test Against Branch (PR) vs Baseline (main)
           │
  ┌────────┴────────┐
  ▼                 ▼
[ Test Passes ]     [ Test Fails (Bug Confirmed) ]
(Hypothesis false)  (PR allocates 450 KB vs Main 0 KB)
  │                         │
SUPPRESS COMMENT            ▼
                 Post Finding with Reproducer Test as Proof
```

The review pipeline transitions from subjective opinion to verifiable proof:

```text
Hypothesis:
The new implementation introduces O(n²) behavior.

Experiment:
Run a benchmark for 1k, 10k, and 100k elements.

Result:
main:  38 ms
PR:    4.7 s

Conclusion:
Confirmed performance regression.
```

The same protocol applies to correctness and functional regressions:

```text
Reviewer suspects a bug
        |
        v
generate reproduction test
        |
        v
run against main
        |
        v
run against PR
        |
        v
report only if confirmed
```

Language models are strong hypothesis generators, but poor execution engines. Deterministic tools provide the evidence.

---

## Orchestrating the Toolchain

An AI review team does not replace existing continuous integration pipelines; it orchestrates and interprets them. The review agent should have access to the workspace and the authority to invoke standard development tools:

```text
dotnet test / pytest / go test
static analyzers (Roslyn, ESLint, Clippy)
CodeQL
coverage profilers
BenchmarkDotNet / criterion
dotnet-counters / dotnet-trace
SQL EXPLAIN / query plan analyzers
linters
property-based testing frameworks (FsCheck, Hypothesis)
fuzz testing harnesses
```

When an agent identifies a suspicious pattern, it selects the appropriate tool, executes it against the local workspace, parses the standard output, and embeds the concrete execution metrics directly into its finding.

Instead of writing:
> *"This allocation could become expensive."*

It posts an evidence-backed finding:

```text
Severity: HIGH | Confidence: HIGH | Category: Performance Regression
Target: OrderProcessingPipeline::ExecuteBatch

Hypothesis Confirmed:
The new stream pipeline allocates an intermediate buffer on every transaction.

Empirical Proof:
- Baseline (main): 1.8 µs per transaction | 0 heap allocations
- Pull Request:   4.2 µs per transaction | 480 bytes heap allocated per transaction
- Production Impact: At 5 million calls/day, this introduces ~2.4 GB of unnecessary garbage collection churn.

Reproduction Benchmark: tests/benchmarks/batch_processing_benchmark
Suggested Fix: Reuse a pre-allocated buffer slice instead of allocating a new array per transaction.
```

This transforms code review from a debate over personal coding styles into an objective discussion grounded in verifiable data.

---

## Generating Reproduction Tests During Review

A mature reviewer agent should have permission to create temporary unit, integration, or property tests to validate its failure hypotheses.

```text
Potential bug detected
        |
create regression test
        |
test passes on main
        |
test fails on PR
        |
finding confirmed
```

If an agent suspects that refactoring an order calculation routine will break handling for negative balances, it writes a test asserting the expected behavior:

1. It checks out the baseline branch (`main`) and runs the synthesized test. The test passes, confirming the baseline behavior.
2. It checks out the pull request branch and executes the test. The test fails with an unexpected exception or incorrect calculation.
3. The agent formats the failure, includes the synthesized test in the review comment, and suggests the necessary fix.

The reproducer test can then be committed directly to the test suite by the author, permanently preventing the regression.

---

## Separation of Concerns: Reviewer vs. Fixer

It is an anti-pattern to let the same agent find a bug and immediately patch the source code. When an agent both analyzes and modifies:

- It tends to rationalize its own misunderstandings.
- If it hallucinates a bug, it will write a patch that adds unnecessary complexity to solve an imaginary problem.
- It is prone to modifying assertions in the test suite to make its broken patch pass.

To preserve integrity, maintain a strict separation of concerns:

```text
┌────────────────────────────────────────────────────────┐
│ Reviewer Agent (Read-Only)                             │
│ • Reads code diffs, specs, and commit history          │
│ • Generates failing reproducer tests                   │
│ • Forbidden from editing source files                  │
└───────────────────────────┬────────────────────────────┘
                            │ Emits verified bug + failing test
                            ▼
┌────────────────────────────────────────────────────────┐
│ Fixer Agent (Write-Only)                               │
│ • Receives failing test and defect description         │
│ • Edits implementation files to make test pass         │
│ • Forbidden from modifying test assertions             │
└───────────────────────────┬────────────────────────────┘
                            │ Proposes patch
                            ▼
┌────────────────────────────────────────────────────────┐
│ Verification Harness                                   │
│ • Runs full regression test suite                      │
│ • Confirms patch passes without regressions            │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
               Human Approves or Rejects Patch
```

The reviewer can read, run tests, and execute benchmarks, but has no write access to production code. The fixer receives the failing reproducer test and the defect description, working exclusively to make the test pass without altering test assertions. 

This guarantees that fixes are verified objectively against independent criteria.

---

## Model Diversity and Context Isolation

Code review benefits from architectural independence. The model reviewing a pull request should not share context or biases with the model that generated the code.

```text
Model A generates code.

Model B reviews correctness.

Model C reviews security.

Model D tries to find counterexamples.
```

Different model families have distinct reasoning tendencies and failure modes. A model that excels at rapid code synthesis might struggle with subtle edge cases in asynchronous state machines. Introducing a different model to review the implementation brings fresh perspectives to the review.

Even when using the same underlying foundation model, you should run review agents in isolated, stateless context windows. When an agent reviews code without seeing the generation prompt or the author's internal reasoning chain, it evaluates the pull request on its merits, without being anchored to the author's assumptions.

---

## Routing to Manage Token Economics

Running full multi-agent review sweeps across every single commit is slow and cost-prohibitive. A lightweight classifier must sit in front of the specialist panel:

```text
Change classification:

documentation only
    -> suppress all technical reviewers

test-only change
    -> correctness + test reviewer

database migration
    -> correctness + database + compatibility reviewers

authentication change
    -> correctness + security + test reviewers

hot-path implementation
    -> correctness + performance + test reviewers
```

The router uses a small, fast model or deterministic file-matching heuristics to analyze the diff metadata. Heavy reasoning models and sandboxed environments are reserved for changes that modify core execution paths, schema boundaries, or security perimeters.

---

## Synthesizing Findings and Filtering Noise

Deploying seven specialized reviewers creates a severe coordination challenge: comment noise. If seven agents post thirty independent comments across a pull request, developers will quickly mute notifications and ignore the output.

A **Synthesizer Agent** must intercept all specialist findings before they reach the pull request, acting as a quality filter:

```text
7 reviewers
     │
     ▼
24 candidate findings
     │
     ▼
[ Synthesizer Pipeline ]
  ├── Deduplicate overlapping comments
  ├── Suppress unverified or disproved hypotheses
  └── Apply confidence and severity gating
     │
     ▼
6 high-signal findings presented to the developer
```

The synthesizer consolidates findings into a standardized, structured format:

```text
Severity: HIGH
Confidence: HIGH

Problem:
Missing database index on newly added foreign key in high-volume query.

Evidence:
SQL EXPLAIN indicates full sequential scan across 12 million rows on `Orders.CustomerId`.

Impact:
Endpoint latency estimated to degrade from 12ms to 1,400ms under standard peak load.

Suggested fix:
Add `CREATE INDEX CONCURRENTLY idx_orders_customer_id ON Orders(CustomerId);` to migration script.

Reviewer:
database-performance
```

---

## Confidence Gating

To maintain developer trust, the synthesizer must apply a clear notification policy based on finding severity and confidence:

```text
HIGH severity + HIGH confidence
    -> Inline comment / request changes (blocking)

MEDIUM severity + HIGH confidence
    -> Normal inline comment

LOW confidence / Unverified hypothesis
    -> PR review summary checklist only (non-blocking)

LOW severity + LOW confidence
    -> Suppress entirely (log to telemetry for tuning)
```

False positives erode engineering trust faster than missed edge cases. If an agent cannot generate deterministic proof for a hypothesis, that observation must either be suppressed or placed in an informational summary. It should never block the developer.

---

## The Closed-Loop Feedback Engine

Every interaction between a developer and an automated reviewer produces telemetry that can refine the system. The platform should record explicit developer actions:

```text
accepted
rejected
false positive
already known
fixed
ignored
disputed
```

Over time, this data reveals systematic blind spots and noise patterns in specialist playbooks. For example, if engineers repeatedly reject performance warnings regarding heap allocations in an administrative initialization routine, the performance playbook should be tuned accordingly:

```text
Do not report allocation differences unless:
- The execution path is demonstrably hot (e.g., inside request middleware, core loops, or stream pipelines).
- The allocation delta exceeds 64 bytes per operation.
- The allocation introduces measurable GC churn under production-scale loads.
```

The review system becomes an evolving platform that adapts to the team's operational tolerances.

---

## Measuring Review Quality

Automated review pipelines should be measured with the same rigor as any production software service. Key operational metrics include:

```text
findings generated
findings accepted
findings rejected
false-positive rate
confirmed bugs found
security vulnerabilities intercepted
regressions caught
reproducer tests generated
hypotheses confirmed by tools
review latency (time to feedback)
token cost per pull request
```

This tracking shifts the team's focus from subjective prompt engineering to objective system performance:

```text
Security Reviewer Metric Summary:
- 1,240 pull requests reviewed
- 87 findings emitted
- 72 accepted by authors
- 9 rejected as invalid / false positive
- 6 marked inconclusive

Precision: 82.7%
Hypothesis verification rate: 94.2%
```

If precision drops below 80%, the specialist's playbook and confidence thresholds must be tightened.

---

## GitHub Integration Architecture

GitHub provides the event-driven foundation required to host a multi-agent review architecture. A review system can listen to standard lifecycle webhooks:

```text
pull_request.opened
pull_request.synchronize
pull_request_review_comment.created
check_run.rerequested
```

Depending on security constraints and execution requirements, there are two primary integration patterns.

### 1. GitHub Actions (Sandboxed Local Execution)

The simplest architecture runs the entire review pipeline inside GitHub Actions:

```text
Pull Request Event
        │
        ▼
 GitHub Actions Runner
        │
        ├── Checkout repository
        ├── Build solution and binaries
        ├── Execute Review Router
        ├── Run Specialist Agents in parallel
        ├── Execute tests, benchmarks, and static analyzers
        ├── Run Synthesizer Agent
        └── Post findings via GitHub API
```

This approach allows the agent to execute code, run benchmarks, and run test suites directly inside the project's native build container. It provides a natural sandbox for verifying hypotheses without exposing internal build systems to external networks.

### 2. GitHub Apps (External Microservices)

For enterprise installations requiring shared caching, centralized orchestration, and dedicated GPU infrastructure, a GitHub App integration is preferable:

```text
GitHub
   │
   ▼ (Webhook Event)
Company Review Platform / External Review Service
   │
   ├── Fetch PR diff & AST metadata via API
   ├── Execute routing and LLM reasoning steps
   ├── Trigger isolated sandboxes for tool verification
   │
   ▼ (GitHub REST / GraphQL API)
Pull Request: Status Checks / Review Comments / PR Summaries
```

The GitHub App acts as an external reviewer, using the GitHub API to post inline comments, generate PR review summaries, and create formal status checks.

---

## On-Demand Agent Invocation

Not all review workflows need to run automatically on every push. Developers can invoke specialist investigations explicitly through pull request comments:

```text
@review-bot performance
```

or:

```text
/review security --depth deep
```

or:

```text
@review-bot verify whether this LINQ query executes client-side evaluation
```

This creates an interactive debugging workflow where the developer uses the agent to run targeted investigations on complex, ambiguous changes before requesting human review.

---

## Structured Checks Over Comment Floods

Inline comments are disruptive and easily derail review threads. Status checks provide a cleaner alternative for automated analysis:

```text
Build                             PASS
Automated Test Suite              PASS
Security Review                   PASS
API Compatibility                 PASS
Performance Review                FAIL
Database Optimization             PASS
```

Detailed failure reports, benchmark graphs, and reproduction scripts can live inside the status check details view rather than polluting the conversation timeline. Merging can then be gated on critical, high-precision automated checks without cluttering the pull request with automated notifications.

---

## An Ecosystem of Independent Reviewers

A mature repository rarely relies on a single AI provider. Instead, it coordinates an ecosystem of independent, decoupled review services:

```text
GitHub Copilot (Syntax and authoring assistance)
Internal Architecture Agent (ADR and organizational pattern enforcement)
Specialized Security Vendor (Taint analysis and dependency scanning)
Performance Agent (Micro-benchmarking and allocation tracking)
CodeQL / SonarQube (Deterministic static analysis)
Business Logic Reviewer (Domain model verification)
```

GitHub operates as an event bus and shared collaboration plane where deterministic linters, commercial scanners, and custom LLM agents collaborate on the same change.

---

## Integrating Organizational Context

Generic SaaS review tools lack visibility into internal architectural decisions, legacy migrations, and production topology. An internal company review platform can leverage private engineering context:

```text
GitHub Pull Request Event
           │
           ▼
Company Review Platform
           │
           ├── LLM Specialist Orchestration
           ├── Internal Architecture Decision Records (ADRs)
           ├── Production Incident Post-Mortems
           ├── OpenTelemetry / Grafana Metric Baselines
           ├── Database Schema Statistics (Catalog row counts)
           └── Jira / Linear Feature Specifications
```

Access to internal context allows an agent to catch failures that look completely benign in isolation:

> *"This endpoint is functional, but Service X is scheduled for deprecation in Q3. New endpoints must consume Service Y via the internal event bus."*

or:

> *"This query performs an unindexed scan on the `AuditEvents` table. In production, this table contains 900 million rows. This query will time out and trigger lock escalation."*

---

## Sandboxing and Principle of Least Privilege

Review agents should run under strict permission boundaries. An agent tasked with analyzing code does not need permission to push commits to production branches:

```text
Repository Contents: Read-Only
Pull Requests:       Read / Write (Comments and Reviews)
Checks:              Read / Write (Status reporting)
Actions:             Read-Only
Administration:      Explicit Deny
Secrets:             Explicit Deny
```

An agent with read-only access to source code and write access only to review comments reduces the security blast radius. If an agent is manipulated via prompt injection embedded in untrusted external code, it cannot exfiltrate repository secrets, alter pipeline configurations, or force-push malicious commits to protected branches. 

Any code modification must be handled by an independent fixer agent with separate, sandboxed permissions and mandatory human approval.

---

## The Evolving Role of the Human Engineer

Automated review changes *what* humans spend their time analyzing. 

Today, human reviewers burn substantial energy checking for mechanical issues:

```text
Did the author handle null reference scenarios?
Is the cancellation token passed down the call chain?
Is this endpoint covered by integration tests?
Will this change break existing mobile API clients?
Did this migration introduce an unindexed foreign key?
```

These checks are critical, but they are procedural. When automated agents run these checks reliably, human engineers can focus their attention on broader architectural concerns:

- Does this business logic reflect the real-world domain problem accurately?
- Does this abstraction support the system's anticipated growth over the next two years?
- Are the performance and operational trade-offs acceptable for our infrastructure budget?
- Does this feature violate any cross-team organizational boundaries?
- Should this feature be built this way at all?

The review process becomes layered:

```text
Machines verify everything that can be systematically proven.

Humans evaluate what requires architectural judgment and business context.
```

---

## Continuous Engineering Verification

Moving to an agentic review architecture is a fundamental shift in how teams validate software before deployment:

```text
Traditional Manual Review:
Developer writes code -> Human reads diff -> Human spots a few bugs -> Merge

Continuous Engineering Verification:
Developer or agent writes code
        │
        ▼
Parallel specialist agents inspect diff
        │
        ▼
Agents formulate failure hypotheses
        │
        ▼
Deterministic tools, tests, and benchmarks verify hypotheses
        │
        ▼
Findings are filtered, deduplicated, and confidence-gated
        │
        ▼
Fixer agent synthesizes patches; tests verify the fixes
        │
        ▼
Human reviews high-signal findings, system architecture, and domain intent
```

The goal of code review is no longer to have an engineer casually read through code before merging. The goal is to **actively attempt to falsify the change before it reaches production**.

Automated agents are not infallible. But they are **relentless, specialized, cheap to run in parallel, capable of executing real tools to verify their ideas, and consistent across every change**. In code review, those operational properties are often what keeps defects out of production.

---

## Related Notes

- [[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]]
- [[Reviewing AI-Generated Code]]
- [[Agent Advantage - Relentless, Methodical Work]]
- [[Testing in the Model, Agent, LLM Era]]
- [[Multi-Agent Software Development]]
- [[Agentic Coding Harness and Controlled Development Workflows]]
- [[Software Decay and the Hidden Costs of Frictionless AI Code]]
