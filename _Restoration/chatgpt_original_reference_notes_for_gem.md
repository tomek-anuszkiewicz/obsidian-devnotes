# Reference Style Baseline: Original Ground-Truth Engineering Notes

This document contains 9 original, uncorrupted reference notes written from the perspective of a Senior Technical Lead / Principal Architect. 

## Purpose for the AI Model / Custom Gem
Use these notes as the **gold standard style and tone reference** (few-shot context). When rewriting, restoring, or creating new architectural notes, strictly mirror the voice, structure, and communication traits demonstrated in these documents:

1. **Voice & Stance**:
   - Calm, conversational, authoritative, and deeply practical.
   - Sounds like a senior engineer explaining real-world systems over coffee or at an internal tech talk.
   - Zero sensationalist hooks, zero purple prose, zero manufactured drama, and zero academic fluff.
2. **Technical Depth & Grounding**:
   - Rich in concrete domain scenarios, real code mechanisms, and negative knowledge (what fails, what not to do).
   - Nuanced exploration of trade-offs and edge cases rather than rigid dogmatic rules.
3. **Structure & Visuals**:
   - Clean, organic headings matched to the problem.
   - Minimalist, functional data-flow diagrams rather than shouting ASCII decorative banners.

---

# Reference Note: Agent Deployment and Execution Models

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

---

# Reference Note: Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize

---
title: Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize
tags:
  - ai-agents
  - code-review
  - software-engineering
  - quality-assurance
  - static-analysis
  - compliance
  - review
aliases:
  - Natural-Language Rules as Executable Policies
  - Agentic Review Rules
  - Semantic Code Review
---

Traditional software quality automation works best when a rule can be expressed precisely.

For example:

```text
Domain must not reference Infrastructure.
Every public endpoint must require authorization.
Result must never be negative.
All handlers must implement a particular interface.
```

Such rules can be encoded as:

- unit tests;
    
- architecture tests;
    
- static analyzers;
    
- compiler rules;
    
- type-system constraints;
    
- linters;
    
- CI checks.
    

This remains extremely valuable.

However, a large part of software engineering has never fit comfortably into this model.

Many important rules are not difficult because developers do not understand them.

They are difficult because they are expensive or nearly impossible to formalize.

LLM-based review agents may automate part of this previously human-only layer.

---

## Many Real Engineering Rules Are Semantic

#coding_standard

Consider rules such as:

> Do not introduce an abstraction unless it represents a meaningful boundary.

Or:

> Controllers should remain thin, but trivial request mapping does not need another service layer.

Or:

> Modules should communicate through their public contracts rather than reaching into each other's internals.

Or:

> Do not introduce a generic framework for a problem that exists only once.

Or:

> Business rules should remain visible in the domain code rather than being hidden inside infrastructure helpers.

These are meaningful architectural principles.

An experienced engineer can often recognize their violation immediately.

But encoding them as a deterministic test may require an enormous amount of machinery.

The problem is not lack of rules.

The problem is that the rules depend on:

- intent;
    
- context;
    
- naming;
    
- surrounding architecture;
    
- business meaning;
    
- exceptions;
    
- trade-offs;
    
- degree rather than binary classification.
    

Historically, this meant that enforcement depended on human attention.

---

## Human Attention Was the Missing Runtime

#review 

Architecture documents frequently contain sentences like:

```text
Prefer explicit dependencies.

Avoid leaking persistence concerns into the domain.

Do not create abstractions prematurely.

Cross-module access should happen through defined boundaries.
```

These rules may be well understood by the team.

But nothing actually executes them.

Their enforcement mechanism is approximately:

```text
developer remembers the rule
        +
reviewer remembers the rule
        +
reviewer notices the violation
```

This is fragile.

Even excellent reviewers:

- get tired;
    
- skim large changes;
    
- forget some guidelines;
    
- focus on the most obvious problem;
    
- have limited time;
    
- do not inspect every pull request with identical depth.
    

A review agent changes this because it can repeatedly interpret the same rule against every relevant change.

The document can become part of an active quality system rather than passive documentation.

---

# Natural-Language Rules Can Become Executable Policies

#coding_standard

Suppose a repository contains:

```text
docs/architecture/principles.md
docs/domain/invariants.md
docs/security/guidelines.md
docs/performance/guidelines.md
ADRs/
```

An architecture reviewer can receive these documents as part of its instructions.

For every pull request it can ask:

```text
Does this change violate any architectural principle?

If so:

- identify the concrete code;
- identify the relevant principle;
- explain why the rule applies;
- consider documented exceptions;
- estimate confidence;
- avoid commenting if evidence is weak.
```

This is not executable specification in the traditional deterministic sense.

It is closer to:

> natural-language executable policy.

The important change is that a rule no longer needs to be translated completely into code before it can be checked automatically.

---

## This Expands the Automatable Region of Engineering

Previously there were roughly two categories:

```text
Formalizable rule
    -> automation

Non-formalizable rule
    -> human review
```

Agents introduce a third layer:

```text
Formalizable rule
    -> deterministic automation

Semantically interpretable rule
    -> agentic verification

Ambiguous strategic decision
    -> human judgment
```

This potentially moves a large amount of work out of the purely human-review category.

Examples include checking whether:

- a new abstraction is justified;
    
- responsibilities remain in the correct module;
    
- domain logic is becoming infrastructure-dependent;
    
- error handling matches surrounding conventions;
    
- a change duplicates an existing capability;
    
- a public API behaves consistently with related APIs;
    
- a workaround violates an architectural direction;
    
- a class has accumulated too many unrelated responsibilities;
    
- a supposedly generic component is actually coupled to one use case.
    

These are exactly the kinds of things senior engineers traditionally catch during review.

---

# Agents Are Particularly Useful Because They Are Relentless

The advantage is not only that an LLM can understand such rules.

It can apply them every time.

A human may know twenty architectural principles perfectly but consciously evaluate only a subset during a particular review.

An agent can inspect every relevant PR against all twenty.

It does not care that:

- the change is repetitive;
    
- the pull request contains 100 files;
    
- this is the fiftieth review this week;
    
- the rule rarely catches anything;
    
- the same check has failed to find a problem for six months.
    

This makes agents particularly suitable for rules that are individually important but rarely violated.

Humans are bad at maintaining attention for checks that almost always produce:

```text
nothing wrong
```

Machines are excellent at it.

---

# But Agents Must Also Handle Formalizable Rules Well

There is an important danger in dividing the world too aggressively into:

```text
tests handle simple rules

LLMs handle difficult rules
```

An effective reviewer must still understand the rules that could have been expressed as deterministic tests.

For example:

```text
A price must never be negative.
```

Even if there is already a unit test for this invariant, an agent reviewing related code should understand that violating it is wrong.

Otherwise the agent has an incomplete model of the system.

The distinction should therefore not be:

> deterministic rules belong to tests and should be invisible to the agent.

Instead:

> deterministic tools are the authoritative verification mechanism, while the agent should also understand their meaning.

The agent should be capable of reasoning:

```text
This change appears capable of creating a negative price.

There is an invariant that prices cannot be negative.

I should inspect or run the relevant tests.
```

Then the deterministic test provides the strongest evidence.

---

## Formal Rules Should Usually Remain Deterministic

If something can be verified cheaply and precisely:

```text
Assert.True(result >= 0);
```

there is little benefit in replacing it with:

```text
Ask an LLM whether result >= 0 appears to hold.
```

The deterministic version is:

- cheaper;
    
- faster;
    
- reproducible;
    
- precise;
    
- easy to debug;
    
- independent of model behavior.
    

Agents should therefore usually sit above these mechanisms rather than replacing them.

A useful principle is:

> Formalize what is cheap to formalize. Use agents where formalization becomes disproportionately expensive.

---

# The Agent Can Connect Formal and Informal Rules

The interesting capability appears when an agent understands both.

Suppose an architecture document says:

> Module A must not depend on Module B's persistence model.

There may also be a deterministic architecture test forbidding direct references between certain namespaces.

The agent can detect a subtler case:

```text
There is no forbidden assembly reference.

However, Module A now copies the exact internal database representation
of Module B and depends on its persistence semantics.
```

The formal test passes.

The architectural intent may still be violated.

The agent operates one level above syntax.

Likewise:

```text
Unit test:
Price cannot be negative.
```

may pass.

But the reviewer may notice:

```text
The implementation clamps negative prices to zero,
which preserves the technical invariant but silently hides
an invalid business state.
```

A deterministic test sees compliance.

A semantic reviewer can question whether the implementation satisfies the underlying intent.

This interaction is potentially much more powerful than either approach alone.

---

# Agents Can Escalate Rules Into Deterministic Tests

Agentic review can also help discover which informal rules should eventually become formal.

Imagine an agent repeatedly finds the same problem:

```text
Five pull requests introduced direct dependencies
from Domain to Infrastructure.
```

At that point the correct response may be:

> Stop asking the LLM to rediscover this every time.

Turn the rule into an architecture test.

The process becomes:

```text
informal principle
        |
agent repeatedly checks it
        |
pattern becomes stable
        |
rule can be formalized
        |
architecture test / analyzer added
```

This gives a useful migration path.

Agents can act as the exploratory layer from which deterministic rules emerge.

---

# The Reverse Is Also Useful

A deterministic check may reveal a violation without explaining its architectural significance very well.

For example:

```text
Architecture test failed:
Namespace X references namespace Y.
```

The agent can add context:

```text
This is prohibited because Y contains persistence-specific models.

The new reference causes the pricing module to depend on the current
database representation of customer data.

The intended integration point is CustomerContract.
```

The machine-verifiable test gives certainty.

The agent gives interpretation.

That combination can make automated checks much easier for developers to understand and fix.

---

# Some Tests May Become Ephemeral

Agents also make it possible to distinguish between permanent tests and tests created only for investigation.

Today a test usually means:

```text
write test
commit test
maintain test forever
```

An agent can instead generate a test to investigate a particular hypothesis.

For example:

```text
I suspect this cache fails when two requests initialize it concurrently.
```

The agent creates a temporary concurrency test, runs it repeatedly, and discovers the race.

The experiment itself does not necessarily need to remain in the repository.

If the discovered behavior represents an important regression risk, the test can then be promoted:

```text
agent-generated experiment
        |
bug reproduced
        |
important invariant discovered
        |
promote test
        |
permanent regression test
```

This separates:

```text
tests as permanent specification
```

from:

```text
tests as investigative instruments
```

Agents can make heavy use of the second category.

---

# Architecture Review May Become Continuous

The same idea applies especially well to architecture.

Today architecture is often enforced through a mixture of:

```text
architecture documents
ADRs
review culture
senior engineers
occasional architecture tests
```

With agents, every pull request can undergo an architecture review.

The reviewer can ask:

```text
Did this change create a new dependency direction?

Did an internal concept leak through a module boundary?

Was an abstraction introduced?

If so, does it have a meaningful reason to exist?

Does this change contradict an ADR?

Does it make a future migration significantly harder?

Is business logic moving into infrastructure code?

Does the new code follow the architecture or merely satisfy its syntax?
```

Most of these questions would be extraordinarily difficult to encode in conventional analyzers.

They are much closer to questions asked by an experienced architect.

---

# The Ideal System Uses Both Forms of Verification

The future quality stack may therefore look something like:

```text
              Human judgment
                    ▲
                    |
          Semantic agent review
                    |
       architecture / intent /
       context / trade-offs
                    ▲
                    |
        Deterministic verification
                    |
      tests / types / analyzers /
       linters / security tools
```

The layers complement each other.

Deterministic verification provides certainty where precise formalization is practical.

Agents extend automation into areas where semantic judgment is required.

Humans remain responsible for decisions where even the correct rule depends on business priorities, risk tolerance, or competing architectural goals.

---

# The Goal Is Not to Replace Rules With Prompts

A tempting mistake would be to conclude:

> If an LLM can inspect the code, we no longer need architecture tests, analyzers, or unit tests.

That would discard one of software engineering's strongest properties: deterministic verification.

A better model is:

```text
If a rule can cheaply become code:
    encode it.

If a rule is difficult to encode but understandable:
    let an agent enforce it.

If an agent repeatedly finds the same formalizable violation:
    consider turning it into code.

If the correct answer depends on strategic judgment:
    escalate it to a human.
```

This creates a continuum rather than a replacement.

---

# Review Agents Turn Human Attention Into a Scalable Resource

Historically, many engineering standards were enforced simply because experienced developers watched for them.

That created an unavoidable constraint:

```text
quality of enforcement
≈
available senior engineering attention
```

Agents weaken this dependency.

A senior engineer may define a principle once:

> Do not hide business decisions behind generic infrastructure abstractions.

Instead of expecting every reviewer to remember and enforce it forever, the principle can become part of an agent's permanent review instructions.

The human provides the judgment once.

The agent applies it thousands of times.

That may be one of the most important consequences of agentic code review:

> knowledge that previously existed only as human review intuition can become continuously executable organizational policy.

The strongest future systems will probably combine two capabilities:

> machines must be extremely reliable at rules that can be formalized, while also extending verification into rules that previously required human interpretation.

The first preserves the precision of traditional software engineering.

The second expands its reach.

---

# Reference Note: Comments May Become More Valuable in AI-Generated Code

---
title: Comments May Become More Valuable in AI-Generated Code
tags:
  - ai-agents
  - software-engineering
  - documentation
  - code-review
  - maintainability
  - intent-specification
aliases:
  - Code Comments in AI Era
  - Semantic Value of Comments in AI Code
---

The traditional rule for comments is often expressed as:

> Good code should explain what it does. Comments should explain why.

This distinction may become even more important in software increasingly written and modified by AI agents.

An agent can usually reconstruct the mechanics of code very well. It does not need comments that merely repeat the implementation.

For example:

```csharp
// Charge 50% if booking starts in less than 3 days.
if (booking.StartDate < DateTime.UtcNow.AddDays(3))
{
    cancellationFee = booking.TotalPrice * 0.5m;
}
```

The comment adds almost no information.

A much more valuable comment would be:

```csharp
// Cancellations within 72 hours are charged 50% because the supplier
// no longer refunds us after this point.
// Do not replace this with the standard hotel cancellation policy.
```

The code explains the mechanism.

The comment preserves information that cannot easily be reconstructed from the implementation:

- why the rule exists;
    
- where it comes from;
    
- whether it is intentional;
    
- which business constraint it represents;
    
- what apparently reasonable changes would be incorrect.
    

## Code Is Self-Documenting Syntactically, Not Semantically

Well-written code can communicate structure and behavior.

For example:

```csharp
ApplyNonRefundableSupplierCancellationFee();
```

This is much better than an obscure method name, but it still does not explain:

- why this supplier is treated differently;
    
- whether the behavior comes from a contract;
    
- whether it is temporary;
    
- which products it applies to;
    
- whether another similar rule should be reused;
    
- what assumptions the implementation depends on.
    

Historically, much of this knowledge lived outside the code:

- in developers' heads;
    
- Jira tickets;
    
- Slack conversations;
    
- meetings;
    
- old specifications;
    
- architecture documents.
    

Future agents modifying the code may never see any of those sources.

A comment located next to the implementation has a major advantage:

> It is very likely to enter the agent's context whenever the relevant code enters the context.

## Comments Can Act as Local Context Retrieval

Suppose an agent receives a task:

> Add partial cancellation support.

It retrieves the classes responsible for cancellations.

Any comments located inside those classes are naturally retrieved together with the implementation.

This makes comments a kind of very small, highly localized knowledge base.

They do not require the agent to know:

- that an ADR exists;
    
- which specification describes the rule;
    
- which ticket introduced it;
    
- what search query to use;
    
- which meeting contained the relevant discussion.
    

The knowledge is physically attached to the place where it matters.

This may make carefully written comments one of the most reliable forms of context delivery for future coding agents.

## Documentation Layers Still Have Different Roles

Comments should not replace specifications or architectural documentation.

Instead, the different layers can complement each other:

```text
Specification
    ↓
describes desired behavior and requirements

Architecture docs / ADRs
    ↓
describe system-wide decisions and trade-offs

Business comments
    ↓
preserve local intent, constraints and exceptions

Code
    ↓
contains the executable implementation
```

During the initial implementation, an agent may have access to the complete specification.

Several years later, another agent may receive only a small portion of the repository while working on an unrelated change.

The original specification may not enter its context at all.

A nearby comment probably will.

## Negative Knowledge May Be Especially Valuable

Some of the most useful comments may describe what must **not** be done.

For example:

```csharp
// Do not calculate this from Payment.Amount.
// Legacy bookings may already contain the agency margin there.
```

Or:

```csharp
// This check looks redundant, but some suppliers occasionally send
// the same reservation with different external IDs.
```

Or:

```csharp
// Intentionally executed before availability validation.
// Sales requires the original quoted price to remain available
// even when availability subsequently fails.
```

This is negative knowledge:

> A seemingly obvious implementation or refactoring is incorrect.

Such knowledge may be particularly important for agents.

An agent performing a local refactoring may see:

```text
strange condition
→ appears redundant
→ simplify it
```

A good comment changes the reasoning to:

```text
strange condition
→ explicitly intentional
→ represents a business constraint
→ preserve unless the requirement itself changes
```

## Clean Code Does Not Eliminate Business Context

The argument that "good code should not require comments" is reasonable when applied to comments describing mechanics.

Comments such as:

```csharp
// Iterate through users.
```

are usually unnecessary.

But business rationale cannot always be encoded through better naming or cleaner abstractions.

A method called:

```csharp
IsEligibleForLegacyCancellationCompensation()
```

still does not explain why legacy cancellation compensation exists.

The useful distinction may therefore become:

> Minimize comments explaining implementation.

> Maximize comments preserving intent, business meaning, invariants, constraints, exceptions and non-obvious decisions.

## Agents Can Produce Their Own Future Context

There is another important consequence.

When an agent implements a feature, it already has the specification in its context.

Instead of converting that specification only into executable code, it can also preserve the parts of the specification that future developers or agents will need.

A useful instruction could be:

> Whenever the implementation encodes a non-obvious business rule, invariant, exception or constraint that cannot be reconstructed from the code itself, preserve that information as a concise comment near the relevant code.

The process then becomes:

```text
task specification
       │
       ▼
     agent
    /     \
   ▼       ▼
code     durable intent
         comments
```

The code is the executable result of the specification.

The comments preserve selected parts of its semantics.

## Comments May Become Part of Designing Code for Agents

Traditionally, comments were primarily written for human maintainers.

In agent-heavy development, another audience appears:

> the future model receiving a limited slice of the repository as context.

This changes how comments can be evaluated.

The question is no longer only:

> Will another developer understand this?

It also becomes:

> If an agent sees only this file two years from now, what important information could it incorrectly infer?

Comments can protect against those incorrect inferences.

This suggests that codebases optimized for agentic development may intentionally preserve more business context next to the implementation.

Not more comments in general.

Better comments.

Especially comments explaining:

- why a rule exists;
    
- which business concept it represents;
    
- which invariant must remain true;
    
- why an unusual implementation is intentional;
    
- which tempting simplification would be wrong;
    
- which external constraint shaped the implementation;
    
- which assumptions future changes must preserve.
    

In this sense, comments may become part of **context engineering for future coding agents** rather than merely an aid to human readability.

## Redefining Low-Level and Architectural Documentation

The ability of LLMs to analyze code and explain its mechanics on demand accelerates two major shifts:

1. **Obsolescence of Low-Level Comments and Descriptive Docs:**
   - Comments explaining *how* a function works or what steps it takes are now pure noise.
   - Broad architectural documentation that merely describes component relationships or data flows is easily reconstructed on the fly by an agent analyzing the codebase.

2. **From Structural Documentation to Decision Records:**
   - Documentation shifts almost entirely from *descriptive* (what exists) to *decisional* (why it was built this way).
   - High-level architecture docs remain valuable only as **guardrails and trade-offs** (e.g., ADRs, system constraints, performance budgets) that prevent agents from making architectural refactorings that break unstated non-functional requirements.

---

# Reference Note: Designing APIs for LLM-Generated Integration Code

---
title: Designing APIs for LLM-Generated Integration Code
tags:
  - api-design
  - ai-agents
  - software-architecture
  - integration
  - developer-experience
  - documentation
aliases:
  - Agent-Friendly API Design
  - APIs for LLM Integrations
---

## Goal

When using an LLM coding agent, the goal is not necessarily for the agent to call an API directly.

Instead, the agent should be able to:

1. understand the requested business operation,
    
2. discover which external API capability provides it,
    
3. find the correct generated client,
    
