---
title: Agentic Coding Harness and Controlled Development Workflows
tags:
  - ai-agents
  - agentic-coding
  - agentic-harness
  - software-engineering
  - testing
  - mutation-testing
  - llm
  - codex
  - software-development
aliases:
  - Agentic harness
  - Coding agent workflow
  - Controlled Development Workflows
  - Meta-Harnessing and Pattern Drift
  - Autonomous Harness Synthesis in Next-Gen Models
  - Steering Agents via Negative Boundaries
  - Negative Bounding in Agent Workflows
  - Bounding by Exclusion
  - Harness Engineering vs Vibe Coding
  - Vibe Coding vs Harness Engineering
  - SOTA Patterns for High-Assurance Agents
---

# Agentic Coding Harness and Controlled Development Workflows

> See also: [[Agent Deployment and Execution Models]], [[Building Determinism from Unpredictable Models]]

## Core Idea

An **agentic harness** is the software runtime that turns a large language model from a stateless text generator into a system that can reliably change software.

Fundamentally, an LLM executes a single operation:

> receive context → produce a text response

The harness wraps that operation in the runtime machinery required to do real engineering work:

- an execution loop that alternates between inference and tool dispatch;
- filesystem, terminal, Git, browser, and API access;
- instruction, context, and specification loading;
- working memory management and history compaction;
- sandboxing, credential masking, and permission gates;
- retries, timeouts, and deterministic stop conditions;
- test execution and automated verification;
- tracing, token budgets, and cost tracking;
- optional orchestration of isolated subagents.

A practical formulation is:

$$\text{Agent} = \text{Model} + \text{Harness} + \text{Instructions} + \text{Tools}$$

Tools like Codex, Claude Code, or custom internal runners are not simply models. They are purpose-built coding harnesses that connect a reasoning engine to a local repository, system tools, and an evaluation loop.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        THE AGENTIC HARNESS RUNTIME                     │
│                                                                        │
│   [ Developer Intent / Task ] ──► [ Harness Controller ]               │
│                                           │                            │
│        ┌──────────────────────────────────┴───────────────┐            │
│        ▼                                                  ▼            │
│   [ Foundation Model ]                          [ Deterministic Tools ]│
│   (Probabilistic Engine)                        - Shell & Compilers    │
│        │                                        - Test Runners         │
│        ▼ (Emits Tool Calls)                     - Git State Manager    │
│   [ Tool Dispatch Gateway ] ────────────────────► Static Analyzers/AST │
│        │                                                  │            │
│        └────────────── [ Permission Fences ] ◄────────────┘            │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

Two agents running the exact same model checkpoint will produce completely different results if their harnesses differ in context pruning, tool interfaces, compiler feedback handling, or verification gates. The harness is what enforces engineering rigor on top of probabilistic text generation.

## How the Agent Loop Works

A standard coding agent session runs through a continuous cycle:

1. **Goal Ingestion**: The user specifies a target or picks an item from the backlog.
2. **Context Assembly**: The harness loads project rules, architectural maps, specifications, and relevant file slices.
3. **Model Planning/Action**: The model inspects the context and emits structured tool calls (read a file, search for symbols, run a build).
4. **Execution**: The harness validates the tool call against permission policies and runs it locally.
5. **Observation**: The harness captures the stdout, stderr, or file contents and feeds them back into the model's context window.
6. **Next Action**: The model inspects the tool output and decides whether to continue modifying files, run tests, or declare completion.
7. **Termination**: The loop runs until acceptance criteria are verified, a human gate is reached, or a circuit breaker trips.

When an agent adds an API endpoint, it never edits files or invokes `dotnet test` directly. It requests these actions through the tool schema exposed by the harness. The harness runs the processes on the local machine and feeds the structured results back into the conversation context.

Because of this, an agent's real-world reliability depends heavily on how the harness handles:

- **Context selection**: Loading only the code and documentation relevant to the current slice rather than flooding the context window.
- **Tool schemas**: Exposing clear, unambiguous JSON tool signatures with explicit parameter descriptions.
- **Error diagnostics**: Truncating massive stack traces while keeping the failure site and relevant line numbers intact.
- **History compaction**: Pruning older, noisy bash outputs to prevent context saturation during extended debugging runs.
- **Permission boundaries**: Blocking dangerous filesystem or network operations before they execute.
- **Exit criteria**: Requiring green test suites rather than taking the model's self-assessed "looks good to me" at face value.

## Harness Versus Workflow

The harness provides the execution engine. A **workflow** provides the operational rules telling the harness how a specific category of engineering work must proceed.

Common workflow policies include:

- read and analyze the specification before touching any code;
- formulate an implementation plan and block until human sign-off;
- implement exactly one approved semantic step at a time;
- write or update a targeted regression test before modifying production code;
- run local verification scripts after every change;
- stop after completing a single architectural slice and show the clean diff;
- never push to remote branches without explicit confirmation.

In simple environments, a workflow can be captured in a Markdown file (`AGENTS.md`) interpreted by the model. However, text prompts provide soft guidance, not hard guarantees. When an operational boundary must not be bypassed—such as requiring a green test suite before committing, or requiring human approval before running database migrations—that boundary must be implemented as code within the harness itself.

