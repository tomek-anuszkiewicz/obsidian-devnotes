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
  - Shadow Twin and Differential Execution
  - Mechanical Sympathy in Legacy Modernization
  - The Ship of Theseus in Code Migration
  - Data-Oriented Design in Legacy Refactoring
  - Exploratory Pruning in Legacy Codebases
---

# Refactoring Legacy Systems with AI Agents

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

### The Limits of Naive Rewriting: The 4GL Curse and Hyrum's Law
However, the newfound viability of agentic rewriting must not be mistaken for the naive fantasy of "disposable code without guardrails":
1. **The 4GL / CASE / Executable UML Trap**: Every two decades, software engineering attempts to eliminate code by generating it from high-level prose or visual diagrams. As formalized in [[Testing in the Model, Agent, LLM Era]], natural language specifications in Markdown are inherently underspecified, probabilistic, and ambiguous. Attempting to prompt-generate a legacy rewrite purely from verbal descriptions fails because the author must specify every atomic nuance, creating a verbose, compiler-less programming language.
2. **Hyrum's Law and Characterization Blindspots**: Characterization tests capture known observed behaviors, but no test suite captures every undocumented reliance (such as exact collection ordering, whitespace formatting, or internal exception types). A green test suite does not guarantee zero breaking changes for downstream consumers.
3. **The Discipline of Invariant-Driven Strangler Fig**: Safe modernization requires anchoring the agent between **Frozen Living Specs** (semantic intent) and an **Ironclad Test Oracle**, validated through live traffic mirroring.

---

## The Psychological Dimension: Cognitive Ownership & The Human Circuit Breaker

Legacy systems are not merely technical artifacts; they dictate team psychology, developer identity, and organizational momentum. Successfully modernizing legacy code requires navigating profound psychological transitions.

### 1. Overcoming Learned Helplessness and Developer Cynicism
Beyond organizational economics, legacy codebases inflict a profound psychological toll on engineering teams: **learned helplessness**.
- When an engineer encounters a fragile, badly designed subsystem, their natural instinct to fix it is crushed by the reality of mechanical friction: months of tedious typing, manual regression testing, and defensive PR reviews.
- Over time, engineers adapt by adopting a defense mechanism of **passive cynicism**: complaining about how terrible the architecture is, making minimal cynical patches, and resigning themselves to the status quo.
- The arrival of AI agents fundamentally dismantles this psychological barrier:
  - When the mechanical cost of rewriting drops from months to hours, developers transition from **cynical complaining to active straightening**.
  - With characterization testing and vertical slice extraction automated by the agent, engineers no longer feel paralyzed by fear of breaking unseen dependencies.
  - The satisfaction of crafting clean, elegant software is restored, transforming the emotional relationship between the engineer and legacy systems.

