---
title: "Reliability of LLM Coding Agents"
tags:
  - llm
  - ai-agents
  - software-engineering
  - testing
  - code-review
  - agentic-harness
aliases:
  - "LLM Coding Agents Reliability"
  - Reliability of LLM coding agents
  - Subtle Errors in Agentic Coding
---
# Reliability of LLM Coding Agents

## Core idea

Using LLMs for programming does not require them to be infallible. A coding agent should be treated as a **generator and executor of proposed changes operating inside a system of controls**, not as an authority capable of deciding by itself whether a solution is correct.

The key question is not:

> How do we prevent an LLM from ever making a mistake?

It is:

> How do we build a process that detects an LLM's mistake before the change reaches production?

When deploying agents in a real codebase, the architecture must separate proposal generation from verification. The model writes changes, but external, deterministic tooling—compilers, test runners, and independent review gates—decides whether those changes are acceptable.

```text
               CLOSED-LOOP VERIFICATION HARNESS
+-------------------------------------------------------------+
| GENERATION PHASE                                            |
|   Task Specification / User Intent                          |
|         |                                                   |
|         v                                                   |
|   Coding Agent --------> Proposed Diff + Spec-Derived Tests |
+---------|---------------------------------------------------+
          v
+-------------------------------------------------------------+
| DETERMINISTIC MECHANICAL GATES                              |
|   - Compiler / Type Checker (syntax, signatures, types)     |
|   - Linters / Static Analysis (formatting, static bugs)     |
|   - Regression Suite (protect existing baseline behavior)   |
+---------|---------------------------------------------------+
          v (Passes mechanical checks)
+-------------------------------------------------------------+
| AUDIT & INVARIANT GATES                                     |
|   - Independent Reviewer (evaluates diff against intent)    |
|   - Domain Invariant Verification (state machine checks)    |
|   - Human Code Comprehension (final production sign-off)    |
+-------------------------------------------------------------+
```

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

Public benchmarks measure performance in a isolated, synthetic environment. They do not represent a universal probability that any generated change will be correct in your proprietary codebase. An agent's actual success rate is dictated by its harness: repository access, terminal execution, quality of tests, depth of documentation, token budgets, retry loops, and stopping conditions.

## Compound error rates in multi-turn execution

A frequent mistake when designing agentic workflows is assuming that a high per-step accuracy translates to reliable autonomous task completion.

LLMs are probabilistic token generators. Even if a model executes individual tool calls or edits with a high per-step reliability—say, 98%—compound probability across a multi-turn autonomous loop dictates that long, unbounded runs will inevitably fail:

$$P(\text{success}) = p^N$$

```text
COMPOUND DRIFT ACROSS TOOL TRAJECTORIES (at 98% per-step reliability):
Turn   1: [====================] 98.0% probability of flawless execution
Turn  10: [================░░░░] 81.7%
Turn  35: [==========░░░░░░░░░░] 49.3%  <-- 50/50 threshold: failure is as likely as success
Turn  70: [=====░░░░░░░░░░░░░░░] 24.3%
Turn 100: [==░░░░░░░░░░░░░░░░░░] 13.3%  <-- ~87% chance of an unrecovered blunder
```

Over a 50- or 100-step trajectory, an agent will encounter tool failures, unexpected command outputs, or context degradation. If the harness allows the agent to loop autonomously without intermediate validation, the model eventually branches off into unrecoverable states. Reliability requires keeping operational turn counts small, validating state after every discrete modification, and resetting to clean Git checkpoints when a turn goes sideways.

## Why an unreliable model can still be useful

Software engineering provides many external and automatic verification mechanisms:

- compilers and type systems,
- unit and integration tests,
- static analysis,
- linters and formatters,
- API schemas and contracts,
- performance benchmarks,
- runtime monitoring and rollback systems.

The model does not have to produce the correct solution on its first attempt. It must produce useful candidates often enough and respond effectively to concrete feedback from compilers and test suites.

A safe **closed-loop workflow** runs as follows:

1. Interpret the specification and expose assumptions.
2. Define acceptance criteria and boundary cases.
3. Make a small, scoped change.
4. Compile and run tests and analyzers.
5. Fix detected problems based on concrete error messages.
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

- **Verbalized confidence** — ask for a confidence estimate, unverified assumptions, and elements requiring confirmation. Treat the answer as a hint, never proof.
- **Response stability** — generate several answers using different seeds, temperatures, or prompt paraphrases. Divergence across runs suggests high uncertainty.
- **Semantic entropy** — measure whether independently generated answers converge on the same underlying logic rather than merely sharing similar phrasing.
- **Token probabilities** — log probabilities indicate token-level uncertainty, but they measure textual prediction fit, not factual correctness.
- **Sensitivity to counterarguments** — a proposed solution should survive an attempt at falsification and point directly to documentation, executable evidence, or concrete code paths.
- **Cross-model disagreement** — running the same task through two distinct model families often exposes ambiguity in the underlying requirements.

