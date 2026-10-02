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
  - Small Behavior-Preserving Cleanup with Agents
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

Before changing legacy code, map the relevant execution boundaries. Loading unrelated parts of a monolith can consume context without resolving the dependencies that matter to the task.

Instead, use the agent as a path-slicing engine:

- **Trace the relevant call graph**: Start at an entry point such as an HTTP controller or queue consumer and follow calls, state, and effects. An absent edge in a static graph does not establish that a runtime-registered callback is unused.
- **Investigate apparent irrelevance**: Check whether adjacent services mutate the same records, whether flags vary by deployment, and whether consumers exist outside the repository. Record remaining uncertainty instead of asking the agent to declare unobserved behavior impossible.
- **Isolate side effects**: Identify every point where the critical path touches external state—raw SQL queries, ambient singletons, filesystem writes, or third-party APIs. These boundaries become the seam for mock injection during characterization testing.

---

## Compare Behavior with Replay or Isolated Shadow Execution

Historical unit tests and synthetic replays are necessary, but they rarely capture the full chaos of production. Subtle edge cases—such as unexpected header formats, null bytes in payloads, or implicit database collation quirks—often escape local testing suites.

When inputs and effects can be isolated, a shadow implementation can evaluate captured production requests without serving its output to users:

1. **Capture relevant inputs**: Record the request and the state needed to interpret it. The original implementation remains responsible for the actual response and effects.
2. **Isolate shadow side effects**: Use captured dependencies, controlled sinks, or an isolated state snapshot. A read-only replica alone is insufficient when the operation needs writes or when replica lag changes its inputs. Never execute a payment or other irreversible action twice.
3. **Run a differential oracle**: An automated comparison worker diffs the legacy response against the shadow response. Any divergence in payload structure, HTTP status codes, error formats, or decimal precision is flagged immediately.
4. **Create regression cases**: Turn unexplained differences into reproducible cases. Resolve their cause without changing the accepted baseline merely to make the new implementation pass.

For stateful workflows, replay can compare a sequence of transitions, not just final responses. CodeScene's agent-refactoring experiment used game replays and state comparisons to detect changes. This provides evidence for the exercised sequences, not a proof about every possible input. [CodeScene's case study](https://codescene.com/blog/case-study-refactoring-at-scale-with-agents)

Zero differences across a large sample is encouraging but still bounded by that sample. Separate nondeterminism such as timestamps from meaningful differences, and check errors, rounding, event order, and external effects where they form part of the contract.

---

## Keep Temporary Interop Temporary

A major failure mode during incremental modernization is getting stranded in a hybrid architecture. Teams frequently build bi-directional database syncs, dynamic translation adapters, and fallback shims to let legacy and modern services coexist.

This transitional glue code is often more fragile and harder to debug than the original legacy system. Coding agents can inadvertently worsen this trap:

- The context window fills up with adapter shims, defensive null-checks, and translation boilerplate.
- The model treats temporary compatibility hacks as permanent architectural patterns, generating even more defensive shims on top of them.
- A task focused on the next feature may leave adapter removal outside its scope.

Give each adapter an owner, a boundary contract, and a removal condition. Freeze a component's behavior during its comparison window when practical; if development must continue, record the source revision and recheck intervening changes. Remove the adapter only after its consumers have moved and deployment and rollback needs are resolved.

A mixed implementation can be a legitimate released stage. Decide which side owns state and which calls cross the boundary, rather than assuming both implementations must process every operation. [[Large-Scale Code Migration with AI Agents]] explains this distinction and the published Copilot runtime example.

## Make Local Cleanup Explain the Existing Rule

Readability cleanup is useful before a migration and as ordinary maintenance. For example, this eligibility condition hides the relationship between three rules:

```csharp
if (order.Total >= 100m && customer.IsActive &&
    (customer.IsPremium || order.CreatedAt >= cutoff))
{
    ApplyDiscount(order);
}
```

A local change can name those rules while preserving short-circuit evaluation:

```csharp
const decimal MinimumDiscountTotal = 100m;

bool HasEligibleCustomer() => customer.IsActive &&
    (customer.IsPremium || order.CreatedAt >= cutoff);

if (order.Total >= MinimumDiscountTotal && HasEligibleCustomer())
{
    ApplyDiscount(order);
}
```

The helper is invoked at the same point where the original customer condition ran. Eagerly evaluating all predicates into variables could change behavior if a property getter has effects, throws, or depends on mutable state. Extracting an expression is therefore more than arranging text.

Choose names that expose the domain rule and avoid helpers that merely conceal obvious expressions. Preserve evaluation order, exception behavior, numeric precision, and side effects. Keep a readability patch separate from a new discount policy, even when the agent proposes both together.

## Delete with a Reason, Not Only a Green Test Run

Use different evidence for different deletion claims:

| Claim | Evidence to investigate |
|---|---|
| No supported path reaches this code | References, registration, configuration, reflection, and external consumers |
| The behavior is no longer required | A reviewed retirement decision and affected interfaces |
| Another implementation replaces it | Comparisons covering results, errors, state, and effects |
| It was not observed in production | Observation window and coverage of rare or seasonal paths |

The last row identifies a candidate; it does not establish the first row. Similarly, a group of old steps can be replaced by one expression if their required effects are preserved, but tests alone cannot establish that the suite captured every effect.

After a reviewed deletion, remove the associated wiring and tests that exclusively describe retired behavior. Retain behavioral coverage for supported behavior that moved elsewhere. A failing test during the deletion is evidence to investigate, rather than permission to delete the test.

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
- [[Large-Scale Code Migration with AI Agents]] — Preparing migration boundaries, releasing mixed implementations, and maintaining the resulting port.
