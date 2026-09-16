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
  - Vertical Slice Implementation Gate
  - Agent TDD Protocol
  - The Specification-First Feature Loop
---

When you hand an AI coding agent an underspecified prompt—such as *"add a subscription billing module with Stripe integration"*—the failure pattern is predictable. The agent writes twenty files at once, invents unstated domain assumptions, overlooks critical edge cases, and writes unit tests that pass only because they assert against mock-heavy trivialities.

Building complex, production-grade features with coding agents requires treating the agent as a fast implementation engine constrained by explicit architectural boundaries. The process must follow a structured pipeline:

```text
Repository Analysis
  │
  ▼
Behavioral Specification & Decision Tables
  │
  ▼
Acceptance Tests (Red State)
  │
  ▼
[ Human Review of Intent ] ──► Freeze Acceptance Contract
                                       │
                                       ▼
                             Thin Vertical Slice
                                       │
                                       ▼
                             Architectural Review
                                       │
                                       ▼
                             Horizontal Expansion
                                       │
                                       ▼
                             Skeptical Second Review
                                       │
                                       ▼
                             Documentation Update
```

By forcing the agent to analyze before modifying files, establish test contracts before writing business logic, and validate system topology with an end-to-end vertical slice, you prevent sprawling diffs and maintain total control over your architecture.

---

## 1. Repository Analysis (Read-Only Reconnaissance)

Before an agent touches a single file, it must map the operational boundaries of the existing codebase. When agents fail at feature development, it is rarely due to syntax errors; it is because they missed an existing transaction boundary, duplicated an existing utility, or ignored a subtle schema constraint.

In this initial phase, restrict the agent to read-only tools and instruct it to identify:

*   **Existing Business Flows:** How data moves through similar domain paths.
*   **Data Models & Schema Constraints:** Foreign keys, indexes, nullability, unique constraints, and enum types.
*   **Integration Points:** External APIs, message brokers, caching layers, and internal service clients.
*   **Transaction Boundaries:** Where transactions begin and end, how database locks are acquired, and how rollbacks are handled.
*   **Testing Conventions:** Framework patterns, fixture setups, and mocking conventions already established in the repo.
*   **Compatibility Risks & Hidden Assumptions:** Shared state, concurrent worker assumptions, or legacy behavior that must not be broken.

The output of this phase is not code—it is an architectural inventory and a list of structural constraints.

---

## 2. Behavioral Specifications, Decision Tables, and State Graphs

Free-form natural language is a terrible medium for complex business logic. Large language models struggle with sprawling narrative prose because unstructured text leaves implicit branches, which models often resolve by hallucinating requirements.

Specifications work best when defined through explicit business rules, bounded contexts, and **Decision Tables or State-Machine Transition Graphs**. These representations give the model clear, deterministic mappings to follow.

The specification must capture:
*   Core business objective and explicit domain terminology.
*   Happy-path rules and expected side effects.
*   Explicit negative cases, validation failures, and edge conditions.
*   Non-functional constraints (latency budgets, concurrency, security).
*   **Explicit out-of-scope boundaries** (what the agent must *not* build).

### Decision Tables and State-Machine Transitions

Instead of writing three paragraphs explaining billing state changes, provide a concrete transition matrix:

| Current State | Event / Input | Condition / Guard | Expected Result | Side Effects |
| :--- | :--- | :--- | :--- | :--- |
| `Active` | Cancel Requested | Within Grace Period | Status: `CancelPending` | Emit `CancellationScheduled` email |
| `Active` | Cancel Requested | Outside Grace Period | Status: `Active` (Error) | Emit `ErrorNotification` |
| `Active` | Payment Fails | Retry Attempt < 3 | Status: `Active` | Schedule retry job in 24h |
| `Active` | Payment Fails | Retry Attempt >= 3 | Status: `Suspended` | Emit `SubscriptionSuspended` event |
| `Suspended` | Payment Succeeds | — | Status: `Active` | Emit `ReactivatedEvent`, clear retries |

Why this approach works:

