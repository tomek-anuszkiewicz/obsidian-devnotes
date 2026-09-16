---
title: LLM Capability, Reliability, and the Shape of Progress
tags:
  - ai
  - llm
  - ai-agents
  - reliability
  - hallucinations
  - software-engineering
  - agents
aliases:
  - "Where Are LLMs on the Progress Curve?"
  - LLM Capability and Reliability S-Curve
created: 2026-08-23
---

# LLM Capability Reliability and the Shape of Progress

## Summary

Large language models are improving rapidly, but their progress is not a monolithic march toward zero errors. In practice, different capabilities advance along decoupled trajectories:

- **Single-task performance** on bounded, well-specified problems is already high.
- **Reasoning, code generation, tool invocation, and multimodality** are advancing quickly through inference-time compute and execution feedback.
- **Agent task horizons**—the length and complexity of multi-step tasks a model can attempt—are expanding at an exponential rate.
- **Error calibration, robustness, and uncertainty detection** improve much more slowly.
- **General-purpose infallibility** remains an unrealistic target because real-world software engineering operates under incomplete information, shifting requirements, and ambiguous specifications.

The practical state of frontier models today can be summarized simply:

> We are high on the curve of single-turn capability, in the steep acceleration phase of agentic task horizons, but still low on the curve of unassisted real-world reliability.

```text
       Capability vs. Operational Reliability Over Step Depth
 100% +-------------------------------------------------------------------+
      |               Raw Benchmark & Single-Task Horizon Capability      |
      |             ..................................................... |
      |          .·´                                                      |
  75% |        .·´                                                        |
      |      .·´                                                          |
      |     .·                                  Operational Reliability   |
  50% |    .·                                   (Unmitigated P = p^N)     |
      |   .·                                    ---------------------\    |
      |  .·                                                           \   |
  25% | .·                                                             \  |
      | ·                                                               \ |
   0% +-------------------------------------------------------------------+
      Step 1      Step 5              Step 10                     Step 20

      [ Probabilistic LLM ] ---> [ Deterministic Harness & Oracles ] ---> [ Verified Output ]
      (Generates Solutions)      (Compilers, Linters, Test Runners)       (Guaranteed State)
```

Reliability in autonomous workflows does not come from waiting for an infallible base model. It comes from enclosing probabilistic model inference inside deterministic verification harnesses, automated test suites, and strict execution sandboxes.

---

## Capability is Not Reliability

Two statements that sound similar describe fundamentally different operational realities:

1. A model **can** solve a difficult task.
2. A model will **reliably** solve every similar task.

The first statement is becoming true across software engineering at an astonishing rate. The second remains far from solved.

This divergence explains why modern models can generate complex, architecturally sound distributed systems code, yet simultaneously introduce a trivial, catastrophic bug: an inverted boolean, an undocumented API parameter, a subtly false concurrency assumption, or a clean, idiomatic implementation of the wrong business rule.

These failures are rarely spectacular, obvious hallucinations. They are **soft hallucinations**: subtle errors embedded within an otherwise coherent, persuasive, and syntactically flawless implementation. Because the surrounding context reads naturally and passes superficial visual inspection, soft hallucinations are far more dangerous in production environments than overt syntax failures.

---

## A Simplified History of Model Generations

```
GPT-3 (2020–2022)        GPT-3.5 (2022–2023)        GPT-4 / Claude 3 (2023–2024)   Reasoning Models & Agents (2024–2026)
-----------------        -------------------        ----------------------------   -------------------------------------
Fluent text generation   Instruction following      Deep multi-file analysis       Inference-time search & reasoning
Small code snippets      Interactive chat utility   Tool and API integration       Self-correction via test execution
High instruction drift   Believable broken code     Pair programming partner       Persistent scratchpads & git tools
Invented APIs            Little error awareness     Requires constant review       Bounded by runtime harnesses
```

### GPT-3 Era: Persuasive Text Generation (2020–2022)
Models in this era were primarily statistical predictors of tokens trained on raw internet text:
- Generated fluent prose and answered broad domain questions.
- Recalled broad factual knowledge and wrote small, isolated code snippets.
- Performed basic text transformations and pattern completion.

