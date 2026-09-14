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

## Core Thesis: Decouple Your Module Boundaries from Process Boundaries

A modular monolith does not mean every piece of code must run inside the exact same operating system process on every server. Instead, it serves as the most practical bridge between simple in-process development and distributed services (see [[Service-to-Service Communication - How Service A Should Call Service B|service communication patterns]]).

The architectural power of this approach comes from decoupling four boundaries that teams often conflate:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                 THE 4-BOUNDARY DECOUPLING PRINCIPLE                     │
├─────────────────────────────────────────────────────────────────────────┤
│ 1. MODULE BOUNDARY        != PROCESS BOUNDARY                           │
│    (Logical domain code != The physical server container running it)    │
├─────────────────────────────────────────────────────────────────────────┤
│ 2. PROCESS BOUNDARY       != DATA BOUNDARY                              │
│    (A process can connect to specific isolated database schemas)        │
├─────────────────────────────────────────────────────────────────────────┤
│ 3. DATA BOUNDARY          != SERVICE OWNERSHIP BOUNDARY                 │
│    (Schema ownership can be partitioned independently of deployments)   │
├─────────────────────────────────────────────────────────────────────────┤
│ 4. LOCAL EXECUTION        == A TRANSPORT OPTIMIZATION                   │
│    (Cross-module calls are designed as potentially remote;              │
│     running in-process is just an optimized zero-network shortcut)      │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Defining Mental Model:
> **Design every cross-module operation as an asynchronous, remote-capable contract—then allow local in-process execution as a performance optimization.**  
> 
> The transport can be transparent, but distributed realities (network latency, partial failure, retries, idempotency, and transaction limits) must remain visible in your software design.

This architecture gives you:
- A single repository, simple local debugging, and fast build times,
- Clean, compiler-enforced module boundaries,
- Independent horizontal scaling for heavy workloads without jumping straight to microservices.

---

## How Local-or-Remote Dispatch Works

At the heart of the system is a command dispatcher that routes requests depending on where modules are currently running (see [[Standardizing Service Infrastructure with Reusable Blocks]]):

```text
Module A sends a Command to Module B:

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
│ - Zero network overhead   │ │ - Serialize payload       │
│ - Direct memory dispatch  │ │ - Dispatch to queue / RPC │
│ - Instant execution       │ │ - Remote worker processes │
└───────────────────────────┘ └───────────────────────────┘
```

From the calling module's perspective, the code is identical:
```text
result = await command_bus.invoke(ReserveInventoryCommand(order_id, items))
```

If the inventory module is loaded in the same process, the bus calls the handler directly in memory. If not, the bus serializes the message, forwards it over a message broker or RPC link, and awaits the response with tracing headers attached (see [[OpenTelemetry]]).

---

## One Codebase, Multiple Deployment Roles

Instead of splitting a new system into ten separate repositories, keep everything in one codebase and configure multiple deployment roles:

```text
repository/
├── modules/
│   ├── orders/          (contracts, domain logic, persistence)
│   ├── payments/        (contracts, domain logic, persistence)
│   └── notifications/   (contracts, domain logic, persistence)
│
└── deployment_roles/
    ├── all_in_one_server/   (Loads: Orders + Payments + Notifications)
    ├── api_gateway/         (Loads: Orders for user traffic)
    ├── payment_worker/      (Loads: Payments with dedicated worker queues)
    └── notification_worker/ (Loads: Notifications with high concurrency)
```

In development, you run `all_in_one_server` locally with one command. In production, you deploy distinct worker pools scaled to their specific CPU and memory needs.

---

## Capability vs. Responsibility: Keep Connectors Broad

A common mistake when splitting workloads is stripping database drivers or network connectors from workers:
- **Capability**: *Does this running process have the libraries and network access to talk to a service?*
- **Responsibility**: *Is this specific worker currently assigned to process this job?*

```text
PRACTICAL DEFAULT:
Capability:      Broad and uniform across worker deployments.
Responsibility:  Tightly constrained and explicitly configured per role.
```

If you strip a background worker of its ability to query a database, a minor business requirement change suddenly requires updating firewall rules, cloud IAM policies, and deployment scripts. Keep instances broadly capable; configure active roles explicitly.

