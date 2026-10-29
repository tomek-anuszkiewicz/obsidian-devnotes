---
title: "Remote-Capable Module Contracts and Distributed Execution"
tags:
  - modular-monolith
  - distributed-systems
  - messaging
  - api-design
  - reliability
aliases:
  - "Remote-Capable Module Boundaries"
  - "Local and Remote Module Call Semantics"
  - "Request Reply and Asynchronous Module Execution"
---

An order module invokes a payment operation in the same process today. Tomorrow, the payment handler moves to a worker. The application-facing call may look similar, but it can now time out after the payment was applied, arrive more than once, or wait behind a queue.

A module contract has to express behavior that survives that change. Inputs and results cross a serialization boundary. The caller cannot depend on shared mutable state or an ordinary in-process transaction. Waiting for a result also consumes a latency budget even when the transport is a message broker.

The sections below examine local execution as an optimization, request/reply, asynchronous commands, and the failure modes of a distributed monolith. [[Scaling a Modular Monolith with Local-or-Remote Module Execution]] explains deployment roles and validates that the required handlers and connectors exist. [[Remote Service Calls — Errors, Resilience, and Observability]] develops the corresponding communication policies for service integrations.

## Local execution as an optimization

The safest mental model is:

> Every cross-module operation is designed as though it may be remote.

If the destination module is available locally, the runtime may optimize the transport away.

This is safer than designing an ordinary local method call and later trying to convert it into RPC.

A good distributed contract should therefore be:

- coarse-grained,

- asynchronous,

- serializable,

- explicit about failure,

- explicit about timeout behavior,

- compatible with retries,

- independent of shared memory,

- independent of a shared database transaction.

Example:

```csharp
await bus.InvokeAsync<ReserveInventoryResult>(
    new ReserveInventory(orderId, items),
    cancellationToken);
```

This is a good coarse-grained operation.

A poor design would be:

```csharp
foreach (var item in items)
{
    var product = await productModule.GetProduct(item.ProductId);
    var price = await pricingModule.GetPrice(item.ProductId);
    var stock = await inventoryModule.GetStock(item.ProductId);
}
```

When local, this may only be inefficient.

When remote, it becomes a large sequence of network round trips.

In-process, this fine-grained loop executes in a few milliseconds over shared RAM. When the target module is extracted to a separate worker, 100 items produce 300 sequential network round trips, turning a sub-10ms in-memory query into a multi-second latency bottleneck.

---

## A remote call is not a local call

Even when the API looks similar, the semantics are different.

### Local call

```text
Very low latency
Shared process memory
No serialization
Immediate exceptions
Potentially shared transaction
No network timeout
```

### Remote call

```text
Network latency
Serialization
Version compatibility concerns
Timeouts
Partial failure
Retry behavior
Possible duplicate execution
No ordinary shared transaction
```

Location transparency should not hide these differences completely (see [[Remote Service Calls — Errors, Resilience, and Observability]]).

The caller should understand that a cross-module operation:

- may be remote,

- may time out,

- may succeed after the caller gives up,

- may be delivered more than once,

- may require idempotency,

- cannot rely on shared mutable state.

The abstraction may hide transport details, but it should not hide distributed-system semantics.

Context propagation also shifts across this boundary. In-process dispatch preserves ambient execution context (`AsyncLocal`), user identity, and cancellation tokens automatically. Once dispatch crosses a network transport, trace context (such as OpenTelemetry W3C `traceparent` headers), security tokens, and correlation identifiers must be explicitly serialized into message metadata and rehydrated at the receiving worker.

---

## Synchronous result over a queue

A command can be executed remotely while still returning a synchronous-looking result.

The mechanism is usually request/reply messaging:

```text
Caller
    -> sends command
    -> includes correlation ID and reply address
    -> waits for response

Handler
    -> executes command
    -> sends response

Caller
    -> matches response using correlation ID
```

From application code:

```csharp
var result = await bus.InvokeAsync<PaymentResult>(
    new ChargePayment(paymentAttemptId, orderId, amount));
```

Internally, the operation may use:

- request queue,

- response queue,

- correlation ID,

- timeout,

- temporary reply endpoint.

This can be useful, but it still creates temporal coupling:

```text
Orders cannot continue until Payments responds.
```

The main failure question becomes:

```text
What happens if Payments completes successfully,
but the response is lost?
```

The caller sees a timeout, but the operation may already have happened.

A retry can then execute the command again.

For operations such as payments, reservations or order creation, an idempotency key is essential:

```csharp
new ChargePayment(
    paymentAttemptId,
    orderId,
    amount);
```

The handler should ensure that the same `paymentAttemptId` cannot cause a second charge.

In any distributed setup, a timeout is an unknown outcome, never a confirmed failure. The receiving handler must enforce deduplication against its persistence store before triggering side effects:

```csharp
public async Task<PaymentResult> Handle(ChargePayment command, CancellationToken ct)
{
    var existingAttempt = await _dbContext.PaymentAttempts
        .FirstOrDefaultAsync(p => p.Id == command.PaymentAttemptId, ct);

    if (existingAttempt is not null)
    {
        return new PaymentResult(
            existingAttempt.Success,
            existingAttempt.TransactionReference,
            existingAttempt.FailureReason);
    }

    var response = await _paymentGateway.ChargeAsync(command.Amount, ct);

    _dbContext.PaymentAttempts.Add(new PaymentAttemptRecord
    {
        Id = command.PaymentAttemptId,
        OrderId = command.OrderId,
        Success = response.IsSuccess,
        TransactionReference = response.Reference,
        FailureReason = response.Error
    });

    await _dbContext.SaveChangesAsync(ct);

    return new PaymentResult(response.IsSuccess, response.Reference, response.Error);
}
```

