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
---

A useful automated review begins with a concrete suspicion about a change, investigates it with the engineering toolchain, and presents evidence that another person or process can check. Several focused reviewers can examine different failure modes without requiring one prompt to cover every concern at once.

This article develops that review design: specialist instructions, hypotheses, reproductions, independent contexts, and the separation of review from repair. [[Operating an Automated Code Review Service]] handles the operating system around it: routing, cost, synthesis, confidence, feedback, GitHub integration, and permissions. The division keeps both the quality of a finding and the behavior of the deployed review service inspectable.

LLMs can change code review from a mostly human, manually executed activity into a continuous system of specialized reviewers.

The most useful model is not:

> One AI reads a pull request and gives its opinion.

A more interesting model is:

> A team of specialized agents continuously examines changes, forms hypotheses about potential problems, and uses deterministic tools to verify them.

The role of humans then shifts toward reviewing important findings, resolving ambiguity, making architectural decisions, and accepting responsibility for the final change.

---

## The Most Important Property May Be Relentlessness

One of the biggest advantages of an automated reviewer is not intelligence.

It is relentlessness.

A human reviewer gets tired.

After reviewing many pull requests, large diffs, repetitive changes, or hundreds of similar files, attention inevitably decreases.

An agent does not care that:

- this is the twentieth pull request today;

- the diff contains 150 files;

- the same validation pattern appears for the hundredth time;

- a checklist contains 40 items;

- the issue it is looking for occurs only once every few thousand changes.

It can apply the same procedure every time.

This makes agents especially useful for review work that is:

- repetitive;

- systematic;

- easy to forget;

- rare but important;

- dependent on large amounts of context.

A human may know that every new endpoint should verify authorization, propagate cancellation, validate input, preserve backward compatibility, update telemetry, and contain relevant tests.

Knowing the rules does not mean remembering every rule during every review.

An agent can.

This may be one of the strongest reasons to introduce AI review even when human reviewers are already very experienced.

---

## Code Review Does Not Need One General Reviewer

A single prompt such as:

```text
Review this pull request.
```

asks one model to simultaneously reason about too many unrelated concerns.

Asking one model instance to simultaneously reason about security boundaries, database query plans, asynchronous cancellation propagation, and domain invariants blows out the context window and dilutes attention. The result is predictable: shallow feedback, pedantic style nits, hallucinated syntax errors, and silence on critical race conditions. Dispatching targeted specialists keeps each agent's attention sharp and prompt context bounded.

A better design is a team of specialized reviewers.

For example:

```text
Review Router
    |
    +-- Correctness Reviewer
    +-- Test Reviewer
    +-- Security Reviewer
    +-- API Compatibility Reviewer
    +-- Database Reviewer
    +-- Performance Reviewer
    +-- Concurrency Reviewer
    +-- Architecture Reviewer
```

Not every reviewer needs to run for every change.

A lightweight routing agent can inspect the diff and decide which specialists are relevant.

For example:

```text
DTO / controller / public contract changed
        ->
API Compatibility Reviewer
```

or:

```text
EF / SQL / migration changed
        ->
Database Reviewer
```

or:

```text
authentication / authorization changed
        ->
Security Reviewer
```

Correctness and test reviewers may run almost always, while expensive specialists run conditionally.

This keeps both cost and noise under control.

---

## Different Reviewers Should Have Different Instructions

Each reviewer can have its own playbook.

A database reviewer may inspect:

- query count;

- N+1 queries;

- indexes;

- transaction boundaries;

- query plans;

- excessive materialization;

- unnecessary round trips;

- locking behavior.

An API reviewer may inspect:

- backward compatibility;

- serialization changes;

- optional versus required fields;

- enum compatibility;

- HTTP semantics;

- authorization;

- versioning.

A performance reviewer may inspect:

- allocations;

- algorithmic complexity;

- reflection;

- unnecessary abstractions;

- excessive LINQ;

- repeated parsing;

- synchronization;

- database access;

- hot-path behavior (see [[AI May Make Aggressive Code Optimization Economically Viable]]).

A correctness reviewer may concentrate on:

- boundary conditions;

- missing cases;

- null handling;

- exception paths;

- inconsistent state;

- assumptions that no longer hold.

This is much easier to improve than one enormous global prompt.

Dividing the review domain into modular playbooks makes the system maintainable. When an agent produces false positives or misses an edge case, you tune a single specialized playbook rather than destabilizing a massive global prompt.

---

## The Reviewer Should Form Hypotheses, Not Just Opinions

LLMs are useful at spotting suspicious patterns, but a review becomes much more valuable when an agent can verify its own suspicions.

The fastest way to destroy developer trust is to deploy an AI reviewer that litters pull requests with speculative, unverified comments like "this code might be slow" or "this could cause a concurrency issue." Speculative comments force engineers to waste time disproving hallucinations. Following a hypothesis-verification protocol ensures that an LLM generates a failure thesis, and deterministic tools verify it before any comment is posted.

Instead of:

```text
This code might be slow.
```

the reviewer should try:

```text
Hypothesis:
The new implementation introduces O(n²) behavior.

Experiment:
Run a benchmark for 1k, 10k and 100k elements.

Result:
main:  38 ms
PR:    4.7 s

Conclusion:
Confirmed performance regression.
```

The same principle applies to correctness.

```text
Reviewer suspects a bug
        |
        v
generate reproduction test
        |
        v
run against main
        |
        v
run against PR
        |
        v
report only if confirmed
```

This creates a useful distinction:

> LLMs generate hypotheses. Deterministic tools provide evidence.

---

## Reviewers Can Use the Existing Engineering Toolchain

AI review does not replace CI.

