---
title: "Workflow Orchestration in Agentic Systems"
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
  - "Introduction to Workflow Orchestration"

# Workflow Orchestration in Agentic Systems

A workflow orchestrator coordinates the individual actions that make up a business process. 

At runtime, it governs:
- What step should happen next
- The exact order of execution
- Branching conditions and prerequisites
- How failures are handled and recovered
- Retry schedules and backoff policies
- When the process needs to pause and wait for external input
- When human approval is required before proceeding
- How long-running state is tracked and persisted across hours, days, or months

A useful way to divide responsibilities across a system is:

```text
Business services:
Know how to perform specific domain operations.

Background workers:
Execute computational tasks asynchronously.

Workflow orchestrator:
Knows when, why, and in what order operations should happen.

Language models:
Assist with steps that require interpretation, parsing unstructured text, or judgment.

Observability:
Records what happened, when it happened, and why.
```

These concerns can live within the same codebase or across dozens of microservices, but keeping their architectural boundaries clean is what prevents large systems from collapsing under their own complexity.

```text
External Trigger (Webhook / Event / Timer / User Action)
                          │
                          ▼
            Durable Workflow Orchestrator (e.g., Temporal, Step Functions)
        [Manages causal ordering, state persistence, and recovery]
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
Deterministic Logic  LLM Interpretation   Human-in-the-Loop
 (Rules / Validation) (Classification /   (Explicit State:
                      Structured Output)  waiting_for_approval)
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
              Isolated Execution Sandbox (e.g., Daytona, E2B, Docker)
        [Broad compute: Shell commands, Git, file edits, test runners]
                          │
                          ▼
            Idempotent Service APIs & Message Brokers (REST / gRPC / Events)
```

---

# Background Execution Is Not Workflow Orchestration

Most backend applications need to run work outside the lifecycle of the incoming HTTP request. Standard examples include:
- Generating PDF reports
- Sending transactional emails
- Rebuilding search indexes
- Purging or refreshing cache layers
- Processing uploaded media files
- Running recurring database maintenance
- Retrying transient network calls

A **background job executor** (such as Celery, Hangfire, BullMQ, or Sidekiq) is built specifically to process that work off the main thread:

```text
Application
    ↓
Enqueue work
    ↓
Background job storage / queue (Redis, RabbitMQ, PostgreSQL)
    ↓
Worker process
    ↓
Execute operation
```

This is an **execution mechanism**. It answers a straightforward operational question:
> *How and when should this specific piece of work run?*

A workflow orchestrator answers a fundamentally different question:
> *Why should this operation happen, what had to succeed before it, and what must run after it completes?*

Confusing an execution mechanism with an orchestration engine is one of the most common architectural traps in growing systems.

---

# When Background Jobs Accidentally Become a Workflow Engine

Background job systems are often used to chain multi-step processes together:

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

This design breaks down when the process is not modeled as a cohesive flow, but is instead stitched together through ad-hoc mechanisms:
- Individual background jobs enqueueing other jobs on completion
- Scheduled cron jobs polling the database for status flags (`is_stock_reserved = true`, `payment_pending = false`)
- Ad-hoc database flags representing intermediate state
- Asynchronous callbacks scattered across different microservices
- Webhook handlers writing directly to local tables to kick off the next worker

The system might work in happy-path scenarios, but the actual business process becomes invisible. When something breaks, basic questions become difficult to answer:
- Where is Order #4821 right now?
- Which steps finished, and which failed?
- What event or timer is this process currently waiting for?
- Why did this specific job run at 3:00 AM?
- If a worker crashed mid-operation, can we resume safely, or will we double-charge the card?
- Where in the codebase is this entire business process actually defined?

The problem isn't that a background worker *can't* run a series of tasks. It can. The problem is that a job queue provides the wrong abstraction for **making the causal flow of a process explicit, visible, and recoverable**.

---

# Execution Versus Orchestration

The core architectural boundary is simple:

```text
Service:
Knows how to execute a specific operation.

Orchestrator:
Knows when and why that operation should be executed.
```

A service exposes explicit business capabilities:
```text
reserve stock
capture payment
generate report
create invoice
prepare deployment
create support ticket
send notification
```

