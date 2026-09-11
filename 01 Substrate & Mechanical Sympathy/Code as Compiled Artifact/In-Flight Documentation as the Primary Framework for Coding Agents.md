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
  - The Triad of Specs Oracles and Human Sympathy
  - Escaping the 4GL and CASE Trap
  - The Compiler-less Language Paradox
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
Source Code ──► Deterministic Compiler / Type Checker ──► Executable Binary / Machine Code

AGENTIC COMPILATION (TWO-STAGE PIPELINE):
Markdown Specification ──► LLM Reasoning Engine ──► Source Code ──► Deterministic Compiler ──► Executable Binary
[High-Level Intent]        [Front-End AI Compiler]   [Intermediate  [Back-End Toolchain]       [Physical Target]
                                                     Artifact / IR]
```

In this operational model:

1. **Source Code as an Intermediate Representation (IR)**:
   In traditional engineering, source code sat at the very apex of the pipeline as the primary human-authored input. In agentic engineering, source code shifts to the middle of the pipeline: it becomes a machine-synthesized, human-auditable **intermediate representation (IR)** emitted by the front-end reasoning engine and consumed by the deterministic back-end compiler.
   
2. **The Two-Stage Agentic Compilation Pipeline**:
   - **Stage 1 (Semantic Front-End Compilation)**: The LLM reasoning engine parses structured Markdown design specifications, domain contracts, and operational invariants, compiling high-level architectural intent into syntactically valid source code.
   - **Stage 2 (Deterministic Back-End Compilation)**: Traditional deterministic compilers, type checkers, and test oracles ingest the generated source code, performing static verification, type inference, memory layout optimization, and emitting the final executable binary, bytecode, or runtime package.

3. **Writing for the AI Front-End Compiler**:
   Engineers author documentation not as passive human prose, but as **precise, mechanically exact input for the front-end AI compiler**. The Markdown design specification is the true canonical source code of the system.
   
4. **The Direct Correlation Between Specification Rigor and Binary Fidelity**:
   The richer, more structurally rigorous, and more physically and mathematically accurate the Markdown documentation, the higher the fidelity, resilience, and runtime performance of both the intermediate source code and the final compiled binary. When the document explicitly defines operational limits, state invariants, concurrency boundaries, and failure cascades, the LLM reasoning engine translates those exact constraints into optimized, production-grade systems code.

5. **Documentation as the Canonical Source of Truth**:
   When system behavior or business logic must evolve, the engineer does not wade through thousands of lines of syntactic boilerplate. They update the high-level Markdown specification and re-compile the subsystem through the agent. The generated source code is merely the transient intermediate representation, and the binary is the final runtime artifact.

### Escaping the 4GL / Executable UML Trap: Specifications, Verification Oracles, and Human Stewardship

A natural, well-founded historical skepticism frequently challenges the concept of in-flight documentation:  
> *"Isn't treating Markdown as high-level source code merely the recurring curse of Fourth-Generation Languages (4GL in the 1980s), CASE tools (in the 1990s), and Model-Driven Architecture / Executable UML (in the 2000s)?"*

Every 15 to 20 years, the software industry attempts to eliminate manual programming by proclaiming that visual diagrams or high-level business prose will automatically compile into flawless code. Every single one of these historic attempts collapsed under the weight of an immutable epistemological reality: **natural language and visual diagrams are inherently underspecified, probabilistic, and ambiguous**.

The modern agentic paradigm does not repeat this failure because it does not attempt to make Markdown an isolated, standalone programming language. Instead, it embeds Markdown as the semantic intent vector inside a **coherent specification, synthesis, and verification pipeline**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│           THE AGENTIC SPECIFICATION & VERIFICATION PIPELINE            │
│                                                                        │
│   1. HUMAN SYSTEM ARCHITECT (Strategic Intent & Constraints)           │
│      - System topology, domain boundaries, and resource budgets        │
│      - Non-functional requirements (latency, security, concurrency)    │
│                         │                                              │
│                         ▼                                              │
│   2. LIVING MARKDOWN SPECS (Semantic Source of Truth)                  │
│      - Architectural invariants, contracts, and state machines         │
│      - Eliminates atomic instruction clutter; defines What & Why       │
│                         │                                              │
│                         ▼                                              │
│   3. LLM REASONING ENGINE (Front-End Semantic Compiler)                │
│      - Synthesizes idioms, boilerplate, and algorithmic logic          │
│                         │                                              │
│                         ▼                                              │
│   4. INTERMEDIATE SOURCE CODE (Machine-Synthesized Artifact)           │
│                         │                                              │
│                         ▼                                              │
│   5. DETERMINISTIC VERIFICATION (Back-End Compiler & Test Oracle)      │
│      - Compiler & Type Checker: Enforces memory safety & typing        │
│      - Test Oracle: Binary pass/fail validation of operational rules   │
│                         │                                              │
│          ┌──────────────┴──────────────┐                               │
│          ▼                             ▼                               │
│      [FAIL / ERROR]                 [PASS]                             │
│   Feedback to Agent       Deployable Executable / Binary               │
└────────────────────────────────────────────────────────────────────────┘
```

