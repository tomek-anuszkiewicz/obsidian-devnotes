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

## Business Logic Is Harder Than Technical Complexity

An agent may easily generate:

- a concurrent processing pipeline,
    
- retry logic,
    
- caching,
    
- generic abstractions,
    
- telemetry,
    
- a large integration class,
    
- technically sophisticated infrastructure.
    

At the same time, it may misunderstand a short business condition.

Technical code can be syntactically complex but semantically familiar. Business logic may consist of several `if` statements while depending on hidden concepts, historical exceptions, regulatory rules, and organization-specific meaning.

For example, the agent may incorrectly assume that:

```csharp
PaymentStatus.Paid
```

means a payment has been finally settled, while in the actual business it only means that the payment was authorized.

In a real enterprise payment system, `Paid` often merely means the payment gateway successfully placed an authorization hold on the customer's credit card. The actual funds are not captured and settled until an automated clearing batch runs at midnight. If the agent writes cancellation logic relying on `PaymentStatus.Paid`, it might block a valid customer cancellation request hours before any settlement occurs. Or worse, if it writes fulfillment logic assuming `Paid` means settled cash, it might release high-value goods before settlement failure alerts can trigger.

The most dangerous output is not code that obviously fails. It is code that is:

- professionally structured,
    
- fully documented,
    
- covered by tests,
    
- technically correct,
    
- based on one incorrect business assumption.
    

The code compiles, runs fast, and passes its tests, yet silently corrupts business operations because the model filled a domain semantic gap with a plausible, generic assumption.

---

## Separate Business Decisions from Technical Execution

When business rules are tangled with database queries, message queues, and HTTP calls, agents will repeatedly misplace checks, hallucinate state transitions, or bury critical domain rules inside infrastructure boilerplate.

Business rules should be isolated into small, explicit decision components:

```csharp
public CancellationDecision CanCancel(
    OrderSnapshot order,
    PaymentSnapshot payment,
    DateTimeOffset now)
{
    if (order.IsCancelled)
        return CancellationDecision.AlreadyCancelled;

    if (payment.IsIncludedInSettlementBatch)
        return CancellationDecision.PaymentAlreadySettled;

    if (order.IsAlreadyReleased)
        return CancellationDecision.AlreadyReleased;

    return CancellationDecision.Allowed;
}
```

Technical execution can remain separate:

```csharp
var decision = cancellationPolicy.CanCancel(
    order,
    payment,
    clock.UtcNow);

if (!decision.IsAllowed)
    return MapFailure(decision);

order.Cancel(userId, clock.UtcNow);

await repository.Save(order, cancellationToken);
await unitOfWork.Commit(cancellationToken);
await eventPublisher.Publish(
    new OrderCancelled(order.Id),
    cancellationToken);
```

This creates a small, reviewable location where a human can verify the meaning of the rule.

The agent can perform much more of the surrounding technical work safely.

This structural isolation delivers three critical operational advantages:

- **Instant Human Auditability:** A reviewer can inspect the business policy in fifteen seconds without mentally parsing SQL statements, retry decorators, or serialization logic.
- **Exhaustive Unit Test Generation:** Because the decision method has zero I/O and zero external dependencies, you can instruct an agent to generate complete truth tables covering every permutation of inputs without mocking a single repository or database connection.
- **Safe Infrastructure Refactoring:** An agent can rewrite the data access layer, upgrade the ORM, or swap the message bus without touching the core business invariants.

By separating evaluation from execution, you restrict the agent's generative power to the areas where it excels: scaffolding plumbing, wiring dependencies, and executing side effects. The business rule itself remains an isolated, tightly guarded domain artifact.

---

## Business Comments Are Valuable

Modern coding models have an aggressive tendency to refactor code toward standard open-source conventions. If an agent inspects an unusual conditional check, its natural reflex is to simplify, inline, or eliminate the clause to reduce boilerplate.

Comments are most useful when they explain why the code is intentionally written in a non-obvious way.

Example:

```csharp
// A payment may be authorized without being included in a settlement batch.
// Cancellation is blocked only after batch assignment.
// Do not replace this condition with PaymentStatus == Paid.
if (payment.BatchSettlementId is not null)
{
    return CancellationResult.PaymentAlreadySettled;
}
```

This tells the agent:

- what the rule means,
    
- why the current condition exists,
    
- which apparently simpler refactor would be incorrect.
    

Useful comments explain:

- unusual business rules,
    
- the meaning of ambiguous states,
    
- required operation order,
    
- historical data exceptions,
    
- why similar conditions must remain separate,
    
- the source of a decision.
    

Comments should not repeat obvious code:

```csharp
// Save the order.
await repository.Save(order);
```

Mechanical comments waste token space and obscure meaningful intent.

A useful principle is:

> Code explains what happens. Comments explain why it must happen that way (see [[Comments May Become More Valuable in AI-Generated Code]] and [[Negative Knowledge and Explicit Architectural Dissents]]).

## Related Notes

- [[Comments May Become More Valuable in AI-Generated Code]] — Preserving domain invariants and rationale in co-located code comments.
- [[Designing Software for AI Agents]] — Structuring domain interfaces to limit agent reasoning errors.
- [[Negative Knowledge and Explicit Architectural Dissents]] — Documenting known failure modes and prohibited simplifications.
- [[Formal Verification and Runtime Safety Boundaries]] — Mechanically checking high-consequence business invariants.