The orchestrator sits above these capabilities and composes them into complete workflows. It manages:
- Execution order and prerequisites
- Conditional branching
- Delays and timers
- Retries with backoff
- Timeout handling
- Compensating transactions (sagas) when a step fails permanently
- Human approval gates
- Coordination across separate services and third-party APIs
- Long-running process state

Consider a customer support pipeline:

```text
New support message
    ↓
Classify request
    ↓
Is it a bug?
    ├── No → Route to standard customer support queue
    └── Yes
          ↓
       Search issue tracker for duplicates
          ↓
       Prepare issue draft
          ↓
       Human approval gate
          ↓
       Create issue in tracker
          ↓
       Notify requester
```

The underlying applications handle the mechanics: how to query an issue tracker, how to create a record via an API, or how to dispatch an email. The orchestrator owns the lifecycle that links those steps together.

---

# Main Classes of Orchestration Infrastructure

"Orchestration" gets applied to very different operational layers. Teams often talk past each other because they are comparing tools designed for completely different problems.

```text
                               THE ORCHESTRATION SPECTRUM
                                            │
       ┌──────────────────┬─────────────────┴───────────────┬──────────────────┐
       ▼                  ▼                                 ▼                  ▼
Background Runners  Integration Engines            Durable Orchestrators  Agent Frameworks
(Celery / BullMQ)   (n8n / Zapier)                (Temporal / Step Func) (LangGraph / CrewAI)
  • Ephemeral tasks   • API plumbing & webhooks     • Event-sourced state  • Context windows
  • Queue & worker    • Visual DAG pipelines        • Multi-day durable    • Dynamic prompt loops
  • Local retries     • Low-code SaaS integration   • Crash-proof replay   • Tool selection
```

## 1. Background Job Executors
- **Typical tools**: Celery, Hangfire, BullMQ, Sidekiq.
- **Primary abstraction**: The **Job** or **Task**.
- **What they do**: Enqueue work, run it asynchronously on worker pools, handle basic retries, and manage recurring cron schedules.
- **When to use them**: When work belongs inside a single application boundary, needs to run off the web request path, and has a simple lifecycle.
- **Limitations**: They have no built-in concept of an end-to-end multi-step process history, distributed transactions, or cross-service compensation.

## 2. Integration and Workflow Automation
- **Typical tools**: n8n, Make, Zapier, Pipedream.
- **Primary abstraction**: The **Integration Pipeline** or **Trigger-Action Graph**.
- **What they do**: Connect third-party SaaS platforms and APIs via webhooks, transform JSON payloads, evaluate routing rules, and push data to downstream destinations.
- **When to use them**: Marketing automations, internal operations tooling, alerting systems, and connecting SaaS endpoints without writing custom boilerplate services.
- **Limitations**: The visual flow is the executable code. While this provides great visibility for business teams, it becomes brittle for high-throughput, latency-critical, or complex domain logic where software engineering practices (version control, automated testing, static typing) are mandatory.

## 3. Durable Workflow Orchestrators
- **Typical tools**: Temporal, Cadence, AWS Step Functions, Azure Durable Functions.
- **Primary abstraction**: The **Durable, Event-Sourced Workflow**.
- **What they do**: Code-first workflow definitions (written in Go, TypeScript, Python, or Java) where the execution state is durably preserved. 

Durable execution engines rely on an append-only event history. Whenever a workflow calls an external activity (like charging a credit card or calling an API), the orchestrator intercepts the call, executes it via a worker, and records the result in the event log. 

If the worker node hosting the workflow crashes midway through execution—or if the workflow has been sleeping for three weeks waiting on a webhook—the orchestrator spins up a new worker, reads the event log, and fast-forwards through the completed steps without re-executing side effects. It picks up execution at the exact line of code where it left off.

```text
Create order
    ↓
Reserve stock
    ↓
Request payment
    ↓
Wait for payment confirmation (System can sleep for days here)
    ↓
Arrange shipment
    ↓
Wait for carrier tracking response
    ↓
Notify customer
```

- **When to use them**: Critical business transactions, multi-step order processing, financial operations, complex customer lifecycles, long-running agentic coding tasks, and any process that must survive infrastructure restarts without losing state.

