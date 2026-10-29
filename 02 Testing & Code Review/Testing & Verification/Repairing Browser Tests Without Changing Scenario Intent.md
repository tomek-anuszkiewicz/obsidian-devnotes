---
title: "Repairing Browser Tests Without Changing Scenario Intent"
tags:
  - testing
  - browser-automation
  - ai-agents
  - verification
  - test-maintenance
aliases:
  - "Protected Intent in Self-Healing E2E Tests"
  - "AI-Assisted Browser Test Maintenance"
  - "Repairing Test Mechanics Without Rewriting Expectations"
---

A browser test cannot locate the button that used to submit an order. The application may still provide the intended action under a changed structure, or the business behavior may actually be broken. A maintenance agent must determine which situation it has encountered before editing the test.

Separate the scenario's intended behavior from the automation that reaches and observes it. A selector or navigation sequence can be a repair candidate; a price, permission, state transition, or expected outcome remains part of the requirement being checked. A repaired execution also needs a visible status so it does not silently erase evidence that the deterministic test failed.

The sections below describe that maintenance boundary and the return to deterministic execution. [[Testing in the Model, Agent, LLM Era]] develops the surrounding test strategy, while [[Trustworthy Test Oracles for Coding Agents]] examines the independence and reliability of the expected result.

## Browser E2E tests can become partially self-healing

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

## AI should heal mechanics, not semantics

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

## Scenario intent may become more important than generated test code

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

## Use AI to maintain deterministic tests, not replace them

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

## Treat the Repair as a New Candidate

Preserve the original failure and the evidence for why the interaction changed. Inspect the proposed automation diff, verify that the scenario and its assertions still mean the same thing, and rerun the resulting deterministic test. Reaching a green result through a different route is not sufficient if the agent skipped the operation or weakened the observation.

When the agent cannot establish whether the UI change is mechanical or behavioral, return that uncertainty for investigation. Once the repair is accepted, ordinary test runs should use the maintained automation rather than needing the model to reinterpret the page on every execution.

## Related Notes

- [[Testing in the Model, Agent, LLM Era]] — Selecting and scheduling browser tests within a wider deterministic suite.
- [[Trustworthy Test Oracles for Coding Agents]] — Independent expectations, meaningful failures, and protected behavioral contracts.
- [[How AI Agents May Control Computers, Applications, and the Web]] — Browser structure, semantic operations, and other control interfaces.
