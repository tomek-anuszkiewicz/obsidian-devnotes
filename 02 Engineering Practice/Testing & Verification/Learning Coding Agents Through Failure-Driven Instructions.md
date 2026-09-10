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
---

## Core Idea

Instead of treating an agent instruction as a static prompt, treat it as a **versioned artifact that can be continuously improved based on agent failures**, forming the basis of [[Constraint Saturation and Rule Oscillation in Coding Agents|governing instruction saturation]].

Within a controlled [[Agentic Coding Harness and Controlled Development Workflows|agentic coding harness]], the goal is not merely to make the agent eventually produce correct code.

The more interesting goal is:

> **Produce good code with the minimum number of iterations by continuously improving the instructions, examples, rules, and context given to the agent.**

This creates two nested optimization loops.

---

## 1. Inner Loop: Improve the Code

As examined in [[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification|correcting AI-generated code]], the normal coding-agent loop looks like this:

```text
task
↓
agent generates code
↓
compile / tests / static analysis / review
↓
failure
↓
agent fixes code
↓
...
↓
success
```

This is already realistic today because software provides unusually strong automated feedback through [[Testing in the Model, Agent, LLM Era|deterministic test oracles]]:

- compiler errors
    
- unit tests
    
- integration tests
    
- architecture tests
    
- static analysis
    
- linting
    
- security checks
    
- performance benchmarks
    
- repository-level validation
    

The agent can repeatedly modify the implementation until the checks pass.

---

## 2. Outer Loop: Improve the Instructions

The more interesting loop happens above the coding loop:

```text
task
+
instruction v12
↓
agent
↓
failure
↓
analyze why the failure happened
↓
extract a reusable lesson
↓
generate candidate instruction changes
↓
evaluate them
↓
instruction v13
```

The system therefore learns not only:

> How do I fix this implementation?

but:

> What information should the agent have received so that this class of mistake would not happen in the first place?

Over time, repeated failures can become organizational knowledge.

---

## Example

Suppose the task is:

> Add an endpoint returning order history.

The agent creates:

```text
Controller
    ↓
DbContext
```

Tests pass, but an architecture test fails because controllers are not allowed to access persistence directly.

The system records:

```text
Failure:
Controller accessed DbContext directly.

Underlying reason:
The agent did not understand the application's architectural boundary.

Candidate rule:
HTTP endpoints should delegate to application handlers and must not access persistence directly.
```

This rule becomes part of the future agent context.

Later, instead of:

```text
task
→ bad implementation
→ feedback
→ fix
→ success
```

we want:

```text
task
→ correct implementation
```

---

## The Important Metric: First-Pass Success

Success rate alone is not sufficient.

An agent that succeeds after seven attempts may be much less useful than one that succeeds almost immediately.

Useful metrics include:

```text
first-pass success rate
average number of iterations
total tokens consumed
execution time
number of regressions introduced
human review effort
```

A simplified optimization function could look like:

```text
score =
    implementation quality
  - iteration cost
  - token cost
  - execution cost
  - regression cost
  - human review cost
```

One of the best high-level KPIs may therefore be:

> **How often can the agent produce an acceptable PR without corrective feedback?**

---

## Do Not Simply Append Every Failure to AGENTS.md

A naive implementation would be:

```text
failure
↓
add another rule
↓
add another rule
↓
add another rule
```

Eventually the instructions would become enormous, redundant, contradictory, and difficult for the model to follow.

Instead, failure processing should look more like:

```text
failure
↓
extract lesson
↓
check whether similar knowledge already exists
↓
generalize
↓
detect contradictions
↓
generate several candidate formulations
↓
evaluate them
↓
keep the version that improves results
```

Instructions themselves should therefore be treated almost like code:

- versioned
    
- tested
    
- reviewed
    
- refactored
    
- compressed
    
- removed when no longer useful
    

---

## A/B Testing Instructions

Different formulations of the same rule may produce different results.

For example:

### Version A

```text
Do not access DbContext from controllers.
```

### Version B

```text
Controllers are transport adapters only.
They may validate transport-level input and invoke application handlers,
but must not access persistence directly.
```

### Version C

```text
Before modifying an HTTP endpoint:

1. identify the application handler,
2. place persistence access there,
3. keep the controller limited to transport concerns.
```

They can be tested against a historical task suite:

|Instruction|Success|Avg. Attempts|Cost|
|---|--:|--:|--:|
|Current|82%|2.1|Low|
|A|84%|1.9|Low|
|B|91%|1.4|Medium|
|C|92%|1.3|Higher|

The best instruction is not necessarily the longest or the one with the highest raw success rate.

The objective is the best trade-off between:

> quality × reliability × iteration count × cost

---

## Avoid Overfitting to Individual Tasks

A dangerous loop would be:

```text
task fails
↓
change instruction
↓
rerun the same task
↓
task passes
↓
declare improvement
```

This may simply encode the solution to one particular case.

Instead, instruction development should resemble machine learning evaluation:

```text
TRAIN SET
historical failures and tasks
↓
optimize instructions

VALIDATION SET
different tasks
↓
check whether the rule generalizes

HOLDOUT SET
unseen tasks
↓
measure real improvement
```

