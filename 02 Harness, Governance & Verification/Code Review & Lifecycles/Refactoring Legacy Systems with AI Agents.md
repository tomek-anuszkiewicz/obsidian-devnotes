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
  - The Frankenstein Intermediate Phase
  - Shadow Twin and Differential Execution
---

# Refactoring Legacy Systems with AI Agents

In traditional software development, rewriting a large legacy system from scratch was an organizational death trap. Human rewrites took years, cost millions, and invariably broke subtle edge cases discovered over decades of production. Teams resigned themselves to living with fragile legacy monoliths, cautiously applying local patches and hoping nothing broke.

AI coding agents invert this economic calculation: **aggressively straightening out and rewriting legacy subsystems using automated characterization tests and shadow traffic mirroring is vastly cheaper than continuously paying the cognitive and operational tax of maintaining a legacy labyrinth.**

```text
Option A: The Maintenance Trap
Leave legacy spaghetti intact ──► Patch with LLMs ──► Context bloat explodes + regressions multiply

Option B: Automated Straightening (Agentic Strangler Fig)
Lock behavior with tests ──► Re-synthesize clean modular slices ──► Future maintenance costs collapse
```

---

## Core Invariants

1. **Automated Straightening Over Complexity Masking**: Using agents to navigate spaghetti code merely masks architectural decay. Extracting business rules and rewriting vertical slices into clean, modular components delivers 10x lower operational overhead than perpetual legacy patching.
2. **The "Frankenstein Intermediate Phase" Trap**: During migrations, developers and agents reflexively build complex hybrid adapters and synthetic bridges. Because LLMs have a strong status-quo bias, they will aggressively rationalize this intermediate mess. Escaping it requires human engineering courage to demand clean breaks.
3. **Parity First, Improvements Second (Avoiding the Second-System Effect)**: The fatal flaw of historical rewrites is trying to add new features while rewriting. Modernization mandates a strict two-phase discipline: **bug-for-bug parity first** ($0.000\%$ behavioral drift under live mirrored traffic), followed by evolutionary optimization only after parity is proven.
4. **Dark Differential Traffic Mirroring**: Deploying the modernized service as a shadow twin receiving mirrored live production traffic catches unmodeled divergence, turning real production traffic into an automated regression suite.
5. **Disciplined Atomic Commits**: Refactoring must be split into distinct, reviewable commits (tests first, renames and structural moves second, clean domain model third, new features fourth). Never bundle behavioral changes with structural refactoring.

---

## 1. The Legacy Dilemma: Endless Patching vs. Automated Straightening

When faced with a massive legacy codebase plagued by technical debt and hidden coupling, an engineering organization faces a fundamental choice:

> **Should the team use AI agents to maintain and patch the legacy code, or use agents to aggressively rewrite the system into clean, modular services?**

### Why Maintaining Legacy with Agents Fails Long-Term
Many teams default to patching because agents make tangled code superficially easier to navigate:
1. **The Context and Token Tax**: Navigating tangled code requires huge context windows and complex retrieval across hundreds of files. Every subsequent feature or bugfix pays this compounding tax.
2. **Hidden Side Effects**: Legacy code rarely enforces modular boundaries. A seemingly isolated function may rely on ambient global state, database triggers, or undocumented ordering rules. What is invisible in the prompt context turns into a production regression.
3. **Complexity Masking**: Because agents can generate a patch in fifteen minutes, management loses the incentive to fix the underlying architecture. The system decays while giving the illusion of progress (see [[AI Changes the Economics of Technical Debt]]).

### Why Straightening Out Becomes Viable
With coding agents:
- **Typing and structural reorganization are cheap**: What took a human team six months of tedious boilerplate extraction can be drafted and structured by an agent in days.
- **Automated extraction of domain truth**: The agent does not need to guess requirements. It can inspect production execution traces, database procedures, and unit histories to generate hundreds of **characterization tests** before a single line of production code is changed.
- **The Strangler Fig Pattern**: The rewrite does not happen as a high-risk Big Bang. Instead, the agent extracts one vertical slice at a time, locks in its behavior, and routes traffic over once verified.

---

## 2. Phase 1: Reconnaissance and Path Slicing

