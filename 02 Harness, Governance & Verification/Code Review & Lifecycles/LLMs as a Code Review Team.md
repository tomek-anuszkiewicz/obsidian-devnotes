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

In traditional software development, code review often becomes a bottleneck of human fatigue. Reviewers scan through large diffs, spot a few formatting inconsistencies, overlook subtle concurrency race conditions, and approve the pull request because they are eager to unblock their colleagues.

Deploying language models as an automated code review team fundamentally shifts this dynamic:

> **Code review transforms from passive human inspection into continuous engineering verification—a panel of specialized, relentless agents that actively attempt to falsify the pull request before human sign-off.**

Instead of asking a single prompt to catch every bug, high-assurance teams deploy a **panel of domain-specialist reviewers** (Security, Concurrency, Database Performance, API Compatibility) that generate concrete failure hypotheses, verify them with automated tests, and present synthesized findings to human engineers.

```text
Proposed Pull Request Diff
           │
           ▼
[ Review Router ] ──► Classifies Diff (API, Database, Concurrency, Hot Path)
           │
     ┌─────┴───────────────────────────┬───────────────────────────┐
     ▼                                 ▼                           ▼
[ Security Specialist ]       [ Database Specialist ]     [ Performance Specialist ]
"Forms vulnerability thesis"  "Inspects query plans"      "Generates benchmark"
     │                                 │                           │
     └────────────────────────┬────────┴───────────────────────────┘
                              │
                              ▼
        [ Tool Execution & Hypothesis Verification ]
        (Test Runners / Static Analysis / Profilers / Query Plans)
                              │
                              ▼
            [ Finding Synthesizer & Noise Filter ]
            (Deduplication, confidence gating, test proofs)
                              │
                              ▼
       HUMAN ARCHITECT REVIEWS HIGH-SIGNAL FINDINGS
```

---

## Core Invariants

1. **Hypothesis Generation Over Vague Opinions**: An agentic reviewer must not post speculative comments (*"This might be slow"*). The reviewer must formulate a concrete hypothesis, generate a reproducer test or benchmark, execute it, and report only when the failure is empirically demonstrated.
2. **Relentless Stamina Over Raw Genius**: The primary value of an automated review agent is not superhuman intelligence, but **infinite patience**. An agent applies the same rigorous 30-point security checklist on Friday evening across a 2,000-line diff with the exact same focus as on Monday morning (see [[Agent Advantage -  Relentless, Methodical Work]]).
3. **Specialized Personas Over Monolithic Prompts**: Asking a single general prompt to review an entire pull request causes attention dilution. Route diffs to focused specialists: Database, Security, Concurrency, API Compatibility, and Performance.
4. **Strict Separation of Reviewer and Fixer**: The reviewer agent must remain strictly read-only (`inspect, execute tests, profile`). Giving the reviewer write permissions to fix the code creates confirmation bias: the model bends the code to validate its own assumptions. Fixing must be delegated to an independent agent.
5. **Noise Filtering and Synthesis**: Multiple reviewers run the risk of spamming pull requests with low-value nitpicks. A synthesizer agent must deduplicate findings, filter out unverified observations, and format findings into structured checks.

---

## 1. The Superpower of Methodical Relentlessness

Human attention is a scarce, easily exhausted resource:
- After reading 500 lines of boilerplate, human reviewers skim.
- Complex checks—like verifying that every asynchronous operation propagates cancellation signals or checking that multi-tenant database filters are present on every query path—are tedious to verify manually.
- Reviewers often retreat into superficial formatting debates because identifying architectural race conditions requires heavy mental simulation.

Automated review agents excel precisely where humans struggle:
- They check every file in the diff without skipping.
- They evaluate every database query against query plan analyzers.
- They check API models against contract schemas to detect accidental breaking changes.

---

## 2. Specialized Reviewer Topologies

Rather than using one monolithic prompt, a mature review pipeline uses a router to inspect the AST diff and dispatch focused reviewer personas:

```text
                             Pull Request Diff
                                     │
                                     ▼
                           [ Review Router ]
                                     │
         ┌───────────────────┬───────┴───────────┬───────────────────┐
         ▼                   ▼                   ▼                   ▼
[ Correctness Reviewer ] [ Test Reviewer ] [ Security Reviewer ] [ Specialized Reviewers ]
(Always Active)          (Always Active)   (Auth / Tokens / Web) (Conditionally Routed)
                                                                     │
                                                   ┌─────────────────┼─────────────────┐
                                                   ▼                 ▼                 ▼
                                             [ Database ]     [ Performance ]    [ Public API ]
                                             (ORM / SQL / DDL) (Allocations)      (Contracts / DTOs)
```

### When Specialists Are Triggered
- **Public API / Contracts**: Triggered when public routes, DTOs, or schema definitions change. Checks for backward compatibility, serialization edge cases, and missing validation.
- **Database Access**: Triggered when queries, entity models, or migrations change. Checks for N+1 query patterns, missing database indexes, unbounded table scans, and transaction isolation risks.
- **High-Throughput Hot Paths**: Triggered when core loop or pipeline files change. Monitors memory allocations, unnecessary boxing, and synchronization contention.
- **Authentication & Authorization**: Triggered when auth middleware or user context files change. Verifies tenant boundary isolation, credential handling, and role verification.

