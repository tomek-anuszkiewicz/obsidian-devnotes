---
title: LLMs as a Code Review Team
tags:
  - code-review
  - ai-agents
  - software-engineering
  - multi-agent
  - quality-assurance
  - testing
aliases:
  - Multi-Agent Code Review
  - Continuous Engineering Verification with LLMs
  - Continuous Falsification Engine
  - Specialized Reviewer Topologies
  - Adversarial Review Pipeline
---

# LLMs as a Code Review Team

> [!IMPORTANT]
> **The Conceptual Shift: Continuous Engineering Verification**: Code review ceases to be a human reading a diff to see if it looks plausible. In the agentic era, code review becomes an **adversarial continuous falsification engine**: a team of specialized, relentless agents that systematically generate failure hypotheses, execute deterministic tools to confirm or refute them, and synthesize high-confidence findings before human review.

```text
Synthetic Diff Proposed
           │
           ▼
[ Review Router ] ──► Classifies Diff (API, Database, Concurrency, Hot Path)
           │
     ┌─────┴───────────────────────────┬───────────────────────────┐
     ▼                                 ▼                           ▼
[ Security Specialist ]       [ Database Specialist ]     [ Performance Specialist ]
"Forms vulnerability thesis"  "Inspects query plans"      "Generates microbenchmark"
     │                                 │                           │
     └────────────────────────┬────────┴───────────────────────────┘
                              │
                              ▼
        [ Tool Execution & Hypothesis Falsification ]
        (Test Runners / Static Analysis / Profilers / EXPLAIN)
                              │
                              ▼
            [ Finding Synthesizer & Filter ]
            (Deduplication, confidence gating, test proofs)
                              │
                              ▼
       HUMAN ARCHITECT REVIEWS SURVIVING DECISIONS
```

---

## Executive Summary & Core Architectural Invariants

1. **Hypothesis Generation vs. Deterministic Proof**: LLMs must not merely offer subjective opinions ("this looks slow"). An agentic reviewer **forms a concrete hypothesis**, generates an automated reproduction test or microbenchmark, runs it against both `main` and the `PR` branch, and reports only when the defect is empirically proven.
2. **Relentlessness Over Genius**: The primary advantage of an automated review agent is not superhuman intelligence, but **inexhaustible stamina**. An agent applies the identical 40-point verification checklist on Friday at 6:00 PM across a 150-file diff with the same mechanical rigor as on Monday morning.
3. **Specialized Topologies Over Monolithic Prompts**: Prompting a single model to "Review this pull request" causes cognitive dilution and rule oscillation. High-assurance systems deploy a router that delegates to domain specialists (Database, Concurrency, Security, Public API Compatibility, Performance).
4. **Strict Separation of Reviewer and Fixer Roles**: The agent identifying problems must remain strictly read-only (`inspect, execute tests, profile`). Granting the reviewer write access creates self-rationalization bias: the model bends the code to validate its own hallucinations. Fixing is delegated to an isolated fixer agent, validated by a third-party test oracle.
5. **Noise Gating and Synthesizer Pipelines**: Seven specialized reviewers emitting uncoordinated findings create pull-request alert fatigue. A centralized synthesizer deduplicates overlap, discards low-confidence observations, and filters out findings disproven by tests.
6. **Multi-Ecosystem Toolchain Orchestration**: Review agents do not replace CI; they orchestrate it. Agents invoke native test runners (`cargo test`, `pytest`, `go test`, `dotnet test`), memory profilers, query plan explainers (`EXPLAIN ANALYZE`), and fuzzing engines to provide empirical data alongside diff comments.

---

## 1. The Superpower of Methodical Relentlessness

Human attention is a perishable, non-renewable resource:
- Human reviewers suffer from cognitive fatigue after reviewing large PRs, repetitive changes, or boilerplate-heavy files.
- Subtle invariants—propagating cancellation tokens, checking tenant authorization filters, handling deserialization backward-compatibility, validating boundary conditions—are easily forgotten under deadline pressure.
- An agentic reviewer executes the same verification protocol every single time:
  - It does not care that this is the 30th pull request of the day,
  - It does not skim because the diff contains 150 files,
  - It relentlessly checks for low-probability, high-consequence failure modes (see [[Agent Advantage -  Relentless, Methodical Work]]).

---

## 2. Specialized Reviewer Topologies & Dynamic Routing

A single general-purpose prompt forces one model to reason simultaneously across dozens of conflicting dimensions. Effective architectures partition review into a modular agent hierarchy:

```text
                             Pull Request Diff
                                     │
                                     ▼
                           [ Review Router ]
                                     │
         ┌───────────────────┬───────┴───────────┬───────────────────┐
         ▼                   ▼                   ▼                   ▼
[ Correctness Reviewer ] [ Test Reviewer ] [ Security Reviewer ] [ Specialized Reviewers ]
(Always Active)          (Always Active)   (Auth / Crypto / Web)  (Conditionally Routed)
                                                                     │
                                                   ┌─────────────────┼─────────────────┐
                                                   ▼                 ▼                 ▼
                                             [ Database ]     [ Performance ]    [ Public API ]
                                             (ORM / SQL / DDL) (Alloc / Latency)  (Contracts / DTOs)
```

### Dynamic Routing Conditions
To optimize token budgets and reduce latency, the router inspects the diff AST and triggers expensive specialists conditionally:
- **Public API / Contract Changed**: Invokes API Compatibility Reviewer (verifies serialization schemas, optionality, HTTP semantics, backward compatibility).
- **Database / Storage Changed**: Invokes Database Reviewer (inspects N+1 queries, locking behavior, transaction scopes, missing indexes, query plans).
- **Hot-Path / Computational Kernels**: Invokes Performance Reviewer (monitors memory allocations, heap boxing, algorithmic complexity $O(n)$, lock contention).
- **Authentication / Tenant Flow**: Invokes Security Reviewer (inspects authorization boundaries, injection vectors, token expiration, secret leakage).

