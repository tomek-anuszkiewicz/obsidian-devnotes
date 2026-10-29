---
title: Agentic Software Development Workflows
tags:
  - ai-agents
  - agentic-workflows
  - software-engineering
  - developer-experience
  - automation
  - workflow
aliases:
  - Coding Agent Workflows
  - Granularity of Agent Work
  - Agentic Development Lifecycles
---

A request to implement an issue, investigate a failure, or explore an unfamiliar module gives an agent a different starting contract. Choosing that contract determines which facts need to be established before editing, what can be discovered interactively, and what evidence must eventually support completion.

This article focuses on framing the task: features, issues, plans, specifications, investigation, exploration, and granularity. [[Taking Coding Agent Tasks to a Verified Result]] follows implementation through tests, review, repair, and outcome checks. [[Agent Deployment and Execution Models]] develops where that work runs, including environments that support general knowledge work. Task definition, verification, and execution location can be chosen separately and then composed.

AI coding agents can work with a repository in very different ways. The important distinction is not only **which agent or tool is used**, but **what workflow governs its behavior**.

The same coding agent can act as a fast code generator, a test-driven implementer, a planner, a reviewer, a refactoring engine, or a semi-autonomous developer.

A useful way to think about agentic software development is therefore as a collection of composable workflows.

---

## Vibe Coding

#vibe_coding

The simplest workflow is:

**Prompt → Code → Run → Fix**

The developer describes what they want in natural language, and the agent immediately starts modifying the repository.

Example:

> Add authentication and password reset support.

The agent explores the codebase, implements a solution, runs the application or tests, and fixes obvious problems.

This approach is useful for:

- prototypes,

- experiments,

- small applications,

- isolated changes,

- learning and exploration.

Its main weakness is that missing requirements are silently filled in by the model.

The agent may decide:

- how the architecture should work,

- what edge cases matter,

- which abstractions to introduce,

- which behavior the business intended.

For larger systems, this creates a risk of producing a technically valid implementation of the wrong problem.

---

## Feature-by-Feature Development

A safer production-oriented workflow is:

**Feature → Implementation → Verification → PR**

Instead of asking the agent to build a large subsystem, work is divided into relatively small features.

Example:

> Allow an unpaid order to be cancelled.

The agent:

1. explores the affected code,

2. implements the feature,

3. modifies or adds tests,

4. runs validation,

5. produces a small diff or pull request.

Then another feature is handled separately.

This has several advantages:

- smaller context,

- easier review,

- easier rollback,

- fewer unrelated changes,

- simpler debugging,

- clearer history.

For normal software development, this is likely a good default unit of work for an agent.

---

## Issue-Driven Development

Feature-driven development can be made more formal by treating a ticket or issue as the contract.

Example:

```text
Problem:
A paid order can currently be cancelled.

Expected:
Paid orders must not be cancellable.

Acceptance criteria:
- API returns 409.
- Order state remains unchanged.
- Audit event is recorded.
```

The workflow becomes:

**Issue → Agent → Verification → PR**

This is especially interesting because a backlog can effectively become a **task queue for coding agents**.

Instead of developers manually starting every coding session, suitable tickets may eventually be assigned directly to agents.

The quality of the issue then becomes much more important.

Poorly specified tickets produce poorly constrained agent behavior.

---

## Plan-Driven Development

For larger changes, the agent should often be prevented from modifying code immediately.

The workflow becomes:

**Explore → Plan → Review → Implement**

Example instruction:

```text
Study the repository and identify all components affected by this change.

Prepare an implementation plan.

Do not modify the code yet.
```

The agent may return:

```text
1. Extend the domain model.
2. Modify CancelOrderHandler.
3. Update API contracts.
4. Add database migration.
5. Add integration tests.
6. Update documentation.
```

Only after the plan is reviewed does implementation begin.

The plan can live in the agent session. A developer may discuss the change with the agent, revise the proposed steps, and approve execution without creating a Markdown plan in the repository. What matters during the task is that the agent and developer agree on the intended behavior, scope, and checks before editing begins.

