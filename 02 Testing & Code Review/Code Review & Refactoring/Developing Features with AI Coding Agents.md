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
  - Progressive Specification with Coding Agents
  - Ready for Development and Ready for Integration
---

## A Strong Workflow for Larger Features

A useful process for consequential changes with sufficiently settled requirements is:

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

When you hand an agent an underspecified prompt on a large feature, its failure mode is predictable: it touches twenty files at once, hallucinates unstated domain assumptions, and writes unit tests that pass only against shallow mocks. Constraining the agent to a staged pipeline prevents sprawling diffs and keeps system topology under control.

### Step 1: Repository Analysis

The agent should first locate:

- existing business flows,
    
- data models,
    
- integration points,
    
- transactions,
    
- existing tests,
    
- compatibility risks,
    
- hidden assumptions.
    

It should not modify the code yet.

Restricting the agent to read-only tools during this phase is essential. When agents break features during repository analysis, it is rarely due to syntax errors; they miss existing transaction boundaries, duplicate helper functions that already exist in adjacent directories, or violate subtle schema constraints like unique indexes and foreign keys. The output of this phase should be an architectural inventory and a list of structural constraints, not code.

### Step 2: Behavioral Specification

The specification should include:

- business objective,
    
- terminology,
    
- rules,
    
- exceptions,
    
- negative cases,
    
- side effects,
    
- compatibility requirements,
    
- non-functional constraints,
    
- explicit out-of-scope items.
    

Free-form requirements can leave branches implicit, which an agent may resolve by inventing a rule. Decision tables and transition matrices make those branches easier to inspect: each row maps a state, event, guard condition, result, and side effect. They improve the review of completeness, but cannot prove that the team identified every important case.

### Step 3: Tests Before Implementation

The agent can prepare:

- business-rule tests,
    
- acceptance tests,
    
- regression tests,
    
- API contract tests,
    
- integration tests.
    

New tests may initially fail. That confirms that they detect the missing behavior.

For newly required behavior, confirm that the relevant test fails for the expected missing behavior before the fix. Tests preserving existing behavior may already pass. A red result caused by broken setup is not evidence that the test detects the requested capability; inspect the failure reason.

### Step 4: Human Review of Meaning

The reviewer should not focus only on test implementation quality.

The main questions are:

- Does the test describe the correct business behavior?
    
- Did the agent invent an unstated rule?
    
- Are negative cases present?
    
- Are priorities between rules correct?
    
- Is the test coupled to one implementation unnecessarily?
    
- Does the test preserve an accidental legacy behavior?
    

This review is an architectural and domain sanity check rather than a syntax or linting pass. The reviewer must ensure tests assert against public boundaries and observable side effects rather than private internal methods, and verify that the agent did not inject arbitrary default values or phantom constraints that were never specified.

### Step 5: Freeze the Acceptance Contract

The implementing agent should not freely modify approved acceptance tests.

It may add technical tests, but changes to the accepted business contract require another review.

Treating approved acceptance tests as read-only is critical during the implementation phase. When an agent runs into difficulty getting code to pass, its path of least resistance is often to rewrite the assertions, remove edge-case coverage, or replace physical database checks with permissive mocks. Freezing the suite forces the agent to fix its implementation rather than weakening the contract.

### Step 6: Implement a Small Vertical Slice

Instead of generating the whole feature at once, implement one full path from entry point to result.

This reveals whether the architecture is appropriate before dozens of files are created.

A vertical slice connects a single path from entry point to persistent storage—for example, one route, one handler, one domain transition, and one transactional database write. Proving out this single slice turns one acceptance test green and confirms that integration boundaries, error envelopes, and transaction lifecycles hold together before expanding horizontally.

### Step 7: Architectural Review of the Slice

Stop and inspect the vertical slice before generating the rest of the feature. This is the cheapest moment to correct structural mistakes:

- Verify that transaction lifecycles and database connections are scoped correctly.
    
- Ensure business invariants remain inside the domain model rather than leaking into application handlers.
    
- Confirm error handling, status codes, and audit logs follow established conventions.
    
- Check that existing utility libraries were reused instead of introducing unnecessary dependencies.
    

### Step 8: Full Implementation (Horizontal Expansion)

Once the vertical slice validates the topology, the agent expands across the remaining requirements:

- Implement the remaining routes, background consumers, and command handlers.
    