However, they suffered from rapid instruction drift, routinely invented non-existent library methods, and could not maintain a coherent multi-step plan. They were creative text generators, not dependable software collaborators.

### GPT-3.5 and Early Chat Models: Useful Assistants (2022–2023)
Reinforcement Learning from Human Feedback (RLHF) turned completion engines into conversational assistants:
- Instruction-following improved significantly, allowing structured zero-shot prompting.
- Models became genuinely useful for drafting boilerplate, explaining concepts, and writing simple functions.
- They frequently produced code that looked completely correct to human eyes but failed at runtime.
- They possessed virtually no internal calibration regarding their own knowledge boundaries.

### GPT-4 and Claude 3 Era: Capable Collaborators Under Supervision (2023–2024)
Substantial leaps in parameter scale, context window capacity, and instruction fine-tuning delivered genuine engineering utility:
- Reliable analysis of complex, multi-file codebases across 100k+ token contexts.
- Planning and executing refactors across multiple interdependent modules.
- Identifying trade-offs between architectural patterns and explaining legacy code.
- Correcting syntax errors when fed compiler error outputs directly.

These models became indispensable daily drivers for experienced developers, but they still operated without an internal execution loop. Every output required rigorous line-by-line review.

### Reasoning Models and Agents (2024–2026)
The breakthrough in this phase did not come from pre-training on more raw text. It came from allocating compute at inference time—allowing models to generate hidden reasoning tokens, explore alternative search paths, and interact directly with execution environments:
- Inference-time reasoning chains to evaluate edge cases before emitting answers.
- Direct access to local shells, file systems, browsers, and terminal test runners.
- The execution of iterative **change → observe → correct** loops.
- Structured context curation, persistent scratchpads, and git-aware diffing.
- [[Agentic Coding Harness and Controlled Development Workflows|Agentic harnesses]] that sandbox, validate, and constrain model operations.

This represents a structural shift. A single raw inference pass from a model may still contain errors, but an agent running inside a harness can confront its output with compilers, linters, and unit tests, systematically repairing its own mistakes before presenting the final diff.

---

## Why Benchmarks Appear to Improve So Dramatically

Stanford’s AI Index recorded that performance on SWE-bench rose from roughly 4.4% in 2023 to over 70% by late 2024. By 2026, benchmarks like SWE-bench Verified were approaching saturation.

```text
 Benchmark Performance (%)
  100% +-------------------------------------------------------+
       |                                      SWE-bench Verified
       |                                  ......................
   75% |                                .·´
       |                              .·´     SWE-bench Pro
       |                            .·´       (Contamination-resistant)
   50% |                          .·´         ------------------
       |                        .·´
   25% |                      .·´
       |         SWE-bench  .·´
    0% +-----------·´------------------------------------------+
       2023                 2024                 2025       2026
```

This rapid benchmark climb does **not** mean that autonomous agents can solve 80% of real-world software engineering issues. It means that models have saturated a specific, bounded class of historical GitHub issues.

When a benchmark saturates, harder, contamination-resistant evaluations reveal the true operational limits. For example, OpenAI reported that GPT-5.2 Thinking reached approximately 80% on SWE-bench Verified, but dropped to 55.6% on SWE-bench Pro—a suite designed to resist training-set leakage and evaluate broader repository-level reasoning.

Every benchmark follows a predictable lifecycle:
1. **Introduction**: A difficult, realistic benchmark is released; baseline frontier models score in the single digits.
2. **Rapid Ascent**: Fine-tuning, prompt engineering, agentic search, and reasoning tokens rapidly improve scores.
3. **Saturation**: Top models bunch together near 80–90%, and the benchmark loses its ability to separate frontier systems.
4. **Recalibration**: A more rigorous benchmark is introduced, exposing blind spots, edge-case failures, and brittle assumptions.

This dynamic explains why two seemingly contradictory realities coexist:
- Benchmark progress is advancing faster than any previous technology cycle.
- The same models that achieve record benchmark scores still fail in production due to undocumented internal dependencies, subtle race conditions, or unstated business assumptions.

