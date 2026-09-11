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

# LLM Capability, Reliability, and the Shape of Progress

> [!IMPORTANT]
> **Executive Architectural Thesis**: Model capability and operational system reliability evolve along decoupled trajectories. While single-attempt benchmark scores and task horizons expand exponentially, autonomous multi-step execution suffers from geometric error compounding ($P = p^N$). Production reliability cannot be achieved by awaiting base model infallibility; it requires bounding untrusted probabilistic model cognition inside deterministic verification harnesses, automated feedback loops, and immutable mechanical oracles.

```text
       ASYMPTOTIC CAPABILITY VS OPERATIONAL RELIABILITY DIVERGENCE
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

      [ Untrusted LLM Engine ] ---> [ Deterministic Harness & Oracle ] ---> [ Verified Output ]
      (Probabilistic Cognition)     (Compilers, Linters, Mutation Tests)    (Guaranteed State)
```

## Executive Summary & Core Architectural Invariants

1. **Decoupling Capability from Operational Reliability**: High scores on static benchmarks (e.g., SWE-bench) prove that an LLM *can* solve an isolated problem, not that it will *reliably* repeat that success across varying contexts or edge conditions.
2. **Geometric Degradation Across Execution Horizons**: In unmitigated multi-step autonomous workflows, success degrades exponentially ($P_{\text{success}} = p^N$). Even a high per-step accuracy ($p = 0.95$) yields a catastrophic $35.8\%$ completion rate across a 20-step execution trajectory.
3. **The Threat of Soft Hallucinations**: As parameter scales and reasoning tokens increase, crude syntactical hallucinations vanish, replaced by subtle semantic deceits—plausible API parameter inversions, hallucinated configuration flags, and incorrect business rules that easily bypass superficial human review.
4. **Harness-Centric Engineering Over Model Waiting**: Reliable software systems do not wait for theoretical model infallibility. They treat probabilistic reasoning engines as untrusted worker components bounded by deterministic gatekeepers, compiler type checks, and [[Automated Regression Suites]].
5. **Differential Progress Velocities**: Coding and tool use improve along steep curves, but uncertainty calibration and boundary recognition improve slowly. Production architectures must bridge this gap mechanically.

## Capability is not reliability

Two claims that sound similar are fundamentally different:

1. A model **can** solve a difficult task.
2. A model will **reliably** solve every similar task.

The first is becoming true at an astonishing rate. The second is still far from true.

This distinction explains why modern models can produce expert-level work and still make a small, convincing mistake: an incorrect parameter, a subtly wrong assumption, a nonexistent API option, or a locally plausible implementation of the wrong business rule.

These are often not spectacular hallucinations. They are *soft hallucinations*: errors embedded in an otherwise coherent and persuasive result.

## A simplified history of model generations

### GPT-3 era: persuasive text generation

Models from roughly 2020–2022 could:

- generate fluent text;
- recall substantial general knowledge;
- write small code fragments;
- perform simple transformations.

However, they easily lost instructions, invented facts and APIs, and were unable to maintain a coherent plan across longer tasks. They were impressive language generators rather than dependable collaborators.

### GPT-3.5 and early chat models: useful assistants

Instruction following improved dramatically. Models became genuinely useful for conversation and programming assistance, but they frequently produced code that looked correct without working. They also had little ability to recognize when they were outside their knowledge.

### GPT-4 and Claude 3 era: capable collaborators under supervision

During 2023–2024, models became much better at:

- analysing code;
- working with larger contexts;
- planning multi-file changes;
- explaining trade-offs;
- correcting some mistakes when given test results.

They became productive tools for experienced developers, but still required verification and review.

### Reasoning models and agents: 2024–2026

The next major improvement did not come only from adding more knowledge. Models gained:

- more inference-time reasoning;
- access to terminals, repositories, browsers, and search;
- the ability to run tests and inspect results;
- iterative `change → observe → correct` loops;
- better context management and persistent notes;
- agent harnesses that constrain and verify their work.

This changed the nature of the system. A single model response may still be wrong, but an agent can now confront its answer with reality and repair some of its own mistakes.

