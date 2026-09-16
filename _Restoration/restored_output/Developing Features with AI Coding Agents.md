---
title: Developing Features with AI Coding Agents
tags:
  - ai-agents
  - software-engineering
  - agentic-workflows
  - feature-development
  - testing
  - code-review
aliases:
  - Feature Development with Agents
  - End-to-End Agentic Feature Lifecycle
---

## A Battle-Tested Workflow for Larger Features

When you hand an autonomous agent a loose prompt for a complex feature—like "add multi-tenant billing with tiered seat pricing"—disaster usually follows. The model writes dozens of sprawling files, invents its own business logic, mocks out critical network boundaries, and writes green tests that pass purely because they assert against its own flawed assumptions.

To ship reliable, production-ready code with coding agents, you need a disciplined, phased pipeline that treats the model as an implementer rather than an unsupervised architect:

```text
repository analysis
→ behavioral specification
→ examples and decision tables
→ acceptance tests
→ human review
→ implementation of one vertical slice
→ architectural review
→ full implementation
→ independent skeptical review
→ documentation update
```

---

### Step 1: Repository Analysis

The first command you give the agent must enforce a strict read-only boundary. Do not let it create or modify a single line of code yet. 

Its job is to inspect the codebase and map the existing operational reality:

* **Business flows:** Trace the exact call paths, controller actions, domain events, and background workers that will interact with the new capability.
* **Data models and storage:** Inspect existing database schemas, migrations, indices, foreign key constraints, and entity relationships. Note whether tables are partitioned or if certain fields rely on implicit database defaults.
* **Integration points:** Identify external API clients, message queues, webhook handlers, and third-party dependencies. Check how retries and idempotency keys are handled.
* **Transaction boundaries:** Look at where database transactions start and end. Are they handled at the service layer, inside repository methods, or managed via unit-of-work patterns?
* **Existing test infrastructure:** Note how current tests run. Are they isolated unit tests, container-backed integration tests (e.g., Testcontainers), or heavily mocked end-to-end suites?
* **Compatibility risks:** Pinpoint where schema changes could break older running instances during a rolling deploy, or where changes to serialized queue payloads could poison active consumers.
* **Hidden assumptions and tribal knowledge:** Surface monkey-patches, hard-coded environment toggles, custom error-handling middleware, and unwritten domain invariants embedded in legacy helper utilities.

The goal here is a grounded discovery report. If the model cannot accurately describe how the system works today, it cannot safely modify it for tomorrow.

---

### Step 2: Behavioral Specification

Once the system context is established, write a strict behavioral specification. You can have the agent draft this, but you must curate and approve it. 

This document must define the boundary conditions in plain, unambiguous domain terms:

* **Business objective:** The root problem being solved and the exact value delivered, stripped of technical implementation details.
* **Terminology:** An explicit glossary. If the codebase uses "Account," "Workspace," and "Tenant," define what each word means so the agent doesn't conflate identity boundaries.
* **Core rules:** Explicit state machine transitions, validation invariants, authorization checks, and calculation formulas.
* **Exceptions and failures:** Exactly how the system responds when things go wrong—network timeouts, validation failures, concurrency conflicts, and rate limits.
* **Negative cases:** What the system *must reject*. For example: "A user cannot downgrade a plan if their current seat usage exceeds the target plan's limit."
* **Side effects:** Background jobs enqueued, cache keys invalidated, domain events published to message brokers, and audit logs recorded.
* **Compatibility constraints:** Wire formats, database backward-compatibility, and API versioning rules that must remain intact.
* **Non-functional constraints:** Hard limits on memory usage, database query counts (preventing N+1 queries), connection pool starvation, and P99 latency budgets.
* **Explicit out-of-scope boundaries:** A firm list of features the agent must *not* attempt to build. Without this, models tend to over-engineer speculative abstractions and secondary workflows.

---

### Step 3: Tests Before Implementation

With the specification locked, have the agent write the tests before writing any production implementation.

These tests serve as executable guardrails across multiple layers:

* **Business-rule tests:** Pure, IO-free tests that exercise domain models, calculation engines, and state machines with comprehensive edge-case coverage.
* **Acceptance tests:** High-level scenarios that exercise full use cases against the public API or service boundary, asserting on observable business outcomes.
* **Regression tests:** Targeted tests ensuring that adjacent features, shared utilities, and existing database queries remain entirely unaffected.
* **API contract tests:** Strict validation of HTTP status codes, JSON schema payloads, error response structures, and header behaviors.
* **Integration tests:** Scenarios that touch real backing services (e.g., PostgreSQL or Redis instances in Docker) to validate transactions, constraint violations, and query mechanics.

**The Golden Rule:** These new tests must fail when run against the current codebase. A test that passes before the implementation exists is either a tautology, testing the wrong code path, or asserting nothing of value. The failure confirms the test can detect the absence of the required behavior.

---

### Step 4: Human Review of Meaning

Do not skim this step just to verify that the test code looks clean, idiomatic, or passes linting. You are conducting a semantic audit of the test suite.

Inspect the suite through these critical questions:

* **Does the test reflect true business requirements?** Ensure the assertions match the behavioral specification, not a shallow mechanical echo of input to output.
* **Did the agent invent an unstated rule?** Models frequently introduce plausible-sounding assumptions (e.g., auto-refunding money on a canceled subscription or silently swallowing errors with default fallbacks) that contradict actual domain policy.
* **Are negative paths genuinely validated?** Check that failure assertions test the specific domain error, rather than just asserting that *any* exception was thrown (which might be an unexpected `NullPointerException`).
* **Are rule priorities and conflicts resolved correctly?** If two business rules collide (e.g., an enterprise discount code applied alongside an automated seasonal promotion), does the test assert the correct priority order?
* **Is the test decoupled from implementation details?** Tests that assert on internal private methods or rely on extensive, brittle mocking will shatter the moment you refactor the underlying classes. Assert on behavior, inputs, and outputs.
* **Does the test accidentally preserve legacy bugs?** If an existing endpoint returns an incorrect status code or malformed payload, make sure the new test doesn't codify that accidental behavior as a permanent requirement.

---

### Step 5: Freeze the Acceptance Contract

Once you approve the acceptance test suite, freeze it. 

The agent responsible for implementing the production code must not have permission to modify these approved acceptance tests. If the model is allowed to edit both the implementation and the tests simultaneously, it will inevitably mutate assertions to make a failing test pass whenever it struggles with an edge case.

The implementing agent is free to create internal, lower-level unit tests for technical plumbing (such as parser utilities or helper functions). However, modifying any part of the agreed acceptance contract requires human intervention and explicit re-review.

---

### Step 6: Implement a Small Vertical Slice

Resist the urge to let the agent generate the entire feature across all layers at once. Asking an agent to build twenty database models, ten repositories, ten services, and five controllers in one shot leads to fragmented code that rarely links together properly.

Instead, instruct it to implement a single, narrow vertical slice:

```text
HTTP Controller / Entry Point
  → Route Validation
    → Domain Service
      → Data Repository / Query
        → Database Transaction / Persistence
```

Pick one critical happy-path operation. Wire it from the external entry point down to disk storage and back out. 

Building a vertical slice validates your architectural decisions immediately:
* Are the dependency injection setups working?
* Do the database transactions roll back cleanly on errors?
* Is context passing correctly through the service layers?
* Are the chosen abstractions clean and ergonomic to build upon?

You catch structural flaws when only three files exist, rather than after twenty files have been committed.

---

### Step 7: Architectural Review

Stop and evaluate the vertical slice before scaling out. 

Examine the integration points:
* Did the agent introduce unnecessary architectural layers, leaky abstractions, or redundant DTO conversions?
* Are database queries efficient, or are we setting ourselves up for memory bloat and connection starvation?
* Is error propagation consistent, or did the agent wrap domain errors in generic runtime exceptions?

