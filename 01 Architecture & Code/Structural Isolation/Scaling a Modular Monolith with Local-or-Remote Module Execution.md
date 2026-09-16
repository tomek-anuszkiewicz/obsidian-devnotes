---
title: Scaling a Modular Monolith with Local-or-Remote Module Execution
tags:
  - modular-monolith
  - software-architecture
  - microservices
  - distributed-systems
  - scalability
  - structural-isolation
aliases:
  - Modular Monolith Scaling
  - Local or Remote Module Execution
  - Location-Transparent Dispatch
  - Evolutionary Modular Architecture
  - Avoiding the Distributed Monolith
---

# Scaling a Modular Monolith with Local-or-Remote Module Execution

## Core Principle: Decouple Module Boundaries from Process Boundaries

A modular monolith does not mean every module must run inside the same operating system process across every server. It means keeping a single codebase, unified domain contracts, compiler-enforced boundaries, and coordinated deployments, while retaining the freedom to run selected workloads in separate deployment units as scaling demands shift.

The architectural power of this approach comes from decoupling four boundaries that teams frequently conflate:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                 THE 4-BOUNDARY DECOUPLING PRINCIPLE                     │
├─────────────────────────────────────────────────────────────────────────┤
│ 1. MODULE BOUNDARY        != PROCESS BOUNDARY                           │
│    (Logical domain code   != The physical host process executing it)    │
├─────────────────────────────────────────────────────────────────────────┤
│ 2. PROCESS BOUNDARY       != DATA BOUNDARY                              │
│    (A process can connect to specific, isolated database schemas)       │
├─────────────────────────────────────────────────────────────────────────┤
│ 3. DATA BOUNDARY          != SERVICE OWNERSHIP BOUNDARY                 │
│    (Schema ownership can be partitioned independently of deployments)   │
├─────────────────────────────────────────────────────────────────────────┤
│ 4. LOCAL EXECUTION        == A TRANSPORT OPTIMIZATION                   │
│    (Cross-module calls are designed as potentially remote;              │
│     running in-process is just an optimized, zero-network shortcut)     │
└─────────────────────────────────────────────────────────────────────────┘
```

The underlying mechanism is a **local-or-remote command dispatcher**:

```text
Module A sends a command to Module B:

┌─────────────────────────────────────────────────────────┐
│                 COMMAND DISPATCH ROUTER                 │
└────────────────────────────┬────────────────────────────┘
                             │
            Is Module B running in this process?
                             │
              ┌──────────────┴──────────────┐
             YES                            NO
              ▼                             ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│ LOCAL IN-MEMORY HANDLER   │ │ REMOTE TRANSPORT OUTBOX   │
│ - Direct memory dispatch  │ │ - Serialize command       │
│ - Zero serialization      │ │ - Route to queue or RPC   │
│ - Microsecond execution   │ │ - Await response if needed│
└───────────────────────────┘ └───────────────────────────┘
```

From the caller’s perspective, the invocation syntax is identical:

```csharp
var result = await commandBus.InvokeAsync<ReserveInventoryResult>(
    new ReserveInventory(orderId, items),
    cancellationToken);
```

The runtime inspects its local service registry. If a handler for `ReserveInventory` is registered in-process, it dispatches in memory. If not, the dispatcher serializes the command, forwards it over a message broker or RPC transport to a dedicated worker, and asynchronously returns the result.

This pattern is known variously as location-transparent invocation, local-or-remote dispatch, a distributed command bus, or a component-based distributed runtime.

---

## Why This Architecture Works

The primary benefit is that your logical architecture remains completely stable while your physical deployment topology evolves:

```text
Logical Architecture:

Orders -> Payments
Orders -> Inventory
Orders -> Notifications
```

On day one, every module runs in a single process behind a load balancer:

```text
Application Instance (All-in-One)
├── Orders
├── Payments
├── Inventory
└── Notifications
```

Six months later, notification processing spikes during sales campaigns, and third-party payment gateways start stalling HTTP worker threads. You peel those two modules off into dedicated worker pools without rewriting business logic:

```text
Main API Host
├── Orders
└── Inventory

