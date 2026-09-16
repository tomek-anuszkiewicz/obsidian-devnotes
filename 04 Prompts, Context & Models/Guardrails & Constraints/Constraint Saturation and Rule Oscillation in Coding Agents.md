---
title: Constraint Saturation and Rule Oscillation in Coding Agents
tags:
  - ai-agents
  - software-engineering
  - prompt-engineering
  - code-review
  - system-design
  - agentic-harness
  - bounded-rationality
aliases:
  - Rule Thrashing in Agentic Coding
  - The Over-Constrained Agent
  - Constraint Oscillation Trap
  - Whack-a-Mole Rule Thrashing
---

# Constraint Saturation and Rule Oscillation in Coding Agents

> [!IMPORTANT] Core Engineering Reality: Attention Capacity Limits and Rule Oscillation
> System prompts and agent instructions have hard attention limits. Patching every edge-case bug by appending another rule to your instructions triggers an exponential compliance drop. If an agent has an independent 95% chance ($p=0.95$) of following any single rule, its probability of following $M=30$ rules across a generation drops to roughly 21%:
> $$P(\text{Full Compliance}) = \prod_{i=1}^M p_i \approx p^M$$
> Past a critical threshold, adding rules triggers **Constraint Oscillation** (rule thrashing or whack-a-mole engineering). The agent edits code to satisfy Rule A, breaks Rule B in the process, patches B only to violate Rule C, and spins in an expensive loop. Fixing this requires **Lexicographical Constraint Tiering** (correctness > domain invariants > operational budgets > style), **Sequential Single-Objective Passes**, and **pushing all formatting and mechanical checks down to deterministic compilers and linters**.