## Why benchmarks appear to improve so dramatically

Stanford's AI Index reported that performance on SWE-bench rose from approximately 4.4% in 2023 to 71.7% in 2024. By 2026, SWE-bench Verified was close to saturation.

This does **not** mean that agents can solve nearly every software-engineering problem. It means they became very effective on a particular, bounded class of issues. Once a benchmark approaches saturation, harder and more diverse benchmarks reveal the remaining limitations.

For example, OpenAI reported 80% for GPT-5.2 Thinking on SWE-bench Verified but 55.6% on the more diverse and contamination-resistant SWE-bench Pro. The goalpost moves because the earlier test no longer separates frontier systems well.

Each benchmark therefore tends to follow its own S-curve:

1. A difficult benchmark is introduced.
2. Results are initially low.
3. Performance rises quickly.
4. The benchmark approaches saturation.
5. A harder benchmark exposes new weaknesses.

Consequently, all of the following can be true simultaneously:

- progress is extremely fast;
- established benchmarks are saturating;
- models still make elementary mistakes in real work.

## Error compounding in long tasks

Suppose an agent performs 20 important steps, with each step being correct 95% of the time. If no mechanism detects errors, the probability that every step is correct is:

$$
0.95^{20} \approx 36\%
$$

Even at 99% correctness per step:

$$
0.99^{20} \approx 82\%
$$

For 100 steps:

$$
0.99^{100} \approx 36.6\%
$$

This calculation is simplified, but it illustrates why being almost always correct on small tasks does not automatically produce a dependable long-running agent.

Real systems can perform better because tests, compilers, schemas, and environmental feedback catch errors. They can also perform worse because errors are correlated: one incorrect assumption may poison dozens of later decisions.

## The task-horizon curve

METR measures the length of a task—expressed as the time a skilled human would need—that an AI agent can complete with 50% success probability.

Its original research found that the frontier task horizon had approximately doubled every seven months since 2019. Later results suggest much longer horizons on some verifiable task suites, although METR warns that measurements above roughly 16 hours are currently difficult to estimate reliably.

The critical qualifier is **50% success probability**. This is evidence that the system can sometimes complete a long task, not that it can be trusted to do so consistently.

Different reliability thresholds correspond to very different uses:

| Success rate | Practical interpretation |
|---:|---|
| 50% | Capability demonstration or multiple attempts required |
| 80% | Useful agent with active supervision |
| 95% | Limited automation with safeguards and recovery paths |
| 99.9%+ | Reliability expected from some critical production systems |

Measuring the 99% or 99.9% horizon requires far larger and more diverse evaluations than measuring the 50% horizon. Rare failures dominate the result.

## We are moving along several curves

### 1. A sequence of benchmark S-curves

There is no single benchmark curve. Models rapidly climb one S-curve, saturate the test, and encounter a new curve created by a harder evaluation.

### 2. An approximately exponential task-horizon curve

The length of coherent work agents can sometimes perform has grown much faster than the apparent quality of an ordinary chat response. This may be the most economically important trend.

### 3. A slow reliability-tail curve

Reducing errors from 20% to 10% is different from reducing them from 2% to 0.1%. Each improvement exposes rarer and more difficult cases:

- ambiguous requirements;
- undocumented business rules;
- obsolete documentation;
- conflicting sources;
- unusual infrastructure configurations;
- failures that appear only after a long chain of actions;
- technically correct solutions to the wrong problem.

The final part of the reliability curve may be harder than all earlier capability gains combined.

## Why general infallibility is unlikely

General-purpose infallibility is not merely technologically difficult; it is poorly defined:

- some questions have no single correct answer;
- sources may conflict;
- requirements may be incomplete;
- facts may change after training;
- the user's premise may be false;
- the evaluator may also be wrong.

Training and benchmarks can additionally reward guessing over admitting uncertainty. A system can reduce hallucinations by refusing more often, but that produces a trade-off:

$$
\text{usefulness} \longleftrightarrow \text{caution}
$$

A model that never answers will rarely hallucinate, but it will also be useless.

## What is likely to improve next

The most plausible near-term future is not a model that never makes mistakes. It is a system that increasingly:

1. verifies claims and actions with tools;
2. detects contradictions in its own reasoning;
3. maintains goals over longer tasks;
4. distinguishes facts, assumptions, and missing information;
5. runs independent attempts or reviews when risk is high;
6. relies on tests, types, schemas, permissions, and observability;
7. asks humans to decide ambiguous product and business questions.

Human work is likely to shift from producing every implementation detail toward defining intent, constraints, acceptance criteria, and review boundaries.

## Why software engineering may automate faster

Programming has unusually strong external feedback:

- code compiles or fails;
- a test passes or fails;
- a type checker identifies inconsistencies;
- an API contract can be validated;
- a UI can be rendered and inspected;
- runtime behaviour can be compared with an expected state.

Tasks with a strong verifier can improve much faster than tasks whose quality is subjective or whose requirements are hidden.

Likely faster areas:

- bounded bug fixes;
- migrations with explicit rules;
- refactoring protected by tests;
- implementing well-specified API operations;
- generating and validating infrastructure definitions.

Likely slower areas:

- discovering what product should be built;
- reconstructing undocumented business knowledge;
- resolving conflicting stakeholder intentions;
- choosing architecture for uncertain future requirements;
- judging maintainability over several years.

## Where we are now

The overall technology does not appear to be on a final plateau. Instead, several waves overlap:

- conventional pre-training scaling may deliver diminishing returns;
- inference-time reasoning still provides substantial gains;
- tool use and agent loops produce large practical improvements;
- context management, evaluation, memory, and harness design are becoming as important as the underlying model.

We are probably past the first great transition—*a model can speak and write*—and in the middle of the second—*a model can perform and verify work*.

The remaining danger is subtle. As models become more capable, their errors become less obvious and their outputs more persuasive. Trust may increase faster than reliability. Therefore, the central engineering question is no longer only:

> How capable is the model?

It is increasingly:

> What evidence would reveal that this particular result is wrong?

## Practical conclusion

LLMs should not be treated as deterministic components. They are probabilistic workers operating inside a deterministic control system.

For serious agentic work, reliability should come from the complete system:

- explicit specification;
- bounded permissions;
- source retrieval;
- executable tests;
- static analysis;
- independent review;
- observable intermediate state;
- stop conditions and escalation rules;
- human approval for ambiguous or high-impact decisions.

The model supplies capability. The [[Agentic Coding Harness and Controlled Development Workflows|Agentic Harness]] supplies control and evidence.

## Related Notes

- **[[LLM Coding Agents Reliability]]**: Practical error modes, subtle hallucinations, and failure topologies of coding agents in real-world codebases.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: The architectural design of deterministic control harnesses that bound probabilistic agent cognition.
- **[[How Reasoning Models Explore and Evaluate Solutions]]**: How test-time compute, Monte Carlo rollouts, and search heuristics affect frontier capability frontiers.
- **[[Improving AI Models - From Scaling to Agent-Generated Training Data]]**: The transition from passive web pre-training to active agentic synthetic data and RLHF.
- **[[AI Productivity Is Limited by the Delivery System]]**: The macroeconomic and organizational bottlenecks that prevent raw capability increases from translating to production throughput.
- **[[Testing in the Model, Agent, LLM Era]]**: Why non-deterministic AI generation requires automated, immutable deterministic test oracles.

## Sources

- [Stanford AI Index 2025 — Technical Performance](https://hai.stanford.edu/ai-index/2025-ai-index-report/technical-performance)
- [Stanford AI Index 2026](https://hai.stanford.edu/ai-index/2026-ai-index-report)
- [METR — Task-Completion Time Horizons of Frontier AI Models](https://metr.org/time-horizons/)
- [METR — Clarifying Limitations of Time Horizon](https://metr.org/notes/2026-01-22-time-horizon-limitations/)
- [METR — Measuring AI Ability to Complete Long Software Tasks](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)
- [OpenAI — Why Language Models Hallucinate](https://openai.com/index/why-language-models-hallucinate/)
- [OpenAI — Introducing GPT-5.2](https://openai.com/index/introducing-gpt-5-2/)

