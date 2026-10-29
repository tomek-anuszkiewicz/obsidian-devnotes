---
title: "Documenting Business Operations with Diagrams and Operation Cards"
tags:
  - documentation
  - software-architecture
  - diagrams
  - knowledge-management
  - reverse-engineering
aliases:
  - "Business Operation Documentation"
  - "Operation Cards and Architectural Diagrams"
  - "Documenting Async Flows States and Failure Paths"
---

A request to cancel an order can cross several modules, publish messages, wait for payment state, and finish after the API has returned. Documentation organized only by classes makes the reader reconstruct that operation again from scattered pieces.

An operation description should connect the entry point, ownership, state changes, synchronous and delayed work, and failure handling. Diagrams show particular relationships; a compact operation card records the scope, supporting evidence, source revision, and unresolved questions. Different readers can use different levels of detail without losing the common operation.

The sections below explain which views answer which questions. [[AI-Generated Architectural Documentation from Code]] develops how to reconstruct the underlying knowledge from code and runtime evidence. [[Keeping Architectural Documentation Aligned with Code]] follows how those descriptions are reviewed and kept current after changes.

## Operation-Oriented Documentation

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

## Generated Architectural Diagrams

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

## Component Diagrams

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

## Sequence Diagrams

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

## Temporal and Asynchronous Flow Diagrams

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

## Data Flow Diagrams

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

## State Machines

For important business entities, documentation can include generated state machines.

Examples:

- Order

- Payment

- Shipment

- Subscription

- Support Ticket

For example:

```text
Pending
   ↓
Confirmed
   ↓
Shipped
   ↓
Completed

Pending
   ↓
Cancelled

Confirmed
   ↓
Refunded
```

The generated documentation should ideally also describe:

- allowed transitions,

- conditions,

- commands causing transitions,

- events emitted,

- terminal states.

State machines are valuable because important business rules are often distributed across handlers, validators, and domain methods.

Making state boundaries explicit eliminates one of the most common agent bugs: invalid lifecycle leaps, such as updating an order directly from `Pending` to `Shipped` because the agent only saw the shipping service handler. Once terminal states and validation triggers are documented in the state machine, agents can verify whether a proposed mutation violates domain rules before modifying code.

---

## Failure-Path Documentation

Documentation should not describe only the happy path.

Failure paths can be even more valuable for maintenance.

Examples:

```text
Payment confirmation
   ↓
Provider timeout
   ↓
Retry
   ↓
Retry exhausted
   ↓
Payment remains Pending
   ↓
Manual reconciliation job
```

Useful failure information includes:

- retry behavior,

- timeout behavior,

- fallback logic,

- compensation,

- dead-letter queues,

- partial state,

- manual intervention.

This can make incident analysis significantly easier.

---

## Multiple Levels of Detail

A single diagram for the entire system quickly becomes unreadable.

Documentation should therefore support different zoom levels.

### Level 1 — Business View

```text
Customer
→ Orders
→ Payments
→ Inventory
→ Shipping
```

### Level 2 — Architectural View

```text
REST API
→ Command Handler
→ Database
→ Message Broker
→ Consumer
```

### Level 3 — Implementation View

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

Hierarchical zoom prevents attention degradation and context exhaustion. An agent solving a localized bug does not need to parse the entire codebase into its prompt; it routes down from the system view to locate the owning container, inspects the component boundary, and only pulls the specific implementation files required for the patch.

---

## Operation Cards

An especially useful abstraction may be an **Operation Card**.

Each important operation receives a compact description of its scope, behavior, supporting evidence, and unresolved questions.

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

The card should also record the source revision and relevant configuration, references to code and execution artifacts, and the assumptions behind individual claims. Separate source-derived findings, observed behavior, and hypotheses. For example, a call to a scheduler establishes neither durable job storage nor recovery after restart. Those claims require evidence from the scheduling and recovery paths.

Track unanswered questions beside the flow: who previously wrote the state being read, which transaction covers the writes, and what happens when a delayed step fails? A shared method's summary is reusable only when its assumptions fit the current operation. An explicit missing dependency is more useful than a complete-looking sequence diagram that guesses its behavior.

[[Recovering Legacy System Behavior with AI Agents]] describes how to develop these cards through alternating code inspection, observations, and characterization tests before a rewrite.

From the same structured representation, the system could generate:

- human-readable documentation,

- Mermaid diagrams,

- LLM context,

- tests,

- review checklists.

---

Select the representation by the question: component ownership, call order, delayed progress, copied data, allowed states, or recovery. Keep the source revision and evidence close enough that a reader can distinguish the described behavior from an unverified inference.

## Related Notes

- [[AI-Generated Architectural Documentation from Code]] — Recovering architectural knowledge from code, configuration, and observed execution.
- [[Keeping Architectural Documentation Aligned with Code]] — Reviewing architectural differences and maintaining generated descriptions.
- [[Recovering Legacy System Behavior with AI Agents]] — Investigating actual behavior before changing an existing system.
