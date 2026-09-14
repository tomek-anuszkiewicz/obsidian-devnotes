---
title: LLM Coding Agents — Reliability, Uncertainty, and Subtle Errors
tags:
  - llm
  - ai-agents
  - software-engineering
  - testing
  - code-review
  - agentic-harness
aliases:
  - Reliability of LLM coding agents
  - Subtle Errors in Agentic Coding
---

# LLM Coding Agents — Reliability, Uncertainty, and Subtle Errors

> [!IMPORTANT]
> **Executive Architectural Thesis**: LLM coding agents are probabilistic change generators, not autonomous engineering authorities. While mechanical errors (compilation, syntax, type mismatches) are deterministically trapped by build systems, semantic near-misses—where code compiles cleanly, passes tautological tests, and persuasively rationalizes a broken domain invariant—represent the primary failure mode. Operational reliability requires decoupling functional generation from independent invariant auditing within a deterministic control harness anchored by human code comprehension.

```text
           TWO-PASS VERIFICATION & MECHANICAL AUDIT HARNESS
+-------------------------------------------------------------------------+
| PASS 1: FUNCTIONAL GENERATION                                           |
|   [ User Intent / Task Spec ]                                           |
|             |                                                           |
|             v                                                           |
|   [ Probabilistic Agent ] ---> Produces: Code Diff + Unit Tests         |
|             |                                                           |
+-------------|-----------------------------------------------------------+
              v
+-------------------------------------------------------------------------+
| MECHANICAL GATES (Deterministic Ground Truth)                           |
|   [ Compiler / Type Checker ] ---> Catch syntax & signature violations  |
|   [ Static Analysis / Linter ] -> Catch memory leaks & style rules      |
|   [ Regression Test Suite ] -----> Verify existing behavioral baselines |
+-------------|-----------------------------------------------------------+
              v (Passes Mechanical Gates)
+-------------------------------------------------------------------------+
| PASS 2: INDEPENDENT INVARIANT AUDIT & HUMAN ORACLE                      |
|   [ Auditor Agent / Human ] -----> Scrutinizes: Semantic Drift,         |
|                                    Tautological Tests & Invariant State |
|             |                                                           |
|             v                                                           |
|   [ Production Merge Gate ] (Guaranteed Zero-Regression Deployment)     |
+-------------------------------------------------------------------------+
```

## Executive Summary & Core Architectural Invariants

1. **Probabilistic Generators, Not Engineering Authorities**: Coding agents must operate as unprivileged proposal generators bounded by deterministic harness controls, never trusted to self-certify correctness or unilaterally approve architectural shifts.
2. **The Danger of Plausible Near-Misses**: Mechanical failures are resolved cheaply and autonomously by tooling. In contrast, semantic near-misses—where an agent generates plausible but inverted business logic wrapped in clean syntax—are the most dangerous and costly error modes.
3. **Local Coherence Masks Global Fallacy**: Because an agent generates code, comments, test assertions, and PR summaries within a unified context trajectory, all artifacts will consistently reinforce the same flawed premise. Green CI verifies internal self-consistency, not alignment with domain reality.
4. **Decoupled Two-Pass Verification**: Generation and invariant auditing must be separated into distinct execution passes. An independent review pass must evaluate diffs strictly against codified invariants without inheriting the generative prompt's attractor biases.
5. **Zero Consequence Awareness**: Probabilistic models have zero operational accountability. When faced with missing context or conflicting requirements, they fabricate plausible workarounds rather than halting. Mechanical boundary fences and mandatory human semantic comprehension are indispensable.

## Core idea

Using LLMs for programming does not require them to be infallible. A coding agent should be treated as a **generator and executor of proposed changes operating inside a system of controls**, not as an authority capable of deciding by itself whether a solution is correct.

The key question is not:

> How do we prevent an LLM from ever making a mistake?

It is:

> How do we build a process that detects an LLM's mistake before the change reaches production?

## There is no single LLM error rate

The probability of an error depends on the task, model, prompt, context, tools, and evaluation method. The same model can be highly reliable when summarizing a supplied document, less reliable when answering from memory, and behave differently again when making a multi-step change in a repository.

In programming, we should distinguish between at least:

- syntax or compilation errors,
- failing tests,
- incorrect API usage,
- reasoning errors,
- omitted requirements,
- incorrect business interpretation,
- regressions outside the immediate scope of the change,
- tool-use or workflow failures.

Public benchmarks measure performance in a particular environment. They are not a universal probability that any generated change will be correct. An agent's performance also depends on its harness: repository access, terminal access, tests, documentation, time and token budgets, retry loops, and stopping conditions.

## Why an unreliable model can still be useful

Software engineering provides many external and partly automatic verification mechanisms:

- compilers and type systems,
- tests,
- static analysis,
- linters and formatters,
- API schemas,
- integration and end-to-end tests,
- performance benchmarks,
- monitoring and rollback.

The model does not have to produce the correct solution on its first attempt. It must produce useful candidates often enough and respond effectively to concrete feedback.

A safer **closed-loop workflow** is:

1. Interpret the specification and expose assumptions.
2. Define acceptance criteria and boundary cases.
3. Make a small change.
4. Compile and run tests and analyzers.
5. Fix detected problems.
6. Stop when the acceptance criteria or retry limit is reached.
7. Perform an independent review against the original intent.

The easier a result is to verify automatically, the safer it is to delegate the task to an agent.

## Can we detect the model's knowledge boundary?

We can estimate whether a model is operating near the edge of its knowledge, but there is no reliable internal truth indicator. The tone of an answer is particularly weak evidence: a model may sound confident while being wrong or sound cautious while being correct.

### Useful but imperfect signals

- **Verbalized confidence** — ask for a confidence estimate, unverified assumptions, and elements requiring confirmation. Treat the answer as a hint, not proof.
- **Response stability** — generate several answers using different seeds, temperatures, or prompt paraphrases. Large disagreement suggests uncertainty.
- **Semantic entropy** — measure whether independently generated answers converge on the same meaning rather than merely sharing similar wording.
- **Token probabilities** — uncertainty between tokens can indicate instability, but it measures textual fit rather than factual correctness.
- **Sensitivity to counterarguments** — a proposed solution should survive an attempt at falsification and point to documentation, executable evidence, or specific code.
- **Cross-model or cross-reviewer disagreement** — independent interpretations can reveal ambiguity in the task.

### Fundamental limitation

There are two different situations:

1. The model is uncertain and generates different answers. This is relatively easy to detect.
2. The model is confidently following an incorrect but well-learned pattern. Sampling and confidence questions may detect nothing.

Therefore, an LLM's introspection must not be used as a safety gate. At most, reported uncertainty should determine how much independent verification is required.

## The most dangerous failure: a plausible near-miss

The main danger is often not a dramatic hallucination. It is a **plausible near-miss**: a solution that is nearly correct, locally coherent, and convincing, but subtly misaligned with the actual requirement.

Typical examples include:

- using the correct method with the wrong parameter variant,
- implementing the main path correctly but missing one boundary case,
- applying a valid design pattern in the wrong context,
- retrying an operation that is not idempotent,
- placing the transaction around the wrong part of the operation,
- checking general permission without checking access to the specific resource,
- handling `null` while failing to distinguish “missing” from “unknown,”
- writing a test that matches the implementation but not the business requirement.

### Example of semantic drift

Requirement:

> An order may be cancelled if shipping has not started.

A superficially reasonable implementation:

```text
if order.status != OrderStatus.Shipped:
    order.cancel()
```

The code confuses two similar concepts:

- “the order has not yet been shipped,”
- “the shipping process has not started.”

If `PreparingShipment` already means that shipping has started, the implementation is wrong despite looking sensible, compiling successfully, and being easy to support with green tests.

## Local consistency can conceal a global mistake

An LLM can produce an internally consistent package containing:

- readable code,
- project-appropriate names,
- comments consistent with the implementation,
- tests consistent with the implementation,
- a convincing pull request description.

If the initial interpretation was slightly wrong, every later artifact may consistently reinforce the same mistake. Green CI then proves agreement between code and tests, not necessarily agreement between the system and the business intent.

This can make generated code unusually difficult to review. It is stylistically clean and appears complete, encouraging the reviewer to confirm the proposed interpretation rather than attempt to falsify it.

In other words:

> An LLM often does not produce an obviously bad answer. It produces an excellent answer to a question that is slightly different from the one we asked.

## Defences against subtle errors

### 1. Review the interpretation before implementation

Before writing code, the agent should present:

- its interpretation of the requirement,
- explicit assumptions,
- similar concepts that could be confused,
- positive and negative examples,
- boundary cases,
- unresolved questions.

The semantics should be approved before a large diff is created.

### 2. Use decision tables and state machines

Do not test only the obvious positive and negative paths. Describe the complete behavioural boundary:

| Status | Cancellation allowed? | Reason |
|---|---:|---|
| `New` | yes | fulfilment has not started |
| `Paid` | yes | payment does not imply shipping has started |
| `PreparingShipment` | unresolved | semantic boundary in the requirement |
| `Packed` | no | shipping fulfilment is already in progress |
| `Shipped` | no | the parcel has been dispatched |

An unresolved cell is valuable: it exposes a business decision instead of allowing the model to silently invent one.

### 3. Derive tests from the specification

