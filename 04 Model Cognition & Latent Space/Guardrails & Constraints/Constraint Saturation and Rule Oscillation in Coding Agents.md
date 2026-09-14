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

> [!IMPORTANT] Architectural Invariant: Attention Capacity Limits and Rule Oscillation in Coding Agents
> System prompts and agent rulebooks are subject to strict attention capacity limits. Appending guidelines to patch past agent mistakes follows an exponential decay curve: if an agent satisfies each independent rule with probability $p=0.95$, its probability of simultaneously obeying $M=30$ rules plummets to $0.95^{30} \approx 21.4\%$:
> $$P(\text{Full Compliance}) = \prod_{i=1}^M p_i \approx p^M$$
> Beyond a critical threshold, adding rules triggers **Constraint Oscillation (Rule Thrashing / Whack-a-Mole Engineering)**: the agent refactors to satisfy Rule $A$, inadvertently violates Rule $B$, patches $B$ only to violate $C$, and loops indefinitely. Eliminating rule thrashing requires **Lexicographical Constraint Tiering** (correctness > domain invariants > operational budgets > style), **Sequential Single-Objective Passes**, and **offloading formatting and mechanical invariants to deterministic compilers and linters**.

```text
+----------------------------------------------------------------------------------------------------+
|               CONSTRAINT SATURATION & THE RULE THRASHING CYCLE                                     |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  THE WHACK-A-MOLE OSCILLATION LOOP (Attention Displacement)                                        |
|                                                                                                    |
|            ┌───────────────────────────────────────────────────────────┐                           |
|            │                                                           │                           |
|            ▼                                                           │                           |
|  [Agent applies Driver A] ──► [Violates Driver B]                      │                           |
|            ▲                             │                             │                           |
|            │                             ▼                             │                           |
|  [Re-violates Driver A] ◄── [Violates Driver C] ◄── [Agent fixes for Driver B]                     |
|                                                                                                    |
|  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HARNESS-LEVEL MITIGATIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  |
|                                                                                                    |
|  1. Lexicographical Tiering: Tier 1 (Correctness) > Tier 2 (Boundary) > Tier 3 (Perf) > Tier 4     |
|  2. Sequential Passes: Pass 1: Semantic Logic ──► Pass 2: Refinement ──► Pass 3: Tool Compliance   |
|  3. Mechanical Offloading: Offload formatting, import sorting, and linting to deterministic tools   |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

## Executive Summary & Core Architectural Invariants

1. **The Law of Exponential Compliance Decay**:
   If an agent satisfies each independent rule with probability $p=0.95$, its compound probability of simultaneously obeying $M=25$ rules drops to $p^M \approx 27.7\%$. Adding rules to patch every historical mistake inevitably guarantees that the agent violates at least one constraint on every turn.

2. **Attention Displacement and Rule Thrashing**:
   Transformers possess finite attention capacity. Focusing on a complex local constraint (e.g., zero-allocation memory layouts) mathematically displaces attention from distant guidelines. When corrected for violating Rule $B$, the model myopically optimizes for $B$ at the expense of previously satisfied Rule $A$, causing infinite Whack-a-Mole oscillation.

3. **Lexicographical Constraint Tiering**:
   System rules must be prioritized into strict, non-negotiable tiers (Tier 1: Functional Correctness > Tier 2: Domain Boundaries > Tier 3: Performance Budgets > Tier 4: Cosmetic Formatting). Agents must be explicitly instructed never to sacrifice Tier 1 correctness or Tier 2 boundaries to satisfy Tier 4 conventions.

4. **Single-Objective Sequential Passes Over Monolithic Generation**:
   Attempting to generate code that is simultaneously functionally complete, memory-optimized, styled, and documented in a single turn exceeds cognitive limits. Production workflows decompose execution into sequential passes: Semantic Logic $\to$ Optimization $\to$ Mechanical Compliance.

5. **Deterministic Mechanical Offloading**:
   Rules that can be checked by mechanical compilers, AST formatters, or static analysis tools (linting, line limits, import sorting) must be eliminated from system prompts. Natural language instructions must be reserved exclusively for semantic, contextual architectural invariants.

---

## The Paradox of Rule Accumulation

As development teams mature their setups within an [[Agentic Coding Harness and Controlled Development Workflows|agentic coding harness]], there is an intuitive instinct to solve agent mistakes by adding more guidelines:
- Repository system rules and [[Learning Coding Agents Through Failure-Driven Instructions|failure-driven instruction files]],
- Specialized domain skills (`SKILL.md`),
- Automated static analysis and linting checks,
- Architectural driver checklists (e.g., zero heap allocation, strict immutability, 1:1 file hierarchies, hard line caps),
- Multi-agent review policies.

Initially, adding guidelines improves consistency. But past a critical threshold, **adding more rules actively degrades agent performance and reliability**.

Instead of producing clean code, the agent falls into the **Constraint Oscillation Trap** (also known as *Rule Thrashing* or *Whack-a-Mole Engineering*), which degrades [[LLM Coding Agents Reliability|coding agent reliability]] to near zero:
1. The agent refactors code to satisfy **Driver A** (e.g., inlining a routine for zero-allocation performance).
2. It discovers or is notified that the change violates **Driver B** (e.g., a hard 500-line limit or single-responsibility rule).
3. It refactors to satisfy **Driver B**, which inadvertently violates **Driver C** (e.g., architectural boundary or interface immutability).
4. It patches **Driver C**, re-triggering the violation of **Driver A**.
5. The agent enters an infinite loop, burning tokens while thrashing back and forth between competing constraints, accelerating [[Software Decay and the Hidden Costs of Frictionless AI Code|software entropy and codebase instability]].

---

## The Root Cause: Bounded Rationality and Context Saturation

The crucial insight is that **the rules are often not inherently contradictory in theoretical logic**. A human principal architect with hours of contemplation could theoretically craft a design that harmonizes all criteria.

Rather, the breakdown stems from the agent's **bounded context capacity and attention fragmentation**:

### 1. Multi-Objective Attention Slippage
Transformers do not evaluate 30 competing constraints simultaneously across an entire codebase. When an LLM allocates its attention heads to solving a difficult local constraint (such as low-level memory layout or complex state transitions), its attention to distant semantic guidelines in the prompt degrades. Attention to Constraint A actively displaces focus from Constraints B, C, and D.

### 2. The Multiplicative Failure Rate of Compound Rules
If an agent has a 95% probability of adhering to any single rule in a prompt, the compound probability of satisfying $M$ simultaneous rules drops exponentially:
$$P(\text{satisfying all } M \text{ rules}) = p^M$$
- With 5 rules at 95% compliance: $0.95^5 \approx 77\%$
- With 15 rules at 95% compliance: $0.95^{15} \approx 46\%$
- With 30 rules at 95% compliance: $0.95^{30} \approx 21\%$

In an over-constrained environment, an agent is mathematically almost certain to violate at least one driver on every turn.

### 3. Myopic Local Optimization
Agents optimize locally within the current turn. When prompted with corrective feedback (*"You violated Driver B"*), the model treats Driver B as the high-priority focal point of the current prompt, blinding it to the historical context that motivated the original design under Driver A.

---

## Architectural Manifestations of Rule Thrashing

| Manifestation | What the Agent Does | Underlying Conflict |
| :--- | :--- | :--- |
| **Allocation vs Abstraction Ping-Pong** | Alternates between creating clean wrapper classes and dumping raw structs in hot loops | Clean Architecture vs High-Performance Drivers |
| **File Budget vs Modular Granularity** | Squeezes 5 classes into one file to reduce file count, then splits them into 5 files to obey line limits | Hard Line Limits vs File Touchpoint Budgets |
| **DRY vs Blast-Radius Isolation** | Extracts a shared utility, then unrolls it back into copy-paste code to avoid cross-module coupling | Extreme DRY vs Localized Duplication |
| **Immutability vs State Machine Performance** | Converts mutable buffers to immutable records, encounters GC pressure warnings, reverts to mutable buffers | Functional Purity vs Low-Latency Telemetry |

---

## Harness-Level Solutions: Breaking the Oscillation Trap

To defeat constraint saturation, engineering harnesses must stop treating prompts as infinite garbage cans for rules. We must implement **structural and architectural governance**:

### 1. Hierarchical Constraint Tiering (Rule Prioritization)
Never present 30 rules as flat peers. The harness must enforce an explicit **lexicographical priority order**:

```text
TIER 1: Inviolable Mechanical Invariants
└── Compilation, green test suites, type safety, memory correctness.

