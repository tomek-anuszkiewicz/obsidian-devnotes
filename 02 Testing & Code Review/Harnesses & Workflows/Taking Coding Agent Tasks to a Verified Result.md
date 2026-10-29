---
title: "Taking Coding Agent Tasks to a Verified Result"
tags:
  - ai-agents
  - software-engineering
  - testing
  - verification
  - agentic-workflows
aliases:
  - "Verification Loops for Coding Agent Tasks"
  - "From Agent Implementation to Accepted Evidence"
  - "Testing Review and Repair in Agent Workflows"
---

An agent has produced a plausible implementation and reports that the feature is complete. The next question is which observable evidence establishes the intended behavior, which assumptions remain untested, and what should happen when a check fails.

A task can start from a detailed specification or from interactive discovery. Both need an agreed result and a way to evaluate it. Tests, independent review, profiling, and investigation supply different evidence; none becomes sufficient merely because the agent chose to run it. A repair changes the candidate and needs relevant checks again.

The workflows below cover test-first changes, verification loops, review, refactoring under invariants, and measurable goals. [[Agentic Software Development Workflows]] explains the corresponding task-definition choices. A production workflow then composes those techniques into an explicit acceptance process rather than relying on the agent's confidence.

## Test-Driven Agent Development

Traditional TDD becomes especially interesting when coding agents are involved.

The workflow is:

**Requirement → Test → Fail → Implementation → Pass → Refactor**

The first task given to the agent may be:

```text
Write tests describing the requested behavior.

Run them and verify that they fail.

Do not modify production code yet.
```

A human can review the tests before implementation begins.

Then the agent receives the next instruction:

```text
Implement the smallest change that makes the tests pass.
```

This separates two important activities:

1. interpreting the requirement,

2. implementing the solution.

If the agent misunderstood the feature, reviewing the expected test results can reveal the problem before large amounts of implementation code are generated. Writing tests first does not by itself establish that those expectations are correct: the agent can encode the same mistaken interpretation in both tests and implementation.

A particularly strong workflow is therefore:

**Specification → Acceptance Tests → Human Review → Implementation**

The tests become an executable contract between the human and the agent.

The reviewed expected results should remain stable during implementation. If the agent changes assertions merely to accommodate its code, a green suite no longer demonstrates the agreed behavior. When implementation reveals a mistake in the requirement or test, revisit that expectation explicitly, explain why it changes, and review it before using the revised test as evidence.

---

## Verification-Driven Development

Agents should not be expected to produce correct code in a single generation.

Instead, they should operate inside a feedback loop.

A typical workflow might be:

```text
Implement
    ↓
Build
    ↓
Unit Tests
    ↓
Integration Tests
    ↓
Static Analysis
    ↓
Architecture Checks
    ↓
Agent Review
    ↓
Fix
    ↓
Repeat
```

The agent does not stop because it believes the implementation is correct.

It stops because observable checks confirm that predefined conditions have been satisfied.

This leads to an important principle of agentic development:

> Do not depend on the quality of a single generation. Build an environment in which the agent can detect and correct its own mistakes.

The better the feedback loop, the more autonomy can safely be delegated.

A clear specification makes verification more focused, but confidence in the result still depends on the checks actually performed and their coverage. The completion report should connect each acceptance criterion to observed evidence and identify remaining gaps. Agreement in conversation establishes what to verify; it does not establish that the implementation works.

---

## Reviewer and Adversarial Workflows

Implementation and review do not need to be performed by the same agent.

A multi-agent workflow may look like:

```text
Implementation Agent
        ↓
Code Review Agent
        ↓
Adversarial Agent
        ↓
Implementation Agent fixes issues
```

Different agents can have deliberately different goals.

For example, a reviewer may receive:

```text
Assume the implementation contains defects.

Search specifically for:
- race conditions,
- security problems,
- missing edge cases,
- architecture violations,
- incorrect error handling,
- performance regressions.
```

This is useful because an agent reviewing its own work may reproduce the assumptions that produced the original implementation.

Independent agents can provide different perspectives.

---

## Refactor-Driven Development

#refactor

Some agent tasks are not about adding behavior but transforming the implementation while preserving behavior.

The task can therefore be expressed through invariants.

Example:

```text
Replace MediatR with direct handler invocation.

Constraints:
- API behavior must remain unchanged.
- Database schema must remain unchanged.
- Public contracts must remain unchanged.
- Existing tests must continue to pass.
```

The workflow may be incremental:

```text
Module A
↓
Refactor
↓
Tests
↓
Commit

Module B
↓
Refactor
↓
Tests
↓
Commit
```