---

## 3. The Hypothesis-Verification Protocol

The fastest way for an automated review bot to lose developer trust is comment spam—posting dozens of trivial or incorrect warnings.

To maintain high signal, agents must follow a strict **verification protocol**:

```text
Reviewer Suspects a Bug
           │
           ▼
Formulate Concrete Hypothesis
"The new batch handler creates O(n²) memory allocation when processing large lists."
           │
           ▼
Synthesize Reproducer Test or Benchmark
           │
           ▼
Run Test Against Branch (PR) vs Baseline (main)
           │
  ┌────────┴────────┐
  ▼                 ▼
[ Test Passes ]     [ Test Fails (Bug Confirmed) ]
(Hypothesis false)  (PR allocates 450 KB vs Main 0 KB)
  │                         │
SUPPRESS COMMENT            ▼
                 Post Finding with Reproducer Test as Proof
```

Instead of vague advice, the agent posts objective evidence:

```text
Severity: HIGH | Confidence: HIGH | Category: Performance Regression
Target: OrderProcessingPipeline::ExecuteBatch

Hypothesis Confirmed:
The new stream pipeline allocates an intermediate buffer on every transaction.

Empirical Proof:
- Baseline (main): 1.8 µs per transaction | 0 heap allocations
- Pull Request:   4.2 µs per transaction | 480 bytes heap allocated per transaction
- Production Impact: At 5 million calls/day, this introduces ~2.4 GB of unnecessary garbage collection churn.

Reproduction Benchmark: tests/benchmarks/batch_processing_benchmark
Suggested Fix: Reuse a pre-allocated buffer slice instead of allocating a new array per transaction.
```

---

## 4. Separation of Concerns: Reviewer vs. Fixer

A common failure mode in autonomous harnesses is letting the review agent edit the code directly.

When an agent both reviews and fixes:
- It tends to rationalize its own misunderstandings.
- If it hallucinates a bug, it writes a patch that introduces real complexity to solve an imaginary problem.

The roles must be strictly separated:

```text
┌────────────────────────────────────────────────────────┐
│ Reviewer Agent (Read-Only)                             │
│ • Reads code diffs, specs, and commit history          │
│ • Generates failing reproducer tests                   │
│ • Forbidden from editing source files                  │
└───────────────────────────┬────────────────────────────┘
                            │ Emits verified bug + failing test
                            ▼
┌────────────────────────────────────────────────────────┐
│ Fixer Agent (Write-Only)                               │
│ • Receives failing test and defect description         │
│ • Edits implementation files to make test pass         │
│ • Forbidden from modifying test assertions             │
└───────────────────────────┬────────────────────────────┘
                            │ Proposes patch
                            ▼
┌────────────────────────────────────────────────────────┐
│ Verification Harness                                   │
│ • Runs full regression test suite                      │
│ • Confirms patch passes without regressions            │
└────────────────────────────────────────────────────────┘
```

By keeping the reviewer strictly read-only and enforcing [[Testing in the Model, Agent, LLM Era|The Frozen Oracle Rule]], the system guarantees that fixes are verified objectively.

---

## 5. Noise Filtering and GitHub Integration

Rather than posting twenty uncoordinated comments on a pull request, use a **Synthesizer Agent** to filter and organize findings:

1. **Deduplication**: Merge overlapping comments from different specialists into a single cohesive note.
2. **Confidence Gating**:
   - High Severity + High Confidence $\rightarrow$ Post as inline blocking comment.
   - Medium Severity + High Confidence $\rightarrow$ Add to the pull request summary checklist.
   - Speculative / Unconfirmed $\rightarrow$ Log to internal CI telemetry; do not post to the developer.
3. **Use GitHub Checks Over Comment Floods**: Post status checks (e.g. `Security Review: PASS`, `API Compatibility: PASS`, `Performance Review: FAIL`) with details expandable in the check output. This keeps the PR conversation clean and focused on human discussion.

---

## Practical Rules for Teams

1. **Never let an unverified hypothesis become a comment**: Require the agent to generate a test or query plan before flagging a potential bug.
2. **Keep the review agent read-only**: Let review bots find problems; let developers or separate fixer agents write solutions.
3. **Focus human review on domain intent**: Use machines for mechanical and technical checks so humans can focus on whether the feature makes sense for the business.
4. **Track reviewer precision**: Measure the acceptance rate of agent review comments. If developers reject more than 20% of findings as false positives, tighten the synthesizer prompt.

---

## Related Notes

- **[[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]]**: How LLM reviewers enforce nuanced architectural and domain guidelines that static linters miss.
- **[[Reviewing AI-Generated Code]]**: Best practices for human reviewers overseeing agent-authored pull requests.
- **[[Agent Advantage -  Relentless, Methodical Work]]**: Why procedural stamina and consistency make agents ideal for high-volume review tasks.
- **[[Testing in the Model, Agent, LLM Era]]**: Combining automated review agents with deterministic test suites and frozen oracles.
- **[[Multi-Agent Software Development]]**: Coordinating specialized agent roles across the software development lifecycle.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Integrating automated review checkpoints into CI/CD pipelines.
- **[[Software Entropy and the Zero-Friction Trap]]**: Using automated review gates to prevent unmonitored code generation from degrading code quality.
