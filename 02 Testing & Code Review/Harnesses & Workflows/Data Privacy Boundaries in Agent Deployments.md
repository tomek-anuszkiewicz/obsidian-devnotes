---
title: "Data Privacy Boundaries in Agent Deployments"
tags:
  - ai-agents
  - privacy
  - security
  - deployment
  - data-governance
aliases:
  - "Agent Hosting and Data Disclosure Boundaries"
  - "Private and Hybrid Agent Execution"
  - "Separating Model Location from Agent Authority"
---

A company hosts an agent on its own machine and allows it to call a cloud model. The shell may stay inside the private network while repository excerpts, logs, or test failures leave it in model requests. A private execution location has not established a private inference path.

Trace the components separately: the user's interface, orchestrator, worker, tools, model endpoint, and stores retaining task state. Identify what context each receives and what credentials allow it to do. An isolated worker with a production login can still have production authority; a remote interface can control a restricted private workspace.

The scenarios below distinguish self-hosted execution, private inference, and fully isolated deployment, then connect those choices to permissions and interactive work. [[Agent Deployment and Execution Models]] provides the broader deployment comparison. [[Building and Hosting Agent Execution Services]] develops the service and environment that enforce the chosen boundaries.

## Data sovereignty and fully private agents

For organizations with strict confidentiality requirements, the privacy boundary must be analyzed separately from the agent deployment boundary.

A useful rule is:

> **The location of the agent does not determine the privacy boundary. The location of model inference does.**

That boundary also depends on what data enters the model request. [[Agent-Assisted Sensitive Data Exposure Audits]] traces sensitive fields through APIs, logs, and stores before an agent or gateway uses them.

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

Review the context actually transmitted and retained, the credentials available to the running process, and the operations permitted at each boundary. Use those facts to assess privacy and authority rather than inferring them from the location of the agent interface.

## Related Notes

- [[Agent Deployment and Execution Models]] — The location and ownership of the model, agent loop, and executor.
- [[Building and Hosting Agent Execution Services]] — The runtime and hosting responsibilities of an execution service.
- [[Isolated Engineering Environments for Coding Agents]] — Operating-system, identity, and network controls for broad engineering capabilities.