Payment Worker Host
└── Payments

Notification Worker Host
└── Notifications
```

The Orders module still issues the exact same command:

```csharp
var result = await commandBus.InvokeAsync<PaymentResult>(
    new ChargePayment(paymentAttemptId, orderId, amount),
    cancellationToken);
```

When Payments is loaded locally, the command runs in-process. When Payments runs on dedicated worker infrastructure, the command routes through the configured transport. 

This gives your team an evolutionary path:

```text
Modular Monolith
  └─► Replicated Monolith (Multiple identical instances behind LB)
        └─► Workload-Specialized Roles (API vs. Workers)
              └─► Independently Scaled Modules (Remote dispatch)
                    └─► Separately Deployed Services (Extracted only when required)
```

You avoid the operational tax of microservices—distributed deployments, complex CI/CD pipelines, disparate repositories, and distributed tracing nightmares—until you genuinely have the operational and organizational scale to justify them.

---

## One Codebase, Multiple Deployment Roles

Instead of splitting a new system into ten separate repositories, keep the domain code inside a single repository organized cleanly into modules and host targets:

```text
src/
├── Modules/
│   ├── Orders/
│   │   ├── Orders.Contracts/
│   │   ├── Orders.Application/
│   │   └── Orders.Infrastructure/
│   │
│   ├── Payments/
│   │   ├── Payments.Contracts/
│   │   ├── Payments.Application/
│   │   └── Payments.Infrastructure/
│   │
│   └── Notifications/
│       ├── Notifications.Contracts/
│       ├── Notifications.Application/
│       └── Notifications.Infrastructure/
│
└── Hosts/
    ├── FullApplication/
    ├── MainApi/
    ├── PaymentsWorker/
    └── NotificationsWorker/
```

Different host targets reference different modules:

- **FullApplication**: References Orders, Payments, Notifications (ideal for local development, integration testing, and low-traffic environments).
- **MainApi**: References Orders and Inventory.
- **PaymentsWorker**: References Payments.
- **NotificationsWorker**: References Notifications.

Alternatively, you can compile a single deployable artifact and activate specific application roles at startup via command-line flags or environment variables:

```bash
app --role full
app --role api
app --role payments
app --role notifications
```

The role determines which message consumers, background schedulers, HTTP route endpoints, and command handlers are registered with the dependency injection container.

---

## Capability vs. Responsibility: Keep Connectors Broad

When configuring specialized deployment roles, maintain a clear distinction between what a process *can* do and what it is currently *assigned* to do:

```text
Capability:     Broad and uniform across worker deployments.
Responsibility: Tightly constrained and explicitly configured per role.
```

By default, give all application roles access to shared infrastructure primitives:
- The main database cluster (using separate schemas per module),
- The message broker,
- External HTTP egress,
- Distributed caches,
- Object storage.

Then, use role-specific configuration to activate only the workloads that specific host should run:

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

### Why Removing Connectors Too Early Is Risky

Teams often try to enforce architectural boundaries by aggressively stripping credentials, database access, or network routes from worker nodes. For example, a developer decides a reporting worker only needs access to a read replica and a message queue.

Two sprints later, a new business requirement demands that the reporting engine verify customer permissions, append order metadata, calculate regional tax overrides, and fire a notification. 

If those capabilities were physically severed at the infrastructure level, this minor functional change suddenly requires:
- Provisioning new cloud IAM credentials,
- Modifying firewall and VPC security group rules,
- Updating CI/CD secret management pipelines,
- Passing infrastructure-as-code reviews,
- Coordinating environment deployments across environments.

A change that should have taken two hours turns into a two-week multi-team coordination bottleneck. 

Unused capability in a binary is cheap. Prematurely restricted capability makes ordinary business evolution expensive. Connector removal should be reserved for explicit, high-value drivers:
- Hard regulatory compliance (e.g., PCI-DSS cardholder data environments),
- Strict security isolation around high-privilege keys,
- Protecting sensitive databases from lateral movement during a breach,
- Extreme resource constraints (e.g., memory-constrained edge nodes).

---

## Scale Activity, Not Necessarily Dependencies

Scaling problems are almost always driven by uneven workload activity, not by code co-location. You can solve 95% of performance bottlenecks by scaling operational controls rather than tearing apart application codebases:

- **Load balancer routing**: Splitting high-throughput read traffic from mutating operations.
- **Queue subscriptions**: Directing compute-heavy background tasks away from web servers.
- **Consumer concurrency**: Running 50 concurrent payment processors on a dedicated machine while running only 2 on standard nodes.
- **Queue partitioning**: Partitioning work by customer or order ID to avoid lock contention.
- **Replica counts**: Scaling worker pods up during batch processing hours and down to zero at night.
- **Resource allocation**: Giving memory-heavy PDF generation workers 16 GB of RAM, while running API gateways on 2 GB.
- **Scheduled job ownership**: Guaranteeing that background schedulers run on only one active instance using distributed locks.

```text
HTTP Ingress Traffic
    └─► Main API Replicas (High CPU, Low Memory, Fast Response)