Before an engineer can rewrite a legacy component, they must understand what it actually does. Human developers often suffer from analysis paralysis when facing 100,000 lines of unfamiliar legacy code, terrified of touching something that might break a distant subsystem.

Coding agents excel as **path-slicing engines**:

1. **Critical Path Slicing**: Given an entry point and a target outcome (e.g. *"How does an incoming billing payload reach database persistence?"*), an agent can traverse the call graph across dozens of files, isolating the active execution path while ignoring thousands of lines of irrelevant scaffolding.
2. **Proving Irrelevance**: The most valuable task an agent performs during legacy analysis is proving what code is *not* relevant:
   - Verifying that adjacent background jobs or telemetry handlers do not mutate the target record.
   - Confirming that a legacy flag is permanently disabled and its branch can be safely discarded.
3. **Reducing Cognitive Scope**: Instead of reading 100,000 lines over several weeks, the engineer isolates the core transaction flow in an afternoon, focusing their review energy exclusively on the critical path.

---

## 3. Phase 2: Disciplined Behavioral Extraction

Never prompt an agent with vague, sweeping refactoring instructions:
> *"Rewrite this billing module using clean architecture."*

Sweeping prompts cause the model to invent new domain abstractions, hallucinate missing business rules, and drop edge cases.

Instead, follow a disciplined, step-by-step extraction workflow:

```text
1. Map Call Graph ──► 2. Add Characterization Tests ──► 3. Rename & Move Code
                                                                 │
7. Verify Zero Drift ◄── 6. Isolate Side Effects ◄── 5. Extract Pure Functions
         │
         ▼
8. Introduce New Features or Remove Dead Code
```

1. **Map the current behavior**: Document the exact inputs, outputs, and side effects.
2. **Add characterization tests**: Write tests that capture what the system *currently* does across real historical data, warts and quirks included. Characterization tests do not assert that the behavior is correct; they assert that it does not change unexpectedly.
3. **Rename and move files only**: Clean up confusing variable names and reorganize file structures without changing a single line of logic.
4. **Extract pure functions**: Separate calculation logic from database reads, HTTP calls, and message emissions.
5. **Introduce explicit types**: Replace untyped dictionaries, raw string payloads, and magic numbers with strongly typed domain models.
6. **Isolate external side effects**: Put database writes and network calls behind explicit interfaces.
7. **Verify zero drift**: Run both implementations against historical production data. The outputs must match identically.

---

## 4. Phase 3: Shadow Traffic Mirroring (Dark Launching)

When rewriting a mission-critical service, relying solely on unit and integration tests is insufficient. Real production traffic contains edge cases and concurrency patterns that no synthetic test suite anticipates (see [[Testing in the Model, Agent, LLM Era|the limits of test oracles]]).

The safest way to replace a legacy service is **asynchronous differential shadow mirroring**:

```text
                             Production API Gateway
                                       │
                     ┌─────────────────┴─────────────────┐
                     ▼ (Live Request)                    ▼ (Mirrored Copy)
         ┌───────────────────────┐           ┌───────────────────────┐
         │     LEGACY SERVICE    │           │    SHADOW SERVICE     │
         │ (Decaying, monolithic)│           │ (Clean, modern code)  │
         └───────────┬───────────┘           └───────────┬───────────┘
                     │                                   │
                     ▼ Live Response                     ▼ Discard Response
            [Production Client]             ┌─────────────────────────────┐
                                            │    DIFFERENTIAL ORACLE      │
                                            │  Compares: Legacy vs Shadow │
                                            └──────────────┬──────────────┘
                                                           │ Disparity Detected (Δ != 0)
                                                           ▼
                                            ┌─────────────────────────────┐
                                            │   AUTOMATED REPAIR AGENT    │
                                            │ Creates regression test &   │
                                            │ fixes shadow implementation │
                                            └─────────────────────────────┘
```