## Controlled Plan-and-Approval Workflows

For non-trivial tasks, running the agent in an unconstrained loop leads to drifted implementations. Splitting execution into separate planning and implementation phases prevents premature edits:

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

Once you review and adjust the plan, authorize a single, tightly scoped step:

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

The explicit instruction to **stop** is mandatory. Without an unambiguous stop directive, models often treat "work step by step" as an invitation to chain every step into a single unreviewed run.

## Semantic Steps vs. Mechanical Steps

Human attention should be reserved for decisions that change the architecture, risk profile, or semantics of the system. Routine tasks should execute automatically.

```text
┌─────────────────────────────────────────────────────────────┐
│                    HUMAN APPROVAL GATES                     │
│  - Public API contract changes      - Dependency additions  │
│  - Database migrations              - Module boundaries     │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Approved)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 AUTOMATED MECHANICAL LOOPS                  │
│  - Compiling & typechecking         - Running test suites   │
│  - Auto-formatting & linting        - Parsing error traces  │
└─────────────────────────────────────────────────────────────┘
```

### Semantic Steps (Require Human Approval)

These operations change the behavior, contracts, or structure of the codebase:

- modifying a public API signature or breaking an endpoint contract;
- altering core business calculation rules;
- establishing or modifying module boundaries;
- adding or executing a database migration script;
- altering domain entities or aggregate roots;
- introducing a new third-party dependency;
- introducing a new architectural abstraction or design pattern.

### Mechanical Steps (Run Autonomously)

These operations are safe to run within an approved semantic step:

- compiling the solution or running type checkers;
- executing existing test suites;
- applying automated code formatters and linters;
- retrying a test run after a targeted code fix;
- inspecting runtime or application logs;
- resolving clean, unambiguous compiler diagnostics.

The goal is not to micro-manage every terminal command. Developers should review semantic intent, data integrity, and system design; compilers and test runners should verify syntax and regression safety.

## The Self-Healing Implementation Loop

Instead of expecting an LLM to generate production-ready code in a single turn, the harness executes a cyclic Actor-Critic loop that feeds deterministic compiler and test failures back into the model:

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

### Key Loop Mechanics

* **Structured Diagnostics Feedback:** Fixer prompts receive trimmed, relevant stack traces, failing assertion details, and target file lines—not vague re-prompts like "that didn't work, try again."
* **Strict Iteration Ceilings:** The loop must enforce a hard iteration cap (typically $N = 3 \text{ to } 5$). If the model cannot resolve an error within that budget, continuing usually leads to context pollution, hallucinated APIs, or thrashing. The loop must cleanly terminate and escalate to a human.
* **Atomic Workspaces:** Every loop should run in an isolated Git branch or disposable Git worktree. If an attempt goes off the rails or burns its budget, the harness cleanly reverts the workspace (`git reset --hard` or worktree deletion) to a known good state.

### Success Conditions

A step is considered complete only when:

- all acceptance criteria defined in the step plan are satisfied;
- relevant unit, integration, and architecture tests run green;
- the solution compiles with zero new warnings or errors;
- no files outside the approved scope were altered;
- git diff reveals clean changes without leftover debugging prints or commented code;
- no unresolved assumptions or unhandled edge cases remain.

### Stop and Escalation Conditions

The harness must abort execution and yield to a human when:

- the business requirement or edge case behavior is ambiguous;
- a public interface, schema, or persistence model requires unexpected changes;
- a fix requires crossing an unapproved module boundary;
- a test failure repeats across multiple attempts without progress;
- a test failure appears flaky or tied to environment setup;
- verification is blocked by unrelated existing bugs in the repository;
- the agent attempts to broaden the scope of the task to bypass a difficult failure;
- an operation requires external credentials, production keys, or elevated permissions.

Without explicit escalation gates, an agent will often try to "make the tests pass" by weakening assertion logic, deleting test cases, or introducing ad-hoc mocks.

### Human Arbitration Artifacts

When an agent hits an iteration limit, it should not dump raw terminal logs on the developer. The harness should generate a structured escalation artifact explaining the impasse:

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

Here is an example escalation comment posted automatically to an issue or pull request review thread:

> ⚠️ **HUMAN ARBITRATION REQUIRED** (Iteration ceiling reached: 3/3)
> 
> **Failing Invariant:**
> * The Security Reviewer agent flagged an unbatched database query inside a high-throughput loop (N+1 query risk).
> * The Coder Agent attempted batching, but encountered a missing foreign key constraint in the SQLite local test harness that passes in Postgres.
> 
> **Options for Developer:**
> - [ ] **Option A:** Add missing SQLite index migration and allow agent to retry query batching.
> - [ ] **Option B:** Accept single-query fetch due to strict low-volume usage in this specific microservice.
> - [ ] **Option C:** Revert module changes and revise high-level architecture.

Replying directly in the thread triggers a webhook that passes the human decision back to the harness, resuming execution with clear guidance.

## The Limits of Soft Prompts: Hard Fences and the Probabilistic Hazard

A frequent trap in agent orchestration is relying on system prompts or instruction markdown files (`AGENTS.md`, `SKILL.md`) to prevent catastrophic errors:

```markdown
<!-- Soft semantic instruction: Can and will fail probabilistically -->
Never delete production database tables or clear root project directories.
```

An LLM is a probabilistic system. Regardless of how well-crafted your instructions are, the likelihood of an out-of-distribution slip is never zero. Under high context saturation, foreign error formats, or long reasoning traces, model attention degrades. Eventually, an agent will interpret an environmental failure as a corrupt workspace and run `rm -rf *`, drop a local table, or rewrite an entire subsystem with empty stubs.

### The Asymmetry of Risk

Human engineers operate with an innate awareness of consequence. We slow down when typing `drop table` or modifying core persistence layers because we understand the pain of data loss, the difficulty of recovery, and the business impact of downtime.

An LLM has no sense of consequence:
- Dropping a core schema or deleting 3,000 lines of complex timing logic is simply another valid token completion or JSON tool call (`execute_command("rm -rf src/")`).
- When a catastrophic deletion happens, the model will cheerfully parse the next empty directory listing and proceed to the next turn without hesitation.
- System prompts are soft semantic guidance—they alter probability distributions, but they cannot enforce invariant physical laws.

### Hard Runtime Fences

Because models cannot guarantee their own containment, the harness must enforce non-negotiable architectural boundaries in code:

1. **The Clean Commit Prerequisite**: Agents must never operate in a dirty working directory with uncommitted local work. Every session must branch from a known clean commit, or run inside an isolated Git worktree. If an agent hallucinates or ruins a file, recovery must be an instantaneous, single-line command (`git checkout .` or `git worktree remove`).
2. **Tool-Level Destructive Gating**: Destructive actions (file unlinking, mass directory deletion, raw database drops) must be disabled at the tool gateway layer, or gated behind an out-of-band human confirmation prompt. The model should physically lack an exposed tool capable of deleting project directories without approval.
3. **Read-Only Path Sandboxing**: Critical directories—such as architecture specs, security guidelines, and environment configuration—should be mounted read-only to the agent process.
4. **Human Review of Diffs**: Never auto-merge agent-written branches directly into mainline branches. Humans must review diffs to catch subtle logic decay, hallucinated dependencies, or weakened assertions.

### Fix the Harness, Not Just the Code

When an agent violates an invariant, drops a table, or introduces bad code patterns, **never manually fix the code in your IDE and move on**. 

If you manually patch the code, the agent will make the same mistake on the next run. Instead, fix the harness:
- Add a negative fence in `.agents/rules/`.
- Introduce a deterministic architecture test that fails if that pattern is used.
- Add an explicit validation script to your pre-flight checks.

Force the agent to re-run against the updated constraint until it passes. Hardening the environment ensures the failure mode is permanently eliminated for both agents and human contributors.

## Steering via Negative Boundaries

A common failure mode when writing agent instructions is **prescriptive over-specification**: trying to document every single allowed path, variable name, and design decision in advance.

### The Leaky Nature of Affirmative Instructions

Affirmative instructions are inherently leaky:

> Telling an agent what it *should* do does not stop it from doing everything else.

If you instruct an agent: *"Use the command pattern to handle this request"*, the model may follow that instruction while also introducing reflection, allocating large heap buffers inside a tight audio loop, or wrapping everything in generic `catch (Exception ex)` blocks. Affirmative instructions guide probability, but they leave an unbounded operational surface.

### Bounding by Exclusion

A more reliable approach pairs wide implementation freedom with rigid negative boundaries (see [[Negative Knowledge and Explicit Architectural Dissents]]):

1. **Grant Implementation Latitude**: Allow the agent to select data structures, local helpers, and algorithm details within the target module scope.
2. **Erect 2–3 Explicit Negative Fences**: Clearly define forbidden anti-patterns:
   - *Forbidden*: Adding new external package dependencies without prior human approval.
   - *Forbidden*: Mutating database schemas or public API contracts in this task slice.
   - *Forbidden*: Introducing heap allocations, dynamic dispatch, or blocking I/O calls inside synchronous hot paths.
3. **Outcome**: The agent retains the flexibility to solve edge cases without getting stuck in brittle, over-specified prompts, while your architectural invariants remain protected against drift.

## Repository Layout and File Organization

A well-structured repository cleanly separates permanent engineering rules, transient roadmaps, architectural documentation, and task state:

```text
repo/
├── AGENTS.md               <-- Universal repository rules and core operating instructions
├── README.md               <-- Environment setup, build commands, service dependencies
├── ARCHITECTURE.md         <-- Module boundaries, dependency flow, component responsibilities
├── ROADMAP.md              <-- Active pruned backlog (ZERO completed items retained)
├── DIARY.md                <-- Living Engineering Chronicle (append-only rationale & logs)
├── .agents/
│   ├── rules/              <-- Granular invariant rules and negative fences
│   │   ├── performance.md
│   │   └── security.md
│   └── skills/             <-- Reusable multi-step operational playbooks
│       └── implement-approved-step/
│           ├── SKILL.md
│           └── references/
├── tools/
│   ├── log_diary.py        <-- Out-of-context CLI append tool (0 prompt tokens consumed)
│   └── pre_flight.py       <-- Fast local gate verifying formats, types, and architecture
├── docs/
│   ├── architecture/
│   └── workflows/
├── tasks/
│   └── order-cancellation/
│       ├── SPEC.md         <-- Acceptance criteria and feature requirements
│       ├── PLAN.md         <-- Granular, stepped implementation plan with states
│       └── DECISIONS.md    <-- Settled architectural debates and rationale
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
Describes how to operate the system locally:
- runtime and toolchain versions;
- local dependency bootstrapping (databases, mock servers);
- compile, lint, and test commands;
- local endpoints, ports, and debugging profiles.

### `ARCHITECTURE.md`
Provides a concise structural map of the repository:
- primary modules, namespaces, and their discrete boundaries;
- permitted dependency directions (e.g., Domain must not reference Infrastructure);
- integration patterns and transport layers;
- location of critical business logic versus glue code.

### `ROADMAP.md` & Active Backlog Pruning
Maintains the immediate plan for upcoming work. High-assurance workflows enforce **Active Backlog Pruning** (see [[Active Backlog Pruning and Context Hygiene in Agentic Roadmaps]]):
- Completed items are **never retained** with `[x]` checkmarks or strikethrough text in the active backlog file.
- Leaving hundreds of lines of completed tasks in view degrades model attention and wastes context tokens on settled work.
- The moment a step is verified and committed, it is deleted from `ROADMAP.md`. High-level capabilities are summarized in a brief "Baseline Deliverables" list at the top, keeping the file small and forward-looking.

### `DIARY.md` & Out-of-Context Tooling
Because the active roadmap prunes completed work, project evolution and technical decisions must be captured in an append-only engineering diary (`DIARY.md`; see [[The Living Engineering Chronicle and Context Compaction]]).

Each entry captures four key areas:
1. Affected Subsystems;
2. What Changed;
3. Architectural Rationale;
4. Verification Results.

To prevent a growing log file from consuming the agent's context window, the agent does not open or edit `DIARY.md` directly. Instead, it uses a lightweight CLI tool:

```bash
python tools/log_diary.py \
  --subsystem "Orders" \
  --changed "Added cancellation event handler" \
  --rationale "Ensures event consistency before inventory updates" \
  --verified "./scripts/test-module.ps1 Orders"
```

The script appends formatted Markdown to disk instantly without passing the rest of the historical log through the model's context window. Periodically, older entries are summarized into high-level architectural digests via a compaction skill.

### `AGENTS.md`
Contains durable, repository-wide rules that apply to every agent run:

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

Keep `AGENTS.md` focused and concise. Use it to point the model to detailed documentation rather than trying to fit the entire architecture into a single file.

### `SPEC.md`
Defines feature behavior and acceptance criteria, independent of implementation details:

```markdown
# Cancel order

An order can be cancelled only before shipment.

## Acceptance criteria

- A pending order can be cancelled.
- A shipped order cannot be cancelled.
- Cancellation records the actor and timestamp.
```

### `PLAN.md`
Breaks the specification down into bounded implementation slices, tracking their state:

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

Standard step states include: `pending`, `approved`, `in-progress`, `completed`, `blocked`, and `rejected`.

Explicitly detailing what is **Out of scope** is essential: it prevents agents from refactoring adjacent systems, adding unrequested endpoints, or introducing scope creep.

### `DECISIONS.md`
Maintains an append-only register of settled technical trade-offs, options considered, and selected paths. This stops models and developers from reopening resolved design choices during subsequent runs.

## Reusable Agent Skills

When a workflow pattern is repeated across projects—such as setting up a new vertical slice, running an upgrade migration, or applying a hotfix—it should be packaged as a reusable skill:

```text
.agents/skills/implement-approved-step/
├── SKILL.md
├── references/
│   └── plan-template.md
└── scripts/
    └── verify.ps1
