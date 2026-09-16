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

## Core Principles & Architecture

In traditional software development, writing documentation is usually an afterthought that decays the moment it hits the repository. Most engineers would rather build systems than spend Friday afternoon drafting static design docs for code they finished on Wednesday. As a result, documentation falls behind reality, and engineering teams fall back on tribal knowledge, implicit framework conventions, and complex class hierarchies to keep everyone aligned.

When you integrate AI coding agents into your daily engineering workflow, that dynamic completely flips:

1. **Documentation is generated in-flight**: While an agent writes an implementation, its context window is already packed with the relevant Abstract Syntax Trees (ASTs), type definitions, boundary conditions, and edge cases. Asking the model to summarize those design decisions into an operational specification right then costs almost zero human time and negligible compute.
2. **Markdown replaces framework boilerplate as the primary scaffold**: Large language models navigate concise, structured markdown specifications and explicit contracts far more reliably than deep object-oriented inheritance trees, dynamic reflection, or framework metaclass magic (see [[The Cost of Hidden Abstractions in Agent-Maintained Code]]).
3. **Specs stop probabilistic drift**: Left unconstrained, LLMs exhibit stochastic behavior—they hallucinate utility functions, pull in unapproved third-party dependencies, and drift away from architectural patterns. An explicit markdown spec narrows the solution space, turning what would be open-ended guesswork into bounded, predictable code generation.
4. **Context efficiency beats file dumping**: Handing an agent a 40-line specification card consumes a tiny fraction of its context window compared to dumping twenty raw source files into the prompt and asking the model to infer system intent from implementation details.

---

## Markdown as High-Level Source Code: The Two-Stage Build Pipeline

In an agent-driven workflow, structured markdown serves as your high-level source code, while the generated code functions as an intermediate representation (IR)—similar to how a compiler treats bytecode before lowering it to machine instructions:

```text
TRADITIONAL BUILD:
Source Code ──► Compiler / Type Checker ──► Binary / Executable

AGENTIC WORKFLOW (TWO-STAGE PIPELINE):
Markdown Spec ──► LLM Agent ──► Source Code ──► Compiler / Tests ──► Working System
[High-Level Intent] [Front-End Engine] [Intermediate Code] [Deterministic Oracle] [Deployable Service]
```

Under this workflow:

1. **Source Code as an Intermediate Artifact**: In traditional engineering, the source code is the primary artifact written and maintained by human hands. With coding agents, the code is synthesized by the model, verified by automated test harnesses, and audited by engineers.
2. **Writing for the Model**: Engineers author or refine markdown specifications not as archival records for human readers, but as operational constraints for the agent. The clearer your definitions around state mutations, system boundaries, and error recovery, the cleaner the synthesized code.
3. **Updating Systems at the Spec Level**: When business logic or operational rules shift, the fastest path forward is updating the markdown specification and letting the agent regenerate or refactor the implementation against existing test suites, rather than manually chasing boilerplate across half a dozen files.
4. **Keeping Humans in the Loop**: Reviewing concise spec cards and targeted diffs allows lead engineers to maintain a crisp, accurate mental model of system architecture without needing to manually write every line of plumbing (see [[Reviewing AI-Generated Code]]).

---

## Why This Isn't the 4GL or Executable UML Trap

Engineers who lived through Fourth-Generation Languages (4GL), CASE tools, or Executable UML in decades past are rightly skeptical of claims that "specifications can replace code."

Those historical efforts failed because they attempted to map natural language or rigid visual diagrams directly down to atomic runtime mechanics—loop increments, dynamic memory allocation, null pointer checks, and stack unwinding. When a visual diagram or pseudo-English spec is forced to dictate every low-level instruction, it degenerates into a clumsy, unreadable, untyped programming language that lacks proper debugging tools and a real compiler.

The agentic model avoids this failure mode for two practical reasons:

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

1. **Markdown describes boundaries, not syntax**: The specification does not waste tokens explaining how to iterate over an array, parse JSON, or handle memory buffers. The model already knows standard library idioms, language syntax, and baseline data structures. The spec focuses strictly on domain invariants, permissible dependencies, latency budgets, and error contracts.
2. **The test suite provides the hard floor**: Natural language alone is fundamentally squishy; a markdown spec without a verification harness can still trigger hallucinations. Specs work as reliable scaffolding only because the generated output is checked immediately by compilers, static type checkers, and automated test suites (see [[Testing in the Model, Agent, LLM Era]]). If the agent generates code that violates an architectural invariant or breaks a type contract, the compiler throws, the tests fail, and the raw error output is fed back into the agent to pull it into alignment.

---

## The Reality: You Don't Write Specs Upfront in a Vacuum

