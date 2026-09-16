---
title: Improving AI Models — From Scaling to Agent-Generated Training Data
tags:
  - ai-scaling
  - synthetic-data
  - training-data
  - model-training
  - reinforcement-learning
  - agent-generated-data
aliases:
  - Scaling Laws to Synthetic Data
  - Agent-Generated Training Data
---

# Improving AI Models - From Scaling to Agent-Generated Training Data

The historical narrative around AI model progress is often framed as a brute-force exercise: more parameters, larger datasets, and massive compute clusters. 

That mental model is increasingly outdated. 

While raw scaling kickstarted the modern LLM era, the mechanics driving frontier capability have fractured into multiple distinct, compounding vectors:

```text
more parameters + more data + more compute
                ↓
better data curation and training efficiency
                ↓
instruction tuning, alignment, and preference learning
                ↓
reasoning models and test-time compute scaling
                ↓
tool orchestration, runtime harnesses, and agent environments
                ↓
trajectory feedback from real-world engineering work
```

The next leap in capability will not come solely from training a trillion-parameter dense model on an even larger scrape of the public internet. It will come from fundamentally richer training loops that blend inference-time search, deterministic verification, and end-to-end problem-solving trajectories.

---

## Phase One: Classical Pre-Training Scaling

Early transformer progress was defined by empirical power-law scaling. The recipe was straightforward:

- Scale the parameter count of the network.
- Scale the volume of scraped web tokens.
- Scale the floating-point operations (FLOPs) allocated to the pre-training run.

Early scaling papers (such as Kaplan et al.) suggested that loss scaled predictably with compute and model size, leading teams to build massive models that were often severely undertrained. 

The Chinchilla findings (Hoffmann et al.) recalibrated the industry by demonstrating that parameter count alone was an inefficient lever. Many first-generation models were capacity-rich but data-starved. For a given compute budget, optimal performance required scaling tokens and parameters in roughly equal proportions.

This shifted the core engineering question from:

> *How large can we make the model?*

to:

> *How compute-optimal is the balance between parameter capacity, token volume, and data quality?*

Pre-training remains foundational. It compresses world knowledge, syntactic structures, and broad domain representations into latent weight distributions. But as public web corpora approach exhaustion, treating pre-training scaling as the sole engine of progress yields rapidly diminishing returns.

---

## Instruction Tuning: Decoupling Latent Knowledge from Usability

The arrival of Supervised Fine-Tuning (SFT), Reinforcement Learning from Human Feedback (RLHF), and Direct Preference Optimization (DPO) revealed a critical architectural reality:

```text
latent knowledge compressed in pre-trained weights
                     !=
the operational ability to retrieve and apply that knowledge
```

A 70-billion-parameter base model might have the theoretical capacity to solve a nuanced systems architecture problem, but when prompted, it defaults to raw token continuation—hallucinating plausible-sounding blog post transitions or repeating boilerplate. Conversely, a smaller 8B or 14B model fine-tuned on high-quality instruction pairs and preference data can consistently outperform an unaligned giant on practical tasks.

Post-training acts as an indexing mechanism. It does not teach the model new fundamental world facts; instead, it shapes:

- Precise instruction adherence and schema compliance (e.g., producing strict JSON without markdown wrappers).
- Turn-by-turn conversational consistency.
- Calibration between certainty and refusal boundaries.
- Structured analytical framing prior to emitting an answer.

Aligning models to human preferences made them usable, but it also exposed a ceiling: models remained passive, single-turn token generators constrained by fixed forward-pass compute.

---

## Reasoning and Test-Time Compute: Scaling at Inference

Historically, "compute scaling" was synonymous with *training-time compute*: how many months a cluster of H100s burned through tokens before checkpoint finalization.

Reasoning models inverted this constraint by operationalizing **test-time compute**.