```

A skill document outlines a repeatable operational sequence:

```markdown
1. Read AGENTS.md, SPEC.md and PLAN.md.
2. Find the first approved step.
3. Confirm that its completion criteria are measurable.
4. Add or update tests.
5. Implement the minimal production change.
6. Run the specified verification.
7. Review the diff against the specification.
8. Mark the step completed only when all criteria pass.
9. Stop; never begin the next step automatically.
```

### Skills as Native Code Functions

While skills can be written as text instructions running standard bash commands, writing skills as native code functions (Python, Go, or C#) provides significant advantages:

1. **AST-Filtered Context**: Instead of reading a 3,000-line source file into context, a native skill can use AST parsers (`tree-sitter`, Roslyn, Python `ast`) to extract only the target class, method signatures, and relevant docstrings.
2. **Structured API Integration**: Using official SDKs (e.g., GitHub, AWS, Docker) avoids fragile stdout string parsing from CLI tools, eliminating errors caused by terminal formatting or unexpected color codes.
3. **Deterministic Sandboxing**: Native functions can spin up lightweight in-memory databases, apply migrations, run test passes, and tear the environment down cleanly, ensuring side-effect-free verification.

## Deterministic Tools Enforce Deterministic Rules

Never waste context tokens or rely on an LLM to check rules that can be evaluated deterministically by a compiler, linter, or static analyzer.

| Concern | Preferred Mechanism |
| :--- | :--- |
| Code Formatting | `.editorconfig`, Prettier, `dotnet format` |
| Compiler Warnings & Errors | `Directory.Build.props`, `tsconfig.json` (`strict: true`) |
| Module & Architecture Boundaries | NetArchTest, ArchUnit, native static analysis rules |
| Behavior & Regression Safety | Automated unit and integration test suites |
| Test Assertiveness & Gap Detection | Mutation testing (e.g., Stryker.NET, Mutmut) |
| Dependency Vulnerabilities | Trivy, Snyk, Dependabot |
| Hardcoded Secret Detection | Gitleaks, Trufflehog |
| Design & Scope Approval | Human engineer reviewing `SPEC.md` / diff |
| Implementation & Patch Synthesis | LLM coding agent |

> Rule of thumb: If a constraint can be verified mathematically or deterministically, use a deterministic tool. Use the LLM to understand requirements, plan edits, write patches, and interpret error output.

### Executable Architecture Tests

Architecture rules should be enforced through test suites rather than text guidelines alone. In .NET, for instance, you can write executable tests using `NetArchTest` to verify that architectural boundaries remain intact:

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

You can also use architecture tests to enforce physical guardrails on the harness itself:
- asserting that no source file in the domain exceeds 800 lines;
- asserting that public API handlers do not contain unhandled `try-catch` blocks;
- asserting that all repository methods accept a cancellation token.

When the agent breaks an architectural rule, the test suite fails with a clear, targeted assertion error, guiding the agent to correct itself through the standard test-fix loop.

## Stable Verification Commands

The repository must provide simple, predictable commands that execute identically for a human developer, a local agent, or a CI runner:

```powershell
./scripts/setup.ps1
./scripts/build.ps1
./scripts/test-module.ps1 Orders
./scripts/verify.ps1
./scripts/mutation-test.ps1 Orders
```

Effective verification scripts should:
- run completely non-interactively without prompting for user input;
- exit with code `0` on success and non-zero on any failure;
- emit clean, concise terminal output that prioritizes failing assertions over verbose noise;
- leave the working tree clean without modifying checked-in files;
- execute cleanly from a fresh git clone;
- share identical logic between local development and CI pipelines.

### Layered Verification Strategy

Running the entire test suite on every small edit quickly becomes a bottleneck. A layered test strategy keeps iteration cycles fast:

1. **Inner Loop**: Run a single targeted test file or method while making code changes.
2. **Module Loop**: Run the unit and integration tests for the current module after completing the step.
3. **Pre-Commit / Pre-Flight**: Run the complete local test suite, formatters, and architecture linters (`./scripts/verify.ps1`).
4. **Outer Loop**: Offload expensive end-to-end integration tests and full mutation coverage runs to CI or background jobs.

## Mutation Testing as the Real Test Oracle

High line coverage can be deceiving. LLM agents often write tests that run every line of code without actually asserting meaningful behavioral boundaries—producing tests that pass regardless of whether the business logic is correct.

Mutation testing verifies the quality of your tests by introducing deliberate defects into your code's abstract syntax tree (AST):

```csharp
// Original
if (order.TotalAmount >= 100) ApplyDiscount();

