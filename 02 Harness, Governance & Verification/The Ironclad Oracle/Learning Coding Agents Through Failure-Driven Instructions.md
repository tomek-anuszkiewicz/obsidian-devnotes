---
title: Learning Coding Agents Through Failure-Driven Instructions
tags:
  - ai-agents
  - agentic-coding
  - continuous-improvement
  - prompt-engineering
  - knowledge-distillation
  - software-engineering
aliases:
  - Failure-Driven Agent Learning
  - Instruction Tuning from Coding Failures
  - Procedural Memory for Coding Agents
  - Eval-Driven Instruction Engineering
  - Dual Optimization Loops
---

# Learning Coding Agents Through Failure-Driven Instructions

> [!IMPORTANT]
> **The Core Thesis**: Instead of treating agent instructions as static prompts or appending ad-hoc rules into a bloated config file, **instructions must be treated as versioned, testable engineering artifacts that evolve through failure analysis**. The ultimate goal of an autonomous harness is not merely to fix broken code through repeated brute-force loops, but to maximize **First-Pass Success** by building an organizational **procedural memory** that prevents entire classes of architectural and domain errors.

```text
Prompt Engineering ──► Instruction Engineering ──► Eval-Driven Optimization ──► Organizational Procedural Memory
```

---

## Executive Summary & Core Architectural Invariants

1. **The Dual Optimization Loop**: Software development with coding agents operates across two nested loops:
   - **Inner Loop (Code Level)**: The agent repairs transient implementation defects against deterministic compiler, lint, and test signals.
   - **Outer Loop (Instruction Level)**: The system analyzes post-task failures and human review dissents, extracts generalizable lessons, and refines repository instructions so future agents avoid the mistake entirely.
2. **First-Pass Success as the Sovereign Metric**: Raw eventual success is an insufficient metric; brute-forcing seven repair loops wastes tokens and human attention. Systems optimize for:
   $$\text{Utility} = \text{Implementation Quality} - \sum (\text{Iterations} + \text{Token Overhead} + \text{Review Friction} + \text{Regression Risk})$$
3. **Instructions as Code (Not Append-Only Sprawl)**: Naively appending every failure to a flat instructions file leads to context saturation, contradictory rules, and rule oscillation. Instructions must be versioned, tested against regression suites, compressed, and pruned.
4. **Dynamic Behavioral Retrieval (RAG for Agent Steering)**: Rather than loading hundreds of accumulated lessons into every prompt, systems dynamically retrieve relevant operational guidelines based on task domain, architectural layer, and touched subsystems.
5. **High-Leverage Human Review**: Human review shifts from repetitive mechanical linting to authoritative negative knowledge curation. When a human explains a subtle domain or architectural error once, the system formalizes it into persistent instructions and tests, compounding organizational capability over time.

---

## 1. The Dual Optimization Hierarchy: Inner Code vs. Outer Instruction Loops

```text
Outer Loop: Organizational Learning (Eval-Driven Instruction Tuning)
┌────────────────────────────────────────────────────────────────────────┐
│ Task Definition + Versioned Instruction Set (vN)                       │
│     │                                                                  │
│     ▼                                                                  │
│ Inner Loop: Implementation Synthesis                                   │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ Agent Synthesizes Code ──► CI / Test Oracle ──► Pass / Fail        │ │
│ │      ▲                                                │            │ │
│ │      └────────── Stochastic Repair Loop ──────────────┘            │ │
│ └────────────────────────────────┬───────────────────────────────────┘ │
│                                  │ (Task Completed or Failed)          │
│                                  ▼                                     │
│ Analyze Root Cause Failure ──► Extract Invariant ──► A/B Eval Suite   │
│                                  │                                     │
│                                  ▼                                     │
│              Promote Optimized Instruction Set (vN+1)                  │
└────────────────────────────────────────────────────────────────────────┘
```

### The Inner Loop: Automated Implementation Repair
As examined in [[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]], the baseline coding loop leverages immediate deterministic feedback:
- Compiler and typechecker errors,
- Deterministic unit and integration test vectors,
- Static analysis, security linters, and architectural boundaries.

