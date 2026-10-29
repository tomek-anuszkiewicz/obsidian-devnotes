---
title: "Composing Agent Platforms from Orchestrators, Runtimes, and Tools"
tags:
  - ai-agents
  - orchestration
  - software-architecture
  - infrastructure
  - tool-use
aliases:
  - "Layered Agent Platform Architecture"
  - "Business Orchestration and Agent Execution"
  - "Agent Frameworks Runtimes and Workflow Tools"
---

A team evaluating an agent platform can encounter a background-job runner, a visual integration tool, a durable workflow engine, an agent framework, and a sandbox provider. Each can appear in an architecture diagram labeled orchestration, even though the objects it controls are different.

Start with the responsibilities. The business process owns why a step exists and what follows it. An agent loop may choose tools while solving an ambiguous step. An execution environment hosts that work. Tools expose capabilities, and telemetry records what happened. Combining these components requires explicit contracts between them.

The comparison below separates these concerns before composing them. [[Workflow Orchestration in Agentic Systems]] develops durability, retries, external events, and human waits. [[Isolated Engineering Environments for Coding Agents]] covers the operating-system, identity, and network boundaries of a worker.

## Main Classes of Orchestration Tools

"Orchestrator" is a broad term.

Different tools solve different versions of the problem.

### Background Job Executors

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

### Integration and Workflow Automation

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

### LLM and Agent Orchestration

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

Agent frameworks manage stochastic reasoning loops, context window compaction, and dynamic tool selection. However, they typically lack built-in crash-proof event sourcing, distributed transaction guarantees, or cross-service compensation logic. In a robust architecture, the durable orchestrator owns the end-to-end business invariant, while the agent framework operates as an isolated sub-process tasked with solving an ambiguous reasoning step.

---

### Observability and Evaluation

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

## Deterministic and Agentic Workflow

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

## LLM as a Component of the Workflow

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

## A Layered Architecture

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

## Choosing the Right Level of Orchestration

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

Choose components by the state and guarantees they own. A product can implement several layers, but the architecture should still identify the owner of the process, the reasoning loop, the execution environment, and each external action.

## Related Notes

- [[Workflow Orchestration in Agentic Systems]] — Durable process state, idempotent operations, and long-running waits.
- [[Agent Deployment and Execution Models]] — Locating the model, harness, executor, and credentials across local and hosted deployments.
- [[Isolated Engineering Environments for Coding Agents]] — Provisioning and restricting the environment that executes broad engineering tools.
