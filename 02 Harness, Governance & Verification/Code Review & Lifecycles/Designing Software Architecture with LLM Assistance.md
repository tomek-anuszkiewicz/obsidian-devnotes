---
title: Designing Software Architecture with LLM Assistance
tags:
  - software-architecture
  - system-design
  - ai-agents
  - llm
  - decision-making
  - tradeoff-analysis
aliases:
  - LLM-Assisted Software Architecture
  - Architecture Exploration with AI
  - Validating the Model of Reality
  - The Plausible Completeness Illusion
  - Reversible Architectural Experimentation
---

# Designing Software Architecture with LLM Assistance

When you ask an AI model to design an architecture for a new system, it will produce a well-formatted, professional document in thirty seconds. It will recommend microservices, event streaming, caching layers, and clean architectural boundaries.

The dangerous part is that the proposal will sound completely plausible.

The fundamental rule when designing software architecture with LLMs is:

> **An LLM's proposal is not an architecture; it is a hypothesis generated from an incomplete mental model of your system.**

Because language models are trained on public code and generic best practices, they silently fill unstated ambiguities with conventional industry tropes. **The architect's job is not to choose between the technologies the model proposed, but to validate the model of reality that produced the proposal.**

```text
Underspecified Problem Statement
               │
               ▼
[ The Plausibility Trap ] ──► Model Fills Gaps with Generic Best Practices
               │             (Assumes linear state, eventual consistency, simple auth)
               ▼
Polished, Plausible Architecture Proposal
               │
    ┌──────────┴───────────────────────────────────────────┐
    ▼                                                       ▼
[ NAIVE ACCEPTANCE ]                     [ RIGOROUS ARCHITECTURAL SPARRING ]
Assumptions accepted unexamined          1. Extract implicit assumptions
Catastrophic failure in production       2. Formulate falsification questions
                                         3. Force divergent alternatives
                                         4. Run cheap empirical spikes
```

---

## Core Invariants

1. **The Plausible Completeness Trap**: When requirements omit critical details, models do not stop to ask questions; they silently make assumptions (e.g. assuming messages always arrive in order or database transactions are cheap). The resulting design looks complete while resting on unverified foundations.
2. **Validate Reality Before Choosing Technology**: Before debating whether to use event sourcing, microservices, or specific databases, audit the model's assumptions: What did it assume about data volume, network latency, team size, and failure boundaries?
3. **Forced Multi-Option Divergence**: Prompting an LLM for "the best architecture" triggers premature convergence on generic, over-engineered defaults (see [[AI, Averaged Decisions, and Premature Convergence on Solutions]]). Architects must force the model to present at least five divergent options (the simplest, the incremental, the reversible, the robust, and the non-technical option).
4. **Adversarial Red-Teaming**: Never ask an agent if a design is good. Instruct it to assume the design failed catastrophically in production and write a post-mortem identifying the root cause.
5. **Reversible Spikes Over Theoretical Debates**: The highest-leverage use of LLMs in architecture is collapsing the time required to build an exploratory prototype from weeks to hours, replacing speculation with real latency and throughput data.

---

## 1. Where LLMs Excel vs. Where They Struggle

```text
┌──────────────────────────────────────────┐  ┌──────────────────────────────────────────┐
│              LLM STRENGTHS               │  │              LLM BLINDSPOTS              │
├──────────────────────────────────────────┤  ├──────────────────────────────────────────┤
│ • Exploring unfamiliar technology spaces │  │ • Undocumented legacy system quirks      │
│ • Generating orthogonal trade-off options│  │ • Understanding team operational limits  │
│ • Rapidly drafting exploratory spikes    │  │ • Signaling that requirements are vague  │
│ • Identifying standard failure modes     │  │ • Strong bias toward complex industry fads│
│ • Adversarial red-teaming of proposals   │  │ • Conflating PoC speed with prod readiness│
└──────────────────────────────────────────┘  └──────────────────────────────────────────┘
```

The greatest danger is **cognitive silence**: an LLM rarely says, *"I cannot answer this because you haven't told me your data consistency requirements."* It simply invents a plausible assumption and moves forward.

---

## 2. The Assumption Extraction Protocol

Whenever an LLM produces an architectural proposal, it smuggles in unstated assumptions:
- **Ordering**: Assuming distributed messages arrive in exact chronological sequence.
- **Idempotency**: Assuming third-party payment or notification webhooks can be safely retried without side effects.
- **Data Locality**: Assuming all required customer records can be queried in a single fast join.
- **Operational Capacity**: Assuming your team has dedicated infrastructure engineers to manage complex event brokers.

Before evaluating the proposal, run this extraction prompt:

```text
Analyze your previous architecture proposal.
List every assumption you made that was NOT explicitly stated in my original prompt.

Group them into:
1. Concurrency, ordering, and transaction assumptions.
2. Failure recovery and network reliability assumptions.
3. Operational complexity and team maintenance assumptions.
4. Data volume, query patterns, and latency assumptions.

For each assumption, answer: If this assumption is completely false, how does this 
architecture fail?
```

This single prompt strips away the polished veneer and exposes the real trade-offs you must decide.

---

## 3. The 5-Vector Divergence Framework

Never accept a single "recommended" architecture. Force the model to explore distinct options across five practical vectors:

```text
                                Architectural Request
                                          │
    ┌──────────────┬──────────────┬───────┴──────┬──────────────┬──────────────┐
    ▼              ▼              ▼              ▼              ▼              ▼
[ SIMPLEST ] [ INCREMENTAL ] [ REVERSIBLE ] [ ROBUST ]   [ RADICAL ]   [ NON-TECHNICAL ]
Single       Add module to   Decoupled via  Strict state Pre-allocated Eliminate need
process,     existing        adapter; easy  machine; zero allocation,   by changing
flat tables  monolith        to discard     ambient data high-perf loop business rule
```

For each option, require the model to specify:
1. **What It Solves**: The core trade-off it optimizes for.
2. **The Conditions It Requires**: What must be true about your domain for this to work.
3. **When It Is a Disaster**: Concrete failure modes where this option is completely wrong.
4. **The 24-Hour Experiment**: A cheap prototype or benchmark that could prove or disprove viability tomorrow.

---

## 4. Practical Sparring Prompts

### Phase 1: Problem Discovery Before Solution Design
```text
Act as a Principal Systems Architect. Analyze the following business requirement, 
but do NOT design a system or select any technologies yet.

Your tasks:
1. Identify all underspecified operational requirements, concurrency limits, and latency targets.
2. Formulate the top 8 critical questions whose answers would completely change the architectural approach.
3. List the 3 most dangerous assumptions an engineer would make when reading this request.
4. Highlight non-functional constraints (compliance, disaster recovery, migration) that are missing.

Stop here. Wait for my answers before proposing any architecture.
```

### Phase 2: Adversarial Failure Post-Mortem
```text
Assume we implemented your recommended architecture and deployed it to multi-tenant production. 
Six months later, during a peak marketing campaign, the system suffers a catastrophic 4-hour outage.

Write the post-mortem report:
1. What was the exact cascading failure sequence (e.g. connection pool exhaustion, unhandled retry storm, database deadlocks)?
2. Which component failed because of an undocumented operational reality?
3. Why did our monitoring and alerting fail to catch the root cause early?
4. What fundamental architectural trade-off was violated?
```

---

## 5. Designing for Future Agent Maintenance

When designing software that will be maintained by coding agents, the architecture itself must be **agent-friendly** (see [[Designing Software for AI Agents]]):

1. **Focused 1:1 Module Boundaries**: Keep individual domain operations self-contained in dedicated files. Large "god classes" flood an agent's prompt context, leading to hallucinations.
2. **Explicit Dependency Injection**: Avoid dynamic reflection, ambient global state, or magical auto-wiring that hides how data moves. If an agent cannot see where a dependency comes from in the AST, it cannot safely modify it.
3. **Automated Verification Harnesses**: Every architectural boundary must have a fast, automated test harness that gives immediate pass/fail feedback (see [[Testing in the Model, Agent, LLM Era|automated test harnesses]]).

---

## Practical Rules for Teams

1. **Never ask for "the best architecture"**: Always ask for divergent options with explicit trade-offs.
2. **Dissect the assumptions first**: Before discussing database choices or frameworks, verify what the model assumed about reality.
3. **Use prototypes to resolve uncertainty**: If two architectures look viable on paper, have an agent build quick prototypes of both on temporary branches to compare real performance.
4. **Human ownership of decisions**: Use the model to expand your thinking and test for blind spots, but keep final architectural responsibility strictly with the human engineer.

---

## Related Notes

- **[[Designing Software for AI Agents]]**: Architectural principles that make codebases easy for autonomous agents to navigate and maintain.
- **[[AI, Averaged Decisions, and Premature Convergence on Solutions]]**: Why LLMs default to conventional, averaged designs and how to force divergent thinking.
- **[[How AI Changes Prototyping and the Path from PoC to Production]]**: Using rapid disposable spikes to test architectural hypotheses before committing to production.
- **[[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]]**: Deciding when to fix code locally versus revisiting foundational architectural decisions.
- **[[Competitive advantage in the age of commodity AI]]**: How rigorous architectural questioning creates engineering advantages over generic AI templates.
- **[[Testing in the Model, Agent, LLM Era]]**: Grounding architectural designs in automated, deterministic verification oracles.
