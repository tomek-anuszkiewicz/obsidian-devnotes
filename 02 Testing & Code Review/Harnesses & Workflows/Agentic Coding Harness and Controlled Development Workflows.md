---
title: Agentic Coding Harness and Controlled Development Workflows
tags:
  - ai-agents
  - agentic-coding
  - agentic-harness
  - software-engineering
  - testing
  - llm
  - codex
aliases:
  - Agentic harness
  - Coding agent workflow
  - Controlled Development Workflows
  - SOTA Patterns for High-Assurance Agents
---

# Agentic Coding Harness and Controlled Development Workflows

> See also: [[Agent Deployment and Execution Models]], [[Building Determinism from Unpredictable Models]]

## Core idea

An **agentic harness** is the software layer that turns an LLM from a text generator into an acting agent.

The model itself fundamentally performs one operation:

> receive context → produce a response

The harness adds the operational machinery required to complete real tasks:

- a model interaction loop;
- access to files, a terminal, Git, browsers, MCP servers and APIs;
- instruction and context loading;
- state and memory management;
- permissions and sandboxing;
- retries, timeouts and stop conditions;
- test execution and result verification;
- tracing, cost monitoring and evaluation;
- optional coordination of subagents.

A useful approximation is:

> **Agent = model + harness + instructions + tools**

Codex and Claude Code are not merely models. They are ready-made coding-agent harnesses. They connect a model to a repository, tools and an execution loop.

## How the agent loop works

A typical coding session follows this cycle:

1. The user provides a goal.
2. The harness loads applicable instructions.
3. The model decides which information or action is needed next.
4. The harness reads a file, searches the repository or runs a command.
5. The result is returned to the model.
6. The model chooses the next action.
7. The loop continues until completion or a stop condition is reached.

For example, when asked to add an API endpoint, the model does not directly open files or execute `dotnet test`. It requests these actions through tools exposed by the harness. The local harness performs them and sends the results back to the model.

This distinction matters because the quality of an agent depends on more than model intelligence. Two agents using similarly capable models can perform differently because their harnesses differ in:

- context selection;
- tool descriptions;
- error handling;
- history compaction;
- permission management;
- verification strategy;
- criteria for deciding that a task is complete.

## Harness versus workflow

The harness provides the execution engine. A **workflow** tells the harness how a particular kind of work should be performed.

Examples of workflow rules:

- analyze the specification before editing code;
- prepare a plan and wait for approval;
- implement only one approved step;
- add or update tests;
- run targeted verification;
- stop after the semantic step and present the diff;
- do not push without explicit permission.

A workflow is often just a Markdown file. It does not need to be executable code when the process is primarily interpreted by an agent.

However, text instructions guide behavior rather than enforcing it technically. If an approval must be a hard gate, a programmatic orchestrator or harness must represent that approval as state and refuse to continue without it.

## A controlled plan-and-approval workflow

For complex work, begin with a planning-only instruction:

```text
Analyze SPEC.md and the repository.

Work only in planning mode:
1. List assumptions and open questions.
2. Divide the implementation into small semantic steps.
3. For each step, describe:
   - the goal,
   - likely affected files,
   - expected behavior,
   - required tests,
   - completion criteria.
4. Do not edit files.
5. Stop and wait for plan approval.
```

After reviewing the plan, authorize only a bounded step:

```text
Step 1 is approved.

Implement only Step 1:
- add or update the relevant tests;
- implement the minimal production change;
- run the specified verification;
- review the diff against SPEC.md;
- present the result and stop.

Do not begin Step 2 without explicit approval.
```

The explicit instruction to **stop** is important. “Work step by step” can still be interpreted as completing all steps sequentially in one run.

## Semantic and mechanical steps

Not every operation should require human approval.

### Semantic steps

These may change the meaning or architecture of the system and should usually require approval:

- changing a public API contract;
- changing business behavior;
- selecting module boundaries;
- introducing a database migration;
- changing the domain model;
- adding a production dependency;
- adopting a new architectural abstraction.

