---
title: Correcting AI-Generated Code — Patch, Regenerate, or Change the Specification
tags:
  - ai-agents
  - software-engineering
  - code-review
  - debugging
  - prompt-engineering
  - refactoring
aliases:
  - Patch vs Regenerate vs Respecify
  - Fixing AI-Generated Code
  - The Defect Attribution Hierarchy
  - Architectural Sedimentation
  - Upstream Defect Resolution
  - Bi-Directional Spec-Code Harmonization
  - Harness-Orchestrated Co-Evolution
  - Living Specification Synchronization
---

# Correcting AI-Generated Code — Patch, Regenerate, or Change the Specification

> [!IMPORTANT]
> **The Governing Law of Defect Attribution**: **Fix the lowest layer in the decision hierarchy that actually contains the defect, but no lower.** If the code is wrong, patch the code. If the generation rule is wrong, update the instruction policy. If the architecture is wrong, update the architectural boundary and regenerate. If the business understanding is wrong, update the living specification. Patching code when the upstream specification or architecture is flawed merely embeds undocumented compromises, producing brittle **architectural sediment**.

```text
Decision Level               Defect Type                    Remediation Strategy
──────────────────────────────────────────────────────────────────────────────────
[ SPECIFICATION ]     ──►  Flawed Business Intent     ──►  Update Spec & Regenerate Module
       │
       ▼
[ ARCHITECTURE ]      ──►  Coupling / Boundary Leak   ──►  Update ADR & Regenerate Slice
       │
       ▼
[ POLICY / PROMPT ]   ──►  Recurring Model Bias       ──►  Update Rules / Negative Fences
       │
       ▼
[ IMPLEMENTATION ]    ──►  Localized Syntax / Bug     ──►  Targeted Inline Code Patch
```

---

## Executive Summary & Core Architectural Invariants

1. **The Source of Truth Axiom**: In agentic engineering, implementation code is an ephemeral projection derived from specifications, architectural constraints, instructions, and tests. Manually hacking generated output without updating upstream sources is the modern equivalent of editing generated build artifacts: the next generation loop will overwrite the patch or hallucinate conflicting logic.
2. **The Regeneration Threshold**: The higher a defect sits in the abstraction hierarchy (Business Intent > Architecture > Design > Implementation), the more attractive **full component regeneration** becomes over incremental patching. Repeated patches across paradigm shifts create "architectural sediment"—convoluted code carrying structural remnants of rejected approaches.
3. **Immutable Acceptance Criteria in Repair Loops**: An autonomous self-healing loop must **never** be permitted to modify its own acceptance criteria or test assertions merely to make the CI bar turn green. Agents optimize along the path of least resistance; allowing an agent to relax constraints turns genuine business defects into silently accepted bugs (enforcing [[Testing in the Model, Agent, LLM Era|The Frozen Oracle Rule]]).
4. **The Tripartite Artifact Separation**:
   - **Targets (What)**: Authoritative specifications, acceptance criteria, and frozen test oracles (strictly human-governed).
   - **Policies (How)**: Generation instructions, negative bounds, review checklists, and architectural patterns (continuously tuned via evals).
   - **Outputs (Generated)**: Disposable code, local DTOs, glue pipelines, and build configs (freely regenerated).
5. **Code Review as Specification Discovery**: Generated code functions as an instant, concrete prototype of human requirements. When a human reviewer objects to an agent's implementation, the objection often reveals an unstated business edge case. The human's duty is to update the specification first, rather than dictating tactical code edits.
6. **The Bi-Directional Harmonization Standard**: When correcting code via conversational prompts (*"Here is what's wrong, fix it"*), the engineering harness must not allow specifications to rot. The harness must be configured so that as the agent implements the fix and prepares the commit, it simultaneously resolves which upstream design documents, RFCs, or living specifications govern that slice, back-propagating the necessary specification amendments in lockstep with the code.

---

## 1. The Defect Attribution Matrix

When an agent-generated PR exhibits defects, engineering teams must categorize the failure before initiating repairs:

| Failure Classification | Root Cause | Target Artifact | Action |
| :--- | :--- | :--- | :--- |
| **LOCAL IMPLEMENTATION** | Off-by-one error, inverted boolean, missing null check, inefficient local call | Concrete Source File | Apply targeted inline patch via inner repair loop. |
| **GENERATION POLICY** | Model introduces unwanted abstraction, violates naming convention, uses banned reflection | Repo Instructions / AGENTS.md | Update behavioral rules or add negative bounding proscription; re-run synthesis. |
| **DESIGN / TOPOLOGY** | Inappropriate class coupling, leaky state machine, misplaced handler logic | Module Structure | Redefine module boundaries; regenerate vertical slice. |
| **ARCHITECTURE** | Subsystem bypasses persistence boundary, violates event ordering, ignores transaction scope | Architecture Docs / ADRs | Update architecture invariants, freeze new oracles, regenerate module. |
| **SPECIFICATION** | Unhandled domain state (e.g., partial refund on shipped items), contradictory business rules | Living Markdown Spec | Halt execution, clarify domain requirements with stakeholders, update spec, regenerate. |

