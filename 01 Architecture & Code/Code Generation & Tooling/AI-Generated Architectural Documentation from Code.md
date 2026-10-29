---
title: AI-Generated Architectural Documentation from Code
tags:
  - ai-agents
  - software-architecture
  - documentation
  - knowledge-management
  - reverse-engineering
  - code-review
aliases:
  - Architectural Documentation Generation
  - Extracting Architecture from Code with LLMs
  - AI-Generated Architectural Documentation
  - Documentation as Semantic Cache
  - Architectural Drift Detection
  - Operation Cards from Code
---

A system's architecture is distributed across source files, configuration, message handlers, data models, and runtime behavior. Reconstructing it is an evidence problem: a relationship in a graph, a possible path in code, and a path observed in a trace establish different things.

This article develops code-derived architectural knowledge, its limits, and its value as reusable context. [[Documenting Business Operations with Diagrams and Operation Cards]] turns that knowledge into business-operation descriptions, diagrams, state transitions, failure paths, and compact cards. [[Keeping Architectural Documentation Aligned with Code]] follows revisions, architectural differences, and the update process. Reconstruction should make its sources and remaining uncertainty visible so later readers can check the explanation.

## Idea

LLMs can be used not only to generate code from specifications, but also to reconstruct documentation, architecture, and system behavior from existing code.

This is especially useful for:

- legacy systems created before widespread AI adoption,

- systems with incomplete or outdated documentation,

- large repositories where the architecture is difficult to infer,

- codebases where architectural knowledge exists mostly in developers' heads.

The goal is not merely to generate class or method descriptions.

The more valuable goal is to create a **semantic model of the system** that explains:

- what components exist,

- what they are responsible for,

- how they communicate,

- how data flows through the system,

- how important business operations execute,

- what happens synchronously and asynchronously,

- what state transitions exist,

- what architectural rules and invariants are implicit in the code.

---

## Code as a Source of Architectural Knowledge

Existing source code contains a large amount of architectural information, but that information is often distributed across many files.

A developer may need to inspect:

- controllers,

- handlers,

- services,

- repositories,

- database models,

- message consumers,

- event publishers,

- configuration,

- dependency injection,

- middleware,

- scheduled jobs,

- external API clients,

before understanding how one business operation works.

An LLM can help reconstruct this information into a more compact representation.

The transformation can be seen as:

```text
Code
  ↓
Structural Analysis
  ↓
System Model
  ↓
Semantic Documentation
```

Structural analysis tools can provide references, calls, and dependencies within the code and configuration they can resolve. A missing edge does not establish that behavior is unreachable: runtime registration, reflection, and consumers outside the repository may remain unresolved.

The LLM can then interpret these relationships and investigate their architectural or business meaning. A call graph alone does not establish transaction ownership, event delivery, or the history of shared state. Inspect those mechanisms before describing an operation's guarantees.

For example:

```text
OrdersController
    ↓
PlaceOrderHandler
    ↓
PricingService
    ↓
OrderRepository
    ↓
EventPublisher
```

can guide investigation of claims such as:

```text
PlaceOrderHandler is the orchestration boundary for order creation.

Pricing is resolved synchronously.

The order is persisted before downstream processing begins.

Inventory processing starts asynchronously after OrderCreated is published.
```

The structural graph provides **relationships**. The explanation of their meaning needs supporting code or execution evidence; the graph alone does not establish the claims above.

---

## Documentation as a Semantic Cache

Without architectural documentation, an agent working on a task may repeatedly perform:

```text
Read code
→ discover dependencies
→ reconstruct architecture
→ understand business flow
→ solve task
```

With good generated documentation, the process can become:

```text
Read architecture summary
→ inspect relevant implementation
→ solve task
```

Documentation therefore acts as a kind of **semantic cache for the repository**.

Instead of repeatedly reconstructing the same system model from raw code, agents can reuse an already prepared high-level representation.

This may improve:

- reasoning quality,

- task completion speed,

- context efficiency,

- consistency between agent sessions.

For very large repositories, this can be particularly important.

In token economics, this reconnaissance loop is brutal. An agent exploring an unfamiliar repository easily burns 30,000 to 50,000 tokens on multi-file grep and AST inspection before making its first edit. Pre-computed architectural cards drop that exploration tax to a couple thousand tokens of targeted navigation. More importantly, it acts as an architectural guardrail: without explicit documents stating module boundaries, an agent will take the path of least resistance—such as importing a repository across domains or executing direct cross-schema SQL joins.

---

## Why Tests Alone Cannot Replace Architectural Documentation