### Fundamental limitation

There are two distinct failure modes to manage:

1. **The model is uncertain and generates unstable answers.** This is relatively easy to detect through sampling and basic validation.
2. **The model confidently reproduces an incorrect but common pattern.** Sampling and confidence inquiries will surface nothing unusual.

An LLM's self-reported confidence must never be used as an automated release gate. At most, reported uncertainty should determine how many independent verification passes are required before human review.

## The most dangerous failure: a plausible near-miss

The main danger in agentic workflows is rarely a dramatic hallucination or obvious syntax error. Compilers and linters catch those immediately.

The primary risk is the **plausible near-miss**: a solution that is nearly correct, locally coherent, and convincing, but subtly misaligned with the actual requirement.

Common examples from production systems:

- calling the correct API method with the wrong parameter variant or flag,
- implementing the happy path cleanly while omitting one edge-case state transition,
- applying a valid design pattern where the domain constraints make it harmful,
- retrying a network operation that is not inherently idempotent,
- wrapping a transaction boundary around the wrong scope, leading to race conditions or deadlocks,
- verifying a user's general permission without checking object-level access to the specific resource,
- handling `null` or `None` while failing to distinguish "value is missing" from "value is explicitly unset",
- writing a test that verifies the implementation code rather than the business invariant.

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

The code confuses two distinct domain concepts:

- "the order has not yet been shipped" (`Status != OrderStatus.Shipped`),
- "the shipping process has not started."

If `OrderStatus.PreparingShipment` means that the warehouse has already packed the items and assigned a courier, the implementation is fundamentally broken. Yet it looks clean, compiles without warnings, passes simple mock tests, and reads naturally to a tired reviewer.

## Local consistency can conceal a global mistake

An LLM can generate an internally consistent package:

- readable, idiomatic code,
- project-appropriate naming conventions,
- inline comments matching the code perfectly,
- unit tests that pass against the implementation,
- a compelling, structured pull request description.

If the initial prompt interpretation was slightly off, every generated artifact will reinforce that original error. Green CI proves only that the code matches the tests; it does not prove that the code matches business intent.

This makes agent-generated pull requests deceptively difficult to review. The code looks complete and well-crafted, which naturally nudges the human reviewer toward confirming the code's internal logic rather than critically checking its assumptions against the actual requirements.

> An LLM often does not produce an obviously bad answer. It produces an excellent answer to a question that is slightly different from the one you asked.

## Defences against subtle errors

### 1. Review the interpretation before implementation

Before generating a diff, the agent should output:

- its interpretation of the requirement,
- explicit assumptions it is making,
- related concepts that could easily be confused,
- concrete positive and negative examples,
- boundary cases it plans to handle,
- open questions requiring human clarification.

Approving the semantic interpretation up front prevents the agent from writing hundreds of lines of code around an inverted assumption.

### 2. Use decision tables and state machines

Avoid testing only the obvious happy and failure paths. Require the agent to map the complete state transition matrix:

| Status | Cancellation allowed? | Reason |
|---|---:|---|
| `New` | yes | fulfilment has not started |
| `Paid` | yes | payment does not imply shipping has started |
| `PreparingShipment` | **unresolved** | semantic boundary in the requirement |
| `Packed` | no | shipping fulfilment is already in progress |
| `Shipped` | no | the parcel has been dispatched |

An unresolved cell is an asset: it exposes an ambiguous domain rule and forces a human engineering decision instead of allowing the model to silently guess.

### 3. Derive tests from the specification

Tests written by the same model prompt that generated the implementation often carry the same semantic blind spots. To break this loop:

- write or generate acceptance tests from the specification before code generation begins,
- populate tests with concrete business examples,
- ensure tests deliberately target boundaries, state mutations, and counterexamples.

A test only validates what it asserts. If the assertion shares the model's mistaken premise, green tests provide nothing more than false confidence.

### 4. Decouple generation from invariant auditing

Generation and auditing should be split into two separate passes:

```text
Pass 1: Functional Generation
  Prompt: Task spec + codebase context -> Produces code diff + tests

Pass 2: Independent Invariant Audit
  Prompt: Original spec + generated diff (WITHOUT the author agent's conversational rationale)
  Task: Falsify the solution against core domain invariants
```

An auditor subagent should:
1. Receive the original specification and relevant interfaces first.
2. Build its own model of the requirements and boundary conditions.
3. Inspect the diff only after establishing its own expectations.
4. Propose targeted edge-case tests specifically designed to break the patch.

Separating these passes prevents the reviewer from being anchored by the author agent's internal reasoning.

### 5. Soft prompt rules versus hard mechanical boundaries

Rules placed in `.cursorrules`, `CLAUDE.md`, or repository-level skills files are **soft semantic guardrails**. They adjust token probabilities; they do not enforce system invariants.

As an agent's context fills with long stack traces, large diffs, and tool outputs, its attention over earlier system prompts degrades. Soft instructions like *"Never delete test files"* or *"Ensure all mutations run in a transaction"* will eventually be ignored during high-entropy recovery loops.