---

## The Reality of Local vs. Remote Execution

Location transparency is convenient, but you must never pretend remote calls are the same as local calls:

| Execution Dimension | Local In-Process Call | Remote Call Over Network |
| :--- | :--- | :--- |
| **Latency** | Microseconds ($\mu s$) | Milliseconds ($ms$) |
| **Memory Access** | Shared heap, zero serialization | Payload serialization required |
| **Failure Modes** | Immediate exception | Timeouts, lost packets, partial failure |
| **Transactions** | Can share an ACID transaction | Eventual consistency; outbox pattern required |
| **Delivery** | Exactly once | At-least-once (duplicates are normal) |
| **Idempotency** | Optional | **Mandatory** for all mutating commands |

### The Idempotency Rule: Timeouts Are Not Failures

In a distributed system, **a timeout is not a confirmed failure**. If a payment worker charges a credit card and the network drops the confirmation packet, the caller sees a timeout. If the caller retries blindly, the customer gets billed twice.

Every mutating cross-module command must include an **Idempotency Key**:
```text
record ChargePaymentCommand(
    idempotency_key: UUID,
    order_id: UUID,
    amount: Money
)
```
The receiving handler checks the idempotency key before running the charge, guaranteeing that retries return the original result safely.

---

## The Warning: Avoid the "Distributed Monolith" Trap

This architecture becomes a distributed monolith if you are careless:
- **Fine-Grained Remote Loops**: Calling a remote module inside a `for` loop to fetch 100 items generates 100 network round trips. Keep cross-module contracts coarse-grained.
- **Lockstep Deployments**: If changing Module A requires deploying Module B at the exact same second, your modules are tightly coupled.
- **Deep Synchronous Call Chains**: `API -> Orders -> Pricing -> Inventory -> Payments -> Email`. If one link stutters, the whole chain times out. Use asynchronous events and queues for background work.

---

## The 8-Stage Evolution Path

Don't jump straight into microservices. Follow this evolutionary progression:

```text
Stage 1: Clean Modular Monolith (Strict in-process module boundaries)
   │
Stage 2: Replicate Monolith behind a Load Balancer (Horizontal scaling)
   │
Stage 3: Separate HTTP API from Background Workers (Workload isolation)
   │
Stage 4: Introduce Explicit Command, Query, and Event Contracts between modules
   │
Stage 5: Enforce Module Boundaries via Automated Linters & Build Rules
   │
Stage 6: Enable Location-Transparent Dispatch (Route heavy jobs to remote workers)
   │
Stage 7: Scale Specific Worker Roles Independently (Based on queue depth and CPU)
   │
Stage 8: Extract Standalone Microservices ONLY where distinct team ownership or
         conflicting compliance boundaries strictly demand it.
```

---

## Practical Rules for Teams

1. **Keep contracts coarse-grained**: Never design a cross-module API that requires calling it inside a tight loop.
2. **Mandate idempotency keys for mutations**: Any command that can execute over a queue or network must support safe retries.
3. **Enforce boundaries in CI**: Use project reference constraints or linter rules so modules cannot query each other's internal database tables directly.
4. **Use asynchronous events when immediate results aren't needed**: Decouple workloads using background queues rather than chaining synchronous RPC calls.

---

## Related Notes

- **[[Service-to-Service Communication - How Service A Should Call Service B]]**: Guidelines for choosing between synchronous RPC, asynchronous messaging, and event streaming.
- **[[Designing Software for AI Agents]]**: Structuring module boundaries and explicit handlers so agents can navigate code easily.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Providing reusable platform infrastructure without locking application code into rigid frameworks.
- **[[Propagating User Context Between Services]]**: Managing security tokens and user identity across in-process and remote module boundaries.
- **[[OpenTelemetry]]**: Tracing requests as they traverse in-memory dispatchers, message queues, and external services.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: Preventing sprawling, unchecked cross-module dependencies when using AI coding agents.
- **[[Internal Shared Packages vs Agent-Generated Code]]**: Deciding when to build a shared internal dispatcher package versus generating local boilerplate.