The instruction system itself can overfit.

---

## Instructions Should Be Retrieved, Not Always Loaded

Eventually the organization may accumulate hundreds of useful lessons.

Loading all of them into every agent request would be inefficient.

Instead, knowledge could be organized by domain:

```text
instructions/

architecture/
    boundaries.md
    messaging.md
    persistence.md

dotnet/
    ef-core.md
    cancellation.md
    serialization.md

business/
    pricing.md
    reservations.md
    authorization.md

testing/
    integration-tests.md
    test-data.md
```

For a task such as:

> Add cancellation of a hotel reservation

the system may retrieve only:

```text
architecture/boundaries
business/reservations
business/authorization
testing/integration-tests
```

This creates a form of **RAG for agent behavior**.

Instead of retrieving facts for answering a question, the system retrieves the relevant operational knowledge required to perform the task correctly.

---

## Compressing Organizational Experience

Repeated failures may generate overlapping rules:

```text
Never instantiate HttpClient manually.

Use IHttpClientFactory.

External integrations must use typed clients.

Handlers should not construct HttpClient.
```

A meta-agent can detect that they express the same underlying principle and replace them with:

```text
External HTTP integrations must use the project's registered typed clients.
Application code must not instantiate HttpClient directly.
```

The compressed instruction set can then be evaluated against the regression suite.

If performance does not decrease, the redundant rules can be removed.

This creates something resembling a:

> **garbage collector for agent knowledge**

---

## Human Feedback Becomes Much More Valuable

Not every mistake can be detected automatically.

The hardest failures are often things like:

> Technically correct, but this domain model is wrong.

For example, a reviewer may say:

```text
A reservation is not cancelled immediately.

Cancellation creates a request that may later be accepted or rejected.
```

Instead of treating this as feedback only for one PR, the system can transform it into:

- a domain rule
    
- an example
    
- an architecture constraint
    
- a test
    
- a reusable agent instruction
    

The human therefore supplies the expensive insight once.

Future agents can reuse it indefinitely.

---

## Code Review Changes Meaning

Traditional code review:

```text
agent makes mistake
↓
human explains mistake
↓
agent fixes PR
↓
knowledge disappears into PR history
```

Learning-oriented code review:

```text
agent makes mistake
↓
human explains mistake
↓
mistake becomes structured knowledge
↓
knowledge becomes instruction / example / test
↓
instruction enters regression suite
↓
future agents avoid the same class of mistake
```

This changes the economics of review.

A good review comment is no longer only an improvement to one PR.

It becomes a potential improvement to **all future generated code**.

---

## What Can Already Be Automated?

### Strong automatic feedback

These areas are particularly suitable today:

- compilation
    
- unit tests
    
- integration tests
    
- architecture tests
    
- dependency rules
    
- linters
    
- static analysis
    
- security scanning
    
- performance benchmarks
    
- repository conventions
    

For these signals, the complete learning loop can potentially run automatically.

### Weak automatic feedback

Human judgment is still very valuable for:

- domain modeling
    
- architecture trade-offs
    
- unclear business semantics
    
- maintainability
    
- unnecessary abstractions
    
- conceptual correctness
    
- product intent
    

However, even here the human may only need to provide the explanation once.

The system can then convert the explanation into reusable knowledge.

---

## The Result Is Not Necessarily a Better Model

An important distinction:

The underlying LLM may remain unchanged.

What improves is the system around it:

```text
LLM
+
repository
+
tests
+
evaluation suite
+
organization-specific instructions
+
examples
+
failure history
+
retrieval
+
feedback loop
```

After enough iterations, the same general-purpose model may become dramatically more effective inside one particular organization.

The advantage comes from accumulated organizational experience.

---

## Mental Model

The interesting progression is:

```text
Prompt Engineering
↓
Instruction Engineering
↓
Eval-Driven Instruction Development
↓
Organizational Agent Learning
```

The long-term asset may therefore not be a giant prompt.

It is a continuously evolving system containing:

```text
tasks
+
failures
+
lessons
+
instructions
+
examples
+
tests
+
evaluations
```

The objective is:

> **Every meaningful agent failure should increase the probability that future agents avoid the entire class of mistake.**

In this model, an organization gradually builds its own **procedural memory for software-engineering agents**.
---

## Relationship to the Knowledge Graph

- **[[Agentic Coding Harness and Controlled Development Workflows]]**: How failure-driven instructions and project rules are integrated into agent runtime harnesses.
- **[[Constraint Saturation and Rule Oscillation in Coding Agents]]**: The dangers of instruction over-accumulation leading to multi-objective thrashing and rule oscillation.
- **[[LLM Agents and Institutional Memory]]**: Preserving historical failure modes and architectural decisions in version-controlled instruction sets.
- **[[What Should Organizations Preserve from AI-Assisted Development]]**: Capturing rejected trajectories and debugging sessions as strategic training assets.
- **[[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]]**: Identifying whether agent failures stem from code, instructions, or domain ambiguity.
- **[[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]]**: Translating past failure modes into active pre-merge review rules.
