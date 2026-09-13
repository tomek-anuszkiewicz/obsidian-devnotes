---
title: Agentic Software Development Workflows
tags:
  - ai-agents
  - agentic-workflows
  - software-engineering
  - developer-experience
  - automation
  - workflow
aliases:
  - Coding Agent Workflows
  - Granularity of Agent Work
  - Agentic Development Lifecycles
  - From Code Assistant to Engineering Agent
  - The System Around the Model
---

# Agentic Software Development Workflows

> [!IMPORTANT]
> **The Sovereign Question**: The central question of agentic software engineering is no longer *"How capable is the model at generating syntax?"* It has become: **"How robust is the development system around the model?"** A mediocre model inside an execution harness with frozen living specifications, deterministic test oracles, hard permission gates, and adversarial review produces vastly superior, defect-free software than a frontier model running unconstrained in a loose prompt loop.

```text
EVOLUTION OF AGENTIC ENGINEERING MATURITY:
AI writes code snippets ──► AI implements features ──► AI executes engineering tasks ──► AI follows rigorous harnesses
                                                                                                     │
                                                                                                     ▼
                                                         CONTINUOUS SOFTWARE SYSTEM COLLABORATION
```

---

## Executive Summary & Core Architectural Invariants

1. **Workflow as the Decisive Differentiator**: The identical foundation model can act as a careless code generator, a disciplined TDD practitioner, a cautious refactoring engine, or an adversarial reviewer solely based on the workflow state machine that governs its execution loop.
2. **The Progression of Workflow Granularity**:
   - *Tier 1: Vibe Coding (Prompt $\rightarrow$ Output)*: Rapid, unconstrained prototyping suitable only for disposable exploratory spikes; dangerous for production due to unstated assumptions.
   - *Tier 2: Feature-by-Feature (Vertical Slices)*: Small, bounded changes isolated to single operational commands with deterministic validation.
   - *Tier 3: Plan-Execute-Review (State-Machine Gating)*: Mandatory human audit of behavioral plans before implementation files are modified.
   - *Tier 4: Agent TDD (Frozen Oracle Verification)*: Tests and decision tables generated, reviewed, and frozen before implementation code is synthesized.
   - *Tier 5: Autonomous Multi-Agent Workflows*: Specialized personas (router, implementer, tester, reviewer, synthesizer) executing coordinated tasks under deterministic CI/CD gates.
3. **Complementary Workflow Dimensions**: Workflows are not mutually exclusive. Spec-driven development defines *what* should exist; plan-driven development defines *how* work decomposes; test-driven development turns expectations into *executable checks*; adversarial review provides *independent criticism*.
4. **Environment Over Model**: Generative speed without empirical feedback produces exponential technical debt. The engineering team's primary role shifts from writing manual syntax to **designing the contracts, execution environments, test oracles, and feedback loops** within which agents operate.

---

## 1. Granularity Spectrum of Delegated Work

The unit of work delegated to an agent spans a wide continuum:

```text
Autocomplete ──► Single Function ──► Single Change ──► Feature ──► Issue ──► Pull Request ──► Epic ──► Product Goal
```

As the delegated unit expands from a single function to an entire issue or pull request, the need for explicit architectural scaffolding increases exponentially:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      THE AGENTIC WORKFLOW SPECTRUM                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────┬───────┴───────┬───────────────────────┐
    ▼                       ▼               ▼                       ▼