4. choose the correct client method,
    
5. generate application code that uses that method correctly.
    

A useful mental model is:

```text
Business requirement
        ↓
Discover business capability
        ↓
Find appropriate client
        ↓
Find appropriate operation
        ↓
Generate application code
        ↓
Generated client
        ↓
REST API
```

## Internal vs External APIs

It is useful to distinguish between internal and external APIs.

### Internal APIs

Internal APIs may:

- reflect internal service architecture,
    
- expose implementation-specific concepts,
    
- use internal data representations,
    
- change relatively freely,
    
- depend on concepts already understood inside the system.
    

### External APIs

External APIs should:

- provide stable contracts,
    
- avoid leaking internal implementation details,
    
- expose business concepts rather than internal mechanics,
    
- remain compatible over time,
    
- use terminology meaningful to consumers.
    

This distinction becomes even more important for LLM-generated code.

The easier it is to understand the business meaning of an operation, the easier it is for an agent to select it correctly.

---

## OpenAPI as the Source of Truth

For REST APIs, OpenAPI should describe not only the HTTP contract, but also the semantics of the operation.

A weak specification:

```yaml
/users/{id}/sessions:
  delete:
    operationId: deleteSessions
```

A better specification:

```yaml
/users/{userId}/sessions:
  delete:
    operationId: revokeUserSessions
    summary: Revoke all active sessions for a user
    description: |
      Revokes all active authentication sessions belonging
      to the specified user.

      Use this operation when access for the user must be
      immediately invalidated.

      This operation does not delete the user account.
```

The description should answer questions such as:

- What does this operation do?
    
- When should it be used?
    
- When should it not be used?
    
- What are the preconditions?
    
- What side effects does it have?
    
- What are the important failure modes?
    

Negative guidance can be especially useful.

For example:

```yaml
description: |
  Permanently deletes a draft invoice.

  Only draft invoices can be deleted.

  Do not use this operation for issued invoices.
  Issued invoices must be cancelled using cancelInvoice.
```

This helps the agent choose the correct business operation rather than matching only on words such as "delete".

---

## Prefer Business-Oriented Operations

Operations should clearly express intent.

Prefer:

```text
cancelInvoice
revokeUserSessions
reserveInventory
approveOrder
```

over vague operations such as:

```text
updateEntity
executeAction
changeStatus
processRequest
```

CRUD operations are perfectly fine when the business operation really is CRUD.

For example:

```http
DELETE /drafts/{id}
```

is appropriate if the object is actually deleted.

But a business operation such as cancelling an issued invoice should probably be represented explicitly:

```http
POST /invoices/{id}/cancel
```

rather than pretending that cancellation is equivalent to deletion.

The important principle is:

> The API should expose business capabilities, not merely database mutations.

---

## Generate Strongly Typed Clients

The coding agent should normally not construct HTTP requests manually.

Instead of generating:

```csharp
await httpClient.DeleteAsync(
    $"/users/{userId}/sessions");
```

prefer a generated typed client:

```csharp
await identityClient.RevokeUserSessionsAsync(
    userId,
    cancellationToken);
```

The client can be generated from OpenAPI using tools such as:

- Kiota,
    
- NSwag,
    
- OpenAPI Generator.
    

The flow becomes:

```text
OpenAPI
   ↓
Client generator
   ↓
Strongly typed client
   ↓
LLM-generated application code
```

This significantly reduces the space in which the agent can make mistakes.

It no longer needs to reconstruct:

- the URL,
    
- HTTP method,
    
- serialization format,
    
- request schema,
    
- response schema,
    
- query parameter names.
    

Instead, it chooses a typed method.

---

## Preserve Documentation in Generated Clients

Ideally, descriptions from OpenAPI should become XML documentation or equivalent comments in the generated client.

For example:

```csharp
public interface IInvoicesClient
{
    /// <summary>
    /// Cancels an issued invoice while preserving it for audit.
    /// Do not use for draft invoices.
    /// </summary>
    Task CancelInvoiceAsync(
        Guid id,
        CancellationToken cancellationToken);

    /// <summary>
    /// Permanently deletes a draft invoice.
    /// Issued invoices cannot be deleted.
    /// </summary>
    Task DeleteDraftInvoiceAsync(
        Guid id,
        CancellationToken cancellationToken);
}
```

This is particularly useful for coding agents because the most relevant semantic information is available directly next to the methods they are expected to use.

If the generated client loses all API descriptions, much of the semantic value of OpenAPI is lost.

---

## Client Discoverability

Having good generated clients is not enough.

The agent must also be able to discover which client provides a given capability.

Prefer domain-oriented names:

```text
IIdentityClient
IOrdersClient
IBillingClient
IInvoicesClient
```

instead of implementation-oriented names:

```text
IServiceAClient
IBackendClient
IApiV2Client
```

Likewise, operation names should expose intent clearly:

```text
RevokeUserSessionsAsync
CancelInvoiceAsync
ReserveInventoryAsync
```

This allows a coding agent to search the repository by business concepts.

Example reasoning:

```text
Requirement:
"When an employee is disabled, invalidate all login sessions."

↓ search for:
session
revoke session
identity

↓ find:
IIdentityClient

↓ inspect methods:
RevokeUserSessionsAsync

↓ generate:
await identityClient.RevokeUserSessionsAsync(...)
```

The repository itself becomes a semantic index of available capabilities.

---

## Repository Guidance for Agents

The agent should be explicitly told how external integrations are organized.

For example, an `AGENTS.md`, repository instruction, or coding skill may contain:

```text
When integrating with another service:

1. Search existing generated clients by business concept.
2. Inspect method names and documentation.
3. Prefer generated clients over direct HTTP calls.
4. If the correct operation is unclear, inspect the source OpenAPI specification.
5. Do not invent endpoint URLs or construct REST requests manually when a generated client exists.
```

The instruction tells the agent **how to discover and use capabilities**.

The OpenAPI specification tells it **which capabilities exist and what they mean**.

These are different responsibilities.

---

## OpenAPI Does Not Always Need to Be Read Directly

If the generated client is well named and well documented, the coding agent may not need to inspect `swagger.json` for every task.

In the common case:

```text
Business requirement
        ↓
Search generated clients
        ↓
Inspect documented methods
        ↓
Generate code
```

OpenAPI remains the authoritative contract and can be consulted when additional details are needed.

For example:

- detailed error responses,
    
- optional parameters,
    
- lifecycle constraints,
    
- response schemas,
    
- operation semantics not fully exposed by the generated client.
    

Therefore, a useful hierarchy is:

```text
OpenAPI
   ↓
Generated typed client
   ↓
Generated documentation/comments
   ↓
Coding agent
```

---

## Error Responses Should Also Be Semantic

Avoid responses such as:

```json
{
  "errorCode": 3817
}
```

Prefer errors that expose the state and possible resolution:

```json
{
  "code": "invoice_already_issued",
  "message": "Issued invoices cannot be deleted.",
  "suggestedOperation": "cancelInvoice"
}
```

This is useful both for generated application code and for an LLM trying to understand the intended workflow.

---

## The Same Principle Applies Beyond REST

The same architecture can be applied to other integration styles.

### GraphQL

Use:

- well-described schema fields,
    
- meaningful query and mutation names,
    
- introspection,
    
- generated typed GraphQL clients.
    

Example:

```graphql
"""
Cancels an issued invoice while preserving it for audit.
Do not use for draft invoices.
"""
cancelInvoice(id: ID!): Invoice!
```

### Messaging

Use message contracts plus AsyncAPI.

For example:

```text
RevokeUserSessions
```

should be clearly distinguishable from:

```text
UserSessionsRevoked
```

The first may be a command that application code sends.

The second is an event produced as a result of processing that command.

AsyncAPI can describe:

- messages,
    
- payload schemas,
    
- channels/topics,
    
- send/receive direction,
    
- headers,
    
- operation semantics.
    

A coding agent can then generate or discover the correct publisher abstraction.

---

## Preferred Architecture

A good integration architecture for LLM-generated code is:

```text
                       Business requirement
                                ↓
                           Coding agent
                                ↓
                 Discover business capability
                                ↓
                     Strongly typed interface
                                ↓
           ┌────────────────────┼────────────────────┐
           │                    │                    │
        OpenAPI             GraphQL              AsyncAPI
           │                    │                    │
         REST                GraphQL             Messaging
```

The important abstraction presented to the coding agent should usually be a **typed, semantically named application client**.

Transport details should remain underneath it.

---

## Core Principle

A useful rule is:

> External integrations should expose well-documented formal contracts, generate strongly typed clients from those contracts, and make those clients easy for coding agents to discover by business capability.

The coding agent should prefer those generated clients over constructing transport-level calls directly.

A well-designed API therefore becomes more than a machine-readable protocol description.

It becomes part of the semantic environment from which the LLM can infer:

- what capabilities exist,
    
- which capability matches the requested business operation,
    
- how it should be called,
    
- and which operations must not be confused with one another.

---

# Reference Note: Designing Software Architecture with LLM Assistance

---
title: Designing Software Architecture with LLM Assistance
tags:
  - software-architecture
  - system-design
  - ai-agents
  - llm
  - decision-making
  - tradeoff-analysis
aliases:
  - LLM-Assisted Software Architecture
  - Architecture Exploration with AI
---

## Core idea

LLMs can significantly accelerate architectural exploration, but they are not reliable guarantees of completeness.

They are good at:

- exploring unfamiliar technologies,
    
- generating design alternatives,
    
- extracting constraints from available context,
    
- comparing trade-offs,
    
- producing prototypes,
    
- identifying common risks,
    
- reviewing an existing proposal.
    

They are weaker at:

- discovering constraints that were never documented,
    
- recognizing questions that neither the user nor the model knows should be asked,
    
- distinguishing a true requirement from an accidental property of the current implementation,
    
- understanding organizational and domain knowledge that exists only in people’s heads,
    
- reliably signaling that the problem description is incomplete.
    

The main risk is not only hallucination.

A more subtle risk is that the model fills missing information with a plausible, typical scenario. The result may be coherent and professionally justified, even though it depends on assumptions that were never confirmed.

This creates an illusion of completeness.

---

## The model may provide a plausible answer instead of revealing missing knowledge

When the description is incomplete, an LLM tends to complete the story.

For example, it may implicitly assume that:

- eventual consistency is acceptable,
    
- operations are idempotent,
    
