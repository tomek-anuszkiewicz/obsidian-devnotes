---
title: Multi-Agent Software Development
tags:
  - multi-agent
  - ai-agents
  - software-engineering
  - orchestration
  - team-collaboration
  - agentic-workflows
aliases:
  - Multi-Agent Engineering Teams
  - Collaborative Coding Agents
  - "Collaboration Patterns for Coding Agents"
---

Adding another agent can mean investigating an alternative, dividing independent implementation work, bringing in a specialist, or reviewing a candidate from a separate context. Those choices solve different problems even when they use similar infrastructure.

This article develops collaboration patterns and the trade-off between shared context and independent judgment. [[Operating a Reliable Multi-Agent Engineering Workflow]] follows how workers are run and coordinated: workspaces, roles and skills, containment, integration, model and compute allocation, asynchronous work, and human coordination. Choose the reason for involving several agents before choosing how many workers to start.

Modern agentic development is no longer limited to a single coding agent working in one loop. A new class of workflows is emerging around multiple agents working in parallel, sequentially, competitively, or as a coordinated team.

This creates a new design problem: not only _what should an agent do_, but also _how many agents should be involved, how should work be divided, how independent should they be, and how should their outputs be validated and integrated_.

## From One Agent to Many Agents

The simplest model is a single agent:

```text
Human
  ↓
Agent
  ↓
Result
```

A more advanced model is to run several independent sessions:

```text
Human
├── Agent A
├── Agent B
├── Agent C
└── Agent D
```

In this model, the human is still the orchestrator.

The developer decides:

- what each agent should do,

- what context each agent receives,

- whether the agents work on the same or different problems,

- how results are compared,

- which changes are accepted,

- how conflicts are resolved.

This is often the easiest way to experiment with multi-agent development because it requires almost no dedicated orchestration infrastructure.

## Multiple Independent Sessions

Running several independent sessions is particularly useful for exploration.

For example:

```text
Agent A → analyze the current architecture
Agent B → propose the smallest possible change
Agent C → propose a radical simplification
Agent D → focus only on security risks
```

The goal here is not parallel implementation.

The goal is to obtain several independent views of the same problem.

This can be valuable because agents can suffer from anchoring in the same way that humans do. Once one solution appears plausible, later reasoning can become biased toward defending or extending it.

Independent sessions make it easier to search a larger solution space.

A useful pattern is:

```text
independent exploration
        ↓
human comparison
        ↓
architecture decision
        ↓
implementation
```

This is different from a system where one agent decomposes a task and immediately delegates implementation.

## Subagents

Subagents introduce another layer.

Instead of the human manually managing multiple sessions, a main agent can delegate smaller tasks:

```text
Human
  ↓
Main Agent
  ├── Research Agent
  ├── Test Agent
  ├── Database Agent
  └── Reviewer Agent
```

Each subagent can have:

- its own context,

- its own instructions,

- a restricted toolset,

- a specialized role,

- a limited task.

This is useful because large tasks often pollute a single context.

Instead of one model simultaneously reasoning about:

```text
architecture
database
frontend
tests
documentation
security
```

the problem can be split into smaller, cleaner contexts.

This is not only a performance optimization. It is also a form of context engineering.

When a single agent attempts to reason about database schemas, API contracts, frontend components, test harnesses, and security policies inside one long context window, the model inevitably suffers from instruction drift and attention degradation. Important constraints get pushed out of active attention, and the agent begins making unforced errors across module boundaries. Partitioning the work into subagents keeps contexts small, focused, and disposable.

## Fleet-Style Execution

Fleet-style systems automate decomposition and parallel execution.

The user provides one larger task:

```text
Add a new payment provider.

- implement the adapter
- update the API
- add tests
- update documentation
```

The orchestrator decides which parts can run independently:

```text
           task
            ↓
       orchestrator
       /    |    \
adapter   tests   docs
       \    |    /
        integration
```

This works best when the problem contains independent or loosely coupled subtasks.

Examples include:

- updating many independent modules,

- migrating multiple components,

- creating tests for many handlers,

- updating documentation,

- analyzing several failures,

- modifying independent APIs.

Fleet-style execution provides little benefit when the task is fundamentally sequential:

```text
A → B → C → D
```

It is most useful when the task looks more like:

```text
A
B
C
D
```

or:

```text
A
├── B
├── C
└── D
```

## Persistent Agent Teams

A persistent agent team goes beyond temporary subagents.

Instead of creating anonymous workers for every task, the repository can contain stable roles:

```text
Team
├── Lead Agent
├── Backend Agent
├── Frontend Agent
├── Database Agent
├── Test Agent
└── Security Agent
```

Each agent may have its own:

- instructions,

- responsibilities,

- tools,

- skills,

- context,

- conventions.

This starts to resemble an organizational structure rather than a simple task execution mechanism.

The repository may also contain persistent team knowledge:

```text
AGENTS.md
architecture.md
decisions.md
skills/
review-rules/
```

This gives agents a form of organizational memory.

