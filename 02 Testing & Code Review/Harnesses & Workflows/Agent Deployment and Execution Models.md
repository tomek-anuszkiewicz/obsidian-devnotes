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
  - The 3-Plane Agent Architecture
  - Model vs Harness vs Executor
---

# Agent Deployment and Execution Models

> See also: [[Agentic Coding Harness and Controlled Development Workflows]], [[Model Access and Execution Infrastructure]]

When designing or deploying coding agents, the agent workflow logic and the environment where that logic physically runs are distinct architectural concerns. Conflating them leads to muddled security boundaries, fragile workflows, and operational headaches. 

A clean architecture separates the system into three distinct planes:

```text
1. Model Plane (Inference)
   Where do the weights live and where does token generation occur?
   (Provider API, dedicated private cloud GPU, or local/on-prem inference server)

2. Orchestration Plane (Harness & State)
   Where does the agent loop, state machine, and context management live?
   (Developer CLI, background daemon, team workflow service, or managed platform)

3. Execution Plane (Runtime Environment)
   Where do the filesystem, Git operations, shell commands, builds, and tests run?
   (Developer workstation, ephemeral container sandbox, isolated CI runner, or cloud VM)
```

These three planes do not need to run on the same machine or inside the same network boundary. 

For instance, an agent might run inference against an external provider API, execute its orchestration loop on a developer's laptop, but dispatch all builds, tests, and bash commands to an isolated cloud sandbox. Alternatively, an event-driven cloud orchestrator might control an executor daemon running inside a secured on-premises network.

Understanding how to decouple and combine these planes determines how well your agents scale, how securely they access internal systems, and how strictly they honor data sovereignty policies.

---

## Architectural Planes and Topologies

Decoupling reasoning from physical execution yields several standard operational configurations:

```text
Configuration A: Local Interactive (Inner Loop)
[ Laptop: Harness + Git + Tools + Compiler ] ──► HTTPS ──► [ Model Provider API ]

Configuration B: Team Managed Service (Unattended / CI)
[ Event / Webhook ] ──► [ Cloud Orchestrator ] ──► [ Ephemeral Container Sandbox ]
                               │                               │
                               ▼                               ▼
                     [ Provider Model API ]         [ Private Git Repository ]

Configuration C: Air-Gapped / High-Sovereignty
[ Private VPC: Team Orchestrator ] ──► [ Internal Execution Worker ] ──► [ On-Prem Inference Server ]

Configuration D: Hybrid Runner
[ Cloud Orchestrator ] ──► Secure Tunnel ──► [ On-Prem Runner Daemon ] ──► [ Internal Builds / Repos ]
          │
          ▼
[ Provider Model API ]
```

The four primary deployment models across these topologies are:

1. **Local agents**
2. **Managed remote agents**
3. **Self-hosted enterprise agents**
4. **Hybrid agents**

---

## Comparative Matrix: Deployment Models

| Dimension | Local Agent | Managed Remote Agent | Self-Hosted Agent | Hybrid Agent |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Use Case** | Interactive coding, inner-loop debugging | Unattended tasks, overnight PRs, scheduled runs | Internal VPC codebases, strict compliance | Cloud orchestration controlling private runners |
| **Workstation Dependency** | High (machine must stay online and awake) | None (runs asynchronously in cloud) | None (runs in private cluster/compute) | None (executes on internal worker pool) |
| **Setup Overhead** | Low (CLI or IDE extension install) | Minimal (SaaS platform onboarding) | High (Kubernetes, runners, monitoring, IAM) | Moderate (lightweight runner daemon deployment) |
| **Network Locality** | Developer workstation LAN | Cloud vendor network | Corporate intranet / private VPC mesh | Split perimeter (inbound control plane, local egress) |
| **Trust Boundary** | Local machine | Vendor managed infrastructure | Enterprise perimeter | Shared / brokered trust boundary |
| **Resource Limits** | Workstation CPU/RAM/Battery | Elastic cloud instances | Cluster capacity limits | Internal worker pool capacity |

---

## Local Agents

A local coding agent runs its orchestration loop and tool execution directly on the developer's workstation. CLI utilities and IDE extensions that manipulate local checkouts operate on this model.

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

