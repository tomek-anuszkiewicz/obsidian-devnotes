---
title: Why Business Logic Is the Hardest Part of Agentic Coding
tags:
  - business-logic
  - ai-agents
  - software-engineering
  - domain-driven-design
  - specification
  - requirements
aliases:
  - Hardness of Business Logic in Agentic Coding
  - Domain Nuances vs Agent Capabilities
  - Business Semantics vs Technical Complexity
---

# Why Business Logic Is the Hardest Part of Agentic Coding

## Technical Plumbing Is Easy; Business Rules Are a Minefield

When working with autonomous coding agents, every developer quickly notices a strange contrast:

```text
TECHNICAL INFRASTRUCTURE (Syntax-Heavy, Standardized):
  - Concurrent queues, retry loops, distributed tracing
  - Database connection pools, schema migrations, Redis caching
  ──► Solved effortlessly by AI (Trained on millions of public open-source implementations)

BUSINESS RULES (Deceptively Simple Syntax, High Domain Ambiguity):
  - Accounting settlement boundaries, refund eligibility windows
  - Tax calculation exceptions, legacy customer tier overrides
  ──► High failure rate (Full of unwritten tribal knowledge and subtle domain traps)
```

An agent can set up an asynchronous processing pipeline with backoff, jitter, and OpenTelemetry instrumentation in 30 seconds. Yet in that exact same PR, it can completely misunderstand a two-line business condition.

Technical infrastructure code is syntactically complex, but its patterns are identical across thousands of companies. Real business logic looks deceptively simple—often just a few `if` statements—yet it carries years of unwritten corporate history, regulatory compromises, and edge-case exceptions.

---

## The Most Dangerous Bug: The Plausible Hallucination

The greatest risk with AI-generated code is never broken syntax or runtime crashes. Compilers and linters catch those immediately.

**The real killer is code that is:**
- Professionally structured and clean,
- Fully documented with readable comments,
- Covered by unit tests that pass,
- **Fundamentally wrong in its core business assumption.**

### The Classic Example
An agent sees `PaymentStatus.Paid` and naturally assumes money has been deposited into the company's bank account. In reality, in that company's billing system, `Paid` only means the payment gateway authorized the credit card. The actual funds aren't captured until a nightly settlement batch runs.

If the agent writes code that immediately unlocks a high-value shipment or writes to an irrevocable financial ledger based on that check, it creates a silent production bug that no compiler or standard test will catch.

---

## The Architectural Fix: Decouple Business Decisions from Technical I/O

To keep AI agents from breaking business logic, you must physically separate **Domain Decision Rules** from **Technical Execution Plumbing**:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. PURE DECISION FUNCTION (Zero I/O, Zero Side Effects)     │
│    Inputs:  (OrderSnapshot, PaymentSnapshot, CurrentTime)   │
│    Logic:   Deterministic rule evaluation                   │
│    Output:  Explicit Decision Enum (e.g., Allowed / Blocked)│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼ (Decision passed to execution)
┌─────────────────────────────────────────────────────────────┐
│ 2. TECHNICAL EXECUTION (I/O, Database, Network)             │
│    - Open database transaction                               │
│    - Save updated records                                    │
│    - Publish event to message broker                         │
│    - Emit telemetry metrics                                  │
└─────────────────────────────────────────────────────────────┘
```

### 1. The Pure Decision Function
The business logic should live in a pure function with zero database access, zero network calls, and zero framework magic:

```text
function can_cancel_order(order, payment, current_time):
    if order.is_already_cancelled:
        return CancellationDecision.ALREADY_CANCELLED

    if payment.is_locked_in_settlement_batch:
        return CancellationDecision.BLOCKED_PAYMENT_ALREADY_SETTLED

    if order.is_dispatched_to_warehouse:
        return CancellationDecision.BLOCKED_IN_FULFILLMENT

    return CancellationDecision.ALLOWED
