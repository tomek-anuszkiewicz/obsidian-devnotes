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
---

## Idea

LLMs can be used not only to generate code from specifications, but also to reconstruct documentation, architecture, and system behavior from existing code—a vital tool when [[Refactoring Legacy Systems with AI Agents|refactoring legacy systems with AI agents]].

This is especially useful for preserving [[LLM Agents and Institutional Memory|institutional memory in software teams]] and managing systems with:

- legacy systems created before widespread AI adoption,
    
- systems with incomplete or outdated documentation,
    
- large repositories where the architecture is difficult to infer,
    
- codebases where architectural knowledge exists mostly in developers' heads.
    

The goal is not merely to generate class or method descriptions.

The more valuable goal is to create a **semantic model of the system** (serving as [[In-Flight Documentation as the Primary Framework for Coding Agents|in-flight documentation for coding agents]]) that explains:

- what components exist,
    
- what they are responsible for,
    
- how they communicate,
    
- how data flows through the system,
    
- how important business operations execute,
    
- what happens synchronously and asynchronously,
    
- what state transitions exist,
    
- what architectural rules and invariants are implicit in the code.
    

---

# Code as a Source of Architectural Knowledge

Existing source code contains a large amount of architectural information, helping clarify [[What Should Organizations Preserve from AI-Assisted Development|what organizations should preserve from AI-assisted development]].

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

Structural analysis tools such as dependency graphs, call graphs, symbol graphs, GitNexus, Graphify, or static analysis can provide reliable structural facts.

The LLM can then interpret these facts and describe their architectural or business meaning.

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

can be interpreted as:

```text
PlaceOrderHandler is the orchestration boundary for order creation.

Pricing is resolved synchronously.

The order is persisted before downstream processing begins.

Inventory processing starts asynchronously after OrderCreated is published.
```

The structural graph provides **relationships**.

The LLM adds **meaning**.

---

# Documentation as a Semantic Cache

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

### 1. Token Usage and Inference Economics
- **Amortizing the Reconnaissance Tax**: Without high-level summaries, agents spend dozens of tool calls reading raw source files (controllers, services, repositories, configurations) simply to map the mutation surface. Architectural documentation collapses thousands of lines of raw code into compact topological summaries (such as Operation Cards or Module Specs), amortizing the cognitive reconstruction cost across every subsequent agent interaction.
- **Reducing Turn-Count Multipliers**: In iterative agentic tool loops, each conversational turn re-submits previous history plus new tool outputs. Slashing exploratory reconnaissance calls directly prevents exponential context accumulation, drastically reducing cumulative prompt token consumption.
- **Hardware-Level Prompt and KV-Cache Alignment**: Static, highly standardized semantic documentation modules serve as invariant prompt prefixes. Modern inference providers can leverage KV-cache reuse on these deterministic prefixes, yielding significant latency and cost discounts compared to volatile, dynamically queried code snippets.

### 2. Attention Density and Signal-to-Noise Ratio
- **Preventing "Lost-in-the-Middle" Attention Dilution**: Raw source code is dominated by syntactic ceremony—boilerplate, imports, type declarations, serialization annotations, and low-level loop mechanics. As formalized in [[Retrieval-Augmented Generation and Context Architecture]], injecting raw files dilutes transformer self-attention. A semantic cache isolates pure relational invariants, state boundaries, and data ownership contracts, maximizing token attention density.
- **Preserving Context Window Headroom for Complex Reasoning**: By loading high-density semantic abstractions instead of raw file trees, agents retain maximum context capacity for multi-step reasoning, execution traces, diff generation, and compiler error triage, directly raising the complexity ceiling of solvable tasks (see [[How LLM Systems Build Context]]).
- **Eliminating Premature Context Window Compaction**: When agents exhaust their context windows during exploratory code reading, session compaction or sliding-window truncation is triggered. Compaction frequently discards subtle architectural constraints. A semantic cache keeps working memory lean, bypassing compaction loss.

