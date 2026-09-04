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

A useful standard is:

> Before approving the change, the reviewer should be able to explain the complete new flow in their own words.

If they cannot, they probably have not understood the change sufficiently.

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

---

## Practical Working Rules

### For review

- Review risk, not file order.
    
- Start with business meaning.
    
- Inspect tests as critically as production code.
    
- Ask what assumption could make the whole solution wrong.
    
- Require the reviewer to explain the flow independently.
    
- Keep diffs small enough to understand honestly.
    
- Protect focused review time.
