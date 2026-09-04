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
---

The classical test pyramid is still useful, but it is no longer a complete description of how we should verify software in an agent-driven development process.

Its core economic principle remains valid:

> Prefer cheap, fast, deterministic verification where possible, and use slower, more expensive, integrated verification more selectively.

However, AI changes both the economics of test creation and the role tests play in development.

## 1. Tests become part of the agentic control loop

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

---

## 2. Some tests should exist before code generation

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

---

## 3. We probably need fewer manually written unit tests

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

## 4. Unit testing should become more selective

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

---

## 5. The classical test pyramid may flatten

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

## 6. AI can explore the E2E scenario space

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

## 7. The pyramid may flatten in inventory, but not in execution frequency

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

## 8. Browser E2E tests can become partially self-healing

Browser automation remains useful through tools such as:

- Playwright,
    
- Selenium/WebDriver,
    
- Cypress,
    
- similar browser automation frameworks.
    

A new opportunity is AI-assisted recovery when automation breaks for mechanical reasons.

Example:

```text
Click "Pay now"
```

The test expects:

```text
button[name="Pay now"]
```

but the UI changes to:

```text
"Complete purchase"
```

Traditional behavior:

```text
locator fails
→ test fails
→ developer investigates
```

AI-assisted behavior:

```text
locator fails
      ↓
collect:
- DOM
- accessibility tree
- screenshot
- current URL
- intended step
      ↓
model searches for likely equivalent control
      ↓
temporary fallback action
      ↓
suite continues
```

This can be very useful because a single stale locator does not need to block the remaining suite.

However, the result should not silently become a normal success.

A useful status model is:

```text
PASS
PASS_WITH_HEALING
FAIL
```

For example:

```text
Checkout scenario: PASS_WITH_HEALING

Expected:
button "Pay now"

Used:
button "Complete purchase"

Suggested test patch available.
```

The generated repair can later become a normal deterministic test change.

---

## 9. AI should heal mechanics, not semantics

Self-healing must have strict boundaries.

Potentially healable:

```text
selector changed
label changed
element moved
navigation moved
DOM structure changed
```

Not healable:

```text
wrong price
payment failed
wrong permission
missing data
incorrect business state
```

The model may repair:

> How do I reach the intended state?

It must not redefine:

> What is the intended state?

For example:

```text
Expected:
Payment successful

Actual:
Payment failed
```

must remain a failure.

An LLM should never reinterpret the acceptance criterion simply to make the test pass.

---

## 10. Scenario intent may become more important than generated test code

An E2E test can increasingly be viewed as three artifacts:

```text
1. Intent
   "User can cancel an unpaid order"

2. Automation
   generated Playwright code

3. Runtime evidence
   DOM / accessibility tree / screenshots / trace
```

The stable artifact is primarily the intent.

The automation can be:

- regenerated,
    
- repaired,
    
- refactored,
    
- updated after UI changes.
    

This is an important change.

Instead of treating every line of test automation as handcrafted permanent code, some E2E automation may become partially generated infrastructure.

---

## 11. Use AI to maintain deterministic tests, not replace them

A useful hierarchy is:

```text
stable deterministic locator
        ↓
deterministic fallback
        ↓
AI-assisted semantic recovery
        ↓
mark as healed
        ↓
generate permanent patch
        ↓
review
        ↓
future executions deterministic again
```

We should avoid architectures where an LLM looks at every page and decides what to click during every test run.

That would convert a cheap deterministic suite into an expensive probabilistic system.

A better principle is:

> Use AI as a maintenance bridge around deterministic tests.

---

## 12. Most tests should not require model inference

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

## 13. Live-model evals should remain a relatively small layer

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

## 14. Mutation testing becomes more interesting

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

---

## 15. Coverage becomes an even weaker metric

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

## 16. Test provenance can become useful

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

## 17. Test diagnostics become machine-facing

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

---

## 18. Flaky tests become more expensive

Flaky tests were already harmful for human developers.

They can be even worse for agents.

A coding agent may interpret a random failure as evidence that its implementation is wrong and start modifying correct code.

This can produce unnecessary repair loops.

Therefore in agentic development:

> Determinism and test reliability become more important, not less.

---

## 19. Test selection becomes important

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

# Resulting Testing Model

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

# Core Principles

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

> **The better the deterministic verification around an agent, the less intelligence and reliability we need to trust in the agent itself.**