### 3. Latency and Cold-Start Velocity
- **Zero-Turn Cold Start (Time-to-First-Mutation)**: Bypassing the exploratory search phase enables the agent to transition immediately from problem statement to implementation. The agent skips blind grep-and-read cycles and navigates directly to the target component.
- **Minimizing Cognitive Trajectory Variance**: Without an architectural map, agents frequently explore irrelevant code paths, rabbit-holing into downstream libraries or legacy adapters. A semantic cache provides a deterministic topological index, bounding the search space.

### 4. Multi-Agent and Cross-Session Cohesion
- **Shared Ontological Baseline Across Agent Swarms**: When multiple subagents work in parallel (e.g., frontend, backend, migrations, integration tests), a shared semantic cache ensures that every worker shares an identical mental model of domain boundaries and interface contracts. Without this shared cache, independent agents construct divergent, conflicting abstractions.
- **Defending Invariants Against Status-Quo Rationalization**: Raw code often contains historical cruft and accidental coupling. LLMs naturally pattern-match against existing code smells and reproduce them. A canonical semantic cache explicitly documents non-negotiable architectural invariants (e.g., *"Module A must never directly access Module B's database"*), anchoring autonomous mutations to intended design rather than legacy entropy.
- **Cross-Session Determinism**: Successive agent sessions remain architecturally aligned over days or weeks, preventing the architectural drift that occurs when different models or prompts reconstruct system intent differently.

### 5. Architectural Invariant Auditing and Drift Detection
- **Cache Misses as Architectural Signals**: When an agent attempts an implementation that cannot be resolved against the semantic cache—or when a proposed change violates a cached constraint—it indicates architectural novelty or boundary drift.
- **Automated Cache Invalidation**: Treating documentation as a cache establishes a clean invalidation lifecycle: when code mutations alter symbols or call graphs, CI pipelines invalidate and recompile the affected semantic documentation slices, maintaining a zero-drift living architecture.

For very large repositories, operating documentation as a semantic cache is not merely an ergonomic convenience—it is an absolute economic necessity that directly dictates the feasibility and cost-effectiveness of autonomous software engineering.

---

# Useful Levels of Generated Documentation

Generated documentation should exist at several levels.

## 1. System Level

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

## 2. Module Level

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

# Operation-Oriented Documentation

Some of the most useful documentation should be organized around **business operations**, not classes.

Examples:

- Place Order
    
- Cancel Order
    
- Confirm Payment
    
- Issue Refund
    
- Register Customer
    

A single operation may involve multiple modules and continue over time.

An operation document can contain:

- purpose,
    
- entry points,
    
- participating components,
    
- sequence of steps,
    
- data changes,
    
- events,
    
- asynchronous processing,
    
- failure modes,
    
- state transitions,
    
- links to relevant source code.
    

Example:

```text
ConfirmPayment

Purpose:
Confirm an authorized payment and start downstream fulfillment.

Entry points:
- POST /payments/{id}/confirm
- PaymentConfirmationWorker

Flow:

1. Validate request
2. Load payment
3. Verify payment state
4. Call external payment provider
5. Persist Confirmed state
6. Publish PaymentConfirmed
7. Accounting processes the event asynchronously

Failure modes:
- payment not found
- invalid state
- provider timeout
- event publication failure
```

This can be significantly more useful than documentation organized around individual classes.

---

# Generated Architectural Diagrams

LLMs can also generate diagrams from reconstructed system knowledge.

These diagrams should preferably be stored as structured text such as:

- Mermaid,
    
- PlantUML,
    
- Graphviz,
    
- JSON graphs,
    

rather than only as images.

This makes them:

- versionable,
    
- diffable,
    
- editable,
    
- readable by agents,
    
- regenerable into visual diagrams.
    

---

# Component Diagrams

Component diagrams show the major parts of the system and their dependencies.

Example:

```text
Client
   ↓
API
   ↓
Orders
   ├── PostgreSQL
   ├── Pricing
   └── Message Broker
             ↓
          Inventory
             ↓
         Inventory DB
```

