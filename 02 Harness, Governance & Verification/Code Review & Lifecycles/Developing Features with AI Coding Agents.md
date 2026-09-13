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

# Developing Features with AI Coding Agents

When developers ask an agent to build a new feature using a vague prompt—*"Add a subscription billing module with Stripe integration"*—the result is almost always a mess. The agent generates twenty files at once, invents its own domain logic, leaves edge cases unhandled, and writes tests that pass only because they assert mock trivialities.

Building reliable features with AI agents requires a disciplined, step-by-step engineering progression:

```text
Repository Analysis ──► Behavioral Spec & Decision Tables ──► Acceptance Tests Prepared
                                                                          │
                                                                          ▼
Full Implementation ◄── Architectural Review ◄── Vertical Slice ◄── [ HUMAN REVIEW ]
(Skeptical Audit)       (Verifies topology)      (Thin end-to-end)   (Freezes tests)
```

By forcing the agent to analyze before touching code, write tests before implementation, and prove the architecture with a thin vertical slice first, teams avoid sprawling rewrites and keep systems maintainable.

---

## Core Invariants

1. **Analyze Before Editing**: Never let an agent modify code on turn one. The agent must first map existing domain boundaries, data models, and integration points.
2. **Decision Tables Over Prose Prompts**: Natural language instructions are inherently ambiguous. High-leverage feature specifications use explicit truth tables and boundary matrices, eliminating model confusion across business permutations (see [[Why Business Logic Is the Hardest Part of Agentic Coding]]).
3. **Tests Before Code (Agent TDD)**: The agent must generate acceptance tests that fail against the current codebase before writing implementation code.
4. **The Frozen Acceptance Gate**: Once a human engineer reviews and approves the acceptance tests, those tests are marked read-only. The implementing agent must adapt the code to satisfy the tests—never modify the tests to excuse partial implementations (enforcing [[Testing in the Model, Agent, LLM Era|The Frozen Oracle Rule]]).
5. **The Vertical Slice Rule**: Never generate an entire feature across twenty files in a single pass. Implement one thin, end-to-end path (from API endpoint down to database write) first to validate the architecture before generating the remaining handlers.

---

## 1. The Disciplined Feature Lifecycle

Within a modern development workflow, building a feature with an agent follows eight distinct phases:

```text
1. Repository Reconnaissance ──► Maps models, endpoints, and schemas without changing files.
               │
               ▼
2. Behavioral Specification  ──► Documents business intent, decision tables, and non-goals.
               │
               ▼
3. Failing Acceptance Tests  ──► Writes tests covering business rules; tests fail initially.
               │
               ▼
4. Human Review of Meaning   ──► Engineer confirms: does this describe the real business need?
               │
               ▼
5. Freeze the Test Suite     ──► Tests locked read-only; agent cannot weaken assertions.
               │
               ▼
6. Thin Vertical Slice       ──► Implements one single end-to-end path to prove architecture.
               │
               ▼
7. Horizontal Expansion      ──► Implements remaining endpoints, edge cases, and handlers.
               │
               ▼
8. Skeptical Second Review   ──► Independent agent audits diff for concurrency and security gaps.
```

---

## 2. Step-by-Step Implementation Guide

### Step 1: Repository Reconnaissance (Read-Only)
Before writing any code, instruct the agent to inspect the codebase and answer:
- Where do similar features live, and what patterns do they follow?
- What database tables and schema constraints are involved?
- How are transactions, logging, and error handling managed?
- What existing utilities or shared packages should be reused?

*Hard Rule*: Zero file modifications during this step. The output is purely a technical summary.

### Step 2: Behavioral Specification & Decision Tables
Do not rely on long narrative descriptions of business logic. Use structured decision tables that map inputs and states directly to expected outputs:

```text
Current State    Event / Input            Expected Result          Side Effects
────────────────────────────────────────────────────────────────────────────────────────────
Active           Cancel Requested         Status: CancelPending    Send cancellation email
Active           Payment Fails (Attempt 1)Status: Active           Schedule retry in 24h
Active           Payment Fails (Attempt 3)Status: Suspended        Emit SubscriptionSuspendedEvent
Suspended        Payment Succeeds         Status: Active           Emit SubscriptionReactivatedEvent
```

Decision tables force clarity: every branch is explicit, preventing the agent from guessing how to handle edge cases.

### Step 3 & 4: Acceptance Tests & Human Sign-Off
The agent translates the decision table into automated acceptance tests. Before any implementation begins, a human engineer reviews the tests:
- *Did the agent invent business rules that were never requested?*
- *Are distributed failure modes (database timeouts, third-party 500 errors) tested?*
- *Do the tests assert actual business state changes, or do they merely check mock interactions?*

Once approved, the tests are locked. The agent is strictly forbidden from altering test assertions during implementation.

### Step 5: The Vertical Slice
Instead of having the agent generate five controllers, eight DTOs, three service interfaces, and database migrations simultaneously, have it implement **one complete transaction**:
1. One API route.
2. One application command handler.
3. One database query or update.
4. Verify that this single path compiles, runs, and passes its corresponding acceptance test.

If the module boundaries or database mappings feel awkward, refactoring one thin slice takes two minutes. If you waited until twenty files were generated, restructuring would take hours.

### Step 6: Horizontal Expansion & Skeptical Audit
Once the vertical slice proves the architecture, let the agent generate the remaining branches, error paths, and validation rules.

Before opening a pull request, run a secondary agent session with a skeptical review prompt:
> *"Audit this pull request diff for race conditions, unhandled exceptions, missing database indexes, and security issues. List only concrete concerns."*

This surfaces hidden landmines before the code reaches human review (see [[Reviewing AI-Generated Code]]).

---

## Practical Rules for Teams

1. **Never skip the analysis step**: An agent that jumps straight to editing files will almost certainly miss existing utilities and create duplicate logic.
2. **Review the tests before the code**: Reviewing tests takes three minutes and ensures you agree on what the feature actually does.
3. **Freeze test files during generation**: In automated agent harnesses, mark test directories as read-only while the agent writes implementation code.
4. **Implement thin slices**: If an agent's pull request touches more than 6 files for a new feature, you probably didn't slice it thinly enough.
5. **Separate refactoring from features**: If building a feature requires cleaning up existing code, do the refactoring in a separate, dedicated commit first.

---

## Related Notes

- **[[Reviewing AI-Generated Code]]**: Best practices for auditing agent-generated code with a focus on risk and human mental models.
- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Why domain rules and decision tables are essential for keeping agents on track.
- **[[Testing in the Model, Agent, LLM Era]]**: The foundational verification hub explaining why automated tests must remain immutable during implementation.
- **[[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]]**: How to triage whether to fix bugs in code or upstream in the specification.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Practical harness architectures that enforce vertical slice workflows automatically.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Maintaining living specifications alongside code during feature development.
- **[[LLMs as a Code Review Team]]**: Using independent agent reviewers to audit features before human sign-off.
- **[[AI Changes the Economics of Technical Debt]]**: Why clean, modular architecture directly accelerates feature delivery speed with agents.
