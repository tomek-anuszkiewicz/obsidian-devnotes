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
---

# In-Flight Documentation as the Primary Framework for Coding Agents

## Core Thesis

In traditional software development, documentation was often an agonizing afterthought—a post-implementation chore frequently abandoned due to human writing fatigue. Code, class hierarchies, and concrete frameworks served as the primary scaffolding for developers.

In agentic software engineering, this paradigm is completely inverted:
1. **Documentation is generated in-flight**: Rather than writing prose manually, the engineer instructs the agent to synthesize concise architectural documentation concurrently as code is authored.
2. **Documentation replaces code as the primary framework and template**: For an AI agent, structured markdown specifications, interface contracts, and operation cards are far more effective scaffolds than bloated OOP base classes or framework boilerplate.
3. **In-flight documentation imparts determinism to future stochastic modifications**: It narrows the model's solution space, turning what would be creative probabilistic guesswork into predictable, deterministic schema compliance.
4. **It radically optimizes token consumption**: Ingesting a 50-line semantic blueprint consumes a fraction of the context window compared to loading dozens of raw source files to infer architectural intent.

---

## "Documentation as Code for the Agent": Markdown as the Highest-Level Source Code

The transition to agentic engineering redefines the very definition and purpose of software documentation:

- **The Classical View**: Documentation was an annoying, quickly outdated post-implementation chore written by humans for other humans, constantly suffering from drift as the codebase evolved.
- **The Agentic Reality**: Structured Markdown documentation **is the highest-level source code**.

```text
TRADITIONAL COMPILATION:
C# / Rust Source Code ──► Deterministic Compiler (Roslyn / rustc) ──► Machine Assembly / Bytecode

AGENTIC COMPILATION:
Markdown Design Specification ──► LLM Reasoning Engine (AI Compiler) ──► Systems Code (Rust / C# / TypeScript)
```

In this operational model:

1. **Writing for the AI Compiler**:
   Engineers do not author documentation for human casual browsing—they write it as **precise, mechanically exact input for the AI compiler**. The Markdown design document serves as the formal, executable high-level specification.
   
2. **The Direct Correlation Between Documentation Rigor and Code Fidelity**:
   The richer, more structurally rigorous, and more physically and mathematically accurate the Markdown documentation, the higher the fidelity, resilience, and runtime performance of the generated code. When the document explicitly defines operational limits, state invariants, concurrency boundaries, and failure cascades, the LLM reasoning engine translates those exact constraints into optimized, production-grade systems code.

3. **Documentation as the Canonical Source of Truth**:
   When system behavior or business logic must evolve, the engineer does not wade through thousands of lines of syntactic boilerplate. They update the high-level Markdown specification and re-compile the subsystem through the agent. The generated code is merely the transient, downstream manifestation of the architectural document.

### Escaping the 4GL / Executable UML Trap: The Essential Triad

A common historical skepticism arises: *Is treating Markdown as "executable source code" merely a recurrence of the failed 4GL, CASE tools, and Executable UML fads of the 1980s–2000s?*

Those historic paradigms collapsed because their code generators were rigid, rule-based AST transpilers. To generate correct C or Java without human intervention, engineers had to specify every atomic detail—register assignments, null checks, thread synchronization—inside clumsy diagrammatic or proprietary 4GL languages. The specification inevitably became more verbose, opaque, and brittle than simply writing C++.

The agentic paradigm avoids this trap through a fundamental **triad of complementary forces**:

```text
HISTORICAL CASE / UML TRAP (Failure):
Executable UML / 4GL ──► Rigid AST Transpiler ──► Fragile, bloated C++/Java
(Engineers forced to specify every atomic loop and variable in diagrams)

THE AGENTIC TRIAD (Success):
Living Markdown Specs (Intent & Invariants) ──┐
                                              ├─► LLM Reasoning Engine ──► Clean, Idiomatic Systems Code
Ironclad Test Oracle (Deterministic Vectors) ─┤   (Pretrained on syntax,
                                              │    borrow checkers, idioms)
Human Architect (Mechanical Sympathy) ────────┘
```