Model inference typically happens remotely over an HTTPS API, but all file reads, file edits, shell commands, builds, and test runs execute against the developer's local filesystem.

### Advantages

- **Zero context friction**: The agent immediately sees uncommitted changes, local branches, and developer-specific environment overrides.
- **Interactive debugging**: The developer can observe the agent's work in real time, interrupt bad execution paths, and inspect diffs inside familiar IDE tooling.
- **Low infrastructure overhead**: No cloud runners, Kubernetes clusters, or isolated sandboxes to provision or manage.
- **Familiar environment**: The agent runs using the exact compilers, runtimes, and local credentials already configured on the machine.

### Limitations

The agent's lifecycle is bound to the physical machine. If the laptop goes to sleep, loses Wi-Fi, or runs out of memory during a heavy compilation step, the execution loop halts.

Local agents are ideal for:
- Interactive pair programming and inner-loop feature work
- Exploratory refactoring and ad-hoc debugging
- Small, well-scoped tasks with immediate human oversight
- Developer-specific tooling and experiment workflows

---

## Managed Remote Agents

A managed remote agent runs both its orchestration loop and its execution environment on managed cloud infrastructure provided by a platform vendor.

Instead of binding to a developer's laptop, the agent receives explicit, scoped credentials to pull repositories, consult documentation, run tools, and interact with APIs.

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

Because the execution does not depend on a developer workstation remaining online, managed sessions handle long-running, asynchronous, and scheduled workflows that would otherwise tie up a local machine:

- Overnight refactoring and broad codebase upgrades (such as migrating dependency versions)
- Asynchronous task dispatch (assigning a task and checking back hours later)
- Scheduled repository maintenance and security patch application
- CI-triggered failure triage and automated test repair
- Deep, repository-wide code reviews and architectural audits

---

## Why Managed Agents Scale Across Teams

For an individual engineer, a local agent CLI is usually the path of least resistance. But across an engineering organization, running uncoordinated local agents creates fragmentation:

```text
Developer A → local agent A (custom prompt, local tools, unverified model)
Developer B → local agent B (different tool versions, unvetted scripts)
Developer C → local agent C (personal API key, missing corporate linting rules)
```

Shifting to a managed agent turns individual tooling into **shared development infrastructure**:

```text
               Shared Agent Platform
                 /       |       \
                /        |        \
          Developer A Developer B Developer C
```

A shared platform enforces consistency across the engineering org:

- **Repository instructions**: Consistent system prompts, architecture guidelines, and coding standards.
- **Verified toolsets**: Standardized linters, compilers, testing suites, and MCP servers.
- **Centralized model routing**: Directing requests to approved models and enterprise-contracted endpoints.
- **Guardrails and policy**: Enforcing read-only access on critical branches, blocking forbidden terminal commands, and controlling egress traffic.
- **Unified telemetry**: Tracking token usage, cost attribution, tool failure rates, and execution traces.
- **Credential management**: Using scoped, short-lived tokens instead of storing production or repository secrets on personal laptops.

Managed agents operate more like continuous integration (CI) infrastructure than desktop productivity apps.

---

## Event-Driven and Unattended Workflows

Because remote agents run on servers rather than laptops, they can respond directly to infrastructure events without human initiation:

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
      run verification (build / test / lint)
          |
          v
       create PR
