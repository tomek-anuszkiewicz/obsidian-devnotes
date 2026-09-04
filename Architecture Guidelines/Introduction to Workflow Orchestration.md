---
title: Introduction to Workflow Orchestration
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
---

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

# Background Execution Is Not Workflow Orchestration

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

# When Background Jobs Accidentally Become a Workflow Engine

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

# Execution Versus Orchestration

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

# Main Classes of Orchestration Tools

"Orchestrator" is a broad term.

Different tools solve different versions of the problem.

## 1. Background Job Executors

These systems primarily execute asynchronous work inside or near an application.

Typical responsibilities:

```text
enqueue
schedule
retry
persist
execute
```

They are a good fit when:

- work belongs mostly to one application;
    
- execution should happen outside the HTTP request;
    
- retries are useful;
    
- scheduled or recurring work is required;
    
- the process itself is simple.
    

Their main abstraction is usually a **job**.

They are execution-oriented rather than process-oriented.

---

## 2. Integration and Workflow Automation

Examples of this category include tools such as:

- n8n;
    
- Make;
    
- Zapier;
    
- Pipedream.
    

Their main purpose is connecting systems and APIs.

Typical flow:

```text
Trigger
    ↓
Read data
    ↓
Transform data
    ↓
Call API
    ↓
Evaluate condition
    ↓
Perform another action
```

They work particularly well for:

- webhooks;
    
- scheduled automations;
    
- Slack and email workflows;
    
- GitHub automation;
    
- CRM integration;
    
- API composition;
    
- lightweight business workflows;
    
- workflows containing occasional LLM calls.
    

In many of these systems, the visual diagram is itself the executable workflow:

```text
Diagram
    ↓
Workflow definition
    ↓
Execution
```

This makes the process highly visible.

---

## 3. Durable Workflow Orchestrators

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

---

## 4. LLM and Agent Orchestration

Another category focuses primarily on controlling the internal behavior of an LLM application or agent.

Examples include:

- LangGraph;
    
- LangChain;
    
- Semantic Kernel;
    
- AutoGen;
    
- CrewAI;
    
- Dify.
    

These tools may coordinate:

- prompts;
    
- model calls;
    
- tools;
    
- retrieval;
    
- agent state;
    
- memory;
    
- branching;
    
- loops;
    
- multiple agents;
    
- human approval;
    
- structured outputs.
    

For example:

```text
Receive request
    ↓
Understand intent
    ↓
Retrieve documentation
    ↓
Do we have enough information?
    ├── No → call another tool
    └── Yes
          ↓
       Generate proposal
```

The main object being orchestrated is no longer simply a business service.

It may be the model's interaction with tools and information.

This creates an important distinction:

```text
Business workflow orchestrator:
coordinates the overall business process

Agent orchestrator:
coordinates the model's reasoning and tool usage
```

The two can be combined.

A business workflow may call an agent as one step.

---

## 5. Observability and Evaluation

Some systems are adjacent to orchestration rather than orchestrators themselves.

For LLM applications, observability platforms can capture:

- prompts;
    
- model calls;
    
- tool calls;
    
- intermediate steps;
    
- token usage;
    
- latency;
    
- errors;
    
- agent trajectories;
    
- evaluations.
    

A useful mental distinction is:

```text
Workflow automation:
What happened across systems?

Agent framework:
How does the agent decide what to do?

Agent observability:
What did the agent actually do, and how well did it work?
```

These concerns often appear together, but they should not be confused.

---


## 6. Agent Execution Environments and Sandboxes

Another class of infrastructure becomes important when an agent needs to do more than call a small set of predefined APIs.

A coding or computer-use agent may need capabilities such as:

- a filesystem;
- a shell;
- Git;
- package managers;
- compilers and runtimes;
- long-running processes;
- development servers;
- network access;
- temporary credentials;
- isolated CPU, memory, and disk.

Giving an LLM direct access to the machine hosting the application is usually a poor security boundary.

Instead, the agent can operate inside an isolated execution environment.

Examples of this category include systems such as **Daytona**.

Daytona's main abstraction is a programmatically managed sandbox: an isolated runtime that behaves much more like a disposable computer than a single `run_code` function.

Conceptually:

```text
Agent framework:
decides what the agent should do

Agent sandbox/runtime:
provides an isolated computer in which the agent can do it
```

For example, a coding-agent loop might look like:

```text
Receive task
    ↓
Create sandbox
    ↓
Clone repository
    ↓
Agent inspects code
    ↓
Modify files
    ↓
Build / run tests
    ↓
Inspect result
    ↓
Modify again if necessary
    ↓
Produce commit / patch / pull request
    ↓
Destroy or retain sandbox
```

The sandbox does **not** normally decide that this is the correct sequence.

That responsibility belongs to the agent framework, coding agent, or outer workflow.

The sandbox provides the environment in which those actions can safely execute.

This creates another important distinction:

```text
Workflow orchestrator:
coordinates the overall process

Agent framework:
coordinates model reasoning and tool usage

Agent sandbox/runtime:
executes broad computer operations inside an isolation boundary
```

### Why Sandboxes Matter Especially for Coding Agents

For many business agents, the safest interface is a narrow set of explicit capabilities:

```text
find_customer
create_support_ticket
prepare_refund_request
request_deployment
```

A coding agent is different.

Software development inherently requires a very broad operation space:

```text
read arbitrary repository files
write files
run shell commands
install dependencies
compile code
run tests
start applications
inspect processes
use developer tools
```

Trying to represent every possible development operation as a predefined business tool would be impractical.

Therefore the security boundary can move from **restricting every operation** to **restricting the environment in which broad operations are allowed**.

For example:

```text
Business agent
    ↓
Restricted business capabilities
    ↓
Production systems
```

versus:

```text
Coding agent
    ↓
Broad computer capabilities
    ↓
Isolated sandbox
    ↓
Controlled artifact / commit / pull request
    ↓
Review and validation
    ↓
Real system
```

This is an important agent architecture pattern.

The agent may be highly capable inside the sandbox while still having tightly controlled ways of affecting external systems.

### Sandboxes Are Not Orchestrators

It is easy to confuse a sandbox platform with an agent platform because both may appear in the same system.

But they solve different problems.

A sandbox primarily answers:

> Where can this generated or agent-directed computation safely run?

An agent framework primarily answers:

> What should the model do next?

A workflow orchestrator primarily answers:

> Why is this step happening, what preceded it, and what should happen afterward?

These layers can be combined.

For example:

```text
GitHub issue
    ↓
Workflow orchestrator
    ↓
Coding agent / agent framework
    ↓
Create Daytona sandbox
    ↓
Clone repository
    ↓
Investigate → edit → build → test loop
    ↓
Produce pull request
    ↓
Review agent
    ↓
Human approval
    ↓
Merge / deployment workflow
```

Daytona owns mainly the isolated execution environment in this picture.

The surrounding workflow still needs something else to own process state, decisions, approvals, retries, and business policy.

### Sandboxes and Parallel Agents

Sandbox infrastructure also becomes useful when many agents work concurrently.

Instead of multiple agents modifying the same workspace, each task can receive its own isolated environment:

```text
Task A → Agent A → Sandbox A → branch A
Task B → Agent B → Sandbox B → branch B
Task C → Agent C → Sandbox C → branch C
```

This provides a natural boundary for:

- filesystem state;
- dependencies;
- running processes;
- experiments;
- credentials;
- resource limits;
- cleanup.

The orchestration problem then becomes deciding which tasks should exist, how they depend on one another, and how their outputs should be reviewed or combined.

The sandbox solves a different problem: giving every task a disposable execution environment.

---

# Deterministic and Agentic Workflow

Not every workflow needs an agent.

A deterministic process may look like:

```text
Receive invoice
    ↓
Validate file
    ↓
Extract data
    ↓
Store invoice
    ↓
Notify accounting
```

If the next action is already known, normal workflow logic is usually enough.

An agentic step becomes useful when interpretation is required:

```text
Receive support request
    ↓
Understand intent
    ↓
Decide which information is relevant
    ↓
Search appropriate systems
    ↓
Propose next action
```

A useful combined model is:

```text
Deterministic workflow
        ↓
LLM-assisted decision
        ↓
Deterministic validation
        ↓
Controlled action
```

The LLM does not need to own the entire process.

It can simply handle the parts where normal rules become difficult to express.

---

# LLM as a Component of the Workflow

Good LLM tasks include:

- classifying unstructured text;
    
- extracting structured information;
    
- summarizing;
    
- comparing documents;
    
- identifying likely duplicates;
    
- translating intent into structured commands;
    
- ranking alternatives;
    
- proposing a next action;
    
- drafting content.
    

For example:

```json
{
  "requestType": "bug_report",
  "component": "authentication",
  "confidence": 0.92,
  "suggestedAction": "create_issue"
}
```

This output can then enter normal deterministic software.

```text
LLM proposes
    ↓
Workflow validates
    ↓
Authorization checks permissions
    ↓
Human approves if necessary
    ↓
Normal code executes
```

This is usually safer and easier to reason about than giving the model unrestricted control.

---

# Tools Should Represent Capabilities

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

# Long-Running Operations

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

---

# REST, Messaging, and Orchestration Solve Different Problems

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

# Retries Require Idempotency

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

---

# Human Approval Is a Workflow State

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

---

# Workflow State and Observability

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

# A Layered Architecture

These mechanisms are not necessarily competitors.

They can form layers.

For example:

```text
Slack / Email / GitHub / Timer
              ↓
      Workflow Orchestrator
              ↓
      LLM-assisted decision
              ↓
  Validation / Human Approval
              ↓
       Business Service API
              ↓
       Application Logic
              ↓
  Background Job Executor
              ↓
            Worker
```

A more complex architecture might additionally contain:

```text
Agent framework:
complex LLM decision process

Agent sandbox/runtime:
isolated computer environment for agent actions

Durable orchestrator:
long-running business process

Message broker:
reliable asynchronous communication

Background worker:
local execution

Observability platform:
tracing and evaluation
```

The important point is that each component solves a different problem.

---

# Choosing the Right Level of Orchestration

A simple local task may require only:

```text
background queue
    ↓
worker
```

An integration workflow may require:

```text
workflow automation
    ↓
several APIs
```

A critical multi-day business process may require:

```text
durable workflow orchestrator
    ↓
multiple services
```

A complex LLM application may require:

```text
agent framework
    ↓
models + tools + retrieval
```

An autonomous coding or computer-use agent may additionally require:

```text
agent framework
    ↓
agent sandbox / runtime
    ↓
filesystem + shell + processes + tools
```

And these can be composed:

```text
Durable business workflow
          ↓
Agent performs ambiguous analysis
          ↓
Agent may use isolated sandbox for broad computation
          ↓
Workflow validates result
          ↓
Service API / controlled artifact
          ↓
Local background execution
```

There is no reason for one tool to own every layer.

---

# Mental Model

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

The goal is not to replace normal software with one universal workflow or autonomous agent.

The goal is to use the right abstraction at each level:

```text
deterministic code where the rules are known,
orchestration where processes span multiple steps,
durability where processes must survive time and failure,
sandboxes where agents require broad but isolated execution capabilities,
and LLMs where interpretation provides real value.
```