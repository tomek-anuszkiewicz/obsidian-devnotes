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
---

> [!IMPORTANT] Executive Architectural Thesis: Multi-Agent Systems as Distributed Computing with Stochastic Reasoning Nodes
> Multi-agent software engineering transforms software construction from interactive IDE assistance into a **distributed systems problem**. The central engineering question shifts from *"Can a frontier model write correct code in isolation?"* to:
> $$\text{System Reliability} = f(\text{Task Decomposition}, \text{Context Isolation}, \text{Adversarial Verification}, \text{State Synchronization})$$
> Multi-agent architectures introduce a fundamentally new computational primitive: **the autonomous, ephemeral software worker** that is dynamically provisioned, specialized via modular skills, sandboxed in isolated repository worktrees, verified against non-negotiable harness oracles, and terminated on demand. Scaling engineering velocity requires managing communication topologies, context pollution boundaries, and failure containment rather than expanding monolithic prompt contexts.

| Coordination Topology | Execution Pattern | State & Context Boundary | Primary Failure Mode | Arbiter / Verification Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Independent Exploration** | Parallel non-communicating sessions | 100% disjoint context | Solution space anchoring / human review bottleneck | Human architect comparison & selection |
| **Hierarchical Subagents** | Vertical tree delegation (Parent $\to$ Child) | Filtered, scoped context per leaf node | Context loss across parent-child boundary | Parent agent summary aggregation & re-prompting |
| **Fleet / Graph Decomposition** | Parallel horizontal task graphs (DAG) | Isolated repository worktrees / sandboxes | Merge conflicts & inter-module interface drift | Integration test suites & harness oracles |
| **Role Pipelines** | Sequential stage-gate transitions | Progressively enriched pipeline artifact | Cascading upstream hallucinations | Downstream verification gates (lint, build, review) |
| **Competitive / Adversarial** | Best-of-$N$ generation & red-teaming | Disjoint generation with shared critique | Over-optimization of proxy metrics | Automated benchmark suites & scoring oracles |
| **Persistent Agent Teams** | Long-lived specialized functional roles | Shared repository conventions & skills | Role boundary confusion & coordination deadlock | Team lead orchestrator & architectural rulebooks |

---

Modern agentic development is no longer limited to a single coding agent working in one loop. A new class of workflows is emerging around multiple agents working in parallel, sequentially, competitively, or as a coordinated team.

This creates a new design problem: not only _what should an agent do_, but also _how many agents should be involved, how should work be divided, how independent should they be, and how should their outputs be validated and integrated_—questions central to both [[Introduction to Workflow Orchestration|workflow orchestration]] and building an [[LLMs as a Code Review Team|automated code review team]].

## 1. From One Agent to Many Agents

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

In this model, the human is still the orchestrator operating within an [[Agentic Coding Harness and Controlled Development Workflows|agentic coding harness]].

The developer decides:

- what each agent should do,
    
- what context each agent receives,
    
- whether the agents work on the same or different problems,
    
- how results are compared,
    
- which changes are accepted,
    
- how conflicts are resolved.
    

This is often the easiest way to experiment with multi-agent development because it requires almost no dedicated infrastructure beyond standard [[Agent Deployment and Execution Models|agent deployment and execution models]] (or custom environments evaluated in [[Exploring Agent Harnesses|exploring agent harnesses]]).

## 2. Multiple Independent Sessions

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

## 3. Subagents

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

## 4. Fleet-Style Execution

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

## 5. Persistent Agent Teams

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

## 6. Parallelism Has Several Different Meanings

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

## 7. Competitive Solution Search

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

## 8. Role Pipelines

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

## 9. Shared Context vs Independent Context

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

## 10. Workspace Isolation

Parallel coding introduces a practical problem: filesystem conflicts.

This is dangerous:

```text
Agent A → Service.cs
Agent B → Service.cs
Agent C → Service.cs
```

when all agents modify the same checkout.

A safer model is:

```text
main
├── worktree-agent-auth
├── worktree-agent-tests
├── worktree-agent-db
└── worktree-agent-docs
```

Each agent gets its own:

- Git worktree,
    
- branch,
    
- container,
    
- VM,
    
- sandbox.
    

Changes can later be reviewed and merged.

Git therefore becomes more than version control.

It becomes a transactional isolation layer for autonomous workers.

## 11. Failure Containment

Isolation also limits the blast radius of agent mistakes.

A safe workflow looks like:

```text
Agent
  ↓
isolated environment
  ↓
tests
  ↓
review
  ↓
merge
```

Instead of:

```text
many agents
    ↓
shared workspace
    ↓
main branch
```

Multi-agent development therefore needs many ideas already familiar from distributed systems:

- isolation,
    
- retries,
    
- idempotency,
    
- ownership,
    
- conflict resolution,
    
- validation,
    
- rollback.
    

## 12. Specialized Agents

Repositories may increasingly define reusable agents such as:

```text
architecture-agent
security-agent
database-agent
performance-agent
test-agent
migration-agent
documentation-agent
```

Each can have dedicated instructions and skills.

For example:

```text
security-agent

- never modify production code
- inspect authentication and authorization
- inspect secret handling
- inspect dependency vulnerabilities
- return findings with severity
```

or:

```text
performance-agent

- inspect allocations
- inspect database round trips
- inspect unnecessary abstractions
- benchmark before proposing changes
```

This avoids repeatedly explaining domain-specific expectations in every prompt.

## 13. Skills as Agent Capabilities

Agents can also load reusable skills.

A skill may contain:

- instructions,
    
- scripts,
    
- examples,
    
- domain knowledge,
    
- validation procedures,
    
- tool usage conventions.
    

This creates a useful separation:

```text
Agent = role
Skill = capability
Task = current objective
```

For example:

```text
Database Agent
+
PostgreSQL optimization skill
+
migration task
```

This makes the agent system more composable.

## 14. Heterogeneous Agent Teams

A multi-agent system does not require identical models.

A possible system could use:

```text
Orchestrator
   |
   ├── strong reasoning model → architecture
   ├── coding model → implementation
   ├── large-context model → repository analysis
   ├── cheap model → repetitive transformations
   └── deterministic tools → tests/static analysis
```

This may be economically more efficient than running the strongest available model for every task.

It creates a new optimization problem:

> Which model should handle which kind of work?

The best agent may not be the best worker for every subtask.

## 15. Compute Scheduling

Multi-agent systems create another important problem: cost.

One agent means approximately:

```text
one context
one reasoning loop
one tool stream
```

Ten agents may mean:

```text
10 contexts
10 reasoning loops
10 environments
+ orchestration
+ synthesis
+ validation
```

Parallelism can reduce wall-clock time while dramatically increasing total compute.

Therefore the system needs a scheduler.

Conceptually:

```text
if task.is_simple:
    run_single_agent()

elif task.is_parallelizable:
    spawn_parallel_workers()

elif task.is_ambiguous:
    spawn_independent_explorers()

elif task.is_high_risk:
    spawn_implementer()
    spawn_independent_reviewers()
```

The interesting optimization question becomes:

> Is additional compute worth purchasing for this task?

## 16. Adaptive Agent Count

The number of agents does not need to be fixed.

A system may begin with one agent.

If uncertainty remains high:

```text
1 agent
  ↓
uncertain result
  ↓
spawn 3 investigators
```

If investigators disagree:

```text
3 hypotheses
  ↓
spawn verifier
```

If verification still fails:

```text
spawn additional specialist
```

This resembles adaptive search.

The system increases compute only when confidence is insufficient.

## 17. Asynchronous Agent Workforce

Agents also do not need to operate interactively.

A future development workflow can look like:

```text
GitHub / Jira / monitoring
          ↓
      task queue
          ↓
    agent scheduler
     /    |    \
Agent A Agent B Agent C
   ↓       ↓       ↓
  PR     report    fix
```

The developer does not necessarily watch agents while they work.

Instead, the developer may begin the day with:

```text
3 prepared PRs
2 bug analyses
1 failed task
4 review findings
```

The interaction becomes similar to managing a development team.

## 18. Humans Become Orchestrators

The developer's role moves gradually from direct implementation toward orchestration.

Instead of:

```text
write this code
```

the work becomes:

```text
define the problem
define constraints
choose exploration strategy
decide what can run in parallel
choose required reviewers
evaluate competing solutions
approve integration
```

This resembles the work of a technical lead more than the traditional work of an individual contributor.

The difference is that the "team" can be created on demand.

## 19. A Possible End-to-End Workflow

A mature workflow may look like this:

```text
                   HUMAN
                     │
          define problem / constraints
                     │
              planning agent
                     │
          ┌──────────┴──────────┐
          │                     │
     exploration          implementation
          │                     │
    ┌─────┼─────┐          orchestrator
    │     │     │          /   |   \
   A      B     C          D    E    F
    │     │     │          │    │    │
    └─────┼─────┘          └────┼────┘
          │                     │
      synthesis             integration
          └──────────┬──────────┘
                     │
                reviewer team
            ┌────────┼────────┐
         security architecture tests
            └────────┼────────┘
                     │
                   HUMAN
                     │
                   merge
```

Different stages use different forms of multi-agent collaboration.

Exploration favors independence.

Implementation favors decomposition.

Review favors specialization and separation of responsibility.

## 20. Multi-Agent Development as a New Scaling Dimension

Historically, model capability was increased through:

```text
larger model
better training
more context
better tools
```

Multi-agent systems introduce another dimension:

```text
more agents
```

Instead of:

```text
one extremely capable agent
```

we may sometimes prefer:

```text
many moderately capable agents
+
good orchestration
+
verification
```

For some problems:

```text
1 × expensive model
```

may be worse than:

```text
10 × cheaper model
+
independent exploration
+
voting
+
review
+
synthesis
```

The optimum is not yet obvious.

This resembles earlier changes in computing:

```text
single CPU
   ↓
multicore
   ↓
distributed systems
```

except that the workers are not deterministic processors.

They are autonomous reasoning systems.

## 21. Multi-Agent Development Is a Systems Problem

Once multiple agents become involved, the core difficulty changes.

The challenge is no longer simply:

> Can the model write good code?

It becomes:

> Can we build a reliable system in which many imperfect reasoning agents cooperate effectively?

This introduces questions such as:

- How should tasks be decomposed?
    
- How much context should be shared?
    
- When should agents work independently?
    
- How are conflicting conclusions resolved?
    
- Which agent is allowed to modify which files?
    
- How are failures detected?
    
- How are results validated?
    
- How much compute should be allocated?
    
- Which model should handle each task?
    
- When should a human intervene?
    

The problem therefore increasingly resembles distributed systems and organizational design rather than classical IDE assistance.

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

**an autonomous software worker that can be created, specialized, isolated, coordinated, reviewed, and discarded on demand.**
---

## Relationship to the Knowledge Graph

- **[[LLMs as a Code Review Team]]**: Implementing multi-agent reviewer teams with distinct personas and adversarial verification goals.
- **[[Introduction to Workflow Orchestration]]**: State machine orchestrators and message passing for managing multi-agent tasks.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Programmatic harnesses that coordinate subagent execution and isolated workspaces.
- **[[Agent Deployment and Execution Models]]**: The operational runtime topologies for hosting and executing multiple collaborating agents.
- **[[Exploring Agent Harnesses]]**: Comparing multi-agent harnesses against single-agent interactive workflows.