```

Common trigger mechanisms include:

- **Git webhooks**: Opening an issue, pushing to a branch, or requesting a review.
- **CI failures**: Automatically spinning up an agent to analyze a failed test run, fix the regression on a branch, and push a patch.
- **Issue tracker events**: Moving a ticket to "Ready for Dev" in Jira or Linear.
- **Scheduled cron jobs**: Nightly dependency updates, dead code elimination, or documentation synchronization.
- **Message queues**: Processing task queues from Slack bots or developer portals.

Critical checkpoints—such as merging to the main branch or releasing to production—remain guarded by standard branch protection rules, mandatory CI passes, and human code reviews.

---

## Managed Agent Platforms

Vendors offer different balances between turnkey operational convenience and architectural control.

### Anthropic Claude Managed Agents

Claude Managed Agents bundle an optimized, Anthropic-managed harness together with managed execution infrastructure.

Configuration centers on declarative primitives:
- Model selection (e.g., Sonnet, Haiku)
- System instructions and skill libraries
- Tool definitions and Model Context Protocol (MCP) servers
- Multi-agent coordination structures

The engineering team configures the agent rather than building the control loop from scratch. Sessions run within isolated environments managed by the provider, or against dedicated customer-managed execution workers. 

This model fits teams that want an out-of-the-box runtime with minimal plumbing, enterprise-grade context management, and zero orchestration code to maintain.

### Microsoft Foundry Hosted Agents

Microsoft Foundry Hosted Agents focus on hosting custom agent applications on managed infrastructure.

Instead of locking you into a proprietary harness format, this approach lets you write the agent logic directly in code (using .NET, Python, or TypeScript) while the cloud platform handles operational concerns:
- Compute orchestration and horizontal autoscaling
- Managed identity (Azure Entra ID) and secret injection
- Persistent session storage and execution checkpoints
- OpenTelemetry instrumentation and audit logging
- Container deployment pipelines

For a .NET engineering team, the workflow mirrors standard microservice delivery:

```text
dotnet run (local testing)
    |
    v
local agent workflow validation
    |
    v
container image build
    |
    v
deploy to Foundry Hosted Agent runtime
```

The distinction comes down to control:

- **Managed harness**: Configure a vendor-provided agent loop and execution environment.
- **Hosted custom agent**: Write your own orchestration code and let a platform manage the servers, scaling, and state persistence.

### Choosing Across Provider Ecosystems

Similar hosting patterns exist across AWS (Bedrock Agents), Google Cloud (Vertex AI Agent Builder), and specialized platforms like Modal or Replit. The fundamental decision is always the same:

1. Use a vendor-managed agent runtime for fast time-to-market.
2. Deploy a custom agent container onto managed application compute (e.g., Azure Container Apps, AWS ECS, Google Cloud Run).
3. Self-host the entire orchestration and execution stack on private infrastructure.

Keep your agent deployment model decoupled from your model provider choice whenever possible. Tying your orchestration engine strictly to a single model vendor creates painful migration friction as model price-performance characteristics shift.

---

## Writing the Agent Loop Yourself

You do not need a heavy vendor harness or framework to build a production agent. At its foundation, an agent loop is an ordinary while-loop paired with tool dispatch:

```python
while not state.finished:
    response = call_model(
        messages=state.messages,
        tools=available_tools
    )

    if response.requests_tool:
        result = execute_tool(response.tool_call)
        state.messages.append({
            "role": "tool",
            "tool_call_id": response.tool_call.id,
            "content": result
        })
    else:
        state.finished = True
```

In a production harness, that basic loop expands with essential operational controls:

- **State machine transitions**: Restricting which tools can be called based on the current phase of execution.
- **Directed Acyclic Graph (DAG) execution**: Orchestrating parallel planning, execution, and review steps.
- **Budgets and circuit breakers**: Setting hard caps on total tokens, wall-clock runtime, and API expenditure per task.
- **Human approval gates**: Pausing execution for explicit user confirmation before destructive commands (e.g., git force pushes, database migrations).
- **Tool permission boundaries**: Enforcing read-only vs. read-write access dynamically.
- **Context window management**: Compacting history, truncating massive tool outputs, and summarizing older messages to prevent out-of-context errors.
- **Checkpoints and durable state**: Persisting state after every step so an execution can pause, crash, resume, or rewind safely.
- **Dynamic model routing**: Using cheap, fast models for planning or syntax checks, and reasoning-heavy models for code generation and review.

Building your own harness gives your team total ownership over the workflow, treating underlying LLMs as interchangeable inference engines:

```text
Custom Python/.NET Harness
          |
          +--> Claude (Sonnet / Opus)
          |
          +--> OpenAI (GPT-4o / o-series)
          |
          +--> Google Gemini
          |
          +--> Self-hosted open weights (vLLM / Ollama)
```

---

## Deterministic Orchestration with Probabilistic Workers

A critical architectural rule for reliable agent systems:

> **Keep the workflow deterministic in code, and use LLM inference only inside the specific steps that require judgment.**

Do not rely entirely on natural-language system prompts to guide a complex lifecycle (e.g., "First create a plan, then write the code, then run tests, and only open a PR if the tests pass"). A model can hallucinate past an instruction, misunderstand state, or prematurely mark a task complete.

Instead, enforce lifecycle rules in code via a deterministic state machine:

```text
Task Triggered
      |
      v
