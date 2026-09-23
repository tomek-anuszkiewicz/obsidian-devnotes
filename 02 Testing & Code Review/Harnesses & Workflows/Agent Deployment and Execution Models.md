---
title: Agent Deployment and Execution Models
tags:
  - ai-agents
  - agentic-coding
  - llm
  - cloud
  - infrastructure
  - software-engineering
  - deployment
  - software-development
aliases:
  - Agent deployment models
  - Local and managed agents
  - Agent hosting
---

# Agent Deployment and Execution Models

> See also: [[Agentic Coding Harness and Controlled Development Workflows]]

## Core idea

The **agent workflow** and the **place where the agent runs** are separate architectural concerns.

A useful decomposition is:

```text
1. Model
   Where does LLM inference happen?

2. Orchestrator / harness
   Where does the agent loop, workflow and state machine run?

3. Executor
   Where do files, Git, shell commands, builds and tests actually run?
```

These three components do not have to run in the same place.

For example, a model may run in a provider cloud while the harness and tool execution run on a developer workstation. A cloud orchestrator may also control a self-hosted executor inside a private network.

The main deployment models are:

1. local agents;
2. managed remote agents;
3. self-hosted agents;
4. hybrid agents.

## Local agents

A local coding agent runs its harness or execution loop on the developer's machine.

Typical examples are CLI or IDE coding agents that operate directly on a local checkout.

```text
Developer workstation
        |
        ├── agent harness
        ├── repository
        ├── filesystem
        ├── Git
        ├── compiler
        ├── tests
        └── local tools
               |
               v
          remote LLM API
```

The LLM inference may still happen remotely, but file access, shell commands, builds and tests are performed locally.

### Advantages

- direct access to the developer's checkout;
- simple interactive debugging;
- low setup cost;
- easy experimentation;
- the agent sees the same environment as the developer;
- useful for pair-programming-style work.

### Limitations

The agent is normally tied to that workstation.

If the machine is turned off or disconnected, the local execution loop stops unless some separate remote service keeps it alive.

This makes local agents particularly suitable for:

- interactive coding;
- exploratory work;
- debugging;
- small tasks;
- developer-specific workflows.

## Managed remote agents

A managed agent runs its agent loop and usually its execution environment in cloud infrastructure provided by a vendor.

Instead of depending on a developer workstation, the agent receives controlled access to repositories, documentation, tools, APIs and credentials.

```text
Git repositories ─────┐
Documentation ────────┤
Issue tracker ────────┤
CI/CD ────────────────┤
Internal APIs / MCP ──┤
                      v
              Managed Agent Runtime
                      |
              isolated workspace
                      |
              build / test / Git
```

The developer who starts the task does not have to keep a workstation running.

Managed sessions can therefore support:

- long-running tasks;
- asynchronous work;
- overnight execution;
- scheduled maintenance;
- CI-triggered work;
- webhook-triggered work;
- repository-wide analysis;
- pull-request review.

## Why managed agents are attractive for teams

For an individual developer, a local agent is often the simplest choice.

For a team, a remote or managed agent can become **shared development infrastructure**.

Instead of:

```text
Developer A → local agent A
Developer B → local agent B
Developer C → local agent C
```

the organization can provide:

```text
               Shared Agent Platform
                 /       |       \
                /        |        \
          Developer A Developer B Developer C
```

The shared platform can enforce the same:

- repository instructions;
- tools;
- model selection;
- permissions;
- architecture rules;
- workflows;
- verification commands;
- tracing;
- cost policies;
- credentials.

This reduces the risk that every developer maintains a slightly different local setup.

A managed agent can therefore behave more like CI infrastructure than like an IDE extension.

## Event-driven and unattended work

A remote agent can be started manually, but it can also be invoked by infrastructure events.

For example:

```text
Jira issue becomes "Ready"
          |
          v
      start agent
          |
          v
    analyze repository
          |
          v
      create plan
          |
      human approval
          |
          v
    implement on branch
          |
          v
      run verification
          |
          v
       create PR
```

Possible triggers include:

```text
GitHub / GitLab webhook
CI event
scheduled job
issue tracker event
manual API request
message queue event
```

The merge or production deployment can still remain protected by normal CI, branch protection and human approval.

## Managed agent platforms

Several vendors provide managed infrastructure for running agents remotely.

### Anthropic Claude Managed Agents

Claude Managed Agents provide a pre-built Claude agent harness together with managed execution infrastructure.

An agent configuration can include concepts such as:

- model;
- system prompt;
- tools;
- MCP servers;
- skills;
- multi-agent configuration.

The important characteristic is that the organization configures the Anthropic-managed harness rather than implementing the complete agent loop itself.

A managed session can operate in a vendor-managed execution environment or, depending on the setup, use execution infrastructure controlled by the organization.

This model is attractive when a team wants:

- the Claude agent runtime;
- long-running sessions;
- remote execution;
- shared configuration;
- managed lifecycle;
- minimal custom orchestration code.

### Microsoft Foundry Hosted Agents

Microsoft Foundry Hosted Agents support hosting an agent application in Microsoft-managed infrastructure.