- messages may be retried safely,
    
- status transitions are linear,
    
- no external system reads the database directly,
    
- a relational database is suitable,
    
- rolling deployments do not create compatibility problems.
    

These assumptions may be reasonable in a typical system, but they may be false in the actual one.

The dangerous part is that a reasonable answer can look like an evidence-based answer.

A model can generate:

- a clean architecture,
    
- a detailed justification,
    
- diagrams,
    
- migration steps,
    
- code,
    
- a list of advantages and disadvantages.
    

This can make the user accept the proposal without examining the assumptions behind it.

Therefore:

> A fluent and internally consistent answer should not be treated as evidence that the problem was understood completely.

---

## Constraints may come from business logic

Technical constraints often originate in business requirements.

The reasoning chain should be:

```text
Business requirement
→ required system property
→ architectural constraint
→ technology choice
```

Examples:

```text
Business rule:
A customer must never be charged twice.

Required property:
Duplicate execution must be safe or prevented.

Architectural consequence:
Idempotency, deduplication, transactional boundaries, or unique operation identifiers are required.
```

```text
Business rule:
The user must immediately know whether a reservation succeeded.

Required property:
The result cannot rely only on eventual consistency.

Architectural consequence:
A purely asynchronous workflow may be insufficient.
```

```text
Business rule:
The organization must reconstruct why a decision was made years later.

Required property:
Historical state and decision inputs must be preserved.

Architectural consequence:
Audit records, versioning, immutable logs, or event history may be required.
```

A technology choice such as a database type may therefore be derived from the domain rather than being a purely technical preference.

At the same time, a stated constraint such as “we must use SQL Server” should be questioned.

It may represent:

- a real organizational standard,
    
- existing expertise,
    
- licensing constraints,
    
- integration dependencies,
    
- transactional requirements,
    
- direct reporting access,
    
- or only historical habit.
    

The model should ask what underlying requirement makes the constraint necessary.

---

## Categories of constraints

It is useful to divide constraints into three groups.

### Explicit constraints

These are written in:

- requirements,
    
- tickets,
    
- documentation,
    
- ADRs,
    
- contracts,
    
- security policies.
    

The model can usually handle them well if they are clearly provided.

### Discoverable constraints

These are not explicitly documented, but can be inferred from:

- code,
    
- tests,
    
- schemas,
    
- deployment manifests,
    
- integrations,
    
- production data,
    
- telemetry,
    
- incident history.
    

Finding them requires a dedicated discovery phase.

### Hidden constraints

These exist only in:

- people’s experience,
    
- manual processes,
    
- informal agreements,
    
- organizational politics,
    
- undocumented customer behavior,
    
- historical exceptions.
    

The model cannot discover them unless some trace of them is available.

This is the most dangerous category.

---

## Do not start with architecture selection

A weak process is:

```text
Problem description
→ architecture proposal
→ implementation
```

A stronger process is:

```text
Problem description
→ confirmed facts
→ missing information
→ assumptions
→ required system properties
→ design alternatives
→ attempt to invalidate alternatives
→ conditional recommendation
→ implementation
```

The first phase should be constraint discovery, not solution generation.

The model should first identify:

- what is known,
    
- what is inferred,
    
- what is assumed,
    
- what is unknown,
    
- what can be interpreted in multiple ways,
    
- what information could reverse the decision.
    

Only then should it propose technologies or architecture.

---

## Separate facts, inferences, assumptions, and unknowns

Important design analysis should not be presented as one continuous narrative.

A useful classification is:

### Confirmed fact

Supported by a trusted source.

Example:

> Deployments are rolling and old instances may run for up to thirty minutes.

### Inference

Logically derived from confirmed facts.

Example:

> Database changes must remain compatible with both application versions.

### Assumption

Used temporarily because information is missing.

Example:

> No external reporting system reads the modified table directly.

### Unknown

Not yet established.

Example:

> Whether message ordering must be preserved across all customers.

### Typical practice

A common recommendation that may not apply here.

Example:

> Using a message broker for long-running operations.

This classification prevents plausible assumptions from silently becoming requirements.

---

## Ask what could reverse the recommendation

One of the most valuable questions is:

> Which missing information could make your recommendation completely different?

Other useful questions include:

- Under what conditions is this solution wrong?
    
- Which assumption has the greatest effect on the decision?
    
- What did you assume even though I did not provide it?
    
- What must be true for this design to work?
    
- Which of those conditions have not been verified?
    
- What system property would make another alternative preferable?
    
- Which parts of the recommendation come from my context, and which come from generic best practices?
    

A good recommendation should be conditional.

For example:

> If delayed consistency is acceptable, operations are idempotent, and the team can operate the broker, asynchronous messaging is a strong option. If the user requires an immediate authoritative result, a synchronous transactional path may be more appropriate.

This is more useful than declaring one architecture universally best.

---

## Ask for the whole solution space, not only several technologies

When asked for “a few options,” the model may generate several variations of the same idea.

Instead, request options from different strategic categories:

- the simplest solution,
    
- a solution using existing infrastructure,
    
- an incremental solution,
    
- a reversible experiment,
    
- a conservative solution,
    
- a long-term target architecture,
    
- a less obvious but realistic option,
    
- a non-technical process change,
    
- changing or removing the requirement,
    
- doing nothing for now.
    

For every option, require:

- applicability conditions,
    
- assumptions,
    
- benefits,
    
- risks,
    
- operational cost,
    
- migration path,
    
- rollback difficulty,
    
- validation method,
    
- information that could change its evaluation.
    

---

## The model may prefer solutions it can implement comfortably

Even when the user asks a neutral question and does not suggest an answer, the resulting recommendation is not necessarily neutral.

An LLM tends to favor solutions that are:

- common in its training data,
- well documented,
- represented by many public examples,
- easy to explain using familiar patterns,
- easy for the model to turn into plausible code.

The model does not have to consciously decide, “I will choose this because I can implement it.” The bias arises indirectly:

```text
Familiar and high-probability approach
→ proposed more often
→ justified more fluently
→ implemented more successfully by the same model
```

This correlation is useful, because implementability matters. However, it can also narrow the solution space.

> The solution the model can describe and generate most confidently is not necessarily the solution that best fits the problem.

### Earlier context can anchor the recommendation

The bias can be triggered by merely mentioning a technology earlier in the conversation.

For example, if SQL Server, Kafka, Temporal, Kubernetes, microservices, or event sourcing appeared anywhere in the preceding discussion, the model may assign that technology more importance than it deserves. It may interpret the mention as:

- an implicit preference,
- an available part of the infrastructure,
- a constraint that should be preserved,
- evidence that the user expects the technology to be used,
- or the intended direction of the conversation.

This can happen even when the technology was mentioned only as an example, comparison point, rejected idea, or unrelated background detail.

The effect is a form of contextual anchoring:

```text
Technology appears in the context
→ becomes more available during generation
→ shapes the alternatives and evaluation criteria
→ is more likely to be recommended
```

Therefore, a neutral-sounding question asked after discussing a specific technology is not fully context-neutral. The model may produce a high-quality answer to the solution space implied by the conversation rather than reconsidering the entire solution space from first principles.

To reduce contextual anchoring:

- state explicitly that previously mentioned technologies are examples, not requirements,
- ask the model to solve the problem once without using any technologies already mentioned,
- request alternatives derived only from confirmed requirements,
- ask which recommendations would disappear if the earlier technology names were removed from the conversation,
- use a fresh context or an independent reviewer for important decisions,
- distinguish technologies that are required, available, preferred, merely considered, and explicitly rejected.

A useful instruction is:

> Treat every previously mentioned technology as non-binding unless it appears in the confirmed constraints. Derive the required system properties first, then generate alternatives without privileging technologies already present in the conversation.

A particularly risky workflow is:

```text
The model selects the criteria
→ selects the technology
→ justifies its own selection
→ implements it
→ reviews its own result
```

The entire chain may be internally consistent while optimizing for an unverified interpretation of the problem. A convincing implementation can then be mistaken for evidence that the architectural choice was correct.

To reduce this bias:

- separate solution selection from implementation,
- ask for alternatives from genuinely different strategic categories,
- require the model to distinguish problem fit from its confidence in implementation,
- explicitly include less familiar or harder-to-generate approaches when they may fit the constraints,
- let a human define or approve the evaluation criteria,
- use an independent review that does not inherit the original recommendation as a fact,
- evaluate the architecture before showing how easily code can be generated for it.

A useful question is:

> Is this solution recommended because it best satisfies the confirmed constraints, or because it is popular, well documented, and easy for the model to implement?

The model cannot perfectly inspect its own internal reasoning, so its answer should not be treated as proof. The question is still valuable because it forces an explicit comparison between problem fit, ecosystem familiarity, and implementation confidence.

For important decisions, ask the model to report these dimensions separately:

| Dimension | Question |
| --- | --- |
| Problem fit | How well does the option satisfy confirmed requirements and constraints? |
| Evidence quality | Which parts are supported by project evidence rather than generic practice? |
| Implementation confidence | How reliably can the model produce and test the implementation? |
| Ecosystem familiarity | Is the recommendation favored because examples and documentation are abundant? |
| Decision uncertainty | Which missing information could change the ranking? |

Implementation confidence is a legitimate criterion, but it should be visible and weighted deliberately rather than silently determining the architecture.

---


## Review the problem across multiple dimensions

A model should be asked to inspect the problem from several perspectives, not only technology selection.

Useful dimensions include:

- business rules and invariants,
    
- state transitions,
    
- data ownership,
    
- consistency,
    
- transactions,
    
- concurrency,
    
- ordering,
    
- duplication and idempotency,
    
- retries and timeouts,
    
- partial failures,
    
- integration contracts,
    
- version compatibility,
    
- deployment strategy,
    
- rollback,
    
- migration,
    
- security and trust boundaries,
    
- privacy,
    
- auditability,
    
- retention,
    
- performance,
    
- scale,
    
- observability,
    
- diagnostics,
    
- operational support,
    
- cost,
    
- team expertise,
    
- vendor lock-in,
    
- reversibility.
    

The purpose is not to generate an enormous checklist for every decision.

The purpose is to identify which dimensions can materially change this specific decision.

---

## Use the model in multiple roles

A single model can be prompted to perform different reviews.

### Domain analyst

Extracts:

- business rules,
    
- actors,
    
- invariants,
    
- states,
    
- exceptions,
    