---

## Error Compounding in Multi-Step Workflows

Autonomous agent workflows consist of discrete, sequential decisions: parsing requirements, finding relevant files, editing code, running builds, parsing error logs, and refining edits.

In an unmitigated sequential workflow without external validation, overall success is governed by geometric compounding:

$$
P_{\text{success}} = \prod_{i=1}^{N} p_i
$$

Assuming an optimistic, uniform per-step correctness probability $p$:

$$
P_{\text{success}} = p^N
$$

If an agent executes a 20-step workflow where each step has a 95% probability of being correct:

$$
0.95^{20} \approx 35.8\%
$$

Even if per-step accuracy rises to 99%:

$$
0.99^{20} \approx 81.8\%
$$

Across an extended 100-step operational trajectory:

$$
0.99^{100} \approx 36.6\%
$$

```text
 Multi-Step Success Probability (P = p^N)
  100% +-------------------------------------------------------+
       | *---\_
       |       \__  p = 0.99 per step
   75% |          \----\_
       |                 \----\__
   50% |   o                     \----\_
       |    \--\_                       \----\_
   25% |         \---_  p = 0.95 per step      \---\_
       |              \------\____                   \--------
    0% +--------------------------\----------------------------+
       N = 1       N = 10         N = 25                      N = 100
```

This math explains why an LLM that feels brilliant in an interactive chat session can fail completely when left to run autonomously overnight.

In practice, execution environments alter this dynamic in two opposite ways:

1. **Compensating Feedback**: Deterministic feedback loops (compilers, linters, unit tests, schema validators) intercept errors before they compound. If step 4 breaks the build, the harness feeds the compiler error back to the model, giving it a bounded opportunity to self-correct before proceeding to step 5.
2. **Correlated Failure Cascades**: Errors in real systems are rarely independent. If an agent misinterprets an authorization rule in step 2, that poisoned assumption enters its context window. Steps 3 through 20 may execute with flawless internal logic, but they are building on a fundamentally broken foundation.

---

## The Task-Horizon Curve

METR (Model Evaluation and Threat Research) evaluates autonomous capability using the **task horizon**: the duration of a task—measured in the time a skilled human engineer would require—that an AI agent can complete with a **50% success probability**.

```text
 Human Task Duration Completed with 50% Success
 16 hrs +----------------------------------------------------+
        |                                                 .·´
        |                                             .·´
  8 hrs |                                         .·´
        |                                     .·´
  4 hrs |                                 .·´
        |                             .·´
  2 hrs |                         .·´
        |                     .·´
  1 hr  |                 .·´
        |             .·´
  0 hrs +-------------·´-------------------------------------+
        2020         2022         2024         2026
```

METR’s data shows that this frontier task horizon has roughly doubled every seven months. Frontier models have progressed from solving 5-minute single-file bugs to handling complex multi-hour development tasks involving multi-file edits, package updates, and regression testing.

However, the critical constraint is the **50% success threshold**. A 50% completion rate demonstrates high technical capability, but it is insufficient for production systems that demand high reliability.

| Success Rate | Operational Paradigm | Production Role |
|:---|:---|:---|
| **50%** | Non-deterministic trial; multiple rollouts required | Speculative prototyping, Best-of-$N$ offline exploration |
| **80%** | Interactive pairing; continuous human oversight | Developer copilot; agent drafts, engineer reviews |
| **95%** | Guarded automation; automated sandboxing and tests | Automated dependency updates, low-risk bug fixes with CI gates |
| **99.9%+** | True production automation; zero human-in-the-loop | Mission-critical pipelines, live infrastructure modifications |

Closing the gap between a 50% task horizon and a 99.9% production threshold cannot be achieved simply by waiting for base models to scale up. As success approaches 100%, long-tail edge cases dominate: undocumented environment quirks, subtle race conditions, inconsistent third-party APIs, and ambiguous requirements.

---

## The Three Decoupled Curves of Progress

Model evolution is best understood as three distinct, overlapping curves moving at different speeds:

```text
 Capability Level
  High ^                                          Sequence of S-Curves
       |                                          (Saturating Benchmarks)
       |                                    _.-''''-._      _.-''''-._
       |                                _.-'          '-._.-'
       |                     _.-''''-._.-'
       |                 _.-'
       |              .-'                     Exponential Task Horizons
       |           .·´                        (Gross Autonomous Duration)
       |        .·´                     .·´
       |     .·´                    .·´
       |   .·                   .·´
       |  .                 .·´               Slow Reliability Tail
       | ·              .·´                   (Ambiguity, Edge Cases, Dark Knowledge)
       |·          .·´                        ---------------------------------------
   Low +-------------------------------------------------------------------------> Time
```

### 1. The Sequence of Benchmark S-Curves
Benchmarks do not follow a single linear trajectory. They follow a jagged sequence of individual S-curves. A model family rapidly climbs an evaluation (e.g., HumanEval, SWE-bench Verified), saturates it, and appears to plateau—until a harder, cleaner benchmark exposes the next tier of limitations.

### 2. The Exponential Task-Horizon Curve
The volume and duration of coherent, multi-step work an agent can perform before derailing is growing exponentially. This expansion is driven by extended context windows, faster inference, scratchpad reasoning, and tool use. This is the most commercially disruptive trend: tasks that once required constant developer intervention can increasingly be handed off as asynchronous jobs.

### 3. The Slow Reliability-Tail Curve
Progress along the long-tail reliability curve is fundamentally slower. Reducing an error rate from 20% down to 10% requires straightforward model scaling and instruction tuning. Driving an error rate from 2% down to 0.1% requires solving hard, open-world problems:
- Incomplete or contradicting technical documentation.
- Institutional business rules that exist only in senior engineers' heads.
- Legacy system side effects that do not appear in local test suites.
- Latent bugs exposed only under production concurrency.
- Code changes that are technically flawless implementations of the wrong architectural abstraction.

---

## Why General Infallibility is a Flawed Metric

Infallibility in real-world software systems is not merely difficult to engineer; it is conceptually ill-defined:

- **Requirements are inherently incomplete**: Software requirements rarely specify every edge condition. When a human engineer encounters an ambiguity, they consult stakeholders or make an informed architectural bet. A model must either guess or ask.
- **Ground truth drifts**: Code libraries deprecate methods, upstream APIs alter rate limits, and security vulnerabilities emerge after training cutoffs.
- **The usefulness vs. caution trade-off**: A model can achieve near-zero hallucination rates by refusing to act whenever it encounters uncertainty. However, an agent that aborts execution every time an environment variable is ambiguous is useless in practice:

$$
\text{Usefulness} \longleftrightarrow \text{Caution}
$$

A model tuned for high caution will refuse valid, creative solutions; a model tuned for high usefulness will make plausible, unverified guesses. Production engineering requires balancing this trade-off using external rules rather than relying on model intuition alone.

---

## What Improves Next: The Shift Toward Verification

The near-term future of software automation will not be defined by a model that never hallucinates. It will be defined by systems that systematically identify and repair their own mistakes before touching production:

```
[ Natural Language Intent ]
           │
           ▼
┌───────────────────────────────────────────────────────────┐
│              Agentic Harness Architecture                 │
│                                                           │
│   ┌───────────────────┐        ┌──────────────────────┐   │
│   │   Reasoning LLM   │◄──────►│ Deterministic Tools  │   │
│   │ (Proposes Diffs)  │        │ (Bash, LSP, Linters) │   │
│   └─────────┬─────────┘        └──────────┬───────────┘   │
│             │                             │               │
│             ▼                             ▼               │
│   ┌───────────────────────────────────────────────────┐   │
│   │              Verification Gatekeepers             │   │
│   │   - Headless Compilers & Static Type Checkers     │   │
│   │   - Local Sandbox Unit & Integration Tests        │   │
│   │   - Invariant Checks & Mutation Testing           │   │
│   └─────────────────────────┬─────────────────────────┘   │
└─────────────────────────────┼─────────────────────────────┘
                              │
               Passes All Gates?
               ├── Yes ──► [ Git Commit & PR Created ]
               └── No  ──► [ Rollback / Human Escalation ]
```