```text
Traditional Generation:
Prompt ───────────────────────────────► Static Forward Pass ──► Output Token Stream

Test-Time Compute:
Prompt ──► [ Internal Exploration / Thought Stream ] ──► Verified Output
           ├── Hypothesis Generation
           ├── Intermediate Step Verification (PRMs)
           ├── Branch Pruning & Backtracking
           └── Self-Correction
```

Instead of committing immediately to the first probable token sequence via greedy decoding, the model spends variable inference compute to explore solution spaces. Under the hood, this involves:

1. **Chain-of-Thought and Deliberation Tokens**: The model emits an explicit internal reasoning trajectory before generating the user-facing output.
2. **Search and Backtracking**: Generating multiple intermediate candidates, evaluating them against internal heuristics or Process Reward Models (PRMs), and discarding flawed logical branches.
3. **Dynamic Resource Allocation**: Spending milliseconds on trivial syntax lookups, but spending several minutes of continuous inference compute unrolling an intricate concurrent programming bug.

This decouples runtime capability from the static base model footprint. An inference system allowed to spin through thousands of test-time tokens to verify intermediate states will consistently outperform a massive static model executing a single, unverified forward pass.

---

## Agentic Environments: Bridging Models into Execution Runtimes

When models are deployed into software engineering, they stop operating as pure text engines and begin functioning as execution components inside an operating environment:

```text
+-----------------------------------------------------------------------+
|                         AGENT RUNTIME HARNESS                         |
|                                                                       |
|   +-------------------+                     +---------------------+   |
|   |                   |   Tool Invocations  |                     |   |
|   |  Reasoning Model  | ──────────────────► | Filesystem & Git    |   |
|   |   (Search/Plan)   | ◄────────────────── | Compilers & Linters |   |
|   |                   |     Tool Output     | Test Runners (CI)   |   |
|   +-------------------+    (State Feedback) | Debuggers & APIs    |   |
|                                             +---------------------+   |
+-----------------------------------------------------------------------+
```

The functional system is no longer just the model weights. The system is the composite loop:

```text
model + reasoning trace + tool harness + local environment + feedback loops
```

In this setup, separating "raw model capability" from "agent capability" becomes counterproductive. A model that fails to write a complex, multi-file database migration script in a single shot can still deliver a production-ready patch when wired into a runtime loop:

```text
inspect schema
     ↓
write migration draft
     ↓
execute database migration in sandbox
     ↓
compiler / constraint violation detected
     ↓
parse migration error log
     ↓
adjust foreign key sequence
     ↓
re-run migration and run integration suite
     ↓
verify clean test run
```

The system's practical intelligence scales dramatically because the runtime harness provides deterministic reality checks that intercept and correct the model's stochastic errors.

---

## AI Work Itself as the Next Training Frontier

The explosion of coding agents is generating a category of training data that previously never existed at scale.

Traditional code training datasets rely on static snapshots:

```text
repository snapshot ──► final polished source code
```

The model sees only the destination. It never sees the missteps, the compiler errors, the dead-end architectural approaches, or the iterative refinements that produced the final commit.

Agent-driven software development produces end-to-end execution traces:

```text
system requirement
        ↓
initial implementation attempt
        ↓
compiler failure (e.g., type mismatch in concurrent pipeline)
        ↓
stack trace inspection and internal correction
        ↓
unit test assertion failure (e.g., edge case on empty buffer)
        ↓
targeted patch
        ↓
peer review comment: "This breaks invoice immutability after capture"
        ↓
architectural refactor respecting business invariants
        ↓
clean test suite and successful integration build
```

This trajectory contains far more operational signal than raw source code. It explicitly captures:

- The initial flawed hypothesis.
- The mechanical failure that invalidated it.
- The diagnostic step used to understand the error.
- The domain constraint provided by human review.
- The delta that bridged the broken state to the working state.

Training on this data teaches models *how to engineer*, not just *what code looks like*.

---

## Human Corrections as High-Density Training Signals

Consider a standard interaction between an engineer and a coding agent:

```text
Agent:
Mutates the order price on an existing line item after the transaction has settled.

Human:
"This is invalid. Once an order reaches 'Settled' state, line items are immutable. 
Any adjustment requires appending a new credit or debit line item to preserve the 
ledger audit trail."
```

