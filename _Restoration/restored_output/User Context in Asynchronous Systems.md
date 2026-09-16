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

Propagating user identity and context through asynchronous message brokers (RabbitMQ, Apache Kafka, Azure Service Bus, Amazon SQS) requires a fundamentally different architecture than passing bearer tokens between synchronous HTTP services.

In an HTTP pipeline, requests execute immediately while the user is actively connected. In message-driven architectures, messages decouple producers and consumers across time, network, and security boundaries. Treating an asynchronous message like an HTTP request—by dumping a live token into message headers or payloads—introduces critical operational and security failures.

---

## 1. Why Asynchronous Context Differs from HTTP

In synchronous HTTP, execution is ephemeral and immediate. A gateway verifies a user's JSON Web Token (JWT) or session cookie, downstream services propagate that token, and the entire call chain resolves within hundreds of milliseconds while the user waits for a response.

```text
Synchronous HTTP:
User ──(Bearer Token)──> Gateway ──(Forward Token)──> Service A ──(Forward Token)──> Service B
                                                      [Immediate ms execution, active user session]

Asynchronous Queue:
User ──> Service A ──[Enqueues Message]──> Message Broker
         (Token drops here)                     │ (Seconds / Hours / Days / Retries)
                                                ↓
                                            Consumer B
                                            [Background execution, user session long gone]
```

In asynchronous systems, this temporal coupling disappears:

* **Temporal Latency:** Messages may sit in topics or queues for seconds, hours, or even days during maintenance windows, downstream throttles, or massive backpressure.
* **Transient Consumer Failures and Retries:** A consumer might fail, triggering exponential backoff retries over several hours.
* **Dead Letter Queues (DLQs):** Poison messages land in DLQs for days or weeks until an on-call engineer inspects and re-drives them.
* **Terminated Sessions:** Background workers process tasks long after the originating user has logged out, closed their browser, or had their corporate credentials revoked.

---

## 2. Never Store Live User Tokens in Queue Messages

Serializing a JWT, API key, session cookie, or raw credential into a message envelope, payload, or broker transport header introduces three severe vulnerabilities:

1. **Token Expiration During Queue Lag:** Access tokens are intentionally short-lived (typically 15 to 60 minutes). If a consumer service experiences a backlog, is scaled to zero, or hits downstream rate limits, the token will expire while sitting on the broker. When the consumer finally dequeues the message, downstream calls fail with `401 Unauthorized`.
2. **Credential Exposure in Storage and Tooling:** Message brokers persist messages to disk, replicate them across cluster nodes, and retain them in Dead Letter Queues. Placing credentials in messages exposes live user tokens to broker administrators, log aggregators, message tracing tools, and DLQ inspection interfaces.
3. **Replay Attacks:** Storing live bearer tokens in persistent queues creates a replay window. Anyone with administrative read access to the broker or DLQ can extract a valid bearer token and impersonate the user against production APIs until the token expires.

> [!WARNING]
> **Rule:** Never serialize user bearer tokens, session keys, or raw credentials into message envelopes, payload bodies, or transport headers.

---

## 3. Recommended Message Context Contract

Instead of security credentials, pass a lean, strongly-typed **execution context envelope** containing immutable origin and tracing metadata. 

Machine-to-machine authentication handles transport-level trust (e.g., services authenticate to the broker using platform-managed identities, IAM roles, or mTLS). The payload carries the user context purely as an audit trail and scoping identity:

```json
{
  "messageId": "msg-90214",
  "messageType": "GenerateMonthlyInvoiceCommand",
  "correlationId": "corr-4819a",
  "causationId": "cmd-1092b",
  "traceParent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
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

In .NET / C#, model this contract using immutable records:

```csharp
public sealed record MessageEnvelope<T>(
    T Payload,
    MessageContext Context);

public sealed record MessageContext(
    string ProducerService,
    string? InitiatedByUserId,
    string? TenantId,
    string CorrelationId,
    string? CausationId,
    string? TraceParent,
    DateTimeOffset EnqueuedAt);
