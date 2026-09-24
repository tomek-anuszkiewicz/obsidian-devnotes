---
title: Software Decay and the Hidden Costs of Frictionless AI Code
tags:
  - software-architecture
  - ai-agents
  - software-entropy
  - code-maintainability
  - modularity
  - blast-radius
  - code-duplication
  - refactoring
aliases:
  - Software Entropy and the "Zero-Friction" Trap
  - Software Entropy and the Zero-Friction Trap
  - Software Entropy & The "Zero-Friction" Trap
  - The Human Friction Advantage
  - Mechanical Isolation for AI Agents
  - Zero-Friction Coding Trap
  - The Ghost Ship Codebase
  - Re-evaluating Duplication in AI Era
---

# Software Decay and the Hidden Costs of Frictionless AI Code

## The effort of writing code used to slow us down

Writing code by hand takes time. So does reviewing a pull request that touches 40 files or following a database query through several layers of wrappers. That effort often made an engineer pause before adding another abstraction. Is a 20-line database read really worth three factory classes, an interface, two builders, an event publisher, and 300 lines of supporting code? Often the engineer wrote the 20-line function and moved on.

An agent has no such physical limit. It can produce 500 lines of scaffolding, dynamic proxy wrappers, and dependency-injection wiring as readily as it can produce a five-line utility. The time and effort of generating code no longer provide the same brake on unnecessary files and abstractions. Without explicit limits in the repository, that code can accumulate quickly.

The proposed response is mechanical: keep operations in their own files, limit file size, and restrict how many files an agent can change in one task. These rules give the team a point at which to stop and review a change that is spreading (see [[Designing Software for AI Agents]] and [[Executable Architecture Tests for Coding Agent Guardrails]]).

---

## A working UI does not tell you much about a backend

It is easy to feel productive when building a landing page or UI prototype with an agent. If a margin is off by four pixels, an asset loads 50 milliseconds later, or an error appears as a generic alert, the page still works. You can open the browser, click around, and see the result immediately.

Backend failures can be much harder to spot that way. In a distributed service, a financial ledger, a transactional data pipeline, or a busy network client, a silent type conversion, a missing row-level lock, a query without an index inside a loop, or an unhandled timeout may remain hidden until production load exposes it. An extra layer of indirection can also add cost on a hot CPU path.

An agent focused on making a failing integration test pass may add a conditional inside a loop, wrap an existing service, or spread mutable state across three new files. The test goes green, but the code is harder to understand and the underlying problem may remain. That is why backend changes need architectural boundaries as well as a passing test.

---

## When the team can no longer explain its own code

Imagine agents adding 50,000 lines across 300 files in a few weeks while the team stops reviewing the diffs closely. The system keeps running, but nobody can say where a state transition happens or trace a request through the components. It is a codebase without someone who can confidently steer it.

Then a deadlock, connection-pool exhaustion, or state corruption appears at 2 a.m. An engineer has to trace the failure through perhaps 200 tangled files. Asking the agent to sort it out may also fail: its context fills with overlapping wrappers, contradictory assumptions, and code written in earlier sessions. The team may find itself waiting for a future model to untangle the system before its runway runs out; failing that, it may have to discard the codebase.

Technical leads can delegate the typing and much of the implementation. They still need to understand the system topology: its component boundaries, interfaces, and the lifetime of its state. Those relationships should remain simple enough to sketch on a whiteboard from memory.

---

## Reconsider where duplication is cheaper than sharing

DRY has long pushed us toward shared code. Two ordinary human costs helped motivate that approach: people dislike repeatedly typing the same boilerplate, and they can forget to update all three copies of a business rule.

Agents change both costs. An agent can search for copies with AST queries or semantic search and update them together. Writing 40 lines of explicit logic in a particular endpoint also costs little typing time. That makes localized duplication a more attractive choice than it used to be.

Shared code has a cost of its own. If three distinct operations use one generic helper or base service, a change for Feature A can affect Feature B. The engineer may then add a flag to the helper to keep both behaviors working. When each operation keeps its business logic in its own file, a change to one operation has a smaller path through the code and is less likely to disturb the others.

This is the case for preferring two clear, local implementations over a clever abstraction that couples unrelated operations (see [[Internal NuGet Packages vs Agent-Generated Code]] and [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]). It gives both the engineer and the agent a smaller piece of code to inspect when something changes.

---

## Agents learned from code written for human constraints

Agents produce code from examples written by people. Many of those examples use inheritance trees, reflection, dependency-injection containers, and metaprogramming. Such patterns can reduce repetitive work for a human developer.

