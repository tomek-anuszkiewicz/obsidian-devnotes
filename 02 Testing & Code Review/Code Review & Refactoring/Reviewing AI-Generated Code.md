---
title: Reviewing AI-Generated Code
tags:
  - code-review
  - ai-agents
  - software-engineering
  - verification
  - testing
  - developer-experience
aliases:
  - AI Code Review Practices
  - Verification of Agent Diffs
---

## Human Attention Becomes the Critical Resource

An agent can generate code faster than a human can honestly review it.

The danger is the illusion of understanding:

- code has good names,
    
- tests are green,
    
- the summary sounds convincing,
    
- the architecture looks familiar,
    
- most lines appear standard.
    

The reviewer may scan the diff without reconstructing the actual behavior.

When diffs are merged based on superficial plausibility, software entropy and frictionless code sprawl accelerate. Over time, the repository morphs into a codebase where every file compiles and passes tests, but no engineer on the team understands how the pieces interact, which invariants protect the database, or why specific trade-offs were made. When a severe production defect strikes—such as a distributed race condition, database connection pool exhaustion, or an inconsistent state transition across services—the generating agent hits a reasoning wall debugging distributed state without deterministic feedback loops. If engineers surrender their mental model during review, they are left operating an alien system they do not understand.

Review should therefore be organized around risk rather than file order.

Review first:

1. business rules,
    
2. public contracts,
    
3. migrations,
    
4. transactions and concurrency,
    
5. authorization,
    
6. ordering of side effects,
    
7. acceptance tests.
    

Review mechanical mapping and boilerplate later.

Standard code review tools display files alphabetically, burning mental energy on trivial configuration files, generated DTOs, and dependency injection wiring before the reviewer inspects core business logic. Prioritizing review by operational risk ensures critical boundaries receive scrutiny while focus is highest. If fatigue sets in, it happens on low-risk mechanical glue rather than state mutations that can corrupt production data.

A useful standard is:

> Before approving the change, the reviewer should be able to explain the complete new flow in their own words.

If they cannot, they probably have not understood the change sufficiently.

Specifically, an engineer should be able to answer four concrete operational questions before signing off:

1. **Execution and Transformation:** How does data enter, transform, and leave this component? Trace the primary path from entry point to persistence.
2. **Invariants and Constraints:** What conditions must always hold true? What prevents corrupted or half-formed state from being committed?
3. **Partial Failure Behavior:** What happens when an external HTTP call, cache write, or secondary database query fails halfway through execution? Does the system leave orphaned records, or does it roll back cleanly?
4. **Concurrency and Idempotency:** Can two worker processes or HTTP threads execute this operation on the same entity simultaneously without race conditions, duplicate writes, or deadlocks?

### Inspecting Tests as Critically as Production Code

Coding agents are remarkably adept at generating tests that pass without proving requirements. When an agent writes both the implementation and the test suite, it naturally mirrors its own blind spots across both. Inspect the test diff with the same skepticism applied to production code, looking for three recurring patterns:

- **Tautological Assertions:** Tests that assert mock outputs against hardcoded mock expectations. The test passes green, but only proves the mocking framework was configured as written, not that the integrated system behaves correctly.
- **Missing Negative Cases:** Agents lean heavily into happy paths. A pull request may include ten tests checking successful 200 OK responses, but zero tests for network timeouts, schema validation rejections, duplicate webhook deliveries, or authorization denials.
- **Vacuous and Overly Permissive Matchers:** Assertions that check only for broad conditions (such as asserting an object is non-null or an HTTP status is 200) without validating that payload contents, database state, and side effects match the business specification.

---

## Use Agents to Support Review, Not Replace It

A separate agent session can prepare:

- a map of the changed behavior,
    
- assumptions made by the implementation,
    
- high-risk files,
    
- missing edge cases,
    
- differences between old and new behavior,
    
- potential race conditions,
    
- test gaps,
    
- suspicious abstractions.
    

A skeptical review prompt can ask:

```text
Review this diff as a critical senior engineer.

Look for:
- incorrect business assumptions,
- architecture violations,
- race conditions,
- transaction boundary problems,
- incorrect idempotency,
- compatibility issues,
- security problems,
- missing negative cases,
- tests that pass without proving the requirement,
- unnecessary abstraction.
```

The second agent is an attention aid, not the final authority.

Because the authoring agent is biased toward justifying its own implementation choices, running an isolated session with an adversarial prompt prevents the model from rubber-stamping its own assumptions. The second agent points human focus directly toward potential landmines, but the final judgment, architectural verification, and approval remain strictly with the human engineer.

---

## Practical Working Rules

### For review

- Review risk, not file order.
    
- Start with business meaning.
    
- Inspect tests as critically as production code (see [[Tests Are for Verification, Not Architectural Navigation]]).
- Ask what assumption could make the whole solution wrong.
- Require the reviewer to explain the flow independently (see [[LLMs as a Code Review Team]]).
- Keep diffs small enough to understand honestly.
- Protect focused review time.

## Related Notes

- [[LLMs as a Code Review Team]] — Designing multi-perspective review teams to spot structural defects.
- [[Tests Are for Verification, Not Architectural Navigation]] — Preventing tests from becoming fragile rubber stamps.
- [[Correcting AI-Generated Code — Patch, Regenerate, or Change the Specification]] — Tactical decision-making when review identifies model defects.
- [[Software Decay and the Hidden Costs of Frictionless AI Code]] — Why uninspected AI additions degrade long-term code quality.