```

### Context Propagation Mechanics

1. **Distributed Tracing:** Propagate `traceParent` (W3C Trace Context) to maintain end-to-end distributed telemetry in OpenTelemetry across producer and consumer spans. Many brokers allow this in transport headers (e.g., Kafka record headers or Azure Service Bus application properties).
2. **Correlation and Causation:** Track `correlationId` (the overall root operation) and `causationId` (the direct message or command that triggered this message) to trace cascading asynchronous workflows.
3. **Tenant Isolation:** Background workers consuming messages must rehydrate the tenant isolation context (`tenantId`) before running queries or persisting state, ensuring database connection routing, multi-tenant row-level security, or schema switches are properly applied.

The consuming service authenticates to the broker using its own machine identity and validates the producer service via broker-level access control lists (ACLs) or message signatures, rather than parsing user signatures.

---

## 4. Authorization Timing: Acceptance vs. Execution Time

Queued operations decouple the moment an action is requested from the moment it executes. You must decide whether authorization happens at **Acceptance Time** or **Execution Time**.

```text
Option 1: Acceptance-Time Authorization (Pre-Authorization)
User ──> Service A ──[Authorize User]──> Enqueue Accepted Command ──> Consumer B
                                                                         │
                                                                         └── Trusts Producer A

Option 2: Execution-Time Authorization (Post-Authorization)
User ──> Service A ──[Enqueue Requested Command]────────────────────> Consumer B
                                                                         │
                                                                         └── Evaluates User Permissions
                                                                             against current database state
```

### Authorization at Acceptance Time (Pre-Authorization)

* **How it works:** Service A validates the user's active permissions, roles, and business rules *before* putting the command on the bus. Once enqueued, the message represents an approved, validated business intent.
* **Best for:** Most interactive business operations where the user initiated an explicit workflow and received an immediate confirmation (e.g., `PlaceOrderCommand`, `SendNotificationCommand`, `ProcessCheckoutCommand`).
* **Consumer Role:** Consumer B only verifies that Service A is authorized to produce this command type. It trusts that the command was pre-authorized and records `initiatedByUserId` strictly for audit logs.

### Authorization at Execution Time (Post-Authorization)

* **How it works:** Service A enqueues the request without executing final authorization. When Consumer B dequeues the message, it queries an authoritative directory, policy engine, or local database to verify that `initiatedByUserId` *currently* holds the necessary permissions before running the task.
* **Best for:** High-latency, delayed, or high-privilege administrative tasks (e.g., scheduled database purges, delayed financial releases, batch data exports, or overnight payroll runs).
* **Rationale:** A user's employment status, permissions, or security clearance might be revoked between the time a job is scheduled and the time it executes. If an admin schedules a database export for 3:00 AM and is terminated at 5:00 PM, an execution-time check prevents unauthorized data access.

---

## 5. Commands vs. Events Semantics

User context carries very different meaning depending on whether a message represents a **Command** (an instruction to do something) or a **Domain Event** (a notification that something already happened).

| Dimension | Command (`GenerateInvoice`) | Domain Event (`InvoiceGenerated`) |
| :--- | :--- | :--- |
| **Intent** | Direct request to perform an action. | Notification of an immutable fact that has occurred. |
| **Authorization** | Required (either at acceptance or execution time). | Not applicable — downstream consumers cannot deny history. |
| **User Context Role** | Validates intent and dictates business authority. | Purely historical audit metadata (*"Who triggered this action?"*). |
| **Consumer Behavior** | Executes business logic on behalf of the initiator. | Reacts to state changes, updates read models, or triggers side effects. |

> [!TIP]
> **Anti-Pattern:** Never inject tokens or authorization requirements into Domain Events. An event is an immutable historical statement; consumers cannot "reject" or "deny" an event based on whether the user who triggered it still has active access. Downstream consumers simply record, project, or react to the fact.

---

## Related Guidelines

- **[[Propagating User Context Between Services]]**: Synchronous HTTP propagation patterns vs. asynchronous messaging envelopes.
- **[[Service vs User Authorization Models]]**: Choosing between machine identity (mTLS/IAM) and user context for distributed operations.
- **[[Service-to-Service Communication - How Service A Should Call Service B]]**: Evaluating synchronous RPC against message broker architectures.
- **[[OpenTelemetry as the Runtime Truth for Autonomous Agents]]**: Propagating W3C `traceparent` headers across asynchronous queue boundaries.
- **[[Workflow Orchestration in Agentic Systems]]**: Context preservation and durability in multi-step asynchronous workflow engines.
