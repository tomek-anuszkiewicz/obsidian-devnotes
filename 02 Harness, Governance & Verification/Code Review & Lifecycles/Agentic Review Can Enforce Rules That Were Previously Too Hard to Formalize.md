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

In traditional software engineering, quality rules were strictly divided into two categories:

1. **Rules that can be coded deterministically**: Typecheckers, linters, and unit tests. If a rule can be expressed as a regex, an AST visitor, or a Boolean assertion, CI checks it instantly and cheaply.
2. **Rules that live in human memory**: Architectural principles like *"keep domain models free of database concerns"*, *"avoid premature abstractions"*, or *"ensure errors fail safely"*. These rules were written down in wiki pages or architectural decision records, but their enforcement depended entirely on whether an exhausted human reviewer remembered them during a pull request.

Coding agents introduce a third category: **natural-language executable policies**. 

By using language models to evaluate code diffs against written guidelines, teams turn subjective architectural taste into continuously enforced rules—checking for boundary leaks, hidden coupling, and semantic intent that static analyzers cannot detect.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      THE 3-TIER VERIFICATION CONTINUUM                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
[ TIER 1: DETERMINISTIC ]     [ TIER 2: SEMANTIC AGENTS ]    [ TIER 3: HUMAN JUDGMENT ]
• Compilers & Typecheckers    • Natural-language guidelines   • Strategic product trade-offs
• Linters & AST Analyzers     • Architectural boundary leaks  • Risk tolerance & exceptions
• Unit & Integration Tests    • Unnecessary abstractions      • Unclear business intent
"Cheap, instant, reproducible" "Context-aware architectural    "Ultimate decision maker"
                                intent & domain invariants"
