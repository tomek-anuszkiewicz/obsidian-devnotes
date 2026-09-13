---
title: In-Flight Documentation as the Primary Framework for Coding Agents
tags:
  - software-architecture
  - documentation
  - ai-agents
  - agentic-coding
  - developer-experience
  - context-engineering
aliases:
  - In-Flight Documentation Generation
  - Documentation as Agent Framework
  - Deterministic Agent Scaffolding
  - Generating Documentation During Code Writing
  - Documentation as Code for the Agent
  - Markdown as the Highest-Level Source Code
  - Documentation as AI Compiler Input
  - Two-Stage Agentic Compilation Pipeline
  - Source Code as Intermediate Representation
  - Operation Cards
  - Iterative Specification Calibration
---

# In-Flight Documentation as the Primary Framework for Coding Agents

## Core Thesis

In traditional software development, documentation was usually an afterthought. Developers rarely enjoyed writing design docs after spending days writing code, so documentation lagged behind reality or was abandoned altogether. Systems relied on framework conventions, class hierarchies, and tribal knowledge to keep developers aligned.

When building systems with AI coding agents, that workflow inverts:

1. **Documentation is generated in-flight**: Because the agent already holds the architecture, variable names, and edge cases in its working context while writing code, having it generate companion documentation costs almost zero developer effort.
2. **Markdown replaces framework boilerplate as the primary scaffold**: Large language models navigate concise markdown specs and explicit contracts far more reliably than deep OOP inheritance trees or opaque framework reflection (see [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]).
3. **Specs stop probabilistic drift**: Giving an agent an explicit blueprint turns what would be open-ended guesswork into bounded, predictable code generation.
4. **Context efficiency beats file dumping**: Handing an agent a 40-line specification card uses a fraction of the context window compared to dumping twenty raw source files into the prompt to let the model guess the system's intent.

---

## Markdown as High-Level Source Code: The Two-Stage Build Pipeline

In an agentic workflow, structured markdown acts like high-level source code, while the generated code functions as an intermediate representation:

```text
TRADITIONAL BUILD:
Source Code ──► Compiler / Type Checker ──► Binary / Executable

AGENTIC WORKFLOW (TWO-STAGE PIPELINE):
Markdown Spec ──► LLM Agent ──► Source Code ──► Compiler / Tests ──► Working System
[High-Level Intent] [Front-End Engine] [Intermediate Code] [Deterministic Oracle] [Deployable Service]
```

Under this workflow:

1. **Source Code as Intermediate Artifact**: In classical engineering, source code is the primary artifact written by humans. With coding agents, code is frequently synthesized by the model, verified by tools, and inspected by humans.
2. **Writing for the Model**: The engineer writes or refines markdown specs not as static documentation, but as explicit instructions for the agent. The clearer the rules around state, boundaries, and errors, the cleaner the generated code.
3. **Updating Systems at the Spec Level**: When business logic or workflow rules change, the cleanest path is often updating the markdown specification and letting the agent regenerate or refactor the implementation, rather than manually hacking through boilerplate.
4. **Keeping Humans in the Loop**: Reading concise spec cards and running focused code reviews is how human engineers keep a firm mental model of the codebase without having to hand-type every line (see [[Reviewing AI-Generated Code]]).

---

## Why This Isn't the 4GL or Executable UML Trap

Every developer who remembers Fourth-Generation Languages (4GL), CASE tools, or Executable UML from past decades is rightly skeptical of claims that "specifications replace code."

Those historical attempts collapsed because they tried to make diagrams or natural language describe every single atomic operation—memory allocation, loop counter increments, null checks, and error unwinding. When a visual tool or natural language spec is forced to specify every minute detail, it turns into a clumsy, untyped programming language without a proper compiler.

The agentic approach avoids this trap for two reasons:

```text
┌────────────────────────────────────────────────────────────────────────┐
│               HOW SPECS AND VERIFICATION WORK TOGETHER                 │
│                                                                        │
│   1. HUMAN ARCHITECT                                                   │
│      Defines system boundaries, performance limits, and domain goals.  │
│                         │                                              │
│                         ▼                                              │
│   2. MARKDOWN SPECIFICATION (Intent & Constraints)                     │
│      Defines invariants, allowed dependencies, and failure contracts.  │
│      Never dictates trivial syntax or obvious loop mechanics.          │
│                         │                                              │
│                         ▼                                              │
│   3. AGENT IMPLEMENTATION                                              │
│      Synthesizes idiomatic code using language and library knowledge.   │
│                         │                                              │
│                         ▼                                              │
│   4. DETERMINISTIC TEST ORACLE & COMPILER                              │
│      Compiler checks types and syntax; test suite verifies contracts.  │
│      Fails produce concrete errors that steer the agent back on track. │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Markdown describes boundaries, not syntax**: The specification doesn't explain how to loop through an array or serialize JSON. The LLM already knows language syntax, standard libraries, and standard idioms. The spec only needs to define domain invariants, allowed dependencies, performance budgets, and error contracts.
2. **The test suite provides the hard floor**: A markdown spec on its own can still lead to hallucinations. The only reason specs work as reliable scaffolding is that the resulting code is checked by deterministic compilers, linters, and test suites (see [[Testing in the Model, Agent, LLM Era|automated test verification]]). If the agent's code violates a contract, the test fails, and the error output pulls the model back into alignment.

---

## The Reality: You Don't Write Specs Upfront in a Vacuum

A common misconception is that agentic development requires writing pristine, exhaustive specifications before writing any code.

In real-world software engineering, nobody understands every edge case upfront. When building an intricate data pipeline, a stateful event handler, or a low-latency network client, intent crystallizes through experimentation:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                 ITERATIVE SPECIFICATION WORKFLOW                       │
│                                                                        │
│   1. EXPLORATION                                                       │
│      Tackle the problem hands-on with targeted prompts and quick tests.│
│                         │                                              │
│                         ▼                                              │
│   2. WORKING IMPLEMENTATION                                            │
│      Get the code running, verify edge cases, and ensure tests pass.   │
│                         │                                              │
│                         ▼                                              │
│   3. CAPTURE IN-FLIGHT (Freeze the Knowledge)                          │
│      Have the agent generate an Operation Card capturing the rules,   │
│      dependencies, and decisions discovered during implementation.    │
│                         │                                              │
│                         ▼                                              │
│   4. CALIBRATION CHECK                                                 │
│      Hand the card to a fresh agent session. Can it modify or extend   │
│      the component without breaking invariants? If not, sharpen rules. │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Explore first when the path is unclear**: When building something unfamiliar, steer the agent through quick iterative prompts, inspect the code directly, and uncover hidden edge cases.
2. **Freeze the solution immediately**: Once the code works and the design stabilizes, immediately instruct the agent to synthesize an Operation Card. If you skip this, the hard-won insights remain trapped in transient chat logs, and the next agent session will guess the rules from scratch.
3. **Calibrate the spec**: The true test of a specification is whether another agent—or another engineer—can safely modify the component six months later using just that card and the tests.

---

## Token Economics: Concise Cards vs. Sprawling Context

In agentic development, context window space and model attention are practical bottlenecks:

| Approach | Context Ingestion | Attention Overhead | Drift Risk |
| :--- | :--- | :--- | :--- |
| **Dumping Source Files** | 15–30 files (15,000–40,000 tokens) | High (needle-in-a-haystack, model misses subtle details) | High (model mimics inconsistent local quirks) |
| **In-Flight Spec Card** | 1 spec card (300–800 tokens) + target file | Low (clean focus on explicit contracts) | Minimal (stays strictly within documented boundaries) |

Feeding the model a compact spec card instead of dozens of loosely related source files produces:
- Faster agent response times,
- Substantially lower token costs,
- Higher reasoning accuracy by avoiding attention dilution (see [[How Context Narrows an AI's Solution Space]]).

---

## Anatomy of a Real-World Operation Card

An effective in-flight doc doesn't duplicate the source code line for line. It records **purpose, boundary invariants, file touchpoints, dependencies, and failure handling**:

```markdown
### Operation: ProcessPaymentSettlement

**Purpose**: Orchestrates credit card settlement against external payment gateways and records ledger journal entries.

**Boundary Invariants**:
- Idempotent: Safe to retry with the same `TransactionId`.
- No direct database writes to Ledger tables (must emit `SettlementCompleted` domain event).
- External gateway timeout limit: 5000ms.

**File Touchpoints**:
- Orchestrator: `billing/settlement_coordinator`
- External Client: `billing/gateways/stripe_client`
- Event Contract: `billing/events/settlement_completed`
- Verification Suite: `tests/billing/settlement_coordinator_test`

**Allowed Dependencies**:
- Permitted: Gateway client, Clock service, Structured logger.
- Strictly Forbidden: Shopping cart storage, Direct user session store.

**Failure Handling**:
- Timeout -> Mark transaction as `PendingReconciliation`, emit operational metric alert.
- Validation failure -> Reject immediately with `DomainValidationError` (do not retry).
```

When an agent needs to touch this component later, loading this single card gives it the exact boundaries it needs without scanning five directories.

---

## Practical Rules for Engineering Teams

1. **Never write operational docs by hand**: Instruct the agent to generate the spec card the moment the implementation stabilizes.
2. **Use markdown cards as structural guardrails**: Treat structured docs as the primary guide for where code belongs, what dependencies are allowed, and what errors to expect.
3. **Pair specs with automated tests**: Markdown sets the intent; the test suite provides the hard pass/fail verification that keeps the agent honest.
4. **Protect your token budget**: Feed agents compact architectural cards rather than dumping the whole repository into context.
5. **Keep future changes safe from entropy**: Documenting "what must not break" alongside new code prevents future agent sessions from quietly unraveling design choices (see [[Software Entropy and the Zero-Friction Trap|controlling generative code entropy]]).

---

## Relationship to the Knowledge Graph

- **[[Testing in the Model, Agent, LLM Era]]**: Explains how deterministic test suites serve as the non-negotiable verification gate backing up markdown specifications.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: Details how codebase layout, file boundaries, and explicit contracts adapt when agents become the primary readers and writers of code.
- **[[Reviewing AI-Generated Code]]**: How engineers use concise in-flight documentation and targeted diff reviews to maintain deep systems understanding.
- **[[AI-Generated Architectural Documentation from Code]]**: The reverse process—extracting high-level architectural maps from existing codebases to bootstrap initial specs.
- **[[Comments May Become More Valuable in AI-Generated Code]]**: Why non-derivable business intent belongs in code comments and companion markdown cards.
- **[[Software Entropy and the Zero-Friction Trap]]**: Using standardized spec cards as intentional engineering discipline to stop sprawling agent-generated complexity.
- **[[Designing Software for AI Agents]]**: Core architectural patterns that make code discoverable, isolated, and simple for agents to modify safely.
