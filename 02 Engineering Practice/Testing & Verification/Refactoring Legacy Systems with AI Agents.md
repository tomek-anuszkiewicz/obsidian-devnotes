---
title: Refactoring Legacy Systems with AI Agents
tags:
  - legacy-code
  - refactoring
  - ai-agents
  - software-engineering
  - migration
  - testing
aliases:
  - Legacy Migration with Agents
  - AI-Driven Code Modernization
  - The Legacy Dilemma: Maintaining vs Rewriting with AI
  - Automated Straightening of Legacy Code
  - Complexity Masking in Legacy Systems
  - The Frankenstein Intermediate Phase
  - The Hybrid Trap in AI Refactoring
  - LLM Anchoring and Status-Quo Bias
---

## The Legacy Dilemma: Maintaining with Agents vs. Automated Straightening (Rewriting)

When an enterprise possesses a massive codebase plagued by decades of technical debt, labyrinthine architecture, and undocumented runtime coupling, it faces a fundamental strategic dilemma:

> **Should the organization use AI agents to maintain and patch the legacy monolith, or should it use agents to aggressively "straighten out" and rewrite the system into a modern, agent-native architecture?**

```text
Option A: The Maintenance Trap (Complexity Masking)
leave legacy spaghetti intact → use agents to navigate & patch → context costs explode + hidden dependencies trigger regressions

Option B: Automated Straightening (Agentic Strangler Fig)
extract behavior via tests → isolate pure business rules → rapidly rewrite into 1:1 flat modules → future maintenance costs collapse
```

### Why Maintaining Legacy with Agents Is a Trap
Many organizations default to Option A because agents make legacy systems feel superficially easier to navigate. However, this is a dangerous illusion:

1. **The Context and Token Tax**: Navigating tangled code requires massive context windows, RAG retrieval across thousands of files, and complex prompt scaffolding just to make small changes. Every subsequent feature or bugfix pays this compounding tax.
2. **Hidden Dependencies and Blast Radius**: Legacy code is rarely modular. A seemingly local change can trigger an unmapped database trigger, rely on ambient thread-local state, or violate an undocumented temporal ordering constraint. Agents cannot infer what is not visible in their context, leading to subtle, catastrophic regressions.
3. **The Complexity Masking Problem**: Because agents can patch the system in 15 minutes, management loses the incentive to fix the underlying architecture. The system rots while maintaining the illusion of productivity.

### The Economic Inversion: Why Rewriting Becomes Viable
In classical software engineering, rewriting a large legacy system from scratch was considered suicidal (the classic "Things You Should Never Do" warning). Human rewrites took years, cost millions, and invariably lost thousands of obscure edge cases discovered over decades of production.

AI agents invert this economic calculation:
- **Abundant generative capacity**: What took a team of humans six months to rewrite can now be drafted, typed, and structured by an agent in days.
- **Automated extraction of domain truth**: The agent does not need to guess the requirements. It can inspect production execution traces, database logs, and legacy procedures to generate hundreds of **characterization tests** that lock in existing behavior before a single line is rewritten.
- **The Automated Strangler Fig Pattern**: The rewrite does not happen as a high-risk "Big Bang." Instead, the agent extracts one vertical slice at a time, covers it with characterization tests, isolates the pure business rules, and rewrites it into a clean, 1:1 agent-native structure.

For an enterprise, **straightening out the legacy code once is vastly cheaper over time than continuously paying the cognitive and operational tax of agent-assisted legacy maintenance.**

### The Psychological Shift: Overcoming Learned Helplessness and Developer Cynicism

Beyond organizational economics, legacy codebases inflict a profound psychological toll on engineering teams: **learned helplessness**.
- When an engineer encounters a fragile, badly designed subsystem, their natural instinct to fix it is crushed by the reality of mechanical friction: months of tedious typing, manual regression testing, and defensive PR reviews.
- Over time, engineers adapt by adopting a defense mechanism of **passive cynicism**: complaining about how terrible the architecture is, making minimal cynical patches, and resigning themselves to the status quo.
- The arrival of AI agents fundamentally dismantles this psychological barrier:
  - When the mechanical cost of rewriting drops from months to hours, developers transition from **cynical complaining to active straightening**.
  - With characterization testing and vertical slice extraction automated by the agent, engineers no longer feel paralyzed by fear of breaking unseen dependencies.
  - The satisfaction of crafting clean, elegant software is restored, transforming the emotional relationship between the engineer and legacy systems.

### The "Frankenstein Intermediate Phase" and LLM Status-Quo Bias

When migrating or modernizing a subsystem, engineering teams frequently encounter the most dangerous trap in agent-assisted development: **the Frankenstein Intermediate Phase**.