```text
+----------------------------------------------------------------------------------------------------+
|                         CONSTRAINT SATURATION & THE RULE THRASHING CYCLE                           |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  WHACK-A-MOLE OSCILLATION LOOP (Attention Displacement)                                            |
|                                                                                                    |
|            ┌───────────────────────────────────────────────────────────┐                           |
|            │                                                           │                           |
|            ▼                                                           │                           |
|  [Agent satisfies Driver A] ──► [Breaks Driver B]                      │                           |
|            ▲                             │                             │                           |
|            │                             ▼                             │                           |
|  [Re-violates Driver A]    ◄── [Breaks Driver C] ◄── [Agent fixes Driver B]                        |
|                                                                                                    |
|  HARNESS-LEVEL MITIGATIONS                                                                         |
|                                                                                                    |
|  1. Lexicographical Tiering: Tier 1 (Correctness) > Tier 2 (Boundary) > Tier 3 (Perf) > Tier 4     |
|  2. Sequential Passes: Pass 1: Core Logic ──► Pass 2: Refinement ──► Pass 3: Tool Checks           |
|  3. Tool Offloading: Push formatting, line caps, and import sorting to automated tooling          |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

---

## Core Engineering Realities

### 1. The Math Behind Exponential Compliance Decay
Assuming an agent has an optimistic 95% chance ($p=0.95$) of adhering to any individual constraint in your prompt, compound compliance drops off a cliff as the rule count grows:
$$P(\text{satisfying all } M \text{ rules}) = p^M$$
At $M=25$ rules, the compound probability of total compliance is $0.95^{25} \approx 27.7\%$. If your engineering team keeps appending instructions to patch past agent blunders, you guarantee that the model will violate at least one constraint on every single generation.

### 2. Attention Displacement and Rule Thrashing
Transformers operate on finite attention budgets. Forcing a model to track complex local mechanics—such as cache alignment, zero-copy buffer layouts, or precise lifetime scopes—mechanically displaces its attention from high-level architectural rules parked higher up in the prompt context. When test feedback informs the agent that it broke Rule B, it over-indexes on B, immediately violates Rule A, and enters an infinite loop.

### 3. Lexicographical Constraint Tiering
Never throw rules at an agent as a flat list of equal requirements. You need an explicit priority stack:
$$\text{Tier 1: Correctness} \succ \text{Tier 2: Domain Boundaries} \succ \text{Tier 3: Performance Budgets} \succ \text{Tier 4: Style/Formatting}$$
Make it unambiguous in the prompt harness: the agent must never break Tier 1 logic or Tier 2 security boundaries just to appease Tier 4 style guides.

### 4. Sequential Single-Objective Passes Over Monolithic Generation
Asking an agent to emit code that is functionally complete, memory-optimized, styled, fully documented, and statically verified in a single turn inevitably fails. Production harnesses break execution down into discrete stages: **Business Logic** $\to$ **Performance Optimization** $\to$ **Automated Formatting and Linting**.

### 5. Push Predictable Checks to Tooling
If a rule can be enforced by a compiler flag, a linter, an AST visitor, or a formatter (such as import ordering, maximum line lengths, or naming conventions), delete it from your system prompt. Natural language instructions must be reserved exclusively for domain logic and high-level architectural trade-offs that static tools cannot evaluate.

---

## The Paradox of Rule Accumulation

When teams set up an [[Agentic Coding Harness and Controlled Development Workflows|agentic coding harness]], their default reaction to an agent mistake is to add another rule to the repository instructions. 

Over a few sprints, the harness gets weighed down with:
- Expanding system instructions and [[Learning Coding Agents Through Failure-Driven Instructions|failure-driven instruction files]],
- Sprawling skill definitions (`SKILL.md`),
- Static analysis checklists dumped into markdown prompts,
- Architectural mandates (zero heap allocation, rigid immutability patterns, 1:1 file-to-class mappings, strict 300-line limits),
- Multi-agent review policies.

Early on, adding a handful of rules helps eliminate basic mistakes. But past a certain density, **stacking more rules makes the agent less reliable, not more**.

The agent gets trapped in **Constraint Oscillation** (also called *rule thrashing* or *whack-a-mole engineering*), tanking [[LLM Coding Agents Reliability|coding agent reliability]]:

1. The agent refactors code to hit **Driver A** (e.g., inlining a routine to eliminate an allocation on a hot path).
2. The harness test suite or linter reports a violation of **Driver B** (e.g., a hard 400-line-per-file limit or a single-responsibility modularity check).
3. The agent splits the code to satisfy **Driver B**, which inadvertently violates **Driver C** (e.g., an architectural boundary prohibiting cross-package internal imports).
4. The agent patches **Driver C**, which forces it to re-introduce the dynamic allocation from **Driver A**.
5. The agent loops indefinitely, burning tokens and context window capacity while thrashing between conflicting goals, accelerating [[Software Decay and the Hidden Costs of Frictionless AI Code|software entropy and codebase instability]].

---

## Root Causes: Attention Budgets and Context Saturation

On paper, your engineering constraints rarely contradict each other. A senior systems engineer given sufficient time could easily design an architecture that satisfies every single requirement.

The failure happens because an LLM does not reason like a human engineer with an external notepad. It is constrained by **finite context capacity and attention fragmentation**:

### 1. Multi-Objective Attention Slippage
Transformers do not simultaneously weigh thirty competing constraints across a complex codebase. When a model dedicates its attention heads to solving a dense, localized problem—like managing pointer arithmetic, handling concurrent state transitions, or mapping a tricky relational query—its attention to distant system prompt instructions degrades. Fulfilling Constraint A actively pushes Constraints B, C, and D out of effective focus.

### 2. The Multiplicative Failure Rate of Compound Rules
If an agent has a 95% chance of respecting any single rule, compound reliability plummets as the rules accumulate:
$$P(\text{satisfying all } M \text{ rules}) = p^M$$

| Number of Rules ($M$) | Compliance per Rule ($p$) | Compound Probability ($p^M$) |
| :--- | :--- | :--- |
| 5 rules | $0.95$ | $\approx 77.4\%$ |
| 15 rules | $0.95$ | $\approx 46.3\%$ |
| 30 rules | $0.95$ | $\approx 21.5\%$ |

In an over-constrained system prompt, the model is mathematically primed to violate at least one architectural rule on nearly every turn.

### 3. Myopic Local Optimization
LLMs prioritize the immediate turn context. When you inject corrective feedback (*"You broke Driver B: max file length exceeded"*), the model treats Driver B as the primary objective for its next generation. In hyper-focusing on Driver B, it forgets the design constraints and historical context that shaped its solution for Driver A two turns earlier.

---

## Architectural Manifestations of Rule Thrashing

Below are four common oscillation loops seen in production repositories when prompt constraints conflict:

| Manifestation | What the Agent Does | Underlying Conflict |
| :--- | :--- | :--- |
| **Allocation vs. Abstraction Ping-Pong** | Alternates between creating clean object-oriented wrapper classes and unwrapping raw structs in hot execution loops. | Clean Architecture mandates vs. Zero-Allocation/Low-Latency performance budgets. |
| **File Budget vs. Modular Granularity** | Squeezes five classes into a single file to keep total file count down, then splits them across five files when warned about line count caps. | Hard line limits vs. Single-responsibility / touchpoint budgets. |
| **DRY vs. Blast-Radius Isolation** | Deduplicates shared logic into a common utility package, then unrolls it back into copy-pasted implementations when warned about cross-module coupling. | Rigid DRY enforcement vs. Module boundary isolation. |
| **Immutability vs. State Machine Throughput** | Converts mutable buffers into immutable record types, hits garbage-collection or memory churn warnings, and immediately reverts to mutable buffers. | Functional immutability rules vs. High-throughput runtime constraints. |

---

## Harness-Level Solutions: Breaking the Oscillation Trap

To eliminate constraint saturation, stop treating your system prompt like an unbounded catch-all for every historical failure. Enforce structural isolation in the execution harness:

### 1. Hierarchical Constraint Tiering
Never feed rules to an agent as an unranked, flat list. The harness must declare an unambiguous, lexicographical priority order:

```text
TIER 1: Inviolable Technical Invariants
└── Clean compilation, passing tests, strict memory safety, type checking.