If a dropped response packet forces the caller to retry, the handler detects the existing record, skips the external payment call, and immediately returns the cached transaction reference.

---

## When synchronous remote calls are reasonable

They are useful when:

- the caller genuinely needs the result immediately,

- the operation is coarse-grained,

- latency is bounded,

- failure behavior is understood,

- idempotency is implemented where necessary,

- the call chain is short,

- tracing is available.

Examples:

```text
Validate a promotion
Reserve inventory
Calculate a final price
Check permissions
Confirm a short-running business decision
```

They become dangerous when used for long chains:

```text
HTTP request
-> Orders
-> Customer
-> Pricing
-> Promotions
-> Inventory
-> Payments
-> Notifications
```

The source code may look like several normal method calls, while runtime behavior becomes a fragile distributed transaction.

Cascading synchronous chains also wreck system availability. If each module in a synchronous chain has a 99% success rate, a call spanning five consecutive hops drops the overall transaction success rate to $0.99^5 \approx 95.1\%$. Worse, the upstream caller remains blocked for the entire duration of the slowest downstream dependency. Under load, this latency tail cascades backward, exhausting web server thread pools and causing catastrophic failure across completely unrelated modules.

---

## Asynchronous commands are often safer

When an immediate result is not necessary, prefer:

```text
Command accepted
-> queue
-> processing
-> event or status update
```

Example:

```text
Orders
-> GenerateInvoice command
-> Invoice worker
-> InvoiceGenerated event
```

The caller does not wait for the entire operation.

This provides:

- backpressure,

- independent scaling,

- retry handling,

- workload isolation,

- reduced synchronous coupling.

However, it introduces eventual consistency and requires explicit status handling.

Asynchronous queueing introduces critical operational shock absorbers. Traffic spikes sit safely in the broker instead of crashing ingress API servers. If a background worker throws an out-of-memory exception on a corrupt payload, the message returns to the broker for retry or dead-lettering without dropping the customer's checkout session. Furthermore, background workloads can be scheduled on dedicated, cheaper compute instances with tailored concurrency limits.

---

## Avoid a distributed monolith

This architecture can become a distributed monolith when:

- synchronous calls form long chains,

- many modules must be deployed together,

- message contracts change in lockstep,

- developers do not know which calls are remote,

- one business operation assumes a global transaction,

- tracing is weak (see [[Propagating User Context Between Services]] and [[Standardizing Service Infrastructure with Reusable Blocks]]),

- the command bus becomes a magical global method dispatcher.

Warning signs include:

```text
Every module can call every other module.

Commands are fine-grained.

Deployment requires all services to be updated together.

A timeout is treated as a definite failure.

Retries are enabled without idempotency.

Business transactions span many synchronous remote calls.
```

The architecture should preserve explicit module ownership rather than turn the message bus into a distributed replacement for arbitrary method calls.

The most common trap is relying on ambient database transactions. In-process dispatch allows developers to cheat by wrapping multiple module calls inside an ambient `TransactionScope` or shared EF Core `DbContext`. The moment any of those modules is moved to a remote host, that atomic guarantee evaporates. If Module A commits local state and the remote command to Module B fails, Module A cannot roll back without compensating transactions or an explicit transactional outbox.

---

## Recommended rules

### Module boundaries

```text
Each module owns its business logic and data.

Other modules may reference only public contracts.

No direct access to another module’s:
- database tables,
- repositories,
- entities,
- internal handlers,
- infrastructure.
```

### Cross-module operations

```text
Use commands, queries and events.

Prefer coarse-grained operations.

Assume every call may become remote.

Do not expose shared mutable objects.

Do not rely on a shared in-memory transaction.
```

### Deployment

```text
Use one codebase where practical.

Define a small number of explicit application roles.

Enable workloads through:
- routing,
- consumers,
- concurrency,
- schedulers,
- replica counts.

Keep capabilities broad unless isolation has a concrete benefit.
```

### Reliability

```text
Use idempotency keys for retryable commands.

Define timeouts explicitly.

Distinguish timeout from confirmed failure.

Use distributed tracing.

Validate runtime topology during startup and deployment.
```

### Static analysis

```text
Enforce allowed project references.

Forbid implementation-level cross-module dependencies.

Require approved command/query abstractions.

Validate serializable contracts.

Run architecture tests in CI.
```

---

Make the externally observable behavior and failure cases part of the module contract. Exercise representative separated deployments before relying on local tests as evidence that a module can move safely.

## Related Notes

- [[Scaling a Modular Monolith with Local-or-Remote Module Execution]] — Activating and scaling module responsibilities through deployment roles.
- [[Remote Service Calls — Errors, Resilience, and Observability]] — Timeout budgets, retry safety, and ambiguous remote outcomes.
- [[User Context in Asynchronous Systems]] — Carrying identity and execution context across delayed processing.