[ Plan Agent ] ── (Generates technical spec)
      |
      v
[ Human Approval Gate ] ── (Rejection routes back to Plan Agent)
      |
      v
[ Implementation Agent ] ── (Writes code to branch)
      |
      v
[ Deterministic Step: dotnet build ]
      |
      +── Fail ──► [ Repair Agent ] ──► (Retries build, capped at 3 loops)
      |                    ▲
      v Pass               │
[ Deterministic Step: dotnet test ]
      |                    │
      +── Fail ────────────┘
      |
      v Pass
[ Review Agent ] ── (Validates architecture and code style)
      |
      v
[ Draft PR Created ]
```

The transitions, retry budgets, compilation steps, and approval requirements are strictly enforced by the software runtime. The LLMs act as probabilistic workers inside bounded, verifiable boxes. 

A state machine makes illegal transitions structurally impossible. If `dotnet test` fails, the system cannot open a pull request, no matter what the model claims in its text generation.

---

## Orchestration Frameworks

A custom agent loop does not require a third-party framework, but as workflows gain branching logic and persistence needs, choosing the right tool matters:

- **Plain application code**: Ideal for simple, linear tool-calling workflows. Easy to write, profile, and debug with standard tools.
- **LangGraph**: Useful for complex graph topologies, cyclic loops, and stateful multi-agent workflows in Python or TypeScript.
- **Temporal / Azure Durable Functions**: Best-in-class choices when workflows require durability, multi-day pauses for human approval, reliable timers, and resilient retry logic across server restarts.
- **Message queues (RabbitMQ, SQS, Kafka)**: Ideal for decoupling agent dispatch from worker execution pools.

The architectural decision is not which library to import, but where you draw the line between:
1. Deterministic control logic (state transitions, test validation, branch operations)
2. Probabilistic model decisions (analyzing errors, writing implementations)
3. Sandboxed tool execution (running bash, compiling code)
4. Durable persistence (saving execution state across failures)

For modest systems, fifty lines of clear state-machine logic in Python, Go, or C# are far easier to maintain and debug than a sprawling framework abstraction.

---

## Hosting Options for Custom Agents

A custom agent harness is simply a service, container, or background worker. It can be hosted on standard enterprise infrastructure:

### Azure
- **Azure Container Apps (ACA)**: Excellent for microservices, background event-driven workers, and scaling to zero when idle.
- **Azure Kubernetes Service (AKS)**: Best for complex, high-density runner setups with customized network policies and hardware requirements.
- **Azure Functions / Durable Functions**: Serverless event routing and durable, long-running workflow orchestration.
- **Microsoft Foundry Hosted Agents**: Managed lifecycle for custom agent code within the Azure ecosystem.

### AWS
- **AWS ECS (Fargate / EC2)**: Straightforward, highly reliable container hosting for harness services and isolated execution sandboxes.
- **AWS EKS**: Enterprise-scale container deployment with deep network and security controls.
- **AWS Lambda**: Cost-effective for lightweight, stateless webhook receivers and short-lived agent tasks (subject to the 15-minute execution limit).

### Google Cloud
- **Cloud Run**: Fast-scaling container platform suitable for both synchronous webhooks and asynchronous background jobs.
- **GKE**: Flexible Kubernetes environment for complex runner orchestration and custom node pools.

### Infrastructure Selection Criteria

Select your hosting target based on runtime needs:
- **Execution duration**: Does the agent finish in 30 seconds, or does it run full test suites for 45 minutes?
- **Filesystem persistence**: Does the harness need ephemeral throwaway disks, or fast, warm checkouts on persistent SSDs?
- **Network topology**: Does the agent need direct access to private corporate VPCs, internal package registries, or internal databases?
- **Sandbox requirements**: Can tools run directly in the worker container, or must they execute in an isolated microVM to prevent unsafe code execution?

---

## Self-Hosted Agents and Corporate Trust Boundaries

A self-hosted agent runs its orchestration harness and execution workers entirely inside infrastructure owned and operated by your organization:

```text
Corporate VPC / On-Premises
        |
        ├── orchestrator service
        ├── worker runner pool
        ├── internal repository access
        ├── private artifact feeds
        └── build & test sandboxes
                 |
                 v
             LLM API
