---
title: Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize
tags:
  - ai-agents
  - code-review
  - software-engineering
  - quality-assurance
  - static-analysis
  - compliance
  - review
aliases:
  - Natural-Language Rules as Executable Policies
  - Agentic Review Rules
  - Semantic Code Review
  - The Semantic Verification Continuum
  - Human Review Intuition as Executable Policy
---

# Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize

> [!IMPORTANT]
> **The Semantic Verification Continuum**: Historically, engineering rules were bifurcated: either a rule could be precisely coded into a deterministic compiler/linter check, or it lived as unenforced folklore in documentation, dependent on human vigilance. Coding agents introduce a third operational layer: **natural-language executable policies**. Semantic review agents transform subjective human intuition into continuously enforced organizational invariants, operating directly on architectural intent, boundary leakage, and domain semantics.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      THE 3-TIER VERIFICATION CONTINUUM                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
[ TIER 1: DETERMINISTIC ]     [ TIER 2: SEMANTIC AGENT ]     [ TIER 3: HUMAN JUDGMENT ]
- Compilers & Typecheckers    - Natural language policies     - Strategic trade-offs
- Linters & AST Analyzers     - Architectural boundary leaks  - Business risk tolerance
- Unit & Mutation Tests       - Speculative abstractions      - Conflicting priorities
"Cheap, exact, reproducible"  "Context-aware intent & taste"  "Ultimate authority"
```

---

## Executive Summary & Core Architectural Invariants

1. **Human Attention Was the Missing Runtime**: Teams have always authored architecture principles ("prefer explicit dependencies", "do not leak persistence into domain", "avoid premature abstractions"). Without agents, these documents were dead prose; their execution depended entirely on whether a fatigued human remembered them. Agents serve as the missing runtime that evaluates every diff against the full policy corpus.
2. **The Verification Continuum Protocol**:
   - *If a rule can be cheaply and deterministically coded* $\rightarrow$ **Encode it in compilers, types, or tests** (never replace cheap tests with expensive, stochastic LLM prompts).
   - *If a rule is semantically rich and too costly to formalize* $\rightarrow$ **Delegate enforcement to review agents**.
   - *If an agent repeatedly catches the same recurring violation* $\rightarrow$ **Promote it into a deterministic architecture test**.
   - *If the resolution requires business trade-offs or strategic context* $\rightarrow$ **Escalate to the human software architect**.
3. **Intent Over Syntax (The Semantic Gap)**: A deterministic architecture test verifies that Module A does not reference Module B's package. An agent catches the deeper violation: Module A copying Module B's internal database layout, violating boundary semantics while passing all mechanical tests.
4. **Relentlessness as the Great Equalizer**: Senior architects know twenty principles, but fatigue causes them to evaluate only three under Friday afternoon pressure. Agents relentlessly apply all twenty checks against a 150-file diff without degrading attention.
5. **From Ephemeral Experiments to Permanent Oracles**: Agents can generate temporary, hypothesis-driven tests to verify race conditions or cache corruptions during review, promoting the test to the permanent regression suite only if an invariant violation is proven.

---

## 1. The Breakdown of Traditional Rule Formalization

Traditional software quality automation excels when an invariant can be expressed as a binary mathematical constraint:
```text
- Domain must not import Infrastructure.
- Every public endpoint must validate authentication context.
- Transaction amount must be non-negative: assert(amount >= 0).
- All command handlers must implement the dispatch contract.
```

These rules map cleanly to compiler types, static analyzers, linters, and unit tests.

However, the most critical architectural failures in large codebases stem from **semantic violations** that resist deterministic formalization:
- *"Do not introduce an abstraction unless it represents a genuine domain boundary."*
- *"Controllers should remain thin adapters, but trivial request translation does not warrant an extra indirection layer."*
- *"Business rules must remain visible in pure domain logic rather than buried inside database triggers or infrastructure helpers."*
- *"Do not build a generic framework for a problem that occurs exactly once."*

An experienced architect spots these anti-patterns immediately, but writing a deterministic AST linter to detect them requires an impractically complex semantic graph. As a result, enforcement historically decayed into oral tradition.

---

## 2. Natural-Language Documents as Executable Policies

Rather than leaving architecture guidelines as passive markdown files in `docs/architecture/`, an agentic harness injects them as active operational constraints:

```text
docs/
├── architecture/principles.md
├── domain/invariants.md
├── security/guidelines.md
└── adrs/
```

During every pull-request evaluation, the architecture reviewer evaluates:
```text
1. Identify code modifications in the diff.
2. Cross-reference changes against active architectural principles and ADRs.
3. Determine whether a semantic boundary is violated (even if syntax tests pass).
4. Check for documented historical exceptions.
5. Provide precise line citations and explain the architectural trade-off.
```

This transforms living documentation into an **active semantic firewall**, bridging the gap between passive human documentation and rigid compiler checks.

---

## 3. The Semantic Gap: Why AST Linters Miss Intent

The true power of agentic review emerges when an implementation satisfies the letter of the law while violating its spirit:

### Case 1: The Database Shadow Leak
- **Deterministic Test**: An architecture analyzer checks package imports and reports green: `Billing` does not reference `Inventory.Data`.
- **Semantic Reality**: The agent notices that `Billing` duplicated the exact raw SQL schema and column names of the `Inventory` database, binding the two services at the storage layer while bypassing the module interface. The deterministic linter is blind; the agent flags the coupling immediately.

### Case 2: The Malicious Compliance Guard
- **Deterministic Test**: A unit test asserts `assert(price >= 0)`.
- **Semantic Reality**: To make the test pass, an implementation added `price = Math.max(0, calculatedPrice)`. The technical test passes, but the code silently conceals negative invoice calculations caused by upstream discount bugs. The semantic reviewer questions the business validity of clamping an impossible financial state.

---

## 4. The Two-Way Rule Escalation Cycle

Agentic review does not eliminate deterministic testing; it feeds it:

```text
        [ Human Architect Authors Informal Semantic Principle ]
                                  │
                                  ▼
             [ Review Agent Relentlessly Enforces in PRs ]
                                  │
                                  ▼
        [ Violation Pattern Becomes Stable & Predictable ]
                                  │
                                  ▼
      [ ESCALATION: Engineer Converts Rule to Deterministic Test / AST Rule ]
                                  │
                                  ▼
      [ Agent Freed to Monitor Newer, More Subtle Invariants ]
