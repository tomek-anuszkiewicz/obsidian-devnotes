---
title: Designing Software for AI Agents
tags:
  - software-architecture
  - system-design
  - ai-agents
  - agentic-coding
  - modularity
  - observability
  - mechanical-sympathy
aliases:
  - Agent-Oriented Software Design
  - Building Software for AI Consumption
  - Principles of Agentic System Design
---

# Designing Software for AI Agents

## The Core Thesis: Mechanical Discoverability Over Human Brevity

Autonomous coding agents do not eliminate the necessity of disciplined software architecture; **they make architectural rigor far more urgent**. When AI models can generate and modify hundreds of lines of code in seconds, structural ambiguities that once took months for human developers to stumble into will cascade across an entire repository in days.

```text
HISTORICAL HUMAN-CENTRIC ARCHITECTURE:
  Goal: Minimize typing, conserve developer working memory
  Mechanisms: Ambient containers, deep inheritance, reflection, magic interceptors
  Cost: High implicit complexity, invisible runtime graphs

AGENTIC-CENTRIC ARCHITECTURE:
  Goal: Maximize mechanical discoverability, bound reasoning scopes
  Mechanisms: 1:1 operation-to-file hierarchy, explicit execution pipelines, deterministic oracles
  Cost: Modest local verbosity, but zero ambient surprises and bounded blast radius
```

An agent-friendly system is designed to provide immediate, deterministic answers to four foundational questions:
1. **Locality of Change**: *Where exactly should this mutation occur?*
2. **Behavioral Invariant**: *What contract is expected, and what must never be broken?*
3. **Verification Oracle**: *How can correctness be proven mechanically within seconds?*
4. **Blast Radius Enclosure**: *What parts of the system are physically isolated from this change?*

The objective is not to optimize code for a specific foundation model version, but to build architectures that can be navigated, modified, and verified deterministically by any intelligent participant—human or synthetic.

---

## Generative Sprawl & The 3 Mechanical Enclosures

While human developers are naturally constrained by biological friction (typing fatigue, diff aversion, context-switching drag), AI agents possess **zero generative friction**. Left unconstrained, an agent will effortlessly create sprawling intermediate classes, nested interfaces, and multi-file dependencies.

To contain zero-friction generation, architecture must transition from polite guidelines to **hard mechanical enclosures**:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. THE 1:1 STRUCTURAL HIERARCHY (One Operation, One File)   │
│    Every domain command, query, or handler lives in its own │
│    dedicated file. Editing Operation A physically cannot    │
│    corrupt Operation B.                                     │
├─────────────────────────────────────────────────────────────┤
│ 2. HARD FILE CEILINGS (e.g., 500–800 Lines Max)             │
│    Mechanically enforced by linters. Prevents the emergence │
│    of "god files" and bounds prompt context requirements.   │
├─────────────────────────────────────────────────────────────┤
│ 3. CONSTRAINED TOUCHPOINT BUDGETS                           │
│    Tasks are bounded to 1–2 files per mutation step. Cross- │
│    module imports are blocked at the build boundary.        │
└─────────────────────────────────────────────────────────────┘
```

For the exhaustive theoretical analysis of this dynamic, see **[[Software Entropy and the Zero-Friction Trap|the treatise on software entropy and generative sprawl]]**.

---

## Predictable, Discoverable Execution Over Ambient Magic

In an agentic codebase, **code length is not equivalent to cognitive complexity**. An agent can reliably reason through twenty explicit, self-contained classes, but will fail completely when navigating five ultra-short classes whose behavior depends on assembly scanning, ambient reflection, or undocumented middleware ordering.

### The Explicit Execution Standard:
```text
// EXPLICIT EXECUTION (High Semantic Locality):
operation_pipeline:
    check_authorization(command, current_user)
    validate_contract(command)
    execute_transaction:
        result = handler.process(command)
        event_outbox.record(result.domain_events)
    return result
