---
title: Agentic Software Development Workflows
tags:
  - ai-agents
  - agentic-workflows
  - software-engineering
  - developer-experience
  - automation
  - workflow
aliases:
  - Coding Agent Workflows
  - Granularity of Agent Work
  - Agentic Development Lifecycles
---

AI coding agents can work with a repository in very different ways, operating most reliably when guided by a structured [[Agentic Coding Harness and Controlled Development Workflows|agentic coding harness]]. The important distinction is not only **which agent or tool is used**, but **what workflow governs its behavior**.

The same coding agent can act as a fast code generator, a test-driven implementer, a planner, a reviewer (operating within [[LLMs as a Code Review Team|a multi-model code review team]]), a refactoring engine, or a semi-autonomous developer.

A useful way to think about agentic software development is therefore as a collection of composable workflows, particularly when [[Developing Features with AI Coding Agents|developing features with AI coding agents]].

---

## 1. Vibe Coding

#vibe_coding 

The simplest workflow is:

**Prompt → Code → Run → Fix**

The developer describes what they want in natural language, and the agent immediately starts modifying the repository.

Example:

> Add authentication and password reset support.

The agent explores the codebase, implements a solution, runs the application or tests, and fixes obvious problems.

This approach is useful for:

- prototypes,
    
- experiments,
    
- small applications,
    
- isolated changes,
    
- learning and exploration.
    

Its main weakness is that missing requirements are silently filled in by the model, reinforcing why [[Testing in the Model, Agent, LLM Era|testing in the model era]] demands rigid, deterministic oracles rather than loose prompt expectations.

The agent may decide:

- how the architecture should work,
    
- what edge cases matter,
    
- which abstractions to introduce,
    
- which behavior the business intended.
    

For larger systems, this creates a risk of producing a technically valid implementation of the wrong problem.

---

## 2. Feature-by-Feature Development

A safer production-oriented workflow is:

**Feature → Implementation → Verification → PR**

Instead of asking the agent to build a large subsystem, work is divided into relatively small features.

Example:

> Allow an unpaid order to be cancelled.

The agent:

1. explores the affected code,
    
2. implements the feature,
    
3. modifies or adds tests,
    
4. runs validation,
    
5. produces a small diff or pull request.
    

Then another feature is handled separately.

This has several advantages:

- smaller context,
    
- easier review,
    
- easier rollback,
    
- fewer unrelated changes,
    
- simpler debugging,
    
- clearer history.
    

For normal software development, this is likely a good default unit of work for an agent.

---

## 3. Issue-Driven Development

Feature-driven development can be made more formal by treating a ticket or issue as the contract.

Example:

```text
Problem:
A paid order can currently be cancelled.

Expected:
Paid orders must not be cancellable.

Acceptance criteria:
- API returns 409.
- Order state remains unchanged.
- Audit event is recorded.
```

The workflow becomes:

**Issue → Agent → Verification → PR**

This is especially interesting because a backlog can effectively become a **task queue for coding agents**.

Instead of developers manually starting every coding session, suitable tickets may eventually be assigned directly to agents.

The quality of the issue then becomes much more important.

Poorly specified tickets produce poorly constrained agent behavior.

---

## 4. Plan-Driven Development

For larger changes, the agent should often be prevented from modifying code immediately.

The workflow becomes:

**Explore → Plan → Review → Implement**

Example instruction:

```text
Study the repository and identify all components affected by this change.

Prepare an implementation plan.

Do not modify the code yet.
```

The agent may return:

```text
1. Extend the domain model.
2. Modify CancelOrderHandler.
3. Update API contracts.
4. Add database migration.
5. Add integration tests.
6. Update documentation.
```

Only after the plan is reviewed does implementation begin.

This approach is particularly useful for:

- cross-cutting changes,
    
- architectural changes,
    
- migrations,
    
- unfamiliar repositories,
    
- large refactors,
    
- changes involving multiple modules.
    

Planning separates **understanding the problem** from **executing the change**.

---

## 5. Spec-Driven Development

#sdd

Spec-driven development pushes this idea further.

Instead of going directly from request to implementation, the workflow becomes:

**Request → Requirements → Design → Tasks → Implementation**

A specification may contain several layers.

### Requirements

Example:

```text
WHEN an authenticated user cancels an unpaid order
THE SYSTEM SHALL change its state to Cancelled.
```

### Design

The agent determines the affected components and expected architecture.

Example:

```text
CancelOrderCommand
    ↓
CancelOrderHandler
    ↓
Order Aggregate
    ↓
OrderCancelled Event
```

### Tasks

The specification is decomposed into concrete implementation steps.

