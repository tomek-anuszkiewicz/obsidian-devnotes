---
title: Workflow Orchestration in Agentic Systems
tags:
  - orchestration
  - distributed-systems
  - software-architecture
  - durable-execution
  - microservices
  - background-processing
aliases:
  - Workflow Orchestration Concepts
  - Durable Execution and Orchestration
  - Decoupling Process Durability from Stochastic Reasoning
  - Distributed Process State and Agent Workflows
---

A process may wait for an external event, an execution result, or a person's decision long after the original request has ended. Its owner needs to know the completed steps, the next permitted action, and how to resume without repeating an external effect blindly.

This article focuses on representing and operating that durable business process. [[Composing Agent Platforms from Orchestrators, Runtimes, and Tools]] compares the surrounding categories of tools and the role of an agent inside the process. [[Isolated Engineering Environments for Coding Agents]] develops sandbox provisioning and the boundaries of the machines on which broad engineering tools run. The workflow keeps ownership of state and progression even when individual workers are replaced.

## Core Idea

A workflow orchestrator coordinates actions that together form a process.

It decides:

- what should happen;

- in what order;

- under which conditions;

- what to do after a failure;

- when to retry;

- when to wait;

- when human approval is required;

- how the state of a long-running process should be maintained.

A useful distinction is:

```text
Business services:
know how to perform business operations

Background workers:
execute work

Workflow orchestrator:
knows when, why, and in what order operations should happen

LLM:
helps with decisions that require interpretation

Observability:
shows what happened and why
```

These responsibilities can exist in the same application, but they represent different architectural concerns.

---

## Background Execution Is Not Workflow Orchestration

Many applications need to execute work outside the request that initiated it.

Examples include:

- generating reports;

- sending emails;

- rebuilding indexes;

- refreshing caches;

- processing uploaded files;

- running scheduled maintenance;

- retrying transient failures.

A **background job executor** is designed primarily to run such work reliably.

Typical capabilities include:

- queues;

- workers;

- persistence;

- retries;

- delayed execution;

- recurring jobs;

- concurrency limits.

Conceptually:

```text
Application
    ↓
enqueue work
    ↓
background job storage / queue
    ↓
worker
    ↓
execute operation
```

This is an execution mechanism.

It answers:

> How and when should this piece of work run?

A workflow orchestrator answers a different question:

> Why should this operation happen, and what should happen before or after it?

That distinction becomes increasingly important as processes grow.

---

## When Background Jobs Accidentally Become a Workflow Engine

A background execution system can technically be used to chain many operations together.

For example:

```text
Create order
    ↓
Reserve stock
    ↓
Capture payment
    ↓
Wait for confirmation
    ↓
Arrange shipment
    ↓
Notify customer
```

The problem appears when this process is implicitly represented by a mixture of:

- background jobs;

- continuations;

- scheduled checks;

- retries;

- database flags;

- events;

- callbacks;

- manually chained methods.

The system may still work, but the business process becomes difficult to see.

It becomes harder to answer:

- Where is the process now?

- Which steps completed?

- What is it waiting for?

- Why was this job created?

- What happens after a failure?

- Can the workflow resume?

- Which operations can be safely retried?

- Where is the complete process actually defined?

The issue is therefore not whether a background job system **can execute** a multi-step process.

It usually can.

The question is whether it is the right abstraction for **representing that process explicitly**.

---

## Execution Versus Orchestration

A useful architectural rule is:

```text
Service:
knows how to perform an operation

Orchestrator:
knows when and why the operation should be performed
```

A service may expose capabilities such as:

```text
reserve stock
capture payment
generate report
create invoice
prepare deployment
create support ticket
send notification
```

The orchestrator composes those capabilities into processes.

It may manage:

- ordering;

- branching;

- waiting;

- retries;

- timeouts;

- compensation;

- human approval;

- communication between systems;

- long-running process state.

For example:

```text
New support message
    ↓
Classify request
    ↓
Is it a bug?
    ├── No → route to normal support
    └── Yes
          ↓
       Search for duplicate issues
          ↓
       Prepare issue draft
          ↓
       Human approval
          ↓
       Create issue
          ↓
       Notify requester
```

The individual applications know how to search issues, create an issue, or send a notification.

The orchestrator owns the process connecting them.

---

### Durable Workflow Orchestrators

Another class focuses on **durable, long-running processes**.

Examples include:

- Temporal;

