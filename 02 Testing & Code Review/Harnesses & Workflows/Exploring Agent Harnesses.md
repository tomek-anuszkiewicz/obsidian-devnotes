---
title: Exploring Agent Harnesses
tags:
  - agentic-harness
  - ai-agents
  - software-engineering
  - runtime-environment
  - tooling
  - sandboxing
aliases:
  - Agent Harness Architecture
  - Agent Execution Environments
  - The Operating Environment for AI Agents
  - From Model to Agent Runtime
---

When working with modern AI systems, it is useful to stop thinking only in terms of **models**.

> For detailed engineering workflows, the self-healing feedback loop, and custom harness implementation, see: [[Agentic Coding Harness and Controlled Development Workflows]].

A model such as GPT, Claude, or Gemini is only one component of a larger system. What increasingly determines the practical capabilities of an AI agent is the **agent harness** around the model.

The harness defines how the model receives context, what tools it can use, how long it can work, whether it can operate in a loop, how it verifies its own work, and how it interacts with external systems.

A simplified view looks like this:

```text
Task
 ↓
Agent Harness
 ├── instructions
 ├── skills
 ├── project context
 ├── memory / RAG
 ├── filesystem
 ├── terminal
 ├── browser
 ├── MCP servers
 ├── external APIs
 ├── tests / verification
 └── agent loop
        ↓
      Model
```

The model is therefore becoming increasingly interchangeable. The same underlying task can potentially be executed using Claude, GPT, Gemini, or another model while keeping much of the surrounding infrastructure unchanged.

## What an Agent Harness Provides

A useful agent environment may provide several layers.

### Instructions

Persistent rules defining how the agent should work.

Examples include:

- coding conventions,
    
- architectural rules,
    
- review requirements,
    
- security constraints,
    
- preferred workflows,
    
- project-specific assumptions.
    

These may live in files such as `AGENTS.md`, `CLAUDE.md`, project rules, system prompts, or equivalent configuration.

### Skills

Skills package reusable procedures or domain knowledge.

Instead of repeatedly explaining a workflow, we can define something conceptually similar to:

```text
investigate-production-error
review-pull-request
implement-api-endpoint
analyze-regression
prepare-release
summarize-meeting
```

A skill may contain instructions, examples, scripts, references, or tool configuration.

This allows the agent environment to gradually accumulate organizational knowledge.

Storing these playbooks directly within the repository (such as in `.agents/skills/`) turns dynamic agent workflows into version-controlled engineering assets. When engineers encounter novel edge cases, updating the skill file permanently upgrades the agent's baseline capability across the team.

### Context

The agent may receive context from many sources:

- the current repository,
    
- documentation,
    
- architecture notes,
    
- issue trackers,
    
- previous conversations,
    
- logs,
    
- monitoring systems,
    
- meeting transcripts,
    
- databases,
    
- personal or organizational knowledge bases.
    

The quality of context may eventually matter almost as much as the model itself.

Dumping whole repositories into the prompt burns token budget and degrades attention. An effective harness manages context dynamically: pruning AST symbol trees, retrieving targeted architectural decision records (ADRs), and compacting execution history so critical error traces and diffs remain visible while redundant tool noise is stripped away.

### Tools

Agents can increasingly interact with the environment rather than merely generate text.

Typical tools include:

- filesystem access,
    
- shell commands,
    
- Git,
    
- compilers,
    
- tests,
    
- browsers,
    
- databases,
    
- APIs,
    
- ticket systems,
    
- observability platforms.
    

MCP is becoming one important mechanism for exposing such capabilities to agents in a relatively standardized way.

### Agent Loop

The most important difference between a chatbot and an agent is often the ability to continue working.

Instead of:

```text
question → answer
```

the process becomes:

```text
understand
↓
plan
↓
act
↓
inspect result
↓
verify
↓
find problems
↓
modify approach
↓
act again
```

This loop may continue until the task succeeds, a stopping condition is reached, or human input is required.

The ability to run this loop reliably is one of the most important properties to investigate when comparing agent environments.

### Verification Layer

A production harness cannot treat probabilistic model output as working code. Instead of trusting raw text or conversational self-assessment, it grounds the agent using deterministic local tooling:

- Running language compilers and static typecheckers (`tsc`, `cargo check`, `mypy`).
- Executing unit and integration test suites against modified code.
- Running linters and formatting tools (`eslint`, `ruff`, `prettier`).
- Analyzing mutation coverage or failing reproduction tests to ensure new tests actually fail when the bug is present.