```

---

## Core Invariants

1. **Never Replace Cheap Deterministic Tests with LLMs**: If an invariant can be validated with a compiler type, a linter, or a unit test (`assert(price >= 0)`), keep it deterministic. LLMs should handle the nuanced, contextual rules that are too difficult or brittle to code into static analyzers (see [[Testing in the Model, Agent, LLM Era|deterministic verification versus semantic review]]).
2. **Review Agents as Living Documentation Runtimes**: Architectural documentation has historically been dead prose. Agents act as the active execution engine that checks every pull request against your team's documented principles before human review.
3. **Intent Over Syntax (The Semantic Gap)**: Static linters check whether Module A imports Module B's package. An agent catches the deeper violation: Module A copying Module B's raw database schema or table names, creating tight coupling while passing all mechanical linter checks.
4. **The Escalation Flywheel**: When an agent repeatedly catches the same architectural violation across multiple pull requests, do not burn tokens checking it forever. Promote the rule into a deterministic linter or custom architecture test.
5. **Ephemeral Investigation vs. Permanent Tests**: Agents can write temporary, disposable test scripts during review to verify suspected race conditions or cache leaks, promoting them to the permanent test suite only if a real defect is proven.

---

## 1. Why Traditional Linters Fall Short

Static analysis tools excel at checking concrete syntax:
- *Does this file have unused imports?*
- *Are all public methods documented?*
- *Does this variable follow camelCase naming?*
- *Does this query have a parameter placeholder to prevent SQL injection?*

However, the most expensive bugs and architectural decay stem from **semantic violations** that static linters cannot understand:
- *"Do not create a generic wrapper framework for a problem that occurs in exactly one place."*
- *"Transport controllers should be thin adapters; do not put orchestration logic here, but do not create pointless single-line service interfaces either."*
- *"Business validation must remain explicit in domain handlers rather than buried in database triggers or ORM lifecycle hooks."*
- *"Do not introduce speculative fields or unrequested configuration flags."*

Writing custom AST linters for these rules is notoriously difficult and brittle. As a result, enforcement historically depended on senior engineers catching them in review—a process that inevitably degrades under deadline pressure, accelerating [[Software Decay and the Hidden Costs of Frictionless AI Code|uncontrolled code sprawl]].

---

## 2. Living Documentation as Executable Policy

Instead of leaving architectural guidelines as passive documents in a repository folder, an agent harness injects them as active review criteria:

```text
docs/
├── architecture/boundaries.md
├── domain/invariants.md
├── conventions/error-handling.md
└── adrs/
```

During pull request review, the semantic review agent checks:
1. **Scope the Diff**: What components, data paths, and layers does this pull request modify?
2. **Retrieve Relevant Policies**: Load the specific architectural guidelines and ADRs that govern those components.
3. **Evaluate Intent**: Does the code violate the underlying architectural principle, even if it compiles and passes existing unit tests?
4. **Provide Contextual Feedback**: Explain *why* the design conflicts with team conventions and reference the specific ADR or guideline.

This turns architectural documentation into an active guardrail that protects code quality on every turn.

---

## 3. The Semantic Gap: Real-World Examples

### Case 1: The Database Shadow Leak
- **Deterministic Check**: A dependency analyzer checks module imports. It reports clean: `Billing` does not reference `Inventory.Data`.
- **Semantic Reality**: The developer in `Billing` wrote a direct SQL query against the `inventory_items` table, bypassing the inventory service contract. The dependency linter reports green because no library reference was added; the semantic review agent flags the direct database coupling immediately.

### Case 2: Malicious Compliance
- **Deterministic Check**: A unit test asserts `assert(invoiceTotal >= 0)`.
- **Semantic Reality**: To make the test pass, the code added `invoiceTotal = Math.max(0, calculatedTotal)`. The technical test passes, but the code silently conceals negative invoices caused by faulty discount logic. A static analyzer sees a valid math function; the review agent questions the business validity of clamping an invalid financial calculation.

---

## 4. The Escalation Flywheel: Turning Agent Findings into Deterministic Rules

Agentic review should not be a permanent tax on your token budget. It acts as an exploratory incubator for new deterministic rules:

```text
        [ Human Engineer Defines Semantic Principle ]
                             │
                             ▼
        [ Review Agent Enforces Principle in Pull Requests ]
                             │
                             ▼
        [ Violation Pattern Becomes Stable & Predictable ]
                             │
                             ▼
    [ ESCALATION: Convert Rule to Custom Linter or Architecture Test ]
                             │
                             ▼
        [ Agent Freed to Focus on Newer, Subtle Edge Cases ]
```

When an agent catches five pull requests violating the same boundary, stop asking the LLM to find it. Write a deterministic architecture test or linter rule. The agent is your scout; the compiler and linter are your permanent border guards (see [[Learning Coding Agents Through Failure-Driven Instructions|failure-driven instruction updates]]).

---

## Practical Rules for Teams

1. **Keep simple checks deterministic**: Never use an LLM to check code formatting, indentation, or type correctness.
2. **Focus prompts on architectural intent**: Instruct review agents to look for boundary leaks, premature abstractions, and unhandled failure states.
3. **Escalate recurring findings**: Turn frequently caught violations into deterministic tests to save tokens and speed up CI.
4. **Reference documented decisions**: When an agent flags a violation, have it cite the relevant ADR or architectural guideline so the author understands the context.

---

## Related Notes

- **[[LLMs as a Code Review Team]]**: Configuring specialized review personas to systematically evaluate pull requests.
- **[[Reviewing AI-Generated Code]]**: How human reviewers focus on domain intent while machines handle mechanical and semantic checks.
- **[[Testing in the Model, Agent, LLM Era]]**: The foundational balance between deterministic test oracles and semantic guidelines.
- **[[Agent Advantage - Relentless, Methodical Work]]**: Why inexhaustible procedural consistency makes agents ideal for checking complex rule sets.
- **[[Learning Coding Agents Through Failure-Driven Instructions]]**: How post-incident lessons are codified into living repository guidelines.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: Using semantic review gates to prevent unmonitored code generation from degrading system health.