```

When an agent repeatedly catches developers or other agents violating the same structural boundary, the team should not burn LLM tokens checking it forever. The team formalizes the stabilized check into an automated linter or architecture test, continually pushing deterministic certainty outward while the agent explores emerging semantic debt.

---

## 5. Ephemeral Hypothesis Testing vs. Permanent Specs

Traditional engineering conflates *investigating a defect* with *maintaining a permanent test*:
- An engineer who suspects a concurrency race must write a unit test, wire up mocks, commit it, and maintain it across future framework upgrades.
- In contrast, an agentic reviewer creates **ephemeral investigative harnesses**:
  ```text
  Suspected Concurrency Leak Detected in PR
                      │
                      ▼
       Agent Synthesizes Ephemeral Fuzz Harness
                      │
                      ▼
     Runs 10,000 Iterations Under Virtualized Clocks
                      │
           ┌──────────┴──────────┐
           ▼                     ▼
     [ No Defect Found ]    [ Race Reproduced ]
     Harness Discarded      Promoted to Permanent Regression Test
  ```
This separation between **exploratory instruments** and **permanent specification assets** keeps repository test suites lean, deterministic, and free of sprawling speculative test mocks.

---

## Relationship to the Knowledge Graph

- **[[LLMs as a Code Review Team]]**: Architectural topologies for routing diffs to specialized semantic and deterministic review agents.
- **[[Reviewing AI-Generated Code]]**: Human-centric heuristics for inspecting business assumptions and hidden coupling that escape linters.
- **[[Testing in the Model, Agent, LLM Era]]**: The foundational duality pairing hard deterministic oracles with soft semantic living specifications.
- **[[Agent Advantage -  Relentless, Methodical Work]]**: Why tireless agent execution transforms unenforced guidelines into continuous automated checks.
- **[[Learning Coding Agents Through Failure-Driven Instructions]]**: How post-incident lessons are codified into living review policies.
- **[[Software Entropy and the Zero-Friction Trap]]**: Preventing unreviewed code accumulation from degrading repository maintainability.