### Mechanical steps

These can usually run automatically within an approved semantic step:

- compiling the solution;
- running tests;
- formatting code;
- rerunning a failed test after a correction;
- examining logs;
- fixing an unambiguous compiler error.

The goal is not to approve every `dotnet test` invocation. The human should approve changes in meaning, scope and risk.

## Bounded implementation loops (The Self-Healing Loop)

An agent can work in a loop, but the loop needs explicit success and failure conditions. Instead of expecting an LLM to generate production-ready code in a single prompt, the harness runs a cyclic, self-correcting feedback loop (Actor-Critic pattern):

```text
[Task Prompt / Issue]
        │
        ▼
┌─► [Agent Coder] ──(Generates Patch)──┐
│                                       │
│                                       ▼
│                             [Deterministic Verification]
│                             - Tests (pytest, dotnet test)
│                             - Linters & Typecheck (mypy, eslint)
│                             - Build & Syntax Check
│                                       │
│                         ┌─────────────┴─────────────┐
│                      (Failed)                    (Passed)
│                         │                           │
│                         ▼                           ▼
│                  [Error Trace]             [Specialized Reviewers]
│                         │                  (Security, Architecture)
│                         │                           │
│ └─ (Iterate / Fix) ◄──────┴───────────────────────────┤
                                                      │ (All Passed)
                                                      ▼
                                            [Git Commit & Push]
```

### Key Loop Principles
* **Structured Error Feedback:** Fixers receive raw error outputs (stack traces, failed test names, line numbers) rather than vague re-prompts.
* **Hard Iteration Caps:** Enforce a maximum iteration threshold (e.g., N=3 to 5). If the agent cannot solve the issue within the budget, the loop aborts and triggers human escalation.
* **Atomic Operations:** Each cycle works in a dedicated Git worktree or branch. Failed attempts can be cleanly rolled back (`git reset --hard`).

### Success conditions

A step is complete when:

- its acceptance criteria are satisfied;
- the relevant tests pass;
- the solution builds;
- no unrelated files were changed;
- the result remains within the approved scope;
- no unresolved assumption affects correctness.

### Stop and escalation conditions

The agent should stop and ask for direction when:

- the requirement is ambiguous;
- a public contract or schema must change unexpectedly;
- work must cross an unapproved module boundary;
- the same failure remains after a bounded number of attempts;
- a test appears flaky;
- verification is blocked by unrelated existing failures;
- completing the step requires expanding its scope;
- credentials or access to a non-local environment would be required.

Without these boundaries, an agent may loop, broaden the change, weaken an assertion or modify unrelated code in an attempt to achieve a superficially successful result.

### Structure of an Escalation to Human Arbitration

When the automated loop reaches its iteration ceiling without passing all gates, it must not dump uncontextualized code on the human reviewer. It should generate an escalation artifact:

```text
[Loop Aborted at Iteration 3]
              │
              ▼
[Escalation Artifact Generation]
  ├── Summary of disagreement / failing constraint
  ├── Diff evolution across attempts
  └── 2-3 Concrete Decision Options (A / B / C)
              │
              ▼
[Draft PR with Inline Comments on GitHub]
```

Example inline PR escalation comment:

> ⚠️ **HUMAN ARBITRATION REQUIRED** (Iteration limit reached)
> 
> **Conflict Summary:**
> * Security Reviewer flagged SQL query in loop (potential N+1).
> * Coder Agent attempted batching, but encountered missing foreign key constraint in SQLite/test setup.
> 
> **Options for Developer:**
> - [ ] **Option A:** Add missing index migration and retry batch query.
> - [ ] **Option B:** Accept single-query fetch due to strict low-volume usage.
> - [ ] **Option C:** Revert module changes and revise high-level architecture.

The developer replies directly in the GitHub PR review thread, triggering a webhook that re-engages the harness with explicit human guidance.