Example:

```text
[ ] Extend domain model
[ ] Add command handler
[ ] Add endpoint
[ ] Add unit tests
[ ] Add integration tests
```

### Implementation

Only after these artifacts exist does the agent modify production code.

This reduces the probability that implementation decisions silently redefine the requirement.

Spec-driven development is especially useful when the feature is large enough that the intended behavior should survive beyond a single chat session.

---

## 6. Test-Driven Agent Development

Traditional TDD becomes especially interesting when coding agents are involved.

The workflow is:

**Requirement → Test → Fail → Implementation → Pass → Refactor**

The first task given to the agent may be:

```text
Write tests describing the requested behavior.

Run them and verify that they fail.

Do not modify production code yet.
```

A human can review the tests before implementation begins.

Then the agent receives the next instruction:

```text
Implement the smallest change that makes the tests pass.
```

This separates two important activities:

1. interpreting the requirement,
    
2. implementing the solution.
    

If the agent misunderstood the feature, the problem becomes visible in the tests before large amounts of implementation code are generated.

A particularly strong workflow is therefore:

**Specification → Acceptance Tests → Human Review → Implementation**

The tests become an executable contract between the human and the agent.

---

## 7. Verification-Driven Development

Agents should not be expected to produce correct code in a single generation.

Instead, they should operate inside a feedback loop.

A typical workflow might be:

```text
Implement
    ↓
Build
    ↓
Unit Tests
    ↓
Integration Tests
    ↓
Static Analysis
    ↓
Architecture Checks
    ↓
Agent Review
    ↓
Fix
    ↓
Repeat
```

The agent does not stop because it believes the implementation is correct.

It stops because observable checks confirm that predefined conditions have been satisfied.

This leads to an important principle of agentic development:

> Do not depend on the quality of a single generation. Build an environment in which the agent can detect and correct its own mistakes.

The better the feedback loop, the more autonomy can safely be delegated.

---

## 8. Reviewer and Adversarial Workflows

Implementation and review do not need to be performed by the same agent.

A multi-agent workflow may look like:

```text
Implementation Agent
        ↓
Code Review Agent
        ↓
Adversarial Agent
        ↓
Implementation Agent fixes issues
```

Different agents can have deliberately different goals.

For example, a reviewer may receive:

```text
Assume the implementation contains defects.

Search specifically for:
- race conditions,
- security problems,
- missing edge cases,
- architecture violations,
- incorrect error handling,
- performance regressions.
```

This is useful because an agent reviewing its own work may reproduce the assumptions that produced the original implementation.

Independent agents can provide different perspectives.

---

## 9. Refactor-Driven Development

#refactor

Some agent tasks are not about adding behavior but transforming the implementation while preserving behavior.

The task can therefore be expressed through invariants.

Example:

```text
Replace MediatR with direct handler invocation.

Constraints:
- API behavior must remain unchanged.
- Database schema must remain unchanged.
- Public contracts must remain unchanged.
- Existing tests must continue to pass.
```

The workflow may be incremental:

```text
Module A
↓
Refactor
↓
Tests
↓
Commit

Module B
↓
Refactor
↓
Tests
↓
Commit
```

This approach is suitable for:

- library migrations,
    
- framework migrations,
    
- architecture cleanup,
    
- performance optimization,
    
- large-scale renaming,
    
- API transitions.
    

The key concept is:

**Transformation under preserved invariants.**

---

## 10. Goal-Driven Development

An even more autonomous workflow describes the desired outcome rather than the implementation.

Example:

> `/orders/search` must respond within 100 ms at p99 under the defined test load.

The agent may then:

- profile the endpoint,
    
- inspect database queries,
    
- introduce benchmarks,
    
- modify indexes,
    
- rewrite SQL,
    
- remove allocations,
    
- change caching,
    
- measure the result,
    
- repeat the experiment.
    

The workflow becomes:

**Goal → Measure → Change → Measure → Iterate**

In this model, code is only one possible instrument for achieving an externally measurable objective.

This is particularly promising for:

- performance optimization,
    
- cost reduction,
    
- reliability improvement,
    
- flaky-test reduction,
    
- security hardening,
    
- build-time optimization.
    

---

## 11. Investigation-Driven Development

Sometimes the task should begin with investigation rather than implementation.

Example:

> Production started throwing this exception yesterday. Find out why.

The workflow becomes:

```text
Incident
↓
Collect Evidence
↓
Inspect Logs and Telemetry
↓
Compare with Recent Repository Changes
↓
Form Hypotheses
↓
Test Hypotheses
↓
Propose Fix
↓
Implement
```