This model is particularly interesting when the development team wants to own more of the agent implementation.

A team can write the agent or workflow in code and let the platform provide infrastructure concerns such as:

- compute;
- scaling;
- identity;
- session state;
- telemetry;
- deployment lifecycle.

For a .NET team, the development path can be close to:

```text
dotnet run
    |
    v
local agent/workflow
    |
    v
container or source deployment
    |
    v
Foundry Hosted Agent
```

The important distinction is:

```text
Managed harness
    = configure a vendor-provided agent loop

Hosted custom agent
    = write your own agent logic and let a platform host it
```

### Other provider ecosystems

Similar patterns also exist across other cloud and agent ecosystems.

The exact APIs differ, but the architectural choices are usually the same:

- use a provider-managed agent runtime;
- run a custom agent on managed compute;
- self-host the entire agent stack.

The deployment model should be selected independently from the model provider whenever possible.

Decoupling the orchestration engine from specific model providers avoids architectural lock-in. When frontier models shift in pricing, context windows, or reasoning capabilities, a provider-agnostic harness allows swapping models without redesigning tool contracts, persistent state machines, or CI integrations.

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

## Self-hosted agents

A self-hosted agent runs the agent loop in infrastructure controlled by the organization.

```text
Company infrastructure
        |
        ├── orchestrator
        ├── agent workers
        ├── repository access
        ├── internal services
        └── build environment
                 |
                 v
             LLM API
```

This provides strong control over the agent execution environment, including:

- networking;
- secrets;
- filesystem access;
- runtime versions;
- build infrastructure;
- observability;
- data retention for the agent runtime.

It also means the organization must operate more infrastructure.

This model can be attractive when the agent needs access to private systems that should not be exposed to an external execution environment.

However, **self-hosting the agent does not imply self-hosting the model**.

If the agent still calls an external LLM API, then prompts, selected repository content, diffs, compiler output, test failures and other context sent to the model cross the organization's trust boundary.

## Data sovereignty and fully private agents

For organizations with strict confidentiality requirements, the privacy boundary must be analyzed separately from the agent deployment boundary.

A useful rule is:

> **The location of the agent does not determine the privacy boundary. The location of model inference does.**

There are several important deployment levels.

### Self-hosted agent with an external model API

```text
Company infrastructure
        |
        ├── harness
        ├── executor
        ├── repository
        └── internal tools
                 |
                 v
          External LLM API
```

The repository and execution environment may remain inside the company network, but any context sent to the model leaves that environment.

This can still be acceptable when the organization trusts contractual, technical and retention guarantees offered by the model provider.

It is **not** sufficient for a policy that requires source code and prompts to never reach an external model provider.

### Self-hosted stack on rented private GPU infrastructure

An organization does not necessarily have to buy and operate its own physical GPU servers.

It can deploy its own inference stack on rented GPU compute while still avoiding a vendor-hosted LLM API.

```text
Company systems
        |
        ├── repositories
        ├── documentation / RAG
        ├── harness
        ├── executor
        └── internal services
                 |
                 v
        Private GPU environment
                 |
                 ├── inference server
                 └── self-hosted model
```

The GPU environment can be implemented using virtual machines, Kubernetes, dedicated hosts or other rented compute.

Typical controls can include:

- private VPC / VNet networking;
- no public ingress;
- restricted or disabled egress;
- private endpoints;
- organization-controlled identity and access policies;
- organization-controlled encryption keys;
- private model and artifact storage;
- internal logging and telemetry.

This removes dependence on a model provider's inference API, but the physical infrastructure is still operated by the cloud or hosting provider.

For many organizations, this is a useful middle ground between SaaS model APIs and owning a GPU datacenter.

In practice, this pattern pairs dedicated cloud compute (such as AWS `g5`/`p4` instances or Azure ND-series) with optimized open-weights inference servers like vLLM or TensorRT-LLM. Connecting the inference cluster to internal networks via private endpoints (AWS PrivateLink or Azure Private Link) eliminates public internet exposure and multi-tenant data sharing without incurring the procurement lead times of physical hardware.

### Fully on-premises or isolated deployment

The strongest sovereignty model is to run the complete stack on infrastructure physically controlled by the organization.

```text
Company datacenter
        |
        ├── repositories
        ├── documentation / RAG
        ├── harness
        ├── executor
        ├── inference server
        ├── GPU cluster
        └── model weights
```

This can be deployed with no dependency on an external inference service and, if required, without Internet access.

Such a design is appropriate when the requirement is literally:

> Source code, prompts, retrieved context and model inputs must not leave organization-controlled infrastructure.

The trade-off is significantly higher operational responsibility, including:

- GPU procurement and capacity planning;
- model serving;
- model upgrades;
- scaling;
- observability;
- security patching;
- inference optimization;
- reliability and redundancy.

### The model becomes part of the infrastructure decision

Strict data-sovereignty requirements can also constrain model selection.

If a model is available only through a vendor API, then an organization that forbids external inference cannot use it for protected workloads.