A common assumption is that an exhaustive test suite makes architectural documentation redundant—if the tests pass, the system is correct.

Tests and architectural models answer different questions. A functional test may verify an output without checking how the result was obtained. A coding agent could bypass an event-driven queue, query another service's private table, and still satisfy that assertion. Dedicated architecture or integration checks can examine those boundaries, but an ordinary output assertion does not do so automatically.

Passing tests establish agreement on the exercised cases and assertions. Documentation explains intended structure, data ownership, and navigation, but does not enforce them by itself. Use it to direct source review and executable checks where practical (see [[Executable Architecture Tests for Coding Agent Guardrails]]).

---

## Useful Levels of Generated Documentation

Generated documentation should exist at several levels.

### System Level

Describe the major runtime components.

Examples:

- web applications,

- APIs,

- workers,

- databases,

- message brokers,

- schedulers,

- caches,

- external integrations.

This answers:

> What does the system consist of?

---

### Module Level

For each module, describe:

- responsibility,

- owned data,

- public entry points,

- dependencies,

- emitted events,

- consumed events,

- architectural boundaries.

For example:

```text
Orders Module

Responsibility:
Owns the lifecycle of customer orders.

Owns:
- Order aggregate
- Orders database tables
- Order API

Depends on:
- Pricing synchronously
- Inventory asynchronously
- Payments asynchronously

Must not:
- modify inventory tables directly
- modify payment state directly
```

This kind of documentation is particularly useful for coding agents because it explicitly describes architectural constraints.

---

## Documentation Generated from Runtime Evidence

Static code analysis helps identify possible behavior within the code and configuration it can resolve. Runtime telemetry shows behavior exercised during particular runs. Neither provides a complete account alone: a trace may omit a rare failure, while static analysis may leave a dynamically selected implementation unresolved.

Useful sources include:

- distributed tracing,

- logs,

- metrics,

- event streams,

- production request traces.

Combining code analysis with runtime evidence can produce richer documentation.

For example:

```text
Code model:
API → Service A → Service B → Database

Runtime observation:

P50: 80 ms
P95: 420 ms
P99: 2.1 s
```

Or:

```text
Payment callback normally arrives within 3–10 seconds.

Approximately 2% of requests trigger one retry.

The reconciliation job handles unresolved payments after 15 minutes.
```

This transforms architectural documentation into something closer to an **operational model of the system**.

Grounding static analysis in APM metrics and OpenTelemetry traces prevents teams from architecting around theoretical assumptions. For instance, code analysis might show that a controller calls a pricing client and a repository. Telemetry exposes that the pricing client accounts for 75% of total P99 latency and that connection pools saturate under peak traffic. Feeding these runtime realities back into documentation ensures both human architects and AI agents optimize for real operational bottlenecks rather than imaginary ones.

---

## Key Principle

The most valuable generated documentation is usually **not information that is obvious from one source file**.

Automatically documenting every method:

```text
GetOrder retrieves an order.
SaveOrder saves an order.
```

adds little value.

Instead, generation should focus on information that requires understanding relationships across the repository:

- module boundaries,

- responsibilities,

- ownership,

- dependencies,

- operation flows,

- asynchronous behavior,

- state transitions,

- side effects,

- failure paths,

- architectural invariants.

This is precisely the information that is expensive for both humans and agents to reconstruct repeatedly.

---

## Broader Model

The long-term architecture of AI-assisted software development may therefore look less like:

```text
Documentation
    ↓
   Code
```

and more like:

```text
        Specification
             ↕
     Semantic Architecture
        ↙            ↘
     Code           Diagrams
       ↕                ↕
Structural Graph    Runtime Model
        \              /
         \            /
          Agent Context
```

Code, documentation, graphs, diagrams, telemetry, and specifications become different representations of the same system.

Each representation can validate and enrich the others.

The result is not simply "automatically generated documentation".

It is a **living semantic model of the software system** that can be consumed by both humans and AI agents (see [[The Living Engineering Chronicle and Context Compaction]] and [[In-Flight Documentation as the Primary Framework for Coding Agents]]).

## Related Notes

- [[The Living Engineering Chronicle and Context Compaction]] — Compacting ongoing decisions into living context anchors.
- [[In-Flight Documentation as the Primary Framework for Coding Agents]] — Real-time documentation as a coordination protocol for coding agents.
- [[Comments May Become More Valuable in AI-Generated Code]] — Preserving operational rationale and semantic constraints directly in code.
- [[Refactoring Legacy Systems with AI Agents]] — Using semantic code extraction to safely decompose legacy architectures.
