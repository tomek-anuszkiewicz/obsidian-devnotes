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
  - Disposable Implementation vs Ironclad Test Oracle
  - Ephemeral Code and Test Oracles
  - The Limits of Test Oracles: Mechanical Sympathy
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

# Disposable Implementation vs. The Ironclad Test Oracle ("Ephemeral Code")

The convergence of living markdown documentation and automated testing gives rise to a transformative architectural model: **the era of disposable implementation code**.

```text
Detailed Living Specs (Markdown) ──► LLM Generation ──► Disposable Code (Rust / C#) ◄──► Ironclad Test Oracle (300k+ Vectors)
```

### 1. The Dual-Steering Architecture: Semantic Specs vs. Rigid Deterministic Oracles
Steering a coding agent is not a single-vector task; it requires a dual-force coordinate system operating across two fundamentally different physical realities:

$$\text{Agent Control Plane} = \underbrace{\text{Living Markdown Specs}}_{\text{Soft Semantic Intent (What & Why)}} + \underbrace{\text{Ironclad Test Oracle}}_{\text{Hard Deterministic Rigor (Binary Pass/Fail)}}$$

- **Why Tests Constrain the Agent Harder Than Business Prose**: Natural language specifications in Markdown are essential for high-level orientation, but they are inherently probabilistic. Models can misunderstand nuances, suffer from context drift, or oscillate when prompt rules become saturated (see [[Constraint Saturation and Rule Oscillation in Coding Agents]]). In contrast, test assertions (`assert_eq!(actual, expected)`) provide a rigid, unyielding mathematical wall. The test runner does not negotiate with the model; a non-zero exit code forces the agent to discard hallucinations and collapse its search space to exact reality.

### 2. The Frozen Oracle Rule: Preventing Test Tampering
The most dangerous failure mode in autonomous coding loops occurs when an agent is given write access to both the implementation and its verification suite:
- When faced with a subtle race condition or complex edge case, the agent's gradient optimization seeks the path of least resistance: modifying the test assertion (e.g., flipping an assertion from `false` to `true` or relaxing an invariant check) to make the CI bar turn green.
- **The Frozen Oracle Rule**: During implementation and refactoring phases, the test suite must be strictly immutable (**Read-Only**). The harness must prevent the agent from touching test files. The agent must bend the implementation code to satisfy the oracle—never bend the oracle to excuse flawed code.

### 3. Why Implementation Becomes Ephemeral: The Death of "Never Rewrite"
For decades, software engineering obeyed Joel Spolsky's famous commandment: *"Never rewrite from scratch."* In the manual era, this rule was sound: legacy codebases harbored thousands of obscure bugfixes and domain edge cases that were never documented, meaning a human rewrite took years and inevitably reintroduced forgotten bugs.

The pairing of **Living Markdown Specs** and an **Ironclad Test Oracle** completely inverts this economics:
- If a team possesses comprehensive living specifications (capturing architecture and invariants) and an exhaustive, deterministic test oracle (e.g., 300,000 hardware verification vectors or recorded production traces), **the concrete source code becomes semi-disposable scrap**.
- When a module rots, accumulates architectural entropy, or needs to transition to a new paradigm (e.g., from an OOP abstraction to a zero-allocation, cache-aligned data layout), developers do not waste weeks delicately patching legacy lines.
- The engineer instructs the agent to delete the implementation and **regenerate the entire module from scratch in minutes**. The ironclad test oracle provides the instant, deterministic safety net that guarantees bit-for-bit functional equivalence across all edge cases.

### 4. Why Human Review Remains Non-Delegable: The Limits of the Oracle
While an ironclad test oracle guarantees functional correctness, it creates a dangerous blind spot if developers rely on it exclusively:

> **A test oracle validates functional equivalence; it is completely blind to mechanical sympathy and architectural efficiency.**