1. **The LLM Is Not an AST Transpiler**:
   The LLM reasoning engine already understands idiomatic Rust, C#, memory layouts, standard libraries, and concurrency primitives. Markdown does not need to specify how to allocate a vector or handle loop iterators; it specifies **the "Why" and the "What"**—architectural invariants, state machines, domain terminology, and error cascades.
2. **Markdown Without Tests Is Hallucination**:
   Natural language in Markdown is inherently ambiguous. Relying on Markdown alone would produce plausible-looking code riddled with subtle semantic regressions. The Markdown specification functions as high-level code **only because it is bounded by an [[Testing in the Model, Agent, LLM Era|Ironclad Test Oracle]]**. The immutable test suite provides the unyielding, binary pass/fail physical reality that forces the agent to align its generated code with exact specifications.
3. **The Human as the Guardian of Domain Reality**:
   Neither Markdown nor test suites possess mechanical sympathy. Only the human engineer understands the underlying hardware constraints, cache line budgets, and production traffic distributions.

Markdown documentation is therefore not an attempt to create a new pseudo-code language; it is the **semantic steering vector** within a rigorous, three-pillar control system.

---

## The Shift from Code Frameworks to Documentation Frameworks

Historically, frameworks provided scaffolding through rigid syntactic structures:
- Abstract base classes,
- Boilerplate design patterns,
- Code generation scripts,
- Runtime reflection conventions.

These mechanisms existed because human developers needed guardrails against inconsistency. However, LLM coding agents do not reason best through deep inheritance trees or opaque framework internals (see [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]). 

For an agent, **structured documentation is the framework**:

```text
CLASSICAL PARADIGM:
Specification ──► Human writes Code ──► (Documentation skipped due to friction)
                                              │
Future maintenance: Read 20 source files to guess original intent

AGENTIC PARADIGM:
Task / Intent ──► Agent writes Code + In-Flight Documentation simultaneously
                                              │
Future maintenance: Agent ingests concise Documentation Blueprint ──► Deterministic, token-efficient edit
```

When an agent writes a new vertical slice or domain operation, producing a standardized markdown specification alongside the implementation establishes the authoritative schema for all subsequent iterations.

---

## Why In-Flight Generation Is Feasible in the AI Era

Why was "continuous, concurrent documentation" rarely practiced historically? **Human friction.**
Typing out comprehensive data flows, failure modes, invariants, and sequence cards consumed significant developer cognitive energy.

With coding agents, the marginal cost of documentation generation drops to near zero:
- The agent already holds the architectural mental model, variable names, entry points, and edge cases fresh in its context window during the authoring phase.
- Generating a companion markdown card requires merely a single instruction in the workflow harness:
  > *"Synthesize an Operation Card documenting the entry points, invariant rules, data flow, failure modes, and file touchpoints for this new component."*
- The engineer does not type the prose; they simply review and validate the agent's synthesized blueprint.

---

## Imparting Determinism to Stochastic Systems

Large language models are fundamentally non-deterministic, probabilistic inference engines (see [[LLM Coding Agents Reliability]]). When an agent is instructed to modify or extend an existing subsystem without explicit architectural documentation, it is forced to infer context:
- It scans arbitrarily selected files,
- It extrapolates patterns based on general pretraining weights rather than local repo intent,
- It risks hallucinating novel conventions or duplicating existing utilities.

In-flight documentation acts as a **deterministic constraint anchor**:
- It replaces subjective inference with explicit structural bounds:
  - *Which files own which state,*
  - *Which operations are strictly synchronous vs. asynchronous,*
  - *Which side effects are forbidden,*
  - *What exact error handling contract is required.*
- By anchoring the agent's attention on an explicit blueprint, subsequent tasks shift from probabilistic invention to **constrained slot-filling**.

---

## Token Economics and Context Efficiency

In agentic coding, **context window bandwidth and attention fidelity are the ultimate bottlenecks**:

| Approach | Context Ingestion | Attention Overhead | Risk of Semantic Drift |
| :--- | :--- | :--- | :--- |
| **Code-Only Inference** | 15–30 source files (10,000–30,000 tokens) | High (needle-in-a-haystack effect, diluted attention) | High (misinterprets obscure cross-file dependencies) |
| **In-Flight Blueprint** | 1 concise doc card (300–800 tokens) + 1 target file | Minimal (pinpoint attention on explicit contracts) | Very Low (operates strictly within documented bounds) |