[ VIBE CODING ]    [ FEATURE SLICES ] [ PLAN-AND-GATE ]     [ AGENT TDD ]
Prompt → Code      Feature → Diff     Plan → Gate → Code    Test → Freeze → Code
"Exploratory"      "Low Context"      "Safe Architecture"   "High Assurance"
```

### 1. Vibe Coding (Rapid Exploratory Probing)
- **Loop**: `Prompt → Direct Code Edit → Run → Ad-hoc Fix`
- **Utility**: Excellent for 30-minute disposable proof-of-concept spikes and library reconnaissance (see [[How AI Changes Prototyping and the Path from PoC to Production|prototyping dynamics]]).
- **Failure Mode**: The model silently invents business logic and edge-case behaviors. In complex stateful systems (e.g. execution kernels, dispatch loops, financial ledgers), prompt-and-pray collapses because it cannot enforce state machine invariants (see [[In-Flight Documentation as the Primary Framework for Coding Agents|in-flight documentation patterns]]). In enterprise settings, it triggers the "Permanent Prototype V1" trap.

### 2. Feature-by-Feature (Bounded Vertical Slices)
- **Loop**: `Feature Spec → 1:1 Implementation → Targeted Tests → Atomic PR`
- **Utility**: Keeps context small and bounded; isolates changes to single operational files; prevents cross-subsystem blast radius.

### 3. Plan-and-Approve (Human Architectural Gating)
- **Loop**: `Repository Analysis → Living Plan Spec → Human Gate → Scaffolding → Verification`
- **Utility**: Essential for complex refactoring or legacy modernization. The agent is strictly locked in read-only mode during the planning phase; it cannot edit code until the human signs off on the proposed state machine transitions.

### 4. Agent TDD (Specification-First Invariants)
- **Loop**: `Requirements → Decision Tables → Acceptance Tests → Freeze Oracle → Synthesize Code`
- **Utility**: Highest-assurance workflow for mission-critical domain logic. The agent is forbidden from touching the tests once approved, ensuring it cannot negotiate success criteria (see [[Developing Features with AI Coding Agents|feature development workflows]]).

---

## 2. A Production-Ready Engineering Workflow

In mature production environments, these dimensions compose into a deterministic, multi-stage delivery pipeline:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        THE PRODUCTION AGENT PIPELINE                   │
├────────────────────────────────────────────────────────────────────────┤
│ 1. SPECIFICATION: Markdown requirements with explicit non-goals        │
│ 2. RECONNAISSANCE: AST path-slicing and repository exploration         │
│ 3. IMPLEMENTATION PLAN: Structured blueprint reviewed by human tech lead│
│ 4. ORACLE GENERATION: Acceptance tests and decision truth tables       │
│ 5. SYNTHESIS: Incremental module generation within strict line bounds  │
│ 6. DETERMINISTIC VERIFICATION: Native compiler, linter, and unit tests │
│ 7. ADVERSARIAL AUDIT: Independent read-only reviewer agent checks diff │
│ 8. ATOMIC COMMIT: Clean commit history explaining architectural reason │
└────────────────────────────────────────────────────────────────────────┘
```

The system succeeds not because the model is infallible, but because the **workflow renders failure modes immediately detectable and mechanically reversible**.

---

## 3. Execution Environments vs. Work Organization

A crucial architectural distinction separates *how work is organized* from *where work executes*:

```text
┌────────────────────────┬───────────────────────────────────────────────┐
│ Execution Environment  │ Where the agent runs and what tools it touches│
│                        │ (Coding repo, Document workspace, Cloud VM)   │
├────────────────────────┼───────────────────────────────────────────────┤
│ Work Organization      │ How agent labor is orchestrated               │
│                        │ (Single agent, Parallel fleet, Review team)   │
└────────────────────────┴───────────────────────────────────────────────┘
```

| Execution Environment | Typical Work Unit | Tool Surface |
| :--- | :--- | :--- |
| **Coding Workspace** | Issues, PRs, refactoring slices | Git, compilers, test runners, shell |
| **Knowledge Workspace** | Technical specs, ADRs, post-mortems | Markdown documents, issue trackers, RAG indices |
| **Cloud Background Runner** | Long-running migrations, fuzz testing | Headless CI containers, isolated workers |

Organizations combine these two axes: a coding workspace can be operated by a single developer-driven agent, or handed off to a parallel fleet of specialized workers running overnight migrations.

---

## Relationship to the Knowledge Graph

- **[[Agentic Coding Harness and Controlled Development Workflows]]**: The architectural implementation of controlled plan-and-approval workflows and self-healing loops.
- **[[Developing Features with AI Coding Agents]]**: Tactical guide for vertical-slice implementation and freezing business acceptance tests.
- **[[Testing in the Model, Agent, LLM Era]]**: How executable test suites serve as the primary verification environment for agentic workflows.
- **[[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]]**: How review workflows enforce subtle organizational and architectural standards.
- **[[LLMs as a Code Review Team]]**: Multi-agent adversarial review teams that stress-test code before merge.
- **[[How AI Changes Prototyping and the Path from PoC to Production]]**: Explaining when to use unstructured vibe coding (disposable probes) versus rigorous harnesses (production synthesis).
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Generating in-flight markdown blueprints and contracts to prevent vibe coding collapse on stateful systems.
- **[[AI Productivity Is Limited by the Delivery System]]**: Demonstrating that workflow gains collapse without automated CI/CD verification infrastructure.