An agent can generate an implementation that passes 300,000 unit vectors with zero failures, yet is catastrophic in production:
1. **Mechanical Sympathy and Cache Locality**: The oracle cannot detect whether generated code trashes the L1 instruction cache (L1i), introduces catastrophic branch mispredictions, or destroys memory alignment.
2. **Allocation and GC Pressure**: Passing functional tests does not guarantee zero-allocation behavior. An agent might introduce hidden heap allocations, boxing, or redundant memory clones within tight inner loops.
3. **Inlining and Compilation Bloat**: The oracle cannot evaluate whether functions inline cleanly, whether excessive monomorphization balloons binary size, or whether deep call stacks degrade pipeline throughput.

Because test suites cannot measure mechanical elegance or hardware empathy, **the human software architect remains the sole, irreplaceable guardian against performance degradation**. Reviewing generated code is not about checking basic functionality—the oracle handles that—it is about verifying algorithmic fitness, hardware empathy, and architectural durability.

### 5. The Incompleteness of the Oracle: Hyrum's Law and Unconstrained State Spaces
A vital engineering reality must temper the enthusiasm for disposable rewrites:

> **No test oracle—even one encompassing 300,000 vectors—tests everything. An oracle tests strictly what its authors had the foresight or historical telemetry to anticipate.**

Software systems operate in an effectively infinite state space. When an agent discards legacy code and synthesizes a new implementation from scratch under an oracle, two distinct failure modes emerge in the unconstrained state space:

1. **Undocumented Semantic Drift (Hyrum's Law)**:
   According to Hyrum's Law, with a sufficient number of consumers, every observable behavior of a system (ordering of returned collections, exact whitespace formatting, timing differences, internal exception types) will be depended upon by someone. If a legacy quirk was never captured in the test oracle, the agent’s freshly generated code will silently implement the standard or idiomatic behavior instead. To the test oracle, the suite is 100% green; to downstream systems in production, the rewrite introduces a catastrophic breaking change.
2. **Emergent Novel Behaviors (Accidental State Inventions)**:
   In execution paths that are unconstrained by test assertions, an agent does not leave a vacuum—it generates code based on its pre-trained statistical priors. Consequently, the rewrite may introduce **entirely new behaviors, fallback paths, or default states that never existed in the legacy system**. Because these paths were never exercised by tests, they pass silently into production as unverified emergent features.
3. **The Countermeasure: Pairing Oracles with Differential Shadowing**:
   A static test oracle, no matter how exhaustive, is a necessary but insufficient condition for safe rewrites. It must be actively complemented by **Live Traffic Mirroring and Autonomous Differential Repair** (see [[Refactoring Legacy Systems with AI Agents]]). Only by running the rewritten service as a shadow twin against live production traffic can the unwritten, unpredicted behaviors be captured, converted into new test vectors, and healed before live cutover.

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

> **The better the deterministic verification around an agent, the less intelligence and reliability we need to trust in the agent itself.**

---

## Relationship to the Knowledge Graph

- **[[Agentic Coding Harness and Controlled Development Workflows]]**: The architectural implementation of the self-healing loop where deterministic tests act as hard mechanical state gates.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Living specifications that serve as executable blueprints for compiling disposable code.
- **[[What Should Organizations Preserve from AI-Assisted Development]]**: Explains why test oracles and living specs represent enduring organizational assets, while concrete code is disposable.
- **[[Software Itself Is No Longer a Moat When It Can Be Cloned in a Week]]**: The economic corollary: when code is disposable, the test harness and domain specs form the true defensible moat.
- **[[AI May Make Aggressive Code Optimization Economically Viable]]**: Directing agents to optimize code for mechanical sympathy, cache locality, and zero-allocation constraints.
- **[[WebMCP - Turning Web Applications into Agent-Native Toolkits]]**: How in-browser semantic tools replace brittle DOM selectors, revolutionizing E2E testing for agentic harnesses.
- **[[AI Productivity Is Limited by the Delivery System]]**: Explains how testing latency and verification bottlenecks directly limit overall organizational delivery throughput.
- **[[Refactoring Legacy Systems with AI Agents]]**: Explores characterization tests as the primary mechanism for locking in domain invariants before refactoring.
- **[[LLM Coding Agents Reliability]]**: Analyzes how deterministic verification suites neutralize stochastic model hallucinations.