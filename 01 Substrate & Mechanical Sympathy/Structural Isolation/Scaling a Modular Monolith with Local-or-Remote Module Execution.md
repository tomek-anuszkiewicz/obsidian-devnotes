---
title: Scaling a Modular Monolith with Local-or-Remote Module Execution
tags:
  - modular-monolith
  - software-architecture
  - microservices
  - distributed-systems
  - scalability
  - structural-isolation
  - mechanical-sympathy
aliases:
  - Modular Monolith Scaling
  - Local or Remote Module Execution
  - Location-Transparent Dispatch
  - Evolutionary Modular Architecture
---

# Scaling a Modular Monolith with Local-or-Remote Module Execution

## The Core Thesis & The 4-Boundary Decoupling Invariant

A modular monolith does not mandate that every module must execute within every operating system process. Instead, it serves as the most resilient evolutionary bridge between unified in-process development and distributed microservices, as explored in [[Service-to-Service Communication -  How Service A Should Call Service B|service-to-service communication]].

The architectural power of this pattern emerges from **decoupling four structural boundaries that classical architectures conflate**:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                 THE 4-BOUNDARY DECOUPLING INVARIANT                     │
├─────────────────────────────────────────────────────────────────────────┤
│ 1. MODULE BOUNDARY        != PROCESS BOUNDARY                           │
│    (Logical domain contracts != Physical operating system container)   │
├─────────────────────────────────────────────────────────────────────────┤
│ 2. PROCESS BOUNDARY       != DATA BOUNDARY                              │
│    (A process may access multiple schema domains or shared persistence) │
├─────────────────────────────────────────────────────────────────────────┤
│ 3. DATA BOUNDARY          != SERVICE OWNERSHIP BOUNDARY                 │
│    (Schema ownership can be partitioned independently of deployments)   │
├─────────────────────────────────────────────────────────────────────────┤
│ 4. LOCAL EXECUTION        == A TRANSPORT OPTIMIZATION                   │
│    (Every cross-module call is designed as potentially remote;          │
│     in-process execution is merely an optimized zero-network shortcut)  │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Defining Mental Model:
> **Design every cross-module operation as an asynchronous, remote-capable contract—then allow local execution as a runtime optimization.**  
> 
> Transport may be transparent, but distributed failure modes (latency, partial failure, retries, idempotency, and transactional isolation) must remain visible in the design.

This architecture enables an organization to retain:
- A single unified codebase and build pipeline,
- Strongly isolated module contracts and domain boundaries,
- Deterministic local testing and rapid agent reasoning,
- Coordinated multi-module atomic refactoring,
while allowing compute-heavy or mission-critical workloads to scale independently across distinct deployment roles.

---

## The Local-or-Remote Command Dispatcher

At the center of the architecture sits a **location-transparent command dispatcher**, aligning with [[Standardizing Service Infrastructure with Reusable Blocks|standardizing service infrastructure with reusable blocks]]:

```text
Module A emits a Command targeted at Module B:

┌─────────────────────────────────────────────────────────┐
│               COMMAND DISPATCH ROUTER                   │
└────────────────────────────┬────────────────────────────┘
                             │
            Is Module B loaded in current process?
                             │
              ┌──────────────┴──────────────┐
             YES                            NO
              ▼                             ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│ LOCAL IN-MEMORY HANDLER   │ │ REMOTE TRANSPORT OUTBOX   │
│ - Zero network overhead   │ │ - Serialize message       │
│ - Direct memory dispatch  │ │ - Dispatch to Queue / RPC │
│ - Instant execution       │ │ - Remote worker processes │
└───────────────────────────┘ └───────────────────────────┘
```

From the calling module's perspective, invocation syntax remains identical:
```text
result = await command_bus.invoke(ReserveInventoryCommand(order_id, line_items))
```

Under the hood, the runtime inspects the active deployment role. If the inventory module is loaded in the same process, it invokes the handler directly in memory. If not, it serializes the payload, attaches [[Propagating User Context Between Services|distributed user context and tracing headers]], forwards it through a message queue or gRPC transport, and awaits the response via [[OpenTelemetry]] instrumented pipelines.

---

## One Codebase, Multiple Deployment Roles

Rather than prematurely partitioning a system into ten separate microservice repositories, a single codebase can compile into multiple distinct operational deployment roles:

```text
repo/
├── modules/
│   ├── orders/          (contracts, application logic, infrastructure)
│   ├── payments/        (contracts, application logic, infrastructure)
│   └── notifications/   (contracts, application logic, infrastructure)
│
└── deployable_hosts/
    ├── all_in_one_server/   (Loads: Orders + Payments + Notifications)
    ├── customer_facing_api/ (Loads: Orders)
    ├── payments_worker/     (Loads: Payments)
    └── notification_engine/ (Loads: Notifications)
```

Alternatively, a single unified executable container can dynamically assume roles based on startup environment flags:
```text
server --role=api-gateway
server --role=payment-worker --concurrency=30
server --role=notification-worker
```

The runtime role dictates which background consumers, event listeners, and API endpoints are initialized.

---

## Capability vs. Responsibility: The Safety Default

A common architectural trap when splitting deployments is aggressively stripping infrastructure connectors from workers. 

Architects must strictly differentiate:
- **Capability**: *Does this running process have the network access, drivers, and credentials to communicate with a resource?*
- **Responsibility**: *Is this specific process instance currently assigned to execute this workload?*

```text
SAFE ARCHITECTURAL DEFAULT:
  Capability:      Broad and uniform across all worker roles
  Responsibility:  Tightly constrained and explicitly configured per role
```

