---
title: Reviewing AI-Generated Code
tags:
  - code-review
  - ai-agents
  - software-engineering
  - verification
  - testing
  - developer-experience
aliases:
  - AI Code Review Practices
  - Verification of Agent Diffs
  - Risk-First Code Review
  - Human Mental Models in Agent Code
---

# Reviewing AI-Generated Code

An AI coding agent can generate five hundred lines of plausible-looking code in thirty seconds. A human engineer cannot review that code with genuine understanding in thirty seconds.

As coding agents become standard in development workflows, **human attention becomes the critical bottleneck**. 

The purpose of code review changes in this environment. It is no longer about catching typos, syntax errors, or formatting debates—linters, static analyzers, and formatters handle mechanical checks before code ever reaches a pull request. Instead, **code review is the mandatory checkpoint where human engineers build and maintain their mental model of the system**. 

When engineers rubber-stamp pull requests because the code looks clean and the tests are green, the team surrenders comprehension of its own software. When an inevitable production incident strikes, the team finds itself operating an alien codebase that nobody truly understands.

```text
Agent Code Generation (Low Friction)
             │
             ▼
Automated Linters & Unit Tests Pass
             │
             ▼
Illusion of Understanding  ──► Skimmed and approved without building mental model
             │                                   │
             ▼                                   ▼
Production Incident Strikes                Agent Reasoning Limit Reached
             │                                   │
             ▼                                   ▼
Engineer Summoned to Debug  ◄────────────── Agent Thrashes / Hallucinates Fixes
             │
             ▼
No Engineer Understands Runtime Behavior  ──► Extended Downtime & Operational Deadlock
```

---

## 1. The Illusion of Understanding

The most dangerous failure mode in agentic development is skimming. Agent-generated diffs are uniquely deceptive because they rarely look broken:

- Variable and method names are descriptive and idiomatic.
- Unit tests pass cleanly in CI.
- The model-generated pull request summary sounds structured and authoritative.
- The architecture mimics established patterns in the repository.
- Most lines look like standard boilerplate.

It is remarkably easy to scroll through a diff, nod along, and approve it without reconstructing the actual runtime behavior in your head. 

This creates a slow-burning architectural hazard. When diffs are merged based on superficial plausibility, [[Software Decay and the Hidden Costs of Frictionless AI Code|software entropy and frictionless code sprawl]] accelerate. Over several months, the repository morphs into an application where every file compiles and passes tests, but no engineer on the team understands how the pieces interact, which invariants protect the database, or why specific trade-offs were made.

When a severe production defect emerges—such as a distributed race condition, database connection pool exhaustion, or an inconsistent state transition across microservices—the generating agent will struggle. Large language models hit reasoning limits when debugging cross-system distributed state without deterministic feedback loops. If the human engineers abdicated their mental model during review, they are left debugging a system they do not understand.

---

## 2. Risk-First Review Order

Standard code review tools display files alphabetically. Reviewing an agent's pull request alphabetically is a mistake: it burns fresh mental energy on trivial configuration files, generated DTOs, and dependency injection wiring before the reviewer ever inspects the core business logic.

Review must be organized strictly around operational risk:

```text
1. Business Rules & State Mutations  ──► Did the agent understand the domain invariants?
               │
               ▼
2. Public Contracts & Migrations    ──► Are API contracts preserved? Will migrations lock tables?
               │
               ▼
3. Transactions & Concurrency       ──► Are isolation levels, locks, and retry loops safe?
               │
               ▼
4. Authorization & Failure Paths    ──► Are permission checks intact? What happens on partial failure?
               │
               ▼
5. Side-Effect Ordering             ──► Do database writes happen before external network calls?
               │
               ▼
6. Acceptance & Regression Tests    ──► Do tests verify edge cases or merely pass vacuously?
               │
               ▼
7. Mechanical Glue & Boilerplate    ──► DTO mappings, DI registration, and trivial adapters.
```

By prioritizing the review this way, critical boundaries receive scrutiny while your focus is highest. If fatigue sets in, it happens on low-risk mechanical glue rather than the state mutations that corrupt production data.

---

## 3. The Core Review Standard: Mental Model Construction

A foundational standard for approving any agent-generated change is:

> Before approving the change, the reviewer must be able to explain the complete new execution flow in their own words without consulting the AI-generated summary.

If you cannot explain the flow independently, you have not reviewed the code; you have merely verified that it compiles. Specifically, an engineer should be able to answer four concrete operational questions:

1. **Execution and Transformation:** How does data enter, transform, and leave this component? Trace the primary path from entry point to persistence.
2. **Invariants and Constraints:** What conditions must always hold true? What prevents corrupted or half-formed state from being committed?
3. **Partial Failure Behavior:** What happens when an external HTTP call, cache write, or secondary database query fails halfway through execution? Does the system leave orphaned records, or does it roll back cleanly?
4. **Concurrency and Idempotency:** Can two worker processes or HTTP threads execute this operation on the same entity simultaneously without race conditions, duplicate writes, or deadlocks?

---

## 4. Inspecting Tests as Critically as Production Code

Coding agents are remarkably adept at generating tests that pass without proving requirements. When an agent writes both the implementation and the test suite, it naturally mirrors its own blind spots across both.