## Runtime boundaries for the workflow

A Markdown rule can guide an agent away from destructive actions, but it cannot stop a tool call by itself. The host should scope files, credentials and commands to the approved task, and use an isolated branch or worktree when recovery matters. Preserve pre-existing changes rather than relying on a blanket reset. Review the resulting diff before accepting a semantic change. When an agent repeatedly crosses an observable boundary, turn that failure into an executable check instead of adding more detailed prose (see [[Building Determinism from Unpredictable Models]] and [[Configuring and Testing Coding Agent Capabilities]]).

## Files used to guide an agent

A practical repository can separate permanent guidance from task-specific state:

```text
repo/
├── AGENTS.md
├── README.md
├── ARCHITECTURE.md
├── ROADMAP.md
├── DIARY.md
├── .codex/
│   └── config.toml
├── .agents/
│   ├── rules/
│   │   ├── performance.md
│   │   └── security.md
│   └── skills/
├── tools/
│   ├── log_diary.py
│   └── pre_flight.py
├── docs/
│   ├── architecture/
│   └── workflows/
├── tasks/
│   └── order-cancellation/
│       ├── SPEC.md
│       ├── PLAN.md
│       └── DECISIONS.md
├── scripts/
│   ├── setup.ps1
│   ├── build.ps1
│   ├── test-module.ps1
│   ├── verify.ps1
│   └── mutation-test.ps1
├── src/
└── tests/
```

### `README.md`

Explains how to operate the project:

- required SDK and tools;
- environment setup;
- starting local dependencies;
- building and running the application;
- running tests;
- finding logs and local endpoints.

### `ARCHITECTURE.md`

Provides a short, practical map:

- modules and responsibilities;
- important directories;
- allowed dependency directions;
- integration patterns;
- where business rules, persistence and transport code belong.

For a modular monolith, it should explain module boundaries explicitly. Whenever possible, these boundaries should also be enforced with architecture tests.

### `ROADMAP.md` and active backlog pruning

Maintains the immediate plan for upcoming work. High-assurance workflows enforce active backlog pruning (see [[Active Backlog Pruning and Context Hygiene in Agentic Roadmaps]]):

- Completed items are deleted immediately from the active backlog file rather than retained with `[x]` checkmarks or strikethrough text.
- Leaving dozens of completed tasks in view degrades model attention and burns context budget on settled work.
- The moment a step is verified and committed, it is removed from `ROADMAP.md`. High-level capabilities are summarized in a brief baseline deliverables list at the top, keeping the file small and forward-looking.

### `DIARY.md` and out-of-context tooling

Because the active roadmap prunes completed work, project evolution and technical decisions must be captured in an append-only engineering diary (`DIARY.md`; see [[The Living Engineering Chronicle and Context Compaction]]).

Each entry captures four key areas:
1. Affected subsystems;
2. What changed;
3. Architectural rationale;
4. Verification results.

To prevent a growing log file from saturating the agent's context window, the agent does not open or edit `DIARY.md` directly. Instead, it uses a lightweight CLI tool:

```bash
python tools/log_diary.py \
  --subsystem "Orders" \
  --changed "Added cancellation event handler" \
  --rationale "Ensures event consistency before inventory updates" \
  --verified "./scripts/test-module.ps1 Orders"
```

The script appends formatted Markdown to disk directly without passing the historical log through the model's context window. Periodically, older entries can be summarized into architectural digests.

### `AGENTS.md`

Contains durable repository instructions that apply to most tasks:

```markdown
# Agent instructions

## Before editing

1. Read README.md and ARCHITECTURE.md.
2. Read the applicable SPEC.md and PLAN.md.
3. Inspect existing patterns in the affected module.
4. Do not implement an unapproved plan.

## Engineering rules

- Preserve modular-monolith boundaries.
- Prefer existing abstractions and generated clients.
- Do not add a production dependency without approval.
- Do not change public contracts, schemas or migrations without approval.
- Do not weaken tests merely to make them pass.
- Do not edit generated files manually.

## Workflow

- Implement only a step marked approved.
- Work on one semantic step at a time.
- Run targeted tests after changes.
- Run ./scripts/verify.ps1 before completion.
- Stop after completing the approved step.
```

