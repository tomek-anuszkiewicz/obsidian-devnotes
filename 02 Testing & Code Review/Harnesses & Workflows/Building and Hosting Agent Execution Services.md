---
title: "Building and Hosting Agent Execution Services"
tags:
  - ai-agents
  - infrastructure
  - orchestration
  - deployment
  - developer-experience
aliases:
  - "Custom Agent Runtimes and Hosting"
  - "Agent Execution as a Managed Service"
  - "Hosting Coding and Knowledge-Work Agent Environments"
  - "Coding and Knowledge-Work Environments"
---

A team wants an agent that can resume a task, use a repository and engineering tools, and return a candidate with evidence. The service around the model must own execution state, enforce permitted actions, and provide an environment that lasts as long as the task requires.

Building the loop in application code or using a framework is one choice. Hosting workers, managing workspaces and processes, separating interactive sessions from durable work, and deciding which capabilities the environment supplies are additional choices. A model response should enter an explicit control process rather than grant itself the next external action.

The sections below develop the loop, hosting options, permissions, and coding and knowledge-work environments. [[Agent Deployment and Execution Models]] compares deployment models. [[Data Privacy Boundaries in Agent Deployments]] examines the distinct question of which data leaves each environment and what authority its credentials provide.

## Writing the agent loop yourself

Using a ready-made agent harness is not mandatory.

The agent loop can be implemented directly in an ordinary programming language such as:

- Python;
- C#;
- TypeScript;
- Go.

At its simplest:

```python
while not state.finished:
    response = call_model(
        messages=state.messages,
        tools=available_tools
    )

    if response.requests_tool:
        result = execute_tool(response.tool_call)
        state.messages.append(result)
    else:
        state.finished = True
```

A production harness can then add:

```text
state machine
DAG execution
parallel branches
retries
timeouts
budgets
human approval gates
tool permissions
context management
checkpoints
persistent state
tracing
model routing
subagents
```

This gives the organization control over the workflow while treating models as replaceable execution components.

```text
Custom Python/.NET harness
          |
          +--> Claude
          |
          +--> OpenAI model
          |
          +--> Gemini
          |
          +--> local model
```

## Deterministic orchestration with probabilistic workers

A useful design principle is:

> **Keep the workflow deterministic where possible and use LLM inference inside the steps that require judgment.**

For example:

```text
Task
 |
 v
Plan Agent
 |
 v
Human Approval
 |
 v
Implementation Agent
 |
 v
dotnet build
 |
 v
dotnet test
 |
 +-------------------+
 |                   |
pass                fail
 |                   |
 v                   v
Review Agent      Repair Agent
 |                   |
 +---------<---------+
 |
 v
Draft PR
```

The transitions, retry limits and approval requirements can be enforced by code.

The individual agents remain probabilistic.

This is stronger than encoding the entire process only as natural-language instructions such as:

```text
plan first;
then implement;
then test;
then review.
```

Text instructions guide model behavior. A state machine can make invalid transitions impossible.

Hard verification gates protect the codebase from model hallucinations. If a compilation or test step fails, code logic routes the diagnostic output directly into a repair loop or halts for human review. Enforcing validation invariants in software ensures that an optimistic model response cannot prematurely open a pull request or merge unverified code.

## Frameworks for custom orchestration

A custom agent loop does not require a graph framework, but frameworks can help once the workflow becomes complex.

Possible approaches include:

- a simple custom state machine;
- LangGraph;
- Microsoft Agent Framework workflows;
- Temporal;
- Durable Functions;
- queue-based worker orchestration;
- a custom DAG engine.

The important decision is not which framework is used, but which parts are:

- deterministic workflow logic;
- probabilistic model decisions;
- external tool execution;
- persistent state;
- human approval.

For a small system, plain application code may be easier to understand than a large orchestration framework.

## Hosting a custom agent

A custom agent application is ultimately a service, worker or container and can be hosted using ordinary cloud infrastructure.

Possible environments include:

### Azure

- Azure Container Apps;
- Azure Kubernetes Service;
- Azure Functions;
- Durable Functions;
- virtual machines;
- Microsoft Foundry Hosted Agents.