```

This model gives you total governance over the execution environment:
- **Private networking**: Direct access to internal source control, documentation wikis, and staging databases without exposing them to the internet.
- **Secret protection**: Secrets and credentials stay within internal vault solutions (e.g., HashiCorp Vault, AWS Secrets Manager).
- **Environment parity**: Workers use the exact container images, toolchains, and operating systems used by internal development and CI teams.
- **Auditability**: Complete logging, telemetry, and network capture of all commands the agent attempts to run.

### The Inference Boundary Trap

Self-hosting the agent harness and execution workers **does not** mean the overall system is private. 

If your self-hosted agent calls an external LLM API (such as OpenAI, Anthropic, or Google), **your source code, test failures, schema definitions, and internal context still cross your network boundary**. 

The location of the agent harness determines where tools run. The location of the model inference determines where your data goes.

---

## Data Sovereignty and Inference Boundaries

For organizations handling proprietary source code, regulated customer data (HIPAA, PCI-DSS, GDPR), or classified systems, the model plane must be evaluated carefully.

> **The physical location of the model inference dictates your data trust boundary.**

There are three distinct operating levels for data sovereignty:

```text
Level 1: Self-Hosted Agent + External Model API
[ Enterprise Network: Harness + Repo + Sandboxes ] ──► (Public Internet) ──► [ Model Provider API ]
* Code stays local until read. Prompts, diffs, and context files exit your perimeter.

Level 2: Self-Hosted Stack on Dedicated Private Cloud Compute
[ Enterprise Network: Harness + Repo ] ──► Private Link / VNet ──► [ Dedicated GPU Instances (vLLM) ]
* Zero multi-tenant sharing. Traffic traverses private cloud backbones. Hardware is rented from cloud providers.

Level 3: Fully Air-Gapped / On-Premises Stack
[ Enterprise Datacenter: Harness + Repo + Execution Sandboxes + Bare-Metal GPU Nodes ]
* Fully isolated. No outbound internet connectivity. Complete hardware and weight ownership.
```

### Level 1: Self-Hosted Agent with External Inference APIs
The agent runs in your VPC, but sends context out to commercial inference APIs over TLS. 

This model is acceptable for many enterprises if they have enterprise zero-data-retention (ZDR) agreements and HIPAA/SOC2 compliance guarantees from the model vendor. However, it violates policies that strictly forbid source code from leaving internal corporate boundaries.

### Level 2: Self-Hosted Stack on Rented Private Cloud GPUs
You do not need to buy physical hardware to achieve inference privacy. You can rent dedicated GPU compute (e.g., Azure ND-series, AWS `p4`/`g5` instances, or specialized providers like CoreWeave and Lambda Labs) and deploy an open-weights inference engine (such as vLLM or TensorRT-LLM).

Key technical controls:
- Inference instances run in your own isolated VPC/VNet.
- Private endpoints (AWS PrivateLink, Azure Private Link) eliminate public internet transit.
- Egress gateways drop all outbound traffic to the public internet.
- Disk encryption uses customer-managed keys (CMK).
- Model weights (e.g., Llama 3, Qwen 2.5, DeepSeek-Coder) are downloaded once, cryptographically verified, and hosted in private object storage.

This architecture delivers strong data isolation without the massive capital expense and multi-month lead times of physical hardware procurement.

### Level 3: Fully Air-Gapped / On-Premises Deployment
The entire stack—repositories, orchestration, sandboxed execution, and bare-metal GPU clusters—runs inside physical enterprise datacenters with no external internet connection.

This pattern is required for defense, intelligence, critical national infrastructure, and high-security financial systems.

The trade-offs are significant:
- **Capital expense and lead time**: Procuring high-memory GPU servers (NVIDIA H100/H200, B200, or high-capacity unified memory workstations) is expensive and slow.
- **Operational maintenance**: Your infrastructure team owns GPU driver stability, CUDA patching, vLLM optimizations, model serving high availability, and capacity scaling.
- **Capability lag**: Top-tier proprietary models (such as Claude 3.7 Sonnet or OpenAI o3) are not available for on-prem weight deployment. While open models have closed the gap significantly for code generation, the most capable reasoning models often remain behind vendor APIs.

```text
Maximum Model Capability / Zero Ops
        │
        ▼
