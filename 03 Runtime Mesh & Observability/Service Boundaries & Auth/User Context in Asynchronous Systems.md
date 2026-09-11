---
title: User Context in Asynchronous Systems
tags:
  - distributed-systems
  - messaging
  - event-driven
  - context-propagation
  - security
  - asynchronous
aliases:
  - Async User Context
  - Context Propagation in Message Queues
---

# User Context in Asynchronous Systems

> [!IMPORTANT] Executive Architectural Thesis: Temporal Decoupling and Credential-Free Asynchronous Context
> Asynchronous messaging breaks the temporal and security assumptions of synchronous HTTP. Passing live bearer tokens across message brokers introduces catastrophic security and operational failure modes: **token expiration during queue lag**, **credential leakage in broker logs and Dead Letter Queues (DLQs)**, and **replay vulnerabilities**.  
> The correct architectural pattern decouples **identity assertion** from **authorization mechanics**:
> 1. **Zero Live Tokens**: Enqueue lean, immutable audit context (`initiatedByUserId`, `tenantId`, `correlationId`) inside an execution envelope without credentials.
> 2. **Explicit Authorization Timing**: Choose between *Acceptance-Time* (producer pre-authorizes command before enqueueing) and *Execution-Time* (consumer re-evaluates permissions against current state).
> 3. **Strict Command vs Event Distinction**: Commands carry intent and require authorization; Domain Events represent immutable historical facts where user context is strictly informational audit metadata.

```text
+----------------------------------------------------------------------------------------------------+
|               ASYNCHRONOUS USER CONTEXT & TEMPORAL BOUNDARY TOPOLOGY                               |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ Synchronous HTTP Boundary ] (Immediate ms, Active User Session)                                 |
|  User Browser ──(Bearer Token)──> Edge Gateway ──(Forward Token)──> Service A                      |
|                                                                                                    |
|  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TEMPORAL & SECURITY DETACHMENT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  |
|                                                                                                    |
|  [ Asynchronous Messaging Boundary ] (Decoupled: Minutes / Hours / Retries / User Session Terminated)  |
|                                                                                                    |
|  +------------------------+             +----------------------+             +------------------+  |
|  | Producer (Service A)   |             | Distributed Broker   |             | Consumer Service |  |
|  | - Pre-Authorizes Intent|             | (Kafka/Rabbit/SBus)  |             | (Worker Daemon)  |  |
|  | - Strips Live Creds    |             |                      |             | - Reads Audit Id |  |
|  | - Builds Lean Envelope |             | Dead-Letter Storage  |             | - Optional Check |  |
|  +------------------------+             +----------------------+             +------------------+  |
|              |                                     ^                                  ^            |
|              |                                     |                                  |            |
|              +-- Enqueues Envelope Without Tokens -+                                  |            |
|                  { msgId, tenantId, initiatedByUserId, traceparent }                  |            |
|                                                    +--- Dequeues for Processing ------+            |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

## Executive Summary & Core Architectural Invariants

1. **Zero Live Credentials Across Message Brokers**:
   Raw bearer tokens (JWTs), browser session cookies, and user passwords must never be serialized into asynchronous message envelopes, payloads, or transport headers. Enqueuing live credentials causes inevitable expiration failures during queue backpressure, leaks secrets to persistent broker disks and Dead-Letter Queues (DLQs), and creates catastrophic replay attack surfaces.

2. **Lean, Immutable Context Envelopes**:
   Asynchronous workflows propagate caller provenance as lean, strongly-typed audit metadata—consisting strictly of `initiatedByUserId`, `tenantId`, `correlationId`, `causationId`, and W3C `traceparent`. Identity in asynchronous queues is an immutable historical claim of origin, not an active cryptographic authorization key.

3. **Explicit Temporal Authorization Strategy**:
   Systems must deliberately choose between *Acceptance-Time Authorization* (the producing service validates user permissions before enqueueing an accepted, binding command) and *Execution-Time Authorization* (the consuming worker dynamically re-verifies user permissions against the authoritative directory upon dequeuing). Execution-time authorization is mandatory for high-latency or scheduled tasks where user permissions may be revoked prior to execution.

4. **Strict Semantic Division: Commands vs. Domain Events**:
   Commands carry intent and mandate explicit authorization. Domain Events represent immutable historical occurrences (*"OrderPlaced"*, *"PaymentSettled"*); domain events can never be authorized or denied by downstream consumers, and their user context exists exclusively for audit logging and read-model projections.

5. **Traceability and Tenant Isolation Integrity**:
   Every message must preserve distributed trace continuity and multi-tenant scoping across consumer boundary execution. Background workers consuming asynchronous events must rehydrate tenant isolation boundaries from the message envelope before executing any data persistence operations.

---

## 1. Why Asynchronous Context Differs from HTTP

In synchronous HTTP, a request is processed immediately, within milliseconds, while the user is actively connected.

In message-driven systems:
- Messages may sit in queues for seconds, hours, or days before being consumed.
- Messages may be retried repeatedly following consumer failures.
- Poison messages land in Dead Letter Queues (DLQ), where they are inspected by operators or automated recovery tools.
- Processing often occurs in background workers long after the original user's web session has terminated.

```text
HTTP Request:
User ──> Gateway ──(immediate ms)──> Service A ──(immediate ms)──> Service B

