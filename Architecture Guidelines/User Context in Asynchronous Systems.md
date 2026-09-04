# User Context in Asynchronous Systems

Propagating user identity and context through asynchronous message brokers (RabbitMQ, Azure Service Bus, Apache Kafka) requires fundamentally different patterns than synchronous HTTP calls.

This document details asynchronous context propagation, message contracts, and authorization timing. It is an atomic guideline complementing [[Propagating User Context Between Services]] and [[Service vs User Authorization Models]].

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

In .NET / C#, model this using immutable records:

```csharp
public sealed record MessageEnvelope<T>(
    T Payload,
    MessageContext Context);

public sealed record MessageContext(
    string ProducerService,
    string? InitiatedByUserId,
    string? TenantId,
    string CorrelationId,
    DateTimeOffset EnqueuedAt);
```

The consuming service authenticates to the broker using its own machine identity (e.g. Managed Identity or mTLS) and verifies the producer service via message signatures or broker-level topic permissions.

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