The codebase increasingly contains not only source code, but also instructions describing how autonomous workers should operate on it.

## Parallelism Has Several Different Meanings

"Multi-agent" should not be understood only as "do things faster."

There are several distinct patterns.

### Parallel execution

Different agents execute independent subtasks:

```text
Agent A → backend
Agent B → frontend
Agent C → tests
Agent D → documentation
```

The objective is mostly speed.

### Decomposition

A large problem is split into smaller problems.

The main advantage is reduced complexity and cleaner context.

### Specialization

Different agents have different roles:

```text
Database Agent
Security Agent
Performance Agent
Test Agent
Architecture Agent
```

The objective is not necessarily parallelism, but better reasoning within each domain.

### Diversity

Multiple agents investigate the same problem independently:

```text
Agent A ─┐
Agent B ─┼→ same problem
Agent C ─┘
```

The objective is to avoid premature convergence on one solution.

## Competitive Solution Search

An especially interesting pattern is to let several agents solve the same problem.

For example:

```text
Find the cause of this performance regression.
```

Different agents may investigate different hypotheses:

```text
Agent A → database queries
Agent B → memory allocations
Agent C → concurrency
Agent D → recent repository changes
```

A separate judge can then compare the evidence:

```text
A ─┐
B ─┼→ Judge Agent → ranked hypotheses
C ─┤
D ─┘
```

This transforms multi-agent development from simple task parallelization into search over the solution space.

The same pattern can be used for architecture:

```text
Agent A → minimal-change architecture
Agent B → performance-oriented architecture
Agent C → simplest architecture
Agent D → long-term maintainability
```

Then another stage compares trade-offs.

## Role Pipelines

Multiple agents do not need to work simultaneously.

They can form a pipeline:

```text
Planner
  ↓
Implementer
  ↓
Tester
  ↓
Security Reviewer
  ↓
Architecture Reviewer
  ↓
Fixer
```

This provides separation of responsibility.

A particularly important example is review.

An implementer should not necessarily be responsible for validating its own assumptions.

A separate reviewer can receive only:

```text
specification
+
diff
```

without seeing the implementer's reasoning.

This reduces anchoring and makes the review more independent.

When an implementer reviews its own code, it suffers from self-confirmation bias—routinely glossing over its own logic flaws and rationalizing edge-case omissions. Passing only the raw diff and the specification to an independent reviewer agent, with zero chain-of-thought inheritance from the implementer, forces the reviewer to evaluate the solution strictly on its own merits.

## Shared Context vs Independent Context

Multi-agent systems introduce an important tension.

If all agents share information immediately:

```text
Agent A discovers X
        ↓
Agents B and C immediately know X
```

collaboration becomes efficient.

But independence decreases.

If contexts are isolated:

```text
Agent A → hypothesis X
Agent B → hypothesis Y
Agent C → hypothesis Z
```

the system receives more diverse reasoning, but work may be duplicated.

This means context sharing should itself be a design decision.

Some tasks benefit from collaboration.

Others benefit from deliberate information isolation.

For debugging, architecture review, risk analysis, and security review, independent reasoning can be especially valuable.

If an early agent makes an incorrect assumption in a fully shared context, that hallucination cascades across the entire fleet. On the other hand, complete isolation risks duplicate token spend as multiple agents rediscover the same codebase layout or type contracts. The practical heuristic is simple: collaborative implementation of known interfaces benefits from shared context, whereas adversarial review, root-cause debugging, and security sweeps demand hard context isolation.

## Conclusion

Fleet, Squad, subagents, multiple sessions, custom agents, and isolated worktrees should not be treated as competing solutions.

They represent different building blocks of a broader model:

**multi-agent software development**.

A useful conceptual mapping is:

```text
Multiple sessions
→ exploration and diversity

Subagents
→ focused delegation

Fleet
→ automatic decomposition and parallel execution

Persistent agent teams
→ specialization and organizational memory

Worktrees / sandboxes
→ isolation and failure containment

Reviewer agents
→ independent verification

Heterogeneous models
→ compute optimization

Agent scheduler
→ dynamic allocation of reasoning resources
```

The most interesting change may ultimately not be that agents write code faster.

It may be that software development acquires a completely new unit of computation:

**an autonomous software worker that can be created, specialized, isolated, coordinated, reviewed, and discarded on demand** (see [[Workflow Orchestration in Agentic Systems]] and [[The Conductor Pattern for High-Bandwidth Engineering]]).

## Related Notes

- [[Workflow Orchestration in Agentic Systems]] — State machines, durable sagas, and execution boundaries in agentic systems.
- [[The Conductor Pattern for High-Bandwidth Engineering]] — Human coordination of multiple concurrent autonomous agent tracks.
- [[LLMs as a Code Review Team]] — Multi-agent ensembles for specialized security, architecture, and correctness review.
- [[From AI-Assisted Teams to Cross-System Feature Ownership]] — How multi-agent setups shift engineer responsibilities from isolated code to feature lifecycles.
