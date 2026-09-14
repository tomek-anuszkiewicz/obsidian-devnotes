---
title: Correcting AI-Generated Code — Patch, Regenerate, or Change the Specification
tags:
  - ai-agents
  - software-engineering
  - code-review
  - debugging
  - prompt-engineering
  - refactoring
aliases:
  - Patch vs Regenerate vs Respecify
  - Fixing AI-Generated Code
  - The Defect Attribution Hierarchy
  - Architectural Sediment
  - Upstream Defect Resolution
  - Co-Evolution of Code and Specs
---

# Correcting AI-Generated Code — Patch, Regenerate, or Change the Specification

When an autonomous coding agent delivers code with a bug or a design flaw, developers instinctively reach for their keyboard and start editing lines manually. But in an agent-assisted workflow, manual code hacking is often the slowest and most fragile path forward. 

The fundamental rule for correcting agent-generated code is:

> **Fix the lowest layer in the system that actually contains the defect, but no lower.**

- If the code contains a localized bug, patch the code.
- If the agent repeatedly violates team style or conventions, update the project rules.
- If the module's structure or layering is wrong, update the architectural boundary and **regenerate the component**.
- If the agent mishandled a business edge case because the requirements were ambiguous, **update the specification first**.

Treating generated code as sacred and applying patch after patch creates **architectural sediment**—brittle, disjointed code that carries the fossilized remains of previous failed attempts.

```text
Decision Level               Defect Type                    Remediation Strategy
──────────────────────────────────────────────────────────────────────────────────
[ SPECIFICATION ]     ──►  Missing Business Edge Case  ──►  Update Spec & Regenerate Module
       │
       ▼
[ ARCHITECTURE ]      ──►  Layering / Boundary Leak    ──►  Update Boundary & Regenerate Slice
       │
       ▼
[ PROJECT POLICY ]    ──►  Recurring Model Mistake     ──►  Update Rules / Negative Fences
       │
       ▼
[ IMPLEMENTATION ]    ──►  Isolated Local Bug          ──►  Targeted Inline Code Patch
```

---

## Core Invariants

1. **Fix Upstream, Not Downstream**: Implementation code is an artifact derived from specifications, architectural rules, instructions, and tests. Patching code without updating the upstream specification guarantees that the next agent invocation will overwrite your fix or reintroduce the bug.
2. **The Regeneration Threshold**: When an agent gets the high-level architecture or state transitions wrong, delete the code and regenerate it. Throwing away 300 lines of flawed code and regenerating a clean version takes two minutes; trying to untangle and patch bad architecture takes hours.
3. **The Frozen Oracle Rule**: Never allow an agent in a self-repair loop to modify its own test assertions or acceptance criteria. An agent given permission to change tests will inevitably weaken them to make its broken code pass (see [[Testing in the Model, Agent, LLM Era|test oracles and verification]]).
4. **Three Distinct Classes of Artifacts**:
   - **Targets (What)**: Acceptance criteria, living specs, and frozen tests (owned and approved by human engineers).
   - **Policies (How)**: Architectural rules, negative constraints, and code conventions (continuously updated).
   - **Outputs (Generated)**: Implementation code, boilerplate DTOs, and configuration files (cheap to throw away and regenerate).
5. **Code Review Shifts from Formatting to Invariants**: Reviewing agent code is not about checking syntax or formatting debates. Automated formatters handle syntax; human review focuses on state invariants, concurrency boundaries, and unhandled failure states.

---

## 1. The Defect Attribution Matrix

When an agent-generated pull request fails tests or design review, diagnose the level of failure before choosing a fix:

| Failure Level | Typical Symptom | Target Artifact | Corrective Action |
| :--- | :--- | :--- | :--- |
| **LOCAL IMPLEMENTATION** | Off-by-one loop error, inverted boolean, missing null check | Concrete Source File | Apply an inline patch or prompt the agent to fix the single function. |
| **PROJECT POLICY** | Model imports banned library, uses deprecated API, skips logging | `.agents/rules/` / Guidelines | Add an explicit rule or negative constraint; re-run the generation. |
| **ARCHITECTURE** | Controller queries database directly, bypassing application layer | Module Architecture / ADR | Define the boundary rule, delete the generated file, and regenerate. |
| **SPECIFICATION** | Unhandled domain state (e.g. user cancels order while payment is processing) | Living Markdown Spec | Clarify the business requirement in the spec, add a test, and regenerate. |

---

## 2. Patching vs. Regeneration: Avoiding Architectural Sediment

A major trap in working with AI coding assistants is the **patch cascade**:

```text
Agent generates initial implementation A
                 │
                 ▼
Reviewer spots an architectural flaw ──► Prompts agent to patch into hybrid B
                 │
                 ▼
Edge case breaks under testing       ──► Prompts agent to patch into compromise C
```

Version `C` may eventually pass the unit tests, but its internal structure is a mess: dead helper methods, defensive null-checks wrapping redundant try/catches, and awkward adapter layers left over from versions `A` and `B`. This is **architectural sediment**.

### When to Patch
- The overall component structure, layering, and domain model are completely sound.
- The defect is confined to a single function body or arithmetic calculation.
- Applying the fix takes thirty seconds and does not alter how other components interact with this code.

### When to Regenerate
- The agent chose the wrong abstraction (e.g. creating a complex inheritance hierarchy instead of a simple composition loop).
- Data ownership is in the wrong place (e.g. state is managed in transport controllers instead of domain aggregates).
- You find yourself writing more than two rounds of corrective prompts trying to bend bad code into shape. 
- Discarding the file, updating your prompt or specification with one clear negative boundary, and regenerating from scratch produces pristine code with zero baggage.

---

## 3. Concrete Example: Upstream Correction vs. Local Patching

Imagine an agent tasked with adding an order status endpoint. It generates this structure:

```text
[ HTTP Controller ] ──► [ OrderService ] ──► [ Raw Database Queries / ORM Context ]
```

During review, you realize this violates your team's architecture: transport controllers must not call database services directly; they must dispatch through command and query handlers.

### The Bad Fix (Local Patching)
You prompt the agent: *"Wrap the database call in a try/catch block inside the controller and call it a day."*
- **The Consequence**: The pull request merges, but the architectural violation is now locked into the codebase. Future agents reading this controller as an example will copy this bad pattern across twenty new endpoints.

### The Good Fix (Upstream Boundary & Regeneration)
1. **Enforce the Boundary**: Add a negative rule to project guidelines: *"Transport controllers must dispatch commands and queries via mediator/application handlers; direct database access is forbidden."*
2. **Delete & Regenerate**: Delete the controller and instruct the agent: *"Implement the order status endpoint following our mediator pattern."*
3. **The Outcome**: The agent generates clean, separated layers:
   ```text
   [ HTTP Controller ] ──► [ GetOrderStatusQueryHandler ] ──► [ OrderRepository ]
   ```
4. The codebase stays clean, and the updated rule protects every future agent task.

---

## 4. Immutable Success Criteria in Automated Loops

When setting up autonomous agent loops that compile, run tests, and fix errors automatically, the permissions must be strictly divided:

```text
               Agent Permission Boundary in Automated Repair Loops
┌────────────────────────────────────────────────────────────────────────┐
│ MUTABLE BY AGENT                                                       │
│ • Implementation source code                                           │
│ • Local helper methods, variable names, and internal logic             │
│ • Scratchpad notes and temporary execution traces                      │
├────────────────────────────────────────────────────────────────────────┤
│ STRICTLY IMMUTABLE (READ-ONLY)                                         │
│ • Acceptance criteria and user story specifications                    │
│ • Frozen test suites and behavioral assertions                         │
│ • Repository architectural rules and forbidden dependencies            │
└────────────────────────────────────────────────────────────────────────┘
```

If an agent has write access to the test suite while trying to fix a bug, its path of least resistance is often to modify the test assertion so that it passes. Automated repair loops must treat tests as **frozen oracles**: the code must adapt to the test, never the test to the code.