Enforce critical invariants using hard mechanical boundaries:
- use Git checkpoints to snapshot state before every autonomous turn,
- restrict agent tooling permissions (disable destructive terminal flags unless explicitly authorized),
- mount sensitive directories or configuration files as read-only during generation passes,
- block merges at the CI level using linters, formatters, and static security analyzers.

### 6. Keep changes small and traceable

Each change should encompass as few semantic decisions as possible. Maintain a clean, traceable sequence:

```text
requirement → concrete example → failing test → implementation diff
```

Small diffs prevent scope creep and make subtle assumption shifts immediately obvious to the human reviewer.

### 7. Require evidence, not declarations

An agent should never finish a task by simply declaring it "complete." It must supply an audit trail:

- which specific requirements were addressed,
- which files and lines were modified,
- which exact test commands were executed and their terminal outputs,
- which assumptions remain unverified,
- which operational risks remain open.

A crucial question to ask the agent before accepting any diff:

> How can we independently falsify your implementation?

### 8. Engineers must continue reading code

Automated test suites, static analysis, and multi-agent audit passes can catch mechanical failures, syntax errors, and regressions. They cannot verify that the software does what the business actually needs.

An agent can generate code that builds without warning, passes all unit tests, and satisfies an automated reviewer, yet silently drops an edge-case business invariant. Developers who treat coding agents as an opaque code pipeline will quickly build up structural technical debt.

Reading the generated diff, questioning its assumptions, and maintaining a complete mental model of the codebase remains the non-negotiable responsibility of the human engineer.

## Stopping and escalation conditions

An agent should stop execution and escalate to a human when:

- repeated attempts fail to resolve the same compiler or test error,
- successive modifications expand the diff beyond the planned boundaries,
- the requirement is found to be ambiguous or self-contradictory,
- critical verification tests cannot be run locally or in the sandbox,
- there is no mechanism available to independently verify the change,
- the task modifies authentication, authorization, financial logic, or destructive database migrations,
- the solution requires a business trade-off not documented in the specification.

Without hard stopping conditions, an agent caught in an error loop will continue modifying adjacent files, drifting further away from a working solution with every iteration.

## A practical risk score

Instead of trusting the model's self-reported confidence, assess the verifiability and impact of the task:

```text
+2  relevant documentation is missing or outdated
+2  the solution depends on an unverified domain assumption
+2  independent runs produce divergent implementations
+3  critical verification tests cannot be run in the local harness
+3  the change touches security, permissions, or financial calculations
+2  no deterministic failing test can be written to reproduce the issue
+2  the business intent contains unresolved ambiguities
-2  a deterministic failing test is available before implementation
-2  an authoritative API schema or contract is provided
-2  independent acceptance tests pass consistently
```

An operational policy based on this score:

- **0–2**: The agent may proceed autonomously through its verification loop.
- **3–6**: Mandatory independent audit pass and targeted human review required before merge.
- **7+**: Stop. Require human architectural clarification, documentation, or manual implementation.

This score does not predict the mathematical correctness of the code. It measures how effectively your testing harness and review pipeline can catch a subtle error if one occurs.

## Conclusions

1. An LLM can be highly productive in software engineering despite an imperfect underlying error rate.
2. Mechanical errors—syntax mistakes, missing types, and failing tests—are cheap and easy to catch deterministically.
3. The most dangerous failures are convincing near-misses that compile cleanly and pass existing tests while missing domain requirements.
4. Asking an agent if it is confident does not work as a release gate; confident errors look identical to correct answers.
5. Reliability is achieved through external falsification: compilers, deterministic tests, independent review, and operational telemetry.
6. Semantic review of the specification and edge cases must precede code generation.
7. Prompts and skill files are soft guardrails; hard safety requires mechanical constraints like Git checkpoints and tool permission boundaries.
8. Because compound error rates degrade multi-turn trajectories, agent loops must remain small, scoped, and strictly bounded.

Reliability is never an intrinsic property of the model alone. It is a property of the entire system:

```text
model + context + specification + tools + tests + review + harness
```

---

## Related Notes

- **[[LLM Capability Reliability and the Shape of Progress]]**: Macro analysis of model capability leaps, non-linear reliability curves, and agent operational boundaries.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Practical harness architectures implementing self-healing execution loops, state-machine verification gates, and sandboxed execution.
- **[[Testing in the Model, Agent, LLM Era]]**: How deterministic test execution neutralizes stochastic generation errors and prevents code drift.
- **[[Enforcing Hard-to-Formalize Architectural Rules with Agents]]**: Using decoupled multi-agent review teams to catch architectural near-misses before merge.
- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Why subtle business logic misinterpretations are harder for agents to get right than complex technical syntax.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: Strategies for identifying and containing structural code rot and generative technical debt.
- **[[Exploring Agent Harnesses]]**: Detailed comparison of headless agent harnesses versus interactive CLI tools for managing code reliability.