#### 1. The Hybrid Trap
During a profound architectural transition—such as moving from high-level abstract linear processing to fine-grained discrete state-machine execution, or from an in-memory monolith to asynchronous distributed queues—there is a natural temptation to build an intermediate compromise:
- Developers and agents attempt to bridge the two incompatible paradigms with glue code, synthetic queues, adapter wrappers, and complex outer polling loops.
- This results in an **unmaintainable hybrid monster**: it inherits the synchronization overhead, latency spikes, and edge-case fragility of both worlds without delivering the conceptual purity of either.
- The intermediate glue code often becomes more complex, fragile, and bloated than the original legacy code it was intended to replace.

#### 2. The LLM Anchoring Bias (Status-Quo Rationalization)
When an agent is asked to debug or advance a codebase stuck in this intermediate state, it exhibits a powerful **anchoring bias**:
- LLMs are pattern-completion engines. When the context window is dominated by existing glue code, adapter wrappers, and historical git diffs, the model **naturally rationalizes the status-quo complexity**.
- The agent will enthusiastically justify the flawed hybrid architecture, proposing increasingly baroque patches, nested locks, and defensive null-checks to keep the Frankenstein monster functioning (see [[AI, Averaged Decisions, and Premature Convergence on Solutions]]).
- An agent will almost never conclude on its own: *"This entire intermediate bridge is an architectural dead-end; we must tear it down."* Instead, it defends the existing code simply because the context points to it.

#### 3. The Human Circuit Breaker: Architectural Courage and Clean Breaks
Escaping the hybrid trap requires **human architectural courage**:
- The human engineer must act as the circuit breaker, decisively rejecting the agent’s plausible rationalizations and refusing to invest another hour in patching intermediate glue.
- The engineer must mandate a **clean break**: demanding the complete removal of the hybrid bridge and committing 100% to first-principles reality (e.g., pure, atomic discrete state transitions that directly own their execution phases and resource boundaries).
- Once the human provides the directional courage and enforces the clean paradigm, the agent’s zero-friction generative speed can be unleashed to build the pure, final architecture in days, rendering weeks of intermediate struggle obsolete.

---

## The Shadow-Twin and Autonomous Differential Mirroring Pattern

When rewriting an aging, critical service from scratch, the greatest existential danger is breaking undocumented downstream assumptions. Rather than speculative manual testing, the agentic paradigm enables **Zero-Risk Rewriting via Autonomous Differential Mirroring**.

```text
                               ┌────────────────────────────────────────┐
                               │       Production Traffic Gateway       │
                               │        / Message Bus Event Stream      │
                               └───────────────────┬────────────────────┘
                                                   │
                         ┌─────────────────────────┴─────────────────────────┐
                         ▼ (Live Traffic)                                    ▼ (Mirrored Traffic)
             ┌───────────────────────┐                           ┌───────────────────────┐
             │     LEGACY SERVICE    │                           │    SHADOW SERVICE     │
             │ (Decaying, bloated)   │                           │ (Clean, agentic code) │
             └───────────┬───────────┘                           └───────────┬───────────┘
                         │                                                   │
                         │ Live Response                                     │ Shadow Response
                         ▼                                                   ▼
                [Production Client]                               ┌─────────────────────────────┐
                                                                  │    DIFFERENTIAL ORACLE      │
                                                                  │   (Observer Agent/Filter)   │
                                                                  └──────────────┬──────────────┘
                                                                                 │
                                                                                 │ Disparity Detected (Δ != 0)
                                                                                 ▼
                                                                  ┌─────────────────────────────┐
                                                                  │  AUTONOMOUS REPAIR AGENT    │
                                                                  │  1. Generates test vector   │
                                                                  │  2. Diagnoses & patches     │
                                                                  │  3. Re-compiles shadow      │
                                                                  └─────────────────────────────┘
```

### 1. The Immutable External Facade
In legacy rewrites, the internal implementation must not dictate the migration boundary:
- **Internal Freedom**: The internal database, data structures, state machines, and file layouts can be completely reimagined into flat, high-performance, agent-native code (e.g. eliminating ORMs in favor of direct [[Agentic Coding with EF Core and SQL Server|explicit SQL]] or branchless state tables).
- **External Immobility**: The **facade**—how the service interacts with the rest of the enterprise—must remain 100% frozen:
  - Exact REST/gRPC contracts, header propagation, and error payloads,
  - Identical queue consumer/producer semantics and message serialization,
  - Preserved transactional boundaries and database side-effects.

To all upstream and downstream callers, the new service is a bit-for-bit behavioral drop-in replacement.

### 2. Live Traffic Mirroring (Dark Launching)
Rather than relying on artificial mocks, the shadow service is deployed directly into production alongside the legacy service:
- The production gateway duplicates (mirrors) real live requests to the shadow service asynchronously.
- The shadow service executes the request, but its responses are discarded so live clients remain insulated from any errors.
- Both systems process real-world load, production concurrency, and realistic payloads.

