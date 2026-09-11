---
title: What Should Organizations Preserve from AI-Assisted Development
tags:
  - knowledge-management
  - software-engineering
  - documentation
  - decision-records
  - institutional-memory
  - traceability
aliases:
  - Preserving Decisions in AI Development
  - Artifacts to Keep from Agentic Coding
---

# What Should Organizations Preserve from AI-Assisted Development

> [!IMPORTANT]
> **Executive Summary & Architectural BLUF**:  
> When code generation is free, treating the raw code syntax as the primary asset to preserve is an architectural mistake. Code becomes ephemeral and easily regenerated; what an organization must fiercely preserve is the **upstream intent and downstream verification**: the architectural decision records (ADRs), business invariant specifications, rejected counter-hypotheses, and deterministic test oracles.
> - **The Ephemeral Code Inversion**: Raw code is simply a compiled artifact of intent. If the business decision record and test oracles survive, the code can be deleted and re-synthesized overnight.
> - **Combating Structural Amnesia**: Without explicit capture of *why* an obscure rule was chosen and *what failure modes* were considered, teams suffer catastrophic institutional memory loss when rotating engineers or swapping agent models.

### Comparative Matrix: What to Preserve vs. What to Treat as Disposable

| Artifact Category | Traditional Development Value | Agentic Era Value | Retention & Governance Strategy |
| :--- | :--- | :--- | :--- |
| **Raw Code Syntax & Boilerplate** | High: Considered the primary intellectual property asset. | **Disposable**: Ephemeral implementation detail; easily regenerated. | Refactor, straighten, or delete without hesitation; zero sentimental attachment. |
| **Business Decision Records (BDRs)** | Often neglected; trapped in scattered emails or meetings. | **Paramount (The Crown Jewel)**: The ultimate source of truth for agents. | Version-controlled Markdown co-located with code; updated on every PR. |
| **Architectural Dissents & Dead Ends** | Discarded upon ticket closure; forgotten. | **Extremely High**: Prevents future agents from re-exploring failed branches. | Recorded in `Negative Knowledge and Explicit Architectural Dissents`. |
| **Deterministic Test Oracles** | Moderate: Often secondary to shipping features. | **Non-Negotiable**: The rigid mathematical fence that prevents drift. | Frozen, immutable execution gates; exit code 0 or pull request rejected. |

---

## Documentation Can Become a Process Output

Agents can reduce the cost of maintaining business documentation, helping safeguard [[LLM Agents and Institutional Memory|institutional memory in software teams]].

For each feature, an agent can update:

- domain documentation,
    
- business decision records,
    
- architectural decision records,
    
- decision tables,
    
- comments near unusual rules,
    
- links to tests and implementation,
    
- migration notes,
    
- known limitations.
    

Because [[Why Business Logic Is the Hardest Part of Agentic Coding|business logic is the hardest part of agentic coding]], a useful Business Decision Record structure is:

```markdown
# BDR-XXX: Decision title

## Context
What ambiguity or business problem existed?

## Decision
How should the system behave?

## Examples
What is allowed and rejected?

## Rationale
Why was this behavior selected?

## Consequences
What systems, processes, or data does it affect?

## References
Code, tests (anchoring [[Testing in the Model, Agent, LLM Era|deterministic test oracles]]), tickets, and previous decisions.
```

The human does not need to write everything from a blank page. The human verifies whether the generated record is accurate, integrating it directly into [[In-Flight Documentation as the Primary Framework for Coding Agents|in-flight documentation for coding agents]].

The agent must distinguish between:

- confirmed information,
    
- conclusions inferred from code,
    
- assumptions requiring confirmation.
    

It must not invent plausible business history.

---

## Agent Work Data Becomes Strategic Intellectual Property

The most valuable data is not only the final source code.

A complete development trajectory contains:

```text
task
→ repository analysis
→ proposed plan
→ agent attempts
→ compiler and test failures
→ human review
→ corrections
→ accepted diff
→ production outcome
```

This data reveals:

- how the organization makes decisions,
    
- which solutions are rejected,
    
- what business rules matter,
    
- which implementations survive production,
    
- how experts recognize subtle errors.
    

Organizations should treat:

- agent logs,
    
- review comments,
    
- accepted and rejected changes,
    
- business specifications,
    
- test suites,
    
- production feedback,
    

as valuable intellectual property rather than disposable telemetry.

### Negative Trajectories and Rejection Logs as High-Value Training Data

When organizations consider fine-tuning internal coding models or context-grounding their agents, they instinctively gather **successful outcomes**: merged pull requests, clean source code, and passing test suites.

This is a fundamental sampling error. **Clean code presents only the destination, completely erasing the minefield navigated to reach it.**

The most defensible organizational IP lies in **Negative Trajectories (Via Negativa)**:
1. **Rejected Implementation Attempts**: The alternative architectures the agent generated that failed compiler checks, violated latency constraints, or deadlocked under load.
2. **Human PR Rejection Rationales**: The exact review comments where senior human engineers rejected an agent's syntactically valid code because it violated unspoken business invariants, introduced operational debt, or ignored hardware cache locality.
3. **Debug Trajectories and Heisenbug Retries**: The step-by-step reasoning steps where an agent wrestled with distributed race conditions before finding the minimal, correct fix.

As explored in [[Negative Knowledge and Explicit Architectural Dissents]], training on positive outputs alone creates brittle, hallucinatory agents that repeatedly wander into known corporate traps. Incorporating negative trajectories transforms corporate memory from a naive repository of code into a **defensive epistemic firewall**.

---

## Training on Model-Generated Code Requires External Verification

As more code is generated by models, future systems will increasingly encounter model-produced code in their training material.

Blindly learning from synthetic output risks:

- repeating common mistakes,
    
- reducing solution diversity,
    
- losing unusual but valuable patterns,
    
- converging on the same fashionable architecture.
    

Model-generated code becomes more valuable when validated through:

- compilation,
    
- tests,
    
- mutation testing,
    
- benchmarks,
    
- static analysis,
    
- human review,
    
- production behavior,
    
- later maintenance history.
    

The valuable training object is not simply generated code.

It is:

> generated proposal + external evidence about whether it was good.

---

## Practical Working Rules

### For documentation

- Keep domain decisions close to the code.
    
- Generate BDR and ADR drafts as part of the change.
    
- Link decisions, tests, code, and tickets.
    
- Distinguish confirmed facts from inferred assumptions.
    
- Update documentation in the same diff as behavior.

---

## Relationship to the Knowledge Graph

- **[[LLM Agents and Institutional Memory]]**: Explores how organizational memory, architectural decisions, and rejected approaches become high-value context for future models.
- **[[The Most Valuable Software Training Data May Be Private]]**: Details why private corporate execution traces and verified trajectories are more valuable than public web data.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: How execution logs, mutation scores, and verification gates prevent autophagous model collapse.
- **[[AI-Generated Architectural Documentation from Code]]**: Concrete patterns for maintaining living architectural decision records (ADRs) alongside code changes.
- **[[Early AI Adoption as Organizational Readiness]]**: Why capturing internal decision processes early builds long-term capability moats.
- **[[Negative Knowledge and Explicit Architectural Dissents]]**: How negative decision trajectories and explicit dissents form the most defensible organizational training data.