The plan does not necessarily need to survive the task. Once the change is complete, code and tests show what was implemented. Decisions that future work will depend on should be recorded where they can be found later, such as in an issue, pull request, or project documentation. The rest of the session plan can be discarded.

This approach is particularly useful for:

- cross-cutting changes,

- architectural changes,

- migrations,

- unfamiliar repositories,

- large refactors,

- changes involving multiple modules.

Planning separates **understanding the problem** from **executing the change**.

### The hidden cost of starting implementation too early

A short instruction can produce a substantial implementation before the developer and agent have agreed on what success means. The apparent saving is the time spent discussing the task. The later cost is discovering which interpretation the agent implemented.

That discovery is engineering work. The developer may need to read unfamiliar code, ask several rounds of questions, trace state changes, or debug the application before being able to judge the result. An explanation from the agent can help locate the relevant code, but its account still needs to be checked against what the system does. Correcting the result then adds another cycle of explanation, implementation, and review.

The cost of a delegated task therefore includes clarification, implementation, understanding the result, verification, and rework. Fast code generation can leave most of that cost with the developer. A useful measure is **time to a result whose correctness we can assess**.

Discussing the behavior before implementation moves some of that understanding work earlier. A wrong assumption can be corrected while it is still a sentence or an example, before it shapes several components and their tests. The developer also enters review with an explicit expectation to compare against the implementation.

The discussion needs a concrete outcome. A plan that says "update the handler and add tests" still leaves the important decisions open. Before implementation, agree on the observable result, the scope of the change, behavior that must be preserved, representative examples, and how the result will be checked.

The appropriate depth depends on uncertainty and the cost of a mistake. A small, familiar change may need only a few acceptance criteria. When the behavior is unclear, agree on a bounded experiment: the question it should answer, the evidence to collect, and the decision that evidence will inform. Trying to specify an entire unknown solution in advance can waste time too.

---

## Spec-Driven Development

#sdd

Spec-driven development makes the intended behavior explicit before implementation.

Instead of going directly from request to implementation, the workflow becomes:

**Request → Requirements → Design → Tasks → Implementation**

A specification may contain several layers. They can be worked out in a conversation and captured in an approved plan. Separate files become useful when the requirements need to be shared or revisited after the session.

### Requirements

Example:

```text
WHEN an authenticated user cancels an unpaid order
THE SYSTEM SHALL change its state to Cancelled.
```

### Agree on examples and evidence

An expected outcome becomes easier to review when it includes a concrete starting state, an action, and an observable result. Discuss unsuccessful operations and boundary cases as well as the successful path. Also identify what a proposed check cannot establish.

For example, "add document saving and test it" leaves persistence behavior and the meaning of a successful test open. A more useful agreement might be:

| Question | Agreed behavior or check |
| --- | --- |
| What should the user achieve? | Save an edited document and recover the same content after restarting the application. |
| What triggers the operation? | The user explicitly selects Save; automatic saving is outside this change. |
| What happens on failure? | A failed write displays an error, retains the edits in memory, and does not report a successful save. |
| How will success be checked? | Start with known content, edit and save it through the application, close the process, reopen the application, and compare the loaded content with the expected content. |
| How will failure be checked? | Cause the storage write to fail and verify the error indication, retained edits, and absence of a success indication. |
| What remains unverified? | These checks alone do not establish recovery from a crash during a write or behavior under concurrent edits. |

A unit test asserting that a save method was called cannot establish the restart behavior. A test that replaces storage with a mock also cannot establish that the real write and reload paths work together. Defining the evidence early exposes this gap before implementation is declared complete.

### Design

The agent determines the affected components and expected architecture.

Example:

```text
CancelOrderCommand
    ↓
CancelOrderHandler
    ↓
Order Aggregate
    ↓
OrderCancelled Event
```

### Tasks

The specification is decomposed into concrete implementation steps.

Example:

```text
[ ] Extend domain model
[ ] Add command handler
[ ] Add endpoint
[ ] Add unit tests
[ ] Add integration tests
```

### Implementation

Only after the intended behavior and implementation approach have been reviewed does the agent modify production code. The review does not require a particular file format.