// Mutated (Boundary flipped)
if (order.TotalAmount > 100) ApplyDiscount();
```

The test runner is then executed against each mutation:
- **Killed**: A test failed, successfully catching the defect.
- **Survived**: The code changed, but the test suite still passed (indicating weak assertions or missing test coverage).
- **No Coverage**: The mutated line was never executed by any test.
- **Timeout**: The mutation caused an infinite loop or hanging process.

An LLM should not manually generate mutations. Mutation tools handle generation and test runs efficiently; the model should be used to analyze survivors and write targeted tests that kill them.

```text
┌─────────────────────────────────────────────────────────────┐
│                 MUTATION TESTING CYCLE                      │
│                                                             │
│   [ Mutation Tool (e.g. Stryker) ]                          │
│   - Injects AST mutations (e.g. >= to >)                    │
│   - Runs tests & produces machine-readable JSON report      │
│                         │                                   │
│                         ▼ (Identifies Surviving Mutants)    │
│   [ Agent Test Analyst ]                                    │
│   - Parses JSON report for surviving mutants                │
│   - Analyzes missing edge cases                             │
│   - Writes new targeted tests with real assertions          │
│                         │                                   │
│                         ▼ (Re-runs Mutation Pass)           │
│   [ Verification Gate ] ────────────────────────────────────┘
│   - Mutant killed: Test suite hardened                      │
└─────────────────────────────────────────────────────────────┘
```

### Division of Responsibilities

- **Mutation Runner (e.g., Stryker.NET, Mutmut)**: Parses the AST, injects mutations, executes tests, reverts changes, and exports structured JSON reports.
- **Agent**: Parses surviving mutants from the report, pinpoints missing edge-case assertions, writes tests specifically designed to kill those mutants, and explains the behavioral regression being guarded.
- **Human**: Decides which mutations represent critical business logic versus low-value implementation details, avoiding the trap of chasing a 100% mutation score on non-critical glue code.

## Reproducible Local Environments

An agent cannot operate reliably if setting up dependencies requires undocumented tribal knowledge. A project should provide a clear, automated path from a fresh clone to a passing test suite:

- runtime SDKs pinned in declarative files (`global.json`, `.nvmrc`, `rust-toolchain.toml`);
- centralized dependency lockfiles (`Directory.Packages.props`, `pnpm-lock.yaml`, `poetry.lock`);
- local tool manifests for project-specific CLIs (`dotnet-tools.json`);
- container configurations (`docker-compose.yml`) for databases, queues, and backing services;
- deterministic local test seeds and fixture data;
- standard bootstrap and verification scripts;
- optional Dev Container configurations for full environment isolation.

A fresh setup should work with a few standardized commands:

```bash
# Example local bootstrapping flow
dotnet tool restore
docker compose up -d
./scripts/setup.ps1
./scripts/verify.ps1
```

## Permissions, Sandboxing, and Secrets

Because local agents execute terminal commands, they can potentially access SSH keys, local databases, container runtimes, and cloud provider CLIs. The harness should enforce least privilege by default:

- restrict file writes exclusively to the active workspace directory;
- block outbound network connections from the shell tool, except for explicit package restores;
- never expose production credentials or live cluster endpoints to the local agent environment;
- inject mock keys or local credentials via environment variables, keeping production `.env` files in `.gitignore`;
- require explicit human confirmation before running cloud CLI tools (`aws`, `az`, `gcloud`, `kubectl`);
- physically block execution of deployment or migration commands against remote hosts.

```markdown
<!-- Standard safety rules in AGENTS.md -->
- Never log, print, or commit private keys, API tokens, or secrets.
- Use only local database instances running on localhost/docker-compose.
- Never run cloud provider authentication or deployment commands.
```

Sandboxing physically restricts what the agent's process can do at the OS and network level. Permission policies define when the agent must stop and prompt for human approval. Both are necessary to keep the development environment secure.

## Git, Commits, and Pull Requests

An agent running inside a capable harness can manage the complete local Git lifecycle:

```bash
git switch -c feature/order-cancellation
git add src/Orders/Domain/Order.cs tests/Orders.UnitTests/OrderTests.cs
git commit -m "feat(orders): enforce cancellation invariant before shipment"
git push -u origin feature/order-cancellation
gh pr create --draft --title "feat(orders): order cancellation support"
```

### Git Policy Matrix

| Operation | Agent Authority | Policy & Conditions |
| :--- | :--- | :--- |
| Create feature branch | Automatic | Must follow repo naming conventions (`feature/`, `fix/`). |
| Stage modified files | Automatic | Explicit file paths only; `git add .` or `git add -A` is prohibited. |
| Create local commit | Allowed | Permitted only after `./scripts/verify.ps1` runs clean. |
| Push to remote branch | Approval Required | Must prompt human before publishing branch to origin. |
| Create Draft PR | Approval Required | Opens as draft with diff summary and test evidence. |
| Ready for Review | Human Only | Human developer marks PR ready after reviewing the diff. |
| Merge PR | Human Only | Merges require human approval and passing CI checks. |
| Direct commit to `main` | Prohibited | Blocked by local rules and remote branch protection. |
| Force push (`-f`) | Prohibited | Blocked entirely to prevent history loss. |

### Enforcing Clean Commits

Commits should represent coherent, verified units of work rather than a messy stream of trial-and-error edits:

```text
test(orders): add failing tests for order cancellation rules
feat(orders): implement cancellation checks on order aggregate
feat(api): expose order cancellation endpoint
docs(orders): update order lifecycle documentation
```

### Docs-as-Code Drift Prevention

Autonomous changes frequently introduce drift between implementation details and architectural documentation. A high-assurance harness should verify that documentation updates accompany code changes within the same commit:

```text
[Code Patch Generated]
          │
          ▼
[Docs-Drift Gate]
  ├── Inspects modified interfaces, endpoints, and domain models
  ├── Compares signatures against /docs, OpenAPI specs, and README.md
  └── Generates matching documentation updates within the same branch
```

If a public interface, configuration flag, or database schema changes without a corresponding update in `/docs` or the relevant `README.md`, the verification check should flag the omission before the branch is pushed.

## Multi-Agent Roles and Worktree Isolation

Rather than relying on a single agent trying to juggle every task in a massive context window, complex workflows benefit from splitting responsibilities among specialized personas:

```text
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Implementer   │       │  Test Analyst   │       │    Reviewer     │
│ - Scoped edits  │       │ - Coverage gaps │       │ - Spec fidelity │
│ - Unit tests    │       │ - Mutation runs │       │ - Arch rules    │
│ - Passes build  │       │ - Hardens tests │       │ - Read-only diff│
└────────┬────────┘       └────────┬────────┘       └────────┬────────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   ▼
              ┌────────────────────────────────────────┐
              │      ISOLATED GIT WORKTREE SPACES      │
              │  worktrees/agent-impl                  │
              │  worktrees/agent-review                │
              └────────────────────────────────────────┘