This is different from normal feature development because the agent does not initially know what code needs to change.

Its first job is to reduce uncertainty.

This pattern is useful for:

- bugs,
    
- production incidents,
    
- regressions,
    
- performance degradation,
    
- unexpected business metrics.
	
- check for private data in logs

---

## 12. Exploration Before Modification

A general rule for larger repositories is that agents should often have a dedicated exploration phase.

For example:

```text
Find:
- relevant modules,
- entry points,
- existing implementations,
- tests,
- architectural rules,
- similar features.

Do not modify code.
```

Only afterward should the agent propose the change.

This avoids a common failure mode where the model encounters one plausible implementation location and starts editing before understanding the wider system.

For agentic work, repository understanding should often be treated as a first-class task.

---

# Granularity of Agent Work

Another important dimension is the size of the unit delegated to the agent.

There is a continuum:

```text
Autocomplete
    ↓
Single Function
    ↓
Single Change
    ↓
Feature
    ↓
Issue
    ↓
Pull Request
    ↓
Epic
    ↓
Specification
    ↓
Product Goal
```

As the delegated unit becomes larger, stronger controls are needed.

Large autonomous tasks generally require more:

- specification,
    
- planning,
    
- testing,
    
- observability,
    
- architecture rules,
    
- verification,
    
- checkpoints,
    
- review.
    

The correct level of autonomy therefore depends heavily on the quality of the surrounding environment.

---

# A Production-Oriented Agent Workflow

Many of the techniques above can be composed.

A mature workflow could look like:

```text
Business Request
      ↓
Clarify Requirements
      ↓
Write Specification
      ↓
Explore Repository
      ↓
Prepare Implementation Plan
      ↓
Generate Acceptance Tests
      ↓
Human Review
      ↓
Implement Small Task
      ↓
Build + Tests + Static Checks
      ↓
Agent Self-Review
      ↓
Independent Agent Review
      ↓
Commit
      ↓
Next Task
      ↓
Pull Request
      ↓
Human Review
```

This may look heavier than vibe coding, but automation removes much of the cost.

The important change is that software engineering discipline does not disappear when agents write the code.

Instead, many previously human-driven process steps can themselves become automated.

---

# These Workflows Are Complementary

These approaches should not necessarily be treated as competing methodologies.

They describe different dimensions of the development process.

**Spec-driven development** defines what should exist.

**Plan-driven development** determines how the work should be decomposed.

**Test-driven development** turns expected behavior into executable checks.

**Feature- or issue-driven development** defines the unit of work.

**Verification-driven development** determines how correctness is demonstrated.

**Reviewer and adversarial workflows** provide independent criticism.

**Refactor-driven development** performs transformations while preserving invariants.

**Goal-driven development** allows the agent to search for solutions to measurable outcomes.

A practical agent workflow may therefore combine several of them.

For example:

```text
Issue
↓
Specification
↓
Repository Exploration
↓
Plan
↓
Acceptance Tests
↓
Implementation
↓
Verification Loop
↓
Independent Review
↓
PR
```

---


# Agentic Execution Environments

The workflows described above answer the question:

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

## Coding Environments

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

## General Knowledge-Work Environments

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

For example:

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

## From Tools to Digital Workers

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

---

# From Coding Assistants to Software Engineering Agents

The evolution can be summarized roughly as:

```text
AI writes code
        ↓
AI implements features
        ↓
AI executes engineering tasks
        ↓
AI follows engineering processes
        ↓
AI participates in continuous software development
```

The important question is therefore gradually changing from:

> How good is the model at generating code?

to:

> How good is the development system around the model?

A mediocre generation followed by strong tests, feedback, review, and iteration may be far more valuable than an impressive one-shot generation without verification.

The most important architectural challenge in agentic software development may therefore not be code generation itself.

It may be designing the **environment, contracts, feedback loops, and boundaries within which agents work**.
---

## Relationship to the Knowledge Graph

- **[[Agentic Coding Harness and Controlled Development Workflows]]**: The architectural implementation of controlled plan-and-approval workflows and self-healing loops.
- **[[Developing Features with AI Coding Agents]]**: Tactical guide for vertical-slice implementation and freezing business acceptance tests.
- **[[Testing in the Model, Agent, LLM Era]]**: How executable test suites serve as the primary verification environment for agentic workflows.
- **[[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]]**: How review workflows enforce subtle organizational and architectural standards.
- **[[LLMs as a Code Review Team]]**: Multi-agent adversarial review teams that stress-test code before merge.
- **[[Introduction to Workflow Orchestration]]**: Explores the orchestration state machines and sandboxes required for multi-step agentic execution.