TIER 2: Core Domain & Security Invariants
└── Data ownership, transaction boundaries, authorization, zero data loss.

TIER 3: Operational & Performance Budgets
└── Latency limits, heap allocation caps, hot-path inlining.

TIER 4: Soft Ergonomic & Stylistic Guidelines
└── Naming conventions, line limits, comment density, aesthetic formatting.
```
When a conflict occurs, Tier 1 and 2 automatically trump Tier 3 and 4. The agent is explicitly instructed: *"Never sacrifice Tier 1 correctness or Tier 2 boundaries to satisfy Tier 4 formatting."*

### 2. Context-Relevant Dynamic Rule Scoping
Never inject the entire repository rulebook into every prompt. Rules should be **dynamically activated just-in-time**:
- Hot-path optimization rules are loaded **only** when touching files tagged `@performance-critical`.
- API contract rules are loaded **only** when editing controller or endpoint modules.
- General feature development loads at most 3–5 high-level architectural rules.

### 3. Sequential Multi-Pass Decomposition (Separation of Concerns)
Instead of forcing a single agent to produce code that is simultaneously functionally complete, zero-allocation, beautifully formatted, fully documented, and strictly bounded:
Decompose execution into discrete, single-objective pipeline stages:
1. **Pass 1 (Semantics)**: Implement correct business logic and pass behavioral tests (ignoring line counts and micro-optimizations).
2. **Pass 2 (Refinement)**: Optimize memory and execution performance within the verified logic.
3. **Pass 3 (Compliance & Formatting)**: Clean up formatting, verify file boundaries, and run static linters.

Each pass has a single evaluative driver, eliminating multi-objective thrashing.

### 4. Oscillation Detection & Circuit Breakers
The harness must monitor file diffs across retry iterations:
- If the harness detects that file $F$ is oscillating between two AST structures or alternating git diffs across iterations $N$ and $N+2$, it immediately trips a **Circuit Breaker**.
- The harness halts autonomous execution and generates an escalation artifact:
  > *"Rule Oscillation Detected: The agent is thrashing between [Rule A: Line Limit] and [Rule B: Zero Allocations]. Human arbitration required."*

### 5. Offloading Rules to Mechanical Compilers and Formatters
Every rule enforced by an LLM prompt costs attention and token bandwidth. If a rule can be enforced by a deterministic mechanical tool (automated code formatters, static AST linters, compiler flags, architecture unit test runners), **it must be removed from the prompt**.
Reserve the model's limited attention window exclusively for semantic, contextual architectural decisions that cannot be verified by a deterministic compiler.

---

## Key Principles

1. **Rule volume has diminishing and eventually negative returns**: Beyond a certain threshold, adding rules induces thrashing rather than compliance.
2. **Rule failure is driven by bounded context capacity**: Agents fail multi-objective optimization not because rules contradict in theory, but because transformer attention degrades under constraint saturation.
3. **Prioritize hierarchically**: Define explicit constraint tiers so the agent never sacrifices correctness for aesthetic guidelines.
4. **Decompose multi-objective tasks into single-objective passes**: Run correctness, performance, and formatting in sequential stages.
5. **Install harness circuit breakers**: Mechanically detect oscillatory edits and escalate to human arbitration before burning token budgets.

---

## Relationship to the Knowledge Graph

- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Practical loop design, iteration caps, and escalation artifacts that prevent infinite rule thrashing.
- **[[Learning Coding Agents Through Failure-Driven Instructions]]**: Explains why blindly appending rules to `AGENTS.md` creates redundant, contradictory bloat.
- **[[Reviewing AI-Generated Code]]**: Diagnosing when an agent hits its reasoning horizon and starts thrashing superficial patches during review.
- **[[How Context Narrows an AI's Solution Space]]**: How constraints narrow search spaces constructively, and the tipping point where over-constraint causes attention breakdown.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: Imposing mechanical constraints without overloading prompt context.
- **[[LLM Coding Agents Reliability]]**: The statistical inevitability of compound errors when agents attempt to satisfy dozens of simultaneous rules.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Using concise semantic blueprints to focus agent attention rather than spraying dozens of generic rules.