### AWS

- ECS;
- EKS;
- Lambda;
- EC2.

### Google Cloud

- Cloud Run;
- GKE;
- Compute Engine.

### General-purpose infrastructure

- Kubernetes;
- Docker hosts;
- virtual machines;
- serverless container platforms;
- internal company infrastructure.

The appropriate host depends on whether the agent needs:

- long-running processes;
- persistent filesystem state;
- queues;
- scheduling;
- webhook endpoints;
- isolated sandboxes;
- private network access;
- access to internal repositories;
- access to internal package feeds;
- databases or internal APIs.

Execution duration and filesystem dynamics heavily influence hosting choices. Serverless runtimes like AWS Lambda work well for lightweight webhook dispatch, but their strict execution timeouts (such as Lambda's 15-minute ceiling) make them unsuitable for heavy compilation passes or multi-turn test suites. Similarly, agents performing large codebase refactorings benefit from container hosts with fast, warm disk checkouts rather than cold-starting full repository clones inside ephemeral functions.

## Security and permissions

Deployment location does not remove the need for least privilege.

A shared cloud agent should not automatically receive access to every repository, environment or production credential.

Permissions should be scoped by role.

For example:

```text
Planner
  read repository
  read documentation
  read issue tracker

Implementer
  read/write feature branch
  build
  test

Reviewer
  read repository
  read diff
  no write access

Release Agent
  deployment permissions
```

The ability to share an agent across a team makes centralized identity and permission management more important, not less.

### Execution sandboxing and isolation boundaries

Running agent-generated code and arbitrary shell commands on shared infrastructure requires defense-in-depth isolation:

[[Security Boundaries for Agents, RAG, and MCP]] separates the sandbox's enforced limits from approval prompts and from a worktree's file-state isolation.

- **Ephemeral sandboxing**: Execute tool calls and compilation steps inside disposable containers or microVMs (such as gVisor or Firecracker). Tearing down the environment immediately after execution prevents state poisoning, contaminated package caches, or untrusted dependencies from persisting across tasks (see [[Agentic Coding Harness and Controlled Development Workflows]]).
- **Network egress filtering**: Restrict outbound network access from the execution runtime. Allowlist only required package registries, internal source control, and inference endpoints. Explicitly block access to cloud instance metadata endpoints (`169.254.169.254`) to prevent credentials from being extracted by untrusted dependencies.
- **Short-lived credentials**: Avoid persisting long-lived API keys or deployment credentials on disk. Use short-lived, workload-identity-federated tokens (such as OIDC) scoped strictly to the task.
- **Clean workspace trees**: Provision each task in a fresh, isolated Git worktree. Never allow untracked build artifacts or modified scripts to leak across unrelated agent runs.

## Interactive work can use centrally managed execution

A developer can interact with an agent through a local client while the repository, tools, and application run in a managed remote workspace. The same environment service can provision unattended tasks. Interactive sessions benefit from low startup latency and persistence; batch tasks often benefit from disposable environments and cost controls.

Separate workspace persistence, agent-session continuity, and durable workflow state. A saved VM does not ensure that the agent retains its conversation, and a resumed conversation does not ensure that files or services are unchanged. Record enough artifacts and environment information to reconstruct the work.

Use containers where they fit, Windows VMs for desktop behavior that requires them, and scoped capability services for databases, logs, and cloud inspection. A VM with a production login still has production authority. Enforce host, identity, and network boundaries together (see [[Isolated Engineering Environments for Coding Agents]]).

## Coding and General Knowledge-Work Environments

Deployment location and work environment are different choices. A remote service can expose a coding workspace or a broader document-and-application environment; either can participate in a workflow with explicit outputs and permissions. [[Agentic Software Development Workflows]] compares task contracts, while [[Taking Coding Agent Tasks to a Verified Result]] follows the evidence required for coding-task completion.

### Agentic Execution Environments

Workflows such as issue-driven implementation and verification-driven development answer the question:

> **How should an agent perform the work?**

There is another, orthogonal question:

> **Where does the agent work, and what kind of environment is available to it?**

This distinction becomes increasingly important as agents move beyond source-code generation.

A useful conceptual separation is:

```text
Workflow
→ how the work is organized

Execution environment
→ where the work is performed and which resources the agent can manipulate
```

The same workflow may potentially be executed in very different environments.

For example, plan-driven or verification-driven work can happen inside a coding workspace, while research-driven or document-oriented work may happen inside a more general knowledge-work environment.

### Coding Environments

Coding-oriented agent environments are optimized around:

- repositories,
- source files,
- terminals,
- builds,
- tests,
- Git,
- branches and worktrees,
- development tools.

Examples include environments such as Claude Code, Codex, and coding agents integrated with IDEs.

Their natural unit of work is usually a software engineering task:

```text
Issue
↓
Repository
↓
Code Change
↓
Tests
↓
Commit / Pull Request
```

### General Knowledge-Work Environments

Claude Cowork represents a broader category.

Instead of focusing primarily on repositories and terminals, a Cowork-style environment is designed around general knowledge work:

- documents,
- files,
- spreadsheets,
- research,
- reports,
- presentations,
- connected applications.

Its natural tasks may look like:

```text
Collect information
↓
Inspect documents
↓
Compare data
↓
Prepare analysis
↓
Produce report / spreadsheet / presentation
```

A useful mental model is:

```text
Chat
→ conversation with a model

Claude Code
→ agentic software workspace

Claude Cowork
→ agentic knowledge-work workspace
```

Cowork is therefore not directly comparable to Fleet, Squad, subagents, or multiple parallel sessions.

These concepts describe different dimensions.

```text
Execution environment
├── coding workspace
├── knowledge-work workspace
├── browser environment
├── desktop / OS environment
└── cloud / background environment

Work organization
├── single agent
├── multiple independent sessions
├── subagents
├── fleet-style parallel execution
└── persistent agent team
```

The two dimensions can be combined.

A coding environment may use one agent or many agents.

A knowledge-work environment may also eventually use specialized workers, reviewers, or parallel research agents.

This gives a broader model:

```text
                 WORK ORGANIZATION

              Single   Fleet   Team
                │        │       │
Coding          ●        ●       ●
Knowledge Work  ●        ●       ●
Browser         ●        ●       ●
Desktop / OS    ●        ●       ●
Cloud           ●        ●       ●
```

This distinction helps avoid treating every new agent product as a competing methodology.

Some products primarily change **how agents are orchestrated**.

Others primarily expand **what environment agents can operate in**.

### From Tools to Digital Workers

This also suggests a larger evolution:

```text
Chatbot
   ↓
Agent with tools
   ↓
Agent with a repository
   ↓
Agent with a workspace
   ↓
Agent controlling applications
   ↓
General digital worker
```

Claude Cowork is useful in this model because it demonstrates that the agentic paradigm is expanding beyond software development.

The same concepts that make coding agents useful—

- autonomous task execution,
- tool use,
- persistent workspaces,
- feedback loops,
- artifact creation,
- verification,
- delegation—

can be applied to general office and knowledge work.

For software engineers, this may create a split between different agentic environments:

```text
Coding agent
→ implementation, debugging, testing, refactoring

Knowledge-work agent
→ requirements, documentation, analysis, reports, presentations

Browser / application agent
→ external systems, research, administrative workflows
```

The long-term direction is therefore not necessarily one universal agent interface.

It may instead be a collection of specialized execution environments sharing similar agentic principles.

Define the task state and outputs independently of any one model session. Make the environment lifecycle, tool permissions, checks, and result publication explicit so workers can fail or be replaced without leaving the process owner guessing what happened.

## Related Notes

- [[Agent Deployment and Execution Models]] — Local, managed, self-hosted, and hybrid deployment choices.
- [[Data Privacy Boundaries in Agent Deployments]] — Data flows, model requests, identities, and credentials across trust boundaries.
- [[Composing Agent Platforms from Orchestrators, Runtimes, and Tools]] — Separating business process control, agent reasoning, and execution capabilities.