They answer:

> Which components exist and how are they connected?

---

# Sequence Diagrams

Sequence diagrams are especially useful for reconstructing how a concrete operation executes.

They show:

- who calls whom,
    
- in what order,
    
- request-response boundaries,
    
- event publication,
    
- callbacks,
    
- retries,
    
- asynchronous continuation.
    

Example:

```text
Client
  → Orders API
  → PlaceOrderHandler
  → Pricing
  → Orders DB
  → Event Broker

Event Broker
  → Inventory Consumer
  → Inventory DB
```

These diagrams expose behavior that may otherwise be distributed across many parts of the repository.

---

# Temporal and Asynchronous Flow Diagrams

A particularly valuable type of generated documentation is a diagram showing how one logical operation is distributed over time.

Many real systems do not execute as:

```text
request
→ business logic
→ response
```

Instead they behave more like:

```text
T0
Client sends request

T0 + milliseconds
API validates request

T0 + milliseconds
State is persisted

T0 + milliseconds
Event is published

T0 + milliseconds
API returns 202 Accepted

T0 + seconds
Consumer receives event

T0 + seconds
Inventory is reserved

T0 + seconds/minutes
External provider responds

T0 + minutes
Final status is updated
```

This distinction is extremely important.

An API response may mean only:

> the operation was accepted for processing

rather than:

> the entire business process completed successfully.

Temporal diagrams can make this explicit.

They can show:

- immediate processing,
    
- delayed work,
    
- scheduler execution,
    
- queue waiting,
    
- retries,
    
- callbacks,
    
- eventual consistency,
    
- timeout boundaries.
    

This is particularly valuable when debugging distributed systems.

---

# Data Flow Diagrams

Data-flow documentation explains:

- where data originates,
    
- how it is transformed,
    
- who owns it,
    
- where it is stored,
    
- where it is copied,
    
- which events contain it.
    

For example:

```text
HTTP Request
   ↓
CreateOrderCommand
   ↓
Order Aggregate
   ↓
Orders Database
   ↓
OrderCreated Event
   ↓
Inventory Projection
```

This can help answer questions such as:

- Where is `CustomerTier` calculated?
    
- Which service owns `FinalPrice`?
    
- When does the order status change?
    
- Why does one system contain stale data?
    
- Which service is the source of truth?
    

---

# State Machines

For complex business entities, documentation should extract and formalize explicit **state machines**. Real-world business entities rarely progress in simple linear sequences; they branch across retries, transient states, asynchronous validations, manual interventions, disputes, and terminal states.

Below is an architectural state machine representing an asynchronous payment and settlement lifecycle:

```text
                            ┌────────────────────────┐
                            │      INITIALIZED       │
                            └───────────┬────────────┘
                                        │ AuthorizePaymentCommand
                                        ▼
                            ┌────────────────────────┐
                            │      AUTHORIZING       │◄─────────────────────────────┐
                            └─────┬────────────┬─────┘                              │
     [Hard Decline / Auth Error]  │            │  [Provider Timeout / Network Drop] │
  ┌───────────────────────────────┘            └────────────────────┐               │
  │                                                                 │               │
  ▼                                                                 ▼               │ [RetryCount < Max]
┌────────────────────────┐                               ┌──────────────────────┐   │ (Exp. Backoff)
│        DECLINED        │                               │   RETRY_SCHEDULED    ├───┘
│       (Terminal)       │                               └──────────┬───────────┘
└────────────────────────┘                                          │ [RetryCount >= Max]
                                                                    ▼
                                                         ┌──────────────────────┐
                                                         │   SUSPENDED_AUDIT    │
                                                         │ (Reconciliation Job) │
                                                         └──────────┬───────────┘
                               Reconciliation Expired /             │
                               Manual Void                          │
  ┌─────────────────────────────────────────────────────────────────┼─────────────────────────────────┐
  │                                                                 │ Reconciled Verified             │ Reconciled Error /
  ▼                                                                 ▼                                 │ Unrecoverable
┌────────────────────────┐                              ┌────────────────────────┐                    ▼
│       CANCELLED        │                              │       AUTHORIZED       │         ┌──────────────────────┐
│       (Terminal)       │                              └───────────┬────────────┘         │RECONCILIATION_FAILED │
└────────────────────────┘                                          │                      │    (Terminal/DLQ)    │
                                                                    │                      └──────────────────────┘
                                       ┌────────────────────────────┴─────────────┐
                                       │ CapturePaymentCommand                    │
                                       ▼                                          │ VoidPaymentCommand
                            ┌────────────────────────┐                            ▼
                            │       CAPTURING        │                 ┌────────────────────────┐
                            └─────┬────────────┬─────┘                 │         VOIDED         │
        [Capture Succeeded]       │            │                       │       (Terminal)       │
     ┌────────────────────────────┘            │                       └────────────────────────┘
     │                                         │ [Settlement Failure / Drop]
     ▼                                         ▼
┌────────────────────────┐          ┌────────────────────────┐
│        SETTLED         │          │   SETTLEMENT_FAILED    │
│  (Terminal Happy Path) │          │  (Escalate to DLQ/Ops) │
└───────────┬────────────┘          └────────────────────────┘
            │
            ├──────────────────────────────────────────┐
            │ DisputeInitiatedEvent                    │ RefundRequestedCommand
            ▼                                          ▼
┌────────────────────────┐                 ┌────────────────────────┐
│        DISPUTED        │                 │       REFUNDING        │
└─────┬────────────┬─────┘                 └─────┬────────────┬─────┘
      │            │                             │            │
      │DisputeLost │DisputeWon                   │Full Refund │Partial Refund
      ▼            ▼                             ▼            ▼
┌──────────┐ ┌───────────┐                 ┌───────────┐ ┌──────────────────┐
│ CHARGED_ │ │  SETTLED  │                 │ REFUNDED  │ │PARTIALLY_REFUNDED│
│   BACK   │ │(Restored) │                 │(Terminal) │ │   (Terminal)     │
└──────────┘ └───────────┘                 └───────────┘ └──────────────────┘
```

### State Machine Transition Contract

To make state machines actionable for LLM coding agents, the generated documentation should formalize transitions into a deterministic matrix:

| Source State | Trigger (Command / Event) | Guard Condition | Target State | Emitted Domain Event | Side Effects |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `INITIALIZED` | `AuthorizePaymentCommand` | Valid request payload | `AUTHORIZING` | `PaymentAuthorizingEvent` | Dispatches external gateway RPC |
| `AUTHORIZING` | Gateway Decline Response | Hard decline from issuer | `DECLINED` | `PaymentDeclinedEvent` | Releases reserved inventory |
| `AUTHORIZING` | Gateway Timeout / Drop | `RetryCount < MaxRetries` | `RETRY_SCHEDULED` | `PaymentRetryScheduledEvent` | Registers timer with exponential jitter |
| `RETRY_SCHEDULED`| Retry Timer Fired | `RetryCount < MaxRetries` | `AUTHORIZING` | `PaymentAuthorizingEvent` | Re-executes gateway RPC with idempotency key |
| `RETRY_SCHEDULED`| Retry Timer Fired | `RetryCount >= MaxRetries`| `SUSPENDED_AUDIT` | `PaymentSuspendedEvent` | Enqueues to reconciliation worker |
| `SUSPENDED_AUDIT`| `ReconcilePaymentCommand`| Ledger verifies success | `AUTHORIZED` | `PaymentAuthorizedEvent` | Unblocks order fulfillment workflow |
| `SUSPENDED_AUDIT`| `ReconcilePaymentCommand`| Ledger confirms drop | `CANCELLED` | `PaymentCancelledEvent` | Compensates previous reservation sagas |
| `AUTHORIZED` | `CapturePaymentCommand` | Within capture window | `CAPTURING` | `PaymentCapturingEvent` | Dispatches settlement instruction |
| `AUTHORIZED` | `VoidPaymentCommand` | Pre-capture cancellation | `VOIDED` | `PaymentVoidedEvent` | Issues gateway reversal transaction |
| `CAPTURING` | Settlement Confirmation | Bank clears funds | `SETTLED` | `PaymentSettledEvent` | Triggers final accounting journal entry |
| `SETTLED` | `RefundRequestedCommand` | `Amount <= RemainingBalance`| `REFUNDING` | `PaymentRefundInitiatedEvent`| Initiates downstream payout transaction |
| `SETTLED` | `DisputeInitiatedEvent` | Chargeback notification | `DISPUTED` | `PaymentDisputedEvent` | Freezes merchant dispute funds |