Keep `AGENTS.md` concise. It should route the agent to more detailed documentation rather than duplicate all project knowledge.

More specific `AGENTS.md` files can be placed closer to individual modules when their rules differ.

### `SPEC.md`

Defines what the system must do, independently of the implementation:

```markdown
# Cancel order

An order can be cancelled only before shipment.

## Acceptance criteria

- A pending order can be cancelled.
- A shipped order cannot be cancelled.
- Cancellation records the actor and timestamp.
```

### `PLAN.md`

Describes implementation steps and their state:

```markdown
## Step 1: Domain cancellation behavior

Status: approved

### Scope

- Order.Cancel
- OrderCancelled domain event
- domain unit tests

### Out of scope

- HTTP endpoint
- database migration
- notifications

### Verification

- ./scripts/test-module.ps1 Orders -Type Unit

### Done when

- pending orders can be cancelled;
- shipped orders are rejected;
- the domain event is raised;
- all Orders domain tests pass.
```

Useful states include:

- `pending`;
- `approved`;
- `in-progress`;
- `completed`;
- `blocked`;
- `rejected`.

The `Out of scope` section is especially valuable because it prevents opportunistic expansion of the change.

### `DECISIONS.md`

Records decisions made while refining the plan, including alternatives and rationale. This prevents the agent or a later developer from reopening settled questions without context.

## Agent configuration and verification

A controlled workflow also needs scoped agent roles, concise rules, reusable skills, appropriate tool permissions and checks that run at defined points. As those parts grow, test both their selection and the hooks that invoke audits (see [[Configuring and Testing Coding Agent Capabilities]]).

## Executable architecture tests

Architecture rules should be enforced through executable test suites rather than text guidelines alone. In .NET, for instance, you can write automated tests using `NetArchTest` (or `ArchUnit` in Java) to verify that architectural boundaries remain intact:

```csharp
[Fact]
public void DomainLayer_ShouldNotHaveDependencyOn_InfrastructureLayer()
{
    var result = Types.InAssembly(DomainAssembly)
        .ShouldNot()
        .HaveDependencyOn("Orders.Infrastructure")
        .GetResult();

    Assert.True(result.IsSuccessful, "Domain must remain isolated from Infrastructure.");
}
```

Architecture tests can also enforce structural guardrails on the codebase:
- asserting that no source file in the domain exceeds a given line threshold;
- asserting that public API handlers do not swallow exceptions with empty catch blocks;
- asserting that all repository methods accept a cancellation token.

When an agent breaks an architectural boundary, the test runner fails with a clear, targeted assertion error, guiding the agent to correct itself through the standard test-fix loop.

## Stable verification commands

The repository should offer simple commands that work for humans, agents and CI:

```powershell
./scripts/setup.ps1
./scripts/build.ps1
./scripts/test-module.ps1 Orders
./scripts/verify.ps1
./scripts/mutation-test.ps1 Orders
```

Scripts should:

- run non-interactively;
- return exit code `0` on success and non-zero on failure;
- produce concise failure summaries;
- avoid modifying production code during verification;
- work from a clean checkout;
- be shared by local development and CI.

A layered strategy avoids running an expensive entire suite after every small edit:

1. run focused tests while iterating;
2. run all tests for the affected module after the step;
3. run full verification before completion;
4. run expensive mutation or end-to-end suites separately.

## Mutation testing as a separate verification pass

Mutation testing can expose weak assertions after the ordinary tests pass. Run it selectively, then have the agent analyze surviving mutations and propose tests for the business-critical gaps. The mutation engine should generate and run the variants; the agent and human reviewer decide which results deserve action (see [[Testing in the Model, Agent, LLM Era]]).