It orchestrates and interprets it.

A reviewer can use:

```text
dotnet test
static analyzers
CodeQL
coverage
BenchmarkDotNet
dotnet-counters
dotnet-trace
SQL EXPLAIN
linters
integration tests
property-based tests
fuzz tests
```

The agent can decide which tool is relevant, execute it, interpret the result, and attach the evidence to the finding.

Instead of:

> This allocation could become expensive.

it can report:

```text
main:
2.1 µs
0 B allocated

PR:
3.8 µs
320 B allocated

The method is called approximately 5 million times per day.
```

The discussion then becomes much less subjective.

---

## Agents Can Also Create Tests During Review

A powerful reviewer should be allowed to create temporary tests.

For example:

```text
Potential bug detected
        |
create regression test
        |
test passes on main
        |
test fails on PR
        |
finding confirmed
```

The test itself can become part of the suggested fix.

This turns review into something closer to automated investigation.

The reviewer is not merely saying:

> I think this is wrong.

It is saying:

> I can demonstrate a case where this is wrong.

In practice, the agent writes a reproduction test asserting expected behavior and runs it against baseline (`main`) where it passes, then executes it against the pull request branch where it fails. The reproducer test confirms the defect with empirical evidence and can be committed directly to the test suite by the author, permanently preventing regression.

---

## Reviewer and Fixer Should Be Separate Roles

It may be useful to deliberately separate finding problems from changing code.

For example:

```text
Reviewer
    read
    search
    run tests
    run benchmarks
    no write access
```

and:

```text
Fixer
    read
    edit
    run tests
```

The workflow becomes:

```text
Reviewer:
I suspect a bug.

Validator:
Confirmed by this test.

Fixer:
Here is a proposed patch.

Validator:
The test now passes.

Human:
Approve or reject.
```

This reduces the risk that the same agent unconsciously rationalizes the solution it has just created.

It also makes permissions easier to control.

When an agent both analyzes and modifies, it tends to rationalize its own misunderstandings. If it hallucinates a bug, it will write a patch that adds unnecessary complexity to solve an imaginary problem, or worse, modify assertions in the test suite to make its broken patch pass. Keeping the reviewer strictly read-only and forbidding the fixer from altering test assertions ensures independent verification.

---

## Independent Reviewers May Be Valuable

Review does not necessarily have to be performed by the same model that produced the code.

It may be useful to deliberately introduce diversity:

```text
Model A generates code.

Model B reviews correctness.

Model C reviews security.

Model D tries to find counterexamples.
```

Different models may have different failure modes.

Even using the same model with independent contexts can help because one reviewer is not anchored by the reasoning that produced the implementation.

The analogy is similar to having another engineer examine the change without first hearing a long explanation of why the author thinks it is correct.

---

## Human Review Does Not Necessarily Disappear

AI review may instead change what humans review.

It can also change who receives routine findings. An orchestrator can return a substantiated defect directly to a fixer, rerun the relevant checks on the new candidate, and request a human decision only when policy requires it or the bounded repair loop cannot resolve the problem. Automatic acceptance is appropriate only within an explicitly authorized scope; the reviewer does not grant itself merge authority (see [[Acceptance Policies and Automated Repair in Agentic SDLC]]).

Today humans often spend time checking things such as:

```text
Did someone forget a null check?
Is cancellation propagated?
Is this method tested?
Is this API backward compatible?
Did someone accidentally introduce N+1?
```

These are valuable checks, but they consume attention.

Agents can perform them relentlessly.

Humans can spend more attention on:

- whether the business behavior is correct;

- whether the abstraction makes sense;

- whether the product should behave this way at all;

- long-term architecture;

- trade-offs;

- organizational context;

- risk acceptance.

The review becomes layered:

```text
machines check everything they can check repeatedly

humans concentrate on what requires judgment
```

---

## Code Review May Become Continuous Engineering Verification

The most important shift may therefore be conceptual.

Traditional review is approximately:

```text
developer writes code
        |
human reads diff
        |
human notices some problems
        |
merge
```

Agentic review can become:

```text
developer or agent creates change
        |
multiple reviewers inspect it
        |
reviewers form hypotheses
        |
tests and tools verify them
        |
findings are challenged and filtered
        |
fixes are proposed
        |
tests verify the fixes
        |
human reviews the remaining decisions
```

The goal is no longer merely:

> Have somebody read the code before merge.

It becomes:

> Continuously attempt to prove that the change is wrong before it reaches production.

That is where LLM reviewers may be particularly powerful.

They are not perfect.

But they can be **relentless, specialized, cheap to duplicate, able to investigate suspicious changes, and willing to run the same verification procedure every single time**.

For code review, those properties may matter almost as much as raw intelligence (see [[Multi-Agent Software Development]] and [[Building Determinism from Unpredictable Models]]).

## Related notes

- **[[Acceptance Policies and Automated Repair in Agentic SDLC]]** — Structured findings, protected policy, and repair before human escalation.
- **[[Observability and Controlled Improvement of Coding Agent Harnesses]]** — Measures reviewer value, repair cost, and controlled configuration changes.

- **[[Reviewing AI-Generated Code]]** — Review heuristics and inspection methods for AI-authored changes.
- **[[AI May Make Aggressive Code Optimization Economically Viable]]** — The architectural and economic justification for eliminating unnecessary abstractions and allocations on hot paths.
- **[[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]]** — Using review agents to enforce architectural standards at scale.
- **[[Multi-Agent Software Development]]** — Coordinating multiple specialized agent personas across development lifecycles.
- **[[Building Determinism from Unpredictable Models]]** — Verification gates and deterministic checks to validate reviewer hypotheses.
