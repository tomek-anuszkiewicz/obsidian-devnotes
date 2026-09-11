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

# Reviewing AI-Generated Code

> [!IMPORTANT]
> **The Cognitive Duty of Code Review**: In the agentic era, code review ceases to be a syntax or formatting gatekeeper—linters and compilers already solve mechanical checks. **Code review is the mandatory cognitive checkpoint where the human engineer constructs and internalizes their mental model of the system.** When reviewers fall into the trap of rubber-stamping clean, green-tested diffs without understanding internal state transitions and invariants, the team faces total paralysis ("dead in the water") the moment a production outage exceeds the model's reasoning horizon.

```text
Synthetic Code Generation (Fast, Zero-Friction)
                       ↓
        Passes Test Oracle & Linters
                       ↓
   [ THE ILLUSION OF UNDERSTANDING TRAP ] ──► Rubber-stamped without mental model
                       ↓                                   ↓
            Production Incident Strikes            Agent Hits Insolubility Horizon
                       ↓                                   ↓
        Human Summoned to Intervene ◄─────────────── Agent Thrashes / Hallucinates
                       ↓
   HUMAN HAS NO MENTAL MODEL → TOTAL SYSTEMIC PARALYSIS
```

---

## Executive Summary & Core Architectural Invariants

1. **Review as Cognitive Model Construction**: If a reviewer cannot explain the lifecycle, state mutations, and failure boundaries of the diff in their own words without looking at the LLM summary, the code must not be merged.
2. **The Insolubility Horizon**: AI agents excel at localized patches, but suffer cognitive thrashing when faced with non-deterministic race conditions, distributed deadlocks, or contradictory invariants. The human engineer is the sole fallback.
3. **Risk-First Order Over File-Order Traversal**: Never review diffs top-to-bottom in alphabetical file order. Audit highest-risk architectural invariants first: business rules, transaction boundaries, concurrency locks, security authorization, and external side-effects; review mechanical mapping and glue code last.
4. **The Green-Test Mirage**: An agent can generate an implementation that satisfies 100% of unit assertions while violating domain semantics or introducing catastrophic latency degradation. Tests prove what was anticipated, not what was omitted.
5. **Adversarial Multi-Agent Audit**: Deploy secondary, isolated agent personas with explicit skeptical directives (hunting unstated assumptions, missing negative branches, and race hazards) to guide human attention, never as the approving authority.

---

## Human Attention Becomes the Critical Resource

An agent can generate code faster than a human can honestly review it, dramatically increasing the risk of [[Software Entropy and the Zero-Friction Trap|software entropy and frictionless code sprawl]].

The danger is the illusion of understanding:

- code has good names,
    
- tests are green,
    
- the summary sounds convincing,
    
- the architecture looks familiar,
    
- most lines appear standard.
    

The reviewer may scan the diff without reconstructing the actual behavior.

Review should therefore be organized around risk rather than file order, recognizing that [[Why Business Logic Is the Hardest Part of Agentic Coding|business logic is the hardest part of agentic coding]] and cannot be verified by surface-level syntax checks.

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

## The "Intractable Bug" Trap: Why Reviewers Must Build a Mental Model

The greatest operational failure mode in an agent-assisted team is **the illusion that green tests eliminate the need to understand how the code works**.

When an agent produces a clean 300-line implementation, all unit tests pass, and the PR description sounds authoritative, reviewers face immense temptation to skim the diff and approve, forgetting that [[Testing in the Model, Agent, LLM Era|test oracles can suffer from incomplete specification]]. This treats the code as an opaque black box, which can be mitigated by deploying [[LLMs as a Code Review Team|specialized agent review teams]] to challenge assumptions.

### When the Agent Hits the Insolubility Horizon
Inevitably, every production system encounters failure modes that exceed an agent's reasoning capability:
- Non-deterministic race conditions and microsecond concurrency deadlocks,
- Latency cliffs caused by unexpected database connection pooling or cache invalidation storms,
- Deep domain state corruption where multiple subsystem invariants contradict each other,
- Low-level runtime quirks (GC pauses, memory fragmentation, socket exhaustion).

When faced with these problems, **an agent begins to thrash**. Because it lacks holistic architectural awareness, it generates superficial patches: wrapping calls in blind retries, adding arbitrary mutexes, masking null references, or introducing subtle semantic regressions that worsen the root problem.

### The Systemic Impasse: "Dead in the Water"
If the human engineer also abdicated understanding during code review, the team faces an existential operational deadlock:

```text
Production incident occurs
       ↓
Agent attempts fix → Agent thrashes / hallucinates (hits reasoning horizon)
       ↓
Human engineer summoned to intervene
       ↓
Human has zero mental model of the code (rubber-stamped an opaque diff)
       ↓
Total engineering paralysis ("Dead in the water")
```

### Review as Cognitive Duty: The Minimum Viable Mental Model
Code review is not a formatting gatekeeper; compilers and linters already handle syntax. 

**Code review is the mandatory cognitive checkpoint where the engineer constructs and refreshes their internal mental model of the system.**

A reviewer must never approve an agentic pull request unless they can independently explain:
1. **The Lifecycle and State Flow**: How do requests enter, mutate state, and exit the component?
2. **Invariants and Ownership**: What guarantees must hold true under all circumstances, and who owns the data?
3. **Failure Boundaries**: What happens when an external dependency times out, drops connection, or returns malformed data?
4. **Concurrency Assumptions**: Is the code re-entrant, thread-safe, and idempotent?

If you cannot sketch the architecture and failure paths without looking at the LLM summary, do not merge the code. When the agent fails in production, the human engineer is the only fallback.

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
---

## Relationship to the Knowledge Graph

- **[[LLMs as a Code Review Team]]**: How automated multi-agent reviewer teams assist humans by conducting initial adversarial checks.
- **[[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]]**: Codifying tribal review knowledge into continuous automated prompts.
- **[[Constraint Saturation and Rule Oscillation in Coding Agents]]**: Diagnosing when an over-constrained agent enters a thrashing loop between competing review rules.
- **[[Developing Features with AI Coding Agents]]**: Ensuring specifications and acceptance tests are reviewed before code implementation.
- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Focusing review energy on subtle domain misinterpretations rather than syntax.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: Explores the aesthetic bikeshedding trap where human reviewers reject machine code over harmless syntactic explicitness.
- **[[AI Changes the Role and Training of Software Engineers]]**: How the engineering role elevates toward skeptical review, risk control, and architectural design.
- **[[Developer Satisfaction, Identity, and Burnout in the Age of Coding Agents]]**: The cognitive fatigue and vigilance penalty of full-time agent diff auditing.
