---
title: Testing in the Model, Agent, LLM Era
tags:
  - testing
  - software-engineering
  - ai-agents
  - mutation-testing
  - verification
  - test-pyramid
aliases:
  - Software Testing in the AI Era
  - Agent-Driven Test Strategies
  - "Deterministic Test Strategy and Model Evaluations"
---

Agents reduce the cost of authoring many kinds of tests, but execution time, diagnostic value, maintenance, and confidence still differ between them. A large generated suite can provide weak feedback if it repeats implementation detail or runs expensive checks at every edit.

This article develops the testing strategy: useful unit and component checks, broader scenarios, selection frequency, deterministic agent tests, live-model evaluations, and release behavior. [[Trustworthy Test Oracles for Coding Agents]] examines why the expected result can be trusted and how failures guide repair. [[Repairing Browser Tests Without Changing Scenario Intent]] develops a narrower maintenance loop for browser automation while keeping scenario intent protected.

The classical test pyramid is still useful, but it is no longer a complete description of how we should verify software in an agent-driven development process.

Its core economic principle remains valid:

> Prefer cheap, fast, deterministic verification where possible, and use slower, more expensive, integrated verification more selectively.

However, AI changes both the economics of test creation and the role tests play in development.

## We probably need fewer manually written unit tests

AI weakens some traditional reasons for manually writing unit tests.

Humans no longer necessarily need to write tests in order to:

- think through every implementation,

- discover basic design issues,

- generate boilerplate,

- cover obvious combinations.

Agents can do much of this.

Therefore:

> We may need far fewer manually authored unit tests.

But this does not necessarily mean:

> We need fewer useful unit tests.

Unit tests remain extremely valuable to agents because they provide cheap, precise feedback.

For example:

```text
E2E failure:
"Checkout failed"

vs.

Domain test failure:
Invoice.CanBePaid()
Expected false for Balance == 0
Actual true
```

The second result dramatically reduces the search space for the agent.

---

## Unit testing should become more selective

The agent era may finally make the weakness of many low-value unit tests more obvious.

Examples of questionable tests:

```text
GetName() returns Name

repository.Load() called exactly once

mapper.Map() called once

service calls dependency X and then dependency Y
```

These tests often encode implementation structure rather than meaningful behavior.

AI can cheaply generate thousands of them, creating:

- test inflation,

- maintenance cost,

- slower pipelines,

- resistance to refactoring,

- false confidence.

Instead, unit tests should concentrate on:

- business rules,

- calculations,

- state transitions,

- invariants,

- boundary conditions,

- authorization,

- tricky transformations,

- regression cases,

- deterministic concurrency behavior.

A better principle is:

> Test important behavior at the cheapest level that expresses it clearly.

Sometimes that is a unit test.

Sometimes it is a component test.

Sometimes it is an API or E2E test.

### The oracle blind spot: runtime behavior

Functional tests can check output equivalence (`actual == expected`) for exercised cases without measuring how the implementation behaves under production load.

An agent can generate an implementation that passes every functional unit test while introducing serious runtime problems:
- **Performance regressions:** More abstraction, allocation, or data conversion may make a frequently executed path slower without changing its output.
- **Resource growth:** A test can finish before an unbounded queue, connection leak, or retained object becomes visible.
- **Concurrency failures:** Unit tests rarely reproduce the timing and contention of production traffic.

Functional tests provide evidence about the checked answers under the tested conditions. They do not prove that the code will survive production traffic. Engineers remain responsible for memory layouts, data structures, and profiling under load.

### External ground truth and high-performance oracles

In high-throughput, stateful, or low-level systems (such as storage engines, simulation kernels, or financial ledger systems), synthetic unit tests written by agents are particularly vulnerable to shared blind spots: the agent writes the code and the tests based on the same flawed assumptions. To break out of this loop, verification must anchor to external, non-negotiable ground truth:

1. **Direct-injection execution harnesses**: Integration suites can spend most of their time on migrations, server startup, and network setup. A focused harness can inject test state at a supported entry point and replace external dependencies with lightweight test implementations. This shortens the feedback loop, but it does not replace tests of the complete deployed system.
2. **Golden reference differencing and anti-tamper contracts**: For serialized pipelines, parsers, codecs, and renderers, tests compare output buffers directly against verified reference data (byte-for-byte binary diffs or exact frame captures). The harness must enforce an anti-tamper contract: golden benchmark files and reference hashes reside in protected paths with read-only permissions during agent tasks. Modifying a golden file without an explicit human override flag fails the build immediately.
3. **Host performance measurement**: Benchmarks can compare latency distributions, throughput, allocations, and hardware counters against a baseline. A change in execution time is a signal to investigate, not proof of a particular CPU-level cause. Profiling and performance counters are needed before attributing it to branching, cache behavior, allocation, or another mechanism.

---

## The classical test pyramid may flatten

Historically, E2E tests were kept relatively scarce because they were:

- expensive to design,

- expensive to implement,

- expensive to maintain,

- slow,

- fragile.

AI changes especially the first three.

A model can help generate:

1. candidate E2E scenarios,

2. edge cases,

3. scenario descriptions,

4. Playwright or equivalent test code.

For example:

```text
Feature description
      ↓
LLM proposes 30 scenarios
      ↓
human reviews scenario list
      ↓
LLM generates test code
      ↓
tests run deterministically
```

This makes it economically reasonable to have more high-level tests than before.

The model is used during authoring:

```text
LLM → generate test
```

but execution stays deterministic:

```text
test runner → PASS / FAIL
```

This is an attractive division of responsibility.