Inspect the test diff with the same skepticism applied to production code, looking for three common patterns:

- **Tautological Assertions:** Tests that assert mock outputs against hardcoded mock expectations. The test passes green, but only proves the mocking framework works as configured, not that the integrated system behaves correctly.
- **Missing Negative Cases:** Agents lean heavily into happy-path validation. A pull request may include ten tests checking successful 200 OK responses, but zero tests for network timeouts, schema validation rejections, duplicate webhook deliveries, or authorization denials.
- **Vacuous and Overly Permissive Matchers:** Assertions that check only for broad conditions (such as asserting an object is non-null or an HTTP status is 200) without validating that the payload contents, database state, and side effects match the business specification.

As detailed in [[Why Business Logic Is the Hardest Part of Agentic Coding|verifying agent business logic]], tests serve as your executable specification. If the agent's tests are shallow, its implementation guarantees are worthless (see [[Testing in the Model, Agent, LLM Era|test oracles and verification limits]]).

---

## 5. Using Agents to Support Review, Not Replace It

While an agent should never be the approving authority on a pull request, an isolated, secondary agent session makes an effective adversarial assistant.

Because the authoring agent is biased toward justifying its own implementation, run a fresh agent session against the diff with an explicitly skeptical prompt. A secondary agent can rapidly prepare:

- A concise execution map of the changed runtime behavior.
- Implicit assumptions made by the implementation regarding inputs or external dependencies.
- A shortlist of high-risk files and mutation points.
- Missing negative edge cases and test gaps.
- Observable differences between the old and new behavior.
- Concurrency hazards, race conditions, and leaky transaction boundaries.
- Suspicious abstractions or premature indirection.

### The Adversarial Review Prompt

Use a prompt that explicitly forbids superficial summarization and forces the model to search for operational risks:

```text
Review this diff as a critical staff software engineer and systems architect. 
Do NOT summarize what the code does or praise clean style. 

Actively search for subtle failure modes, bugs, and architectural risks:
1. Incorrect business assumptions: Identify domain invariants that may be violated.
2. Concurrency hazards: Look for race conditions, thread-safety issues, missing locks, or unhandled retry storms.
3. Transaction boundary problems: Check for partial writes, missing rollbacks, long-running transactions holding locks, or incorrect idempotency.
4. Security and authorization issues: Look for missing permission checks, unvalidated inputs, or leaky internal data.
5. Compatibility issues: Identify breaking changes to public API contracts, database migration locks, or backward-incompatible serialization changes.
6. Test weaknesses: Find tests that pass vacuously, assert trivialities, rely on tautological mocks, or fail to prove the underlying requirement.
7. Unnecessary abstraction: Flag speculative indirection, premature generic wrappers, or dead code.

List only concrete technical risks, edge cases, and targeted questions for the human reviewer to verify.
```

The second agent functions as an attention aid. It points your focus directly toward potential landmines, but the final judgment, architectural verification, and approval remain strictly with the human engineer.

---

## 6. Practical Working Rules

- **Review risk, not file order:** Start with database migrations, domain logic, and state mutations; leave controllers, DTO mappings, and boilerplate for the end.
- **Start with business meaning:** Before looking at how a function is implemented, clarify what business invariant it exists to preserve.
- **Inspect tests with production-grade rigor:** Look for tautological assertions, missing failure cases, and loose matchers. Verify that tests fail when the core logic is broken.
- **Ask the invalidating question:** Ask: *"What unstated assumption would make this entire implementation fundamentally wrong?"* Check database isolation assumptions, network latency, and service availability.
- **Enforce the independent explanation rule:** If the reviewer cannot describe the runtime execution path and failure handling in their own words, the pull request stays unmerged.
- **Keep diffs small enough to comprehend:** Agents can spit out 1,500 lines of code effortlessly. Break features into small, cohesive, reviewable slices so humans can maintain genuine mental comprehension.
- **Automate formatting completely:** If a review comment concerns indentation, naming conventions, or import sorting, update the linter or formatter rules. Never waste human review attention on mechanical syntax.
- **Treat review as system learning:** In an agentic workflow where you type less raw code, reviewing diffs is the primary mechanism for maintaining technical mastery over your systems.

---

## Related Notes

- **[[LLMs as a Code Review Team]]**: Practical workflows for configuring multi-agent reviewer teams to assist human auditors.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Maintaining living technical specifications during development to provide the context needed for review.
- **[[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]]**: Decision frameworks for handling review feedback: when to edit manually, re-prompt, or revise the specification.
- **[[Testing in the Model, Agent, LLM Era]]**: Why automated verification is necessary, and where test suites fail to catch deep architectural flaws.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: The operational consequences of unchecked, frictionless code generation and rubber-stamped pull requests.
- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Why domain rules, edge cases, and business invariants require deep human review rather than surface-level checks.
- **[[Developer Satisfaction, Identity, and Burnout in the Age of Coding Agents]]**: Managing the cognitive vigilance required when reviewing high volumes of machine-generated code.
- **[[AI Changes the Role and Training of Software Engineers]]**: The transition of core engineering skills from code production to system design, verification, and critical review.
