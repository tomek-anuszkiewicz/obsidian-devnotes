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

## Core idea

Using LLMs for programming does not require them to be infallible. A coding agent should be treated as a **generator and executor of proposed changes operating inside a system of controls**, not as an authority capable of deciding by itself whether a solution is correct.

The key question is not:

> How do we prevent an LLM from ever making a mistake?

It is:

> How do we build a process that detects an LLM's mistake before the change reaches production?

When deploying agents in a real codebase, the architecture must separate proposal generation from verification. The model writes changes, but external, deterministic tooling—compilers, test runners, and independent review gates—decides whether those changes are acceptable.

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

## Compound error rates in multi-turn execution

A frequent mistake when designing agentic workflows is assuming that a high per-step accuracy translates to reliable autonomous task completion.

LLMs are probabilistic token generators. Even if a model executes individual tool calls or edits with a high per-step reliability—say, 98%—compound probability across a multi-turn autonomous loop dictates that long, unbounded runs will inevitably fail:

$$P(\text{success}) = p^N$$

Over a 50- or 100-step trajectory, an agent will encounter tool failures, unexpected command outputs, or context degradation. If the harness allows the agent to loop autonomously without intermediate validation, the model eventually branches off into unrecoverable states. Reliability requires keeping operational turn counts small, validating state after every discrete modification, and resetting to clean Git checkpoints when a turn goes sideways.

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

## Consequence blindness and the helpfulness trap

Human software engineers operate with genuine operational stakes. The fear of causing an outage, losing data, or debugging a production issue over the weekend enforces natural caution. When an engineer touches a critical migration script or an authorization boundary, they slow down.

An LLM has no operational stakes or awareness of consequences:

- To an agent, invoking a tool that wipes a database table or deletes an architecture directory is just another valid token sequence matching a tool-call schema.
- When an unexpected file contention, IDE timeout, or malformed stack trace occurs, the agent does not pause to reflect. It will proceed to the next token prediction with the same calm fluency, even if that means overwriting critical code to bypass a failing test.

### The helpfulness trap and engineering dead-ends

Because models are fine-tuned for conversational helpfulness, an agent rarely admits: *"I do not know how this domain system works, and I lack the context to solve it."*

Instead, it will generate plausible, syntactically clean workarounds that violate domain realities:
- If a developer grants too much trust based on earlier, straightforward successes, they can easily spend hours testing and applying these fluent suggestions, only to realize the agent has led them in circles.
- This creates an expensive engineering dead-end: the agent cannot solve the core problem, and the developer—having outsourced their understanding of the change to the model—now lacks the mental model required to step in and fix it manually.

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

```csharp
if (order.Status != OrderStatus.Shipped)
{
    order.Cancel();
}
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

### 7. Soft prompt rules versus hard mechanical boundaries

Rules placed in `.cursorrules`, `CLAUDE.md`, or repository-level skills files are **soft semantic guardrails**. They adjust token probabilities; they do not enforce system invariants.

As an agent's context fills with long stack traces, large diffs, and tool outputs, its attention over earlier system prompts degrades. Soft instructions like *"Never delete test files"* or *"Ensure all mutations run in a transaction"* will eventually be ignored during high-entropy recovery loops.

Enforce critical invariants using hard mechanical boundaries:

- use Git checkpoints to snapshot state before every autonomous turn,
- restrict agent tooling permissions (disable destructive terminal flags unless explicitly authorized),
- mount sensitive directories or configuration files as read-only during generation passes,
- block merges at the CI level using linters, formatters, and static security analyzers.

### 8. Engineers must continue reading code

Automated test suites, static analysis, and multi-agent audit passes can catch mechanical failures, syntax errors, and regressions. They cannot verify that the software does what the business actually needs.

An agent can generate code that builds without warning, passes all unit tests, and satisfies an automated reviewer, yet silently drops an edge-case business invariant. Developers who treat coding agents as an opaque code pipeline will quickly build up structural technical debt.

Reading the generated diff, questioning its assumptions, and maintaining a complete mental model of the codebase remains the non-negotiable responsibility of the human engineer.

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

## Conclusions

1. An LLM can be productive in software development despite a significant non-zero error rate.
2. Explicit failures—compilation errors, exceptions, and failing tests—are the easiest to detect.
3. The most dangerous failures are subtle, convincing near-misses that pass existing tests.
4. Asking the model how confident it is does not provide sufficient protection.
5. The strongest defence is external falsification through sources, execution, tests, independent review, and monitoring.
6. Specification examples and semantic review should precede implementation.
7. An agentic harness should constrain scope, run verification loops, preserve evidence, and enforce stopping conditions.

Reliability is therefore not merely a property of the model. It is a property of the entire system:

```text
model + context + specification + tools + tests + review + harness
```