---

## 5. Review as Specification Discovery

In traditional programming, discovering a missing business rule during code review is painful because rewriting manual code takes days.

With coding agents, **code review becomes a tool for discovering missing requirements**:
1. You review an agent's pull request for order cancellations:
   ```typescript
   if (order.status === OrderStatus.Pending) {
       cancelOrder();
   }
   ```
2. Reading the concrete code triggers a question you hadn't considered: *"What happens if the payment gateway already authorized the charge while the order was pending?"*
3. Instead of hacking a quick nested `if` statement into the code, you update the specification:
   ```markdown
   ### Order Cancellation Requirements
   An order in `Pending` status may only be cancelled immediately if no payment 
   authorization exists. If funds were authorized, cancellation must trigger an 
   asynchronous release request before updating the status to `Cancelled`.
   ```
4. You pass the updated specification back to the agent, which regenerates the handler with proper payment gateway calls and error handling.

Code review shifts from superficial nitpicking to high-leverage business modeling.

---

## 6. Co-Evolution: Keeping Specs and Code in Sync

In fast-paced engineering, developers often don't have time to write comprehensive specification documents before every small bug fix. They give conversational instructions: *"When the remote payment gateway returns a 429 rate-limit error, retry three times with exponential backoff before throwing."*

The danger of this conversational shortcut is **documentation drift**: the code gets updated, but the specification document or architecture diagram rots.

A mature development harness automates **co-evolution**:

```text
                  CO-EVOLUTION & BACK-PROPAGATION WORKFLOW
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. DEVELOPER CONVERSATIONAL PROMPT                                          │
│    "When payment gateway returns 429, retry 3x with backoff before failing" │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. HARNESS RESOLVES TRACEABILITY                                            │
│    Agent identifies target source files AND governing spec:                 │
│    [docs/architecture/payment-integration.md]                               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                     ┌─────────────────┴─────────────────┐
                     ▼                                   ▼
┌───────────────────────────────────────────┐ ┌───────────────────────────────────────────┐
│ 3A. IMPLEMENT CODE REPAIR                 │ │ 3B. UPDATE LIVING SPECIFICATION           │
│ • Implements exponential backoff loop     │ │ • Adds 429 retry policy to payment spec   │
│ • Adds automated regression unit test     │ │ • Documents backoff timings and limits    │
└─────────────────────┬─────────────────────┘ └─────────────────────┬─────────────────────┘
                      │                                             │
                      └─────────────────────┬───────────────────────┘
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. ATOMIC COMMIT                                                            │
│    Code fix, regression test, and documentation update committed together   │
└─────────────────────────────────────────────────────────────────────────────┘
```

By ensuring that every code repair back-propagates into project specifications and regression tests, the team prevents documentation drift while maintaining rapid development momentum (see [[In-Flight Documentation as the Primary Framework for Coding Agents]]).

---

## Related Notes

- **[[Testing in the Model, Agent, LLM Era]]**: The foundational verification hub explaining the Frozen Oracle Rule and why automated tests must remain immutable during repair loops.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: How maintaining lightweight documentation during development anchors agent context and prevents documentation drift.
- **[[Learning Coding Agents Through Failure-Driven Instructions]]**: How to turn agent failures into project-level rules and eval benchmarks.
- **[[Negative Knowledge and Explicit Architectural Dissents]]**: How defining what an agent must NOT do is often more effective than micro-managing step-by-step implementations.
- **[[Developing Features with AI Coding Agents]]**: Best practices for breaking down feature requests into verifiable specifications before prompting agents.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: Why unconstrained code patching without architectural resets accelerates technical debt.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Designing closed-loop execution harnesses that constrain agent repairs.
- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Why domain requirements and business edge cases are the primary source of agent failure.
- **[[Refactoring Legacy Systems with AI Agents]]**: Applying the regeneration and clean-slate approach to modernizing legacy codebases.