### Sandboxing and Security Boundaries

Allowing an autonomous model to execute arbitrary shell commands introduces immediate operational risk. A robust harness enforces strict execution guardrails:

- Ephemeral execution environments using containers (Docker, Podman) or system namespaces (chroot, cgroups).
- Scoped filesystem permissions, keeping sensitive system paths read-only while mounting the working tree as read-write.
- Credential isolation by stripping secrets, production tokens, and `.env` files from the agent's accessible environment.
- Command gating or interactive confirmation before executing destructive operations (`rm -rf`, `git push --force`, or schema drops).

---

# Current Families of Agent Environments

There are already several overlapping categories.

## Terminal-first Agents

Examples include:

- Claude Code
    
- Codex CLI
    
- Gemini CLI
    
- GitHub Copilot CLI
    
- Aider
    
- OpenHands CLI
    

These environments are naturally suited to software engineering because the terminal already exposes an enormous amount of functionality.

A terminal agent can often:

```text
inspect repository
→ search code
→ modify files
→ run compiler
→ run tests
→ inspect failures
→ modify implementation
→ run tests again
→ commit changes
```

This makes the command line a surprisingly powerful universal interface for agents.

Terminal agents run with near-zero UI overhead, plug directly into existing shell aliases and SSH sessions, and have native access to compilers, debuggers, and local package caches without an intervening abstraction layer.

## IDE-based Agents

Examples include:

- VS Code with GitHub Copilot
    
- VS Code with Claude or Codex integrations
    
- Cursor
    
- Cline
    
- Roo Code
    
- Kilo Code
    
- Antigravity
    

The IDE becomes not merely an editor with AI autocomplete but increasingly an **agent control environment**.

It can provide:

- repository context,
    
- terminals,
    
- diffs,
    
- code navigation,
    
- multiple agent sessions,
    
- human review,
    
- local and remote execution.
    

This may lead to IDEs becoming interfaces for supervising teams of agents rather than primarily tools for manually editing code.

In this setup, the IDE acts as a supervisory cockpit. The developer reviews side-by-side diffs, monitors background terminal runs, and approves tool execution boundaries while the agent navigates the codebase using the Language Server Protocol (LSP) and AST indexers.

## Cloud Coding Agents

Another model is delegation.

```text
issue
↓
cloud agent
↓
clone repository
↓
implement change
↓
run tests
↓
create commit
↓
prepare pull request
```

Examples include systems such as:

- Codex cloud tasks,
    
- GitHub coding agents,
    
- Cursor cloud agents,
    
- Devin.
    

This model is particularly interesting when tasks take tens of minutes or hours and do not require constant human interaction.

The human becomes more of a task author and reviewer than an interactive pair programmer.

## Agent Platforms

Tools such as OpenHands and similar systems expose more of the agent architecture itself.

They can be useful for experimenting with:

- alternative models,
    
- tool definitions,
    
- custom agent loops,
    
- context management,
    
- subagents,
    
- skills,
    
- orchestration.
    

These tools may be more useful when the goal is not simply to use an agent but to understand and modify how agents operate.

---

# The Model Is Only One Variable

A useful way to think about the emerging architecture is:

```text
                  Agent System

        Instructions / Policies
                  +
                Skills
                  +
             Context / RAG
                  +
                 MCP
                  +
          Tools / APIs / CLI
                  +
              Agent Loop
                  +
          Verification Layer
                  ↓
          ┌────────────────┐
          │     Model      │
          │ GPT / Claude   │
          │ Gemini / etc.  │
          └────────────────┘
```

This changes how AI systems should be compared.

Instead of asking only:

> Which model is best?

we can ask:

- Which harness manages context best?
    
- Which one can work autonomously for the longest time?
    
- Which one recovers best from mistakes?
    
- Which one has the best tool ecosystem?
    
- Which one supports MCP well?
    
- Which one supports reusable skills?
    
- Which one allows custom instructions?
    
- Which one can delegate to subagents?
    
- Which one verifies its work effectively?
    
- Which one provides good human supervision?
    
- How easily can the underlying model be replaced?
    

A weaker model inside a very good harness may sometimes outperform a stronger model operating with poor tools and limited context.

### Evaluate prompt changes within a recorded configuration