This reduces the probability that implementation decisions silently redefine the requirement.

If the intended behavior must survive beyond a single chat session, keep a durable specification or update the relevant project documentation. Otherwise, a reviewed session plan may be enough.

---

## Investigation-Driven Development

Sometimes the task should begin with investigation rather than implementation.

Example:

> Production started throwing this exception yesterday. Find out why.

The workflow becomes:

```text
Incident
↓
Collect Evidence
↓
Inspect Logs and Telemetry
↓
Compare with Recent Repository Changes
↓
Form Hypotheses
↓
Test Hypotheses
↓
Propose Fix
↓
Implement
```

This is different from normal feature development because the agent does not initially know what code needs to change.

Its first job is to reduce uncertainty.

This pattern is useful for:

- bugs,

- production incidents,

- regressions,

- performance degradation,

- unexpected business metrics.

- check for private data in logs

In this investigative pattern, the agent operates in forensic mode: querying structured logs, inspecting recent commit diffs, and correlating anomalies before proposing code changes. The critical gate is writing a minimal failing integration test that reproduces the bug under controlled conditions. Only once the failure is deterministically reproduced does the workflow transition into implementation.

---

## Exploration Before Modification

A general rule for larger repositories is that agents should often have a dedicated exploration phase.

For example:

```text
Find:
- relevant modules,
- entry points,
- existing implementations,
- tests,
- architectural rules,
- similar features.

Do not modify code.
```

Only afterward should the agent propose the change.

This avoids a common failure mode where the model encounters one plausible implementation location and starts editing before understanding the wider system.

For agentic work, repository understanding should often be treated as a first-class task.

Enforcing a strict read-only tool gate during exploration prevents premature editing. Disabling file modification tools during initial reconnaissance forces the agent to inspect the repository structure, map dependencies, and discover existing shared abstractions before writing code.

---

## Granularity of Agent Work

Another important dimension is the size of the unit delegated to the agent.

There is a continuum:

```text
Autocomplete
    ↓
Single Function
    ↓
Single Change
    ↓
Feature
    ↓
Issue
    ↓
Pull Request
    ↓
Epic
    ↓
Specification
    ↓
Product Goal
```

As the delegated unit becomes larger, stronger controls are needed.

Large autonomous tasks generally require more:

- specification,

- planning,

- testing,

- observability,

- architecture rules,

- verification,

- checkpoints,

- review.

The correct level of autonomy therefore depends heavily on the quality of the surrounding environment.

---

## These Workflows Are Complementary

These approaches should not necessarily be treated as competing methodologies.

They describe different dimensions of the development process.

**Spec-driven development** makes the intended behavior explicit before implementation. It does not require a permanent specification file for every task.

**Plan-driven development** determines how the work should be decomposed.

**Test-driven development** turns expected behavior into executable checks.

**Feature- or issue-driven development** defines the unit of work.

**Verification-driven development** determines how correctness is demonstrated.

**Reviewer and adversarial workflows** provide independent criticism.

**Refactor-driven development** performs transformations while preserving invariants.

**Goal-driven development** allows the agent to search for solutions to measurable outcomes.

A practical agent workflow may therefore combine several of them.

A reviewed plan can bring these concerns together for one task: what should change, which steps the agent will take, when tests should be written, and how the result will be checked. Preparing the plan does not replace those steps. A test-driven plan still needs a test that fails before the implementation, and a verification-driven plan still needs observable checks to run.

For example:

```text
Issue
↓
Specification
↓
Repository Exploration
↓
Plan
↓
Acceptance Tests
↓
Implementation
↓
Verification Loop
↓
Independent Review
↓
PR
```

---

## Related Notes

- [[Agentic Coding Harness and Controlled Development Workflows]] — Orchestrating vertical slices and constraints in the agent harness.
- [[Building Determinism from Unpredictable Models]] — Enforcing deterministic build, test, and rollback boundaries around models.
- [[AI Productivity Is Limited by the Delivery System]] — Why harness and CI/CD throughput bound practical AI output.
- [[Multi-Agent Software Development]] — Multi-role agent coordination, handoffs, and verification architectures.