TIER 2: Core Domain & Security Invariants
└── Data integrity, explicit transaction scopes, authorization checks, zero data loss.

TIER 3: Operational & Performance Budgets
└── Latency SLAs, allocation limits, query count caps, hot-path optimization.

TIER 4: Ergonomics & Style
└── Naming conventions, line caps, file structures, comment formatting.
```

When two rules collide, Tier 1 and Tier 2 win every time. Configure your harness prompt with clear instructions:
> *"Never compromise Tier 1 correctness or Tier 2 domain boundaries to satisfy Tier 4 formatting or line limits."*

### 2. Context-Relevant Dynamic Rule Scoping
Do not feed your entire engineering handbook into every single agent run. Load constraints **just-in-time** based on the files being touched:
- Hot-path memory guidelines load **only** when touching modules matching `src/core/engine/**` or files flagged with `@performance-critical`.
- API validation and payload constraints load **only** when editing controllers, routes, or schema definitions.
- Baseline feature tasks run with a lean prompt containing no more than three to five core architectural guidelines.

### 3. Sequential Multi-Pass Decomposition
Stop asking a single agent to deliver code that is functionally correct, fully optimized, styled, and documented in one shot. Break execution into a discrete pipeline:

```text
[Raw Feature Prompt]
         │
         ▼
┌──────────────────┐
│ Pass 1: Logic    │ ──► Focus purely on functional correctness and passing unit tests.
└──────────────────┘     Ignore line limits, formatting, and micro-optimizations.
         │
         ▼
┌──────────────────┐
│ Pass 2: Refine   │ ──► Profile and optimize hot paths, clean up memory allocations,
└──────────────────┘     and enforce performance budgets on the working code.
         │
         ▼
┌──────────────────┐
│ Pass 3: Tooling  │ ──► Run auto-formatters (e.g., Prettier, Ruff), sort imports,
└──────────────────┘     and execute deterministic linter fixes.
```

Each stage targets a single, isolated objective, which prevents multi-objective attention thrashing.

### 4. Oscillation Detection and Circuit Breakers
Your agent harness should track file diffs and AST changes across internal retry loops:
- If the harness detects that file `F` is oscillating between two AST shapes or generating cyclic git diffs across iterations $N$ and $N+2$, it should immediately trip an internal **Circuit Breaker**.
- The harness stops the loop and raises an explicit error:
  > *"Rule Oscillation Detected: The agent is thrashing between [Rule A: 300-Line Limit] and [Rule B: Zero Allocations]. Aborting loop. Requires human arbitration."*

### 5. Offload Mechanical Checks to Deterministic Tools
Every rule an LLM tracks consumes attention and token budget. If an invariant can be checked by a compiler, a linter, a code formatter, or an architecture unit test (like ArchUnit or custom AST scripts), **strip it from the prompt**.
Save the model's limited attention window for business domain architecture and structural choices that deterministic tools cannot evaluate.

---

## Practical Rules of Thumb

1. **More rules yield diminishing, then negative returns**: Past a modest threshold, every rule added to a prompt increases the probability of constraint oscillation.
2. **Context saturation drives rule failure**: Agents do not drop constraints because the rules logically conflict on paper. They drop them because their attention mechanisms degrade under multi-objective saturation.
3. **Establish an explicit hierarchy**: Define constraint tiers so the model never sacrifices functional correctness or security to appease aesthetic formatting rules.
4. **Decompose generations into single-objective steps**: Run correctness passes, performance optimizations, and static formatting in sequential, isolated stages.
5. **Add harness-level circuit breakers**: Monitor diff hashes across turns. If the agent alternates between the same two implementations across iterations, break the loop and alert the engineer.

---

## Graph Connections

- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Practical loop construction, iteration limits, and escalation patterns designed to prevent infinite rule thrashing.
- **[[Learning Coding Agents Through Failure-Driven Instructions]]**: The systemic risks of appending rules to `AGENTS.md` whenever an edge-case bug occurs.
- **[[Reviewing AI-Generated Code]]**: Spotting when an agent hits its reasoning limit and starts generating superficial patches back and forth during reviews.
- **[[How Context Narrows an AI's Solution Space]]**: Using constraints constructively to narrow search spaces, and identifying the tipping point where over-constraint degrades attention.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: Enforcing mechanical constraints via deterministic tooling without polluting prompt context.
- **[[LLM Coding Agents Reliability]]**: The math behind compound error rates when models are forced to juggle dozens of concurrent rules.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Replacing long lists of generic rules with lean, task-specific semantic blueprints to focus model attention.
