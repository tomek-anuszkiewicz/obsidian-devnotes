---
title: Learning Coding Agents Through Failure-Driven Instructions
tags:
  - ai-agents
  - agentic-coding
  - continuous-improvement
  - prompt-engineering
  - knowledge-distillation
  - software-engineering
aliases:
  - Failure-Driven Agent Learning
  - Instruction Tuning from Coding Failures
  - Procedural Memory for Coding Agents
  - Eval-Driven Instruction Engineering
  - Dual Optimization Loops
---

# Learning Coding Agents Through Failure-Driven Instructions

When developers get frustrated with a coding agent making mistakes, their instinctive reaction is to either manually fix the code or dump another paragraph of rules into a global prompt file. Both reactions fail over time: manual fixes teach the system nothing, and append-only instruction files quickly become bloated, contradictory, and ignored by the model.

Instead of treating agent instructions as static prompts or dumping grounds for grievances, **instructions should be treated as versioned, testable engineering assets that evolve through failure analysis**. 

The goal is to increase **first-pass success**: every time an agent fails, that failure should be diagnosed, generalized, and encoded into the system so that future agents avoid the entire category of mistake.

```text
Ad-hoc Prompting ──► Project Instructions ──► Eval-Driven Rules ──► Organizational Procedural Memory
```

---

## Core Invariants

1. **The Dual Optimization Loop**: Agent-assisted development operates on two distinct loops:
   - **Inner Loop (Code Level)**: The agent writes and fixes code against immediate compiler, lint, and test signals.
   - **Outer Loop (Instruction Level)**: The engineering team analyzes mistakes that escaped the inner loop, extracting reusable rules so future agents get it right on the first try.
2. **First-Pass Success as the Primary Metric**: Eventual success after eight repair loops is expensive in both token cost and human attention. Systems should optimize for getting acceptable code on turn one.
3. **Instructions as Code**: Never let instructions become an uncurated list of ad-hoc rules. They must be versioned, tested against regression suites, compressed, and pruned when obsolete.
4. **Targeted Rule Retrieval (Behavioral RAG)**: Rather than loading hundreds of project rules into every prompt, dynamically retrieve instructions based on the specific subsystem, framework, or task domain being touched.
5. **Compounding Code Review**: When a senior engineer points out a design flaw in review, that insight should be captured once and converted into an instruction, linter rule, or test.

---

## 1. The Two Optimization Loops

```text
Outer Loop: Team Learning (Eval-Driven Instruction Tuning)
┌────────────────────────────────────────────────────────────────────────┐
│ Task Spec + Versioned Instructions (vN)                                │
│     │                                                                  │
│     ▼                                                                  │
│ Inner Loop: Code Generation & Immediate Feedback                       │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ Agent Generates Code ──► Linter / Compiler / Tests ──► Pass / Fail │ │
│ │      ▲                                              │              │ │
│ │      └────────── Local Fix Loop ────────────────────┘              │ │
│ └────────────────────────────────┬───────────────────────────────────┘ │
│                                  │ (Task Complete or Stuck)            │
│                                  ▼                                     │
│ Diagnose Root Cause ──► Extract Invariant ──► Eval Against Past Tasks  │
│                                  │                                     │
│                                  ▼                                     │
│              Commit Updated Instruction Set (vN+1)                     │
└────────────────────────────────────────────────────────────────────────┘
```

### The Inner Loop: Local Code Repair
The baseline coding loop relies on deterministic tools:
- Compilers and typecheckers.
- Unit and integration tests.
- Linters, formatters, and dependency boundary checkers.

The agent loops locally until these automated checks pass (see [[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]]). But if the team only relies on the inner loop, the system has no memory: an agent will make the exact same architectural mistake on Friday that it made on Monday, burning tokens and time rediscovering boundaries that were already known.

### The Outer Loop: Instruction Refinement
The outer loop operates across tasks:
1. **Log Failures**: Track where agents required multiple correction cycles, violated unwritten architectural standards, or received human review pushback.
2. **Find the Root Cause**: Determine whether the failure was a one-off logic bug or a missing architectural constraint (see [[Negative Knowledge and Explicit Architectural Dissents]]).
3. **Draft a Rule Update**: Formulate a concise guideline or negative constraint.
4. **Evaluate Offline**: Test the new rule against a benchmark suite of historical tasks to confirm that it prevents the error without degrading performance on other tasks.

---

## 2. Example: Preventing Architectural Layering Violations

Suppose an agent is assigned a straightforward task:
> *"Add an endpoint to retrieve recent customer orders."*

### The Naive Implementation
The agent writes a solution that passes all unit tests, but violates system boundaries:

```text
[ HTTP Controller / Endpoint Handler ]
                 │
                 │ (Direct database query: architectural violation)
                 ▼
        [ Database Storage ]
```

A human reviewer flags the pull request: *Controllers are transport adapters only. They must not query the database directly; they must call application query handlers.*

### Turning the Review into a System Rule

```text
Observed Mistake:
The controller queried the database directly instead of dispatching to an application handler.

Why It Happened:
The agent had no context describing the service's layered architecture or clean boundaries.

Extracted Guideline:
Controllers and transport handlers are interface adapters only. They validate request input 
and delegate execution to application handlers. Never query the database or ORM directly 
from transport controllers.
```

By adding this rule to the repository instructions (or enforcing it with an architecture linter), future agents across all services will structure the code correctly on the very first attempt:

```text
[ HTTP Controller ] ──► [ Application Query Handler ] ──► [ Storage Layer ]
```

---

## 3. First-Pass Success: Measuring Real Productivity