---

## 2. Patching vs. Regeneration: The Architectural Sediment Trap

A pervasive anti-pattern in agentic coding is **the patch cascade**:
```text
Agent emits initial implementation A
                 │
                 ▼
Reviewer requests modification ──► Agent patches into hybrid B
                 │
                 ▼
Edge case fails ──► Agent patches into compromise C
```

While version `C` may technically satisfy unit assertions, its internals resemble a geological cross-section of conflicting design choices: redundant defensive checks, abandoned helper functions, and awkward adapter layers left over from versions `A` and `B`.

### The Regeneration Heuristic
- **When to Patch**: The overall structure, boundary separation, and domain model are sound; the defect is isolated to a single function body or local algorithm.
- **When to Regenerate**: The fix requires changing data ownership, introducing a new state-machine phase, or unwinding an inappropriate abstraction. Discarding the implementation and prompting the agent to synthesize clean code from the updated specification takes 90 seconds and produces zero structural cruft.

---

## 3. Case Study: Upstream Architectural Inversion

Consider an agent asked to implement an order status update. It produces:

```text
[ Controller / Transport ] ──► [ Generic Service ] ──► [ Direct ORM / SQL Persistence ]
```

The review team notices that this violates repository clean architecture: the transport layer bypassed application handlers, and business validation is buried inside database helpers.

### Anti-Pattern: Local Code Patching
The developer instructs the agent: *"Wrap the database call in a try/catch and move the discount check into a helper function inside the service."*
- **Result**: The code compiles, but the architectural violation is solidified. Future agents reading this code assume this layering is acceptable and propagate it across ten new endpoints.

### Best Practice: Upstream Policy Correction & Regeneration
1. **Update Architectural Guidance**: Add an explicit negative constraint: *"Transport adapters must not import persistence layers; all commands must dispatch through explicit application handlers."*
2. **Delete & Regenerate**: The agent discards the previous controller and synthesizes:
   ```text
   [ Transport Adapter ] ──► [ UpdateOrderStatusHandler ] ──► [ Domain Entity ] ──► [ Persistence Gateway ]
   ```
3. **Outcome**: The architecture remains pristine, and the new guideline prevents future agents from repeating the defect.

---

## 4. Immutable Intent During Autonomous Repair Loops

When an agent enters an automated test-and-repair loop, the control plane must enforce strict permission boundaries:

```text
                   Autonomous Agent Execution Boundary
┌────────────────────────────────────────────────────────────────────────┐
│ MUTABLE BY AGENT                                                       │
│ - Implementation source files                                          │
│ - Local variable naming and internal algorithms                        │
│ - Generation tactics and temporary scratchpads                         │
├────────────────────────────────────────────────────────────────────────┤
│ STRICTLY IMMUTABLE (READ-ONLY)                                         │
│ - Frozen Test Oracles and behavioral assertion suites                  │
│ - Business specifications and acceptance criteria                      │
│ - Repository architectural boundaries and non-goals                    │
└────────────────────────────────────────────────────────────────────────┘
```

If an agent has write access to test files or requirements, its gradient optimization will inevitably modify the assertions to match its broken implementation. True self-healing requires that the **target remains absolute** while only the **projection is mutable**.

---

## 5. Review as Continuous Specification Discovery

In traditional development, discovering a missing requirement during PR review is frustrating because rewriting manual code takes days.

In an agentic workflow, **generated code is a disposable thinking tool**:
- The human architect reads the agent's PR:
  ```text
  // Implementation checks:
  if (order.status == Status.Pending) {
      cancelOrder();
  }
  ```
- The concrete code immediately triggers a domain insight: *"What if the payment was already captured by an asynchronous gateway while the order was pending?"*
- Instead of manually hacking an inline condition, the architect updates the living specification:
  ```markdown
  ### Order Cancellation Invariant
  An order in `Pending` status may only be cancelled if the payment gateway 
  confirms zero captured authorizations. If funds were captured, cancellation 
  must trigger an asynchronous `RefundEscrowTransaction`.
  ```
- The agent ingests the updated specification and regenerates the implementation, complete with the compensating refund workflow and verification tests.

Code review is thus elevated from clerical linting to **active domain modeling**.

---

## 6. The Third Mode: Harness-Orchestrated Co-Evolution & Bi-Directional Spec Harmonization

While the classic dichotomy pits **tactical code patching** against **manual spec-first regeneration**, high-bandwidth frontier workflows introduce an essential **third mode**: **Harness-Orchestrated Co-Evolution**.

### The High-Velocity Tension

In fast-paced development, forcing a human operator to pause, manually navigate the documentation tree, write detailed specification diffs in Markdown, and then invoke a fresh generation loop introduces significant friction. Conversely, giving a quick prompt to patch the code (*"Hey, you handled the timeout incorrectly here; retry twice before throwing"*) risks immediate **specification rot**, rendering documentation obsolete within days.

### The Mechanism of Co-Evolution

