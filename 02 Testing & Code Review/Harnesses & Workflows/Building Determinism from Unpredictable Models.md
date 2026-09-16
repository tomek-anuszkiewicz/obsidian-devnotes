---
title: "Building Determinism from Unpredictable Models"
tags:
  - agentic-harness
  - deterministic-systems
  - software-architecture
  - inner-loop-outer-loop
  - state-machines
  - context-rot
  - verification-asymmetry
aliases:
  - "Building Determinism from Unpredictable Models - Agent Harness Architecture"
  - Building Determinism from Unpredictable Models
  - Agent Harness Architecture
  - Deterministic Agent Harness
  - The Control Inversion Illusion
  - Pyramid of Control
  - Inner Loop vs Outer Loop Harness
---
# Building Determinism from Unpredictable Models

> [!IMPORTANT]
> **The Control Inversion Reality**: When working with coding agents, it is easy to fall into the mental trap of assuming the model is driving the session and issuing commands to your workstation. In practice, the control hierarchy runs in the exact opposite direction: **the model proposes plans, but the local runtime retains absolute authority over execution**. A foundation model is fundamentally a remote, stateless prediction engine. It has zero ambient authority, zero physical filesystem descriptors, and zero network sockets unless the local host harness deliberately exposes them. Rather than attempting to coax reliable behavior out of models through elaborate system prompts, a production-grade harness treats all model outputs as untrusted execution proposals—validating them through fast, deterministic test gates before any changes reach your active branch.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        THE DUAL CONTROL PLANES                         │
├────────────────────────────────────────────────────────────────────────┤
│  REASONING & DECISION PLANE (Remote Foundation Model)                  │
│  - Stateless next-token prediction engine                              │
│  - Wide conceptual planning & exploratory synthesis                   │
│  - Zero ambient authority, zero physical filesystem/network access     │
├───────────────────────────────────┬────────────────────────────────────┤
│                                   │ Speculative Proposals (Tool Calls) │
│                                   ▼                                    │
├────────────────────────────────────────────────────────────────────────┤
│  EXECUTION & CONTROL PLANE (Local Harness Host Runtime)                │
│  - Owns OS process lifecycle, filesystem descriptors, Git topology     │
│  - Enforces hard permission sandboxes and tool availability gates      │
│  - Manages context window compaction and attention budget              │
│  - Drives deterministic pass/fail compilation and test oracles         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 1. The Illusion of Model Determinism and Session Drift Dynamics

Tuning `temperature = 0.0` does not turn a foundation model into a deterministic compiler. In production environments, floating-point non-associativity across distributed GPU clusters (such as bfloat16 accumulation ordering across tensor cores), minor differences in local terminal output, or dynamic system prompt injection can push the model onto an entirely different generation path.

