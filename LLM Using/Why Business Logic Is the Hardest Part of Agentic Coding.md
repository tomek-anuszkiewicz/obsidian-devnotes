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

The most dangerous output is not code that obviously fails. It is code that is:

- professionally structured,
    
- fully documented,
    
- covered by tests,
    
- technically correct,
    
- based on one incorrect business assumption.
    

---

## Separate Business Decisions from Technical Execution

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

---

## Business Comments Are Valuable

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

A useful principle is:

> Code explains what happens. Comments explain why it must happen that way.

---
