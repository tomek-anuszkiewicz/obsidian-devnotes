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

A modular application can keep one logical codebase while assigning different runtime responsibilities to different processes. The deployment question is which handlers, endpoints, and consumers each role activates, how those roles scale, and how configuration proves that required capabilities exist.

That topology only remains safe when module contracts tolerate a process boundary. A remote operation adds serialization, delay, partial failure, and duplicate-execution concerns; local execution can remove transport overhead without removing the contract. [[Remote-Capable Module Contracts and Distributed Execution]] develops those semantics and the choice between waiting for a result and accepting asynchronous progress. This article follows deployment roles, connectors, architectural checks, and the evolution path.

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

This creates a stable logical boundary while allowing deployment topology to change (see [[Designing Software for AI Agents]]).

---

## Static analysis as architectural enforcement

Strong static analysis can prevent developers from accidentally bypassing module boundaries.

A Roslyn analyzer, project-reference policy or architecture test can enforce rules such as (see [[Executable Architecture Tests for Coding Agent Guardrails]]):

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

## Related notes

- [[Standardizing Service Infrastructure with Reusable Blocks]] — Reusable platform infrastructure for decoupled service runtimes.
- [[Remote Service Calls — Errors, Resilience, and Observability]] — Remote failure semantics, retry budgets, and idempotency.
- [[Designing Software for AI Agents]] — Modularity patterns and mechanical boundary enforcement.
- [[Propagating User Context Between Services]] — Carrying security and tracing context across process boundaries.