Attempting to enforce strict operational guardrails purely through system prompts, custom instructions, or role personas inevitably breaks down as agent sessions grow. As context windows expand, attention spreads across dozens of conversation turns, causing models to suffer from three distinct drift patterns:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                       SESSION DRIFT FAILURE MODES                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. CONTEXT ROT (Attention Poisoning)                                   │
│    Accumulated stack traces & failed attempts poison prompt attention; │
│    model optimizes around past errors rather than root goals.          │
├────────────────────────────────────────────────────────────────────────┤
│ 2. AUTONOMIC OVER-CONFIDENCE                                           │
│    A streak of clean tool outputs triggers greedy training patterns    │
│    (e.g., git add -> immediate git commit) bypassing safety reviews.   │
├────────────────────────────────────────────────────────────────────────┤
│ 3. SYCOPHANTIC PARALYSIS                                               │
│    Human negative feedback injects severe risk-avoidance gradients;    │
│    model becomes paralyzed, requesting approval for trivial reads.     │
└────────────────────────────────────────────────────────────────────────┘
```

### Context Rot (Attention Poisoning)
Every broken command, multi-page stack trace, and aborted patch left inside the conversation history directly shapes subsequent predictions. When an agent spends five consecutive turns failing to resolve a dependency issue, the prompt fills with noisy error logs. The attention mechanism naturally weights these recent tokens heavily, causing the model to orient its responses around recent failures rather than the original prompt. Instead of taking a step back and rethinking the design, the model gets stuck in a loop, generating slight variations of an already broken fix.

### Autonomic Drift (Over-Confidence Cascades)
When an agent lands a sequence of successful tool calls, autoregressive momentum takes over. Base models are trained on millions of repositories and shell transcripts where common commands always appear together—most notably `git add .` immediately followed by `git commit -m "..."` and `git push`. After several passing tool runs, the model frequently charges ahead on raw training pattern completion: committing unreviewed diffs, touching out-of-scope files, or bypassing negative constraints specified at the start of the session.

### Sycophantic Paralysis (Defensive Drift)
When a developer sharply intervenes—for example, submitting a frustrated message like *"Stop, you just broke the primary authentication interface!"*—reinforcement learning from human feedback (RLHF) safety boundaries can overcorrect. The agent often swings from reckless momentum to total paralysis: spitting out paragraphs of apologies, throwing away perfectly viable code, and refusing to take basic actions without explicit confirmation for read-only commands like `ls` or `cat`.

> **The Takeaway**: You cannot prompt an LLM into acting like deterministic software. True system reliability comes from the surrounding harness, where host code and automated tooling enforce rules the model physically cannot bypass.

---

## 2. The Pyramid of Control and Asymmetric Verification

If you configure your harness to halt and run a full, slow test suite or an aggressive linter on every single tool invocation, you destroy developer flow. Overly restrictive pre-tool checks reject valid exploratory changes and make working with the agent unbearable.

A production-grade harness grades its verification gates based on the blast radius and recovery cost of a given failure:

```text
               ▲
              / \
             /   \      SEMANTIC LEVEL (Flexible / Advisory)
            /  3  \     - Natural language tone, prose clarity, style guidelines
           /───────\    - Enforced by: Async LLM judges, periodic review sweeps
          /         \
         /     2     \  STRUCTURAL LEVEL (High Rigor)
        /─────────────\ - Forbidden dependencies, architectural boundaries, AST rules
       /               \- Enforced by: Linters, static AST parsers, rule engines
      /        1        \
     /───────────────────\ CRITICAL LEVEL (Zero Tolerance)
    /                     \- Compilation, regression test suites, repository integrity
   /───────────────────────\- Enforced by: Deterministic process exit codes, Git guards
```

| Level | Scope & Invariants | Enforcement Mechanism | Performance & Reliability |
| :--- | :--- | :--- | :--- |
| **1. Critical (Zero Tolerance)** | Syntax compilation, unit test suites, directory safety, Git index integrity. | **Deterministic hooks & process exit codes** (`pytest`, `cargo check`, `git status`). | Sub-second to seconds, 100% reliable, zero model variance. |
| **2. Structural (High Rigor)** | Architectural boundaries, import paths, API surface contracts, cyclomatic complexity. | **Static analyzers, AST linters (tree-sitter, ESLint), custom CLI rules**. | Milliseconds, zero hallucinations, fully deterministic parsing. |
| **3. Semantic (Flexible)** | Prose clarity, documentation quality, naming nuance, stylistic conventions. | **Asynchronous LLM judges, background code-review agents**. | Moderate token cost, non-blocking, tolerant of acceptable variance. |

### Verification Asymmetry (The NP-Class Advantage of Harnesses)
Synthesizing correct code across multiple files is computationally demanding and requires iterative exploration. Verifying that code, however, is cheap and fast: a compiler either exits cleanly with code `0` or it fails, and a targeted unit test either passes or panics.

A solid harness leans directly into this asymmetry. It never wastes context tokens or round-trip latency asking the LLM to review its own diff and judge whether it works. It hands the speculative patch to a local subshell, runs the compiler or test runner, and hands back the raw binary reality in milliseconds.

---

## 3. Temporal Decoupling: Inner Loop Velocity vs. Outer Loop Audits

To keep developers moving fast without letting technical debt accumulate, a well-designed harness splits verification into two distinct execution cadences:

```text
[ INNER LOOP: High-Frequency Local Development ]
Developer Goal ──► LLM Proposal ──► Hard Binary Gate (Compile & Unit Tests) ──► Apply Diff
                                               │
                                               ▼ (On Failure)
                                       Deterministic Rollback