1. **The Frozen Facade**: The external API contract, message format, and error schemas must remain completely identical. Upstream callers should not need to know that the underlying implementation was replaced.
2. **Live Traffic Duplication**: The gateway duplicates incoming live requests to the shadow service asynchronously. The shadow service runs the request, but its response is discarded so live users are never affected.
3. **Differential Comparison**: An automated observer compares the response from the legacy service with the response from the shadow service. If there is any discrepancy in payload fields, status codes, or rounding, the observer captures the request and both responses.
4. **Automated Test Generation**: The discrepancy is immediately turned into an automated test vector. An agent analyzes the diff, patches the shadow service, and verifies that the fix resolves the discrepancy without regressing existing tests.
5. **Promotion to Production**: Once the shadow service runs against millions of live production requests with zero discrepancies over several days, cutover is trivial and risk-free.

---

## 5. Escaping the "Frankenstein Intermediate Phase"

During major refactorings, teams frequently fall into the **hybrid trap**:
- Developers attempt to bridge two incompatible architectures with complex adapter wrappers, translation layers, and background polling loops.
- This intermediate code is often more fragile, confusing, and bug-ridden than the legacy system it was supposed to replace.

When an agent is asked to work in this intermediate state, its natural pattern-matching works against the team:
- The context window is full of messy adapter wrappers and workaround code.
- The agent treats this glue code as normal and begins defending it, proposing more defensive null-checks and nested retries to patch the hybrid mess (see [[AI, Averaged Decisions, and Premature Convergence on Solutions]]).
- The agent will never independently suggest tearing down the adapter layer.

Escaping the Frankenstein trap requires **human architectural leadership**:
- The human engineer must recognize that the intermediate hybrid is a dead end.
- The engineer mandates a **clean break**: remove the intermediate adapters and commit fully to the new, clean architecture.
- Once the goal is clear, the agent's generative speed can be used to implement the clean architecture in days, rendering weeks of intermediate patching obsolete.

---

## 6. Atomic Commit Discipline for Refactoring

When agents refactor code, they tend to bundle formatting, renaming, structural extraction, and bug fixes into a single massive commit. This makes meaningful code review impossible.

A disciplined refactoring pull request should be broken into distinct, single-purpose commits:

```text
Commit 1: test: add characterization tests for pricing calculation
Commit 2: refactor: rename legacy variables and move calculation files
Commit 3: refactor: extract pure discount calculation from database service
Commit 4: refactor: introduce strongly typed PricingRequest and PricingResult
Commit 5: feat: add tiered discount rule for enterprise customers
Commit 6: chore: delete obsolete legacy pricing procedures
```

### Commit Discipline Rules
1. **One purpose per commit**: Never mix mechanical refactoring with business logic changes.
2. **Every commit must be green**: Each commit must compile and pass all tests independently.
3. **Immutable test assertions during refactoring**: During behavior-preserving steps, never alter expected test values to make a failing test pass.
4. **Reject trial-and-error commit logs**: Commits like "fix compile", "fix test", and "cleanup" describe the agent's internal struggle, not the evolution of the software. Squash or structure them before merging.

---

## Related Notes

- **[[Testing in the Model, Agent, LLM Era]]**: The foundational verification hub explaining the Frozen Oracle Rule and why characterization tests are critical during refactoring.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: Why unconstrained code generation without disciplined boundaries accelerates legacy decay.
- **[[AI Changes the Economics of Technical Debt]]**: How reducing the generative cost of rewrites alters the ROI of modernizing legacy systems.
- **[[Negative Knowledge and Explicit Architectural Dissents]]**: How capturing explicit architectural rejections prevents agents from reintroducing flawed legacy patterns.
- **[[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]]**: Deciding when to patch legacy components versus when to tear them down and regenerate.
- **[[Designing Software for AI Agents]]**: Target architectural patterns (focused files, explicit boundaries) that make modernized systems easy for agents to maintain.
- **[[Developer Satisfaction, Identity, and Burnout in the Age of Coding Agents]]**: How automated refactoring transforms developer morale from learned helplessness to active stewardship.
- **[[AI, Averaged Decisions, and Premature Convergence on Solutions]]**: Why agents exhibit status-quo anchoring bias and defend flawed intermediate architectures.
- **[[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]]**: How runtime observers and telemetry monitor shadow services during live migrations.
- **[[Formal Verification and Runtime Safety Boundaries]]**: Why formal tests cannot prove the absence of unstated side effects, establishing the necessity of differential shadow mirroring.