A test written by the implementation's author can reproduce the same interpretation error. Ideally, at least some tests should:

- exist before implementation,
- come from approved business examples,
- be prepared independently,
- deliberately target boundaries and counterexamples.

Tests prove only what they assert. If the assertion contains the same semantic mistake as the implementation, green tests provide false reassurance.

### 4. Use an independent reviewer

A reviewer agent should ideally:

1. Receive only the original specification first.
2. Build its own model of the requirements and boundary cases.
3. See the implementation diff only afterwards.
4. Compare the code with its independent interpretation.
5. Propose tests designed to falsify the solution.

Using a different model or at least a substantially different prompt can help. The reviewer should not be anchored by the author's convincing explanation before performing its own analysis.

### 5. Keep changes small and traceable

Each change should contain as few semantic decisions as possible. Maintain a visible chain:

```text
requirement → example → test → implementation
```

Small diffs make unintended scope expansion and subtle assumption changes easier to detect.

### 6. Require evidence, not declarations

The agent should not finish with “done.” It should report:

- which requirements were implemented,
- which files were changed,
- which commands and tests were run,
- what could not be verified,
- which assumptions remain,
- which risks are still open.

A particularly useful question is:

> How can we independently falsify your solution?

## Stopping and escalation conditions

The agent should stop and ask for human input when:

- repeated attempts do not remove the same failure,
- successive fixes expand the scope beyond the plan,
- the requirement turns out to be ambiguous,
- critical tests cannot be run,
- there is no independent verification mechanism,
- the change concerns security, authorization, money, or irreversible data migration,
- the solution requires a business decision not contained in the specification.

Without explicit stopping conditions, the agent may continue “repairing” code while moving progressively further away from the intended solution.

## A practical risk score

Instead of trusting the model's declared confidence, assess how verifiable the task is:

```text
+2 relevant documentation is missing
+2 the solution depends on an unverified assumption
+2 independent attempts produce different designs
+3 critical tests cannot be run
+3 the change affects security, authorization, or data
+2 no reproducing test can be created
+2 the business intent is ambiguous
-2 there is a deterministic failing test
-2 authoritative API documentation or a schema is available
-2 independent acceptance tests pass
```

An example policy:

- `0–2`: the agent may continue autonomously,
- `3–6`: human or independent-agent review is required,
- `7+`: stop and escalate.

This is not a mathematical probability that the answer is correct. It measures how likely the process is to detect a potential mistake.

## The Statistical Inevitability of Out-of-Distribution Aberrations

A hazardous assumption when scaling agentic workflows is believing that **a mature skill set (`SKILL.md`), sophisticated system prompts, or automated review loops eliminate catastrophic errors**.

They do not. LLMs are non-deterministic, probabilistic inference engines. Even if a model operates at a stellar 98% per-step reliability, compound probability across multi-turn autonomous loops ($P(\text{success}) = p^N$) dictates that over a 50- or 100-step tool trajectory, out-of-distribution deviations and catastrophic blunders are mathematically inevitable:

```text
COMPOUND DRIFT ACROSS TOOL TRAJECTORIES (at 98% per-step reliability):
Turn  1: [■■■■■■■■■■■■■■■■■■■■] 98.0% probability of flawless execution
Turn 10: [■■■■■■■■■■■■■■■■░░░░] 81.7%
Turn 35: [■■■■■■■■■■░░░░░░░░░░] 49.3% ◄── 50/50 threshold: anomaly is now expected
Turn 70: [■■■■■░░░░░░░░░░░░░░░] 24.3%
Turn 100: [■■░░░░░░░░░░░░░░░░░░] 13.3% ◄── ~87% chance of an out-of-distribution blunder
```

### 1. The Cold Indifference of Non-Human Execution (Zero "Skin in the Game")
When a human software engineer touches a mission-critical codebase, physiological feedback loops—fear of downtime, adrenaline, pride in craft, and the cognitive dread of rebuilding weeks of architectural work—enforce natural caution. The human has genuine **skin in the game**: an outage damages their reputation, drains their weekend, or risks their employment.

An LLM agent possesses **zero emotional stakes, no fear of failure, and zero consequence awareness**:
- To the model, accidentally invoking a tool that deletes a foundational architecture file or wipes a configuration directory is indistinguishable from appending a docstring; both are merely valid tokens in a tool-call schema.
- When an unexpected IDE tool timeout, file-locking contention, or malformed context payload occurs, the agent does not hesitate or panic. It will casually destroy an indispensable asset and proceed to the next token prediction with pristine, unbothered fluency.