The agent loops locally until the deterministic harness turns green. However, relying exclusively on this inner loop treats every task as an amnesic event: the agent makes the same architectural missteps on Monday that it made the previous Friday, burning compute to rediscover boundaries.

### The Outer Loop: Continuous Instruction Refinement
The outer loop abstracts beyond the immediate pull request:
1. **Failure Ingestion**: Captures failures where the agent required multiple iterations, violated an unwritten architectural rule, or received human review corrections.
2. **Root-Cause Generalization**: Distinguishes between localized code bugs and missing contextual constraints.
3. **Candidate Synthesis**: Drafts candidate instruction updates or architectural non-goals (see [[Negative Knowledge and Explicit Architectural Dissents]]).
4. **Offline Evaluation**: Tests candidate instructions against a historical suite of representative tasks to ensure the change improves first-pass yield without inducing regressions or rule oscillation.

---

## 2. Abstracting Domain Failures: An Architectural Case Study

Consider a task assigned to an autonomous coding agent:
> *"Implement an API endpoint that queries and returns historical customer orders."*

### Naive Implementation & Architectural Failure
The agent generates a solution that passes unit tests, but violates architectural layering:

```text
[ Transport Layer (HTTP Controller / RPC Handler) ]
                       │
                       │ (Direct coupling: architectural violation)
                       ▼
         [ Persistence Layer (ORM / Database) ]
```

An automated architectural rule or human reviewer flags the PR: *Transport handlers must remain pure adapters and are forbidden from querying persistence engines directly; they must delegate to application-layer command/query handlers.*

### Transforming the Failure into Procedural Memory

```text
Observed Failure:
Transport adapter bypassed the application boundary to query database persistence directly.

Underlying Architectural Defect:
The agent lacked explicit knowledge of the repository's hexagonal / clean architecture boundaries.

Extracted Boundary Invariant:
Transport adapters (HTTP/RPC/CLI) are interface translators only. They validate transport payloads 
and dispatch to domain application handlers; they must never import or invoke persistence gateways directly.
```

By formalizing this rule, the outer loop ensures that subsequent agents across all services generate the decoupled architecture on their very first pass:

```text
[ Transport Layer ] ──► [ Application Handler ] ──► [ Domain / Persistence ]
```

---

## 3. The Sovereign Metric: First-Pass Success & Optimization Trade-offs

Raw eventual completion is an economically naive metric. An agent that reaches a solution on attempt #8 often generates bloated, defensive code while consuming excessive tokens and wall-clock time.

### Key Performance Indicators
- **First-Pass Success Rate (FPSR)**: The percentage of tasks where the agent generates an acceptable, green PR without needing corrective inner loops.
- **Iteration Depth**: Average number of compile/test/repair cycles per task.
- **Token Efficiency**: Total input/output tokens consumed per merged feature.
- **Cognitive Load on Human Reviewers**: Hours of senior engineering attention required to audit PRs.

$$\text{Instruction Score} = \frac{\text{Functional Correctness} \times \text{Architectural Fidelity}}{\text{Iterations} \times \log(\text{Prompt Token Cost})}$$

---

## 4. Avoiding Instruction Sprawl: Eval-Driven Hygiene

The most dangerous anti-pattern in agent prompt management is the **Append-Only Trap**:
```text
Failure Occurs ──► Append New Rule to Instructions ──► File Reaches 1,000 Lines ──► Context Saturation & Rule Oscillation
```

As documented in [[Constraint Saturation and Rule Oscillation in Coding Agents]], models overwhelmed by massive, unorganized prompt rules suffer cognitive degradation. Instructions must be governed with the same rigor as production software:

```text
                         Agent Failure Event
                                  │
                                  ▼
                        Extract Core Invariant
                                  │
                                  ▼
           Check for Semantic Duplication / Contradictions
                                  │
                                  ▼
          Generate Candidate Formulations (Short vs. Explanatory)
                                  │
                                  ▼
            Evaluate on Holdout Suite (Regression Verification)
                                  │
                     ┌────────────┴────────────┐
                     ▼                         ▼
             [ Improves FPSR ]         [ Degrades / Neutral ]
                     │                         │
                     ▼                         ▼
             Promote to Repo           Discard Candidate
```