Tracking only whether an agent eventually completes a task is misleading. An agent that takes seven compile-and-fix iterations often produces bloated, defensive code full of unnecessary null-checks and redundant wrapper logic.

### Core Metrics to Track
- **First-Pass Success Rate**: The percentage of tasks completed without requiring corrective cycles or human intervention.
- **Iteration Depth**: The average number of compile, test, and repair cycles per task.
- **Token and Compute Cost**: Total tokens spent per merged pull request.
- **Reviewer Overhead**: How much human engineering time is needed to audit and correct agent-authored pull requests.

The goal is to improve first-pass quality while keeping instructions concise enough that they don't eat into the model's working memory (see [[How LLM Systems Build Context]]).

---

## 4. Preventing Instruction Bloat

The biggest trap in prompt maintenance is the **append-only anti-pattern**:

```text
Bug Occurs ──► Append Rule to INSTRUCTIONS.md ──► File Grows to 1,000 Lines ──► Model Ignores Half the Rules
```

When prompt instructions become too long or repetitive, models suffer from [[Constraint Saturation and Rule Oscillation in Coding Agents|rule oscillation]], prioritizing recent or loudly worded constraints while ignoring foundational ones.

Instructions need regular maintenance:

```text
                      Agent Mistake Observed
                                │
                                ▼
                       Extract Core Rule
                                │
                                ▼
                   Check for Duplication / Conflicts
                                │
                                ▼
               Draft Formulations (Concise vs. Detailed)
                                │
                                ▼
                 Run Against Historical Task Suite
                                │
                   ┌────────────┴────────────┐
                   ▼                         ▼
            [ Better Results ]        [ Neutral / Worse ]
                   │                         │
                   ▼                         ▼
            Commit to Repo            Discard Draft
```

### Testing Rule Formulations
Different ways of phrasing the same concept can produce surprisingly different results:

| Formulation Style | Example | First-Pass Rate | Avg. Iterations | Token Cost |
| :--- | :--- | :---: | :---: | :---: |
| **Strict Proscription** | *"Do not access the database context from controllers."* | 84% | 1.9 | Lowest |
| **Architectural Role** | *"Controllers are transport adapters only. Delegate all data queries to application handlers."* | 91% | 1.4 | Moderate |
| **Step-by-Step Procedure** | *"1. Create or find the handler. 2. Place query inside handler. 3. Call handler from controller."* | 92% | 1.3 | Highest |

The best formulation is rarely the longest one; it is the most concise phrasing that reliably steers the model.

---

## 5. Behavioral RAG: Loading Rules on Demand

As an organization accumulates dozens of architectural rules, injecting all of them into every prompt wastes context and dilutes attention.

A better approach is **Behavioral Retrieval**: breaking guidelines into small, focused files and loading only what is relevant to the task:

```text
rules/
├── architecture/
│   ├── layer-boundaries.md
│   ├── messaging-conventions.md
│   └── database-access.md
├── runtime/
│   ├── async-cancellation.md
│   └── error-handling.md
├── domain/
│   ├── billing-rules.md
│   └── order-workflows.md
└── testing/
    ├── integration-tests.md
    └── test-fixtures.md
```

When an agent is assigned to *"Update payment retry backoff"*, the harness loads only:
- `architecture/layer-boundaries.md`
- `runtime/async-cancellation.md`
- `domain/billing-rules.md`

This provides high-signal guidance exactly where needed, without polluting the context with irrelevant rules about front-end components or database migrations.

---

## 6. Turning Review Comments into Compounding Assets

Traditional code review treats human corrections as disposable:

```text
Traditional Review:
Agent Makes Error ──► Human Explains Flaw ──► Agent Patches PR ──► Insight Lost in Git History
```

A learning-oriented development workflow captures human feedback as enduring assets:

```text
Compounding Review:
Agent Makes Error ──► Human Explains Flaw ──► Insight Encoded into Rule or Linter
                            │
                            ▼
              Added to Behavioral Regression Suite
                            │
                            ▼
              Future Agents Avoid the Entire Category of Error
```

### The Don't-Patch-in-Silence Rule
To prevent organizational memory from leaking away, teams should follow a simple rule: **never silently patch an agent's architectural mistake by hand**.

1. **The Silent Fix Anti-Pattern**: A developer sees that an agent created an unnecessary wrapper class or mishandled an edge case. To save 30 seconds, the developer fixes it manually and merges the pull request. The problem is that the next agent will make the exact same mistake tomorrow.
2. **Codify the Correction**: Instead of a silent fix, spend two minutes turning the correction into an explicit guideline, a project rule file, or an architecture lint rule.
3. **Compound Team Velocity**: By treating recurring mistakes as defects in the development harness rather than one-off annoyances, the system becomes noticeably more competent over time.

---

## Related Notes

- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Designing runtime harnesses that feed versioned instructions, linters, and test feedback directly to agents.
- **[[Constraint Saturation and Rule Oscillation in Coding Agents]]**: Why dumping too many rules into a prompt causes agents to thrash, and how to keep instruction sets lean.
- **[[Negative Knowledge and Explicit Architectural Dissents]]**: How failure analysis builds an explicit record of rejected patterns and architectural boundaries.
- **[[Testing in the Model, Agent, LLM Era]]**: Using deterministic test suites as the fast inner loop that validates functional correctness.
- **[[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]]**: The practical decision matrix for fixing buggy agent code versus updating prompt specifications.
- **[[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]]**: Using LLM reviewers to enforce nuanced architectural guidelines before code is merged.
- **[[How LLM Systems Build Context]]**: Managing working memory and prompt overhead when supplying instructions to agents.