Under this third pattern, the human operator directs the agent at high conversational bandwidth:
> *"Hey, you made a mistake in this error path: when the downstream service returns a 429, we cannot drop the message; we must route it to the dead-letter queue after three exponential backoffs. Fix this."*

Rather than performing a blind inline patch or modifying test suites in isolation, the **[[Agentic Coding Harness and Controlled Development Workflows|agentic harness]]** orchestrates a dual-mutation workflow:

```text
               THE HARNESS CO-EVOLUTION & BACK-PROPAGATION LOOP
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. OPERATOR CONVERSATIONAL PROMPT                                           │
│    "You did X wrong in component Y. Fix it and handle edge case Z."         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. HARNESS CONTEXT & TRACEABILITY RESOLUTION                                │
│    - Agent identifies target source files and module boundaries             │
│    - Harness maps code path to governing spec: [docs/specs/order-queue.md]  │
│    - Harness identifies related architectural decision records (ADRs)       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
             ┌─────────────────────────┴─────────────────────────┐
             ▼                                                   ▼
┌───────────────────────────────────────────┐ ┌───────────────────────────────────────────┐
│ 3A. CONCRETE CODE REPAIR                  │ │ 3B. LIVING SPECIFICATION AMENDMENT        │
│ - Implements algorithmic fix              │ │ - Back-propagates new business invariant  │
│ - Adds deterministic regression test      │ │ - Updates state machine / sequence schema │
│ - Maintains clean architectural layers    │ │ - Documents edge-case rationale           │
└─────────────────────┬─────────────────────┘ └─────────────────────┬─────────────────────┘
                      │                                             │
                      └─────────────────────┬───────────────────────┘
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. PRE-FLIGHT VERIFICATION & HARMONIZATION GATE                             │
│    - Runs automated test suite (verifying zero regressions)                 │
│    - Validates semantic parity between updated spec and repaired code       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. ATOMIC SYNCHRONIZED COMMIT                                               │
│    - Staged together: code fix + regression tests + specification diff      │
│    - Commit message explains both the code repair and the spec evolution    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Invariants of the Co-Evolution Harness

To prevent the agent from corrupting design documents during automated repairs, the harness enforces three deterministic guardrails:

1. **Explicit Artifact Traceability**: Every production module must maintain a clear linkage to its governing documentation—whether via file-level metadata frontmatter, structured directory mirroring, or [[In-Flight Documentation as the Primary Framework for Coding Agents|in-flight task scoping]]. The harness uses this index to immediately resolve which document must receive the back-propagated change.
2. **Expansion-Only Spec Mutation (No Constraint Erasure)**: An agent is permitted to *expand* the specification with newly discovered requirements, edge cases, and compensating workflows. It is strictly barred from *erasing* existing requirements or weakening security/concurrency invariants to rationalize a sloppy patch.
3. **Paired Atomic Commit Discipline**: The harness automatically binds the code modification, its deterministic regression test, and the specification amendment into a single commit (or a pair of explicitly linked atomic commits). This prevents "documentation debt" from ever separating from production code.

### Comparing the Three Remediation Strategies

| Dimension | Mode 1: Tactical Code Patch | Mode 2: Manual Spec-First Rewrite | Mode 3: Harness Co-Evolution |
| :--- | :--- | :--- | :--- |
| **Operator Friction** | Very Low (single quick prompt) | High (operator manually authors spec diff) | Very Low (conversational prompt directing harness) |
| **Documentation Health** | ❌ Severe Drift (spec becomes stale) | ✅ Pristine (spec precedes code) | ✅ Pristine (harness synchronizes spec automatically) |
| **Architectural Purity** | ❌ High risk of architectural sediment | ✅ High (clean regeneration from spec) | ✅ High (harness checks structural invariants) |
| **Regression Guard** | Often missing or ad-hoc | Re-evaluated against full suite | Dedicated regression test added + spec codified |
| **Best Suited For** | Isolated cosmetic fixes, typos | Foundational structural redesigns | Daily feature refinement, edge-case fixes, bug repairs |

---

## Relationship to the Knowledge Graph

- **[[Developing Features with AI Coding Agents]]**: Principles for keeping specifications immutable during implementation.
- **[[The Conductor Pattern - Cognitive Ergonomics of High-Bandwidth Agentic Engineering]]**: The operator leadership model where conversational directing triggers harness-level dual mutations across code and specifications.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Living specifications as active semantic context that must be continuously updated during repair loops.
- **[[Learning Coding Agents Through Failure-Driven Instructions]]**: Codifying correction lessons into repo instructions to prevent recurrent regressions.
- **[[Testing in the Model, Agent, LLM Era]]**: Using deterministic failing tests to anchor agent self-healing loops.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Bounding the correction loop to prevent unbounded retries and hallucination compounding.
- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Distinguishing technical compile failures from deep domain specification defects.
- **[[Refactoring Legacy Systems with AI Agents]]**: Applying the clean refresh and regeneration discipline to legacy modernization.
- **[[Software Entropy and the Zero-Friction Trap]]**: How repeated patching without architectural resets accelerates code entropy.