Instead of burning tens of thousands of tokens per prompt just to orient the model within a sprawling codebase, the harness feeds the relevant in-flight documentation card. This delivers:
1. **Faster execution times**,
2. **Lower API operational costs**,
3. **Substantially higher reasoning fidelity**, avoiding the attention saturation traps described in [[How Context Narrows an AI's Solution Space]].

---

## Maintaining Architectural Trajectory and Preventing Entropy

As a codebase evolves across dozens of autonomous agent sessions, the risk of architectural drift and "zero-friction sprawl" increases exponentially (see [[Software Entropy and the Zero-Friction Trap]]).

In-flight documentation ensures **directional alignment**:
- Every newly created component adheres to a uniform template (e.g., standard lifecycle states, explicit error returns, dedicated file boundaries).
- Future agents cannot claim ignorance of design choices made three weeks prior.
- If a future change requires violating an invariant recorded in the in-flight documentation, the conflict is immediately exposed during code review or agent reasoning, forcing explicit human approval rather than silent architectural rot.

---

## Anatomy of an In-Flight Agentic Template

An effective in-flight documentation card does not replicate code verbatim; it captures **intent, constraints, and boundaries**:

```markdown
### Component / Operation: ProcessPaymentSettlement

**Purpose**: Orchestrates payment settlement against external gateways and posts journal entries.

**Boundary Invariants**:
- Idempotent: Can be retried safely with the same `TransactionId`.
- No direct database writes to Ledger tables (must publish `SettlementCompleted` event).
- External PSP timeout ceiling: 5000ms.

**File Touchpoints**:
- Orchestration: `Billing/SettlementCoordinator.cs`
- Contract: `Billing/Contracts/ISettlementGateway.cs`
- Verification Test: `Billing.Tests/SettlementCoordinatorTests.cs`

**Allowed Dependencies**:
- Synchronous: Gateway client, Clock, Logger.
- Forbidden: User context store, Cart repository.

**Failure Handling**:
- Timeout -> Mark state as `PendingReconciliation`, emit operational telemetry alert.
- Validation error -> Immediate terminal abort with `DomainValidationException`.
```

Such cards act as executable specifications for future agent modifications.

---

## Key Principles

1. **Never write documentation manually; demand it from the authoring agent**: Generate architectural cards at the moment of code creation when context is richest.
2. **Documentation is the agent's framework**: Treat structured markdown cards as the primary scaffolding that guides where code goes and how it behaves.
3. **Constrain stochasticity with explicit blueprints**: Use in-flight documentation to convert open-ended probabilistic generation into deterministic, bounded implementation.
4. **Optimize token budgets aggressively**: Provide compact semantic cards rather than dumping dozens of raw source files into agent context.
5. **Anchor long-term architectural trajectory**: Preserve the "why" and "what must not break" alongside the code to eliminate architectural rot across agent sessions.

---

## Relationship to the Knowledge Graph

- **[[AI-Generated Architectural Documentation from Code]]**: Explores reverse-engineering and continuous architectural extraction from existing code; in-flight generation complements this by capturing intent at authoring time.
- **[[Comments May Become More Valuable in AI-Generated Code]]**: How inline comments and in-flight markdown cards preserve non-derivable domain rationale.
- **[[Software Entropy and the Zero-Friction Trap]]**: Using standardized in-flight templates as mechanical friction to prevent uncontrolled code sprawl.
- **[[Designing Software for AI Agents]]**: Architectural design patterns that make code discoverable, predictable, and cleanly documentable.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: How codebases evolve when optimized for agent consumption rather than human syntax habits.
- **[[How Context Narrows an AI's Solution Space]]**: Theoretical mechanisms of how targeted contextual blueprints eliminate hallucinations.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Harness workflows that automate in-flight documentation generation as a mandatory step in feature loops.
- **[[LLM Coding Agents Reliability]]**: Mitigating the probabilistic hazards of agents by grounding their actions in deterministic documentation fences.
