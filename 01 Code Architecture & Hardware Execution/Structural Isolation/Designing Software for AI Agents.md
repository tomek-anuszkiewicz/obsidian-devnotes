---
title: Designing Software for AI Agents
tags:
  - software-architecture
  - system-design
  - ai-agents
  - agentic-coding
  - modularity
  - observability
aliases:
  - Agent-Oriented Software Design
  - Building Software for AI Consumption
  - Principles of Agentic System Design
  - Designing Discoverable Codebases
---

# Designing Software for AI Agents

## Core Principle: Discoverability and Explicit Contracts Beat Clever Shortcuts

Autonomous coding agents don't make software architecture obsolete; **they make good architecture more important than ever**.

When human developers build on top of a messy, ambiguous codebase, they waste hours in meetings and Slack threads deciphering implicit conventions. When an AI agent works on that same messy codebase, it burns thousands of tokens, hallucinates non-existent patterns, and casually spreads bugs across twenty files in seconds.

```text
HISTORICAL HUMAN-CENTRIC CODEBASE:
- Minimized typing to save human fingers
- Relied on implicit conventions, ambient context, deep inheritance, and runtime reflection
- High hidden complexity; easy to break things accidentally

AGENT-FRIENDLY CODEBASE:
- Maximizes discoverability and explicit contracts
- Uses 1:1 operation files, clear pipeline stages, and deterministic test oracles
- Code may be slightly more verbose, but has zero ambient magic and an isolated blast radius
```

An agent-friendly system provides fast, unambiguous answers to four simple questions:
1. **Where does the change belong?** (Locality)
2. **What contract must never break?** (Invariants)
3. **How do we prove it works in seconds?** (Test Oracle)
4. **What parts of the system are safe from side effects?** (Blast Radius)

---

## Code Length Is Not the Same as Cognitive Complexity

One of the biggest mistakes teams make when designing software for agents is trying to make code as short as possible.

An agent can reason through **twenty simple, explicit classes** with 100% accuracy. But it will fail constantly when trying to understand **five short classes** whose behavior depends on dynamic runtime scanning, reflection magic, or undocumented middleware ordering (see [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]).

### The Explicit Execution Standard

Compare these two approaches:

```text
MAGIC / IMPLICIT APPROACH (Confuses Agents):
// Where is authorization handled? Which filter runs first?
// Does this mutate a database transaction? Nobody knows without reading framework docs.
[CustomMagicFilter]
public Response Handle(Request req) => _service.DoThing(req);

EXPLICIT PIPELINE (Clear to Humans and Agents):
function handle_checkout(command: CheckoutCommand) -> CheckoutResult:
    check_user_permission(command.user_id, Permission.CHECKOUT)
    validate_cart_contract(command.cart)
    
    transaction:
        order = order_repository.create(command)
        outbox.record(OrderPlacedEvent(order.id))
        
    return CheckoutResult.success(order.id)
```

In the explicit version, the order of execution, transaction boundaries, and side effects are plainly visible in the code. Any agent reading this file immediately understands the workflow without searching through ten framework configuration files.

### Centralize Infrastructure, Keep Domain Flow Visible

This doesn't mean you should duplicate boilerplate everywhere. Standard infrastructure—like mapping exceptions to HTTP error envelopes or generating trace IDs—belongs in centralized middleware.

The boundary is simple:
- **Centralize generic technical plumbing** (logging formats, network serializers, metrics).
- **Keep domain logic and operational sequence explicit** (authorization, state transitions, validation, transaction boundaries).

---

## Monoliths vs. Microservices: Trade-offs for Agents

Agents don't care about architectural fashion. They care about **bounded reasoning scope and fast feedback loops**:

| Architectural Pattern | Why Agents Like It | Risks to Watch Out For |
| :--- | :--- | :--- |
| **Modular Monolith** | Single repository, instant local compilation, fast integration tests, compile-time type safety across modules. | Weak module boundaries let agents create tangled cross-domain dependencies; context bloat if the repo is huge. |
| **Microservices** | Small, focused codebases; explicit REST/gRPC interfaces; isolated blast radius. | Distributed contract drift; difficult multi-repo changes; testing requires complex local Docker harnesses. |