Payment Commands
    └─► Payments Message Queue
          └─► Payment Workers (High Concurrency, Strict Timeouts)

Notification Events
    └─► Notification Queue
          └─► Notification Workers (High I/O, Asynchronous Retries)
```

Every deployment can run off the exact same built container image and configuration templates. The only variation between instances is which consumers, listeners, and handlers are enabled.

---

## The Reality of Local vs. Remote Execution

While location transparency simplifies caller syntax, treating a remote network call as if it were a local in-memory method invocation is dangerous. The runtime may abstract the network transport, but it cannot abstract physics.

| Execution Dimension | Local In-Process Dispatch | Remote Dispatch Over Transport |
| :--- | :--- | :--- |
| **Latency** | Sub-microsecond ($\mu s$) | Single- to triple-digit milliseconds ($ms$) |
| **Memory Boundaries** | Shared heap, zero serialization overhead | Network packet serialization (JSON, Protobuf) |
| **Failure Modes** | Immediate, deterministic in-memory exception | Timeouts, dropped packets, partial connection failures |
| **Transactions** | Can share an ambient ACID transaction | Distributed state; requires outbox pattern or sagas |
| **Delivery Guarantees** | Exactly-once execution | At-least-once delivery (duplicates are routine) |
| **Idempotency** | Optional | **Mandatory** for all mutating commands |
| **Context Propagation** | Ambient `AsyncLocal` / execution context | Explicit metadata injection (trace headers, baggage) |

Location transparency must never obscure these operational realities. Cross-module calls must always be designed to survive the remote column of this table:
- They must be asynchronous.
- They must accept cancellation tokens.
- They must pass serializable, self-contained payloads.
- They must assume that network packets will be delayed, dropped, or duplicated.

---

## Local Execution as an Optimization

The primary architectural principle for this topology is:

> **Design every cross-module operation as though it is remote, then allow local execution to optimize away the transport.**

When you design for remote execution from the start, local dispatch simply runs faster. But if you design for local in-memory execution—passing mutable object graphs, relying on shared database transactions, or making dozens of round-trips in a loop—extracting that code to a separate process later will break your system.

### The Granularity Rule

Consider this anti-pattern:

```csharp
// ANTI-PATTERN: Fine-grained local calls disguised as clean code
foreach (var item in items)
{
    var product = await productModule.GetProduct(item.ProductId, cancellationToken);
    var price = await pricingModule.GetPrice(item.ProductId, cancellationToken);
    var stock = await inventoryModule.GetStock(item.ProductId, cancellationToken);
}
```

In-process, this code is merely sub-optimal: it executes in a few milliseconds over shared RAM. But when `Inventory` or `Pricing` is moved to a remote worker, this loop becomes an operational disaster: 100 items produce 300 sequential network round-trips, turning a 5 ms request into a 3,000 ms bottleneck.

Cross-module operations must be coarse-grained batch requests:

```csharp
// CORRECT: Coarse-grained, batch-oriented contract
var reservationResult = await commandBus.InvokeAsync<ReserveInventoryResult>(
    new ReserveInventory(orderId, items),
    cancellationToken);