### A/B Testing Rule Formulations
Different expressions of the identical architectural invariant produce dramatically different model behaviors:

| Formulation Type | Instruction Example | FPSR | Iterations | Context Overhead |
| :--- | :--- | :---: | :---: | :---: |
| **Negative Proscription** | *"Do not query database contexts inside transport controllers."* | 84% | 1.9 | Low |
| **Architectural Rationale** | *"Transport controllers are interface adapters. They must delegate all persistence operations to application handlers."* | 91% | 1.4 | Moderate |
| **Procedural Step-by-Step** | *"1. Identify application handler. 2. Place query logic in handler. 3. Call handler from controller."* | 92% | 1.3 | High |

The winning formulation is not necessarily the most prescriptive; it is the one that balances cognitive clarity with minimal token consumption.

---

## 5. Architectural Memory: Retrieval-Augmented Steering (Behavioral RAG)

As an enterprise accumulates hundreds of validated architectural invariants, loading every rule into every prompt saturates the model's working memory. 

Organizations must deploy **Behavioral Retrieval**: partitioning rules into modular, domain-specific packs and dynamically retrieving them based on the task's context envelope:

```text
instructions/
├── architecture/
│   ├── boundary-enforcement.md
│   ├── messaging-topologies.md
│   └── persistence-gateways.md
├── runtimes/
│   ├── concurrency-cancellation.md
│   ├── allocation-limits.md
│   └── serialization-pipelines.md
├── domain/
│   ├── billing-invariants.md
│   ├── order-state-machine.md
│   └── identity-tenancy.md
└── verification/
    ├── integration-harness.md
    └── property-fuzzing.md
```

When an agent is assigned to *"Update payment retry backoff"*, the harness dynamically retrieves:
1. `architecture/boundary-enforcement.md`
2. `runtimes/concurrency-cancellation.md`
3. `domain/billing-invariants.md`

This delivers surgical, high-density steering instructions without global context pollution.

---

## 6. Transforming Human Review into Compounding Organizational Capital

Traditional code review treats human corrections as ephemeral, single-use interventions:
```text
Traditional Model:
Agent Makes Error ──► Human Explains Flaw ──► Agent Patches PR ──► Knowledge Lost in Git History
```

Learning-oriented engineering harnesses convert every human review correction into enduring organizational capital:
```text
Compounding Model:
Agent Makes Error ──► Human Explains Flaw ──► Knowledge Extracted into Formal Invariant
                             │
                             ▼
              Added to Behavioral Regression Suite
                             │
                             ▼
              Future Agents Immunized Against Entire Error Class
```

When a principal architect spends 15 minutes explaining why an implicit state-machine transition violates downstream billing guarantees, that explanation is not discarded. It is distilled into an architectural rule, verified against the eval suite, and embedded into the agent's procedural memory.

---

## Relationship to the Knowledge Graph

- **[[Agentic Coding Harness and Controlled Development Workflows]]**: The physical execution harness that injects versioned instructions and evaluates pass/fail metrics.
- **[[Constraint Saturation and Rule Oscillation in Coding Agents]]**: The mathematical and cognitive foundation explaining why instructions must be pruned, compressed, and retrieved selectively.
- **[[Negative Knowledge and Explicit Architectural Dissents]]**: How failure-driven instruction learning systematically builds the repository's Negative Knowledge Base ($K^-$).
- **[[Testing in the Model, Agent, LLM Era]]**: Deterministic test suites and verification oracles as the foundational inner loop providing automated signal.
- **[[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]]**: Decision criteria for determining whether a failure demands an inline code patch, a specification rewrite, or an instruction update.
- **[[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]]**: How learned instruction rules are integrated into pre-merge automated agent reviewers.
- **[[What Should Organizations Preserve from AI-Assisted Development]]**: Capturing rejected trajectories and instruction evals as high-value strategic assets.
