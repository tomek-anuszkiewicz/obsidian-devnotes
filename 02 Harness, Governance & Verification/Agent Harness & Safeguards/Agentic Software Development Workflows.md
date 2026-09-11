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
> **The Sovereign Question**: The central question of agentic software engineering is no longer *"How capable is the model at writing syntax?"* It has become: **"How robust is the development system around the model?"** A mediocre model inside a harness with frozen living specs, deterministic test oracles, hard permission gates, and adversarial review produces vastly superior, defect-free production software than a frontier model running unconstrained in a loose prompt loop.

```text
EVOLUTION OF AGENTIC ENGINEERING MATURITY:
AI writes code snippets ──► AI implements features ──► AI executes engineering tasks ──► AI follows rigorous harnesses
                                                                                                    │
                                                                                                    ▼
                                                        CONTINUOUS SOFTWARE SYSTEM COLLABORATION
```

---

## Executive Summary & Core Architectural Invariants

1. **Workflow as the Decisive Differentiator**: The identical frontier LLM can act as a careless code generator, a disciplined TDD practitioner, a cautious refactoring engine, or an adversarial reviewer solely based on the workflow state machine that governs its execution loop.
2. **The Progression of Workflow Granularity**:
   - *Tier 1: Vibe Coding (Prompt $\rightarrow$ Output)*: Rapid, unconstrained prototyping suitable only for disposable exploratory spikes; dangerous for production due to unstated assumptions.
   - *Tier 2: Feature-by-Feature (Vertical Slices)*: Small, bounded changes isolated to single operational commands with deterministic validation.
   - *Tier 3: Plan-Execute-Review (State-Machine Gating)*: Mandatory human audit of behavioral plans before implementation files are modified.
   - *Tier 4: Agent TDD (Frozen Oracle Verification)*: Tests and decision tables generated, reviewed, and frozen before implementation code is synthesized.
   - *Tier 5: Autonomous Multi-Agent Workflows*: Specialized personas (router, implementer, tester, reviewer, synthesizer) executing coordinated tasks under deterministic CI/CD gates.
3. **Environment Over Model**: Generative speed without empirical feedback produces exponential technical debt. The engineering team's primary role shifts from writing manual syntax to **designing the contracts, execution environments, test oracles, and feedback loops** within which agents operate.

---

## 1. The Spectrum of Agentic Workflows

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
- **Utility**: Excellent for 30-minute disposable proof-of-concept spikes, exploring unfamiliar libraries, and rapid prototyping (see [[How AI Changes Prototyping and the Path from PoC to Production]]).
- **Failure Mode**: The model silently invents business logic and edge-case behaviors. In complex stateful systems (e.g. execution kernels, dispatch loops, financial ledgers), vibe coding collapses almost immediately because prompt-and-pray cannot enforce state machine invariants (see [[In-Flight Documentation as the Primary Framework for Coding Agents]]). In enterprise environments, it triggers the "Permanent Prototype V1" trap.

### 2. Feature-by-Feature (Bounded Vertical Slices)
- **Loop**: `Feature Spec → 1:1 Implementation → Targeted Tests → Atomic PR`
- **Utility**: Keeps context small and bounded; isolates changes to single operational files; prevents cross-subsystem blast radius.

### 3. Plan-and-Approve (Human Architectural Gating)
- **Loop**: `Repository Analysis → Living Plan Spec → Human Gate → Scaffolding → Verification`
- **Utility**: Essential for complex refactoring or legacy modernization. The agent is strictly locked in read-only mode during the planning phase; it cannot edit code until the human signs off on the proposed state machine transitions.

### 4. Agent TDD (Specification-First Invariants)
- **Loop**: `Requirements → Decision Tables → Acceptance Tests → Freeze Oracle → Synthesize Code`
- **Utility**: Highest-assurance workflow for mission-critical domain logic. The agent is forbidden from touching the tests once approved, ensuring it cannot negotiate success criteria (see [[Developing Features with AI Coding Agents]]).

---

## 2. Designing the System Around the Model

Modern software development requires treating the agent as one component within a multi-tiered quality architecture:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        THE SECURE WORKFLOW CHASSIS                     │
├────────────────────────────────────────────────────────────────────────┤
│ 1. TASK DEFINITION: Markdown specification with explicit non-goals     │
│ 2. RECONNAISSANCE: AST path-slicing without write permissions          │
│ 3. TEST ANCHORING: Executable oracles and decision truth tables         │
│ 4. SYNTHESIS: 1:1 module code generation (respecting line limits)      │
│ 5. VERIFICATION: Native compiler, linter, and unit test execution     │
│ 6. ADVERSARIAL AUDIT: Independent read-only reviewer agent checks diff │
│ 7. ATOMIC COMMIT: Clean commit history explaining architectural rationale│
└────────────────────────────────────────────────────────────────────────┘
```

The system succeeds not because the model is infallible, but because the **workflow renders failure modes immediately detectable and mechanically reversible**.

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