State machines prevent agents from generating illegal, out-of-order mutations (e.g., executing a capture on an un-authorized or expired transaction).

---

# Failure-Path Documentation

Documentation must not describe only the happy path. In distributed architectures, failure paths represent the majority of operational complexity: timeouts, partial writes, network partitions, circuit trips, retry exhaustion, and compensating rollbacks.

Below is an architectural topology mapping how an operation navigates failure domains:

```text
[Incoming Command / HTTP Mutation Request]
                  │
                  ▼
      ┌───────────────────────┐
      │ 1. Invariant & Schema ├─────[Schema / Domain Validation Error]────► 422 Unprocessable (Zero State Mutation)
      │      Validation       │
      └───────────┬───────────┘
                  │ Validation Passed
                  ▼
      ┌───────────────────────┐
      │ 2. Optimistic Locking ├─────[Version Conflict / DB Disconnect]────► Transient Error / Jittered Backoff & Retry
      │    & State Persist    │
      └───────────┬───────────┘
                  │ Committed
                  ▼
      ┌───────────────────────┐
      │ 3. External Gateway   ├─────[HTTP 4xx Non-Retryable Error]────────► Terminal Decline (Publish OperationDeclined)
      │    RPC Invocation     │
      └───────────┬───────────┘
                  │ [HTTP 5xx / TCP Timeout / Network Partition]
                  ▼
      ┌───────────────────────┐
      │ 4. Circuit Breaker    ├─────[Circuit OPEN / Rate-Limit Exceeded]──► Fast-Fail Fallback (Queue to Durable Outbox)
      │         Gate          │
      └───────────┬───────────┘
                  │ Circuit CLOSED / HALF-OPEN
                  ▼
      ┌───────────────────────┐
      │ 5. Resilient Retry    │◄────┐ [Attempt <= MaxRetries]
      │      Loop Block       │     │ (Exponential Backoff + Full Jitter)
      └───────────┬───────────┘     │
                  │                 │
                  ├─────────────────┘
                  │ [Retries Exhausted / Unresponsive]
                  ▼
      ┌───────────────────────┐
      │ 6. Compensating Saga  ├─────[Compensation Succeeded]──────────────► State: CANCELLED (Emits CompensatedEvent)
      │     Orchestrator      │
      └───────────┬───────────┘
                  │ [Compensation Failed / Inconsistent Partial State]
                  ▼
      ┌───────────────────────┐
      │ 7. Dead-Letter Queue  ├─────► High-Priority Alert (PagerDuty / Ops Slack)
      │     & Manual Audit    ├─────► Escalate to Human Reconciliation Dashboard
      └───────────────────────┘
```

### Distributed Failure Mitigation Matrix

