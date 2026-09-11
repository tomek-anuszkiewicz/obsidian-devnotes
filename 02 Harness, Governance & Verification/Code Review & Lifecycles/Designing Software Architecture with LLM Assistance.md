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

> [!IMPORTANT]
> **The Epistemological Reality**: **An LLM's answer is not the architecture; it is a synthetic proposal generated from a probabilistic model of the system.** That proposal inherently blends explicit facts with inferred consequences, generic industry tropes, and unstated assumptions. **The architect's primary task is not to validate the proposed technology stack, but to validate the model of reality that produced the proposal.** LLMs must be used to expand the frontier of cheap, reversible experimentation—never to rubber-stamp irreversible architectural commitments.

```text
Problem Statement (Underspecified)
               │
               ▼
[ The Plausibility Trap ] ──► Model Fills Gaps with Generic Best Practices
               │             (Assumes linear state, eventual consistency, simple auth)
               ▼
Coherent, Well-Formatted, Plausible Architecture Proposal
               │
   ┌───────────┴───────────────────────────────────────────┐
   ▼                                                       ▼
[ NAIVE ACCEPTANCE ]                     [ RIGOROUS AGENTIC EXPLORATION ]
Assumptions accepted unexamined          1. Extract implicit assumptions
Catastrophic failure in production       2. Formulate falsification questions
                                         3. Synthesize divergent alternatives
                                         4. Run cheap empirical spikes
```

---

## Executive Summary & Core Architectural Invariants

1. **The Plausible Completeness Trap**: When requirements contain unstated ambiguities, models do not report an error; they silently complete the story using the most ubiquitous industry tropes (e.g., assuming idempotent retries, linear status workflows, or standard relational schemas). The resulting architecture looks comprehensive and professionally justified while resting on unverified assumptions.
2. **Validating Reality Before Technology**: Before evaluating whether to use event sourcing, microservices, or specific database topologies, the architect must rigorously audit the model's factual foundation: What did the LLM assume about concurrency, transaction boundaries, failure domains, and operational team topology?
3. **Forced Multi-Option Divergence**: Prompting an LLM for "the best architecture" triggers premature convergence on averaged, consensus designs (see [[AI, Averaged Decisions, and Premature Convergence on Solutions]]). High-leverage architects mandate the generation of at least five divergent options (the simplest, the incremental, the reversible, the radical, and the non-technical requirement change).
4. **Adversarial Falsification Prompts**: Deploy secondary review prompts with explicit instructions to assume the proposal is fatally flawed, tasking the model with identifying hidden coupling, unmodeled distributed failure states, and migration cliffs.
5. **Increasing Reversible Spikes**: The ultimate value of LLMs in architecture is collapsing the cost of prototyping. What previously required a two-month proof of concept can now be prototyped as an executable vertical spike in 48 hours, replacing speculative theoretical debate with empirical telemetry.

---

## 1. Where LLMs Excel vs. Where They Fail

```text
┌──────────────────────────────────────────┐  ┌──────────────────────────────────────────┐
│             LLM STRENGTHS                │  │              LLM BLINDSPOTS              │
├──────────────────────────────────────────┤  ├──────────────────────────────────────────┤
│ - Exploring unfamiliar technology spaces │  │ - Undocumented operational history      │
│ - Generating orthogonal alternatives     │  │ - Distinguishing essential vs accidental  │
│ - Mapping known trade-off matrices       │  │ - Tribal domain rules in engineers' heads│
│ - Rapid prototyping of vertical spikes   │  │ - Signaling that the prompt is incomplete│
│ - Adversarial red-teaming of proposals   │  │ - Status-quo bias toward common fads     │
└──────────────────────────────────────────┘  └──────────────────────────────────────────┘
```

The core failure mode is **epistemic silence**: an LLM rarely states, *"This problem is underspecified in ways that invalidate any recommendation."* Instead, it fills missing voids with plausible fiction.

---

## 2. Uncovering the Hidden Assumptions Layer

When an LLM produces an architectural design, it almost always smuggles in unverified axioms:
- *Temporal Coupling*: Assuming distributed asynchronous events arrive in strict chronological sequence.
- *Idempotency*: Assuming external webhook providers or upstream payment gateways support safe retries.
- *Data Locality*: Assuming that all required fields can be joined within a single transactional boundary without cross-datacenter latency.
- *Team Ergonomics*: Assuming the organization possesses the SRE and observability maturity to operate complex event-driven topologies.

