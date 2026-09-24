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
---

## Refactoring Legacy Code with Agents

Agents are useful for legacy modernization, but broad instructions are dangerous.

Avoid:

> Rewrite this module using clean architecture.

Prefer small, behavior-preserving steps:

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

## Reconnaissance and Critical Path Slicing

Before touching a single line of legacy code, use the agent to map execution boundaries. The biggest risk in large monoliths is context sprawl—trying to load an entire module into the prompt window leads to token exhaustion and hallucinations.

Instead, use the agent as a path-slicing engine:

- **Trace the active call graph**: Point the agent at a specific entry point (such as an HTTP controller or message queue consumer) and have it trace execution through to database persistence, filtering out dead code and unrelated background workers.
- **Prove irrelevance**: Use the agent to prove what the system does *not* do. Confirm that adjacent services do not mutate the same database records, or identify hardcoded feature flags whose dead execution paths can be safely stripped.
- **Isolate side effects**: Identify every point where the critical path touches external state—raw SQL queries, ambient singletons, filesystem writes, or third-party APIs. These boundaries become the seam for mock injection during characterization testing.

---

## Differential Shadow Traffic Mirroring

Historical unit tests and synthetic replays are necessary, but they rarely capture the full chaos of production. Subtle edge cases—such as unexpected header formats, null bytes in payloads, or implicit database collation quirks—often escape local testing suites.

For mission-critical paths, deploy the refactored code alongside the legacy implementation using asynchronous differential shadow mirroring (dark launching):

1. **Duplicate live traffic**: The API gateway or edge proxy duplicates incoming requests. The live request routes to the legacy service to produce the actual user response, while an asynchronous copy hits the modernized service.
2. **Isolate shadow side effects**: The shadow service must point to read-only database replicas or mock sinks. Its responses are never returned to end users.
3. **Run a differential oracle**: An automated comparison worker diffs the legacy response against the shadow response. Any divergence in payload structure, HTTP status codes, error formats, or decimal precision is flagged immediately.
4. **Synthesize regression tests**: Feed detected disparities back to the agent as reproducible failing test cases. The agent patches the modernized implementation until the differential oracle reports zero divergence across millions of production requests.

---

## Avoiding the Frankenstein Intermediate Phase

A major failure mode during incremental modernization is getting stranded in a hybrid architecture. Teams frequently build bi-directional database syncs, dynamic translation adapters, and fallback shims to let legacy and modern services coexist.

This transitional glue code is often more fragile and harder to debug than the original legacy system. Coding agents can inadvertently worsen this trap:

- The context window fills up with adapter shims, defensive null-checks, and translation boilerplate.
- The model treats temporary compatibility hacks as permanent architectural patterns, generating even more defensive shims on top of them.
- The agent will never suggest tearing down the adapter layer on its own.

Prevent this by establishing strict lifecycles for transitional adapters. Freeze changes to the legacy path, define explicit boundary contracts, and treat compatibility shims as throwaway scaffolding to be deleted the moment differential shadow mirroring confirms parity.

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

A well-structured PR clearly separates mechanical refactoring from changes in business logic:

```text
Commit 1: test: add characterization tests for pricing calculation
Commit 2: refactor: rename legacy variables and move calculation files
Commit 3: refactor: extract pure discount calculation from database service
Commit 4: refactor: introduce strongly typed PricingRequest and PricingResult
Commit 5: feat: add tiered discount rule for enterprise customers
Commit 6: chore: delete obsolete legacy pricing procedures
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
    
- Do not alter expected test values during behavior-preserving refactoring (see [[Testing in the Model, Agent, LLM Era]]).
- Make the commit history explain the evolution of the system.

## Related Notes

- [[AI-Generated Architectural Documentation from Code]] — Extracting semantic architecture and invariants from legacy code before refactoring.
- [[AI Changes the Economics of Technical Debt]] — Assessing the return on investment for automated technical debt reduction.
- [[Correcting AI-Generated Code — Patch, Regenerate, or Change the Specification]] — Determining whether to patch code or respecify upstream intent during modernization.
- [[Testing in the Model, Agent, LLM Era]] — Characterization testing and baseline protection during refactoring.