| Failure Stage | Error Vector | Detection Mechanism | Immediate Action | Final State Outcome | Compensation / Recovery Vector |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ingress & Schema** | Malformed JSON, invariant violation | Static validator middleware | Reject synchronously (422) | No state created | None required (pure function boundary) |
| **Local Persistence** | Concurrency conflict, DB disconnect | DB driver exception / Stale Object | Exponential backoff retry | `INITIALIZED` | Retry transaction up to 3 times |
| **External Provider** | Invalid credentials, account frozen | HTTP 400/401/403 response | Abort immediately | `DECLINED` | Release local reservations, notify client |
| **Network Substrate** | TCP timeout, HTTP 502/503/504 | Connection pool / socket timeout | Hand off to retry scheduler | `RETRY_SCHEDULED` | Exponential backoff with decorrelated jitter |
| **Gateway Congestion** | Rate limits exceeded (HTTP 429) | Circuit breaker trip | Divert to durable outbox | `SUSPENDED_AUDIT` | Throttled background drain when circuit resets |
| **Retry Exhaustion** | 3 successive timeouts | Attempt counter overflow | Trigger compensating saga | `CANCELLED` | Roll back inventory locks, issue reversal |
| **Partial Failure** | Compensation step crashes | Saga transaction failure | Route payload to Dead-Letter Queue | `RECONCILIATION_FAILED` | Human operator intervention via admin dashboard |

### Why Failure-Path Documentation Is Vital for Coding Agents

LLM coding agents have a documented **happy-path cognitive bias**: when prompted to implement or modify a feature, they routinely assume zero-latency networks, immediate database consistency, and infallible third-party APIs. 

Explicit failure-path documentation forces the agent to:
1. **Enforce Idempotency**: Guard every mutation against duplicate execution during automatic retries.
2. **Implement Compensating Logic**: Ensure that partial failures trigger explicit clean-up handlers rather than leaving orphaned database rows.
3. **Handle Eventual Consistency**: Prevent agents from writing synchronous reads immediately following asynchronous command dispatch.

---

# Multiple Levels of Detail

A single diagram for the entire system quickly becomes unreadable.

Documentation should therefore support different zoom levels.

## Level 1 — Business View

```text
Customer
→ Orders
→ Payments
→ Inventory
→ Shipping
```

## Level 2 — Architectural View

```text
REST API
→ Command Handler
→ Database
→ Message Broker
→ Consumer
```

## Level 3 — Implementation View

```text
POST /orders
→ PlaceOrderController
→ PlaceOrderCommand
→ PlaceOrderHandler
→ PricingClient
→ OrderRepository
→ UnitOfWork
→ EventPublisher
```

Agents can then load only the level of detail relevant to the current task.

---

# Intended Architecture vs Implemented Architecture

Generated documentation remains useful even when the original system was created from an existing specification.

In that case there are two distinct representations:

```text
Intended architecture
        ↓
       Code
        ↓
Reconstructed architecture
```

The original documentation describes:

> how the system is supposed to work.

The reconstructed documentation describes:

> how the system actually works.

Comparing them can reveal **architecture drift**.

Examples:

- documentation says communication is asynchronous, but implementation performs synchronous HTTP calls,
    
- modules were supposed to be isolated, but one module accesses another module's database,
    
- a validation step described in the specification is missing,
    
- a new cache or queue exists in code but not in documentation,
    
- implementation contains additional business exceptions,
    
- an originally simple workflow evolved into several consumers and retries.
    

This gives a useful validation loop:

```text
Specification
      ↓
Implementation
      ↓
Reconstructed Model
      ↓
Compare with Specification
```

---

# Architectural Diff

The same idea can be applied between versions of the repository.

Instead of asking only:

> What files changed?

the system can answer:

> What changed architecturally?

For example:

```text
Before:

Orders
→ Payments synchronously


After:

Orders
→ PaymentRequested event
→ Payment Consumer
→ Payments
```

The generated architectural diff could report:

```text
Payment processing changed from synchronous communication
to asynchronous event-driven communication.

A new failure mode was introduced:
PaymentRequested may remain unprocessed if the consumer is unavailable.

Order completion is now eventually consistent.
```

This could be very useful during pull request review.

---

# Documentation Generated from Runtime Evidence

Static code analysis describes what the system **can do**.

Runtime telemetry can show what the system **actually does**.

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

---

# A Possible Documentation Structure