```

- **Implementer**: Focuses entirely on implementing the approved semantic step, writing supporting unit tests, and getting the local build to pass cleanly.
- **Test Analyst**: Evaluates test coverage and mutation test reports. Pinpoints surviving mutants, identifies missing edge-case coverage, and writes tests to harden the suite without altering production code.
- **Reviewer**: Operates in read-only mode, evaluating the implementation diff against `SPEC.md` and `ARCHITECTURE.md`. Identifies regressions, security risks, or architectural drift before human review.

When running multiple agents simultaneously, **never let two write-capable agents share the same working directory**. They will overwrite files, create race conditions, and invalidate each other's test runs. Use dedicated Git worktrees (`git worktree add ../feature-slice-a`) to give each agent its own isolated workspace on disk.

## High-Assurance Engineering Patterns

When building or configuring high-assurance harnesses, five operational patterns help keep agent execution aligned with production requirements:

| Pattern | Operational Purpose | Failure Mode Prevented |
| :--- | :--- | :--- |
| **Repro-First (Regression Guard)** | Write an isolated, failing reproduction test *before* touching any production code. | Prevents unanchored edits, speculative fixes, and masking existing bugs. |
| **Pre-Flight Gate** | Run a single script that verifies code formatting, architecture boundaries, type safety, and logs. | Eliminates manual review checklist fatigue and catches broken conventions early. |
| **Platform Quirks Catalog** | Maintain a Markdown document listing non-obvious runtime behaviors, OS differences, and edge cases. | Prevents agents from "fixing" intentional, low-level platform workarounds. |
| **Reference Triangulation** | Provide official API docs, internal ADRs, and clean-room reference examples in the context. | Eliminates hallucinated third-party SDK calls and divergent code patterns. |
| **Git Worktree Sandbox** | Execute experimental tasks or spikes in disposable, isolated Git worktrees. | Keeps experimental changes from cluttering the primary working tree. |

## Interactive CLI Agents vs. Custom Programmatic Harnesses

Teams often debate whether to use off-the-shelf interactive CLIs (like Claude Code, Codex, or Cursor) or write a custom, code-driven orchestration harness in-house.

| Dimension | Interactive CLI / UI (Claude Code, Cursor) | Custom Programmatic Harness |
| :--- | :--- | :--- |
| **Execution Mode** | Synchronous, interactive (developer at the keyboard). | Asynchronous, headless, event-driven (CI pipelines, webhooks). |
| **Architecture** | Single-agent context processing conversational turns. | Multi-agent coordination with isolated context windows. |
| **Escalation** | Interactive prompts directly in the terminal interface. | Machine-readable artifacts (Draft PRs, structured JSON comments). |
| **Control Flow** | Vendor-managed tool-calling and retry loops. | Deterministic state machine (`while`, `try-catch`, state engines). |
| **Best For** | Feature exploration, day-to-day coding, interactive fixes. | Automated bug-fix queues, batch repo migrations, strict CI gates. |

For day-to-day engineering, a well-configured interactive CLI backed by comprehensive `AGENTS.md` and `SKILL.md` files is often plenty. A custom programmatic harness becomes necessary when workflows need to run unattended in CI, enforce rigid security sandboxes, or process event-driven queues at scale.

### Minimal Programmatic Harness Skeleton

Here is a functional Python skeleton illustrating the core mechanics of a headless implementation loop:

```python
import subprocess
from dataclasses import dataclass
from typing import Tuple, Dict, Any

@dataclass
class HarnessState:
    task_id: str
    spec_path: str
    iteration: int = 0
    max_iterations: int = 3
    last_error: str = ""

def run_tests() -> Tuple[bool, str]:
    """Runs the deterministic test runner and captures output."""
    res = subprocess.run(
        ["pytest", "tests/", "-q", "--tb=short"],
        capture_output=True,
        text=True
    )
    return res.returncode == 0, res.stdout + res.stderr

def apply_llm_patch(state: HarnessState) -> None:
    """Invokes the model with the task spec and recent failure output to apply edits."""
    prompt = f"Task: {state.spec_path}\n"
    if state.last_error:
        prompt += f"Previous verification failed:\n{state.last_error}\nFix the minimal code necessary."
    
    # In a full harness, this calls your LLM client with file edit tools exposed
    pass

def self_healing_loop(state: HarnessState) -> Dict[str, Any]:
    while state.iteration < state.max_iterations:
        state.iteration += 1
        print(f"[Loop] Running iteration {state.iteration}/{state.max_iterations}")

        # 1. Apply code changes via LLM
        apply_llm_patch(state)

        # 2. Run deterministic verification gate
        passed, output = run_tests()
        if passed:
            print("[Loop] Tests passed cleanly.")
            subprocess.run(["git", "commit", "-am", f"fix({state.task_id}): automated implementation"])
            return {"status": "SUCCESS", "iterations": state.iteration}

        # 3. Capture errors to steer the next iteration
        state.last_error = output
        print(f"[Loop] Verification failed. Capturing diagnostics.")

    # 4. Iteration ceiling hit: escalate to human with context
    print("[Loop] Iteration limit exceeded. Generating human escalation artifact.")
    return {
        "status": "ESCALATED",
        "iterations": state.iteration,
        "error_summary": state.last_error[-1000:]
    }