## 4. Agent Reasoning Frameworks
- **Typical tools**: LangGraph, AutoGen, CrewAI, Semantic Kernel.
- **Primary abstraction**: The **Reasoning Loop** or **Agent Graph**.
- **What they do**: Manage prompt assembly, context windows, model calls, dynamic tool-use loops, and memory across interactions.

```text
Receive user request
    ↓
Evaluate intent via model
    ↓
Retrieve relevant documents / context
    ↓
Model determines tool to call
    ├── Missing data → Execute tool → Feed result back to model loop
    └── Ready
          ↓
       Generate final output
```

- **Crucial distinction**: Agent frameworks orchestrate the *model's reasoning process and tool selection*. They do not inherently provide the crash-proof event-sourcing, distributed transaction guarantees, or cross-service reliability that a durable orchestrator provides. 

A durable business orchestrator manages the overall company process; an agent framework manages an individual reasoning step inside that process.

## 5. Observability and Evaluation Platforms
These are companion tools rather than orchestrators, but they sit right beside them in production:
- **What they do**: Track token counts, model latency, prompt templates, tool input/output payloads, cost attribution, and agent evaluation metrics (using standards like OpenTelemetry).
- **The operational separation**:
  - *Workflow orchestrator*: What happened across the systems, and what step comes next?
  - *Agent framework*: How did the model decide which tool to pick?
  - *Observability engine*: What payload did the model see, how many tokens did it burn, and did it hallucinate?

---

# Agent Execution Environments and Sandboxes

When an LLM agent moves beyond querying read-only APIs and starts writing code, running commands, or editing files, the execution boundary changes completely.

A coding or computer-use agent needs access to broad operating system primitives:
- A local filesystem to create, read, and edit files
- A shell environment (bash, zsh)
- Source control tools (`git`)
- Language runtimes and package managers (Node, Python, Go, Cargo)
- Compilers, linters, and test runners
- Background processes (e.g., launching an application server or local database)
- Isolated CPU, memory, and disk allocations
- Temporary network access to fetch dependencies

Giving an untrusted model direct execution access to your production host or internal container fleet is a massive security hazard.

Instead, the agent must run inside an isolated, disposable compute boundary. Platforms like **Daytona** or **E2B** provide programmatic developer sandboxes—isolated environments that act like disposable virtual machines or secure containers rather than simple stateless code evaluation functions.

```text
Agent framework:
Decides what action or command to run.

Agent sandbox / runtime:
Provides the isolated operating system where that command executes.

Workflow orchestrator:
Coordinates the high-level task lifecycle (creating the sandbox, reviewing the output, tearing it down).
```

A practical coding-agent loop looks like this:

```text
Receive GitHub issue or feature request
    ↓
Workflow orchestrator provisions sandbox (e.g., via Daytona API)
    ↓
Clone repository into sandbox
    ↓
Agent investigates codebase (reads files, searches symbols)
    ↓
Agent edits code
    ↓
Agent triggers build and test runs inside sandbox
    ↓
Agent inspects compiler errors or test failures
    ↓
Agent iterates until the test suite passes
    ↓
Agent creates git branch and submits Pull Request
    ↓
Workflow runs automated CI checks and requests human review
    ↓
Tear down sandbox
```

The sandbox engine does not decide *what* to build or *when* to open a PR. That lifecycle belongs to the outer workflow orchestrator. The sandbox simply provides the disposable, isolated operating system where the agent can safely run arbitrary commands.

```text
Workflow orchestrator:
Coordinates the overall business process and state transitions.

Agent framework:
Manages model prompts, tool call parsing, and context windows.

Agent sandbox / runtime:
Executes arbitrary file and shell operations inside a hard isolation boundary.
```

### Why Sandboxes Matter for Coding Agents
For standard enterprise business agents, the safest security model is a whitelist of narrow, explicit capabilities:

```text
find_customer
create_support_ticket
prepare_refund_request
request_deployment
```