## Reproducible local environment

An agent performs best when the repository can be initialized without undocumented manual work.

Useful components for .NET include:

- `global.json` for the SDK version;
- `Directory.Packages.props` for centralized package versions;
- a local .NET tool manifest;
- `docker-compose.yml` for local infrastructure;
- deterministic test fixtures and seed data;
- setup and verification scripts;
- optionally, a Dev Container.

The ideal path from checkout to verification should be close to:

```powershell
dotnet tool restore
docker compose up -d
./scripts/setup.ps1
./scripts/verify.ps1
```

## Permissions and secrets

A local agent can potentially access credentials, local databases, Docker, GitHub, Azure or Kubernetes. It should not receive more authority than necessary.

Recommended defaults:

- restrict writes to the active workspace;
- require approval for network access and operations outside the workspace;
- use only local development services;
- do not expose production credentials;
- keep secrets in ignored local files or a secret store;
- ask before using authenticated cloud CLIs;
- never deploy or migrate a non-local environment without explicit approval.

Example instructions:

```markdown
- Never display secret values.
- Use only services defined in docker-compose.yml.
- Never run database commands against a non-local host.
- Ask before using GitHub, Azure or Kubernetes credentials.
```

Sandboxing controls what the agent can technically do. Approval policy controls when it must stop and ask before doing it. These are separate controls (see [[Security Boundaries for Agents, RAG, and MCP]]).

## Git, commits and pull requests

An agent can perform the full Git workflow if it has the required tools, network access and repository permissions:

1. create a feature branch;
2. modify code;
3. run verification;
4. stage selected changes;
5. create one or more commits;
6. push the branch;
7. open a GitHub pull request;
8. respond to review comments with further commits.

For a local agent, this commonly uses `git` and the authenticated GitHub CLI:

```bash
git switch -c feature/cancel-order
git add <explicit files>
git commit -m "feat(orders): support order cancellation"
git push -u origin feature/cancel-order
gh pr create --draft
```

Recommended initial policy:

| Operation | Policy |
| --- | --- |
| Create a local branch | automatic |
| Stage task-related files | automatic |
| Create a local commit | allowed after verification |
| Push the branch | explicit approval |
| Create a draft PR | explicit approval |
| Mark PR ready for review | human decision |
| Merge PR | human or protected process |
| Push directly to `main` | prohibited |
| Force push | prohibited unless explicitly approved |

Example `AGENTS.md` rules:

```markdown
## Git workflow

- Work only on a feature branch.
- Never commit directly to main.
- Preserve pre-existing uncommitted changes.
- Stage files explicitly; do not use `git add .`.
- Create small commits grouped by purpose.
- Run ./scripts/verify.ps1 before the final commit.
- Do not push without explicit approval.
- Create pull requests as drafts.
- Never merge a pull request.
- Never bypass branch protection or required CI.
```

For larger changes, multiple logical commits can make review easier:

```text
test(orders): cover cancellation rules
feat(orders): implement cancellation behavior
feat(api): expose order cancellation endpoint
docs(orders): document cancellation workflow
```

A commit should represent a coherent, reviewable and preferably verified unit—not every tiny correction made during the loop.

Before staging, inspect the full diff and group changes by the reason they were made. If a task changed an agent skill and also made an independent change to application code or a note, stage and commit those groups separately. That lets a reviewer understand or revert the skill change without taking the other change with it. Keep files together when they form one dependent change, such as a skill and the test that verifies its behavior. If one file contains unrelated edits, stage the relevant hunks separately rather than treating the file as an indivisible unit.

## Pull requests as an additional approval gate

A useful development path is:

1. specification approved;
2. implementation plan approved;
3. one bounded step implemented;
4. tests and diff reviewed locally;
5. commit and push approved;
6. draft PR created;
7. CI and independent review executed;
8. human decides whether to merge.

Branch protection, required checks and human review should remain in place even when the agent reliably creates good pull requests.