Asynchronous Queue:
User ──> Service A ──[Enqueues Message]──> Message Broker
                                               │ (Minutes / Hours / Days / Retries)
                                               ↓
                                           Consumer B (User session is gone)
```

---

## 2. Never Store Live User Tokens in Queue Messages

Placing a JWT access token or browser credential inside an asynchronous message is a severe security vulnerability:

1. **Token Expiration:** Short-lived tokens (e.g. 15–60 minutes) will expire before the message is processed if downstream consumers are paused, backlogged, or throttled.
2. **Credential Leakage in Brokers & DLQs:** Messages persisted on disk, replicated across cluster brokers, or routed to Dead Letter Queues expose live credentials to broker administrators and diagnostic logs.
3. **Replay Attacks:** Storing live credentials in queues enables message replay attacks if the broker or dead-letter queue is inspected or manipulated.

> [!WARNING]
> **Rule:** Never serialize user bearer tokens, session keys, or raw passwords into message envelopes or event bodies.

---

## 3. Recommended Message Context Contract

Instead of security credentials, pass a lean, strongly-typed **execution context envelope** as message metadata or dedicated payload headers:

```json
{
  "messageId": "msg-90214",
  "messageType": "GenerateMonthlyInvoiceCommand",
  "correlationId": "corr-4819a",
  "causationId": "cmd-1092b",
  "context": {
    "producerService": "billing-orchestrator",
    "initiatedByUserId": "usr-88219",
    "tenantId": "tenant-corp-42",
    "enqueuedAt": "2026-09-04T02:15:00Z"
  },
  "payload": {
    "invoiceId": "inv-2026-09-001",
    "billingPeriod": "2026-08"
  }
}
```

In language-agnostic pseudo-code, model this contract using immutable record structures:

```text
record MessageEnvelope<T>:
    payload: T
    context: MessageContext

record MessageContext:
    producerService: String
    initiatedByUserId: Optional<String>
    tenantId: Optional<String>
    correlationId: String
    causationId: String
    enqueuedAt: Timestamp
```

The consuming service authenticates to the broker using its own machine identity (e.g. platform-managed identities or mTLS certificates) and verifies the producer service via message signatures or broker-level topic ACL permissions.

---

## 4. Authorization Timing: Acceptance vs. Execution Time

For queued operations, the architecture must deliberately establish when authorization occurs:

```text
Option 1: Acceptance-Time Authorization
User ──> Service A ──[Authorize User]──> Enqueue Accepted Command ──> Consumer B
                                                                         │
                                                                         └── Trusts Producer A

Option 2: Execution-Time Authorization
User ──> Service A ──[Enqueue Requested Command]────────────────────> Consumer B
                                                                         │
                                                                         └── Evaluates User Permissions
                                                                             against current database state
```

### Authorization at Acceptance Time (Pre-Authorization)
* **How it works:** Service A validates that the user is authorized to issue the command *before* placing it onto the bus. Once on the bus, the message represents an **approved, accepted task**.
* **Best for:** Most business commands where the user initiated an explicit workflow and the system confirmed acceptance (e.g. `PlaceOrderCommand`, `SendNotificationCommand`).
* **Consumer Role:** Consumer B only verifies that Service A is an authorized producer of this command type, and logs `initiatedByUserId` for audit.

### Authorization at Execution Time (Post-Authorization)
* **How it works:** When Consumer B picks up the message, it queries its local database or authorization service to check if `initiatedByUserId` *currently* holds permissions.
* **Best for:** High-latency, scheduled, or sensitive administrative tasks (e.g. scheduled database purge, financial release, batch export).
* **Rationale:** The user's role or employment status might have been revoked between the time the job was scheduled and the time it executes.

---

## 5. Commands vs. Events Semantics

User context carries very different semantics depending on whether the message is a Command or an Event:

| Dimension | Command (`GenerateInvoice`) | Domain Event (`InvoiceGenerated`) |
| :--- | :--- | :--- |
| **Intent** | Direct request to perform an action. | Notification of a fact that already occurred. |
| **Authorization** | Required (either at acceptance or execution time). | Not applicable — downstream consumers cannot "deny" facts. |
| **User Context Role** | Determines authorization rights and business validation. | Purely historical audit metadata (*"Who caused this event?"*). |
| **Consumer Behavior** | Executes business logic on behalf of the initiator. | Reacts to state changes, updates read models, or triggers side effects. |

> [!TIP]
> **Anti-Pattern:** Never inject tokens or authorization requirements into Domain Events. An event is an immutable historical statement; consumers simply record or react to it.

---

Related core guideline: [[Propagating User Context Between Services]] and [[Service vs User Authorization Models]].
---

## Relationship to the Knowledge Graph

- **[[Propagating User Context Between Services]]**: Synchronous vs asynchronous user context propagation patterns.
- **[[Service vs User Authorization Models]]**: Handling user privileges and elevation in deferred, asynchronous batch operations.
- **[[Service-to-Service Communication -  How Service A Should Call Service B]]**: Passing context over message brokers (Kafka/RabbitMQ) vs synchronous calls.
- **[[OpenTelemetry]]**: Preserving distributed trace IDs across message queue producer-consumer boundaries.
- **[[Introduction to Workflow Orchestration]]**: Stateful context preservation in multi-step asynchronous workflow orchestrators.