A repository could contain:

```text
/docs

    system-overview.md

    modules/
        orders.md
        payments.md
        inventory.md
        shipping.md

    flows/
        place-order.md
        cancel-order.md
        confirm-payment.md
        refund-payment.md

    states/
        order-state.md
        payment-state.md

    architecture/
        module-boundaries.md
        data-ownership.md
        integrations.md
        event-topics.md

    diagrams/
        system.mmd
        place-order-sequence.mmd
        payment-timeline.mmd
        order-state-machine.mmd
```

The documentation does not need to be large.

Small, structured documents are often more useful for agents than large narrative documents.

---

# Operation Cards

An especially useful abstraction may be an **Operation Card**.

Each important operation receives a compact description containing everything needed to understand it.

For example:

```text
Operation: ConfirmPayment

Purpose:
Confirm an authorized payment.

Entry points:
- POST /payments/{id}/confirm

Components:
- Payments API
- Payments Domain
- PostgreSQL
- External PSP
- Event Broker
- Accounting Consumer

Synchronous steps:
1. Validate request
2. Load payment
3. Validate state
4. Confirm with PSP
5. Save status

Asynchronous steps:
6. Publish PaymentConfirmed
7. Accounting updates ledger

State transition:
Authorized → Confirmed

Failure modes:
- invalid state
- PSP timeout
- persistence failure
- publication failure
```

From the same structured representation, the system could generate:

- human-readable documentation,
    
- Mermaid diagrams,
    
- LLM context,
    
- tests,
    
- review checklists.
    

---

# Continuous Documentation

Documentation generation does not have to be a one-time migration project.

It can become part of the development lifecycle.

A possible process:

```text
Developer / Agent creates PR
        ↓
Changed symbols detected
        ↓
Affected modules and flows identified
        ↓
Architectural model regenerated
        ↓
Relevant documentation updated
        ↓
Architectural diff generated
        ↓
Consistency with intended design checked
```

This creates a form of **living architecture documentation**.

Instead of manually maintaining every diagram, the repository continuously reconstructs its own architectural representation.

---

# Human Documentation and AI Documentation May Differ

Traditional documentation is optimized primarily for people.

Documentation intended as LLM context may have different priorities.

For agents, concise structural facts can be more valuable than long prose.

For example:

```text
Module: Orders

Owns:
- Order
- OrderLine

Writes:
- orders.*
- order_lines.*

Reads:
- pricing.read_model

Calls synchronously:
- Pricing

Publishes:
- OrderCreated
- OrderCancelled

Consumes:
- PaymentConfirmed
- InventoryRejected

Forbidden:
- direct writes to payment.*
- direct writes to inventory.*
```

This format is extremely compact while providing high-value architectural constraints.

The same repository can therefore maintain:

```text
Human documentation
+
Machine-oriented semantic documentation
```

generated from the same underlying model.

---

# Key Principle

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

# Broader Model

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

It is a **living semantic model of the software system** that can be consumed by both humans and AI agents.
---

## Relationship to the Knowledge Graph

- **[[Comments May Become More Valuable in AI-Generated Code]]**: How decision-focused comments form the raw semantic material for living architectural docs.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Generating documentation concurrently during development as a deterministic blueprint and token-efficient framework.
- **[[Retrieval-Augmented Generation and Context Architecture]]**: Context minimization and attention density mechanics underlying semantic caching.
- **[[How LLM Systems Build Context]]**: Engineering working memory and context headroom for coding agent decision loops.
- **[[What Should Organizations Preserve from AI-Assisted Development]]**: Preserving decision traces and architectural rationale as strategic intellectual property.
- **[[LLM Agents and Institutional Memory]]**: Connecting living documentation to corporate history and onboarding workflows.
- **[[Designing Software for AI Agents]]**: Structuring code to make semantic extraction and architectural diagrams reliable.
- **[[Introduction to RAG]]**: Indexing living architecture documents to provide high-precision context for development agents.