This approach is suitable for:

- library migrations,

- framework migrations,

- architecture cleanup,

- performance optimization,

- large-scale renaming,

- API transitions.

The key concept is:

**Transformation under preserved invariants.**

If existing test coverage is insufficient, the refactoring workflow must begin with characterization tests. Pinning down current runtime behavior with regression tests before generating refactoring diffs prevents the agent from introducing silent behavioral drift.

---

## Goal-Driven Development

An even more autonomous workflow describes the desired outcome rather than the implementation.

Example:

> `/orders/search` must respond within 100 ms at p99 under the defined test load.

The agent may then:

- profile the endpoint,

- inspect database queries,

- introduce benchmarks,

- modify indexes,

- rewrite SQL,

- remove allocations,

- change caching,

- measure the result,

- repeat the experiment.

The workflow becomes:

**Goal → Measure → Change → Measure → Iterate**

In this model, code is only one possible instrument for achieving an externally measurable objective.

This is particularly promising for:

- performance optimization,

- cost reduction,

- reliability improvement,

- flaky-test reduction,

- security hardening,

- build-time optimization.

---

## A Production-Oriented Agent Workflow

Many of the techniques above can be composed.

A mature workflow could look like:

```text
Business Request
      ↓
Clarify Requirements
      ↓
Agree on Intended Behavior
      ↓
Explore Repository
      ↓
Prepare Implementation Plan
      ↓
Generate Acceptance Tests
      ↓
Human Review
      ↓
Implement Small Task
      ↓
Build + Tests + Static Checks
      ↓
Agent Self-Review
      ↓
Independent Agent Review
      ↓
Commit
      ↓
Next Task
      ↓
Pull Request
      ↓
Human Review
```

This may look heavier than vibe coding, but automation removes much of the cost.

The important change is that software engineering discipline does not disappear when agents write the code.

Instead, many previously human-driven process steps can themselves become automated.

---

## Interactive discovery and autonomous delivery share an acceptance boundary

An engineer can explore behavior with an agent, inspect a working slice, and refine requirements in short cycles. Another task can run unattended from an approved specification. These are different execution modes within one delivery process. Both should produce a candidate, current behavioral agreement, and evidence for independent acceptance.

Distinguish readiness to start from readiness to integrate. A bounded experiment can start with open questions, provided its risks and intended learning are explicit. Integration requires those consequential questions to be resolved and the agreed behavior to pass the applicable checks.

Record important discoveries as the work proceeds. A chat correction that changes a business rule must reach the current specification and examples before later agents or reviewers rely on them. Architectural constraints with broad consequences need deliberate decisions; reversible details can be discovered through interaction (see [[Developing Features with AI Coding Agents]]).

### Reuse implementation across business triggers

A feature request, production bug, and review repair can invoke the same implementation workflow with different inputs. The orchestrator owns the durable state and decides what follows: another review, a product decision, release preparation, or a completion notification. The executor should return an explicit outcome and artifacts rather than infer that its session ending completes the business task.

The wider lifecycle continues after deployment through technical observation, business evaluation, flag cleanup, and recovery readiness. [[Designing an Agentic SDLC for Business Software]] connects these activities without prescribing one working style for every task.

## From Coding Assistants to Software Engineering Agents

The evolution can be summarized roughly as:

```text
AI writes code
        ↓
AI implements features
        ↓
AI executes engineering tasks
        ↓
AI follows engineering processes
        ↓
AI participates in continuous software development
```

The important question is therefore gradually changing from:

> How good is the model at generating code?

to:

> How good is the development system around the model?

A mediocre generation followed by strong tests, feedback, review, and iteration may be far more valuable than an impressive one-shot generation without verification.

The most important architectural challenge in agentic software development may therefore not be code generation itself.

It may be designing the **environment, contracts, feedback loops, and boundaries within which agents work** (see [[Agentic Coding Harness and Controlled Development Workflows]] and [[Building Determinism from Unpredictable Models]]).

Record the result being checked, the candidate that produced the evidence, and the gaps that remain. Use failures to decide the next investigation or repair, and reserve completion for the acceptance conditions the task actually needs.

## Related Notes

- [[Agentic Software Development Workflows]] — Choosing an issue, feature, specification, investigation, or exploration contract.
- [[Developing Features with AI Coding Agents]] — Progressive specification and practical feature delivery.
- [[Acceptance Policies and Automated Repair in Agentic SDLC]] — Protected acceptance rules and bounded repair before escalation.