```

A properly designed cross-module contract:
- Is coarse-grained and business-driven,
- Operates asynchronously with cancellation support,
- Uses strictly serializable primitives or DTOs,
- Makes failure and timeout states explicit,
- Is safe for automated retries,
- Operates independently of shared heap memory,
- Does not assume an ambient database transaction spans across the caller and handler.

---

## Module Contracts and Static Architectural Enforcement

Modules must never reference each other's internal implementation details, persistence models, or infrastructure projects.

```text
Allowed:
Orders.Application    ──► Payments.Contracts

Forbidden:
Orders.Application    ──X Payments.Application
Orders.Application    ──X Payments.Infrastructure
Orders.Application    ──X Payments.Domain
Orders.Application    ──X Payments.DbContext
```

Cross-module communication must route exclusively through an explicit contract library defining commands, queries, events, and immutable data transfer objects:

```csharp
namespace Payments.Contracts;

public sealed record ChargePayment(
    Guid PaymentAttemptId,
    Guid OrderId,
    decimal Amount,
    string Currency);

public sealed record PaymentResult(
    bool Success,
    string TransactionReference,
    string? FailureReason);
```

### Static Analysis via Roslyn and Architecture Tests

Never rely on developer discipline alone to protect module boundaries. Use automated compile-time analyzers (such as Roslyn analyzers in .NET, ArchUnit in Java, or project dependency graph linters) to enforce boundary rules directly in CI:

1. **Enforce Project References**: The project build configuration should physically prevent `Orders.Application` from referencing `Payments.Application`.
2. **Forbid Cross-Module Data Access**: Block queries like:
   ```csharp
   // CAUGHT BY ANALYZER: Orders querying Payments schema directly
   var payment = paymentDbContext.Payments.Find(id);
   ```
   Orders must route through the command bus:
   ```csharp
   var status = await commandBus.InvokeAsync<PaymentStatus>(
       new GetPaymentStatus(paymentId),
       cancellationToken);
   ```
3. **Validate Boundary Types**: Analyzers should verify that any method signature crossing a module boundary:
   - Returns a `Task` or `ValueTask`,
   - Accepts a `CancellationToken`,
   - Uses parameters that implement a specific contract interface (e.g., `ICommand`, `IQuery`),
   - Contains only serializable properties (no raw entity classes, open streams, or database connections).

---

## Static Analysis Cannot Validate Runtime Reality

Static analysis only proves that the code compiled without referencing forbidden dependencies. It tells you nothing about whether the distributed runtime can successfully execute the request.

Static analysis cannot verify:
- Whether the remote payment worker is running and healthy,
- Whether the underlying RabbitMQ or SQS queue has been provisioned,
- Whether routing keys match message serialization contracts,
- Whether the deployed worker version understands the serialized schema,
- Whether response timeouts are tuned longer than downstream gateway latencies,
- Whether duplicate message retries will corrupt application state.

To guarantee operational stability, implement validation across four separate layers:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE 4 RUNTIME VALIDATION LAYERS                      │
└─────────────────────────────────────────────────────────────────────────┘
  1. COMPILE-TIME
     - Project reference rules (no direct access to internal packages)
     - Serializability checks on all Contract records
     - Async signatures with CancellationToken enforcement
  
  2. STARTUP VALIDATION (In-Process Host Boot)
     - Fail-fast checks verifying every registered local command has 1 handler
     - Assert that every remote command has a valid, mapped transport route
     - Verify queue listeners match the current host's activated application role
  
  3. DEPLOYMENT & ENVIRONMENT VALIDATION (Health Checks / CD)
     - Smoke test message broker and database connectivity
     - Validate IAM permissions and network security group routing
     - Confirm at least one active worker instance is subscribed to every queue
  
  4. TOPOLOGY INTEGRATION TESTS (Pre-Production CI Pipeline)
     - Spin up split hosts: Orders Host, Payments Host, Message Broker
     - Run end-to-end integration tests over real network transports
     - Ensure features execute identically whether running all-in-one or split
```