---

## AI can explore the E2E scenario space

Models can also help generate broader sets of scenarios than humans typically write.

They can explicitly explore:

- happy paths,

- invalid sequencing,

- permissions,

- boundary values,

- retries,

- state transitions,

- concurrency,

- feature flags,

- unusual user behavior,

- historical regressions.

For example:

```text
role
× account state
× payment state
× feature flag
× locale
```

The model can identify combinations that are semantically different enough to deserve separate tests.

This may significantly increase high-level behavioral coverage.

---

## The pyramid may flatten in inventory, but not in execution frequency

Even if we generate many E2E tests, we should not necessarily execute all of them on every change.

For example:

```text
PR
- unit
- component
- selected E2E

merge
- broader E2E suite

nightly
- full scenario suite

release
- full regression suite
```

So the test pyramid may become flatter in terms of:

> number of authored tests

while remaining pyramid-like in terms of:

> execution frequency and cost.

This distinction is important.

---

## Most tests should not require model inference

Even when an application contains an LLM or an agent, most of its test suite can remain deterministic.

For example, we can test:

- context construction,

- tool schemas,

- permission checks,

- parsers,

- action validation,

- retry limits,

- file modifications,

- patch application,

- orchestration,

- tool execution,

- state transitions.

Agent trajectories can also be tested with scripted model responses.

For example:

```text
FakeModel:

1. SearchCode("Payment")
2. ReadFile("PaymentService.cs")
3. ProposePatch(...)
4. RunTests()
5. Finish()
```

The entire orchestration can then be verified without invoking a real model.

The model should be treated somewhat like another expensive and nondeterministic external dependency.

---

## Live-model evals should remain a relatively small layer

There are still behaviors that require real model inference:

- whether instructions are understood,

- whether a prompt change degrades behavior,

- whether a new model chooses the right tool,

- whether retrieved context is interpreted correctly,

- whether reasoning quality changed between model versions.

These tests are expensive and probabilistic.

They can therefore live separately:

```text
normal CI
---------
unit
component
integration
scripted-agent scenarios


nightly / release / model change
-------------------------------
live-model evals
```

The goal should be:

> Push as much correctness as possible into deterministic software and reserve model evaluation for the narrow boundary where model behavior itself matters.

---

## Test selection becomes important

AI may allow us to generate much larger test inventories.

Running everything on every edit is unnecessary.

An agent should be able to identify a relevant subset:

```text
modified PaymentService
      ↓
run:
- Payment domain tests
- Payment API tests
- checkout component tests
      ↓
repair loop
```

Later stages can run broader verification.

This keeps agent feedback loops fast while maintaining broad system coverage.

---

## Verify release compatibility and recovery as behavior

Agents can help construct a matrix of application, schema, message, and client versions that the deployment strategy must support. Run the new application against its intended schema, and verify that the previous application can read the schema and data left by the new release when rollback is promised. Application-first deployment requires a different combination from schema-first deployment; make those assumptions explicit.

A generated `Down` migration does not prove lossless recovery. Rehearse interruption, retry, data invariants, coexistence, and the supported recovery procedure on representative data. Preserve the evidence with the release so a recovery controller can check whether an automatic action is eligible (see [[Production Feedback and Safe Automated Recovery]]).

Dataset preparation needs its own checks. A masked subset can preserve foreign keys yet remove the condition that causes a defect, while a tiny sample can miss a production query plan. Verify both the data's permitted use and the properties the test needs (see [[Production-Like Test Data for Coding Agents]]).

## Resulting Testing Model

The classical test pyramid does not disappear.

But the agent era changes its interpretation.

A likely direction is:

```text
                  live-model evals
                       small

               broad E2E scenarios
                 more than today

              component / API tests
                    strong

            domain / invariant tests
                    strong

         trivial implementation tests
                   reduced
```

The biggest reduction may happen in mock-heavy, implementation-oriented unit testing.

The biggest growth may happen in:

- behavioral tests,

- component tests,

- generated E2E scenarios,

- regression tests,

- invariants.

---

## Core Principles

Several principles summarize the shift.

> **Tests become executable context for agents, not merely regression protection.**

> **Humans should increasingly review behavioral intent rather than manually author test boilerplate.**

> **Generate tests with models, but execute them deterministically whenever possible.**

> **Use AI to expand the test space, not to decide whether deterministic behavior is correct.**

> **Use AI to maintain deterministic tests, not to permanently replace their determinism.**

> **The implementation agent should not freely rewrite accepted behavioral tests simply because they fail.**

> **Put each important behavior at the cheapest test level that expresses it clearly.**

> **The test pyramid may flatten in test inventory while remaining a pyramid in execution cost and frequency.**

And perhaps the most important principle:

> **The better the deterministic verification around an agent, the less intelligence and reliability we need to trust in the agent itself** (see [[Building Determinism from Unpredictable Models]] and [[Tests Are for Verification, Not Architectural Navigation]]).

## Related notes

- **[[Tests Are for Verification, Not Architectural Navigation]]** — Preventing tests from turning into bloated, brittle navigational crutches.
- **[[AI May Make Aggressive Code Optimization Economically Viable]]** — Benchmarking and deterministic test suites as essential validation gates for automated performance optimization.
- **[[Building Determinism from Unpredictable Models]]** — Verification asymmetry and inner/outer verification loops.
- **[[Executable Architecture Tests for Coding Agent Guardrails]]** — Writing automated architectural invariant tests for coding agents.
- **[[Formal Verification and Runtime Safety Boundaries]]** — Combining symbolic invariants with machine learning implementations.