External Vendor APIs (Claude, OpenAI)
        │
        │ Increasing operational complexity
        │ Increasing data sovereignty
        ▼
Dedicated Private Cloud GPUs (vLLM in customer VPC)
        │
        ▼
Fully Air-Gapped Physical Hardware

Maximum Data Sovereignty / High Ops
```

---

## Hybrid Architectures

In a hybrid architecture, the orchestration plane lives in the cloud, while the execution workers run inside an internal network.

```text
Cloud Management Plane
  - Task scheduling
  - State persistence
  - Team dashboard
  - Model API coordination
         │
         │ Outbound-only secure tunnel / WebSocket
         ▼
Internal Network / VPC
  - Runner daemon (e.g., GitHub Actions Runner, GitLab Runner pattern)
  - Pristine Git clone
  - Internal compilers & build tools
  - Private database & internal API access
```

This model is familiar to platform engineers: it mirrors how GitHub Actions or GitLab CI operates. A cloud-hosted control plane coordinates tasks, but the actual compilation, testing, and secret evaluation happen on a self-hosted runner daemon behind the company firewall.

Benefits of hybrid designs:
- You avoid maintaining a custom web UI, database, and orchestration server on-premises.
- The internal runner initiates outbound connections to the control plane, requiring zero open inbound firewall ports.
- Sensitive source code and build artifacts remain inside the internal network, exposed only to internal toolchains.

---

## Coexistence of Local and Managed Agents

Treating local agents and managed cloud agents as an either/or choice is a false dichotomy. Healthy engineering organizations run both in parallel:

```text
Local Agent (The Inner Loop)
  - Interactive coding and feature prototyping
  - Fast, conversational debugging
  - Developer-driven refactoring on a dirty working tree
  - Instant tactile feedback

Managed Remote Agent (The Outer Loop)
  - Asynchronous, multi-hour background tasks
  - Automated PR reviews and linting triage
  - Large-scale dependency and framework upgrades across 50+ repos
  - Webhook-triggered CI failure auto-repair
  - Nightly security and technical debt remediation