- Camunda;

- Azure Durable Functions;

- AWS Step Functions.

These systems become useful when a workflow may:

- run for hours, days, or months;

- wait for external events;

- survive application restarts;

- retry failed operations;

- execute compensation logic;

- maintain durable process state;

- coordinate multiple services.

For example:

```text
Create order
    ↓
Reserve stock
    ↓
Request payment
    ↓
Wait for payment confirmation
    ↓
Arrange shipment
    ↓
Wait for carrier response
    ↓
Notify customer
```

The important concept here is **durability**.

The process itself is persisted.

The orchestrator can know:

```text
payment requested
payment confirmation pending
shipment not started yet
```

even if the process has been waiting for several days or the underlying services have restarted.

This is fundamentally different from merely putting another job into a queue.

Under the hood, durable execution engines rely on an append-only event history. Whenever a workflow invokes an activity—such as charging a credit card or hitting an external API—the engine intercepts the call, delegates execution to a worker, and records the completion event and payload in the log. If the host process crashes mid-stream or the workflow sleeps for weeks waiting on a webhook, a new worker reconstructs the state machine by replaying the event history. It fast-forwards through completed steps without re-executing external side effects, picking up execution precisely at the point of interruption.

---

## Tools Should Represent Capabilities

An important architectural principle is that orchestration should operate on explicit business capabilities.

Bad interface:

```text
execute_arbitrary_sql
```

Better interfaces:

```text
find_customer
create_support_ticket
prepare_refund_request
request_deployment
```

Similarly, external orchestrators should ideally not depend on the internal background-job representation of an application.

Instead, the application can expose a stable contract:

```http
POST /orders/{id}/reserve-stock
POST /reports
POST /deployments
POST /support-tickets
```

The service may internally use:

```text
background job executor
local queue
worker service
message broker
database transaction
```

but those are implementation details.

Conceptually:

```text
Orchestrator
    ↓
Business API
    ↓
Application
    ↓
Local execution mechanism
```

This separation makes it easier to replace infrastructure without redesigning the workflow.

---

## Long-Running Operations

A long-running operation should usually not keep an HTTP request open.

Instead of:

```text
POST request
    ↓
wait 10 minutes
    ↓
response
```

the service can expose a job-style API:

```http
POST /report-jobs
```

Response:

```json
{
  "jobId": "report-123",
  "status": "queued"
}
```

The workflow can later query:

```http
GET /report-jobs/report-123
```

or continue after receiving an event:

```text
ReportGenerated
```

The important point is that the **business capability** is exposed through the service contract.

The fact that a background worker executes it internally does not need to leak outside the service.

Holding an HTTP connection open across multi-minute tasks invites gateway timeouts, connection drops, and thread exhaustion across the ingress proxy fleet. Shifting long-running tasks to an asynchronous job contract allows the caller to release sockets immediately, while the orchestrator suspends its execution fiber in persistence until an external event or webhook signals completion.

---

## REST, Messaging, and Orchestration Solve Different Problems

REST and messaging are communication mechanisms.

An orchestrator is a process-control mechanism.

They complement each other.

A practical split is:

|Need|Typical mechanism|
|---|---|
|Read current state|REST|
|Execute short command|REST|
|Submit long-running operation|Job API|
|Reliable asynchronous command|Message broker|
|Notify that something happened|Event|
|Coordinate multiple steps|Orchestrator|

For example:

```text
Orchestrator
    ↓
Command: GenerateReport
    ↓
Message broker
    ↓
Report service
    ↓
Event: ReportGenerated
    ↓
Orchestrator continues
```

Messaging reduces temporal coupling because the receiving system does not need to be available at exactly the moment the operation is requested.

But the broker still does not necessarily know the overall business process.

That remains the orchestrator's responsibility.

---

## Retries Require Idempotency

Distributed workflows frequently retry operations.

Retries may occur because of:

- timeouts;

- network failures;

- process restarts;

- lost responses;

- temporary service failures.

This creates an important ambiguity:

```text
Did the operation fail before execution?

or

Did the operation succeed and only the response get lost?
```

Therefore, orchestrated operations should preferably be idempotent.

For example:

```http
POST /payments
Idempotency-Key: order-123-payment
```

Repeated execution using the same key should not charge the customer multiple times.

Reliable orchestration and idempotent business operations strongly complement each other.