### 2. Preserving Mental Continuity: Escaping the "Ship of Theseus" Alienation
A critical finding from empirical studies of AI code generation (such as GitClear's 2024 report across hundreds of millions of lines) is the surge in **code churn (doubled rates) and team alienation**:
- If an agent is allowed to rewrite an entire legacy module in a single unreviewed pass, the team suffers the **Ship of Theseus dilemma**: during a 3:00 AM production outage, the on-call engineer is forced to debug an alien codebase generated 48 hours earlier that nobody understands.
- **Mental Continuity via Living Specs and Granular Commits**: By forcing the agent to execute refactoring across multiple, atomic, reviewable commits (separating renames, extraction, structural changes, and rule changes), the engineering team maintains full cognitive ownership of the code's evolution. The architecture remains deeply understood, turning legacy modernization into a collaborative, disciplined ascent rather than a stochastic rewrite.

### 3. The "Frankenstein Intermediate Phase" and LLM Status-Quo Bias
When migrating or modernizing a subsystem, engineering teams frequently encounter the most dangerous trap in agent-assisted development: **the Frankenstein Intermediate Phase**.

#### A. The Hybrid Trap
During a profound architectural transition—such as moving from high-level abstract linear processing to fine-grained discrete state-machine execution, or from an in-memory monolith to asynchronous distributed queues—there is a natural temptation to build an intermediate compromise:
- Developers and agents attempt to bridge the two incompatible paradigms with glue code, synthetic queues, adapter wrappers, and complex outer polling loops.
- This results in an **unmaintainable hybrid monster**: it inherits the synchronization overhead, latency spikes, and edge-case fragility of both worlds without delivering the conceptual purity of either.
- The intermediate glue code often becomes more complex, fragile, and bloated than the original legacy code it was intended to replace.

#### B. The LLM Anchoring Bias (Status-Quo Rationalization)
When an agent is asked to debug or advance a codebase stuck in this intermediate state, it exhibits a powerful **anchoring bias**:
- LLMs are pattern-completion engines. When the context window is dominated by existing glue code, adapter wrappers, and historical git diffs, the model **naturally rationalizes the status-quo complexity**.
- The agent will enthusiastically justify the flawed hybrid architecture, proposing increasingly baroque patches, nested locks, and defensive null-checks to keep the Frankenstein monster functioning (see [[AI, Averaged Decisions, and Premature Convergence on Solutions]]).
- An agent will almost never conclude on its own: *"This entire intermediate bridge is an architectural dead-end; we must tear it down."* Instead, it defends the existing code simply because the context points to it.

#### C. The Human Circuit Breaker: Architectural Courage and Clean Breaks
Escaping the hybrid trap requires **human architectural courage**:
- The human engineer must act as the circuit breaker, decisively rejecting the agent’s plausible rationalizations and refusing to invest another hour in patching intermediate glue.
- The engineer must mandate a **clean break**: demanding the complete removal of the hybrid bridge and committing 100% to first-principles reality (e.g., pure, atomic discrete state transitions that directly own their execution phases and resource boundaries).
- Once the human provides the directional courage and enforces the clean paradigm, the agent’s zero-friction generative speed can be unleashed to build the pure, final architecture in days, rendering weeks of intermediate struggle obsolete.

---

## Phase 1: Reconnaissance & Exploratory Pruning

Before an architect can design a shadow service or write characterization tests, they must confront the sheer volume of unfamiliar legacy code. Human cognition is severely bottlenecked by **The Breadth Trap**:
- Human engineers struggle to discard code they have not personally inspected. The fear of triggering an unknown side-effect forces developers to spend days or weeks mentally traversing hundreds of peripheral call paths.
- The cognitive load of verifying whether an obscure helper function mutates global state, leaks memory, or touches database locks causes severe analytical paralysis.

### 1. Inverting Code Archaeology via LLM Path Slicing
Modern LLMs act as high-velocity **Symbolic Pruning Engines**:
- **Critical Path Slicing**: Given a target outcome or state mutation (e.g., *"How does an incoming trade order reach final ledger persistence?"*), an agent can traverse the entire AST across hundreds of files, isolating the exact active call graph while ignoring thousands of lines of irrelevant scaffolding.
- **Negative Safety Proofs (Proving Irrelevance)**: The most transformative capability of LLMs in code archaeology is not merely finding what *is* relevant, but **rigorously proving what is NOT relevant**:
  - The model can verify that adjacent background services, diagnostic pipelines, or telemetry hooks are strictly decoupled from the target transaction.
  - It proves negative invariants: *"Path B does not mutate state, does not acquire locks on table T, and has no side effects on domain entity E; it is functionally safe to ignore."*

### 2. Search-Space Reduction from Weeks to Hours
By using the LLM to prove the safety and irrelevance of non-critical branches, the architect prunes 90% of the cognitive search space:
- Instead of reading 100,000 lines over three weeks of anxious exploration, the architect isolates the 3 critical execution paths and their foundational invariants in 45 minutes.
- The architect can then focus 100% of their biological deep-work battery exclusively on the critical path, confident that the pruned branches cannot introduce unseen regressions.

---

## Phase 2: Disciplined Behavioral Extraction

Agents are exceptionally powerful for legacy modernization when guided by disciplined, behavior-preserving workflows.

Avoid broad, unconstrained instructions such as:
> *Rewrite this module using clean architecture.*

Prefer disciplined, step-by-step extraction:
1. **Map current behavior** via LLM path slicing and AST call-graphs.
2. **Add characterization tests** recording actual observed runtime outputs across historical datasets.
3. **Rename ambiguous concepts** and legacy domain terminology to reflect actual business meaning.
4. **Move code without editing it** (pure structural reorganization).
5. **Extract pure functions** isolating computational kernels from I/O side effects.
6. **Introduce explicit types** replacing generic dictionaries, raw tuples, or untyped bags.
7. **Isolate external side effects** (database writes, queue emissions, network calls) behind explicit boundaries.
8. **Compare old and new outputs** deterministically across production datasets.
9. **Only then introduce new business behavior**.

Characterization tests do not claim that the current behavior is correct. They record what the system currently does so that refactoring does not change it accidentally.

For pricing systems, run both implementations against historical data:
```text
old pricing result
vs.
new pricing result
```
During pure refactoring, results should remain identical, including rounding behavior and legacy quirks.

---

## Phase 3: The Shadow-Twin & Autonomous Differential Mirroring Pattern

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
5. **Virtual-Time & Time-Travel Diagnostics (`rr` / `Pernosco`)**: When a subtle, non-deterministic discrepancy occurs under production concurrency, the differential oracle captures a bit-exact record-replay trace. The agent micro-steps backwards through instruction cycles to pinpoint the exact microsecond where the shadow service diverged from legacy behavior.

### 4. Escaping the Premature Modernization Trap (The Second-System Effect)
The historical graveyard of failed software rewrites is paved with the **Second-System Effect** (Fred Brooks):
- When human developers rewrite a legacy system, they inevitably fall into the temptation: *"While we're rewriting this, let's fix the flawed authentication model, clean up the legacy field names, and add the three new features the business has been demanding!"*
- The scope explodes, dependencies break across the company, and the project collapses under its own ambitions.

The agentic paradigm enforces a strict **two-phase discipline**:

> **Phase 1: Bug-for-Bug Equivalence (Parity First)**  
> The sole objective is achieving 100% identical behavioral parity through mirroring. Every legacy quirk, peculiar sorting behavior, and edge-case response must be replicated, because existing enterprise systems silently depend on them. The shadow system is promoted to production only when zero differentials remain.

> **Phase 2: Evolutionary Modernization (Clean Extensions)**  
> Only after the shadow system has successfully replaced the legacy system—and is protected by a massive, empirical test suite accumulated during the mirroring phase—does the team begin adding new features, deprecating old endpoints, or optimizing data models.

### 5. The Zero-Semantic-Drift Baseline: The Discipline of the "Clean Refresh"
The single greatest failure mode in legacy migrations is the instinct to "improve" business logic, re-architect data schemas, or clean up naming conventions during the initial port:
- **Resisting the Siren Call of In-Flight Refactoring**: When an engineer or agent inspects legacy code, decades of accumulated cruft beg to be reorganized. Yielding to this impulse immediately conflates *migration errors* with *intentional behavioral changes*.
- **The "Clean Refresh" (Nowe Stare)**: The architecture mandates complete semantic conservatism. The first iteration of the modernized service must be a faithful, pristine reimplementation of the existing legacy semantics—warts, peculiar sorting conventions, and idiosyncrasies included.
- **Establishing the Shadow Twin Baseline**: The refreshed service is deployed immediately alongside the live legacy system in dark shadow mode. Before any architectural optimizations or algorithmic refactoring are permitted, the shadow twin must ingest mirrored live production traffic until empirical telemetry confirms **$0.000\%$ behavioral drift** across millions of real-world payloads.
- **Negative Proof Resolution**: As established in [[Formal Verification, Neurosymbolic AI, and the Negative Proof Dilemma]], functional specifications and unit tests cannot prove the absence of hidden side-effects or unexpected mutations. Running the "clean refresh" in shadow mode under production load serves as the empirical antidote, proving that no unstated invariants have been violated before the codebase undergoes progressive structural transformation within [[The 5-Layer System Stack for Agentic Software Engineering]].

---

## Phase 4: Mechanical Sympathy in Legacy Modernization (Data-Oriented Design)

When using agents to refactor legacy codebases (such as legacy enterprise C#, Java, or procedural systems), software architects must confront a subtle but dangerous failure mode: **LLM "Object-Oriented Contamination" and Mechanical Blindness**.

### 1. The LLM Object-Oriented Contamination Trap
Because frontier models have been pre-trained on vast repositories of enterprise code, their default statistical prior is to solve problems using deep object-oriented abstractions:
- When asked to clean up tangled procedural legacy code, an agent instinctively wraps everything in factories, strategy patterns, generic dependency-injected interfaces, and heap-allocated DTOs.
- While the resulting code looks aesthetically "clean" to human enterprise reviewers and passes all functional characterization tests, it is mechanically catastrophic: introducing multiple layers of pointer indirection, cache-hostile data structures, and continuous garbage collector / heap allocation pressure.

### 2. The Cache Blindspot: D-Cache vs. L1i Instruction Cache Thrashing
When modernizing high-throughput or latency-sensitive legacy services, test oracles create a dangerous illusion:
- **The Microbenchmark Illusion**: An agent unrolls legacy processing into thousands of specialized, discrete handlers or deep class hierarchies. In unit tests and synthetic microbenchmarks, the small test loop fits easily within CPU caches, branch predictors achieve 99.9% accuracy, and the profiler reports blazing speeds.
- **The Reality of Production (L1i Thrashing)**: In live multi-tenant production, execution does not loop over 10 operations. The CPU must jump across thousands of sprawling class methods and dispatch tables, rapidly blowing past the tiny **32 KB or 64 KB L1 Instruction Cache (L1i)** limit.
- While Data Cache (D-Cache) scales across megabytes of L2/L3 cache, instruction cache exhaustion forces the CPU to stall for hundreds of idle clock cycles while fetching instructions from slower RAM. Throughput collapses under production load despite passing all unit tests (see [[Software Engineering May Shift Toward Code Optimized for Agents]]).

### 3. Enforcing Data-Oriented Design (DOD) as an Invariant
To ensure modernized systems achieve true mechanical sympathy, the human architect must constrain the agent to enforce **Data-Oriented Design (DOD)**:
- **Contiguous Memory Buffers**: Struct-of-Arrays (SoA) layouts instead of Array-of-Structs (AoS) to maximize cache line packing (64-byte alignment).
- **Zero-Allocation Hot Paths**: Eliminating heap allocations, object boxing, and intermediate DTO mappings inside tight calculation pipelines.
- **Compact Dispatch Tables**: Replacing bloated, unrolled agent code with tightly packed jump tables and flat state machines whose entire execution loop remains permanently pinned in the L1i cache.

---

## Tactical Delivery: Atomic Commit Discipline & Review Hygiene

To prevent code churn and maintain mental continuity, refactoring must be structured into meaningful, reviewable commit histories.

A disciplined sequence is:
```text
1. Add characterization tests (locking in baseline behavior)
2. Rename and move only (zero semantic modification)
3. Extract types without behavior change
4. Extract calculation stages and isolate side effects
5. Introduce the explicit domain model / clean refresh
6. Change the business rule (if extending behavior)
7. Remove obsolete legacy code
```

Each commit must:
- Have **one distinct purpose**,
- Compile independently without errors,
- Pass all relevant regression tests,
- Clearly state in its commit message whether it preserves or alters behavior,
- Avoid mixing mechanical formatting with architectural changes.

### Anti-Pattern Commit Histories
Never allow commit streams such as:
```text
add implementation
fix compilation
fix tests
cleanup
```
Those commits describe the agent's internal trial-and-error mistakes, not the deliberate architectural evolution of the system.

A clean history allows any human reviewer to immediately distinguish:
1. Baseline existing behavior,
2. Structural preparation,
3. The exact business or architectural change,
4. Post-migration cleanup.

### Practical Working Rules Checklist

- **One purpose per commit**: Never bundle refactoring with business feature changes.
- **Every commit must be green**: Code must build and pass existing test suites at every commit boundary.
- **Strict category separation**: Keep rename, move, formatting, architectural refactoring, and behavior modifications in separate commits.
- **Immutable test assertions during refactoring**: Do not alter expected test values during behavior-preserving transformations.
- **Self-explanatory evolution**: Write commit messages that explain *why* the architectural boundary shifted.

---

## Relationship to the Knowledge Graph

- **[[Testing in the Model, Agent, LLM Era]]**: Canonical hub establishing the dual-steering architecture, the limits of test oracles, the 4GL curse, and ephemeral code discipline.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: Architectural counterpart governing mechanical sympathy, L1i cache density, and Data-Oriented Design against LLM OOP bias.
- **[[Software Entropy and the Zero-Friction Trap]]**: Explains how disciplined 1:1 isolation and atomic commits prevent code churn and Ship of Theseus team alienation.
- **[[Negative Knowledge and Explicit Architectural Dissents]]**: Formalizing codified rejections of flawed refactoring patterns and premature hybrid intermediate compromises.
- **[[Developer Satisfaction, Identity, and Burnout in the Age of Coding Agents]]**: The psychological transformation from learned helplessness and cynicism into active code straightening and architectural directorship.
- **[[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]]**: Runtime supervisory agents monitoring shadow services and triaging live differential telemetry.
- **[[AI Changes the Economics of Technical Debt]]**: How reducing the generative cost of rewrites flips the economics of legacy maintenance.
- **[[AI, Averaged Decisions, and Premature Convergence on Solutions]]**: Analyzes how LLMs exhibit status-quo anchoring bias and defend flawed hybrid compromises.
- **[[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]]**: Deciding when to patch local issues versus tearing down unmaintainable hybrid glue.
- **[[Designing Software for AI Agents]]**: The target architectural patterns (flat 1:1 modules, explicit boundaries) used when refactoring monoliths.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Step-by-step harness loops for safely modernizing legacy systems without regressions.
- **[[Formal Verification, Neurosymbolic AI, and the Negative Proof Dilemma]]**: Explains why formal specifications cannot guarantee the absence of hidden side-effects, establishing the necessity of the zero-semantic-drift shadow baseline.
- **[[The 5-Layer System Stack for Agentic Software Engineering]]**: The foundational system hierarchy framing where legacy refactoring harnesses interface between substrate efficiency and runtime telemetry.