```

This explicit structure is essential whenever operational sequence, transaction boundaries, and side-effects define business correctness, avoiding [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code|costly hidden abstractions]].

### Centralized Infrastructure vs. Hidden Semantics:
This principle does not advocate duplicating generic plumbing everywhere. Standard infrastructure—such as mapping recognized domain exceptions to standard HTTP error envelopes (RFC 7807) or injecting distributed tracing spans—is legitimately handled by centralized middleware. 

The boundary is clear:
- **Centralize generic, uniform infrastructure mechanics** (telemetry timers, wire format serializers).
- **Keep domain-relevant policy explicit and visible** (authorization checks, business validations, tenant isolation, transaction boundaries).

---

## System Granularity: Monoliths vs. Microservices

Autonomous agents alter the practical boundaries between monolithic and distributed architectures:

| Architectural Style | Advantages for Agents | Operational Liabilities for Agents |
| :--- | :--- | :--- |
| **Modular Monolith** | Single repository, unified local test environment, rapid full-system builds, compile-time contract enforcement. | Risk of leaking dependencies across module boundaries if structural isolation is weak; context bloat if boundaries are blurry. |
| **Microservices** | Tightly bounded reasoning scopes, explicit external REST/gRPC contracts, small standalone codebases, independent blast radius. | Distributed contract drift, asynchronous queue reconciliation, multi-repo PR coordination, network failure cascades. |

### The Pragmatic Rule:
Agents do not inherently prefer monoliths or microservices. **They thrive in architectures where the reasoning scope, public contracts, and verification procedures are self-contained.** A modular monolith with strict build-enforced boundaries (e.g., package/namespace isolation) provides the ideal combination: local in-process verification without distributed network complexity.

---

## Explicit Communication Boundaries

Modules must communicate through explicit, structured contracts rather than sharing internal state, direct database tables, or mutable domain models.

### 1. CQRS Command and Query Contracts
Represent operational intent through immutable, structured messages:
```text
record CancelOrderCommand(
    order_id: UUID,
    operator_id: UUID,
    cancellation_reason: String
)
```

### 2. Module Boundaries: Facades, Handlers, and Dispatchers
Organizations have three primary architectural choices for intra-system boundaries:
- **Module Facade**: Exposes a single public gateway interface (e.g., `OrdersModuleFacade`). Highly discoverable, but risks becoming an unmaintainable "kitchen sink" interface.
- **Granular Operation Handlers**: Exposes discrete public handlers per command (e.g., `CancelOrderHandler`). Minimizes coupling and makes call paths 1:1, but increases public type counts.
- **Command Dispatcher / Mediator**: Provides uniform execution pipelines and decouples callers from handlers, but introduces runtime indirection that requires agents to use semantic search to locate handler implementations.

The chosen mechanism must ensure that **the path from request to implementation is mechanically discoverable** without relying on runtime guesswork.

---

## Modeling Data to Eliminate Interpretive Ambiguity

Codebases written for agents must eliminate semantic ambiguity in data models:
- **Ban Multi-Purpose Nulls**: Never use `null` to represent both "value not yet loaded" and "value does not exist."
- **Eliminate Sentinel Overloading**: Never allow `0` or `-1` to represent both a valid numerical value and a business state (e.g., infinite retries).
- **Prevent Context-Dependent Fields**: A field must never represent supplier wholesale cost in one context and customer retail price in another.
- **Prefer Expressive Enums Over Booleans**: Replace ambiguous flags (`is_valid`, `is_pending`) with explicit lifecycle states (`AccountState.PENDING_EMAIL_VERIFICATION`).

> **Do not minimize the number of fields in a model. Minimize the number of possible interpretations.**

---

## Decomposing Workflows into Explicit Data Stages

Avoid passing a single, massive mutable context object (e.g., `OrderContext`) through dozens of processing steps where fields are incrementally populated and overwritten.

Decompose complex pipelines into discrete, immutable stages:
```text
SupplierRawQuote
  ──► [Validation Stage]     ──► ValidatedSupplierData
  ──► [Normalization Stage]  ──► NormalizedCostModel
  ──► [Currency Stage]       ──► LocalizedCurrencyPricing
  ──► [Policy Engine]        ──► CustomerFinalPrice
  ──► [Audit Generator]      ──► AuditedPriceCalculation
```

Each stage has an explicit, strongly typed input and output. Provenance is visible, intermediate state cannot leak, and agents can verify or refactor individual transformation stages in complete isolation.

---

## Practical Architectural Checklist

1. **Verify Discoverability**: Can a new developer or agent locate the implementation of any API endpoint in under 30 seconds using standard text or symbol search?
2. **Enforce Mechanical Boundaries**: Are file line limits (500–800 lines) and 1:1 operation-to-file layouts verified automatically in CI?
3. **Expose Business Flow**: Are authorization gates, transaction boundaries, and business validations explicitly visible in the operation flow?
4. **Isolate Domain Decisions**: Are business rules separated into pure, side-effect-free decision components?
5. **Stage Complex Transformations**: Are multi-step business pipelines decomposed into immutable, typed stages rather than mutating a shared global context?

---

## Related Notes

- **[[Data Access Economics with Coding Agents - ORMs vs Explicit SQL]]**: Practical patterns for constraining ORM complexity and schema operations under agentic workflows.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Replacing heavy code scaffolding with in-flight documentation as the primary agent framework.
- **[[Software Entropy and the Zero-Friction Trap]]**: Explores the zero-friction generation dilemma and why mechanical 1:1 file constraints are required.
- **[[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]**: Why implicit meta-layers, reflection, and runtime magic disorient agentic reasoning.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: How codebases adapt their structures to be easily maintained, navigated, and verified by agents.

---

## Relationship to the Knowledge Graph

- **[[Designing APIs for LLM-Generated Integration Code]]**: Designing strongly typed, machine-discoverable client boundaries.
- **[[Scaling a Modular Monolith with Local-or-Remote Module Execution]]**: Module boundary isolation that enables agents to reason about domain slices independently.
- **[[AI Changes the Economics of Technical Debt]]**: Operational justifications for refactoring systems into agent-friendly patterns.
- **[[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]]**: Patterns for embedding models directly into production execution pipelines with deterministic envelopes.
- **[[The 5-Layer System Stack for Agentic Software Engineering]]**: Placing agent-oriented system design in Layer 1 (Structural Isolation) and Layer 2 (Governance & Harness).