Even when the harness is fixed, the useful amount of prompt guidance can change as the repository gains reviewed implementations. An instruction that originally had to explain a design may later be replaced by a short reference to real code. Compare those prompts with the model, harness settings, available tools, and starting code held fixed. Repeat the comparison after a model upgrade or a substantial change to the examples rather than assuming the old prompt remains necessary.

Record what the harness actually loads. A short user prompt may be accompanied by repository instructions, skills, memory, and automatically retrieved code. If those inputs vary between trials, the result does not isolate the prompt change. An agent that prepares a candidate prompt may use old conversations and the final implementation, while the session testing that prompt needs an independent starting environment without access to the previous answer. [[How Much Guidance Does a Coding Agent Need]] develops this experiment while keeping prompt optimization as the main question.

---

# Commercial "Work OS" vs. The In-Repository Harness

The market frequently promotes generic enterprise **"Agentic Work OS"** platforms: drag-and-drop SaaS tools, high-level dashboards, and conversational layers built over issue trackers.

### The Abstraction Penalty for Software Engineering

When applied to core software development and systems engineering, generic SaaS wrappers break down quickly:

- **Lowest Common Denominator**: Built for broad administrative tasks, they are blind to the mechanics of software engineering: compiler targets, AST navigation, memory constraints, and local thread concurrency.
- **Debugging the Framework**: Engineers spend more time debugging the orchestration framework's idiosyncratic JSON schemas, complex UI wrappers, and brittle cloud integrations than writing code.
- **Absence of Local Verification**: Generic platforms rely on conversational consensus between multiple models rather than binding validation to local compilers, linters, and unit test suites.

### The In-Repository Approach

High-velocity engineering teams avoid generic SaaS wrappers in favor of a **tailored, repository-native harness**:

- **Version-Controlled Instructions**: Plain Markdown policies (`AGENTS.md`, `.cursorrules`) that live alongside the codebase and evolve through standard Git workflows.
- **Native Tool Integration**: Direct access to local compilers, test runners, and static analyzers via the shell or standard MCP servers.
- **In-Tree Procedural Skills**: Reusable operational runbooks and scripts stored inside `.agents/skills/`, maintained and reviewed just like production code.
- **Zero Overhead**: Fully model-agnostic, low-latency, and directly aligned with the engineer's existing local toolchain.

An effective agent harness supports the working cadence of the engineer driving it while preserving the requirements of the organization and project. One engineer may want to discuss the design before editing; another may start with a failing test or a small experiment. Those approaches can coexist within shared architectural boundaries and verification requirements.

### Shared requirements and personal working styles

A company can maintain a common harness without giving every developer an identical interaction model. Separate the decisions by who owns them:

| Level | Shared requirements or personal choices | Who can change them |
| --- | --- | --- |
| Organization | Allowed model services, data access, tool permissions, spending limits, and required approvals. | The owners of those policies through the organization's change process. |
| Team and project | Architectural boundaries, required checks, review expectations, and reusable task workflows. | The responsible team through review, within organizational requirements. |
| Individual | Explanation depth, input method, plan presentation, and whether exploration starts with discussion, a test, or a prototype. | The developer, within the shared requirements. |

The useful boundary is whether a preference changes obligations for other people or systems. Asking the agent for shorter explanations is usually personal. Skipping a required compatibility check affects everyone who depends on the resulting change. A preference for autonomous execution cannot grant deployment access or remove a required approval.

Make that distinction explicit in the configuration: identify mandatory constraints, overridable defaults, and personal settings. Keep shared rules and skills under review, and document which local settings the harness actually loads. A file called `user.local.md` has no effect unless the harness reads it. A personal setting that conflicts with a mandatory requirement should produce a visible conflict instead of silently weakening that requirement.

Instruction precedence alone does not enforce these boundaries. Service permissions must restrict operations, managed configuration must constrain access to approved services, and repository controls must require the agreed checks before merging. Local instructions can explain those requirements, but changing a prompt must not bypass them (see [[Security Boundaries for Agents, RAG, and MCP]]).

Developers still need to agree on where the boundaries belong. Discuss concrete cases: can a teammate take over the task, can the required verification be repeated, and does a local customization change shared code conventions? Use those consequences to decide what needs a common rule. Keep the reason and owner of each shared requirement visible so disagreements can lead to a reviewed change rather than competing private instructions.

