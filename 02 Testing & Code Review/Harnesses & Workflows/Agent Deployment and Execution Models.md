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

The model, the agent loop, and the environment executing tools can run in different places. A local client can control a remote workspace, and a privately hosted worker can still send context to an external model.

This article compares the deployment choices and the responsibilities a team takes on with each. [[Building and Hosting Agent Execution Services]] develops a custom execution service, its control loop, hosting, workspace, and supported kinds of work. [[Data Privacy Boundaries in Agent Deployments]] follows context, credentials, and model requests across the trust boundaries. The deployment choice should identify the owner of each component before it is treated as a single local or cloud product.

## Agent Deployment and Execution Models

> See also: [[Agentic Coding Harness and Controlled Development Workflows]]

### Core idea

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

### Local agents

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

#### Advantages

- direct access to the developer's checkout;
- simple interactive debugging;
- low setup cost;
- easy experimentation;
- the agent sees the same environment as the developer;
- useful for pair-programming-style work.

#### Limitations

The agent is normally tied to that workstation.

If the machine is turned off or disconnected, the local execution loop stops unless some separate remote service keeps it alive.

This makes local agents particularly suitable for:

- interactive coding;
- exploratory work;
- debugging;
- small tasks;
- developer-specific workflows.

### Managed remote agents

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

### Why managed agents are attractive for teams

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

The shared platform can centrally manage:

- repository instructions;
- tools;
- allowed models and model-selection defaults;
- permissions;
- architecture rules;
- workflows;
- verification commands;
- tracing;
- cost policies;
- credential provisioning scoped to each identity and task.

This reduces duplicated setup work and makes required controls easier to maintain. Instructions guide the agent; permissions and required verification gates enforce the corresponding boundaries.

A shared platform can still offer personal interaction settings. One developer may want design discussion before implementation, while another starts with a test or prototype. Both remain subject to the same applicable data-access limits, architecture rules, and required checks. Personal preferences can change how work proceeds within those boundaries; they cannot remove the boundaries.

The organization and team need to distinguish mandatory requirements from defaults that developers may override. A common base with documented customization points can support both consistency and individual working styles. The same division can also be implemented in local harnesses: shared requirements do not, by themselves, require a centrally hosted agent (see [[Exploring Agent Harnesses#Shared requirements and personal working styles]]).

A managed agent can therefore behave more like CI infrastructure than like an IDE extension.

### Event-driven and unattended work

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

### Managed agent platforms

Several vendors provide managed infrastructure for running agents remotely.

#### Anthropic Claude Managed Agents

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

#### Microsoft Foundry Hosted Agents

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

#### Other provider ecosystems

Similar patterns also exist across other cloud and agent ecosystems.

The exact APIs differ, but the architectural choices are usually the same:

- use a provider-managed agent runtime;
- run a custom agent on managed compute;
- self-host the entire agent stack.

The deployment model should be selected independently from the model provider whenever possible.

Decoupling the orchestration engine from specific model providers avoids architectural lock-in. When frontier models shift in pricing, context windows, or reasoning capabilities, a provider-agnostic harness allows swapping models without redesigning tool contracts, persistent state machines, or CI integrations.

### Self-hosted agents

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

### Hybrid architecture

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

### Local and managed agents can coexist

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

### Choosing a deployment model

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
| Code must not reach an external model provider | Self-hosted model inference (see [[Local vs Cloud and Hybrid Model Execution]] and [[Dynamic Model Routing and Inference Gateways]]) |
| Avoid buying GPUs while controlling model inference | Private rented GPU infrastructure |
| No protected data may leave organization-controlled infrastructure | Fully self-hosted stack |
| Maximum data sovereignty | On-premises or isolated inference |
| Minimal operational overhead | Managed agent |
| Fully custom workflow | Custom-hosted agent |
| Deterministic workflow guarantees | Custom orchestrator |
| Provider portability | Custom harness |

### Final principles

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
13. Keep deterministic workflow rules in code when they must be enforced (see [[Building Determinism from Unpredictable Models]]).
14. Local, managed and hybrid agents can coexist in the same development organization.

## Related notes

- **[[Model Access and Execution Infrastructure]]** — Hardware architectures, API protocols, and runtime isolation for models.
- **[[Dynamic Model Routing and Inference Gateways]]** — Dispatching agent requests between local hardware and cloud providers.
- **[[Agentic Coding Harness and Controlled Development Workflows]]** — Designing deterministic harnesses, state machines, and execution loops.
- **[[Local vs Cloud and Hybrid Model Execution]]** — Economic and privacy trade-offs of hosting local open-weights models vs proprietary cloud APIs.