### The Assumption Extraction Protocol
Before accepting any architectural proposal, run the **Assumptions Extraction Probe**:

```text
Analyze your previous architecture recommendation. 
List every assumption you made that was NOT explicitly stated in the input prompt.
Categorize them into:
1. Concurrency and ordering assumptions.
2. Failure domain and recovery assumptions.
3. Organizational and operational capability assumptions.
4. Data volume and access pattern assumptions.
Rank them by: If this assumption is false, how severely does the architecture collapse?
```

---

## 3. The 5-Vector Architectural Generation Framework

To prevent premature convergence on generic templates, force the model across five structural axes:

```text
                                Architectural Request
                                          │
    ┌──────────────┬──────────────┬───────┴──────┬──────────────┬──────────────┐
    ▼              ▼              ▼              ▼              ▼              ▼
[ SIMPLEST ] [ INCREMENTAL ] [ REVERSIBLE ] [ ROBUST ]   [ RADICAL ]   [ NON-TECHNICAL ]
Single       Add module to   Decoupled via  Strict state Pre-allocated Eliminate need
process,     existing        adapter; easy  machine; zero allocation,   by changing
flat tables  monolith        to discard     ambient data discrete SIMD  business rule
```

For every option, the model must supply:
1. **The Invariants It Preserves**: Transactional, performance, and boundary invariants.
2. **The Conditions It Requires**: What must be true for this to succeed.
3. **When It Is Catastrophic**: Explicit anti-patterns and disqualifying constraints.
4. **The Cheap Disproof Experiment**: A microbenchmark or spike that can disprove viability in under 24 hours.

---

## 4. Reusable Architectural Steering Prompts

### Phase A: Problem Space & Ambiguity Extraction
```text
Role: Principal Systems Architect.
Task: Analyze the following business and technical requirement. Do NOT design an architecture yet.
Do NOT select technologies or frameworks.

Output Requirements:
1. Identify all under-specified operational boundaries, throughput expectations, and latency limits.
2. Formulate the top 10 critical questions whose answers would materially alter the architectural choice.
3. Highlight the 3 riskiest unstated assumptions a junior team would make when reading this prompt.
4. Identify legacy coupling or non-functional constraints that typical designs overlook.
```

### Phase B: Adversarial Red-Teaming
```text
Assume the recommended architecture is deployed into multi-tenant production and experiences a 
catastrophic outage during peak traffic.

Conduct a post-mortem identifying:
1. The exact failure cascade (e.g., thread starvation, connection pool exhaustion, unhandled retry storms).
2. Which component violated Hyrum's Law by depending on an undocumented implementation detail.
3. Why the monitoring and telemetry failed to pinpoint the root cause immediately.
4. The migration or deployment step that secretly introduced the regression.
```

---

## 5. Architectural Scaffolding for Agentic Maintenance

When designing software that will subsequently be implemented and maintained by autonomous agents, the architecture must optimize for **agent ergonomics** (see [[Designing Software for AI Agents]]):
- **1:1 File Isolation**: One domain operation equals one file, containing inputs, validation, business logic, and outputs in a flat vertical slice.
- **Explicit Call Graphs**: Avoid dynamic reflection, invisible aspect-oriented middleware, and magic dependency-injection auto-scanners that blind an agent's static context window.
- **Deterministic Verification Anchors**: Ensure every architectural boundary is guarded by a fast, machine-executable test harness that provides instant binary feedback.

---

## Relationship to the Knowledge Graph

- **[[Designing Software for AI Agents]]**: Translating high-level architectural proposals into agent-friendly codebases.
- **[[Competitive advantage in the age of commodity AI]]**: Why asking provocative architectural questions creates defensibility over generic LLM templates.
- **[[AI, Averaged Decisions, and Premature Convergence on Solutions]]**: Mitigating the risk of models prematurely converging on conventional, mediocre designs.
- **[[Emergence, Latent Space Synthesis, and How Targeted Prompts Crystallize Insight]]**: How real-world friction prompts crystallize novel architectural models.
- **[[Scaling a Modular Monolith with Local-or-Remote Module Execution]]**: A concrete case study of designing flexible, future-proof module topologies with LLMs.
- **[[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]]**: Attributing defects to architectural vs specification flaws.
