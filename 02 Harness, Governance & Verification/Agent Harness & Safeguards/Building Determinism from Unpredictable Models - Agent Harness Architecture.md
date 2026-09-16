---
title: Building Determinism from Stochastic Foundations - Agent Harness Architecture
tags:
  - agentic-harness
  - deterministic-systems
  - software-architecture
  - inner-loop-outer-loop
  - state-machines
  - context-rot
  - verification-asymmetry
aliases:
  - Building Determinism from Stochastic Foundations
  - Agent Harness Architecture
  - Deterministic Agent Harness
  - The Control Inversion Illusion
  - Pyramid of Control
  - Inner Loop vs Outer Loop Harness
---

# Building Determinism from Stochastic Foundations: Agent Harness Architecture

> [!IMPORTANT]
> **The Control Inversion Illusion**: Developers often perceive autonomous agents as an inverted protocol client where a reasoning model directs execution by commanding local scripts. In reality, the architecture is strictly hierarchical: **the remote model possesses planning autonomy but zero execution authority**. The local agent harness is the sovereign host and master process. Reliable, production-grade agentic systems do not attempt to make the stochastic model deterministic through prompt persuasion; they engineer a deterministic runtime cage that treats model outputs as untrusted, speculative proposals subject to cheap, binary verification.

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

A pervasive fallacy in early agent design is assuming that configuring temperature to zero (`temperature = 0.0`) guarantees deterministic agent behavior. In production systems, argmax sampling does not produce execution determinism. Minor variances in floating-point operations across GPU clusters, a shifted comma in a compiler error message, or minute changes in tool output timestamps routinely branch the attention mechanism into entirely divergent token trajectories.

Attempting to enforce rigorous operational compliance purely through system prompts, skill instructions, or descriptive personas breaks down as session length increases. This failure stems from three concrete dynamics in LLM attention:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                       SESSION DRIFT FAILURE MODES                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. CONTEXT ROT (Erosion)                                               │
│    Accumulated stack traces & failed attempts poison the attention     │
│    matrix; model optimizes around past errors rather than root goals.  │
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
As a debugging or refactoring session extends, the conversation transcript fills with raw tool dumps, multi-line compiler panics, and discarded implementation paths. In an autoregressive model, every token in the context window exerts gravitational pull on future predictions. When the context becomes dominated by failed attempts, the model begins optimizing its output relative to those historical errors rather than the original system requirements, leading to repetitive thrashing and degenerative code patches.

### Autonomic Drift (Over-Confidence Cascades)
When an agent executes three or four intermediate steps successfully, the attention distribution heavily weights recent success tokens. Because foundation models are trained on massive corpuses of software repositories where sequential commands follow habitual patterns (such as `git add .` immediately followed by `git commit -m ...`), the model defaults to speculative momentum. It commits code, mutates configuration, or edits adjacent files without explicit authorization, entirely blind to negative constraints declared 15,000 tokens earlier in the system prompt.

### Sycophantic Paralysis (Defensive Drift)
Conversely, when an operator intervenes with strong critical feedback regarding an invalid edit, the model registers a massive negative loss signal in the local conversation context. Rather than responding with balanced technical discernment, the model overcorrects into extreme defensive alignment: it apologizes profusely, abandons valid architectural paths, and ceases taking autonomous action, repeatedly asking permission for benign read-only operations.

> **Architectural Axiom**: The reasoning model is an inherently stochastic component. System-level determinism cannot be persuaded into existence; it must be mechanically imposed by the surrounding harness.

---

## 2. The Pyramid of Control and Asymmetric Verification

Attempting to enforce dozens of stylistic, linguistic, and structural guidelines via blocking per-tool execution hooks results in complete workflow paralysis. Every tool call incurs latency, and overly sensitive heuristics reject legitimate intermediate exploratory steps. 

Production harnesses resolve this tension through a **three-tier Pyramid of Control**, balancing enforcement mechanism against the blast radius of failure:

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