### 3. The Autonomous Differential Repair Loop
An automated observer agent acts as a **Differential Oracle**:
$$\Delta = \text{Response}_{\text{Legacy}} - \text{Response}_{\text{Shadow}}$$
1. **Disparity Ingestion**: Whenever $\Delta \neq 0$ (a mismatched status code, a divergent JSON field, an unexpected ordering, or a rounding difference), the differential oracle captures the full input payload and both outputs.
2. **Instant Test Vector Generation**: The oracle converts the failure into an immutable, reproducible regression test vector in the shadow test suite.
3. **Autonomous Self-Healing**: A background repair agent is triggered with the new test vector, diagnoses the root cause in the shadow code, applies a minimal patch, and verifies that all existing regression vectors remain green.
4. **Convergence to Zero**: Over days of continuous live mirroring across millions of production events, discrepancies systematically converge to zero. The shadow service empirically proves 100% behavioral equivalence under real-world conditions.

### 4. Escaping the Premature Modernization Trap (The Second-System Effect)
The historical graveyard of failed software rewrites is paved with the **Second-System Effect** (Fred Brooks):
- When human developers rewrite a legacy system, they inevitably fall into the temptation: *"While we're rewriting this, let's fix the flawed authentication model, clean up the legacy field names, and add the three new features the business has been demanding!"*
- The scope explodes, dependencies break across the company, and the project collapses under its own ambitions.

The agentic paradigm enforces a strict **two-phase discipline**:

> **Phase 1: Bug-for-Bug Equivalence (Parity First)**  
> The sole objective is achieving 100% identical behavioral parity through mirroring. Every legacy quirk, peculiar sorting behavior, and edge-case response must be replicated, because existing enterprise systems silently depend on them. The shadow system is promoted to production only when zero differentials remain.

> **Phase 2: Evolutionary Modernization (Clean Extensions)**  
> Only after the shadow system has successfully replaced the legacy system—and is protected by a massive, empirical test suite accumulated during the mirroring phase—does the team begin adding new features, deprecating old endpoints, or optimizing data models.

---

## Refactoring Legacy Code with Agents

Agents are exceptionally powerful for legacy modernization when guided by disciplined, behavior-preserving workflows.

Avoid broad, unconstrained instructions such as:

> Rewrite this module using clean architecture.

Prefer disciplined, step-by-step extraction:

1. map the current behavior,
    
2. add characterization tests,
    
3. rename ambiguous concepts,
    
4. move code without editing it,
    
5. extract pure functions,
    
6. introduce explicit types,
    
7. isolate side effects,
    
8. compare old and new outputs,
    
9. only then introduce new business behavior.
    

Characterization tests do not claim that the current behavior is correct. They record what the system currently does so that refactoring does not change it accidentally.

For pricing systems, run both implementations against historical data:

```text
old pricing result
vs.
new pricing result
```

During pure refactoring, results should remain identical, including rounding behavior.

---

## Use Multiple Reviewable Commits

Agents can be instructed to create a meaningful commit history.

A useful sequence is:

```text
1. Add characterization tests
2. Rename and move only
3. Extract types without behavior change
4. Extract calculation stages
5. Introduce the explicit domain model
6. Change the business rule
7. Remove obsolete code
```

Each commit should:

- have one purpose,
    
- compile independently,
    
- pass relevant tests,
    
- clearly state whether it changes behavior,
    
- avoid mixing mechanical and semantic changes.
    

Do not allow histories such as:

```text
add implementation
fix compilation
fix tests
cleanup
```

Those commits describe the agent's mistakes, not the evolution of the system.

A good history allows a reviewer to distinguish:

- existing behavior,
    
- structural preparation,
    
- the exact business change,
    
- later cleanup.
    

---

## Practical Working Rules

### For commits

- One purpose per commit.
    
- Every commit should compile and pass tests.
    
- Keep rename, move, formatting, refactoring, and behavior changes separate.
    
- Do not alter expected test values during behavior-preserving refactoring.
    
- Make the commit history explain the evolution of the system.
---

## Relationship to the Knowledge Graph

- **[[Software Entropy and the Zero-Friction Trap]]**: Explains why zero typing friction makes agents exceptional refactorers capable of executing comprehensive rewrites.
- **[[AI Changes the Economics of Technical Debt]]**: How reducing the generative cost of rewrites flips the economics of legacy maintenance.
- **[[AI, Averaged Decisions, and Premature Convergence on Solutions]]**: Analyzes how LLMs exhibit status-quo anchoring bias and defend flawed hybrid compromises.
- **[[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]]**: Deciding when to patch local issues versus tearing down unmaintainable hybrid glue.
- **[[Testing in the Model, Agent, LLM Era]]**: Using automated characterization tests to lock in legacy invariants before straightening code.
- **[[Designing Software for AI Agents]]**: The target architectural patterns (flat 1:1 modules, explicit boundaries) used when refactoring monoliths.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Step-by-step harness loops for safely modernizing legacy systems without regressions.