1.  **Combinatorial Explicitness:** Every row is an isolated, testable tuple: `(CurrentState, Event, Guard) -> (NextState, SideEffect)`. The agent has no room to invent unsanctioned state transitions.
2.  **Deterministic Test Synthesis:** An agent can translate a 10-row decision table into 10 parametrized acceptance tests without omitting edge cases.
3.  **Rapid Human Audit:** An engineer can scan this table in two minutes and spot missing paths immediately—for example, asking: *"What happens if a user updates their payment method while the account is suspended?"*

---

## 3. Acceptance Tests Before Implementation

With the specification and decision tables set, have the agent author acceptance tests *before* writing any application code.

These tests should target the boundaries:
*   **Business-Rule Tests:** Parametrized domain unit tests derived straight from the decision table.
*   **API Contract Tests:** Request payload schema validation, correct response structures, and HTTP status codes.
*   **Integration Tests:** Real database transactions, migrations, and event emissions.
*   **Negative Path & Edge Tests:** Upstream timeouts, unique constraint violations, and invalid input payloads.

At this stage, **these tests must fail**. If a test passes before implementation code is written, it is either asserting an existing behavior, testing a mock, or asserting nothing meaningful. A failing test proves that the suite can accurately detect the missing feature.

---

## 4. Human Review of Meaning

Before the agent writes any implementation code, an engineer must review the test suite. This review is not a linting pass—it is a business and architectural sanity check.

Evaluate the suite against these key questions:

*   **Does the test reflect the real business need?** Or did the agent interpret the prompt literally while missing the operational context?
*   **Did the agent invent unstated domain rules?** Look out for arbitrary defaults, invented validation limits, or unrequested database fields.
*   **Are negative cases actually covered?** Ensure the tests check what happens when things break, not just the happy path.
*   **Is rule priority correct?** When two conditions collide, does the test verify which one takes precedence?
*   **Is the test unnecessarily coupled to an implementation detail?** Look for tests asserting that an internal private method was called instead of asserting the observable side effect on the system boundary.
*   **Does the test preserve accidental legacy behavior?** If a bug in the old code is being codified as expected behavior, catch it here.

---

## 5. Freezing the Acceptance Contract

Once the human engineer approves the acceptance tests, the acceptance contract is frozen.

The implementing agent must **never** be permitted to modify approved acceptance tests to match its implementation. If an agent struggles to get a test passing, its default failure mode is often to weaken the test's assertions, skip edge cases, or replace real database checks with mocks.

By treating approved acceptance tests as read-only, you enforce a strict boundary: the code must satisfy the specification. The agent is free to add internal, low-level technical unit tests as it implements the code, but any changes to the frozen acceptance tests require explicit human review and re-approval.

---

## 6. Implement a Thin Vertical Slice

Do not let an agent generate five controllers, eight data transfer objects (DTOs), three service layers, and database migrations in a single pass. Massive, horizontal changes generate wide PRs that are difficult to review and often hide flawed abstractions.

Instead, have the agent build a single, end-to-end **Vertical Slice**:

```text
[HTTP Request / Controller Entry]
              │
              ▼
  [Application Service / Handler]
              │
              ▼
     [Domain Model Transition]
              │
              ▼
[Database Persistence / Transaction Commit]
```

Build just enough code to make one row of the decision table pass:
1. One API route or event listener.
2. One application command handler or service method.
3. One domain model state transition.
4. One database query or physical write.
5. Verify that this single path compiles, runs, and turns its corresponding acceptance test green.

### Architectural Review of the Slice

Stop and inspect the vertical slice. This is the cheapest moment to fix your abstractions:
*   Does the domain boundary feel clean, or is the service handler bloated?
*   Are transactions and database connections scoped properly?
*   Is error handling and logging consistent with the rest of the codebase?
*   Did the agent import an unnecessary third-party library instead of using existing utilities?

Refactoring one thin vertical slice takes minutes. Restructuring twenty generated files takes hours.

---

## 7. Horizontal Expansion

Once the vertical slice validates the architecture, direct the agent to implement the remaining functionality:

*   Build out the remaining endpoints, consumers, and CLI commands.
*   Flesh out the remaining rows of the decision tables and edge-case handlers.
*   Implement explicit logging, monitoring hooks, and metrics emission.
*   Verify that the entire suite of frozen acceptance tests passes cleanly.

Because the underlying patterns, schemas, and service boundaries were locked in during the vertical slice, horizontal expansion is largely mechanical and predictable.

---

## 8. Independent Skeptical Review

Before opening a pull request or merging code, run an independent review pass. Using a clean context window or a separate agent prompt helps avoid the confirmation bias of the session that generated the code.

Use a prompt focused on risk:

> *"Audit this git diff. Focus exclusively on concrete architectural bugs: race conditions, transaction boundary leaks, missing database indexes, unhandled exceptions in async workers, and injection vulnerabilities. Do not comment on style or formatting. Flag only clear failure modes."*

This pass catches concurrency bugs, unbounded queries, and forgotten idempotency keys before human engineers spend time reviewing the pull request.

---

## Tests Are Executable Specifications, Not Complete Specifications

A test is an executable example of an expected behavior. However, it rarely provides complete architectural context:

*   It does not explain **why** the rule exists or the business risk it mitigates.
*   It does not clarify the subtleties of domain terminology.
*   It does not indicate which parts of an implementation are critical business invariants versus incidental choices.
*   It cannot explain why two seemingly identical flows must be handled differently for historical reasons.

The strongest development workflows blend multiple layers:

```text
  Business Intent & Context (Written Specification)
+ Deterministic Boundary Logic (Decision Tables)
+ Executable Verification (Acceptance Tests)
+ Explicit Code Architecture (Vertical Slice Implementation)
```

Never allow an agent to define both the implementation and the criteria for correctness without an independent human check. An agent that writes both the implementation and the tests in an unconstrained environment will inevitably write tests that pass simply by agreeing with its own buggy assumptions.

---

## Practical Rules for Teams

*   **Analyze before editing:** Zero code changes on turn one. Force the agent to map existing schemas, utilities, and transactional patterns first.
*   **Write or approve the behavioral specification:** Clarify state changes, edge cases, and non-goals up front using decision tables.
*   **Review tests before code:** A three-minute review of a failing test suite prevents hours of untangling incorrect implementation details later.
*   **Freeze the acceptance suite:** Make test files read-only during the implementation loop so the agent cannot edit assertions to force a green test suite.
*   **Implement one vertical slice first:** Prove out your architectural boundaries with a single working path from entry point to persistent storage before expanding outward.
*   **Separate mechanical work from business changes:** Run refactorings, framework upgrades, and schema cleanups in distinct commits before introducing new feature logic.
*   **Repro-First Defect Resolution:** Fix bugs by requiring a failing test first. The agent must reproduce the issue with a failing test before touching production code to fix it.
*   **Require a skeptical second review:** Use a separate, dedicated agent session to audit diffs for concurrency issues, performance bottlenecks, and security gaps.
*   **Update the documentation:** Have the agent update domain models, interface definitions, and architectural decision records (ADRs) as the final step of the PR.

---

## Related Notes

*   **[[Reviewing AI-Generated Code]]**: Practical techniques for auditing agent-generated diffs with a focus on human mental models and latent failure modes.
*   **[[The Minimal Frame Pattern - Proving System Topology on Atomic Slices]]**: Proving system boundaries on atomic operational primitives before scaling out.
*   **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Why domain rules and decision tables are essential for keeping agents on track.
*   **[[Testing in the Model, Agent, LLM Era]]**: The architectural rationale for why verification suites must remain immutable during agent implementation passes.
*   **[[Correcting AI Code - Patch, Regenerate, or Respecify]]**: Decision frameworks for fixing bugs in code versus updating upstream specifications.
*   **[[Agentic Coding Harness and Controlled Development Workflows]]**: Practical harness architectures that automatically enforce vertical slice workflows.
*   **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Maintaining living specifications alongside code during feature development.
*   **[[LLMs as a Code Review Team]]**: Using specialized agent review passes to audit features before human sign-off.
*   **[[AI Changes the Economics of Technical Debt]]**: How clean, modular architecture directly accelerates feature delivery speed with agents.
