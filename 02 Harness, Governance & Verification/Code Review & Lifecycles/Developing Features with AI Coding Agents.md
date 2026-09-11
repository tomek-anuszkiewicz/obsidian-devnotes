---
title: Developing Features with AI Coding Agents
tags:
  - ai-agents
  - software-engineering
  - agentic-workflows
  - feature-development
  - testing
  - code-review
aliases:
  - Feature Development with Agents
  - End-to-End Agentic Feature Lifecycle
  - Vertical Slice Implementation Gate
  - Agent TDD Protocol
  - The Specification-First Feature Loop
---

# Developing Features with AI Coding Agents

> [!IMPORTANT]
> **The Specification-First Feature Lifecycle**: In an agentic engineering harness, feature development must strictly follow an invariant-driven progression: **Analyze $\rightarrow$ Specify $\rightarrow$ Test $\rightarrow$ Human Audit $\rightarrow$ Vertical Slice $\rightarrow$ Full Synthesis**. Permitting an agent to write implementation code before acceptance tests are reviewed and frozen guarantees that the agent will verify what it accidentally implemented rather than what the business required.

```text
Repository Analysis ──► Behavioral Spec & Decision Tables ──► Acceptance Tests Prepared
                                                                          │
                                                                          ▼
Full Feature Expansion ◄── Architectural Review ◄── Vertical Slice ◄── [ HUMAN GATE ]
(Skeptical 2nd Review)     (Verifies topology)      (Thin end-to-end)   (Freezes tests)
```

---

## Executive Summary & Core Architectural Invariants

1. **The Vertical Slice Precondition**: Never instruct an agent to synthesize a 20-file feature in a single pass. Implement one thin, complete vertical slice (from ingress contract down to persistence mutation) first. This tests architectural viability, schema alignment, and dependency injection before bulk code generation begins.
2. **The Frozen Acceptance Gate**: Acceptance tests written from behavioral specifications must be formally approved and frozen (**Read-Only**) before implementation begins. The implementing agent must bend the code to satisfy the oracle—never modify the tests to excuse partial implementations (enforcing [[Testing in the Model, Agent, LLM Era|The Frozen Oracle Rule]]).
3. **Decision Tables Over Prose Prompts**: Natural language requirements are inherently ambiguous. High-leverage specifications express business rules as explicit truth tables and boundary matrices, eliminating model hallucination across permutation edge cases (see [[Why Business Logic Is the Hardest Part of Agentic Coding]]).
4. **Separation of Meaning vs. Machinery**: Tests verify that specific inputs yield specific outputs, but they cannot explain domain intent, historical exceptions, or architectural rationales. High-assurance features require the triad: **Living Specification** (Semantic Why) + **Decision Tables** (Domain What) + **Deterministic Tests** (Empirical Pass/Fail).
5. **Independent Skeptical Audit**: The agent that wrote the feature must not be the sole automated reviewer. An independent, read-only reviewer persona with explicit skeptical prompts audits the completed slice for unmodeled side effects, performance cliffs, and missing negative branches.

---

## 1. The 8-Stage Agentic Feature Pipeline

Within an [[Agentic Coding Harness and Controlled Development Workflows|agentic coding harness]], feature engineering proceeds through eight disciplined state transitions:

```text
[ STAGE 1: REPOSITORY ANALYSIS ]
Agent maps existing call graphs, data schemas, transaction boundaries, and risks without modifying files.
                │
                ▼
[ STAGE 2: BEHAVIORAL SPECIFICATION ]
Author living markdown doc: business goals, domain terminology, invariants, exceptions, and non-goals.
                │
                ▼
[ STAGE 3: TEST HARNESS PREPARATION (AGENT TDD) ]
Agent generates executable unit, contract, and integration tests; tests fail against current codebase.
                │
                ▼
[ STAGE 4: HUMAN GATE (SEMANTIC AUDIT) ]
Human architect audits test meaning: Did agent invent rules? Are negative error paths covered?
                │
                ▼
[ STAGE 5: FROZEN ORACLE LOCK ]
Acceptance suite marked read-only; agent forbidden from editing test assertions.
                │
                ▼
[ STAGE 6: VERTICAL SLICE IMPLEMENTATION ]
Agent synthesizes a single, complete execution path across all layers to validate architecture.
                │
                ▼
[ STAGE 7: HORIZONTAL EXPANSION ]
Agent synthesizes remaining operational branches, handlers, and edge-case permutations.
                │
                ▼
[ STAGE 8: ADVERSARIAL REVIEW & SPEC SYNC ]
Independent reviewer checks diff; living docs updated with new in-flight operational knowledge.
```

---

## 2. Step-by-Step Operational Discipline

### Step 1: Repository Analysis (Read-Only Reconnaissance)
Before proposing changes, the agent must traverse the codebase to locate:
- Existing domain boundaries and transaction scopes,
- Database isolation levels and schema constraints,
- Downstream integration contracts and telemetry standards.
*Constraint*: Zero file modifications permitted during reconnaissance.

### Step 2: Behavioral Specification & Decision Tables
The specification must anchor domain reality before code generation:
```text
Inputs                Condition                    Expected Output               Side Effects
────────────────────────────────────────────────────────────────────────────────────────────────
Order Status: Pending Payment Authorized           Order Status: Confirmed       Emit OrderConfirmedEvent
Order Status: Pending Gateway Timeout              Order Status: PendingRetry    Schedule ExponentialBackoff
Order Status: Shipped Cancellation Requested       HTTP 409 Conflict             AuditLog: IllegalCancel
```

### Step 3 & 4: Tests Before Code & The Human Semantic Audit
The agent authors acceptance tests derived from the decision table. The human review focuses on business intent:
- *Did the agent assume an optimistic path where real-world systems fail?*
- *Are distributed failure modes (timeouts, partial rollbacks) represented?*
- *Does the test assert business outcomes, or merely echo implementation details?*

### Step 5 & 6: The Vertical Slice as Architectural Proof
Instead of generating ten domain models, five controllers, and multiple repository interfaces simultaneously:
- The agent implements **one single transaction** from end to end.
- The team verifies that the data access pattern, serialization pipeline, and error unwinding work smoothly in runtime reality.
- If the architectural pattern proves awkward, unwinding one vertical slice costs minutes, avoiding large-scale refactoring.

---

## 3. Practical Working Rules Checklist

- **Analyze before modifying**: Never allow an agent to edit files without a prior AST reconnaissance phase.
- **Approve the specification before the code**: Ensure domain rules and decision tables are signed off.
- **Freeze approved business tests**: Lock the acceptance suite so the model cannot negotiate assertions.
- **Implement one vertical slice first**: Prove the architectural flow before bulk generation.
- **Separate structural commits from business commits**: Keep refactoring, renames, and new features in distinct atomic git commits.
- **Deploy a skeptical second reviewer**: Use an isolated agent session to challenge assumptions before human sign-off.

---

## Relationship to the Knowledge Graph

- **[[Agentic Software Development Workflows]]**: The overarching methodology of separating specification, planning, implementation, and review.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Hard state-machine gates ensuring only approved vertical slices are implemented.
- **[[Reviewing AI-Generated Code]]**: Checklist and heuristics for skeptical second-party review of agent diffs.
- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Why business conditions require explicit decision tables and isolation from technical glue.
- **[[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]]**: Triaging whether to patch code, adjust prompt rules, or fix the underlying specification.
- **[[Testing in the Model, Agent, LLM Era]]**: The foundational dual-steering architecture pairing soft markdown specs with hard frozen oracles.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Maintaining living specs alongside code during feature evolution.