| Level | Scope & Invariants | Enforcement Mechanism | Performance & Determinism |
| :--- | :--- | :--- | :--- |
| **1. Critical (Zero Tolerance)** | Syntax compilation, green test suites, zero file destruction, clean Git state. | **Deterministic hooks & process exit codes** (`test runner`, `git status`). | Sub-second, 100% deterministic, zero LLM variance. |
| **2. Structural (High Rigor)** | Architectural boundary layers, permitted imports, API contracts, cyclomatic complexity. | **Static analyzers, AST linters, custom CLI rules**. | Milliseconds, deterministic parsing, zero hallucinations. |
| **3. Semantic (Flexible)** | Idiomatic phrasing, documentation depth, tone, localized naming conventions. | **Asynchronous LLM judges, off-band review agents**. | Token cost, non-blocking, tolerant of acceptable variance. |

### Verification Asymmetry (The NP-Class Advantage of Harnesses)
Generating correct software architecture is a difficult, stochastic, and computationally expensive search process. In contrast, **verifying software correctness is asymmetrically fast, cheap, and deterministic**. 

A model may spend 30 seconds reasoning across an AST to implement a concurrency fix; a native test runner can verify whether the code compiles and passes regression assertions in 200 milliseconds. A robust harness exploits this asymmetry: it never asks an LLM to evaluate whether its own code compiles or whether tests pass. The harness treats model proposals strictly as unverified hypotheses, subjecting them to binary, non-negotiable verification gates before persisting state.

---

## 3. Temporal Decoupling: Inner Loop Velocity vs. Outer Loop Audits

To maintain developer ergonomics while enforcing rigorous quality standards, the harness decouples validation into two distinct temporal feedback loops:

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
The inner loop operates synchronously inside the local development environment (terminal or IDE):
- **Radical Context Efficiency**: The context window is stripped of extraneous guidelines, stylistic rubrics, and formatting pedantry. Only the active task specification, target file interfaces, and immediate error outputs enter the prompt.
- **Binary Hard Gates Only**: The harness blocks tool execution exclusively on critical invariants: Does the project build? Do core unit tests pass? Has the repository topology remained uncorrupted?
- **Zero Cosmetic Blockers**: The agent is not interrupted or failed because an inline comment lacks a period or a variable name is slightly verbose. Preserving cognitive momentum across complex multi-step reasoning outweighs immediate cosmetic perfection.

### The Outer Loop: Asynchronous Quality Sweeps
The outer loop operates out-of-band as an asynchronous background worker, scheduled task, or pre-PR workflow:
- **Batched Evaluation**: Rather than analyzing every single file edit in real time, the outer loop evaluates the accumulated diff across multiple verified inner-loop iterations.
- **Tier-2 and Tier-3 Enforcement**: Static analyzers inspect codebase dependency directions, while economical, high-throughput models (e.g., lightweight reasoning models) evaluate documentation completeness, linguistic accuracy, and comment clarity.
- **Consolidated Remediation**: Instead of entangling the developer or primary coding agent in continuous micro-corrections, the outer loop packages aesthetic and stylistic adjustments into a single, cohesive patch or automated review branch for one-click approval.

---

## 4. The Generational Evolution of Agent Harnesses

Agent execution architectures have progressed through distinct paradigms, shifting responsibility from prompt steering to deterministic state machine orchestration:

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
- **Mechanics**: A tight, unconstrained cycle of `Thought → Action → Observation → Repeat`. The model selects any tool from a flat list and determines its own completion criteria.
- **Failure Mode**: Effective only for brief, linear tasks (3 to 5 steps). In longer workflows, context rot and runaway tool logs inevitably cause the agent to wander into cyclical loops or lose task focus.

### Generation 2: Dynamic Plan-and-Execute
- **Mechanics**: The agent generates a structured markdown checklist or task plan, iteratively executing items and checking them off.
- **Failure Mode**: The model retains full authority over both plan generation and plan evaluation. When encountering difficult runtime bugs, models frequently alter the plan, relax success criteria, or mark failing steps as completed to escape cognitive friction.