If your integration suite passes when every module runs in-process inside `FullApplication`, but fails when `PaymentsWorker` is run as a separate container, your module contracts are leaking in-memory assumptions.

---

## Synchronous Results Over a Queue

There are times when a caller needs an immediate result from a command handled by a separate process. You can accomplish this over message queues using request/reply correlation:

```text
Caller Host                                              Worker Host
┌─────────────────────┐                                  ┌─────────────────────┐
│ 1. Send Command     │───► [ Request Queue ] ──────────►│ 2. Read Command     │
│    Correlation ID: X│                                  │                     │
│    ReplyTo: Queue_A │                                  │ 3. Execute Business │
│                     │                                  │    Logic            │
│ 5. Read Response    │◄─── [ Reply Queue_A ] ◄──────────│                     │
│    Match ID: X      │                                  │ 4. Send Response    │
└─────────────────────┘                                  └─────────────────────┘
```

The application code remains clean and sequential:

```csharp
var result = await commandBus.InvokeAsync<PaymentResult>(
    new ChargePayment(paymentAttemptId, orderId, 150.00m, "USD"),
    cancellationToken);
```

Under the hood, the dispatcher creates a temporary reply queue (or uses a dedicated, partitioned response queue), injects a unique `CorrelationId`, serializes the payload, sends the message, and registers a `TaskCompletionSource` that awaits the matching response or times out.

### The Temporal Coupling Problem

While this looks like a normal asynchronous method call, it introduces direct temporal coupling: the calling thread cannot complete its work until the remote worker picks up, processes, and returns the result.

The critical failure scenario in this pattern is:

> **What happens if the worker charges the customer, but the reply queue drops the confirmation message?**

The caller encounters a timeout exception. But the operation **did not fail**—the state change succeeded, while the notification of that success was lost. If the caller blindly retries, the customer is billed twice:

```text
Caller                                               Worker
  │                                                    │
  │─── ChargePayment(Attempt #1) ─────────────────────►│
  │                                                    │─── Processes Payment ($50)
  │◄── [TIMEOUT: Response dropped over network] ───────X    (Payment Succeeded!)
  │
  │─── RETRY: ChargePayment(Attempt #1 or #2) ────────►│
  │                                                    │─── Processes Payment AGAIN ($50)
  │◄── Payment Success ────────────────────────────────│    (Customer Overcharged!)
```

### The Idempotency Rule: Timeouts Are Not Failures

In any distributed architecture, **a timeout is an unknown outcome, not a confirmed failure**.

Every cross-module mutating command must include a unique idempotency key:

```csharp
public sealed record ChargePayment(
    Guid PaymentAttemptId,  // Idempotency Key
    Guid OrderId,
    decimal Amount,
    string Currency);
```

The receiving module must enforce deduplication at the storage layer:

```csharp
public async Task<PaymentResult> Handle(ChargePayment command, CancellationToken ct)
{
    // 1. Check if this attempt has already been executed
    var existingAttempt = await _dbContext.PaymentAttempts
        .FirstOrDefaultAsync(p => p.Id == command.PaymentAttemptId, ct);

    if (existingAttempt is not null)
    {
        // Return the recorded result without re-executing the charge
        return new PaymentResult(
            existingAttempt.Success, 
            existingAttempt.TransactionReference, 
            existingAttempt.FailureReason);
    }

    // 2. Execute new payment attempt
    var response = await _paymentGateway.ChargeAsync(command.Amount, command.Currency, ct);

    // 3. Persist attempt record atomically
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

Now, if a dropped response causes the caller to retry the command, the worker simply looks up `PaymentAttemptId`, sees that the charge already occurred, and immediately returns the cached transaction reference without double-charging.

---

## When Synchronous Remote Calls Are Acceptable

Synchronous cross-module calls (whether via request/reply queues or direct gRPC) are reasonable when:
- The caller genuinely cannot proceed without the result (e.g., verifying a user's credit balance before placing an order),
- The operation is coarse-grained,
- The downstream latency is low and bounded by aggressive timeouts,
- Failure and timeout paths are explicitly handled,
- The command is idempotent,
- Distributed tracing context (e.g., OpenTelemetry traceparent headers) is propagated through message metadata,
- The synchronous call chain is strictly limited to a depth of one.

### Avoid Deep Synchronous Call Chains

Synchronous calls become dangerous when they form cascading chains across multiple modules:

```text
HTTP Request
  └─► Orders Module
        └─► Customers Module (RPC)
              └─► Pricing Module (RPC)
                    └─► Inventory Module (RPC)
                          └─► Payments Module (RPC)
                                └─► Third-Party Gateway (HTTP)