#### 1. Why Markdown Is Not a Programming Language (The Compiler-less Language Paradox)
The fatal error of 4GL, CASE tools, and Executable UML was attempting to replace programming languages with clumsy abstractions:
- To generate production-grade code without human intervention, visual models or 4GL scripts were forced to specify **every atomic nuance of execution**: exact memory allocation, pointer dereferencing, lock acquisition order, null checks, and error unwinding paths.
- The moment a specification reaches that level of exhaustive granularity, **it ceases to be a specification and becomes an untyped, verbose programming language without a compiler or type checker**. Instead of writing 10 lines of concise, expressive statically typed code, the engineer ended up authoring 50 to 100 lines of clumsy diagrammatic or verbal prose.
- **The Agentic Demarcation**: In our architecture, Markdown **never describes atomic execution steps**. It does not dictate how to iterate a loop, allocate a vector, or handle register arithmetic. The frontier LLM reasoning engine already possesses pre-trained mastery of syntax semantics, standard library interfaces, type systems, and idiomatic execution patterns.
- Markdown specifies strictly **domain invariants, state boundaries, operational non-goals, and boundary contracts**. It is the compass, not the engine.

#### 2. Why Markdown Alone Degrades into Hallucination (The Role of the Deterministic Test Oracle)
Natural language—even when formatted into clean, structured Markdown cards—is fluid and probabilistic:
- When models operate over extended contexts or encounter edge conditions, they suffer from **context drift, rule decay, and constraint saturation** (see [[Constraint Saturation and Rule Oscillation in Coding Agents]]).
- If an agent is guided solely by Markdown prose without deterministic boundaries, it will generate code that *sounds* convincing and *looks* idiomatic, yet silently violates subtle operational contracts or introduces phantom states.
- **The Ironclad Test Oracle as the Verification Gate**: Markdown specification functions as high-level architectural code **only because it is verified by an [[Testing in the Model, Agent, LLM Era|Ironclad Test Oracle]]**. 
  - The automated test suite does not "execute" the Markdown document; it validates the **intermediate source code** generated by the agent.
  - The test runner provides an unyielding, non-negotiable physical wall. A non-zero exit code (`FAIL`) produces precise error feedback that collapses the agent's probabilistic search space back to deterministic compliance.
  - Markdown supplies the **semantic intent**; the test oracle supplies the **binary verification**. Neither can function safely without the other.

#### 3. The Non-Delegable Role of the Human System Architect (Architectural Sympathy & Reality Anchor)
Neither Markdown specifications nor automated test suites possess holistic systems judgment:
- A test oracle validates functional assertions (`actual == expected`); it is completely blind to whether the agent's code introduces catastrophic architectural coupling, exceeds network latency budgets, leaks database connection pools, or introduces subtle concurrency deadlocks under high production load.
- A language model, if left unconstrained, defaults to generic textbook abstractions (over-engineered inheritance trees, unnecessary wrapper layers, leaky boundaries) because of its training distribution.
- **The Non-Delegable Role of the Human Architect**: The human software engineer remains the indispensable strategic governor who:
  1. **Enforces System Topology & Blast Radius Boundaries**: Defines modular boundaries, data ownership, and isolation barriers, preventing spaghetti dependencies.
  2. **Establishes Real-World Non-Functional Constraints**: Sets uncompromising operational envelopes for latency budgets, serialization overhead, concurrency models, and cloud infrastructure cost.
  3. **Acts as the Circuit Breaker Against Architectural Rot**: Identifies complexity traps, rejects speculative abstractions, and maintains long-term system cohesion across autonomous agent sessions (see [[Refactoring Legacy Systems with AI Agents]]).

Markdown documentation is therefore not a nostalgic rehash of the 4GL dream; it is the **semantic intent layer** in a disciplined pipeline that binds human architectural judgment to deterministic machine verification.

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
- Orchestration: `billing/settlement_coordinator`
- Contract: `billing/contracts/settlement_gateway`
- Verification Test: `billing/tests/settlement_coordinator_test`

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

- **[[Testing in the Model, Agent, LLM Era]]**: Foundational hub establishing the ironclad test oracle as the hard deterministic anchor bounding Markdown intent in the agentic triad.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: Architectural counterpart governing mechanical sympathy, L1i instruction cache locality, and Data-Oriented Design against LLM OOP bias.
- **[[Constraint Saturation and Rule Oscillation in Coding Agents]]**: Explains why Markdown specifications suffer from probabilistic drift without rigid deterministic test bounds.
- **[[Refactoring Legacy Systems with AI Agents]]**: Living specifications as the primary blueprints for strangler-fig modernizations and escaping the Frankenstein intermediate phase.
- **[[Negative Knowledge and Explicit Architectural Dissents]]**: Formally codifying architectural rejections and dissents within in-flight specifications to prevent recurrent fads.
- **[[AI-Generated Architectural Documentation from Code]]**: Explores reverse-engineering and continuous architectural extraction from existing code; in-flight generation complements this by capturing intent at authoring time.
- **[[Comments May Become More Valuable in AI-Generated Code]]**: How inline comments and in-flight markdown cards preserve non-derivable domain rationale.
- **[[Software Entropy and the Zero-Friction Trap]]**: Using standardized in-flight templates as mechanical friction to prevent uncontrolled code sprawl.
- **[[Designing Software for AI Agents]]**: Architectural design patterns that make code discoverable, predictable, and cleanly documentable.
- **[[How Context Narrows an AI's Solution Space]]**: Theoretical mechanisms of how targeted contextual blueprints eliminate hallucinations.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Harness workflows that automate in-flight documentation generation as a mandatory step in feature loops.
- **[[LLM Coding Agents Reliability]]**: Mitigating the probabilistic hazards of agents by grounding their actions in deterministic documentation fences.