A well-structured **modular monolith with strictly enforced build boundaries** is often the sweet spot: it gives you the tight operational isolation of microservices without the pain of distributed network debugging.

---

## Explicit Communication Boundaries

Modules should communicate through clear, typed contracts rather than reaching into each other's internal classes or database tables:

1. **CQRS-Style Commands and Queries**: Express intent through immutable data structures (`CancelOrderCommand`, `GetCustomerSummaryQuery`).
2. **Discrete Operation Handlers**: Give each operation its own dedicated handler file (`CancelOrderHandler`). When a request comes in, the path from the API endpoint to the handler is a direct, 1:1 line.
3. **Avoid Kitchen-Sink Facades**: A single `OrderService` containing 40 unrelated methods creates a massive file that wastes agent context and invites merge conflicts. Break operations into focused handlers.

---

## Model Data to Eliminate Guesswork

When designing domain models, make invalid states impossible to represent:

- **Ban Multi-Purpose Nulls**: Never let `null` mean both *"value hasn't been fetched yet"* and *"value does not exist"*.
- **Eliminate Magic Sentinel Values**: Never use `0` or `-1` to represent infinite retries or disabled features; use explicit enums or optional types.
- **Stop Context-Dependent Fields**: A property named `amount` shouldn't mean wholesale supplier cost in one file and retail customer price in another. Name them `supplier_cost_cents` and `customer_price_cents`.
- **Use Enums Instead of Vague Booleans**: Replace boolean flags like `is_active` with explicit lifecycle states (`AccountStatus.SUSPENDED_FOR_NONPAYMENT`).

> **Do not minimize the number of fields in your models. Minimize the number of possible interpretations.**

---

## Break Multi-Step Workflows into Explicit Data Stages

Avoid the anti-pattern of passing a giant, mutable `Context` object through 15 methods, where fields are mysteriously added, modified, or overwritten along the way.

Instead, structure complex pipelines as a sequence of typed transformations:

```text
RawSupplierQuote
      │
      ▼
[Validation Stage]    ──► ValidatedSupplierData
      │
      ▼
[Normalization Stage] ──► NormalizedCostModel
      │
      ▼
[Pricing Rules]       ──► CustomerFinalPrice
      │
      ▼
[Audit Generator]     ──► AuditedPriceRecord
```

Each stage takes an immutable, typed input and produces an immutable, typed output. If a bug appears in the pricing rules, the agent can inspect and test that single stage in isolation without worrying about side effects.

---

## Practical Architectural Rules

1. **Keep the path from request to code direct**: Any engineer or agent should be able to jump from an API endpoint to its business handler in under 10 seconds using symbol search.
2. **Enforce 1:1 operation files**: Give every distinct command and query its own dedicated file to prevent collateral damage (see [[Software Decay and the Hidden Costs of Frictionless AI Code|controlling generative code entropy]]).
3. **Make transaction and error boundaries visible**: Don't hide database commits or rollbacks behind magic attributes; keep state changes explicit.
4. **Decompose complex state transitions**: Use typed pipeline stages instead of mutating a giant shared dictionary or context object.
5. **Back architecture with automated test suites**: Ensure the test runner gives instant pass/fail feedback so agents can verify their work autonomously (see [[Testing in the Model, Agent, LLM Era|automated test verification]]).

---

## Related Notes

- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: Why unconstrained agents create complexity sprawl and how mechanical isolation keeps codebases clean.
- **[[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]**: Why magic frameworks, reflection, and hidden indirection derail agentic reasoning.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: How codebase structure, file layouts, and naming conventions adapt when machines write the code.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Replacing heavy framework scaffolding with structured markdown specs and Operation Cards.
- **[[Data Access Economics with Coding Agents - ORMs vs Explicit SQL]]**: Structuring persistence layers and contract tests for agentic workflows.
- **[[Scaling a Modular Monolith with Local-or-Remote Module Execution]]**: Implementing module boundaries that preserve local reasoning while allowing distributed scaling.
- **[[Testing in the Model, Agent, LLM Era]]**: How deterministic automated tests act as the essential verification floor for agentic development.