This single interaction provides an extraordinarily dense training vector:

```text
contextual problem 
  + invalid code attempt 
  + mechanical/business failure mode 
  + explicit architectural constraint 
  + corrected implementation
```

This interaction is exponentially more valuable than training on an isolated snippet of an accounting library. It captures the boundaries, the edge cases, and the *why* behind architectural patterns.

The same principle applies to detailed specifications provided upstream. When an engineer defines explicit operational invariants, memory limits, and failure modes before code generation, they provide a structured blueprint for traversing the solution space.

Capturing these human-in-the-loop interactions across millions of developer hours builds a training corpus that directly targets the exact failure modes of current models.

---

## Deterministic Verification: Software Engineering's Unfair Advantage

A major bottleneck in reinforcement learning for language models is the "oracle problem": evaluating whether an open-ended essay, marketing copy, or policy recommendation is good requires subjective, noisy human judgment.

Software engineering does not suffer from this bottleneck. Verification is cheap, automated, and deterministic.

```text
                               +─────────────────────────+
                               |     Agent Generation    |
                               +─────────────────────────+
                                            │
                                            ▼
                               +─────────────────────────+
                               |   Deterministic Gates   |
                               +─────────────────────────+
                               │ • Compiler / Type Check │
                               │ • Static Linters & AST  │
                               │ • Unit & Property Tests │
                               │ • Integration Sandboxes │
                               │ • Mutation Testing      │
                               │ • Memory/CPU Profilers  │
                               +─────────────────────────+
                                            │
                      ┌─────────────────────┴─────────────────────┐
                      ▼                                           ▼
            [ Verification Failed ]                     [ Verification Passed ]
                      │                                           │
         Capture error log as feedback               Retain as verified training
         loop for agent self-correction             trajectory for RL fine-tuning
```

An execution harness can interrogate generated code with unambiguous, mechanical checks:

```text
compilation        : SUCCESS (rustc 0 errors)
type-check         : SUCCESS (mypy --strict passed)
unit test suite    : 184 / 184 PASSED
mutation score     : 91% mutants killed
p99 latency        : -4.2ms improvement
memory footprint   : 0 allocation leaks detected
```

Because verification is mechanical, we can run large-scale reinforcement learning environments without human evaluators in the loop. The compiler, test suites, and profilers serve as an objective ground-truth reward mechanism.

---

## Synthetic Data: Controlled Exploration vs. Model Collapse

There is a widespread misconception that training models on model-generated data inherently causes catastrophic degradation—often referred to as "model collapse" or autophagous loops.

That degradation happens when an unguided model loops over its own unverified outputs:

```text
Unverified Synthetic Degradation:
model generates noisy output
       ↓
unverified tokens dumped into training set
       ↓
next model learns and amplifies subtle hallucinations
       ↓
distributional collapse (diversity lost, errors compounded)
```

The verified feedback loop operates on an entirely different premise:

```text
Verified Synthetic Generation:
model generates N candidate implementations (stochastic exploration)
       ↓
deterministic verifiers (compilers, unit tests, linters) evaluate candidates
       ↓
failed attempts routed back for diagnostic correction or discarded
       ↓
verified candidate solutions paired with reasoning trajectories
       ↓
next model trains strictly on mathematically or empirically validated paths
```

Synthetic data is only toxic when it lacks an objective filtering oracle. When paired with mechanical verification, synthetic generation becomes a structured search across an engineering solution space. The model explores; the deterministic tooling selects.

---

## The Evolutionary Curriculum of Coding Agents

This combination creates an accelerating, self-improving operational loop:

```text
frontier model improves
       ↓
powers a more reliable coding agent
       ↓
agent is deployed against harder, messier enterprise codebases
       ↓
agent encounters novel real-world edge cases and failures
       ↓
humans and automated tooling provide corrective feedback
       ↓
high-fidelity failure/recovery trajectories are captured
       ↓
next generation trains on verified resolution arcs
```