```

An engineer can spend their afternoon writing a new microservice alongside an interactive local CLI agent, and before signing off for the day, trigger a managed cloud agent to upgrade API models and fix broken unit tests across three legacy repositories.

---

## Security, Sandboxing, and Permission Scoping

Running arbitrary agent-generated code on shared infrastructure requires defense-in-depth isolation:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        AGENT SECURITY ENCLOSURE                        │
├────────────────────────────────────────────────────────────────────────┤
│ 1. EPHEMERAL SANDBOXING: MicroVMs or isolated containers instantiated  │
│    per task and destroyed immediately upon completion.                 │
│ 2. NETWORK EGRESS FILTERING: Block outbound internet access except to  │
│    allowlisted package registries, source control, and model APIs.     │
│ 3. CREDENTIAL ISOLATION: Inject short-lived, scoped tokens (OIDC);     │
│    never store long-lived production secrets in agent environments.    │
│ 4. DISK PERSISTENCE ISOLATION: Prevent state contamination across      │
│    unrelated tasks by mounting pristine git checkouts.                 │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Ephemeral Sandboxing
Never execute untrusted agent commands directly on a shared, persistent host. Agents can make mistakes, download broken dependencies, or fall victim to prompt injection attacks embedded in third-party issues or documentation.
- Use isolated microVMs (e.g., AWS Firecracker, Fly.io machines) or hardened container runtimes (e.g., gVisor, Kata Containers).
- Treat execution environments as strictly disposable. Destroy the container or microVM immediately after the build, test, or patch completes.

### 2. Network Egress Filtering
Block outbound internet access from the execution environment by default:
- Allowlist specific source control domains (e.g., `github.com`), internal artifact repositories (e.g., Artifactory, internal NuGet/npm feeds), and inference endpoints.
- Drop all traffic directed toward cloud metadata services (`169.254.169.254`) to prevent malicious or accidental extraction of instance profile credentials.

### 3. Credential Scoping and RBAC
Shared agents must not operate under global administrative privileges. Slice capabilities based on the agent's role in the workflow:

- **Planner**: Read-only access to repository code, specs, and issue trackers. No write permissions to files or branches.
- **Implementer**: Read-write access strictly scoped to an ephemeral feature branch (`agent/issue-1234`). Ability to run builds and test suites. No rights to merge or publish artifacts.
- **Reviewer**: Read-only access to the diff, repository, and test logs. Permission to post comments and reviews on pull requests.
- **Release Agent**: Restricted permissions to trigger deployment pipelines, requiring explicit human multi-factor authentication (MFA).

Rely on short-lived OpenID Connect (OIDC) federated credentials rather than long-lived API tokens or SSH keys stored on disk.

### 4. Disk and State Isolation
Prevent contamination across tasks:
- Start every task from a clean, freshly cloned Git worktree.
- Never let an agent carry modified dependencies, temporary files, or environment overrides across to an unrelated task.

---

## Decision Guide: Selecting the Right Architecture

| Operational Requirement | Recommended Architecture |
| :--- | :--- |
| Interactive developer inner loop & pair programming | Local agent integrated with IDE or terminal CLI |
| Long-running, asynchronous, or overnight refactoring | Managed remote agent or self-hosted cloud worker |
| Automated PR review and CI failure triage | Managed or self-hosted agent triggered by webhooks |
| Source code must never leave corporate network | Self-hosted model inference on internal private infrastructure |
| Control inference without buying and managing physical GPUs | Self-hosted inference (vLLM) on rented private cloud GPU instances |
| Strict air-gapped compliance (defense, banking, critical infra) | Fully on-premises stack with bare-metal GPU clusters |
| Minimal operational overhead and fast time-to-market | Managed agent platform with enterprise vendor APIs |
| Complex, proprietary multi-stage engineering workflows | Custom state machine or Temporal workflow with modular model routing |
| Vendor portability across evolving model families | Custom harness decoupling the orchestration loop from model providers |

---

## Architectural Principles

1. **Decouple the three planes**: Treat inference, orchestration, and execution as separate infrastructure choices.
2. **Local for the inner loop**: Use local agents when real-time developer interaction, instant feedback, and low overhead matter most.
3. **Managed for team scale**: Use remote, managed infrastructure to turn agent workflows into consistent, audited team infrastructure.
4. **Decouple the agent from the workstation**: Move long-running, asynchronous, and scheduled tasks off personal laptops and onto cloud runners.
5. **Enforce workflow determinism in code**: Use state machines, typed schemas, and real tool outputs to govern lifecycle transitions. Keep LLMs focused on the probabilistic tasks that require judgment.
6. **Self-hosting the harness is not self-hosting the model**: If you call an external model API from inside your VPC, your prompts and source code still leave your network perimeter.
7. **Inference location governs data sovereignty**: If corporate policy forbids code from leaving your boundary, you must control the inference server, not just the agent harness.
8. **Leverage private cloud GPUs**: Renting dedicated GPU compute within your private cloud VPC provides data isolation without the overhead of physical datacenter procurement.
9. **Coexistence over monoculture**: Pair interactive local agents for daytime feature work with managed remote agents for overnight and event-driven automation.
10. **Sandbox execution rigorously**: Run agent-generated bash and code inside ephemeral, network-filtered, and disposable execution environments.

---

## Related Notes

- [[Agentic Coding Harness and Controlled Development Workflows]] — Architectural patterns for state-machine-driven execution loops and validation gates.
- [[Model Access and Execution Infrastructure]] — Gateway design, connection pooling, and latency optimization for inference traffic.
- [[Dynamic Model Routing and Inference Gateways]] — Decoupling application logic from concrete model providers via smart proxies.
- [[Local vs Cloud and Hybrid Model Execution]] — Evaluating TCO, thermal characteristics, and throughput across local hardware and cloud clusters.
- [[Always-On Autonomous Agents - The 24-7 Local Operating System]] — Architecture, security boundaries, and persistence models for local daemons.
- [[Multi-Agent Software Development]] — Designing specialized agent teams that collaborate across architectural boundaries.
- [[AI Productivity Is Limited by the Delivery System]] — Why raw model output speed is bottlenecked by CI, review pipelines, and verification steps.