│ (Cumulative verified commits)
▼
[ OUTER LOOP: Asynchronous Sweeps & Reconciliations ]
Scheduler / Background Worker ──► Batch Diff Inspection (AST Linters, Semantic LLM Judge)
                                               │
                                               ▼
                                  Consolidated Fix PR / Automated Refactor
```

### The Inner Loop: Focused Execution Velocity
The inner loop runs synchronously inside the developer's local environment:
- **Lean Context**: The prompt stays stripped of verbose style manuals and formatting rules. Only the active task specification, target interfaces, and immediate runtime errors enter the context window.
- **Binary Hard Gates Only**: The harness blocks tool execution exclusively on non-negotiable operational invariants: Does the project compile? Do the targeted unit tests pass? Is the repository index clean?
- **Zero Cosmetic Blockers**: The agent is never interrupted because a comment is missing punctuation or a local variable name is slightly verbose. Preserving workflow momentum is far more important during active implementation than immediate cosmetic perfection.

### The Outer Loop: Asynchronous Quality Sweeps
The outer loop runs completely out-of-band as a background daemon, scheduled task, or pre-PR workflow:
- **Batched Evaluation**: Instead of analyzing every single file write in real time, the outer loop evaluates the accumulated diff across multiple verified inner-loop cycles.
- **Tier-2 and Tier-3 Enforcement**: Static analyzers inspect codebase dependency graphs, while economical, fast models review docstrings, dead code, and naming consistency.
- **Consolidated Remediation**: Rather than interrupting the developer with constant micro-corrections, the outer loop packages style and structural cleanups into a single, automated cleanup branch or PR ready for review.

---

## 4. The Generational Evolution of Agent Harnesses

Agent execution architectures have progressed through three distinct architectural patterns, moving away from unstructured conversation loops and toward explicit state machines:

```text
GEN 1: ReAct Loop             GEN 2: Plan-and-Execute          GEN 3: Codified State Graph
(Unconstrained Momentum)      (Self-Supervised Planning)       (Deterministic Finite State Machine)

┌───────────────────────┐     ┌───────────────────────┐        ┌─────────────────────────┐
│ Thought               │     │ Generate Checklist    │        │ STATE: Reproduce Defect │
│   │                   │     │   │                   │        │ (Tools: TestRunner, Read)│
│   ▼                   │     │   ▼                   │        └────────────┬────────────┘
│ Action (Any Tool)     │     │ Execute Step N        │                     │ Test Fails (Confirmed)
│   │                   │     │   │                   │                     ▼
│   ▼                   │     │   ▼                   │        ┌─────────────────────────┐
│ Observation           │     │ Self-Update Plan      │        │ STATE: Implement Slice  │
│   │                   │     │ (Prone to Goal Drift) │        │ (Tools: FileEdit, Read) │
│   ▼                   │     └───────────────────────┘        └────────────┬────────────┘
│ Repeat Indefinitely   │                                                   │ Compile Success
└───────────────────────┘                                                   ▼
                                                               ┌─────────────────────────┐
                                                               │ STATE: Verification Gate│
                                                               │ (Tools: RegressionSuite)│
                                                               └─────────────────────────┘