1. **Deterministic Verification Loops**: Running builds, executing unit suites, verifying API contracts with OpenAPI schemas, and using the Language Server Protocol (LSP) to flag type mismatches before committing code.
2. **Contradiction Detection**: Cross-checking reasoning chains against tool outputs to spot internal inconsistencies before taking action.
3. **Explicit Goal Tracking**: Maintaining structured scratchpads that track completed sub-tasks, pending verifications, and architectural constraints across long operational horizons.
4. **Epistemic Classification**: Distinguishing between verified repo facts (read from disk), assumptions (inferred from context), and missing knowledge (requiring human confirmation).
5. **Speculative Execution (Best-of-$N$)**: Spawning multiple isolated attempts in parallel git worktrees, running test suites against each branch, and selecting the cleanest passing solution.
6. **Human-in-the-Loop Escalation**: Recognizing when an edit touches sensitive security boundaries, billing pipelines, or architectural foundations, and explicitly halting to request human confirmation.

The human engineer's primary responsibility shifts from manually typing code to defining verifiable specifications: writing rock-solid integration tests, configuring lint rules, bounding sandbox permissions, and reviewing pull requests.

---

## Why Software Engineering Automates Faster Than Other Knowledge Work

Software engineering is uniquely suited to agentic automation because code operates within an environment of rich, immediate, and unambiguous feedback mechanisms:

- **Compilers and Type Checkers**: Provide binary pass/fail verification on syntax, interface contracts, and nullability.
- **Automated Test Suites**: Mechanically validate functional correctness and protect against regressions.
- **Language Server Protocol (LSP)**: Surfaces missing imports, dead references, and type mismatches instantly.
- **Ephemeral Sandboxes**: Containerized environments (Docker, Firecracker microVMs) allow agents to safely execute code, inspect runtime behavior, and evaluate real logs.

Tasks possessing clear deterministic verifiers advance far faster than tasks that rely on subjective human evaluation.

```text
                  Automation Velocity by Task Type
   Faster Automation Velocity           Slower Automation Velocity
   (Strong External Verifiers)          (Subjective / Hidden Context)
  ◄──────────────────────────────────────────────────────────────────►
   • Bounded bug fixes                  • Product feature discovery
   • Version migrations                 • Undocumented business logic
   • Well-tested refactoring            • Cross-team consensus building
   • Boilerplate API endpoints          • Multi-year architecture planning
   • Infrastructure as Code (IaC)       • Maintainability & readability trade-offs
```

### Fast-Moving Areas
- **Bounded Bug Fixes**: A failing test provides an unambiguous target. The agent edits code until the test passes without breaking existing suites.
- **Framework and Dependency Migrations**: Clear syntax transformation rules verified immediately by the compiler and test runners.
- **Refactoring under Deep Test Coverage**: Code can be restructured aggressively because the regression safety net is automated and unambiguous.
- **Spec-First API Development**: Implementing endpoints from explicit OpenAPI/gRPC schemas, where inputs, outputs, and validation rules are strictly typed.

### Slower-Moving Areas
- **System Architecture**: Making structural trade-offs for requirements that will not exist for another two years.
- **Discovering Product Intent**: Identifying that the feature requested by a client will not actually solve their operational bottleneck.
- **Reconstructing Dark Knowledge**: Excavating unwritten organizational assumptions and institutional history that never made it into comments or docs.
- **Balancing Clean Abstractions**: Knowing when code duplication is preferable to the wrong shared abstraction.

---

## Where We Stand Today

The industry is not approaching a performance ceiling; it is navigating overlapping architectural waves:

- **Traditional Pre-training**: Scaling model parameter counts and raw web text is encountering physical and economic limits (data exhaustion, power availability, diminishing returns per watt).
- **Inference-Time Compute**: Allocating test-time compute to search, backtrack, and evaluate multiple candidate solutions yields massive capability leaps on complex reasoning tasks.
- **Agentic Runtime Harnesses**: Surrounding probabilistic models with terminal access, git worktrees, testing suites, and LSP tools provides massive practical reliability gains without changing model weights.