```

## The Evolution of Meta-Harnessing and System Drift

As model capabilities advance, how agentic harnesses are built and configured will shift:

```text
Current State:
Human engineers write harnesses, author rules/*.md, and keep agents on tight rails.

Next Generation:
Agents inspect repository topologies, synthesize bespoke harnesses, and coordinate subagent teams.
```

### 1. The Pretraining Bottleneck

Today's models are proficient at localized code editing, but struggle to configure multi-agent orchestration loops or design comprehensive rule systems from scratch.

This limitation stems from their training data: repositories created prior to 2024 contained almost no examples of agent harnesses, `.agents/rules/`, MCP server configurations, or programmatic subagent workflows. Because models have few training examples of self-governance, human engineers must define the ground rules—structuring context, configuring tools, and erecting boundary fences.

This changes how platform and library maintainers should approach developer documentation:
- **Documentation is no longer consumed only by humans in browsers**: Writing a Swagger UI or a static wiki is no longer enough.
- **Ship Native MCP Servers**: Expose your platform's APIs as Model Context Protocol (MCP) servers, giving agents structured tools and resources to interact with your services directly.
- **Provide Executable Skills (`SKILL.md`)**: Package explicit, multi-step integration workflows, token refresh routines, and pagination logic directly into the repository so agents don't have to guess.

### 2. Autophagous Data and Verifiable Selection Loops

As code written by AI agents becomes a significant portion of public repositories, the next generation of models will inevitably train on synthetic code. In machine learning, training recursively on uncurated synthetic data can cause **Model Collapse**:

- long-tail edge cases and deep domain knowledge are forgotten;
- hallucinated APIs and anti-patterns compound across training generations;
- overall reasoning and code quality degrade.

```text
The Degenerative Loop (Model Collapse):
Model generates code ──► Unchecked code committed to repos ──► Model trains on synthetic output ──► Degraded reasoning

The Verifiable Selection Loop (Robust Drift):
Model generates code ──► Compilers, test suites, and mutation checks verify output ──► Only verified code enters training corpora ──► Hardened next-gen models
```

Fortunately, software engineering has a built-in defense that natural language lacks: **software can be verified deterministically**.

If future models are trained indiscriminately on all synthetic code on GitHub, quality will degrade. But if training pipelines filter datasets through deterministic gates—requiring code to compile cleanly, pass unit test suites, eliminate mutation escapes, and run without warnings—the synthetic training loop becomes a form of **reinforcement learning via verifiable selection**, steadily steering future models toward cleaner, more robust patterns.

## Recommended Adoption Path

Start simple and add process only as your requirements demand:

1. **Start in the IDE**: Install an interactive coding agent CLI or extension.
2. **Pick a Familiar Codebase**: Start with a small, well-understood repository that already has solid test coverage.
3. **Add a Baseline `AGENTS.md`**: Define core rules, module boundaries, and forbidden operations.
4. **Create a Single `verify` Script**: Ensure a single command runs formatting, type checks, and unit tests cleanly.
5. **Write a Focused `SPEC.md`**: Define clear, testable acceptance criteria for a single feature or bug fix.
6. **Require a Plan First**: Direct the agent to produce a `PLAN.md` without modifying any code.
7. **Approve One Slice**: Authorize the agent to implement Step 1 and nothing else.
8. **Verify and Inspect**: Let the agent run its tests, inspect the resulting git diff, and run your independent verification script.
9. **Capture Recurring Mistakes**: Whenever an agent makes a mistake, don't just patch the code—add a rule in `.agents/rules/` or write an automated architecture test to prevent it from happening again.
10. **Automate Over Time**: Introduce custom skills, automated mutation testing, and programmatic harnesses only after your day-to-day workflow outgrows text-based instructions.

## Core Operating Principles

1. **Start with an established harness** before attempting to build a custom orchestrator in-house.
2. **Decouple operational phases**: Keep specification, planning, implementation, and review distinct.
3. **Approve semantic changes**, not every mechanical command or individual test run.
4. **Enforce hard bounds on every loop**: Set explicit iteration limits, atomic Git boundaries, and clear escalation paths.
5. **Enforce deterministic rules with deterministic tools**: Use linters, compilers, and test suites to verify code; use models to synthesize and repair it.
6. **Use mutation testing to assess test quality**: Mutation tools introduce defects; models analyze survivors and write tests to catch them.
7. **Steer with negative boundaries**: Forbidding catastrophic anti-patterns gives the model flexibility while keeping the architecture safe.
8. **Harden the harness, not just the code**: Encode fixes in repository rules, scripts, and tests to eliminate entire categories of recurring mistakes.
9. **Restrict permissions and sandboxes**: Gate destructive filesystem operations, mask production secrets, and require human confirmation for cloud environments.
10. **Retain human oversight on merges**: Let agents write code, run verification, and open draft pull requests, but keep human review and protected branches as the final authority.

---

### Related Notes
- [[Building Determinism from Unpredictable Models]]
- [[Active Backlog Pruning and Context Hygiene in Agentic Roadmaps]]
- [[The Living Engineering Chronicle and Context Compaction]]
- [[Negative Knowledge and Explicit Architectural Dissents]]
- [[Executable Architecture Tests for Coding Agent Guardrails]]
- [[The Conductor Pattern for High-Bandwidth Engineering]]
- [[Agent Deployment and Execution Models]]
- [[Constraint Saturation and Rule Oscillation in Coding Agents]]
- [[Learning Coding Agents Through Failure-Driven Instructions]]
- [[The Minimal Frame Pattern - Proving System Topology on Atomic Slices]]