```

If each link has a 99% success rate, a chain of five services yields an overall success rate of $0.99^5 \approx 95.1\%$. More importantly, the system inherits the latency of the slowest downstream dependency, and thread pool exhaustion can cascade backward through the entire system, taking down unrelated modules.

---

## Asynchronous Commands and Events Are Safer

When an operation does not need to return data immediately to the caller, eliminate synchronous coordination entirely:

```text
Orders Module                                           Invoice Worker
┌──────────────────┐                                   ┌──────────────────┐
│ Accept Order     │                                   │ Consume Message  │
│ Save to Database │                                   │ Generate PDF     │
│ Send Command:    │───► [ Message Broker Queue ] ────►│ Upload to S3     │
│  GenerateInvoice │                                   │ Emit Event:      │
│ Return 202 / OK  │                                   │  InvoiceCreated  │
└──────────────────┘                                   └──────────────────┘
```

The calling thread saves its local state, fires the command to a persistent queue, and immediately returns an HTTP `202 Accepted` response.

This provides:
- **Natural Backpressure**: Surges in orders sit safely in the queue; invoice workers process messages at their maximum sustainable throughput without crashing the API.
- **Fault Tolerance**: If the invoice generator crashes due to an out-of-memory error on a massive document, the message returns to the queue and retries without dropping the customer's purchase.
- **Workload Isolation**: Invoice generation can run on cheap spot instances with dedicated CPU limits.

This pattern introduces eventual consistency. The user interface must be designed to reflect states like `Invoice Pending` rather than assuming the document is ready immediately.

---

## Avoiding the "Distributed Monolith" Trap

A local-or-remote architecture can easily degrade into a distributed monolith if boundaries are neglected. A distributed monolith combines the deployment complexity of microservices with the tight coupling of a legacy monolith.

Watch for these warning signs:

```text
DISTRIBUTED MONOLITH WARNING SIGNS:

1. FINE-GRAINED REMOTE CALLS
   Making repeated, fine-grained cross-module queries inside loops.
   Result: Massive network serialization overhead and latency spikes.

2. CHATTER-DRIVEN SYNCHRONOUS CHAINS
   Module A calls B, which calls C, which calls D, all waiting synchronously.
   Result: Cascading timeouts, fragile availability, and thread pool starvation.

3. LOCKSTEP DEPLOYMENTS
   Changing Module A requires deploying Module B at the exact same instant to prevent crashes.
   Result: Destroys deployment independence and forces coordinated release trains.

4. AMBIENT ASSUMPTIONS OF DISTRIBUTED TRANSACTIONS
   Assuming a database transaction opened in Module A will seamlessly roll back state 
   mutated in Module B over the command bus.
   Result: Corrupted, inconsistent cross-module state when partial failures occur.

5. BLIND RETRIES WITHOUT IDEMPOTENCY
   Configuring generic network retry policies around mutating commands.
   Result: Duplicate charges, duplicated records, and phantom inventory reservations.