Without clear instructions, an agent may reach for the same patterns: an abstract factory, a generic base class, or a separate utility used in one place. Yet the agent does not need to save its own keystrokes. Later, when it has to navigate that code through a limited context window, each additional level of indirection makes the behavior harder to follow. Tell the agent explicitly when you want flat, direct code instead of those abstractions.

---

## Put the limits in CI

Advice such as “keep classes focused” and “avoid touching too many files” is easy for an agent to ignore while it is trying to complete a task. A check in CI makes the limit visible and stops the change when it crosses it (see [[Executable Architecture Tests for Coding Agent Guardrails]] and [[Agentic Coding Harness and Controlled Development Workflows]]). The proposed rules are one operation per file, a file-length limit, and a small budget for files changed by a task.

### One operation per file

Keep each command, query, event handler, or business transaction in a dedicated file. If the task concerns `ProcessPayment.ts`, the agent should have no reason to edit `CancelSubscription.ts`. Keeping those operations apart reduces the chance that a payment change also changes cancellation behavior.

### A file-length limit

Set a maximum file length with a linter or static analysis. The proposed range is 500–800 lines; the example below fails CI above 500 nonblank, noncomment lines. This stops an agent from continually adding cases to one oversized file and pushes it toward smaller, focused routines.

For example, an ESLint rule in `.eslintrc.json`:

```json
{
  "rules": {
    "max-lines": [
      "error",
      {
        "max": 500,
        "skipBlankLines": true,
        "skipComments": true
      }
    ]
  }
}
```

### A budget for changed files

For an ordinary agent task, allow one implementation file and its test. If a feature needs changes across ten files, the lead first breaks it into smaller, decoupled tasks. A CI check can enforce a two-file budget:

```bash
#!/usr/bin/env bash
# ci-touchpoint-budget.sh: fail if the PR changes more than two files

MAX_FILES=2
MODIFIED_FILES=$(git diff --name-only origin/main...HEAD | wc -l | tr -d ' ')

if [ "$MODIFIED_FILES" -gt "$MAX_FILES" ]; then
    echo "ERROR: Touchpoint budget exceeded. Agent touched $MODIFIED_FILES files (Max: $MAX_FILES)."
    echo "Decompose this task into isolated, per-operation changes."
    exit 1
fi

echo "Touchpoint budget valid: $MODIFIED_FILES file(s) modified."
```

---

## The same lack of fatigue makes refactoring easier

The low cost of generating code can also work in our favor. Picture an engineer debugging an edge case at 5 p.m. on Friday. Adding `if (user.isSpecialCase)` to a 400-line function, changing a global singleton, patching local state, or leaving a `TODO` for later can be tempting. The proper fix might involve 25 call sites, three DTOs, database migrations, and a dozen integration tests. That is a great deal of mechanical work under time pressure.

An agent does not tire of editing those files. It can update 30 call sites and their tests, or rewrite a subsystem to use explicit types in place of unstructured dictionaries. It has no reason to choose a quick patch merely to finish the day.

With clear architectural constraints, thorough tests, and type checking, that capacity can help remove old workarounds. The agent can make the broad, consistent change that a human team might postpone because of the effort involved (see [[Refactoring Legacy Systems with AI Agents]] and [[AI Changes the Economics of Technical Debt]]).

---

## Rules for the team

1. **Check the boundaries in CI.** Enforce file-length limits, dependency boundaries with a tool such as dependency-cruiser, and checks on how many files a task changes.
2. **Keep ordinary agent tasks small.** Aim for one operation file and its test. Break changes spanning many files into separate tasks.
3. **Allow local duplication when it keeps operations separate.** Two straightforward 30-line functions can be easier to change than one 60-line function full of branches for different callers.
4. **Ask for the underlying fix.** When a bug comes from the data flow, have the agent correct that flow and update affected call sites instead of adding a conditional that only hides the failure.

---

## Related notes

- **[[Designing Software for AI Agents]]** — Structuring code so agents can inspect, change, and test it without spreading changes across the repository.
- **[[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]** — How metaprogramming and hidden behavior make code harder for an agent to follow.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]** — How repository layout and component boundaries may change when agents write much of the code.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]** — Using focused Markdown documentation to keep an agent on task.
- **[[Refactoring Legacy Systems with AI Agents]]** — Using an agent to carry out broad code migrations that take substantial manual effort.
- **[[Negative Knowledge and Explicit Architectural Dissents]]** — Recording rejected designs and failed approaches so agents do not repeat them.
- **[[AI Changes the Economics of Technical Debt]]** — How cheap code generation can accelerate decay without discipline in the repository.
