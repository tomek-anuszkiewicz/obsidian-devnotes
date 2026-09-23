---
title: Scaling a Modular Monolith with Local-or-Remote Module Execution
tags:
  - modular-monolith
  - software-architecture
  - microservices
  - distributed-systems
  - scalability
  - dotnet
aliases:
  - Modular Monolith Scaling
  - Local or Remote Module Execution
---

## Core idea

A modular monolith does not have to mean that every module must always run in every process.

It is possible to keep:

- one codebase,
    
- strong module boundaries,
    
- shared contracts,
    
- coordinated development,
    

while allowing selected modules or workloads to run in separate deployment units and scale independently.

A useful architecture is based on a **local-or-remote command dispatcher**:

```text
Module A sends a command to Module B.

If Module B is available in the current process:
    execute the handler locally.

If Module B is not available locally:
    serialize the command,
    send it through a queue or RPC transport,
    execute it in another process,
    return the result if needed.
```

From the caller’s perspective, the invocation may look similar:

```csharp
var result = await commandBus.InvokeAsync<ReserveInventoryResult>(
    new ReserveInventory(orderId, items));
```

The runtime decides whether the handler is local or remote.

This pattern may be described as:

- location-transparent invocation,
    
- local-or-remote dispatch,
    
- distributed command bus,
    
- component-based distributed runtime,
    
- service virtualization.
    

---

## Why this is attractive

The logical architecture can remain stable while the physical deployment topology changes.

```text
Logical architecture:

Orders -> Payments
Orders -> Inventory
Orders -> Notifications
```

Initially, all modules may run in one process:

```text
Application instance
├── Orders
├── Payments
├── Inventory
└── Notifications
```

Later, selected modules can be separated:

```text
Main API
├── Orders
└── Inventory

Payment workers
└── Payments

Notification workers
└── Notifications
```

Orders still sends the same command:

```text
ChargePayment
```

When Payments is loaded locally, the command is executed directly.

When Payments is deployed elsewhere, the command is sent through the configured transport.

This provides a gradual path between:

```text
modular monolith
-> multiple application roles
-> independently scalable modules
-> separately deployed services
```

without forcing an immediate migration to conventional microservices.

---

## One codebase, multiple deployment roles

A practical structure may look like this:

```text
src/
├── Modules/
│   ├── Orders/
│   │   ├── Orders.Contracts
│   │   ├── Orders.Application
│   │   └── Orders.Infrastructure
│   │
│   ├── Payments/
│   │   ├── Payments.Contracts
│   │   ├── Payments.Application
│   │   └── Payments.Infrastructure
│   │
│   └── Notifications/
│       ├── Notifications.Contracts
│       ├── Notifications.Application
│       └── Notifications.Infrastructure
│
└── Hosts/
    ├── FullApplication
    ├── MainApi
    ├── PaymentsWorker
    └── NotificationsWorker
```

Different hosts load different modules:

```text
FullApplication:
- Orders
- Payments
- Notifications

MainApi:
- Orders

PaymentsWorker:
- Payments

NotificationsWorker:
- Notifications
```

The same deployable artifact may also support roles through configuration:

```text
app --role full
app --role api
app --role payments
app --role notifications
```

The role determines which handlers, consumers, schedulers and endpoints are active.

---

## Capability versus responsibility

An important distinction is:

```text
Can this instance perform an operation?

Is this instance currently responsible for performing it?
```

A safe default is often:

```text
Capability: broad and consistent
Responsibility: explicitly configured
```

For example, all instances may have access to:

- the main database,
    
- the message broker,
    
- external HTTP services,
    
- caches,
    
- object storage.
    

But only selected deployment roles activate specific workloads:

```yaml
role: payments-worker

consumers:
  charge-payment:
    enabled: true
    concurrency: 20

http:
  public-api:
    enabled: false

schedulers:
  enabled: false
```

This is usually safer than trying to predict which connector or dependency a deployment will never need.

Unused capability is often cheap.

Incorrectly restricted capability can make future changes unexpectedly expensive.

---

## Scale activity, not necessarily dependencies

The most important scaling controls are usually:

- load balancer routing,
    
- queue subscriptions,
    
- consumer concurrency,
    
- queue partitioning,
    
- worker replica count,
    
- CPU and memory limits,
    
- autoscaling based on queue depth,
    
- scheduled job ownership.
    

For example:

```text
HTTP traffic
    -> Main API replicas

Payment commands
    -> Payments queue
    -> Payment workers

Notifications
    -> Notification queue
    -> Notification workers
```

All deployments may use the same codebase and similar infrastructure configuration.

The difference is which workloads are active.

This is often simpler than building multiple partially capable applications with different sets of connectors and secrets.

---

## Why removing connectors too early is risky

Suppose a reporting deployment initially appears to need only:

```text
Reporting database
Message broker
```

Later, a new requirement may need:

```text
Reporting
-> retrieve customer permissions
-> read order metadata
-> call pricing
-> publish a notification
```

If those capabilities were deliberately removed, a small business change now requires:

- new credentials,
    
- network policy changes,
    
- deployment configuration changes,
    
- secret provisioning,
    
- infrastructure review,
    
- additional environment testing.
    

The code change may be simple, but the deployment topology makes it expensive.

Therefore, connector removal should usually be justified by a concrete benefit such as:

- security isolation,
    
- compliance,
    
- sensitive data protection,
    
- reduced blast radius,
    
- expensive client resource usage,
    
- failure isolation,
    
- architectural enforcement.
    

It should not be based only on a guess that a deployment will never need something.

---

## The importance of module contracts

Modules should not directly reference each other’s implementation.

For example:

```text
Orders.Application
    -> Payments.Contracts          allowed
    -> Payments.Application        forbidden
    -> Payments.Infrastructure     forbidden
    -> Payments.DbContext          forbidden
```

Cross-module communication should happen through approved contracts:

- commands,
    
- queries,
    
- events,
    
- public module interfaces,
    
- immutable DTOs.
    

Example:

```csharp
public sealed record ChargePayment(
    Guid PaymentAttemptId,
    Guid OrderId,
    Money Amount);
```

The contract should be usable regardless of whether the handler is local or remote.

This creates a stable logical boundary while allowing deployment topology to change.

---

## Static analysis as architectural enforcement

Strong static analysis can prevent developers from accidentally bypassing module boundaries.

A Roslyn analyzer, project-reference policy or architecture test can enforce rules such as:

```text
A module may reference another module’s Contracts project.

A module may not reference another module’s:
- application implementation,
- infrastructure,
- database context,
- repositories,
- entities,
- internal handlers.
```

It may also verify that cross-module operations:

- return `Task`,
    
- accept a `CancellationToken`,
    
- use serializable contracts,
    
- do not expose internal domain entities,
    
- use approved command or query abstractions.
    

This prevents code like:

```csharp
var payment = paymentDbContext.Payments.Find(id);
```

inside the Orders module.

Instead, Orders must use an explicit contract:

```csharp
var result = await commandBus.InvokeAsync<PaymentStatus>(
    new GetPaymentStatus(paymentId),
    cancellationToken);
```

Static analysis is especially valuable because architecture rules then fail during compilation or CI instead of relying on documentation and developer discipline.

---

## Static analysis cannot validate runtime reality

Static analysis can verify structural properties:

```text
Orders does not reference Payments internals.

The command contract is serializable.

Cross-module calls use the approved dispatcher.
```

It cannot prove that:

```text
The remote handler is deployed.

The queue route is correctly configured.

The destination service is healthy.

The deployed version understands the message.

The response will arrive before the timeout.

A retry will not execute the operation twice.
```

Therefore, additional validation layers are needed.

### Compile-time validation

Check:

- illegal project references,
    
- forbidden namespace dependencies,
    
- serializable contracts,
    
- approved module APIs,
    
- asynchronous method signatures.
    

### Startup validation

Check:

- every enabled local command has exactly one handler,
    
- every remote command has a configured route,
    
- required queues exist,
    
- handlers are not accidentally registered twice,
    
- enabled consumers match the selected application role.
    

### Deployment validation

Check:

- every command has at least one responsible deployment,
    
- required credentials are available,
    
- network policies allow required communication,
    
- singleton workloads are not started by every replica,
    
- queue ownership is unambiguous.
    

### Topology integration tests

Run realistic combinations:

```text
Orders-only host
Payments-only host
Message broker
Database
```

Then verify that the same business scenario works when modules are physically separated.

A system may work perfectly when every handler is local but fail when the first module is moved into another process.

---

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

Location transparency should not hide these differences completely.

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
    
- tracing is weak,
    
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

## Practical evolution path

A reasonable progression is:

```text
1. Modular monolith

2. Replicate the whole application behind a load balancer

3. Separate HTTP and background worker roles

4. Add explicit commands, queries and events between modules

5. Enforce module boundaries using project references and static analysis

6. Allow selected commands to be routed remotely

7. Scale expensive workers or modules independently

8. Extract full services only where separate ownership,
   release cadence, security or scaling clearly justify it
```

This avoids choosing microservices before the operational need is known.

---

## Final mental model

```text
Module boundary != process boundary
Process boundary != data boundary
Data boundary != service ownership boundary
```

These boundaries can be introduced independently.

A module can remain part of one logical application while being deployed in another process.

The most useful principle is:

> Design cross-module operations as remote-capable contracts, then allow local execution as an optimization.

The most important warning is:

> Transport may be transparent, but latency, failure, retries and transaction semantics must remain visible in the design.

And the safest deployment default is:

> Keep instances broadly capable, activate responsibilities explicitly, and restrict connectors only when security, reliability or resource isolation provide a concrete reason.
```