Today's models help build the exact datasets required to train their successors.

Crucially, this shifts the data moat. The public web—open-source repositories, Stack Overflow, public documentation—is largely picked clean. The highest-density software data is private:

- Deep internal git histories showing non-trivial refactors.
- Pull request code reviews explaining business logic and edge cases.
- Production incident post-mortems mapping unexpected runtime failures back to subtle code bugs.
- CI/CD build telemetry and distributed trace logs.

These artifacts represent empirical contact with real-world production environments. Models trained on these dynamics learn to navigate real systems rather than clean room toy problems.

---

## Turning Present Failures into Tomorrow's Training Sets

Consider a task that frequently trips up contemporary agents:

> *"Refactor our billing service from an immediate database write model to an outbox pattern with transactional guarantees, while ensuring zero downtime across a rolling deploy."*

Today, an agent will likely miss an edge case: it might forget backward-compatible serialization for inflight queue messages, or misconfigure the outbox polling lock.

When an engineer intervenes:

```text
agent patch
    ↓
staging deployment failure / CI integration test timeout
    ↓
engineer review: "You cannot change the payload schema without a fallback deserializer. 
Old workers running during the rolling deployment will drop messages."
    ↓
agent incorporates constraint and introduces versioned envelopes
    ↓
staging verification succeeds
```

Every time this sequence occurs, an invaluable training artifact is forged. It documents the exact boundary where the model failed, the physical reality of the execution environment, and the corrective insight required to bridge the gap.

Failures experienced by current agents are not lost compute. When logged and curated properly, they become the precise curriculum for the next model's post-training.

---

## Compounding Progress Curves

Rather than tracking progress along a single axis of raw pre-training compute, real-world systems capability is the product of multiple overlapping curves:

```text
Vector                       Trajectory    Primary Mechanism
──────────────────────────────────────────────────────────────────────────
Base Pre-Training            Linear        Diminishing returns on public web tokens;
                                           focus shifts to efficiency and architecture.

Test-Time Compute            Exponential   Dynamic search, process reward models, 
                                           and internal reasoning unrolling.

Deterministic Verification   Accelerating  Compilers, linters, and property tests 
                                           acting as automated ground-truth oracles.

Agent Orchestration          Accelerating  Runtime environments, multi-file context 
                                           management, terminal/git integration.

Trajectory Training Data     Compounding   Learning from real-world human-agent 
                                           collaboration, failure recovery, and CI loops.
```

When one curve hits an inflection point of diminishing returns, others pick up the slack. 

This explains why saturation on synthetic benchmarks like HumanEval or simple competitive programming does not mean AI capability is plateauing. The real frontier moves to targets with broader operational scope:

- From: *"Can the model implement an isolated string reversal algorithm?"*
- To: *"Can the agent resolve a reproduction script across a 50,000-line repository, edit four files, update the database migration, and pass integration tests within 15 minutes?"*
- Eventually: *"Can the agent autonomously manage a zero-downtime microservice migration over a two-week cycle?"*

---

## The Long-Term Shift

The early era of language modeling focused on passive artifact ingestion. We scraped what humans had already written—books, discussions, documentation, and polished code commits—and trained models on next-token prediction.

The next era is about training models on trajectories of active work.

Software engineering is uniquely positioned to lead this transition. Because code can be executed, measured, benchmarked, and mechanically verified, it provides the ideal sandbox for continuous reinforcement learning.

The paradigm is shifting from:

> *"What does a syntactically valid function look like?"*

to:

> *"How does an engineer take an ambiguous, incomplete requirement, form a hypothesis, iterate through compiler and test failures, incorporate architectural constraints, and deliver a verified, reliable system?"*

Even if raw parameter scaling slows down, progress in software AI will continue to compound. The gains will be driven by the tight feedback loop between increasingly capable models, rich agentic harnesses, deterministic verification, and the massive stream of human-AI engineering trajectories being captured today.