We have moved past the initial phase where the miracle was that an LLM could converse and generate syntax. We are now in the operational phase: engineering dependable systems that direct, constrain, and verify multi-step autonomous work.

Because models produce increasingly persuasive and well-structured output, their failures are becoming harder to catch visually. Trust can easily outpace actual reliability. As a result, the critical engineering question has fundamentally changed:

```text
  Yesterday's Question:  "Can the model write this code?"
  Today's Question:      "What deterministic verification proves this code is correct?"
```

---

## Practical Architectural Takeaway

LLMs are probabilistic reasoning engines. They should never be treated as deterministic components in an enterprise architecture.

For serious agentic automation, operational reliability must be enforced by the surrounding platform:

1. **Hermetic Sandboxing**: Execute agent actions inside disposable microVMs or containers with strict network controls and filesystem boundaries.
2. **Explicit Verification Oracles**: Never accept a code diff based on the model's claim that it works. Require clean build outputs, passing linters, and green unit/integration tests.
3. **Branch-Level Isolation**: Direct agents to work in isolated git worktrees, preventing them from corrupting local working state during failed multi-step attempts.
4. **Least-Privilege Tooling**: Restrict terminal commands to bounded scripts (e.g., specific test runners, formatters, and git commands) rather than granting raw root shell access.
5. **Observable State and Execution Traces**: Log every intermediate thought, tool call, stdout/stderr stream, and file diff to allow rapid post-mortem debugging of failed agent runs.
6. **Hard Escalation Boundaries**: Automatically halt execution and page human operators whenever an agent encounters ambiguous requirements, security-sensitive code paths, or irreversible production actions.

The model provides probabilistic reasoning and code generation. The **[[Agentic Coding Harness and Controlled Development Workflows|Agentic Harness]]** provides deterministic verification, enforcement, and reliability.

---

## Related Notes

- **[[Reliability of LLM Coding Agents]]**: Practical failure modes, soft hallucinations, and architectural recovery paths for autonomous coding agents.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Designing deterministic control environments, test harnesses, and execution sandboxes for agents.
- **[[Testing in the Model, Agent, LLM Era]]**: Adapting testing strategies, mutation testing, and deterministic verification for non-deterministic model outputs.
- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Identifying semantic deceits, incorrect library parameters, and plausible bugs in generated code.
- **[[How Reasoning Models Explore and Evaluate Solutions]]**: Test-time compute, Monte Carlo tree search, and verification heuristics in frontier reasoning architectures.
- **[[Designing APIs for LLM-Generated Integration Code]]**: Structuring internal libraries and interfaces to reduce agent error rates through strict type safety and clear contracts.
- **[[Improving AI Models - From Scaling to Agent-Generated Training Data]]**: How synthetic execution data, RL environments, and self-correction loops train frontier models.
- **[[AI Productivity Is Limited by the Delivery System]]**: Why raw model capability cannot translate to organizational throughput without mature CI/CD and verification pipelines.
- **[[LLM Agents and Institutional Memory]]**: Preserving architectural intent, operational context, and technical decisions across extended agent sessions.
- **[[Exploring Agent Harnesses]]**: Designing contamination-resistant benchmarks, regression suites, and realistic testbeds for coding agents.

---

## Sources

- [Stanford AI Index 2025 — Technical Performance](https://hai.stanford.edu/ai-index/2025-ai-index-report/technical-performance)
- [Stanford AI Index 2026](https://hai.stanford.edu/ai-index/2026-ai-index-report)
- [METR — Task-Completion Time Horizons of Frontier AI Models](https://metr.org/time-horizons/)
- [METR — Clarifying Limitations of Time Horizon](https://metr.org/notes/2026-01-22-time-horizon-limitations/)
- [METR — Measuring AI Ability to Complete Long Software Tasks](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)
- [OpenAI — Why Language Models Hallucinate](https://openai.com/index/why-language-models-hallucinate/)
- [OpenAI — Introducing GPT-5.2](https://openai.com/index/introducing-gpt-5-2/)
