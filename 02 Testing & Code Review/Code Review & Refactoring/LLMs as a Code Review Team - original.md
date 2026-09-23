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
    
- hot-path behavior.
    

A correctness reviewer may concentrate on:

- boundary conditions;
    
- missing cases;
    
- null handling;
    
- exception paths;
    
- inconsistent state;
    
- assumptions that no longer hold.
    

This is much easier to improve than one enormous global prompt.

---

## The Reviewer Should Form Hypotheses, Not Just Opinions

LLMs are useful at spotting suspicious patterns, but a review becomes much more valuable when an agent can verify its own suspicions.

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

## A Review Router Can Control Cost

Running ten powerful models on every typo would be wasteful.

A router can classify a change first.

For example:

```text
Change classification:

documentation only
    -> no technical review

test-only change
    -> correctness + test reviewer

database migration
    -> correctness + database + compatibility

authentication change
    -> correctness + security + tests

hot-path implementation
    -> correctness + performance + tests
```

The router itself can use a cheap model.

Expensive reasoning is reserved for changes where it matters.

---

## A Final Reviewer Can Synthesize the Findings

Multiple reviewers create another problem: noise.

Seven agents producing thirty comments can make a pull request worse rather than better.

A final synthesizer can therefore collect all findings and perform:

```text
deduplication
confidence filtering
severity ranking
cross-checking
evidence validation
```

A possible pipeline is:

```text
7 reviewers

24 candidate findings

9 duplicates / overlapping findings removed

5 low-confidence findings discarded

4 findings disproved by tests

6 findings presented to the developer
```

The final review can use a common format:

```text
Severity: HIGH
Confidence: HIGH

Problem:
...

Evidence:
...

Impact:
...

Suggested fix:
...

Reviewer:
database-performance
```

This makes AI review much less noisy.

---

## Confidence Should Matter

Not every observation deserves a pull-request comment.

A useful policy could be:

```text
HIGH severity + HIGH confidence
    -> inline comment / request changes

MEDIUM severity + HIGH confidence
    -> normal comment

LOW confidence
    -> review summary only

LOW severity + LOW confidence
    -> suppress
```

This is particularly important because an AI reviewer that produces too many false positives will quickly be ignored.

The goal is not maximum number of findings.

The goal is high-value findings.

---

## Reviewers Can Learn From Human Decisions

Every review interaction creates useful feedback.

For each finding the system can record:

```text
accepted
rejected
false positive
already known
fixed
ignored
disputed
```

Over time this becomes a dataset for improving the reviewer instructions.

For example, the team may discover that the performance reviewer frequently complains about allocations in paths that are executed once per request and have no measurable impact.

Its instructions can then be changed:

```text
Do not report allocation differences unless:

- the code is demonstrably hot,
- the difference is measurable,
- or the allocation has another significant consequence.
```

The review process itself can therefore become an optimization loop.

---

## Review Quality Can Be Measured

AI review creates the possibility of measuring reviewer effectiveness much more systematically.

Useful metrics include:

```text
findings generated
findings accepted
findings rejected
false-positive rate
confirmed bugs found
security problems found
regressions found
tests generated
findings confirmed by tests
time per review
cost per review
```

A reviewer can then be evaluated like another engineering component.

For example:

```text
Security Reviewer

1,240 PRs reviewed
87 findings
72 accepted
9 rejected
6 inconclusive

precision: ~83%
```

The question becomes less:

> Is this prompt good?

and more:

> How effective is this reviewer?

---

## GitHub Is a Natural Platform for This Model

GitHub already provides most of the infrastructure required to build such a system.

A reviewer can react to events such as:

```text
pull request created
new commit pushed
review requested
comment created
check completed
```

There are several ways to integrate an AI reviewer.

---

## GitHub Actions

The simplest architecture is often:

```text
Pull Request
     |
GitHub Actions
     |
AI Reviewer
```

The important advantage is that the agent can operate in the same environment as ordinary CI.

It can:

```text
checkout repository
build
run tests
generate temporary tests
run benchmarks
inspect artifacts
```

This is particularly attractive when verification requires executing the code.

---

## GitHub Apps

An external reviewer such as CodeRabbit can instead run as a GitHub App.

The architecture becomes:

```text
GitHub
   |
webhook
   |
External Review Service
   |
GitHub API
   |
PR review / comments / checks
```

The service may run completely outside GitHub.

It can listen for events such as:

```text
pull_request.opened
pull_request.synchronize
issue_comment
review_comment
```

and react automatically.

From the developer's perspective, the application behaves almost like another reviewer.

It can add:

- inline comments;
    
- review summaries;
    
- suggested changes;
    
- approvals;
    
- requests for changes;
    
- status checks.
    

This is the model used by many external analysis and review products.

---

## Reviewers Can Also Be Invoked On Demand

Not everything needs to run automatically.

A developer could request specialized investigation directly from a pull request:

```text
@review-bot performance
```

or:

```text
/review security
```

or even:

```text
@review-bot investigate whether this query causes an N+1 problem
```

This creates an interesting hybrid between a reviewer and an engineering assistant.

The pull request itself becomes the workspace in which humans and agents collaborate.

---

## GitHub Checks May Be Better Than Comments

Not every result needs to appear as another PR conversation.

Reviewers can publish checks such as:

```text
Build                     PASS
Tests                     PASS
Security Review           PASS
API Compatibility         PASS
Performance Review        FAIL
Database Review           PASS
```

Detailed findings can live inside the check.

This reduces comment noise and gives the review system a more structured interface.

Selected checks could eventually become required for merge.

Care is needed, however.

An unreliable LLM reviewer should not become a merge gate merely because it exists.

---

## External Reviewers Can Be Independent Services

There does not need to be one central AI-review system.

A repository could eventually have:

```text
GitHub Copilot
Company Architecture Reviewer
Security vendor
Performance service
CodeQL
Sonar
Dependency scanner
Business Rules Reviewer
```

All of them independently observe the same pull request.

GitHub effectively becomes an event bus and shared collaboration surface.

Different reviewers may be:

- SaaS products;
    
- internal company services;
    
- GitHub Actions;
    
- custom agents;
    
- deterministic analyzers;
    
- LLM-based systems.
    

Their results meet in the pull request.

---

## Private Companies Can Build Their Own Reviewer

A company can create a private GitHub App and run its reviewer in its own infrastructure.

For example:

```text
GitHub
   |
webhook
   |
Company Review Platform
   |
   +-- LLM
   +-- internal documentation
   +-- architecture decisions
   +-- Jira
   +-- production telemetry
   +-- Grafana
   +-- test infrastructure
```

This reviewer could know things that a general-purpose SaaS reviewer cannot know.

For example:

> This endpoint technically works, but service X is being retired and new code must use service Y.

or:

> This query operates on a table containing 900 million rows in production, so this seemingly harmless scan is dangerous.

The value of the reviewer grows significantly when it has access to organizational context.

---

## Permissions Should Be Deliberately Limited

A reviewer does not necessarily need permission to modify code.

A conservative integration could have:

```text
Repository contents: read
Pull requests: read/write
Checks: write
Actions: read
```

while explicitly denying:

```text
Repository contents: write
Administration: write
Secrets
```

A system that only investigates and comments requires much less trust than an autonomous coding agent.

Writing code can be delegated to a separate fixer with stronger permissions.

---

## Human Review Does Not Necessarily Disappear

AI review may instead change what humans review.

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

# Code Review May Become Continuous Engineering Verification

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

For code review, those properties may matter almost as much as raw intelligence.