### Docs-as-Code Drift Prevention

An autonomous harness must enforce documentation synchronization as part of its **Definition of Done**:

```text
[Code Change Generated]
          │
          ▼
[Docs-Drift Agent]
  ├── Compares API signatures against /docs, OpenAPI specs, and README.md
  ├── Detects missing parameters or outdated return types
  └── Generates matching Markdown updates in the same branch commit
```

* **Atomicity:** Code changes, unit tests, and documentation diffs must live within the same pull request commit.
* **Gatekeeper Rule:** Architecture reviewers reject patches where public interfaces changed without corresponding updates in `/docs/*.md`.

## Multiple agents

A small set of explicit roles is usually more useful than many loosely defined agents.

### Implementer

- implements one approved step;
- writes and runs tests;
- stays within scope;
- produces a reviewable diff.

### Reviewer

- starts from the specification and diff;
- does not assume the implementation is correct;
- looks for behavioral regressions, architecture violations and missing tests;
- preferably does not edit the code during the initial review.

### Test analyst

- analyzes test coverage and mutation reports;
- prioritizes important surviving mutants;
- proposes test cases;
- does not change production code without separate approval.

Parallel agents should normally work in separate Git worktrees or branches. Two write-capable agents sharing the same working tree can overwrite or confuse each other's changes.

## High-assurance engineering patterns

When configuring harnesses for production repositories, five operational patterns help keep agent execution aligned with system invariants:

- **Repro-First (Regression Guard)**: Require an isolated, failing reproduction test *before* touching any production code. This prevents unanchored edits, speculative fixes, and masking existing bugs.
- **Pre-Flight Gate**: Run a single local gate script (`./tools/pre_flight.py` or `./scripts/verify.ps1`) that bundles formatting, architecture boundary tests, and type checking before committing.
- **Platform Quirks Catalog**: Maintain a concise document listing non-obvious runtime behaviors, OS differences, and edge cases. This prevents agents from refactoring intentional, low-level platform workarounds.
- **Reference Triangulation**: Provide clean-room reference examples, internal ADRs, or official SDK documentation directly in the context. This eliminates hallucinated third-party SDK calls and divergent code patterns.
- **Git Worktree Sandbox**: Execute experimental spikes and multi-agent tasks in disposable Git worktrees (`git worktree add`). This isolates file churn and prevents dirty working states from polluting the primary repository.

## Execution location

An agentic harness may run locally, in a managed cloud environment, in infrastructure controlled by the organization, or in a hybrid arrangement.

The execution location is largely independent from the workflow itself. The same plan–implement–verify–review process can be executed on a developer workstation, inside a managed agent platform, or by a custom-hosted agent service.

For deployment models, shared team agents, cloud execution, self-hosting and hosting options, see:

[[Agent Deployment and Execution Models]]

## Recommended adoption path

Start with the smallest useful system:

1. Install the coding agent in the IDE.
2. Choose a small repository that you already understand.
3. Add a concise `AGENTS.md`.
4. provide a single `verify` command.
5. describe one feature in `SPEC.md`.
6. ask the agent to create `PLAN.md` without editing code.
7. approve one step only.
8. let the agent implement and verify it.
9. run an independent review of the diff.
10. record repeated mistakes as repository guidance or deterministic checks.

Only introduce skills, subagents and a custom orchestrator after the basic workflow reveals a repeated need. Cloud and remote execution are discussed separately in [[Agent Deployment and Execution Models]].

## When a custom harness is justified

A text workflow inside Codex or Claude Code is sufficient for interactive development. A custom harness or orchestrator becomes useful when the process requires hard guarantees or automation, for example:

- approval state must be enforced by code;
- tasks run unattended in CI;
- retries and budgets must be centrally controlled;
- many repositories or agents must be coordinated;
- execution traces and costs must be recorded;
- outputs must conform to a machine-readable schema;
- failed steps must be resumed deterministically;
- only particular commands may run in particular states.

