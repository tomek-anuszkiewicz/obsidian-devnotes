---
title: "Trustworthy Test Oracles for Coding Agents"
tags:
  - testing
  - ai-agents
  - verification
  - mutation-testing
  - software-engineering
aliases:
  - "Independent Test Oracles for Agent Repairs"
  - "Protecting Expected Behavior from Generated Implementations"
  - "Test Provenance Diagnostics and Flaky Agent Feedback"
  - "Disposable Implementation vs Ironclad Test Oracle"
  - "Ephemeral Code and Test Oracles"
  - "The Frozen Oracle Rule"
  - "The Limits of Test Oracles"
  - "Machine-Facing Test Diagnostics"
---

An agent writes an implementation and tests that encode the same mistaken assumption. Every check passes, but the application still violates the intended behavior. The missing ingredient is an expected result grounded independently of that implementation.

The feedback loop needs a trusted behavioral contract, checks that can expose relevant defects, and diagnostics the agent can use without redefining the requirement. It also needs to distinguish genuine regressions from unreliable tests; otherwise repair can damage correct code in response to random failures.

The sections below connect pre-implementation expectations, implementation replacement, mutation testing, coverage, provenance, diagnostics, and test stability. [[Testing in the Model, Agent, LLM Era]] develops the broader suite and execution strategy. [[Repairing Browser Tests Without Changing Scenario Intent]] applies the same protected-intent boundary to repairs of browser interaction mechanics.

## Tests become part of the agentic control loop

In traditional development, tests primarily served humans:

- they documented behavior,

- forced developers to think through design,

- exposed edge cases,

- prevented regressions,

- helped refactoring.

In an agentic workflow, tests gain another important role:

> They become executable constraints that the agent can use to verify its own work.

A coding loop can look like:

```text
specification
    ↓
generate / modify code
    ↓
compile
    ↓
run deterministic tests
    ↓
inspect failures
    ↓
repair
    ↺
```

The key advantage is that the agent does not need another model to judge every iteration.

The environment can provide a cheap and deterministic signal:

```text
PASS / FAIL
```

This makes tests fundamental to reliable agentic software development.

Natural language specifications are essential for establishing high-level domain context, architectural boundaries, and business rules. However, natural language is inherently ambiguous. Under deep context stacks or complex edge cases, models drift, lose track of constraints, or invent plausible-looking workarounds.

Automated test suites do not negotiate. When an assertion fails with a non-zero exit code, the model cannot rationalize the failure away. The deterministic failure halts the loop and forces the agent to inspect the failure, adjust the implementation, and re-run verification until the code satisfies the specification.

---

## Some tests should exist before code generation

For important behavior, tests should be created before implementation.

A useful workflow is:

```text
requirement / bug / specification
        ↓
agent proposes behavioral scenarios
        ↓
human reviews important scenarios
        ↓
agent generates executable tests
        ↓
tests become part of task definition
        ↓
agent generates implementation
        ↓
automated repair loop
```

The important human responsibility is not necessarily writing test code.

It is reviewing:

> What must be true?

For example:

```text
Invoice closing:

✓ Paid invoice can be closed
✓ Partially paid invoice cannot be closed
✓ Unpaid invoice cannot be closed
✓ Zero-value invoice can be closed without payment
✓ Cancelled invoice cannot be closed
```

Once this behavioral contract is accepted, the agent can generate the actual test implementation.

This avoids an important failure mode:

```text
agent misunderstands requirement
        ↓
agent writes incorrect test
        ↓
agent writes implementation matching incorrect test
        ↓
everything is green
```

Therefore some tests should behave almost like specification artifacts.

The implementation agent should not freely rewrite them simply because they fail.

This dynamic establishes the **Frozen Oracle Rule**: protect accepted behavioral assertions and reference fixtures while the agent changes the implementation. Do not let a difficult failure become permission to relax an expectation or delete coverage. Test harnesses may need translation, new tests may be added, and tests tied to obsolete internal structure may need adaptation, but those changes require a separate reviewed rationale that preserves supported behavioral coverage. Where practical, enforce protection of baseline artifacts through write permissions. Check translated tests against the original implementation and deliberately incorrect variants to establish that the checks still discriminate relevant failures.

### Characterization Tests Help Discover Missing Specifications

An undocumented legacy system may need investigation before anyone can write an accepted behavioral specification. Characterization tests record what the existing implementation does for selected inputs and initial states. Their purpose is discovery and protection of current behavior; they do not establish that the behavior is desirable.

Characterization is a purpose, not a test level. An isolated calculation may suit a unit test, while a rule implemented in a database trigger requires a check that includes the database. A tangled form handler may first need a test through the interface. Establish protection at an accessible boundary before a large refactor, then add narrower tests when calculations or rules can be isolated.

Let execution of the original check the agent's proposed expectations. Otherwise, one misunderstanding can be copied into the description, test, and replacement. Inspect the initial state, outputs, persisted changes, and relevant delayed effects. A mock verifying a scheduling call cannot establish durable storage or recovery after process restart. Record the evidence and any untested parts of that claim.

Once reviewed observations become an accepted compatibility baseline, protect them while changing the implementation. A later decision to correct legacy behavior should identify the changed expectation explicitly. [[Recovering Legacy System Behavior with AI Agents]] explains how these tests participate in an investigation, rather than merely checking an already understood requirement.

### The repro-first defect resolution mandate