Fix the architectural patterns here. This code now acts as the canonical few-shot pattern the agent will reference when implementing the rest of the feature.

---

### Step 8: Full Implementation

With the pattern proven and locked, authorize the agent to fan out and implement the remaining paths: secondary use cases, edge cases, error conditions, and negative branches.

Because the acceptance tests are frozen, the agent can iterate autonomously in a tight loop: write code, run the acceptance suite, inspect failures, and refine the implementation until every test turns green.

---

### Step 9: Independent Skeptical Review

Never rely solely on the implementing agent to review its own work. Pass the resulting Git diff to an independent review process—either a senior engineer or a freshly prompted model configured with an adversarial, critical persona.

The reviewer should scrutinize the diff specifically for:
* Race conditions and lack of row-level locking or optimistic concurrency controls on shared mutable state.
* Resource leaks: unclosed database handles, missing transaction rollbacks, or dangling goroutines/threads.
* Subtly broken edge cases that bypass the test suite.
* Security vulnerabilities: missed authorization checks, improper tenant scoping in database queries, or unvalidated user input.

---

### Step 10: Documentation Update

Code is not complete until the surrounding operational context reflects the changes:

* Update OpenAPI/Swagger definitions.
* Record Architectural Decision Records (ADRs) explaining *why* specific trade-offs were made.
* Update schema migration logs and operational runbooks for deployment and rollback procedures.
* Ensure domain glossaries reflect any newly introduced concepts.

---

## Tests Are Executable Specifications, but Not Complete Specifications

A common trap in agentic workflows is treating test suites as the sole source of truth. Tests are concrete examples of expected behavior, but they are not complete specifications.

A passing test suite demonstrates that specific inputs yield specific outputs under predefined conditions. It does not explain:
* **The "why":** The business rationale or regulatory requirements driving the logic.
* **Domain definitions:** What terms actually signify to human operators in the real world.
* **Protected constraints:** Which code paths look redundant or inefficient to an optimizer, but exist to prevent subtle edge cases or third-party API quirks.
* **Differentiating nuances:** Why two seemingly identical workflows must be handled with slight variations in transaction isolation or event emission.
* **Historical necessity:** Which behaviors are legacy technical debt that must be preserved for backward compatibility versus which can be safely cleaned up.

The most resilient engineering approach combines all four pillars:

```text
business decision
+ examples or decision table
+ acceptance tests
+ explicit implementation
```

### The Peril of Self-Grading Agents

If you allow a model to define both the implementation and the criteria for correctness, it operates inside an unvalidated loop. 

An agent that misunderstands a requirement will write a flawed implementation, write a tautological test asserting that flawed behavior, run the test, watch it pass, and report that the task is complete. Without an independent human verifying the semantic meaning of the tests, the suite merely automates the confirmation of its own hallucinations.

---

## Practical Working Rules

Keep these operational rules front and center when driving feature work with autonomous agents:

* **Analyze before modifying:** Never generate implementation code in the same step as repository discovery. Force a read-only analysis phase.
* **Write and approve the behavioral specification first:** Do not write code or tests until the domain boundaries, edge cases, and terminology are explicitly defined and reviewed.
* **Use examples and decision tables:** When business rules have combinatorial inputs (e.g., combinations of user roles, subscription states, and feature flags), map them out in truth tables. Agents parse tabular logic far more reliably than prose.
* **Review acceptance tests before writing production code:** Ensure test assertions validate business intent rather than implementation details or accidental behavior.
* **Freeze approved business tests:** Keep the acceptance suite locked so the implementing agent cannot alter the grading rubric to match its code.
* **Implement one vertical slice first:** Prove the architecture from the controller down to the database row on a single use case before fanning out to the full feature set.
* **Separate mechanical changes from business changes:** Run refactorings, dependency updates, and lint fixes in isolated commits completely separate from behavioral feature code.
* **Require a skeptical second review:** Treat agent-generated code with the same scrutiny you would apply to code submitted by an over-confident junior engineer: verify invariants, check the edge cases, and run adversarial tests before merging to main.