---

## 3. The Hypothesis-Falsification Protocol

Subjective opinions pollute review threads and erode developer trust. Agentic reviewers must adhere to a strict **Scientific Method**:

```text
Reviewer Detects Potential Defect
               │
               ▼
   Formulate Concrete Hypothesis
   "Adding this nested loop creates O(n²) scaling when collection > 1,000 items."
               │
               ▼
   Synthesize Empirical Verification Test / Benchmark
               │
               ▼
   Execute Against Baseline (main) vs. Branch (PR)
               │
      ┌────────┴────────┐
      ▼                 ▼
[ Hypothesis Disproven ] [ Hypothesis Confirmed ]
(Main == PR)             (Main: 2ms, PR: 4.2s)
      │                         │
   SUPPRESS FINDING             ▼
                     Report Finding with Machine Evidence
```

### Reporting with Objective Machine Evidence
Instead of ambiguous prose (*"This might allocate too much memory"*), the agent reports concrete profiling evidence:
```text
Severity: HIGH | Confidence: HIGH | Category: Performance Regression
Target: OrderProcessingPipeline.cs::ExecuteBatch

Hypothesis Confirmed:
The new stream transformation introduces heap allocation per item in the hot path.

Empirical Evidence:
- Baseline (main): 1.8 µs | 0 bytes heap allocated
- Pull Request:   4.2 µs | 480 bytes heap allocated per transaction
- Production Impact: ~10 million invocations/day = ~4.8 GB unnecessary GC garbage/day.

Reproduction Benchmark: tests/perf/BatchProcessingBenchmark.cs
Suggested Remediation: Use pre-allocated span/buffer slices instead of LINQ / stream iterators.
```

---

## 4. Separation of Concerns: Reviewer vs. Fixer vs. Validator

Granting a single agent write permissions to patch the problems it finds creates acute confirmation bias:

```text
┌────────────────────────────────────────────────────────────────┐
│ Reviewer Agent (Read-Only)                                     │
│ - Reads diff, git history, and living specs                    │
│ - Executes test suites, linters, and profilers                 │
│ - Disallowed from editing source files                         │
└───────────────────────────────┬────────────────────────────────┘
                                │ Emits verified finding + failing test
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ Fixer Agent (Write-Only)                                       │
│ - Receives the failing test vector and defect description      │
│ - Synthesizes minimal patch targeting the implementation       │
└───────────────────────────────┬────────────────────────────────┘
                                │ Submits patch
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ Validation Harness (Independent Gate)                         │
│ - Runs full regression suite                                   │
│ - Verifies the patch fixes the defect without side effects     │
└────────────────────────────────────────────────────────────────┘
```

This strict architectural separation prevents models from silently modifying test assertions to excuse broken implementation code (enforcing [[Testing in the Model, Agent, LLM Era|The Frozen Oracle Rule]]).

---

## 5. Noise Suppression & Synthesizer Pipeline

Multiple parallel reviewers inevitably generate overlapping, redundant, or borderline findings. A centralized **Synthesizer Agent** processes all candidate findings before publishing:

```text
Raw Findings from 6 Specialists (e.g., 28 items)
                       │
                       ▼
         [ Deduplication & Merging ]
         (Combines overlapping database and performance findings)
                       │
                       ▼
        [ Confidence & Severity Matrix ]
        - HIGH Severity + HIGH Confidence   ──► Inline PR Comment (Blocks Merge)
        - MEDIUM Severity + HIGH Confidence ──► PR Review Summary Item
        - LOW Confidence / Speculative      ──► Suppressed to Background Audit Log
                       │
                       ▼
         [ Final Synthesized Review ] (e.g., 4 High-Signal Findings)
```

By enforcing strict confidence gating, engineering teams ensure that automated reviews maintain a high signal-to-noise ratio, preserving developer goodwill and trust.

---

## 6. The Multi-Layered Future: Continuous Engineering Verification

When machines relentlessly handle repeatable invariant verification, human engineers elevate to the architectural summit:

| Layer | Responsibility | Primary Actor |
| :--- | :--- | :--- |
| **Mechanical Syntax & Lint** | Formatting, typing, style, nullability | Compilers & Linters |
| **System Invariants** | Concurrency safety, memory allocation limits, query plans | Multi-Agent Review Team |
| **Hypothesis Proofs** | Generating tests and benchmarks proving defects | Specialized Testing Agents |
| **Domain & Intent Judgment** | Product semantics, business model fidelity, architectural trade-offs | Human Software Architect |

Code review is no longer a bureaucratic pause before merging; it is a **continuous engineering verification pipeline** that actively attempts to falsify every code change before it touches production reality.

---

## Relationship to the Knowledge Graph

- **[[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]]**: How review agents evaluate informal, architectural, and business-level rules.
- **[[Reviewing AI-Generated Code]]**: Principles for human oversight, mental model construction, and skeptical review of agent diffs.
- **[[Multi-Agent Software Development]]**: Coordinating specialized reviewer personas (security, performance, domain logic, test coverage).
- **[[Testing in the Model, Agent, LLM Era]]**: Combining automated review agents with deterministic test suites, frozen oracles, and mutation testing.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Integrating multi-agent review checkpoints into CI/CD delivery harnesses.
- **[[Agent Advantage -  Relentless, Methodical Work]]**: The foundational cognitive asymmetry between human fatigue and agentic procedural stamina.
- **[[Software Entropy and the Zero-Friction Trap]]**: Preventing unreviewed code accumulation from degrading repository maintainability.