The organization may instead need a model whose weights can be deployed in its own environment.

This creates an important trade-off:

```text
Maximum model choice
        |
        v
External model APIs
        |
        | increasing infrastructure control
        v
Self-hosted inference on rented GPU compute
        |
        v
Fully on-premises inference

Maximum data sovereignty
```

The cost of strict sovereignty is therefore not only infrastructure cost. It can also reduce access to closed models that are available only as managed services.

There is also an operational capability trade-off. While open-weights models (such as Llama, Qwen, or specialized coding variants) have narrowed the gap for standard implementation tasks, the most capable reasoning models often remain exclusive to managed cloud APIs. Organizations requiring complete on-premises air-gapping must accept this trade-off, prioritizing total data isolation over frontier reasoning capabilities.

## Hybrid architecture

The model, orchestrator and executor do not need to run together.

For example:

```text
Cloud orchestrator
       |
       v
remote agent loop
       |
       v
self-hosted executor
       |
       +-- private repository
       +-- internal build infrastructure
       +-- private databases
```

Another example:

```text
Vendor LLM
    |
    v
Company-hosted harness
    |
    v
Company-hosted executor
```

A hybrid setup can combine:

- cloud model inference;
- centrally managed orchestration;
- private local execution.

This can be useful when the organization wants cloud-scale orchestration but must keep some execution close to internal systems.

This hybrid topology mirrors the architecture of modern CI runner systems like GitHub Actions or GitLab Runners. A centralized, cloud-hosted control plane manages task dispatch, scheduling, and UI state, while a lightweight runner daemon running inside the private network executes local builds and tests. Because the internal runner connects outbound to the control plane over a secure WebSocket or polling connection, no inbound firewall ports or internal network endpoints need to be exposed to the public internet.

## Local and managed agents can coexist

Local versus managed should not be treated as an exclusive choice.

A development organization can use both:

```text
Local agent
    |
    +-- interactive development
    +-- debugging
    +-- exploratory work
    +-- developer-specific tasks

Managed agent
    |
    +-- shared team workflows
    +-- unattended tasks
    +-- scheduled maintenance
    +-- repository-wide analysis
    +-- PR review
    +-- CI-triggered work
```

A developer may use a local agent while actively modifying code and send larger or unattended tasks to a remote agent.

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

- **Ephemeral sandboxing**: Execute tool calls and compilation steps inside disposable containers or microVMs (such as gVisor or Firecracker). Tearing down the environment immediately after execution prevents state poisoning, contaminated package caches, or untrusted dependencies from persisting across tasks.
- **Network egress filtering**: Restrict outbound network access from the execution runtime. Allowlist only required package registries, internal source control, and inference endpoints. Explicitly block access to cloud instance metadata endpoints (`169.254.169.254`) to prevent credentials from being extracted by untrusted dependencies.
- **Short-lived credentials**: Avoid persisting long-lived API keys or deployment credentials on disk. Use short-lived, workload-identity-federated tokens (such as OIDC) scoped strictly to the task.
- **Clean workspace trees**: Provision each task in a fresh, isolated Git worktree. Never allow untracked build artifacts or modified scripts to leak across unrelated agent runs.

## Choosing a deployment model

A simple decision guide:

| Need | Good starting point |
| --- | --- |
| Interactive personal coding | Local agent |
| IDE/CLI pair programming | Local agent |
| Long-running unattended work | Managed or self-hosted agent |
| Shared agent for a team | Managed or self-hosted agent |
| Webhook / CI-triggered execution | Managed or self-hosted agent |
| Maximum control over agent execution | Self-hosted agent |
| Private internal execution | Self-hosted or hybrid agent |
| Code must not reach an external model provider | Self-hosted model inference |
| Avoid buying GPUs while controlling model inference | Private rented GPU infrastructure |
| No protected data may leave organization-controlled infrastructure | Fully self-hosted stack |
| Maximum data sovereignty | On-premises or isolated inference |
| Minimal operational overhead | Managed agent |
| Fully custom workflow | Custom-hosted agent |
| Deterministic workflow guarantees | Custom orchestrator |
| Provider portability | Custom harness |

## Final principles

1. The model, harness and executor are separate architectural components.
2. Local agents are the simplest option for interactive development.
3. Managed agents are especially valuable as shared team infrastructure.
4. Remote execution enables unattended, scheduled and event-driven work.
5. A custom agent loop can be written in ordinary application code.
6. A custom harness can be hosted on general-purpose cloud infrastructure or a specialized agent platform.
7. Use managed infrastructure when operational simplicity matters more than full control.
8. Use self-hosting when networking, security or execution requirements demand it.
9. Self-hosting the agent does not imply self-hosting the model.
10. The model inference location determines whether prompts and selected code cross the organizational trust boundary.
11. Strict data-sovereignty requirements may require both self-hosted agent infrastructure and self-hosted model inference.
12. Rented private GPU infrastructure can provide a middle ground between external model APIs and fully on-premises deployment.
13. Keep deterministic workflow rules in code when they must be enforced.
14. Local, managed and hybrid agents can coexist in the same development organization.
