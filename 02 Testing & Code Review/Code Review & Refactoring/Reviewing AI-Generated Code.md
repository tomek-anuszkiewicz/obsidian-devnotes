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
  - Behavior-Oriented Review Evidence
  - Human Review by Exception
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

## Route routine findings to repair and consequential decisions to people

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

The second agent supplies evidence. Acceptance authority belongs to the configured policy and the people responsible for decisions that the policy reserves for them.

An isolated review session can reduce anchoring on the author's explanation, but it does not guarantee independent reasoning or correct findings. Require evidence for important claims. A different model can add another perspective; it is not proof that the two reviewers have independent failure modes.

When a finding describes a clear defect within the approved task, return it to the coding agent for repair and repeat the relevant verification. A person need not inspect every naming violation or missing error case. Escalate when the process cannot resolve conflicting rules, changes accepted meaning, exceeds its budget, or reaches a decision requiring human authority. Low-risk changes can be accepted by a protected process if the organization explicitly permits that autonomy (see [[Acceptance Policies and Automated Repair in Agentic SDLC]]).

The requirement to understand a change remains important when a person is asked to approve it. It should not become a ritual human checkbox on every automatically verified change. Organizational ownership of the system also remains necessary even where individual low-risk patches are accepted automatically.

## Present changed behavior before presenting the file list

A diff shows edits. It leaves the reviewer to reconstruct the behavior those edits produce. Prepare a short evidence packet that starts with the user-visible or operational change, then shows the affected execution path, changed contracts, relevant tests, failure behavior, and unresolved decisions.

For a fee calculation, show the old and new result for representative orders, the inputs that select each branch, and the financial rule authorizing the change. Link the explanation to the exact candidate and evidence. A sequence diagram or small decision table can reveal a missing side effect more quickly than an alphabetical list of files.

The packet should answer:

- What behavior changes, and why was that change requested?
- Which invariants and contracts are preserved or intentionally revised?
- What did independent checks establish, and what did they not exercise?
- What specific decision remains for the reviewer?

Keep access to the raw diff, logs, and tests. Generated explanations can omit a path or confidently describe behavior the code does not implement. Verify important claims against the candidate rather than treating the summary as a substitute for evidence.

Existing tools can help with parts of this presentation. CodeRabbit documents [PR summaries and walkthroughs](https://docs.coderabbit.ai/), while Graphite documents [stacked pull requests and review workflows](https://graphite.com/docs/get-started). Those capabilities can reduce navigation work; the company still needs to decide what evidence and authority are required for acceptance. Product references were checked on 2026-10-29.

## Measure the cost and value of review

Track confirmed findings, rejected findings, repair rounds, reviewer latency, human decision time, and defects discovered after acceptance. A reviewer that emits many comments is not necessarily useful. A reviewer that passes everything cheaply may be missing important failures.

Associate repeated repairs with the rules that triggered them. If one convention causes constant oscillation, investigate the convention, examples, and implementation guidance together. Improve the process through controlled comparisons rather than adding another instruction after every disagreement (see [[Observability and Controlled Improvement of Coding Agent Harnesses]]).

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
