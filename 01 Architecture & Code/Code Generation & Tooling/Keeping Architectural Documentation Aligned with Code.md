---
title: "Keeping Architectural Documentation Aligned with Code"
tags:
  - documentation
  - software-architecture
  - code-review
  - knowledge-management
  - automation
aliases:
  - "Continuous Architectural Documentation"
  - "Architectural Diff and Documentation Drift"
  - "Versioned Evidence for Living Architecture Notes"
---

A pull request moves a notification to a queue. The code diff shows the changed files, while the useful architectural change is that completion now depends on a worker, delivery can be delayed, and new failure and retry paths exist. Documentation should make that difference reviewable.

Generated descriptions need a lifecycle. Establish the source revision and configuration, reconstruct the behavior affected by a change, compare it with the intended architecture and previous description, and review the evidence before treating the new description as current knowledge. A trace shows an exercised path; it cannot establish that no other path exists.

[[AI-Generated Architectural Documentation from Code]] develops reconstruction and its evidence limits. [[Documenting Business Operations with Diagrams and Operation Cards]] describes operation-centered views and diagrams. This article follows the maintenance loop and includes the operation-card representation so a reader can see what is being versioned and checked.

## Intended Architecture vs Implemented Architecture

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

## Architectural Diff

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

Reviewing architectural diffs shifts pull request evaluation from line-by-line syntax checking to system-level impact analysis. A tech lead or reviewer can immediately see if a PR introduces an eventual consistency window, adds an unauthorized inter-module coupling, or changes an SLA boundary—issues that are almost invisible when scanning 500 lines of modified implementation code.

---

## A Possible Documentation Structure

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

## Continuous Documentation

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

## Human Documentation and AI Documentation May Differ

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

Treat an architectural description as a claim tied to a source revision and evidence. Refresh the affected claims when behavior changes, preserve useful intended constraints, and make disagreements visible instead of silently replacing one account with another.

## Related Notes

- [[AI-Generated Architectural Documentation from Code]] — The evidence behind reconstructed architecture and its limitations.
- [[Documenting Business Operations with Diagrams and Operation Cards]] — Operation cards and diagrams that expose behavior across modules and time.
- [[The Living Engineering Chronicle and Context Compaction]] — Preserving evolving decisions and useful context through ongoing development.
