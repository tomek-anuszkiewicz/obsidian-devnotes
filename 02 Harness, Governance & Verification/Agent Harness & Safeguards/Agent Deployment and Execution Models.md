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

> [!IMPORTANT]
> **The 3-Plane Decoupling Axiom**: The place where an agent reasons, the place where its workflow is coordinated, and the place where code executes are **three orthogonal architectural planes**:
> 1. **Model Plane (Inference)**: Where the weights reside and token completion occurs (Provider Cloud vs. Dedicated Cloud GPU vs. Self-Hosted On-Premises).
> 2. **Orchestrator Plane (Harness & State)**: Where the agent loop, context compaction, and state machines reside (Local CLI vs. Centralized Workflow Engine).
> 3. **Executor Plane (Environment)**: Where filesystem mutations, Git commits, terminal commands, builds, and test oracles execute (Developer Workstation vs. Isolated Cloud Sandbox / Container).
> Conflating these three planes creates severe security, latency, and data-sovereignty bottlenecks.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     THE 3-PLANE AGENT TOPOLOGY                         │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   [ MODEL PLANE ]       [ ORCHESTRATOR PLANE ]     [ EXECUTOR PLANE ]  │
│   Inference Engine      Harness & Workflow         Filesystem & Tools  │
│   - External API        - Local CLI Loop           - Developer Laptop  │
│   - Private Cloud GPU   - Team Workflow Service    - Ephemeral Sandbox │
│   - On-Premises Cluster - CI Event Trigger         - Isolated CI Runner│
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Executive Summary & Core Architectural Invariants

1. **Orthogonal Deployment Topologies**:
   - **Local Agent**: Orchestrator and Executor run on the developer workstation; Model runs via remote API. Ideal for interactive pair programming and exploratory debugging.
   - **Managed Remote Agent**: Orchestrator and Executor run in isolated vendor cloud environments. Enables unattended, asynchronous, and scheduled maintenance workflows.
   - **Self-Hosted Enterprise Agent**: Orchestrator and Executor run inside corporate VPCs with private network access to internal codebases, databases, and issue trackers.
   - **Hybrid Agent**: Cloud orchestrator dispatches tasks to private on-premises executors, keeping source code and credentials inside internal trust boundaries.
2. **Data Sovereignty is Determined by the Model Plane**: Self-hosting the agent harness does not guarantee data privacy if prompts and code snippets are dispatched to an external multi-tenant LLM. Strict data-sovereignty mandates self-hosting both the executor and model inference.
3. **Role-Based Least Privilege Gating**: Shared team agents must not possess global admin rights. Enforce strict capability boundaries: Planners (Read-Only access to specs/code), Implementers (Write access restricted to ephemeral feature branches), and Reviewers (Read-only access with test execution permissions).
4. **Coexistence Over Monoculture**: High-performing organizations do not enforce a single deployment model. Developers use local interactive agents for tight inner loops, while managed remote agents execute overnight refactorings, automated dependency updates, and continuous PR reviews.

---

## 1. The 3-Plane Architectural Decomposition

The decoupling of reasoning from physical execution enables modular infrastructure configurations:

```text
Config A: Local Interactive (Inner Loop)
[ Laptop: Harness + Git + Tools + Compiler ] ──► HTTPS ──► [ Model Provider Cloud ]

Config B: Team Managed Service (Unattended / CI)
[ Event / Webhook ] ──► [ Cloud Orchestrator ] ──► [ Ephemeral Container Sandbox ]
                               │                               │
                               ▼                               ▼
                     [ Provider Model API ]         [ Private Git Repository ]

Config C: Air-Gapped / High-Sovereignty
[ Private VPC: Team Orchestrator ] ──► [ On-Prem Execution Worker ] ──► [ Local vLLM Cluster ]
```

---

## 2. Comparative Matrix: Deployment Models

| Dimension | Local Agent | Managed Remote Agent | Self-Hosted Agent | Hybrid Agent |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Use Case** | Interactive coding, rapid debugging | Unattended tasks, overnight PRs | Internal VPC codebases, strict compliance | Cloud orchestration of private runners |
| **Workstation Dependency** | High (machine must remain awake) | None (runs asynchronously in cloud) | None (runs in private cluster) | None (executes on internal pool) |
| **Setup Overhead** | Low (CLI install) | Minimal (SaaS onboarding) | High (Kubernetes, runners, monitoring) | Moderate (agent runner daemon) |
| **Network Locality** | Workstation LAN | Cloud vendor network | Corporate intranet / private mesh | Boundary crossing via secure tunnel |
| **Trust Boundary** | Local machine | Vendor infrastructure | Enterprise VPC perimeter | Split perimeter |
| **Resource Constraints** | Laptop CPU/RAM | Elastic cloud instances | Cluster capacity | Worker pool capacity |

---

## 3. Security, Sandboxing, and Permission Scoping

Deploying agents to cloud infrastructure requires defense-in-depth isolation:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        AGENT SECURITY ENCLOSURE                        │
├────────────────────────────────────────────────────────────────────────┤
│ 1. EPHEMERAL SANDBOXING: MicroVMs (Firecracker) or isolated containers │
│    instantiated per task and destroyed immediately upon completion.    │
│ 2. NETWORK EGRESS FILTERING: Block outbound internet access except to  │
│    whitelisted package registries, source control, and model APIs.     │
│ 3. CREDENTIAL ISOLATION: Inject short-lived, scoped tokens (OIDC);     │
│    never store long-lived production secrets in agent environments.    │
│ 4. DISK PERSISTENCE ISOLATION: Prevent state contamination across      │
│    unrelated tasks by mounting pristine git checkouts.                 │
└────────────────────────────────────────────────────────────────────────┘
```

By isolating the executor into disposable execution sandboxes, enterprises unlock autonomous, long-running agent workflows without exposing corporate networks to supply-chain or prompt-injection vulnerabilities.

---

## Relationship to the Knowledge Graph

- **[[Agentic Coding Harness and Controlled Development Workflows]]**: The control harness executing on top of local or cloud deployment models.
- **[[Model Access and Execution Infrastructure]]**: Gateway patterns, routing, latency, and quota orchestration for deployed coding agents.
- **[[Multi-Agent Software Development]]**: Multi-agent team orchestration running across distributed execution nodes.
- **[[Introduction to Workflow Orchestration]]**: Orchestrating long-running, asynchronous agent tasks across infrastructure.
- **[[Exploring Agent Harnesses]]**: Detailed comparison of execution environments and agent harness platforms.
- **[[AI Productivity Is Limited by the Delivery System]]**: Why remote agent scalability is bounded by CI/CD deployment pipelines.
