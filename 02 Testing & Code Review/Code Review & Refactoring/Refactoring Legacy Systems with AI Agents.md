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

Rewriting a legacy system from scratch has historically been one of the fastest ways to burn engineering capital. Big-bang human rewrites regularly ran over schedule, blew past budgets, and introduced regressions by dropping subtle, undocumented edge cases that had been ironed out across years of production. Teams learned to live with fragile monoliths, cautiously applying local patches and hoping nothing critical broke in the background.

Coding agents change the economics of this problem. Using an agent to navigate and endlessly patch tangled legacy code merely defers maintenance and drives up cognitive overhead. However, using agents to methodically extract business rules, backfill characterization tests, and rewrite vertical slices into clean modules is significantly faster and cheaper than living with a legacy codebase. 

The key is treating the agent as a precision extraction tool rather than an autonomous re-architect.

```text
The Maintenance Trap:
Leave legacy spaghetti intact ──► Patch with LLMs ──► Context bloat explodes + regressions multiply

Automated Straightening (Strangler Fig):
Lock behavior with tests ──► Re-synthesize clean modular slices ──► Maintenance costs collapse
```

---

## 1. The Legacy Dilemma: Endless Patching vs. Automated Straightening

When facing a complex legacy codebase burdened with technical debt, engineering leads face a practical choice: use agents to patch the existing spaghetti, or use them to systematically rewrite vertical slices into clean, isolated components.

### Why Patching Legacy Code Fails Long-Term

Patching is tempting because an agent can parse messy code and generate a localized fix in minutes. But relying on this workflow creates serious systemic problems:

1. **Context and Token Overhead**: Spaghetti code rarely respects functional boundaries. Navigating it requires dumping dozens of loosely coupled files into context. As the codebase grows, feeding these large context windows slows down development, drives up costs, and increases the likelihood of model hallucinations.
2. **Hidden Side Effects**: Monolithic legacy code is riddled with ambient global state, implicit execution ordering, and unindexed database queries. A change that looks clean within a narrow prompt context can easily trigger a production outage downstream.
3. **Complexity Masking**: Because an agent can generate a working patch quickly, teams lose the incentive to fix underlying design flaws. The architecture continues to rot beneath automated bandages, deepening technical debt.

### Why Automated Straightening Works

Modern coding agents make structural refactoring economically viable if guided with discipline:

- **Mechanical extraction is cheap**: The tedious work that used to take human teams months—extracting types, isolating database queries, writing DTOs, and splitting monolithic files—can be drafted by an agent in hours.
- **Automated extraction of domain logic**: The agent does not need to guess business requirements. It can inspect production execution traces, database procedures, and unit histories to synthesize comprehensive characterization tests before anyone touches production logic.
- **Incremental replacement (Strangler Fig Pattern)**: You do not perform a high-risk cutover. You slice out a single bounded capability, verify its behavior down to the bit level, route traffic through it, and tear down the legacy path.

---

## 2. Reconnaissance and Critical Path Slicing

The hardest part of modernizing a 100,000-line legacy system is figuring out what the code actually does. Human developers get bogged down trying to understand every nuance before making a move, paralyzed by fear of breaking unseen dependencies.

Agents work exceptionally well as **path-slicing engines**:

1. **Critical Path Tracing**: Given an entry point and an outcome (for example, *"How does an incoming billing payload reach database persistence?"*), an agent can traverse the call graph across files, isolating the active execution path while filtering out irrelevant scaffolding.
2. **Proving Irrelevance**: Often the most valuable step is proving what the system *doesn't* do. An agent can verify that adjacent background workers do not mutate target records, or confirm that an old feature flag is hardcoded to false and its entire code branch can be deleted.
3. **Isolating Scope**: Instead of spending weeks reading through entire modules, the engineer can isolate the core transaction flow in an afternoon, focusing review efforts exclusively on the critical path.

---

## 3. Disciplined Behavioral Extraction

Never give an agent open-ended, sweeping instructions like:

> *"Rewrite this module using clean architecture."*

Vague prompts cause agents to invent abstractions, drop subtle business rules, and hallucinate missing edge cases. Refactoring must proceed through small, verified, behavior-preserving steps:

```text
1. Map Call Graph ──► 2. Add Characterization Tests ──► 3. Rename & Move Code
                                                                 │
7. Parity Verification ◄── 6. Isolate Side Effects ◄── 5. Extract Pure Functions
         │
         ▼
8. Implement New Business Behavior or Delete Dead Code
```

### The Step-by-Step Sequence

1. **Map the current behavior**: Document exact inputs, runtime state, database mutations, and return values.
2. **Add characterization tests**: Characterization tests do not claim that the current behavior is correct. They simply record what the system *currently does*—quirks, bugs, and edge cases included—so that refactoring does not alter behavior accidentally.
3. **Rename and move files only**: Clean up confusing variable names and reorganize file structures without changing a single line of execution logic.
4. **Extract pure functions**: Separate business calculations from database queries, network calls, and message buses.
5. **Introduce explicit types**: Replace untyped dictionaries, dynamic maps, and raw strings with strongly typed domain models.
6. **Isolate external side effects**: Wrap database operations, filesystem access, and API calls behind explicit interfaces or repository boundaries.
7. **Compare old and new outputs**: Run both implementations against historical production data.
8. **Only then introduce new business behavior**: Once the new structure matches the old behavior with zero divergence, you can safely modify business rules or delete obsolete code.

### Verifying Output Parity

For sensitive domains like pricing or financial ledgers, run both implementations side by side against historical data:

```text
old pricing result
vs.
new pricing result
```

During pure refactoring, results must remain identical, down to precision limits and rounding quirks. If the legacy code rounds intermediate calculations to four decimal places, the refactored code must match that behavior exactly until a deliberate business decision is made to change it.

---

## 4. Differential Shadow Traffic Mirroring (Dark Launching)

Synthetic unit and integration tests are necessary, but they rarely capture the full complexity of production environments. Unforeseen null bytes, unexpected header combinations, and race conditions slip past local test suites.

The safest way to replace a mission-critical legacy service is **asynchronous differential shadow mirroring**:

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

1. **The Frozen Facade**: The external API contract, message schemas, and error structures must remain strictly identical. Upstream callers should not know or care that the underlying implementation has changed.
2. **Live Traffic Duplication**: The edge proxy or gateway duplicates incoming live requests asynchronously. The shadow service processes the request against read-only replicas or sandboxed resources, and its output is discarded so real users are unaffected.
3. **Differential Comparison**: An automated oracle compares the legacy response with the shadow response. Any discrepancy in payload fields, status codes, rounding, or error handling is logged alongside the original request payload.
4. **Automated Regression Synthesis**: Each detected discrepancy is automatically turned into an end-to-end test case. The agent analyzes the failure, updates the shadow service to match the legacy behavior, and verifies that existing tests still pass.
5. **Promotion to Production**: Once the shadow service handles millions of mirrored production requests over several days with zero discrepancies, switching primary traffic over is low-risk and straightforward.

---

## 5. Escaping the "Frankenstein Intermediate Phase"

During major refactorings, teams often get stuck in a hybrid state where the legacy engine and the new service are coupled via complex translation layers, bi-directional database syncs, and adapter wrappers.

This intermediate glue code is often more fragile and harder to debug than the original legacy system. When an agent is introduced into this environment, its natural context-following behavior can make things worse:

- The context window is flooded with adapter shims, defensive null-checks, and translation logic.
- The agent treats this glue code as standard domain architecture and continues to build on top of it, adding more retries, fallbacks, and patch layers.
- The agent will not spontaneously recommend tearing down the adapters.

Breaking out of this trap requires deliberate engineering direction:
- Recognize when the intermediate adapter layer has become an architectural dead end.
- Demand a clean break: freeze modifications to the legacy system, define clear service boundaries, and cut over cleanly once parity is proven.
- Use the agent’s speed to build out the target architecture cleanly, rather than spending weeks perfecting temporary bridge code.

---

## 6. Commit Hygiene and Multi-Commit Sequences

Left to themselves, agents tend to bundle formatting, file moves, variable renames, and actual logic changes into a single massive pull request. This makes effective code review impossible.

Instruct the agent to build a clean, reviewable commit sequence:

```text
1. Add characterization tests
2. Rename and move only
3. Extract types without behavior change
4. Extract calculation stages
5. Introduce the explicit domain model
6. Change the business rule
7. Remove obsolete code
```

A well-structured PR clearly separates mechanical refactoring from changes in business logic:

```text
Commit 1: test: add characterization tests for pricing calculation
Commit 2: refactor: rename legacy variables and move calculation files
Commit 3: refactor: extract pure discount calculation from database service
Commit 4: refactor: introduce strongly typed PricingRequest and PricingResult
Commit 5: feat: add tiered discount rule for enterprise customers
Commit 6: chore: delete obsolete legacy pricing procedures
```

Do not accept commit histories like this:

```text
add implementation
fix compilation
fix tests
cleanup
```

Those commits document the agent's internal trial-and-error cycle, not the architectural evolution of the system. Squash or structure them before merging. A reviewer must be able to verify existing behavior, structural adjustments, and deliberate domain changes in isolation.

---

## Practical Working Rules

### For Commits
- **One purpose per commit**: Keep renames, file moves, formatting, structural refactorings, and business logic modifications completely separate.
- **Every commit must be green**: Every intermediate commit must compile cleanly and pass the test suite.
- **Immutable test assertions**: Never modify expected test assertions during behavior-preserving refactoring steps to force a broken build to pass.
- **Explain system evolution**: Ensure the commit log reflects intentional structural changes rather than the agent's troubleshooting steps.

---

## Related Notes

- **[[Testing in the Model, Agent, LLM Era]]**: The foundational verification workflow explaining the Frozen Oracle Rule and why characterization tests are critical during refactoring.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: How unconstrained code generation without disciplined boundaries accelerates technical debt.
- **[[AI Changes the Economics of Technical Debt]]**: How reducing the generative cost of rewrites shifts the trade-offs of modernizing legacy systems.
- **[[Negative Knowledge and Explicit Architectural Dissents]]**: How capturing explicit architectural rejections prevents agents from reintroducing discarded legacy patterns.
- **[[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]]**: Deciding when to patch legacy components versus when to tear them down and regenerate.
- **[[Designing Software for AI Agents]]**: Target architectural patterns (focused files, explicit boundaries) that make modernized systems easy for agents to maintain.
- **[[Developer Satisfaction, Identity, and Burnout in the Age of Coding Agents]]**: How automated refactoring shifts engineering effort from manual maintenance to active system design.
- **[[AI, Averaged Decisions, and Premature Convergence on Solutions]]**: Understanding why agents anchor to existing code patterns and defend messy intermediate architectures.
- **[[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]]**: Implementing runtime observers and telemetry to monitor shadow services during live migrations.
- **[[Formal Verification and Runtime Safety Boundaries]]**: Why formal tests cannot prove the absence of unstated side effects, making differential shadow mirroring necessary.