- ambiguous behavior.
    

### Architect

Generates design alternatives and trade-offs.

### Skeptic

Searches for:

- hidden assumptions,
    
- missing constraints,
    
- failure scenarios,
    
- cases that invalidate the recommendation.
    

### Operator

Checks:

- deployment,
    
- monitoring,
    
- rollback,
    
- support procedures,
    
- failure recovery,
    
- maintenance cost.
    

### Security reviewer

Checks:

- trust boundaries,
    
- sensitive data,
    
- authorization,
    
- abuse scenarios,
    
- compliance implications.
    

### Migration reviewer

Checks:

- old and new versions running together,
    
- schema compatibility,
    
- staged rollout,
    
- backfill,
    
- rollback,
    
- external consumers.
    

Using multiple roles does not make the model automatically correct.

It forces the reasoning to be examined from different angles.

---

## Exploration mode and commitment mode

LLMs are especially valuable because they reduce the cost of experimentation.

They allow teams to:

- explore unfamiliar approaches,
    
- build prototypes quickly,
    
- compare several options,
    
- generate test harnesses,
    
- simulate migrations,
    
- investigate new libraries,
    
- prepare disposable proofs of concept.
    

This supports a more experimental architecture process:

```text
Hypothesis
→ cheap prototype
→ measurement
→ criticism
→ decision
```

However, fast implementation must not be confused with understanding.

The model greatly reduces the cost of entering a new solution, but may not equally reduce the cost of understanding:

- its failure model,
    
- operational complexity,
    
- long-term maintenance,
    
- migration difficulty,
    
- scaling behavior,
    
- guarantees and limitations,
    
- organizational impact.
    

Therefore it is useful to distinguish two modes.

### Exploration mode

Optimize for speed and learning.

- Generate many ideas.
    
- Try unfamiliar technologies.
    
- Accept explicitly labeled temporary assumptions.
    
- Build disposable prototypes.
    
- Avoid production-level completeness.
    
- Prefer reversible experiments.
    

### Commitment mode

Optimize for correctness and reversibility.

- Confirm constraints.
    
- Verify primary documentation.
    
- Test failures and edge cases.
    
- Review operational requirements.
    
- Remove hidden assumptions.
    
- Plan migration and rollback.
    
- Record the architecture decision.
    
- Require human approval.
    

The dangerous transition is when an exploration prototype silently becomes production architecture.

---

## The best role of the model

The model should not be treated as an authority that produces the architecture.

It is better used as an accelerator for:

- knowledge exploration,
    
- question generation,
    
- constraint discovery,
    
- option generation,
    
- trade-off analysis,
    
- prototype creation,
    
- adversarial review,
    
- documentation,
    
- verification planning.
    

The human remains responsible for confirming the model of reality on which the architecture depends.

The most important question is not:

> Did the model produce a reasonable solution?

It is:

> Is the solution based on confirmed properties of this system, or on plausible defaults borrowed from typical systems?

---

## Practical conversation pattern

### Phase 1: problem discovery

Ask the model not to design anything yet.

Request:

- confirmed facts,
    
- inferred consequences,
    
- assumptions,
    
- unknowns,
    
- ambiguities,
    
- missing dimensions,
    
- questions ranked by decision impact.
    

### Phase 2: constraint verification

For each important claim, identify:

- its source,
    
- confidence,
    
- effect on the architecture,
    
- method of verification.
    

### Phase 3: option generation

Generate alternatives from meaningfully different categories.

Do not allow an unconditional recommendation.

### Phase 4: adversarial review

Assume each proposal is wrong.

Search for:

- domain properties that invalidate it,
    
- partial failure scenarios,
    
- hidden consumers,
    
- deployment problems,
    
- migration traps,
    
- operational costs,
    
- POC-to-production gaps.
    

### Phase 5: conditional recommendation

State:

- the preferred option,
    
- the assumptions under which it is preferred,
    
- the conditions that would change the recommendation,
    
- unresolved risks,
    
- required experiments or measurements.
    

### Phase 6: implementation

Provide the implementing agent with:

- business goal,
    
- global invariants,
    
- approved architecture,
    
- local module context,
    
- neighboring contracts,
    
- known assumptions,
    
- required tests,
    
- prohibited changes.
    

---

## Reusable prompt: discovery before design

```text
Help me analyze this architecture problem, but do not propose a solution yet.

First, separate the available information into:

- confirmed facts,
- conclusions derived from those facts,
- working assumptions,
- missing information,
- typical practices that may not apply to this system.

Do not fill missing information with standard assumptions without labeling them explicitly.

Identify all important dimensions of the problem, including dimensions I may not know to ask about:

- business rules and invariants,
- data and consistency,
- transactions and concurrency,
- ordering, retries, and idempotency,
- partial failures,
- integrations,
- performance and scale,
- security and privacy,
- audit and retention,
- deployment, migration, and rollback,
- observability and operations,
- cost and team expertise.

Prepare the questions whose answers could materially change the architecture decision. Rank them by impact.

Also identify:

- assumptions you would otherwise make from the description,
- the riskiest assumptions,
- missing information that could completely reverse the recommendation,
- questions that an inexperienced person might not know to ask.

Stop after the problem analysis and questions. Do not select technologies or architecture yet.
```

---

## Reusable prompt: generating alternatives

```text
Based only on confirmed facts and explicitly stated assumptions, generate meaningfully different solution options.

Include:

- the simplest option,
- an option using the current system,
- an incremental option,
- a reversible option,
- a conservative option,
- a long-term target option,
- a less obvious but realistic option,
- changing the requirement or avoiding a technical solution.

For each option, provide:

1. What it solves.
2. The conditions it requires.
3. Its assumptions.
4. When it is a good choice.
5. When it is a bad choice.
6. Costs and risks.
7. Operational consequences.
8. Migration and rollback difficulty.
9. A cheap experiment that could validate it.
10. Missing information that could change its evaluation.

Do not present any option as unconditionally best.
```

---

## Reusable prompt: adversarial review

```text
Assume the proposed solution is wrong.

Find:

- hidden assumptions,
- missing constraints,
- edge cases,
- unusual domain properties,
- concurrency problems,
- partial failures,
- retry and duplication issues,
- migration and deployment risks,
- operational costs,
- organizational dependencies,
- cases where the solution works in a proof of concept but fails in production.

Then answer:

1. What must be true for the solution to work?
2. Which of those conditions have not been verified?
3. What could completely reverse the recommendation?
4. What tests, measurements, documents, code analysis, or stakeholder conversations would verify the assumptions?
5. Which parts come from the actual context, and which come only from generic best practices?
```

---

## Final mental model

An LLM answer is not the architecture.

It is a proposal generated from a model of the system.

That model contains:

- facts,
    
- inferred consequences,
    
- assumptions,
    
- omissions,
    
- generic patterns.
    

The first task is therefore not to validate the proposed technology.

The first task is to validate the model of reality that produced the proposal.

LLMs make it possible to explore more options, learn faster, and run cheaper experiments. They should increase the amount of reversible experimentation, not the amount of irreversible architectural risk.

---

# Reference Note: Developing Features with AI Coding Agents

---
title: Developing Features with AI Coding Agents
tags:
  - ai-agents
  - software-engineering
  - agentic-workflows
  - feature-development
  - testing
  - code-review
aliases:
  - Feature Development with Agents
  - End-to-End Agentic Feature Lifecycle
---

## A Strong Workflow for Larger Features

A useful process is:

```text
repository analysis
→ behavioral specification
→ examples and decision tables
→ acceptance tests
→ human review
→ implementation of one vertical slice
→ architectural review
→ full implementation
→ independent skeptical review
→ documentation update
```

### Step 1: Repository Analysis

The agent should first locate:

- existing business flows,
    
- data models,
    
- integration points,
    
- transactions,
    
- existing tests,
    
- compatibility risks,
    
- hidden assumptions.
    

It should not modify the code yet.

### Step 2: Behavioral Specification

The specification should include:

- business objective,
    
- terminology,
    
- rules,
    
- exceptions,
    
- negative cases,
    
- side effects,
    
- compatibility requirements,
    
- non-functional constraints,
    
- explicit out-of-scope items.
    

### Step 3: Tests Before Implementation

The agent can prepare:

- business-rule tests,
    
- acceptance tests,
    
- regression tests,
    
- API contract tests,
    
- integration tests.
    

New tests may initially fail. That confirms that they detect the missing behavior.

### Step 4: Human Review of Meaning

The reviewer should not focus only on test implementation quality.

The main questions are:

- Does the test describe the correct business behavior?
    
- Did the agent invent an unstated rule?
    
- Are negative cases present?
    
- Are priorities between rules correct?
    
- Is the test coupled to one implementation unnecessarily?
    
- Does the test preserve an accidental legacy behavior?
    

### Step 5: Freeze the Acceptance Contract

The implementing agent should not freely modify approved acceptance tests.

It may add technical tests, but changes to the accepted business contract require another review.

### Step 6: Implement a Small Vertical Slice

Instead of generating the whole feature at once, implement one full path from entry point to result.

This reveals whether the architecture is appropriate before dozens of files are created.

---

## Tests Are Executable Specifications, but Not Complete Specifications

A test demonstrates an expected example.

It does not always explain:

- why the rule exists,
    
- what a domain term means,
    
- what must not be simplified,
    
- why two similar cases differ,
    
- which behavior is historical but still required.
    

The strongest combination is:

```text
business decision
+ examples or decision table
+ acceptance tests
+ explicit implementation
```

The agent should not be allowed to define both the implementation and the meaning of correctness without independent human review.

Otherwise, it can write tests that confirm its own incorrect interpretation.

---

## Practical Working Rules

### For feature development

- Analyze before modifying.
    
- Write or approve the behavioral specification.
    
- Use examples and decision tables.
    
- Review acceptance tests before implementation.
    
- Freeze approved business tests.
    
- Implement one vertical slice first.
    
- Separate mechanical changes from business changes.
    
- Require a skeptical second review.

---

# Reference Note: Hidden Abstractions May Become More Expensive in Agent-Maintained Code

---
title: Hidden Abstractions May Become More Expensive in Agent-Maintained Code
tags:
  - software-architecture
  - ai-agents
  - abstraction
  - code-maintainability
  - simplicity
  - software-engineering
aliases:
  - Cost of Hidden Abstractions with Agents
  - Explicit vs Magic Abstractions in AI Era