Coding agents cannot work this way. Software engineering requires an open-ended operational surface:
- Reading and writing arbitrary files across deep directory trees
- Invoking shell utilities (`grep`, `sed`, `awk`, `find`)
- Installing third-party libraries and managing lockfiles
- Compiling code, running migrations, and launching test suites
- Inspecting active network ports and local processes

Trying to turn every conceivable development command into a separate, predefined tool is an impossible task. 

Instead of restricting every individual tool call, you **restrict the environment where those broad operations take place**:

```text
Business agent
    ↓
Restricted business APIs (narrow capabilities)
    ↓
Production systems
```

versus:

```text
Coding agent
    ↓
Broad OS capabilities (shell, filesystem, compilers)
    ↓
Isolated sandbox (Daytona / E2B / MicroVM)
    ↓
Controlled artifact (Git commit, diff, pull request)
    ↓
Automated test suite & human review
    ↓
Production deployment
```

This pattern gives the agent the freedom it needs to build and debug software while guaranteeing that the host infrastructure and production databases remain protected.

### Sandboxes Are Not Orchestrators
Because sandbox APIs and agent frameworks often sit in the same codebase, teams frequently conflate them. But their responsibilities are distinct:
- A **sandbox** answers: *Where can this untrusted or dynamically generated compute safely run?*
- An **agent framework** answers: *What tool or prompt should the model evaluate next?*
- A **workflow orchestrator** answers: *Why was this task triggered, what state was saved, what happens if an API times out, and who needs to approve the final change?*

### Sandboxes and Parallel Agents
Sandboxes also solve the state collision problem when running multiple agents in parallel. 

If three agents attempt to fix three separate bugs in the same repository simultaneously, running them on a shared filesystem causes conflicts: one agent's package installation breaks another agent's test suite.

Providing each task with its own disposable sandbox guarantees isolation:

```text
Issue A  ──►  Agent A  ──►  Sandbox A  ──►  Git Branch A
Issue B  ──►  Agent B  ──►  Sandbox B  ──►  Git Branch B
Issue C  ──►  Agent C  ──►  Sandbox C  ──►  Git Branch C
```

Each sandbox gets clean filesystem state, dedicated memory and CPU, isolated dependencies, and its own cleanup lifecycle. The orchestrator is left with the clean task of coordinating dependencies, aggregating pull requests, and triggering reviews.

---

# Deterministic and Agentic Workflows

Not every process needs an LLM. 

If a business process follows clear, predictable rules, writing it as a deterministic workflow is faster, cheaper, and vastly more reliable:

```text
Receive invoice PDF
    ↓
Validate file structure & MIME type
    ↓
Extract text via OCR / deterministic parser
    ↓
Store invoice metadata in database
    ↓
Notify accounts payable
```

Writing this flow as an open-ended agent prompt introduces latency, unpredictability, and unnecessary cost.

LLM steps become valuable when the input is unstructured, ambiguous, or requires human-like interpretation:

```text
Receive support request
    ↓
Evaluate intent from unstructured customer message
    ↓
Decide which backend systems contain relevant context
    ↓
Search knowledge base and ticket history
    ↓
Draft proposed resolution
```

The most resilient architectures combine both approaches:

```text
Deterministic workflow
        ↓
LLM-assisted interpretation step
        ↓
Deterministic schema and business rule validation
        ↓
Controlled action execution
```

The language model does not need to own the entire process. It should be used specifically where traditional code is difficult or brittle to write, while the deterministic orchestrator enforces business invariants and system boundaries.

---

# The LLM as a Component of the Workflow

Where LLMs deliver the highest leverage inside automated workflows:
- Classifying unstructured text into known categories
- Extracting strongly typed JSON data from arbitrary inputs
- Summarizing incident threads, logs, or customer tickets
- Comparing documents for semantic differences
- Deduplicating issues and finding related records
- Translating natural language intent into structured system commands
- Drafting responses for human review

Rather than letting the model execute actions directly, force it to return structured data that your normal code can validate:

```json
{
  "requestType": "bug_report",
  "component": "authentication",
  "confidence": 0.92,
  "suggestedAction": "create_issue"
}
```

Once serialized into a validated schema (e.g., via Pydantic or Zod), the output passes back into standard application logic:

```text
LLM proposes structured action
    ↓
Workflow validates schema and constraints
    ↓
System checks user authorization
    ↓
Human approves (if action exceeds risk threshold)
    ↓
Deterministic code executes mutation
```

Treating the model as an *advisor that produces structured data* rather than an *uncontrolled executor* keeps your systems predictable and debuggable.

---

# Tools Should Represent Capabilities

When exposing tools to workflows or agents, design them around explicit business capabilities rather than low-level technical primitives.

A dangerous tool interface:
```text
execute_arbitrary_sql
```

Clean, capability-focused interfaces:
```text
find_customer_by_email
create_support_ticket
prepare_refund_request
request_canary_deployment
```

Similarly, external workflow orchestrators should not depend on how a service processes work internally. An orchestrator should call an explicit service contract:

```http
POST /orders/{id}/reserve-stock
POST /reports
POST /deployments
POST /support-tickets
```

What the receiving service does under the hood—whether it processes the request synchronously, pushes it to an internal BullMQ queue, starts a goroutine, or runs a local database transaction—is an implementation detail:

```text
Workflow Orchestrator
    ↓  (Stable Business API)
Target Application Service
    ↓  (Internal execution detail)
Local queue / background worker / database transaction
```

Decoupling the workflow contract from internal worker mechanics ensures you can refactor or replace your underlying infrastructure without rewriting your business processes.

---

# Long-Running Operations

Operations that take minutes or hours to complete should never hold an HTTP connection open:

```text
POST /reports
    ↓
[HTTP connection held open for 15 minutes]  ──►  Network dropped / Gateway timeout
```

Instead, services should expose asynchronous, job-style contracts:

```http
POST /report-jobs
```

The service immediately responds with an accepted status and a tracking handle:

```json
{
  "jobId": "report-4821",
  "status": "queued"
}
```

The orchestrator records the identifier and can either poll the status endpoint:

```http
GET /report-jobs/report-4821
```

or pause its execution entirely until the reporting service emits an asynchronous event:

```text
ReportGenerated (payload contains jobId: report-4821)
```

The business capability remains clearly defined through the service API, and the orchestrator can suspend execution for as long as necessary without consuming active network sockets or compute threads.

---

# REST, Messaging, and Orchestration Solve Different Problems

Engineers often debate whether to use REST, message brokers, or workflow orchestrators. In reality, these patterns handle different parts of the system.

Communication protocols move data between services; orchestrators maintain the state and flow of the overall process.

| Requirement | Recommended Mechanism | Primary Role |
| :--- | :--- | :--- |
| **Read current state** | REST / GraphQL | Synchronous, query-only, no side effects |
| **Execute short command** | REST / gRPC | Synchronous command with immediate pass/fail feedback |
| **Submit long-running task** | Asynchronous Job API | Non-blocking command returning a job identifier |
| **Reliable async dispatch** | Message Broker (Kafka, RabbitMQ) | Decouples producer from consumer availability |
| **Notify systems of an event**| Domain Event (Pub/Sub) | Broadcasts that a state change occurred |
| **Coordinate multi-step flow** | Workflow Orchestrator | Enforces causal order, state persistence, and recovery |

In a healthy system, these mechanisms work in harmony:

```text
Orchestrator
    ↓
Dispatch command: GenerateReport
    ↓
Message broker
    ↓
Report generation service
    ↓
Emit event: ReportGenerated
    ↓
Orchestrator receives event and resumes next step
```

A message broker decouples systems in time: the reporting service doesn't need to be online the exact millisecond the orchestrator issues the command. But the broker does not know what Order #4821 is, which steps came before it, or what to do if the report is rejected. That domain lifecycle remains the orchestrator's job.

---

# Retries Require Idempotency

In any distributed system, retrying an operation is inevitable. Retries are triggered by:
- Socket timeouts
- Transient network drops
- Container or pod restarts
- Unhandled worker crashes
- Downstream rate limits or 503 errors

This introduces an unavoidable ambiguity:
> *Did the operation fail before executing on the server, or did it execute successfully and only the network response was lost on the way back?*

If an operation is not idempotent, retrying it risks serious side effects:

```text
Attempt 1: POST /payments (Charges customer $50. Response dropped by network timeout.)
    ↓
Orchestrator assumes failure
    ↓
Attempt 2: POST /payments (Charges customer an additional $50!)
```

To make workflows resilient, every mutative operation managed by an orchestrator should accept an idempotency key:

```http
POST /payments
Idempotency-Key: order-4821-payment-attempt-1
```

The payment service tracks this key in its persistence layer (often using a unique constraint or a Redis cache with a TTL). If it receives a second request with the same key, it does not re-process the charge—it simply returns the cached result of the original transaction:

```text
Repeated execution with identical key  ──►  Return original success payload (Zero duplicate side effects)
```

Reliable workflow orchestration and idempotent APIs are tightly coupled; you cannot build a dependable distributed workflow without both.

---

# Human Approval Is a Workflow State

Human intervention is often necessary when an action is:
- Destructive (dropping a staging database, deleting user environments)
- Expensive (provisioning large GPU clusters, processing large financial refunds)
- Irreversible (deploying code directly to production, sending broadcast emails)
- Low confidence (an LLM-generated classification scoring below an operational threshold)
- Legally or operationally sensitive (approving enterprise contracts, signing off on compliance audits)

```text
LLM drafts pull request or support response
    ↓
Workflow enters waiting_for_approval state
    ↓
Notification dispatched to Slack / Email with action link
    ↓
[Workflow sleeps safely in persistence layer for hours or days]
    ↓
Human reviews, edits, and clicks "Approve"
    ↓
Workflow awakens and resumes execution
```

Human review should not be handled as an edge case, a failure, or an unhandled timeout. In durable orchestrators, human approval is simply another first-class state (`waiting_for_approval`). 

Because systems like Temporal or Step Functions persist workflow state to an append-only store, a workflow can sit paused in an approval state for three weeks without consuming active CPU threads or holding open database connections.

---

# Workflow State and Observability

A workflow engine must make its execution state transparent and queryable at all times:

```json
{
  "workflowId": "support-case-9182",
  "status": "waiting_for_approval",
  "currentStep": "issue_review",
  "startedAt": "2025-05-10T14:22:00Z",
  "retryCount": 0
}
```

At any point in the lifecycle, engineers and operators should be able to answer:
- What triggered this process?
- Which steps have completed successfully, and what were their exact outputs?
- What specific event or external signal is this process waiting for right now?
- If a step failed, what was the stack trace and error payload?
- How many retries have been attempted, and what backoff was applied?
- Can this workflow be safely paused, terminated, or manually patched?

When workflows incorporate language models, observability needs to capture model-specific telemetry alongside standard system events:
- The exact prompt template and prompt version used
- The model identifier and provider version (e.g., `gpt-4o-2024-08-06`, `claude-3-5-sonnet-20241022`)
- The full context payload injected into the prompt
- The raw text response and the parsed structured output
- Total prompt and completion token counts
- Request and response latency
- Evaluation scores or output guardrail validation results

Because language models exhibit non-deterministic behavior, capturing this data is critical for debugging why an agent made a particular decision or took an unexpected branch.

---

# A Layered Architecture

These systems are not mutually exclusive. High-reliability engineering teams compose them into clean, decoupled layers:

```text
External Triggers (Webhooks, Scheduled Crons, User Actions, Message Queues)
                                │
                                ▼
                 Durable Workflow Orchestrator
             (Temporal, Cadence, AWS Step Functions)
         [Owns business process state, recovery, and causal flow]
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
Agent Reasoning Framework   Deterministic Rules     Human Approvals
 (LangGraph, CrewAI)       (Validation, Policies)   (Slack, Web UI)
  [Manages prompt loops]        │                       │
        │                       │                       │
        ▼                       │                       │
Isolated Agent Sandboxes        │                       │
  (Daytona, E2B)                │                       │
  [Disposable execution compute]│                       │
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
                     Stable Business Service APIs
                 (REST, gRPC, Idempotent Endpoints)
                                │
                                ▼
                     Application Domain Logic
                                │
                                ▼
                     Background Job Executors
                     (BullMQ, Celery, Sidekiq)
                                │
                                ▼
                         Worker Processes
```