If a background reporting worker's connector to the pricing engine is prematurely removed, a subsequent requirement (e.g. generating dynamic tax estimates on reports) suddenly triggers expensive network policy reconfigurations, secrets provisioning, and infrastructure deployment changes. 

Unused capability is cheap; artificially crippled capability introduces massive organizational friction.

---

## The Asymmetry of Local vs. Remote Execution

Location transparency must never degenerate into "distributed computing blindness." The semantics of local and remote execution are fundamentally asymmetric:

| Execution Dimension | Local In-Process Execution | Remote Out-of-Process Execution |
| :--- | :--- | :--- |
| **Latency** | Microseconds ($\mu s$) | Milliseconds ($ms$) |
| **Memory Access** | Shared process heap / zero copy | Byte serialization required |
| **Failure Mode** | Deterministic crash or exception | Network timeouts, partial failure, packet loss |
| **Transaction Scope**| Can share local ACID transaction | Distributed eventual consistency; outbox pattern |
| **Delivery Guarantee**| Exactly once (in-memory invocation) | At-least-once delivery (duplicates likely) |
| **Idempotency** | Optional for pure methods | **Mandatory** for all mutations |

### The Idempotency Imperative
In a remote call, **a timeout is not a confirmed failure**. If a payment worker executes a credit card charge successfully but the acknowledgment packet drops on the network, the caller observes a timeout. If the caller retries blindly, the customer is billed twice.

Every mutating cross-module command must mandate a deterministic **Idempotency Key**:
```text
record ChargePaymentCommand(
    idempotency_token: UUID,
    order_id: UUID,
    amount: Money
)
```
The receiving handler must ensure that duplicate deliveries of the same `idempotency_token` return the previous result without re-executing state mutations.

---

## Static Analysis as an Architectural Enforcement Gate

To prevent developers or AI agents from casually bypassing module boundaries, architectures must enforce strict compile-time and static analysis rules (e.g., project references, package boundary linters, ArchUnit rules):

```text
PERMITTED CROSS-MODULE REFERENCE:
  orders/application ──► payments/contracts (Approved interface & DTO models)

FORBIDDEN CROSS-MODULE REFERENCES (CI Build Fails Immediately):
  orders/application ──x payments/infrastructure
  orders/application ──x payments/database_context
  orders/application ──x payments/domain_entities
  orders/application ──x payments/internal_handlers
```

This prevents code from executing direct SQL queries across domain boundaries:
```text
// FATAL ANTI-PATTERN (Tangles module boundaries):
payment = payment_db.query("SELECT * FROM payments WHERE id = :id")

// CORRECT (Enforces decoupled contract):
payment_status = await command_bus.invoke(GetPaymentStatus(payment_id))
```

---

## The 8-Stage Practical Evolution Path

Rather than making an irreversible all-or-nothing bet on microservices, teams should follow an 8-stage evolutionary progression:

```text
Stage 1: Clean Modular Monolith (Strict in-process module boundaries)
   │
Stage 2: Replicate Monolith Behind Load Balancer (Horizontal scaling)
   │
Stage 3: Split HTTP API Role from Background Worker Roles (Workload isolation)
   │
Stage 4: Introduce Explicit Command, Query, and Event Contracts between modules
   │
Stage 5: Enforce Module Contracts via Automated Static Analysis & Linters
   │
Stage 6: Activate Location-Transparent Dispatch (Route heavy commands to remote queues)
   │
Stage 7: Scale Specific Worker Roles Independently (Based on CPU, queue depth, SLA)
   │
Stage 8: Extract Standalone Microservices ONLY where disparate organizational ownership,
         conflicting release cadences, or extreme compliance boundaries mandate it.
```

This evolution avoids the distributed systems tax until concrete operational metrics prove its necessity.

---

## Summary Principles

1. **Decouple Module Boundaries from Process Boundaries**: Keep the code unified while granting deployment topologies the flexibility to adapt.
2. **Local Execution is an Optimization**: Model every cross-module interaction as asynchronous, serializable, and coarse-grained.
3. **Mandate Idempotency Keys**: Never design remote-capable mutations without explicit deduplication tokens.
4. **Enforce Boundaries at Compile Time**: Use static analysis and project-reference restrictions so that boundary violations fail the build automatically.
5. **Broad Capability, Explicit Responsibility**: Allow deployment roles to share baseline infrastructure drivers; configure active workloads explicitly.

---

## Related Notes

- **[[Service-to-Service Communication -  How Service A Should Call Service B]]**: Details contract ownership and dependency rules when modules communicate remotely.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Providing reusable platform infrastructure without obscuring application code.
- **[[Propagating User Context Between Services]]**: Handling user identity and security principals across module and service boundaries.
- **[[Designing Software for AI Agents]]**: How clean modular boundaries enable agents to reason about domain slices independently.
- **[[OpenTelemetry]]**: Distributed tracing across local in-process calls and remote message brokers.

---

## Relationship to the Knowledge Graph

- **[[Designing Internal Packages as an Explicit, Composable Framework]]**: Reusable modular blocks that power local-or-remote dispatchers without framework lock-in.
- **[[Internal Shared Packages vs Agent-Generated Code]]**: Balancing shared dispatcher infrastructure with locally generated handler implementations.
- **[[The 5-Layer System Stack for Agentic Software Engineering]]**: Placing modular monolith architecture in Layer 1 (Structural Isolation) and Layer 3 (Runtime Mesh).
- **[[Software Entropy and the Zero-Friction Trap]]**: Preventing zero-friction agent generation from eroding module boundaries.