---

Modern software engineering often tries to remove repetitive concerns from local code.

Instead of explicitly writing validation, authorization, retries, transactions, logging, tracing, error mapping, and other infrastructure in every operation, we move them into reusable mechanisms such as:

- middleware,
    
- interceptors,
    
- decorators,
    
- dependency injection,
    
- HTTP message handlers,
    
- framework filters,
    
- MediatR behaviors,
    
- Entity Framework interceptors and query filters,
    
- global exception handling,
    
- conventions,
    
- assembly scanning,
    
- ambient context.
    

This can make individual methods extremely small.

For example:

```csharp
public Task<Response> GetOrder(GetOrderRequest request)
{
    return mediator.Send(request);
}
```

The method appears simple.

However, the actual execution may look more like:

```text
HTTP request
→ authentication middleware
→ authorization middleware
→ exception middleware
→ request validation
→ MediatR
→ logging behavior
→ transaction behavior
→ handler
→ Entity Framework query filter
→ database interceptor
→ SQL
→ response mapping
→ serialization
```

The local code is simple, but the semantics are not.

This distinction may become increasingly important when software is primarily modified by agents.

## Local Simplicity Is Not the Same as Semantic Simplicity

An agent working on a method must understand more than the code visible inside the method.

Consider:

```csharp
await httpClient.SendAsync(request);
```

The request may implicitly include:

- authentication headers,
    
- correlation identifiers,
    
- retry policies,
    
- circuit breakers,
    
- timeouts,
    
- telemetry,
    
- logging,
    
- tenant context.
    

The important behavior is distributed across configuration and framework mechanisms.

Similarly:

```csharp
context.Orders.ToListAsync();
```

may actually mean:

```text
load Orders
where TenantId == CurrentTenant
excluding soft-deleted records
using an interceptor-defined database command behavior
```

because of global query filters and other Entity Framework configuration.

The problem is therefore not simply abstraction.

The deeper problem is **non-local semantics**.

The meaning of a line of code depends on code that is not locally visible.

## Hidden Execution Context Is Particularly Difficult

Some dependencies are not passed explicitly at all.

They may come from:

```text
HttpContext
AsyncLocal
Activity.Current
ClaimsPrincipal
current tenant services
current culture
scoped dependency resolution
feature flags
environment configuration
```

A method can therefore appear to depend on:

```csharp
Process(Order order)
```

while its real inputs include:

```text
order
current user
tenant
feature configuration
current transaction
request metadata
culture
authorization context
```

This makes the true dependency graph much larger than the function signature suggests.

Humans often tolerate this because experienced developers gradually learn the architecture.

An agent entering a repository for a single task must rediscover it.

## Dynamic Dependency Injection Makes the Problem Worse

Constructor injection itself is usually relatively easy to understand.

The situation becomes more difficult when implementations depend on runtime context:

```csharp
services.AddScoped<IPriceCalculator>(sp =>
{
    var context = sp.GetRequiredService<OperationContext>();

    return context.Channel switch
    {
        Channel.Web => new WebPriceCalculator(),
        Channel.Api => new ApiPriceCalculator(),
        _ => new DefaultPriceCalculator()
    };
});
```

Local code may only contain:

```csharp
priceCalculator.Calculate(order);
```

but the implementation that actually runs depends on external state.

Similar problems appear with:

- keyed services,
    
- decorators,
    
- assembly scanning,
    
- open generic registrations,
    
- conditional registration,
    
- plugin architectures.
    

The call site no longer tells the agent what code it is calling.

## Interceptors and Pipelines Can Hide Business-Relevant Semantics

Cross-cutting abstractions become especially problematic when they contain behavior that changes the meaning of an operation.

A call such as:

```csharp
repository.Save(order);
```

may secretly perform:

```text
authorization
→ validation
→ transaction creation
→ audit logging
→ persistence
→ event publication
→ cache invalidation
```

Some of these are infrastructure concerns.

Others are part of the operation's semantics.

The distinction matters.

A generic timing metric being invisible is usually harmless.

A transaction boundary, retry policy, tenant filter, authorization rule, or business validation being invisible can fundamentally change how an agent should modify the operation.

## Agents May Change the Economics of Explicit Code

Traditional software engineering strongly rewards removing repetition.

The reasoning is understandable:

```text
duplication
→ more code
→ more maintenance
→ more opportunities for inconsistency
```

This encourages patterns such as:

```text
DRY
→ centralize behavior
→ hide repeated mechanics behind abstractions
```

But agents reduce the cost of producing and maintaining repetitive code.

This creates the possibility of a different tradeoff:

```text
some duplication
→ greater semantic locality
→ easier reasoning
→ safer automated modification
```

The goal does not need to be eliminating abstractions.

It may instead be eliminating **invisible semantics**.

## Explicit Execution Pipelines

One possible direction is to make important operation semantics visible directly in the operation definition.

Instead of:

```csharp
return mediator.Send(request);
```

an operation might resemble:

```csharp
return Operation
    .From(request)
    .Validate<GetOrderValidator>()
    .Authorize<ReadOrderPolicy>()
    .Retry(ExternalPolicies.Read)
    .Execute<GetOrderHandler>()
    .ValidateResponse<GetOrderResponseValidator>()
    .MapErrors<OrderHttpErrors>()
    .Return();
```

The exact syntax is not important.

The important property is that the execution graph becomes visible:

```text
request
→ validation
→ authorization
→ retry policy
→ execution
→ response validation
→ error mapping
→ response
```

An agent can reason about the operation without reconstructing several layers of framework configuration.

## This Does Not Mean Eliminating All Abstraction

Some abstractions should remain hidden.

For example, an ASP.NET action can reasonably receive:

```csharp
GetOrderRequest request
```

without explicitly handling:

```text
TCP
HTTP parsing
TLS
UTF-8
JSON tokenization
object allocation
deserialization
```

These are implementation mechanisms.

The operation usually does not care how the DTO was produced.

Similarly, returning a response object does not require the business operation to explicitly handle HTTP serialization or socket writes.

A useful boundary may therefore be:

```text
framework owns mechanics
operation owns semantics
```

The framework can hide how input becomes a DTO.

The operation should make visible the decisions that influence what the operation means.

## Infrastructure Can Be Implicit More Safely Than Business Semantics

Not all hidden behavior has the same cost.

Relatively safe candidates for implicit handling include:

```text
generic logging
tracing
request timing
metrics
compression
correlation IDs
serialization
```

More dangerous hidden behavior includes:

```text
authorization
tenant selection
business validation
transaction boundaries
retry behavior
idempotency
cache semantics
feature flags
currency or locale selection
handler selection
error interpretation
```

A possible rule is:

> Infrastructure may be implicit. Business-relevant semantics should preferably be explicit.

The boundary will not always be perfect, but it provides a useful design direction.

## Global Configuration Still Has Value

Making behavior explicit does not require copying implementation details into every operation.

For example, retry may still be centrally configured:

```csharp
RetryPolicies.ExternalRead
```

could define:

```text
3 attempts
exponential backoff
jitter
retry on timeout
retry on HTTP 502/503/504
```

while the operation only says:

```csharp
.Retry(RetryPolicies.ExternalRead)
```

This separates two different concerns:

```text
local code:
WHAT semantic policy applies

central configuration:
HOW that policy works
```

This may be a particularly useful compromise.

Global configuration defines reusable policy.

The call site explicitly declares that the policy participates in the operation.

## Named Semantics Are Better Than Silent Global Behavior

Compare:

```csharp
await client.SendAsync(request);
```

where retry is silently injected by global `HttpClient` configuration,

with:

```csharp
await request
    .Retry(RetryPolicies.ExternalRead)
    .Execute();
```

The second version still uses abstraction.

However, the abstraction leaves a visible semantic trace.

The agent immediately knows that:

```text
this operation may execute more than once
```

That knowledge can affect decisions about:

- idempotency,
    
- database writes,
    
- external side effects,
    
- request identifiers,
    
- duplicate handling.
    

The exact implementation of retry remains reusable and centrally controlled.

## Large Applications Already Struggle With Truly Global Policies

This approach may also address a problem that exists even without AI.

In a large system containing:

```text
hundreds of endpoints
many modules
multiple databases
different external integrations
different SLA requirements
different business risks
```

a single global policy is rarely actually global.

It gradually becomes:

```text
default behavior
except Payments
except Reporting
except legacy integration
except bulk operations
except endpoint X
unless attribute Y exists
unless interface Z is implemented
```

The centralized configuration eventually becomes another complex program.

The apparent simplicity of each endpoint is paid for by complexity elsewhere.

Module-level or operation-class policies may therefore scale better:

```text
system defaults
→ module defaults
→ operation category
→ explicit operation override
```

For example:

```text
Catalog:
    external reads may retry

Payments:
    commands do not retry unless explicitly idempotent

Reporting:
    long timeout
    read-only transaction semantics
```

The policy implementation remains centralized, while the semantic choice stays close to the operation.

## Abstractions Could Become Mechanically Expandable

There is another possible solution that does not require removing existing abstractions.

Future frameworks and development tools could expose the resolved semantics of an operation.

The source might contain:

```csharp
.Retry(RetryPolicies.ExternalRead)
```

while an agent can request:

```text
resolve RetryPolicies.ExternalRead
```

and receive:

```text
max attempts: 3
backoff: exponential
jitter: enabled
retry:
  timeout
  502
  503
  504
```

The same mechanism could resolve an entire endpoint:

```text
GetOrder

authentication:
    required

authorization:
    ReadOrderPolicy

validation:
    GetOrderValidator

tenant:
    request tenant

transaction:
    read-only

retry:
    ExternalRead
    attempts: 3

handler:
    GetOrderHandler

cache:
    OrderById
    TTL: 5 minutes
```

This suggests an important property for future abstractions:

> Abstractions should be mechanically expandable.

Documentation is useful.

A machine-readable resolved execution model is much more useful to an agent.

## Good Abstractions for Agents May Optimize for Different Things

Traditional APIs often optimize for:

```text
few lines
few parameters
minimal boilerplate
maximum reuse
```

Agent-oriented APIs may increasingly optimize for:

```text
semantic locality
explicit dependencies
visible execution flow
mechanically discoverable behavior
predictable composition
```

This does not imply that code must become low-level.

For example:

```csharp
.RetryTransient(3)
```

is still an abstraction.