In this architecture, each tool does what it was designed to do:
- **Durable orchestrator**: Maintains the high-level business process, tracking state across days and managing failure recovery.
- **Agent reasoning framework**: Handles prompt assembly, context windows, and model tool-selection loops.
- **Execution sandboxes**: Provide disposable, isolated operating systems where agents can compile code, run tests, and execute arbitrary shell commands safely.
- **Message brokers**: Handle decoupled asynchronous event delivery across services.
- **Business service APIs**: Expose clean, idempotent interfaces that encapsulate domain capabilities.
- **Background workers**: Execute compute-heavy tasks locally without blocking the service API.
- **Observability engines**: Record the traces, metrics, and model outputs needed to audit and debug the entire system.

---

# Choosing the Right Tool for the Job

Avoid using a heavyweight durable orchestrator where a simple queue is enough, and avoid building an implicit, unmaintainable state machine out of background jobs when a durable orchestrator is what you actually need.

Match your tooling to the problem:

1. **Simple asynchronous work inside a single service**:
   Use a **background queue** (BullMQ, Celery, Sidekiq). Enqueue the job, let a worker process it, and handle basic retries locally.

2. **Connecting SaaS platforms and internal webhooks**:
   Use an **integration engine** (n8n, Make, Zapier). Map the fields, configure the webhooks, and let the visual pipeline handle the API glue.

3. **Critical, multi-step, or multi-day business processes**:
   Use a **durable workflow orchestrator** (Temporal, Cadence, AWS Step Functions). Write the workflow as code, make your operations idempotent, and let the engine manage state persistence, timers, and crash recovery.

4. **Dynamic LLM tool-calling and reasoning loops**:
   Use an **agent framework** (LangGraph, Semantic Kernel). Let it manage the context window, prompt templates, and the back-and-forth tool evaluation loop.

5. **Coding agents and computer-use automation**:
   Pair the agent framework with an **isolated execution sandbox** (Daytona, E2B). Give the agent a disposable filesystem and shell environment, restrict its access to production infrastructure, and collect its work as a structured patch or pull request.

---

# Mental Model

The cleanest way to think about this landscape:

```text
Background job executor:
Runs work asynchronously off the main thread.

Integration orchestrator:
Glues third-party APIs and services together through visual graphs.

Durable workflow orchestrator:
Maintains long-running process state and guarantees recovery across failures.

Agent framework:
Coordinates model prompts, context retrieval, and tool-selection loops.

Agent sandbox / runtime:
Provides a disposable, isolated operating system for broad, unconstrained compute.

Language model:
Interprets unstructured text, extracts data, and assists with ambiguous decisions.

Business service API:
Exposes explicit, idempotent business operations.

Message broker:
Provides decoupled, reliable communication between systems.

Observability platform:
Shows what happened across every step, why it happened, and what it cost.
```

The core principle across all of these layers is:
> **Make the business process explicit, durable, and observable, while treating execution environments as implementation details.**

A background job runner is not a workflow orchestrator. 
A message broker is not a process engine. 
An LLM is not a state machine. 
And a sandbox is not an agent.

Resilient architectures do not try to force one tool to solve every problem. They compose them cleanly: deterministic code where the rules are fixed, durable orchestration where processes span multiple steps and survive failure, isolated sandboxes where agents need broad execution privileges, and language models where interpretation and judgment add genuine value.

---

## Related Notes
- [[Agentic Coding Harness and Controlled Development Workflows]] — Architectural patterns for building development harnesses that manage coding subagents safely.
- [[Agent Deployment and Execution Models]] — Operational trade-offs for deploying agent runtimes across local environments, server fleets, and cloud containers.
- [[Exploring Agent Harnesses]] — Comparing headless CLI runners, microVM sandboxes, and durable orchestrator backends.
- [[Multi-Agent Software Development]] — Managing task decomposition, dependency graphs, and coordination topologies across multi-agent systems.
- [[Testing in the Model, Agent, LLM Era]] — Verification strategies, automated test harnesses, and deterministic validation for model-generated code.
- [[Scaling a Modular Monolith with Local-or-Remote Module Execution]] — Techniques for keeping module interfaces decoupled from underlying execution and messaging mechanisms.