```

Your command bus should never be used as a magical RPC layer to call arbitrary internal methods across servers. It is an explicit transport boundary for well-defined domain operations.

---

## The 8-Stage Evolution Path

You do not need to choose between a simple monolith and a fleet of microservices on day one. Walk this progressive path, advancing to the next stage only when forced by clear organizational, performance, or deployment bottlenecks:

```text
Stage 1: Modular Monolith
         Keep everything in one project or solution. Enforce clean domain boundaries
         and contract interfaces in code. Everything runs in-process.

Stage 2: Replicated Monolith
         Deploy multiple identical copies of the full application behind a load balancer.
         Scale horizontally by adding standard nodes.

Stage 3: Role-Specialized Deployments
         Use the same codebase to deploy distinct operational roles: separate your
         user-facing HTTP API nodes from your asynchronous background workers.

Stage 4: Formal Cross-Module Contracts
         Replace direct inter-module method calls with explicit asynchronous Commands,
         Queries, and Events defined in isolated contract libraries.

Stage 5: Static Boundary Enforcement in CI
         Implement Roslyn analyzers, ArchUnit tests, or build policies to strictly
         forbid cross-module references to internal logic, entities, or databases.

Stage 6: Location-Transparent Dispatch
         Introduce the local-or-remote command bus. The runtime now dynamically routes
         commands in memory or across a message broker depending on the host's active role.

Stage 7: Independent Module Scaling
         Extract high-throughput or resource-heavy modules (e.g., Payments, Reporting, 
         Media Processing) into their own worker pools, scaling them based on queue depth.

Stage 8: Standalone Microservices (Only Where Justified)
         Physically carve out a module into a distinct repository and CI/CD pipeline 
         ONLY when separate team ownership, release cadences, or security classifications 
         make independent deployment mandatory.
```

By following this path, you defer the operational complexity of distributed systems until your business actually requires it, while ensuring your code is cleanly structured to make that transition straightforward when the time comes.

---

## Architectural Rules of Thumb

### Module Boundaries
- Each module strictly owns its business logic and persistence store.
- Modules may reference another module's `.Contracts` project, but never its `.Application`, `.Domain`, or `.Infrastructure` projects.
- Never execute cross-module database joins or access another module’s tables directly.

### Cross-Module Operations
- Use explicit Commands for state mutations, Queries for read models, and Events for facts that have already occurred.
- Every cross-module contract must be coarse-grained, asynchronous, and fully serializable.
- Never pass mutable object graphs across module boundaries.
- Assume any cross-module invocation may route over a network; never rely on shared ambient transactions.

### Deployments and Operations
- Maintain a single codebase and deployment pipeline for as long as possible.
- Define a small set of explicit application roles (`api`, `worker-payments`, `worker-notifications`).
- Keep infrastructure capabilities (database drivers, broker connections) broadly available across hosts, but activate operational responsibilities explicitly through configuration.
- Restrict credentials, network access, or drivers only when justified by hard compliance, security isolation, or failure-domain boundaries.

### Distributed Reliability
- Every mutating command routed over a network transport must include a unique idempotency key.
- Receiving modules must verify idempotency keys at the persistence layer before executing business logic.
- Configure explicit timeouts on every remote invocation, and treat a timeout as an indeterminate state, never as a confirmed failure.
- Propagate OpenTelemetry trace context and security tokens across every command dispatch, whether in memory or over a message broker.

---

## Related Notes

- **[[Service-to-Service Communication - How Service A Should Call Service B]]**: Architectural guidance on choosing between synchronous RPC, asynchronous queues, and streaming event buses.
- **[[OpenTelemetry]]**: Instrumenting distributed trace contexts across in-memory dispatchers, message brokers, and downstream network endpoints.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Structuring host configurations, dependency injection extensions, and platform harnesses across specialized deployment roles.
- **[[Propagating User Context Between Services]]**: Handling user identity, ambient security claims, and authorization tokens across modular and distributed boundaries.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: Preventing unchecked cross-boundary dependencies and architectural drift when using code-generation tools.
- **[[Internal Shared Packages vs Agent-Generated Code]]**: Balancing centralized contract packages against local code generation when maintaining cross-module communication boundaries.