#### The "Helpful Hallucination" Trap and the Silent Dead-End
A particularly insidious consequence of this indifference is that **an agent will never proactively admit that a problem exceeds its knowledge or reasoning capacity**:
- Because LLMs are pre-trained and fine-tuned for conversational helpfulness, the model refuses to say *"I do not know how to solve this complex domain problem."*
- Instead, it will cheerfully and repeatedly offer plausible-sounding, syntactically flawless workarounds that are fundamentally broken or mathematically invalid.
- Because the agent demonstrated high competence and accuracy on earlier, standard tasks, the developer grants it trust. The developer spends hours applying these suggestions, only to realize they have been led in circles.
- This results in a devastating **engineering dead-end**: the developer discovers that the agent cannot help them, but the developer themselves does not yet possess the deep, specialized domain knowledge (which might require weeks of dedicated research to acquire). The project stalls, forcing an expensive architectural retreat.

### 2. The Illusion of "Soft" Prompt Security & The Double-Check Harness Pattern
Rules stored in `.agents/rules/` and skills provided in `SKILL.md` are **soft semantic guardrails**:
- They shift token likelihoods; they do not enforce physical laws.
- When an agent encounters tool failures, foreign stack traces, or context saturation, attention slips. Soft instructions inevitably degrade.
- Relying on prompts to prevent destructive operations is an architectural antipattern. Safety must be enforced with **hard mechanical fences**: version control snapshots (`git reset`), tool-level permission gating (disabling destructive operations without explicit human authorization), and filesystem read-only locks. For deeper implementation patterns, see [[Agentic Coding Harness and Controlled Development Workflows]].

#### The Double-Check (Two-Pass) Verification Pattern
To bridge the gap between soft rules and reliable execution, agentic workflows must adopt an explicit **Two-Pass Generation-Audit Pattern**:
1. **Pass 1 (Generation)**: The agent generates the implementation, focusing its immediate attention on the functional problem and domain logic.
2. **Pass 2 (Double-Check Audit)**: A secondary, independent verification pass (or subagent) evaluates the generated diff exclusively against the codified rules and architectural invariants:
   - *"Did this change introduce prohibited abstractions?"*
   - *"Were line limits and file boundaries strictly respected?"*
   - *"Are all business invariants satisfied?"*

Separating *generation* from *rule auditing* prevents attention saturation and ensures that deviations are caught before code is merged into the tree.

### 3. Why Engineers Must Continue Reading Code
Automated tests, typecheckers, and multi-agent review subagents catch syntactic regressions, but they cannot replace semantic comprehension:
- An agent can produce code that builds without warning, passes all unit tests, and satisfies its own automated reviewers, yet silently discards essential domain invariants or deletes critical edge-case handling.
- Engineers who treat autonomous agents as an opaque black box inevitably accumulate catastrophic architectural entropy (see [[Software Decay and the Hidden Costs of Frictionless AI Code|containment strategies for generative entropy]]).
- **Reading the code and maintaining deep situational awareness remains the foundational, non-delegable responsibility of the human engineer.** The human is the sole consequential anchor standing between probabilistic generation and production reality.

## Conclusions

1. An LLM can be productive in software development despite a significant non-zero error rate.
2. Explicit failures—compilation errors, exceptions, and failing tests—are the easiest to detect.
3. The most dangerous failures are subtle, convincing near-misses that pass existing tests.
4. Asking the model how confident it is does not provide sufficient protection.
5. The strongest defence is external falsification through sources, execution, tests, independent review, and monitoring.
6. Specification examples and semantic review should precede implementation.
7. An agentic harness should constrain scope, run verification loops, preserve evidence, and enforce stopping conditions.
8. Because agents are probabilistic machines with zero emotional stakes, catastrophic aberrations across long tool trajectories are statistically inevitable; prompts and skills must never replace mechanical boundaries (Git checkpoints, permission gates) and human code comprehension.

Reliability is therefore not merely a property of the model. It is a property of the entire system:

```text
model + context + specification + tools + tests + review + harness
```

---

## Relationship to the Knowledge Graph

- **[[LLM Capability Reliability and the Shape of Progress]]**: Macro analysis of model capability leaps, non-linear reliability curves, and agent boundaries.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Practical harness architecture implementing self-healing execution loops and state-machine verification gates.
- **[[Testing in the Model, Agent, LLM Era]]**: Explores how deterministic test execution neutralizes stochastic errors and LLM hallucinations.
- **[[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]]**: How multi-agent review teams catch architectural near-misses before code reaches production.
- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Analyzes why subtle business misinterpretations are harder for agents to get right than complex technical syntax.
- **[[AI-Assisted Software Engineering Where Are We Now]]**: High-level empirical survey of agent productivity, capabilities, and failure modes across modern software engineering.
- **[[Exploring Agent Harnesses]]**: Detailed breakdown of headless harnesses versus interactive CLI tools for managing reliability.