It hides backoff implementation, timers, exception matching, and scheduling.

But it preserves the fact that matters semantically:

```text
the operation may execute multiple times
```

By contrast:

```csharp
.ExecuteUsingStandardEnterprisePolicies()
```

may hide almost everything the agent needs to know.

A useful distinction is therefore:

> A good abstraction reduces syntax without hiding important semantics.


## Business Meaning Should Be Encoded in the Same Vocabulary

Semantic locality is not only about where behavior executes.

It is also about whether the code uses the same concepts and vocabulary as the domain, documentation, API contracts, database schema, tests, and operational descriptions.

Consider:

```csharp
if (payment != null)
{
    ...
}
```

In a particular system, this may implicitly mean:

```text
the invoice is unpaid
```

A developer who has worked on the system for years may know that convention.

An agent may not.

The agent sees evidence:

```text
Payment exists
```

but must infer the business conclusion:

```text
invoice is unpaid
```

That inference may be correct, incorrect, or missed entirely.

Compare that with:

```csharp
if (payment.Status == PaymentStatus.Unpaid)
{
    ...
}
```

or:

```csharp
if (payment.IsUnpaid)
{
    ...
}
```

Now the business concept is explicitly represented in the code.

This matters particularly when the same concept appears elsewhere in the system.

Suppose the documentation says:

```text
retry unpaid payments
```

the API specification contains:

```text
paymentStatus: unpaid
```

and tests are named:

```text
ShouldRetryUnpaidPayment
```

An agent searching for or reasoning about "unpaid payment" can directly associate all of these artifacts with:

```csharp
PaymentStatus.Unpaid
```

It has a much weaker semantic connection to:

```csharp
payment != null
```

The same problem appears with sentinel values and technical representations:

```csharp
amount == 0
endDate == null
retryCount == -1
status == 2
customerId != null
```

These values may encode business meanings such as:

```text
free
active
unlimited retries
awaiting payment
customer assigned
```

but the meaning is not present in the expression itself.

A more agent-friendly model exposes the conclusion:

```csharp
price.IsFree
subscription.IsActive
retryPolicy.IsUnlimited
payment.Status == PaymentStatus.Unpaid
order.HasAssignedCustomer
```

This suggests a broader rule:

> Prefer code that encodes business conclusions rather than only technical evidence from which those conclusions must be inferred.

The principle extends beyond source code.

Ideally, the same domain vocabulary should appear consistently in:

```text
domain model
API contracts
database schema
tests
documentation
events and messages
logs and telemetry
```

For example:

```text
Documentation:
    unpaid payment

Code:
    PaymentStatus.Unpaid

API:
    paymentStatus = "unpaid"

Database:
    payment_status = "unpaid"

Event:
    PaymentBecameUnpaid

Test:
    ShouldRetryUnpaidPayment
```

This creates **semantic alignment across artifacts**.

For an agent, that alignment has several benefits:

- repository search becomes more reliable,
- embeddings and RAG retrieval are more likely to connect relevant artifacts,
- documentation can be mapped to implementation more directly,
- fewer hidden conventions must be reconstructed,
- code review requires less inference,
- generated changes are more likely to use the correct business concept.

Comments can help:

```csharp
// A non-null Payment means the invoice has not been paid yet.
if (payment != null)
```

but comments are weaker than encoding the meaning in the model itself.

They can become stale, they may not participate in all tooling, and they still leave the underlying representation semantically indirect.

Documentation or schema descriptions are also useful when the technical representation cannot be changed.

For example, if a legacy database uses:

```text
payment_state = 2
```

then the schema or mapping layer should make the meaning mechanically discoverable:

```text
2 = unpaid
```

or preferably expose it to application code as:

```csharp
PaymentStatus.Unpaid
```

This leads to another useful design principle:

> Use the same business vocabulary across code, contracts, schemas, tests, and documentation whenever practical.

For humans, this reduces the amount of institutional knowledge needed to understand the system.

For agents, it reduces the number of semantic translations that must be inferred before a change can be made safely.

In this sense, agent-friendly code should not merely be readable.

It should be **semantically searchable and cross-referenceable**.


## Semantic Locality May Become an Architectural Goal

We can think about code as having different levels of semantic locality.

High semantic locality:

```csharp
CalculatePrice(order, customer, pricingRules);
```

The important inputs are visible.

Lower semantic locality:

```csharp
priceCalculator.Calculate(order);
```

The implementation must be discovered.

Even lower semantic locality:

```csharp
priceCalculator.Calculate(order);
```

where dependency injection selects the implementation based on runtime context.

Very low semantic locality:

```csharp
priceCalculator.Calculate(order);
```

where the result also depends on:

```text
current tenant
feature flags
ambient user
interceptors
global cache
transaction context
dynamic configuration
```

The textual code can remain equally short while the reasoning cost increases dramatically.

For agent-maintained systems, **semantic locality may become as important as traditional measures such as coupling, cohesion, and duplication**.

## The Likely Direction Is Not "No Abstractions"

The more realistic direction is:

```text
hide mechanisms
expose semantic decisions
centralize implementation
localize intent
make abstractions inspectable
```

This could lead to code that is somewhat more verbose than today's most heavily abstracted application architectures.

But the code may also become:

- easier for agents to modify,
    
- easier for humans to review,
    
- easier to test,
    
- easier to analyze statically,
    
- less dependent on institutional knowledge,
    
- safer to refactor automatically.
    

The important shift may therefore not be from abstraction to no abstraction.

It may be from:

```text
implicit, non-local behavior
```

toward:

```text
explicit, composable, mechanically discoverable behavior
```

In software increasingly written and maintained by agents, the cost of repetition may fall while the cost of hidden semantics becomes much more visible.

That could change what we consider "clean" architecture.

---

# Reference Note: Introduction to Workflow Orchestration

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

---

# Reference Note: LLMs as a Code Review Team

---
title: LLMs as a Code Review Team
tags:
  - code-review
  - ai-agents
  - software-engineering
  - multi-agent
  - quality-assurance
  - testing
aliases:
  - Multi-Agent Code Review
  - Continuous Engineering Verification with LLMs
---

LLMs can change code review from a mostly human, manually executed activity into a continuous system of specialized reviewers.

The most useful model is not:

> One AI reads a pull request and gives its opinion.

A more interesting model is:

> A team of specialized agents continuously examines changes, forms hypotheses about potential problems, and uses deterministic tools to verify them.

The role of humans then shifts toward reviewing important findings, resolving ambiguity, making architectural decisions, and accepting responsibility for the final change.

---

## The Most Important Property May Be Relentlessness

One of the biggest advantages of an automated reviewer is not intelligence.

It is relentlessness.

A human reviewer gets tired.

After reviewing many pull requests, large diffs, repetitive changes, or hundreds of similar files, attention inevitably decreases.

An agent does not care that:

- this is the twentieth pull request today;
    
- the diff contains 150 files;
    
- the same validation pattern appears for the hundredth time;
    
- a checklist contains 40 items;
    
- the issue it is looking for occurs only once every few thousand changes.
    

It can apply the same procedure every time.

This makes agents especially useful for review work that is:

- repetitive;
    
- systematic;
    
- easy to forget;
    
- rare but important;
    
- dependent on large amounts of context.
    

A human may know that every new endpoint should verify authorization, propagate cancellation, validate input, preserve backward compatibility, update telemetry, and contain relevant tests.

Knowing the rules does not mean remembering every rule during every review.

An agent can.

This may be one of the strongest reasons to introduce AI review even when human reviewers are already very experienced.

---

## Code Review Does Not Need One General Reviewer

A single prompt such as:

```text
Review this pull request.
```

asks one model to simultaneously reason about too many unrelated concerns.

A better design is a team of specialized reviewers.

For example:

```text
Review Router
    |
    +-- Correctness Reviewer
    +-- Test Reviewer
    +-- Security Reviewer
    +-- API Compatibility Reviewer
    +-- Database Reviewer
    +-- Performance Reviewer
    +-- Concurrency Reviewer
    +-- Architecture Reviewer
```

Not every reviewer needs to run for every change.

A lightweight routing agent can inspect the diff and decide which specialists are relevant.

For example:

```text
DTO / controller / public contract changed
        ->
API Compatibility Reviewer
```

or:

```text
EF / SQL / migration changed
        ->
Database Reviewer
```

or:

```text
authentication / authorization changed
        ->
Security Reviewer
```

Correctness and test reviewers may run almost always, while expensive specialists run conditionally.

This keeps both cost and noise under control.

---

## Different Reviewers Should Have Different Instructions

Each reviewer can have its own playbook.

A database reviewer may inspect:

- query count;
    
- N+1 queries;
    
- indexes;
    
- transaction boundaries;
    
- query plans;
    
- excessive materialization;
    
- unnecessary round trips;
    
- locking behavior.
    

An API reviewer may inspect:

- backward compatibility;
    
- serialization changes;
    
- optional versus required fields;
    
- enum compatibility;
    
- HTTP semantics;
    
- authorization;
    
- versioning.
    

A performance reviewer may inspect:

- allocations;
    
- algorithmic complexity;
    
- reflection;
    
- unnecessary abstractions;
    
- excessive LINQ;
    
- repeated parsing;
    
- synchronization;
    
- database access;
    
- hot-path behavior.
    

A correctness reviewer may concentrate on:

- boundary conditions;
    
- missing cases;
    
- null handling;
    
- exception paths;
    
- inconsistent state;
    
- assumptions that no longer hold.
    

This is much easier to improve than one enormous global prompt.

---

## The Reviewer Should Form Hypotheses, Not Just Opinions

LLMs are useful at spotting suspicious patterns, but a review becomes much more valuable when an agent can verify its own suspicions.

Instead of:

```text
This code might be slow.
```

the reviewer should try:

```text
Hypothesis:
The new implementation introduces O(n²) behavior.

Experiment:
Run a benchmark for 1k, 10k and 100k elements.

Result:
main:  38 ms
PR:    4.7 s

Conclusion:
Confirmed performance regression.
```

The same principle applies to correctness.

```text
Reviewer suspects a bug
        |
        v
generate reproduction test
        |
        v
run against main
        |
        v
run against PR
        |
        v
report only if confirmed
```

This creates a useful distinction:

> LLMs generate hypotheses. Deterministic tools provide evidence.

---

## Reviewers Can Use the Existing Engineering Toolchain

AI review does not replace CI.

It orchestrates and interprets it.