- Wire in secondary branches, validation guards, and edge-case handlers identified in the specification.
    
- Ensure metrics, telemetry, and structured logging hooks are in place.
    
- Run the full test suite to confirm that all frozen acceptance tests pass cleanly.
    

### Step 9: Independent Skeptical Review

Before opening a pull request, run an independent review pass in a fresh session to eliminate generation bias. Instruct the reviewer prompt to look exclusively for operational defects:

- Race conditions and lock contention in database queries.
    
- Transaction boundary leaks and missing rollback triggers.
    
- Unhandled errors or dropped promises in asynchronous workers.
    
- Missing database indexes on newly queried columns.
    

### Step 10: Documentation Update

Have the agent update the repository's living documentation as the final step. This includes updating API specifications, interface definitions, database schema notes, and any relevant architectural decision records (ADRs) to reflect the newly merged state.

---

## Tests Are Executable Specifications, but Not Complete Specifications

A test demonstrates an expected example.

It does not always explain:

- why the rule exists,
    
- what a domain term means,
    
- what must not be simplified,
    
- why two similar cases differ,
    
- which behavior is historical but still required.
    

The strongest combination is:

```text
business decision
+ examples or decision table
+ acceptance tests
+ explicit implementation
```

The implementing agent should not be allowed to redefine both the implementation and its acceptance criteria. People settle consequential business meaning; independent checks can enforce already approved criteria according to the organization's acceptance policy.

Otherwise, it can write tests that confirm its own incorrect interpretation.

---

## Practical Working Rules

The staged process above is one mode of work. Interactive discovery can use shorter cycles while preserving the same acceptance boundary.

### Discover reversible details through working behavior

A developer may begin with a bounded sketch, inspect the first working slice, and discover that an edge case or user interaction needs to change. That can be more effective than spending days predicting every detail. Record accepted decisions in the current specification and examples as the behavior becomes clear; do not leave the next executor dependent on an old conversation.

Distinguish **ready for development** from **ready for integration**. The first means that the next step has a clear objective, bounded risk, and enough context to proceed. The second requires agreed behavior and the required verification. "Good enough to start" does not waive the checks needed to merge.

Settle decisions with broad consequences early: data ownership, public contracts, authorization boundaries, financial meaning, and deployment constraints. Explore reversible interface details and local workflow choices through short iterations. If exploration exposes a need to change an architectural constraint, record the new decision explicitly (see [[How AI Changes Prototyping and the Path from PoC to Production]]).

### Share an integration process across working modes

Interactive development and autonomous tasks can both produce a versioned specification, candidate commit, and evidence package. Submit them to the same independent acceptance process. The human's close involvement during coding does not replace the final checks; unattended execution does not require a different definition of correctness.

The interactive workspace can run remotely or on a dedicated VM. The engineer can steer the agent continuously without giving it access to the engineer's production credentials (see [[Isolated Engineering Environments for Coding Agents]]).

An approved feature, a bug with a reproducer, and a repair after review can reuse one implementation workflow with different inputs and outcomes. The surrounding orchestrator records the task and decides what follows. This keeps exploratory work flexible while making integration repeatable (see [[Designing an Agentic SDLC for Business Software]]).

### For feature development

- Analyze before modifying.
    
- Write or approve the behavioral specification.
    
- Use examples and decision tables.
    
- Review acceptance tests before implementation.
    
- Freeze approved business tests (see [[Building Determinism from Unpredictable Models]] and [[Tests Are for Verification, Not Architectural Navigation]]).
- Implement one vertical slice first (see [[The Minimal Frame Pattern - Proving System Topology on Atomic Slices]]).
- Separate mechanical changes from business changes.
- Require a skeptical second review (see [[Reviewing AI-Generated Code]] and [[LLMs as a Code Review Team]]).
- Require a reproducer test before fixing defects.
- Update architectural records and API specs as the final step.

## Related Notes

- [[The Minimal Frame Pattern - Proving System Topology on Atomic Slices]] — Validating system plumbing on atomic feature slices before scaling.
- [[Building Determinism from Unpredictable Models]] — Immutability of test baselines and harness execution gates.
- [[Reviewing AI-Generated Code]] — Review heuristics for catching subtle agent hallucinations.
- [[LLMs as a Code Review Team]] — Multi-agent ensembles for automated architectural and security review.