A successful personal workflow can become a shared skill after teammates try it on relevant tasks. Sharing that procedure does not require adopting its author's entire interaction style (see [[The Conductor Pattern for High-Bandwidth Engineering#6. Agree on shared rules when several engineers use agents|shared rules and reusable workflows]]).

There is a maintenance trade-off. Independent harnesses multiply configuration, support, and verification work; an overly rigid common setup can obstruct useful ways of thinking and experimenting. A maintained common base with documented customization points is a practical starting point. Whether that base runs locally or on a shared platform is a separate deployment decision (see [[Agent Deployment and Execution Models]]).

---

# A Useful Exploration Strategy

Rather than trying to choose a single winner immediately, it may be useful to treat the current ecosystem as an experimental field.

A first comparison could include:

```text
Claude Code
Codex CLI
Gemini CLI
```

These provide relatively comparable terminal-oriented agent environments.

A second comparison could examine richer environments:

```text
VS Code + Copilot
Cursor
Cline / Roo / Kilo
Antigravity
OpenHands
```

The same tasks could be given to each environment.

For example:

```text
Investigate this bug.

Determine:
- whether it is reproducible,
- where it was introduced,
- which commit is likely responsible,
- whether similar bugs exist,
- propose a fix,
- implement it,
- run tests,
- prepare a summary.
```

We could then compare not merely whether the final answer was correct, but the entire behavior of the agent.

Key behavioral signals to monitor include:
- Whether the agent writes a minimal reproducing test before modifying code, or attempts blind speculative edits.
- Token consumption and search efficiency when locating the relevant call paths.
- Recovery mechanics when the build breaks or a test throws an assertion error.
- Diff hygiene: whether the resulting patch is focused and minimal, or polluted with unrelated formatting changes.

---

# What to Evaluate

The exploration should therefore focus on several dimensions.

### Context handling

How much of the repository does the agent understand?

Can it locate relevant architecture documentation?

Can it use external knowledge without overwhelming the context window?

### Autonomy

How many meaningful steps can it perform before human intervention is required?

Can it independently discover the next necessary action?

### Reliability

Does it verify assumptions?

Does it run tests?

Does it notice when its solution does not work?

### Recovery

What happens when a command fails?

Does the agent understand the failure and change strategy, or does it repeatedly attempt the same action?

### Tool use

How effectively does the agent use:

```text
Git
shell
tests
browser
databases
MCP
APIs
```

### Skills and persistent knowledge

Can we gradually teach the environment how our organization works?

Can knowledge accumulated from one task improve future tasks?

### Observability

Can we understand what the agent did?

Can we inspect:

- actions,
    
- tool calls,
    
- diffs,
    
- intermediate results,
    
- decisions,
    
- costs?
    

### Human control

Can the agent operate autonomously without becoming difficult to supervise?

Ideally the system should support both:

```text
high autonomy
```

and

```text
clear checkpoints for human review
```

---

# From AI Assistant to Agent Runtime

The broader transition may therefore be described as:

```text
autocomplete
      ↓
chat assistant
      ↓
tool-using assistant
      ↓
coding agent
      ↓
agent runtime
      ↓
multi-agent environment
```

The interesting question is no longer merely how well an LLM can write code.

The more important question may become:

> What environment allows a model to perform useful work reliably over long sequences of actions?

This includes the model, but also everything around it:

- context,
    
- tools,
    
- skills,
    
- memory,
    
- orchestration,
    
- verification,
    
- permissions,
    
- human supervision.
    

The emerging competition between Claude Code, Codex, Gemini CLI, Cursor, VS Code, Antigravity, OpenHands, and similar systems can therefore be viewed as competition over **how to build the operating environment for AI agents**.

That is a useful starting point for further exploration.

## Related notes

- **[[Agentic Coding Harness and Controlled Development Workflows]]** — Practical orchestration, vertical slices, and constraints enforced by the harness.
- **[[Building Determinism from Unpredictable Models]]** — State graphs, sandboxed tool dispatch, and verification gates.
- **[[Agent Deployment and Execution Models]]** — Local, cloud, and hybrid infrastructure models for agent runtimes.
- **[[Dynamic Model Routing and Inference Gateways]]** — Routing requests between local and remote model engines.
- **[[Multi-Agent Software Development]]** — Coordinated specialist agents collaborating within a shared execution harness.