The same discipline applies to fixing production defects. When resolving an issue, an agent should never immediately modify production code. Doing so encourages superficial patches that mask underlying state corruption without verifying root causes.

The bug-resolution cycle must follow an explicit four-step sequence:
1. **Author reproduction test**: The agent writes an isolated test capturing the exact failure preconditions and asserting the correct behavior.
2. **Confirm failure (Red)**: The test runner executes the test against the current codebase and verifies that it fails as expected.
3. **Targeted implementation fix (Green)**: The agent modifies production code to satisfy the reproduction test without breaking existing tests.
4. **Regression immunity**: The reproduction test is merged permanently into the regression suite, preventing future agent sessions from reintroducing the bug.

If an agent cannot write a test that fails before the code change, it does not yet understand the defect.

### Code disposability and the limits of test oracles

Strong deterministic tests can make replacing a well-bounded implementation more practical. They preserve important executable domain knowledge, alongside documented constraints, integration behavior, and operational requirements. Passing every test establishes agreement on the exercised cases; it does not establish that every edge case or invariant was captured. Before regeneration, identify gaps in the oracle and protect behavior that consumers depend on, including errors, effects, and performance where relevant.

Treat regeneration as a deliberate engineering choice. Frequent replacement can make incident diagnosis and change review harder unless the team retains accepted artifacts, source mappings, and a reproducible verification process. Incremental work remains a useful default; runtime migration or a major architectural change may justify replacement (see [[Large-Scale Code Migration with AI Agents]] and [[AI May Make Aggressive Code Optimization Economically Viable]]).

---

## Mutation testing becomes more interesting

There is a particular danger when models generate both production code and tests.

The implementation and tests may share the same misunderstanding.

Everything passes because both artifacts encode the same error.

Mutation testing can help detect weak generated tests.

For example, intentionally modify:

```text
amount > 0
```

into:

```text
amount >= 0
```

If no test fails, the generated suite probably does not constrain this behavior well enough.

Mutation testing therefore becomes especially useful as a quality check for AI-generated tests.

When a mutation engine swaps relational operators (`>` to `>=`), inverts boolean conditions, shifts boundary values, or drops statements, the test suite must catch it. If the suite continues to pass against mutated code, the mutation survived—proving that the generated tests are merely stepping through code paths without asserting true invariants. Forcing an agent to kill mutants is the most reliable automated check against green-by-default suites.

Keep the roles separate. A mutation tool such as Stryker.NET generates variants, runs the tests, restores the code and reports survivors. The agent can group survivors by business risk, propose boundary cases and implement approved tests. A human decides which survivors matter and rejects assertions tied only to implementation detail. A 100% mutation score is not the goal; the useful result is better coverage of intended behavior.

---

## Coverage becomes an even weaker metric

AI makes it extremely cheap to generate tests that increase:

```text
line coverage
branch coverage
```

without significantly increasing confidence.

A model could produce thousands of shallow tests and achieve very high coverage.

Therefore metrics such as these become more interesting:

- meaningful behavioral coverage,

- mutation score,

- invariant coverage,

- scenario coverage,

- regression coverage.

A useful warning is:

> AI makes coverage inflation cheap.

---

## Test provenance can become useful

Generated suites may become large enough that knowing why a test exists matters.

A test could be marked as originating from:

```text
requirement
production bug
human-reviewed scenario
generated edge case
security invariant
implementation discovery
historical regression
```

This helps determine how strongly the test should be protected.

For example:

```text
Human-reviewed business rule
→ implementation agent cannot automatically modify it

Generated exploratory test
→ agent may regenerate/refactor it more freely
```

---

## Test diagnostics become machine-facing

Historically, test failures were primarily written for humans.

In an agentic workflow they are also input to another machine.

Instead of:

```text
Assertion failed.
Expected false.
Actual true.
```

prefer:

```text
Invoice cannot be closed while payment status is Unpaid.

Invoice:
Id = 9281
Status = Open
PaymentStatus = Unpaid

Expected CanClose = false
Actual CanClose = true
```

Better diagnostics reduce the amount of reasoning and repository exploration required by the coding agent.

Structured, machine-readable diagnostics drastically reduce the token overhead and reasoning loops an agent spends diagnosing failures. Providing the explicit domain rule violated, full aggregate state, expected versus actual values, and precise source file coordinates allows the agent to target the fix immediately without wasting turns exploring the repository.

---

## Flaky tests become more expensive

Flaky tests were already harmful for human developers.

They can be even worse for agents.

A coding agent may interpret a random failure as evidence that its implementation is wrong and start modifying correct code.

This can produce unnecessary repair loops.

Therefore in agentic development:

> Determinism and test reliability become more important, not less.

In an autonomous loop, a single intermittent failure causes the agent to thrash: it modifies working production code to accommodate a spurious test failure, corrupting valid logic. Flaky tests cannot be tolerated in agent paths; they must be aggressively quarantined the moment non-deterministic behavior is detected.

---

Keep the expected business behavior and the candidate implementation distinguishable in the evidence. Review changes to the expectation explicitly, use meaningful faults to assess the checks, and make uncertainty in test results visible before asking an agent to repair production code.

## Related Notes

- [[Testing in the Model, Agent, LLM Era]] — Test layers, selection, deterministic execution, and live-model evaluations.
- [[Repairing Browser Tests Without Changing Scenario Intent]] — Repairing interaction code without changing the accepted scenario.
- [[When Is an AI Agent’s Code Ready to Merge]] — Protected rules, candidate-specific evidence, and controlled repair decisions.