A reviewer can use:

```text
dotnet test
static analyzers
CodeQL
coverage
BenchmarkDotNet
dotnet-counters
dotnet-trace
SQL EXPLAIN
linters
integration tests
property-based tests
fuzz tests
```

The agent can decide which tool is relevant, execute it, interpret the result, and attach the evidence to the finding.

Instead of:

> This allocation could become expensive.

it can report:

```text
main:
2.1 µs
0 B allocated

PR:
3.8 µs
320 B allocated

The method is called approximately 5 million times per day.
```

The discussion then becomes much less subjective.

---

## Agents Can Also Create Tests During Review

A powerful reviewer should be allowed to create temporary tests.

For example:

```text
Potential bug detected
        |
create regression test
        |
test passes on main
        |
test fails on PR
        |
finding confirmed
```

The test itself can become part of the suggested fix.

This turns review into something closer to automated investigation.

The reviewer is not merely saying:

> I think this is wrong.

It is saying:

> I can demonstrate a case where this is wrong.

---

## Reviewer and Fixer Should Be Separate Roles

It may be useful to deliberately separate finding problems from changing code.

For example:

```text
Reviewer
    read
    search
    run tests
    run benchmarks
    no write access
```

and:

```text
Fixer
    read
    edit
    run tests
```

The workflow becomes:

```text
Reviewer:
I suspect a bug.

Validator:
Confirmed by this test.

Fixer:
Here is a proposed patch.

Validator:
The test now passes.

Human:
Approve or reject.
```

This reduces the risk that the same agent unconsciously rationalizes the solution it has just created.

It also makes permissions easier to control.

---

## Independent Reviewers May Be Valuable

Review does not necessarily have to be performed by the same model that produced the code.

It may be useful to deliberately introduce diversity:

```text
Model A generates code.

Model B reviews correctness.

Model C reviews security.

Model D tries to find counterexamples.
```

Different models may have different failure modes.

Even using the same model with independent contexts can help because one reviewer is not anchored by the reasoning that produced the implementation.

The analogy is similar to having another engineer examine the change without first hearing a long explanation of why the author thinks it is correct.

---

## A Review Router Can Control Cost

Running ten powerful models on every typo would be wasteful.

A router can classify a change first.

For example:

```text
Change classification:

documentation only
    -> no technical review

test-only change
    -> correctness + test reviewer

database migration
    -> correctness + database + compatibility

authentication change
    -> correctness + security + tests

hot-path implementation
    -> correctness + performance + tests
```

The router itself can use a cheap model.

Expensive reasoning is reserved for changes where it matters.

---

## A Final Reviewer Can Synthesize the Findings

Multiple reviewers create another problem: noise.

Seven agents producing thirty comments can make a pull request worse rather than better.

A final synthesizer can therefore collect all findings and perform:

```text
deduplication
confidence filtering
severity ranking
cross-checking
evidence validation
```

A possible pipeline is:

```text
7 reviewers

24 candidate findings

9 duplicates / overlapping findings removed

5 low-confidence findings discarded

4 findings disproved by tests

6 findings presented to the developer
```

The final review can use a common format:

```text
Severity: HIGH
Confidence: HIGH

Problem:
...

Evidence:
...

Impact:
...

Suggested fix:
...

Reviewer:
database-performance
```

This makes AI review much less noisy.

---

## Confidence Should Matter

Not every observation deserves a pull-request comment.

A useful policy could be:

```text
HIGH severity + HIGH confidence
    -> inline comment / request changes

MEDIUM severity + HIGH confidence
    -> normal comment

LOW confidence
    -> review summary only

LOW severity + LOW confidence
    -> suppress
```

This is particularly important because an AI reviewer that produces too many false positives will quickly be ignored.

The goal is not maximum number of findings.

The goal is high-value findings.

---

## Reviewers Can Learn From Human Decisions

Every review interaction creates useful feedback.

For each finding the system can record:

```text
accepted
rejected
false positive
already known
fixed
ignored
disputed
```

Over time this becomes a dataset for improving the reviewer instructions.

For example, the team may discover that the performance reviewer frequently complains about allocations in paths that are executed once per request and have no measurable impact.

Its instructions can then be changed:

```text
Do not report allocation differences unless:

- the code is demonstrably hot,
- the difference is measurable,
- or the allocation has another significant consequence.
```

The review process itself can therefore become an optimization loop.

---

## Review Quality Can Be Measured

AI review creates the possibility of measuring reviewer effectiveness much more systematically.

Useful metrics include:

```text
findings generated
findings accepted
findings rejected
false-positive rate
confirmed bugs found
security problems found
regressions found
tests generated
findings confirmed by tests
time per review
cost per review
```

A reviewer can then be evaluated like another engineering component.

For example:

```text
Security Reviewer

1,240 PRs reviewed
87 findings
72 accepted
9 rejected
6 inconclusive

precision: ~83%
```

The question becomes less:

> Is this prompt good?

and more:

> How effective is this reviewer?

---

## GitHub Is a Natural Platform for This Model

GitHub already provides most of the infrastructure required to build such a system.

A reviewer can react to events such as:

```text
pull request created
new commit pushed
review requested
comment created
check completed
```

There are several ways to integrate an AI reviewer.

---

## GitHub Actions

The simplest architecture is often:

```text
Pull Request
     |
GitHub Actions
     |
AI Reviewer
```

The important advantage is that the agent can operate in the same environment as ordinary CI.

It can:

```text
checkout repository
build
run tests
generate temporary tests
run benchmarks
inspect artifacts
```

This is particularly attractive when verification requires executing the code.

---

## GitHub Apps

An external reviewer such as CodeRabbit can instead run as a GitHub App.

The architecture becomes:

```text
GitHub
   |
webhook
   |
External Review Service
   |
GitHub API
   |
PR review / comments / checks
```

The service may run completely outside GitHub.

It can listen for events such as:

```text
pull_request.opened
pull_request.synchronize
issue_comment
review_comment
```

and react automatically.

From the developer's perspective, the application behaves almost like another reviewer.

It can add:

- inline comments;
    
- review summaries;
    
- suggested changes;
    
- approvals;
    
- requests for changes;
    
- status checks.
    

This is the model used by many external analysis and review products.

---

## Reviewers Can Also Be Invoked On Demand

Not everything needs to run automatically.

A developer could request specialized investigation directly from a pull request:

```text
@review-bot performance
```

or:

```text
/review security
```

or even:

```text
@review-bot investigate whether this query causes an N+1 problem
```

This creates an interesting hybrid between a reviewer and an engineering assistant.

The pull request itself becomes the workspace in which humans and agents collaborate.

---

## GitHub Checks May Be Better Than Comments

Not every result needs to appear as another PR conversation.

Reviewers can publish checks such as:

```text
Build                     PASS
Tests                     PASS
Security Review           PASS
API Compatibility         PASS
Performance Review        FAIL
Database Review           PASS
```

Detailed findings can live inside the check.

This reduces comment noise and gives the review system a more structured interface.

Selected checks could eventually become required for merge.

Care is needed, however.

An unreliable LLM reviewer should not become a merge gate merely because it exists.

---

## External Reviewers Can Be Independent Services

There does not need to be one central AI-review system.

A repository could eventually have:

```text
GitHub Copilot
Company Architecture Reviewer
Security vendor
Performance service
CodeQL
Sonar
Dependency scanner
Business Rules Reviewer
```

All of them independently observe the same pull request.

GitHub effectively becomes an event bus and shared collaboration surface.

Different reviewers may be:

- SaaS products;
    
- internal company services;
    
- GitHub Actions;
    
- custom agents;
    
- deterministic analyzers;
    
- LLM-based systems.
    

Their results meet in the pull request.

---

## Private Companies Can Build Their Own Reviewer

A company can create a private GitHub App and run its reviewer in its own infrastructure.

For example:

```text
GitHub
   |
webhook
   |
Company Review Platform
   |
   +-- LLM
   +-- internal documentation
   +-- architecture decisions
   +-- Jira
   +-- production telemetry
   +-- Grafana
   +-- test infrastructure
```

This reviewer could know things that a general-purpose SaaS reviewer cannot know.

For example:

> This endpoint technically works, but service X is being retired and new code must use service Y.

or:

> This query operates on a table containing 900 million rows in production, so this seemingly harmless scan is dangerous.

The value of the reviewer grows significantly when it has access to organizational context.

---

## Permissions Should Be Deliberately Limited

A reviewer does not necessarily need permission to modify code.

A conservative integration could have:

```text
Repository contents: read
Pull requests: read/write
Checks: write
Actions: read
```

while explicitly denying:

```text
Repository contents: write
Administration: write
Secrets
```

A system that only investigates and comments requires much less trust than an autonomous coding agent.

Writing code can be delegated to a separate fixer with stronger permissions.

---

## Human Review Does Not Necessarily Disappear

AI review may instead change what humans review.

Today humans often spend time checking things such as:

```text
Did someone forget a null check?
Is cancellation propagated?
Is this method tested?
Is this API backward compatible?
Did someone accidentally introduce N+1?
```

These are valuable checks, but they consume attention.

Agents can perform them relentlessly.

Humans can spend more attention on:

- whether the business behavior is correct;
    
- whether the abstraction makes sense;
    
- whether the product should behave this way at all;
    
- long-term architecture;
    
- trade-offs;
    
- organizational context;
    
- risk acceptance.
    

The review becomes layered:

```text
machines check everything they can check repeatedly

humans concentrate on what requires judgment
```

---

# Code Review May Become Continuous Engineering Verification

The most important shift may therefore be conceptual.

Traditional review is approximately:

```text
developer writes code
        |
human reads diff
        |
human notices some problems
        |
merge
```

Agentic review can become:

```text
developer or agent creates change
        |
multiple reviewers inspect it
        |
reviewers form hypotheses
        |
tests and tools verify them
        |
findings are challenged and filtered
        |
fixes are proposed
        |
tests verify the fixes
        |
human reviews the remaining decisions
```

The goal is no longer merely:

> Have somebody read the code before merge.

It becomes:

> Continuously attempt to prove that the change is wrong before it reaches production.

That is where LLM reviewers may be particularly powerful.

They are not perfect.

But they can be **relentless, specialized, cheap to duplicate, able to investigate suspicious changes, and willing to run the same verification procedure every single time**.

For code review, those properties may matter almost as much as raw intelligence.

---