At that point, the workflow becomes a state machine rather than merely a set of instructions:

```text
Planning
  → Awaiting approval
  → Implementing
  → Verifying
  → Awaiting step approval
  → Commit and draft PR
```

The custom harness controls the transitions. The LLM proposes and executes work only within the currently permitted state.

### Custom Python Harness vs. Interactive CLI Agents

There is a fundamental trade-off between interactive pair-programming tools (e.g., Claude Code, Cursor) and custom program-driven harnesses:

| Dimension | Interactive CLI / UI (Claude Code, Cursor) | Custom Programmatic Harness |
| :--- | :--- | :--- |
| **Execution Mode** | Synchronous, interactive (human at keyboard). | Asynchronous, headless, event-driven (CI/CD, webhooks). |
| **Architecture** | Single-agent context handling tasks sequentially. | Multi-agent orchestration (distinct personas with isolated contexts). |
| **Escalation** | Prompts directly in the terminal interface. | Generates structured escalation artifacts (Draft PRs, inline diff comments). |
| **Control Flow** | Black-box logic governed by vendor abstractions. | Deterministic flow (`while`, `try...except`, custom state machines). |
| **Best For** | Feature exploration, ad-hoc refactoring, solo dev. | Background bug-fixing, batch repository migrations, strict CI gates. |

### Minimal Python Harness Skeleton

```python
import subprocess
from dataclasses import dataclass
from typing import Tuple

@dataclass
class HarnessState:
    task: str
    iteration: int = 0
    max_iterations: int = 3
    error_log: str = ""

def run_deterministic_tests() -> Tuple[bool, str]:
    """Runs test suite and returns pass status with stdout/stderr."""
    result = subprocess.run(["pytest", "tests/"], capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr

def self_healing_loop(state: HarnessState):
    while state.iteration < state.max_iterations:
        state.iteration += 1
        
        # 1. Generate / Edit Code via LLM Tool Call
        apply_llm_patch(state)
        
        # 2. Deterministic Verification Gate
        tests_passed, test_output = run_deterministic_tests()
        if not tests_passed:
            state.error_log = test_output
            continue
            
        # 3. Static Analysis & Multi-Agent Gate
        if run_security_audit_agent():
            subprocess.run(["git", "commit", "-am", f"fix: {state.task}"])
            return {"status": "SUCCESS"}
            
    # 4. Limit Exceeded -> Escalate to Human
    return trigger_human_escalation(state)
```

## Final principles

1. Use a ready-made harness before building a custom one.
2. Separate specification, plan, execution and review.
3. Approve semantic steps, not every mechanical command.
4. Give every loop explicit success, retry and stop conditions.
5. Keep repository guidance concise and close to the relevant code.
6. Make setup and verification reproducible with scripts.
7. Use deterministic tools for deterministic checks.
8. Use mutation tools to generate mutations and an LLM to interpret survivors.
9. Restrict credentials, network access and production authority.
10. Let agents prepare commits and draft PRs, but retain CI, branch protection and merge approval.

## Related notes

- **[[Configuring and Testing Coding Agent Capabilities]]** — Scoping agents, rules, skills and tools, then testing routing, hooks and audits.
- **[[Building Determinism from Unpredictable Models]]** — Turning non-deterministic model outputs into reliable engineering outcomes through structured harnesses.
- **[[Executable Architecture Tests for Coding Agent Guardrails]]** — Automated checks that fail fast when an agent violates structural invariants.
- **[[Active Backlog Pruning and Context Hygiene in Agentic Roadmaps]]** — Managing execution plans and preventing context pollution across iterative turns.
- **[[Dynamic Model Routing and Inference Gateways]]** — Dispatching harness tasks between local and cloud models.
- **[[The Living Engineering Chronicle and Context Compaction]]** — Maintaining long-term project history alongside short-lived execution state.
- **[[Testing in the Model, Agent, LLM Era]]** — Designing test suites as deterministic feedback loops for coding agents.