At the database level, idempotency is typically enforced via unique transaction constraints or a distributed key-value cache with an explicit TTL storing the original operation's result payload. When a duplicate request arrives with the same key, the service bypasses domain mutations entirely and replays the cached response. Without this guarantee at the persistence layer, automatic orchestrator retries will inevitably produce duplicate payments, phantom records, or corrupted downstream state.

---

## Human Approval Is a Workflow State

Human approval is useful when an action is:

- destructive;

- expensive;

- difficult to reverse;

- externally visible;

- low-confidence;

- legally important;

- financially important.

For example:

```text
LLM prepares action
    ↓
Workflow enters waiting_for_approval
    ↓
Human approves / edits / rejects
    ↓
Workflow continues
```

Human involvement should not necessarily be treated as an exception.

In many workflows it is simply another legitimate state.

A durable orchestrator can persist this wait and resume after an approval event without keeping a dedicated worker blocked for the entire interval. The service still consumes storage and operational resources, and persistence mechanisms differ between engines. A long wait should be represented as durable state rather than an agent repeatedly checking for approval.

---

## Workflow State and Observability

A workflow should make its state explicit.

For example:

```json
{
  "workflowId": "support-451",
  "status": "waiting_for_approval",
  "currentStep": "issue_review"
}
```

It should ideally be possible to answer:

- What started the process?

- Which steps completed?

- What is it waiting for?

- Why did it fail?

- Which retries occurred?

- Which external actions were executed?

- Can the process resume?

- Which LLM inputs and outputs affected the decision?

For workflows involving models, useful additional data includes:

- prompt version;

- model version;

- context supplied to the model;

- structured model output;

- latency;

- token usage;

- evaluation results.

This becomes increasingly important because LLM decisions are inherently less predictable than ordinary deterministic code.

---

## Apply durable orchestration to the whole software lifecycle

An issue, approved specification, failed review, and incident investigation can all invoke a shared implementation workflow. Its inputs identify the task, base commit, specification, scope, acceptance policy, environment, and budget. Its output identifies the candidate, evidence, unresolved questions, and terminal status. The surrounding business workflow decides whether to repair, request a decision, release, or close the task.

A Git event must identify the candidate being submitted. Deduplicate repeated webhooks, reject stale evidence, and distinguish checkpoints from deliberate submission. When a worker resumes after failure, reconcile existing artifacts before repeating an external action.

Long-running obligations also include evaluation after feature activation, rollout progression, flag cleanup, and test-data expiry. Store timers, owners, and next actions outside the agent session. Version workflow behavior so an execution waiting for a month is not silently reinterpreted by a deployment of new process code (see [[Designing an Agentic SDLC for Business Software]] and [[Measuring Business Outcomes After Software Delivery]]).

## Mental Model

The most useful distinction is:

```text
Background job executor:
runs work reliably

Integration orchestrator:
connects systems and coordinates steps

Durable workflow orchestrator:
maintains long-running process state

Agent framework:
coordinates model reasoning and tool usage

Agent sandbox/runtime:
provides isolated compute in which agents can act

LLM:
handles ambiguity and language-based judgment

Service API:
exposes controlled business capabilities

Message broker:
provides reliable asynchronous communication

Observability:
shows what happened and why
```

The architectural principle behind all of them is:

> Make the business process explicit and observable, while keeping execution mechanisms as implementation details.

Background execution is not orchestration.

Messaging is not orchestration.

An LLM is not necessarily an orchestrator.

An agent is not necessarily the owner of the business process.

A sandbox is not an agent or a workflow orchestrator.

They are separate building blocks that can be composed into a reliable system.

The goal is to use the right abstraction at each level:

```text
deterministic code where the rules are known,
orchestration where processes span multiple steps,
durability where processes must survive time and failure,
sandboxes where agents require broad but isolated execution capabilities,
and LLMs where interpretation provides real value.
```

(See [[Building Determinism from Unpredictable Models]] and [[User Context in Asynchronous Systems]]).

## Related Notes

- [[Building Determinism from Unpredictable Models]] — Imposing deterministic control loops over stochastic LLM reasoning.
- [[User Context in Asynchronous Systems]] — Preserving user intent and authorization across long-running background workflows.
- [[Agent Deployment and Execution Models]] — Sandboxing, containers, and execution runtimes for autonomous tasks.
- [[Multi-Agent Software Development]] — Coordinating multiple specialized agents within an overarching workflow architecture.