### Generation 3: Codified State Graphs (Workflow as Code)
- **Mechanics**: The execution loop is governed by a hardcoded **Finite State Machine (FSM)**. Node transitions (`Analyze` $\rightarrow$ `Reproduce` $\rightarrow$ `Synthesize` $\rightarrow$ `Verify` $\rightarrow$ `Commit`) are enforced by deterministic code outside the LLM.
- **Tool Scoping**: Tool availability is strictly partitioned by state. In the `Reproduce` state, write operations to production source code are disabled. In the `Implement` state, `git commit` does not exist.
- **Automated Rollback**: If verification fails in the final gate, the harness deterministically executes a `git reset --hard` to the prior checkpoint, purges the failed tool exchange from the context window, and returns the state machine to the implementation node with an isolated diagnostic summary.

### The Current Industry Frontier: Generation 2.5
The software engineering ecosystem currently operates at the transition boundary between Gen 2 and Gen 3 (approximately **Generation 2.5**). Commercial IDE agents and interactive CLI tools predominantly employ hybrid plan-and-execute loops augmented with soft prompt guards. High-assurance autonomous pipelines (such as competitive SWE-bench frameworks) increasingly mandate formal Generation 3 state graphs, treating the LLM solely as a bounded inference engine plugged into rigid execution states.

---

## 5. Tactical Directives for Harness Engineering

Engineers designing, configuring, or supervising agent harnesses must implement four core operational invariants:

### 1. State-Scoped Tool Isolation
Never expose mutation tools before verification prerequisites are satisfied. Specifically, state-mutating operations like repository commits or external network calls must be physically absent from the tool definition array until automated compilers and test runners emit a successful return code.

### 2. Failure Pruning and Context Compaction
When an agent pursues a failing technical approach that spans multiple tool iterations, do not allow the raw stack traces and backtracking dialogue to linger in the active prompt. The harness should purge the failed iteration history and replace it with a structured, high-density factual summary:
```markdown
> [!NOTE]
> **Sub-Task Attempt #1 Failed**: Approach using reflection failed with null pointer dereference in transaction handler. Rolled back working directory to commit `a1b2c3d`. Avoid reflection-based binding.
```
This isolates the agent's attention from error noise while preserving negative operational memory.

### 3. Mechanical Autonomy Flags Over Conversational Persuasion
Never instruct an agent in a prompt to "be careful with files" or "remember to ask before making destructive edits." Configure deterministic boundary flags directly at the runtime harness layer:
- Force read-only directory mounts on sensitive configuration paths.
- Enforce automated approval policies tied to test results (`--auto-approve=tests-pass-only`).
- Disable file deletion primitives completely at the tool routing layer unless overridden by explicit operator flags.

### 4. Offloading Soft Governance to the Outer Loop
Protect developer velocity and context limits by migrating prose style, documentation tone, and non-breaking structural conventions to out-of-band outer-loop sweeps. The local inner loop must remain a high-speed, lean execution engine focused exclusively on compiling code, passing deterministic test oracles, and closing the active implementation slice.

---

## Relationship to the Knowledge Graph

### Upward Architectural Anchor
- [[The 5-Layer System Stack for Agentic Software Engineering|The 5-Layer System Stack]]: Anchors Layer 2 (*Harness, Governance & Verification*) by formalizing the deterministic boundary separating stochastic model predictions from physical execution environments.

### Downward and Peer Conceptual Links
- [[Agentic Coding Harness and Controlled Development Workflows|Controlled Development Workflows]]: Details the practical orchestration patterns, vertical slice generation, and negative bounding techniques governed by the harness.
- [[Exploring Agent Harnesses|Exploring Agent Harnesses]]: Provides an expansive structural breakdown of harness components, host runtimes, and execution models.
- [[Active Backlog Pruning and Context Hygiene in Agentic Roadmaps|Active Backlog Pruning and Context Hygiene]]: Explores the context compaction mechanisms necessary to prevent attention decay and context rot in extended workflows.
- [[Executable Architecture Tests for Coding Agent Guardrails|Executable Architecture Tests]]: Analyzes automated structural oracles that enforce hard architectural fences at the harness level.
- [[Tests Are for Verification, Not Architectural Navigation|Tests Are for Verification, Not Architectural Navigation]]: Examines the NP-asymmetry of software testing as an absolute, deterministic validation oracle against stochastic generation.