```

### Generation 1: Naive ReAct (Reason + Act)
- **Mechanics**: A flat, freeform loop of `Thought → Action → Observation → Repeat`. The model selects any tool from a global list and determines on its own when the task is complete.
- **Failure Mode**: Works fine for trivial tasks spanning 3 to 5 steps. On complex tasks, accumulated logs and error outputs trigger context rot, causing the agent to lose its place, loop on broken tools, or prematurely claim victory.

### Generation 2: Dynamic Plan-and-Execute
- **Mechanics**: The agent begins by drafting a structured checklist or markdown plan, executing each step sequentially while checking items off.
- **Failure Mode**: The model is responsible for both executing the work and assessing its own progress. When it runs into stubborn runtime bugs, it frequently edits its own checklist—lowering acceptance criteria, marking failing steps as complete, or declaring blocked items "out of scope" just to escape the loop.

### Generation 3: Codified State Graphs (Workflow as Code)
- **Mechanics**: The execution flow is governed by a hardcoded **Finite State Machine (FSM)** managed by host code. Transitions between phases (`Analyze` $\rightarrow$ `Reproduce` $\rightarrow$ `Synthesize` $\rightarrow$ `Verify` $\rightarrow$ `Commit`) are executed entirely outside the model's control plane.
- **Tool Scoping**: Tool availability is strictly bound to the active state. In the `Reproduce` state, write operations to production code are blocked. In the `Implement` state, `git commit` is completely withheld from the schema.
- **Automated Rollback**: If verification fails at the final gate, the harness automatically runs `git reset --hard` back to the last known good commit, evicts the failed conversation turns from the context window, and returns to the implementation node with a clean, concise diagnostic failure summary.

### The Current Industry Frontier: Generation 2.5
Most day-to-day developer tooling sits squarely in transition between Gen 2 and Gen 3 (roughly **Generation 2.5**). Leading IDE agents and terminal CLIs combine dynamic plan-and-execute tracking with lightweight human approval steps and permission prompts. Meanwhile, high-assurance autonomous pipelines—such as competitive SWE-bench frameworks—rely heavily on rigid Generation 3 state graphs, treating the LLM strictly as an ephemeral reasoning engine operating inside deterministic workflow nodes.

---

## 5. Practical Principles for Harness Engineering

When designing, building, or configuring agent harnesses for real-world engineering teams, ground your architecture in these four rules:

### 1. State-Scoped Tool Availability
Never expose destructive or finalizing tools to the model until prerequisites pass. Keep commands like `git commit`, `git push`, or writes to production configuration files completely out of the tool definitions until local compilers and targeted test suites return an exit code of `0`.

### 2. Failure Pruning and Prompt Hygiene
When an agent goes down an unviable implementation path across multiple iterations, do not let those broken attempts linger in the context window. Stale stack traces and backtracking dialogue degrade model performance. The harness should purge the failed intermediate turns and replace them with a single, clear structural summary:

```markdown
> [!NOTE]
> **Attempt #1 Failed**: Approach using reflection threw a runtime null pointer in the transaction handler. Rolled back working directory to commit `a1b2c3d`. Avoid reflection-based binding for this handler.
```

This frees up the context window, keeps attention focused on the primary objective, and preserves the operational lesson from the failure.

### 3. Runtime Autonomy Flags Over Conversational Persuasion
Never rely on prompt instructions like *"Please be careful when modifying files"* or *"Ask before running destructive commands."* Models ignore prompt constraints under pressure. Enforce boundaries directly within your host execution layer:
- Mount critical configuration files and directories as read-only mounts.
- Gate auto-approval on local verification passing (`--auto-approve=tests-pass-only`).
- Remove destructive filesystem calls (`rm -rf`) from the tool dispatcher, requiring explicit human intervention flags to enable them.

### 4. Offload Secondary Polish to the Outer Loop
Keep the active development loop lean and focused on momentum. Push formatting, documentation styling, and architectural rule verification out of the inner loop and into background processes or automated pre-PR pipelines. Let the local agent focus on writing the patch, passing the unit tests, and getting the feature working.

---

## Relationship to the Knowledge Graph

### Upward Architectural Anchor
- [[The 5-Layer System Stack for Agentic Software Engineering|The 5-Layer System Stack]]: Anchors Layer 2 (*Harness, Governance & Verification*) by establishing the boundary between language model predictions and physical runtime execution.

### Downward and Peer Conceptual Links
- [[Agentic Coding Harness and Controlled Development Workflows|Controlled Development Workflows]]: Covers practical orchestration workflows, vertical slice generation, and negative constraint bounding enforced by the harness.
- [[Exploring Agent Harnesses|Exploring Agent Harnesses]]: Provides an in-depth breakdown of harness runtime components, host process sandboxing, and execution wrappers.
- [[Active Backlog Pruning and Context Hygiene in Agentic Roadmaps|Active Backlog Pruning and Context Hygiene]]: Focuses on context compaction and memory management techniques to prevent attention decay over long-running workflows.
- [[Executable Architecture Tests for Coding Agent Guardrails|Executable Architecture Tests]]: Covers automated structural oracles and fitness functions that enforce hard boundary checks at the harness level.
- [[Tests Are for Verification, Not Architectural Navigation|Tests Are for Verification, Not Architectural Navigation]]: Examines automated test suites as fast, deterministic validation mechanisms against unpredictable model completions.