A common failure mode in adopting agents is trying to write perfect, exhaustive specifications upfront before running any code.

In real-world systems engineering, nobody understands every edge case, network quirk, or lifecycle race condition before writing code. When you build an event-driven processing pipeline, an internal caching layer, or an integration with a poorly documented third-party API, real system requirements only emerge through hands-on implementation and rapid iteration:

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

1. **Explore first when the path is unclear**: When building something new, run short iterative prompts with the agent. Inspect the generated code directly, write quick spike tests, and surface hidden runtime edge cases (such as connection pool exhaustion, rate limits, or serialization gotchas).
2. **Freeze the solution immediately**: Once the implementation passes its unit and integration tests and the design settles, immediately prompt the agent to write an Operation Card. If you skip this step, the architectural context and hard-won edge case handling remain trapped in ephemeral chat logs. The next time an agent touches the repository, it will be forced to guess the design rules from raw source code.
3. **Calibrate the spec**: The real test of an Operation Card is simple: spin up a clean agent session with no prior conversation history, provide the card and the test suite, and instruct it to add a minor feature or adjust an internal routine. If the agent breaks an invariant or imports an unapproved package, your spec was ambiguous. Clarify the card and commit it.

---

## Token Economics: Concise Cards vs. Sprawling Context

In agent-driven development, context window space and model attention are your main operational bottlenecks. Modern models can ingest 128k or even 1M tokens, but effective reasoning degrades as context length grows—the well-known needle-in-a-haystack problem:

| Approach | Context Ingestion | Attention Overhead | Drift Risk |
| :--- | :--- | :--- | :--- |
| **Dumping Source Files** | 15–30 files (15,000–40,000 tokens) | High (needle-in-a-haystack effect, subtle logic gets lost) | High (agent copies local workarounds and legacy code smells) |
| **In-Flight Spec Card** | 1 spec card (300–800 tokens) + target file | Low (clear focus on explicit contracts and interfaces) | Minimal (agent stays confined to documented boundary rules) |

Providing an agent with a concise, targeted spec card instead of dozens of loosely related source files delivers clear engineering benefits:
- Lower Time-to-First-Token (TTFT) and faster overall generation runs,
- Significantly lower token costs across continuous development loops,
- Higher reasoning accuracy by avoiding attention dilution across large prompt payloads (see [[How Context Narrows an AI's Solution Space]]).

---

## Anatomy of a Real-World Operation Card

An effective in-flight document avoids duplicating line-by-line code logic. It establishes clear architectural boundaries: **purpose, boundary invariants, file touchpoints, allowed dependencies, and failure handling modes**:

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

When an agent needs to maintain or modify this module down the road, loading this single card gives it the exact system constraints it needs to honor—without requiring it to scan five different directories to piece together the architecture.

---

## Practical Rules for Engineering Teams

1. **Never write operational docs by hand**: Require the agent to generate its own Operation Card the moment an implementation stabilizes and the test suite passes.
2. **Use markdown cards as structural guardrails**: Treat structured documentation as the primary control plane for where code lives, what dependencies are permitted, and how exceptions must be handled.
3. **Pair specs with automated tests**: Markdown defines domain intent; the compiler and test harness supply the deterministic validation needed to prevent model drift.
4. **Protect your token budget**: Do not treat multi-hundred-thousand token windows as an excuse for undisciplined file dumping. Supply agents with lean, modular spec cards to maximize reasoning accuracy.
5. **Protect the system against architectural entropy**: Documenting explicit boundary conditions alongside new code prevents future agent sessions from accidentally breaking existing design patterns (see [[Software Decay and the Hidden Costs of Frictionless AI Code]]).

---

## Relationship to the Knowledge Graph

- **[[Testing in the Model, Agent, LLM Era]]**: Explains how automated compilers and test suites serve as the non-negotiable verification layer backing up markdown specifications.
- **[[Optimizing Software Engineering and Code for Agents]]**: Details how codebase layouts, module boundaries, and explicit interface contracts change when agents become the primary readers and writers of code.
- **[[Reviewing AI-Generated Code]]**: How engineers use concise in-flight documentation and targeted diff reviews to maintain deep systems understanding without manually writing every implementation detail.
- **[[AI-Generated Architectural Documentation from Code]]**: The reverse pattern—extracting high-level architectural models from existing production codebases to bootstrap baseline specifications.
- **[[The Increasing Value of Comments in AI-Generated Code]]**: Why non-derivable domain intent, hardware quirks, and business rules belong in inline code comments and companion markdown cards.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: Using standardized spec cards as an engineering control to stop sprawling, unmaintainable agent-generated complexity.
- **[[Designing Software for AI Agents]]**: Core architectural patterns that make code discoverable, isolated, and simple for agents to safely modify.