```

Why is this pattern so powerful for AI-driven workflows?
1. **Instant Human Audit**: In code review, a human engineer can review the business logic in 15 seconds without being distracted by SQL queries, connection pools, or HTTP headers.
2. **Exhaustive Unit Tests**: Because the function has zero I/O, an agent can generate 30 fast unit tests covering every permutation of inputs without needing database mocks.
3. **Safe Infrastructure Refactoring**: The agent can completely rewrite, optimize, or migrate the database layer, queue system, or API framework with zero risk of corrupting the core business rule.

### 2. The Technical Execution Pipeline
Once the decision function emits an explicit result, the surrounding infrastructure code executes the side effects:

```text
decision = can_cancel_order(order, payment, clock.now())

if not decision.is_allowed:
    return map_rejection_to_response(decision)

execute_transaction:
    order.mark_as_cancelled(user_id, clock.now())
    order_repository.save(order)
    event_bus.publish(OrderCancelledEvent(order.id))
```

---

## Comments in Code: Explain "Why", Never "What"

When agents refactor code, their training pushes them to simplify and eliminate boilerplate. If a business condition looks redundant or unusual, an agent's reflex is to "clean it up" and remove it.

To stop agents from accidentally deleting vital business rules, write comments explaining **the non-obvious business reason and explicitly forbidding naive refactoring**:

```text
// BUSINESS RULE WARNING:
// In this payment system, credit card authorization happens immediately,
// but funds are not settled until the nightly batch.
// Cancellation is allowed until batch assignment, even if authorized.
// DO NOT refactor this check to: if (payment.status == PAID)
if payment.batch_settlement_id is not null:
    return CancellationDecision.BLOCKED_PAYMENT_ALREADY_SETTLED
```

### The Rule for Meaningful Comments
* **Useless Comment**: Explains *what* the code does (`// Save the order to repository`).
* **High-Value Comment**: Explains *why* the rule exists and *which* seemingly obvious refactoring would break business logic.

> **Code explains what happens. Comments explain why it must happen that way.**

---

## Summary: Keeping Business Rules Safe in the AI Era

1. **Trust Technical Implementation, Audit Business Logic**: Models know SQL, concurrency, and API frameworks inside out, but they do not know your company's unwritten policies.
2. **Separate Decisions from I/O**: Put business logic into pure, zero-dependency functions that return explicit decision enums.
3. **Protect Non-Obvious Rules with Comments**: Explicitly tell the agent why a weird condition exists and why it must not be simplified away.
4. **Test Permutations Deterministically**: Write fast, table-driven unit tests for every decision function to catch regressions before they reach production.

---

## Related Notes

- **[[Comments May Become More Valuable in AI-Generated Code]]**: How intentional comments protect non-obvious business rules from automated refactoring sweeps.
- **[[Designing Software for AI Agents]]**: Architectural guidelines for isolating pure decision components from technical I/O infrastructure.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: Why hidden abstractions and indirect framework magic make business logic harder for agents to understand.
- **[[What Should Organizations Preserve from AI-Assisted Development]]**: Capturing business decisions and domain context rather than just generated code.
- **[[LLM Agents and Institutional Memory]]**: How institutional history and tribal knowledge prevent agents from misinterpreting business requirements.
- **[[Testing in the Model, Agent, LLM Era]]**: Using deterministic test suites to lock down business assumptions against agent drift.

---

## Relationship to the Knowledge Graph

- **[[Data Access Economics with Coding Agents - ORMs vs Explicit SQL]]**: Keeping domain decisions isolated from database queries and persistence layers.
- **[[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]**: Ensuring business domain logic is explicit and discoverable rather than buried in framework middleware.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: Preventing zero-friction code generation from introducing silent business errors.
- **[[The 5-Layer System Stack for Agentic Software Engineering]]**: Placing business logic authority in Layer 5 (Human Intent) and Layer 2 (Verification Gates).
