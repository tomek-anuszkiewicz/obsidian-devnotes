---
title: Internal Shared Packages vs Agent-Generated Code
tags:
  - ai-agents
  - code-generation
  - software-architecture
  - maintainability
  - package-management
  - modular-design
aliases:
  - Internal Packages vs Agent-Generated Code
  - Shared Libraries vs Generated Code
  - Reusable Implementation vs Repeatable Instruction
  - Internal Packages in the AI Era
  - The Strategic Triad Heuristic
---

# Internal Shared Packages vs Agent-Generated Code

## Core Question: Reusable Implementation vs. Repeatable Instruction

In the era of AI coding agents, does it still make sense to build and distribute large internal corporate packages, or should teams favor locally generated code?

Internal shared packages should **no longer be the default reflex for repeated code**. When an agent can write, test, and refactor code in seconds, the foundational question changes:

> **"Is this a reusable implementation, or merely a repeatable instruction?"**

- If it is a **repeatable instruction** (like mapping a DTO or formatting an error response), an agent can generate and maintain explicit, zero-dependency code locally inside each service.
- If consistency is required across teams, **automated conformance test suites** can verify observable behavior without forcing identical binary dependencies.
- If one exact, certified implementation must be audited and patched in a single place, a **shared package or service API** remains the right tool.

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                      THE STRATEGIC TRIAD HEURISTIC                      │
├─────────────────────────────────────────────────────────────────────────┤
│ 1. USE A SHARED PACKAGE:                                                │
│    When the organization needs ONE CERTIFIED IMPLEMENTATION             │
│    (e.g., Cryptography, security token verification, mTLS drivers).     │
├─────────────────────────────────────────────────────────────────────────┤
│ 2. USE INSTRUCTIONS & CONFORMANCE TESTS:                                │
│    When the organization needs ONE UNIFORM STANDARD                     │
│    (e.g., Error envelopes, telemetry headers, request validation).      │
├─────────────────────────────────────────────────────────────────────────┤
│ 3. USE A SERVICE API:                                                   │
│    When the organization needs ONE CENTRALLY CONTROLLED LIVE STATE      │
│    (e.g., Canonical billing rules, tax calculations, ledger states).    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## The Economic Inversion: Why Cheap Code Redefines Packages

Historically, internal libraries were created to save human labor:
1. Sparing developers from typing the same boilerplate across 15 microservices,
2. Centralizing bug fixes in a single shared repository,
3. Forcing different teams to write code the same way.

When coding agents reduce the marginal cost of producing explicit code to near zero, that economic equation flips (see [[AI Changes the Economics of Software Libraries|the economics of libraries]]). The traditional justification—*"We must publish a shared package because writing this mapper across twelve services takes too many human hours"*—disappears.

However, agents don't solve security governance, regulatory compliance, or coordination headaches. If you blindly let agents generate security tokens or cryptographic hashing routines in 30 different repos, you create an unmaintainable nightmare.

The boundary is clear:
- **Agents eliminate packages whose primary purpose was boilerplate reduction.**
- **Agents reinforce packages whose primary purpose is a certified, auditable runtime implementation.**

---

## Two Distinct Needs: Shared Conventions vs. Certified Implementations

To keep internal frameworks lean, architects must distinguish between two very different organizational needs:

### 1. Shared Conventions (Use Instructions & Tests, Not Packages)
> *"Every service should structure its API endpoints and validation errors in a consistent way."*

Examples:
- Standard HTTP problem details envelopes (RFC 7807),
- Request validation and logging formats,
- CQRS handler directory structures and DTO projections.

For these needs, **a shared binary library is an anti-pattern**. It creates diamond dependency conflicts, forces coordinated version upgrades across teams, and locks services into a single language or framework.

Instead, ship **clear markdown guidelines, reference examples, and an automated conformance test suite**. The agent generates local, explicit, zero-dependency code inside each service, and CI tests verify compliance.

### 2. Certified Implementations (Use Shared Packages)
> *"Every service must execute the exact same mathematically verified, audited implementation."*

Examples:
- Security token validation and cryptographic signature checking,
- Low-level network protocol drivers and mTLS connections,
- Distributed tracing header injection (W3C TraceContext),
- Regulatory fee calculations that must be bit-for-bit identical across products.

Here, **a shared package provides immense value**. The goal is not saving keystrokes; the goal is having **one audited implementation, one place to run penetration tests, and one package to patch when a zero-day vulnerability appears**.

---

## Conformance Tests: Verify Behavior, Don't Force Binaries

Instead of forcing 20 microservices to inherit from a corporate base class just to ensure they format errors identically, platform teams can publish a **conformance test suite**:

```text
┌─────────────────────────────────────────────────────────────┐
│              CORPORATE CONFORMANCE TEST SUITE               │
│  - Assert correlation ID header is propagated on egress     │
│  - Assert standard JSON error envelope on 400 bad requests  │
│  - Assert unauthorized requests return 401 with no leakage  │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Validates observable behavior)
                               ▼
   [Local Application Code (Implementation Owned Locally)]
```

### Assert Behavior, Not Classes
Never write conformance tests that inspect class names:
```text
// WRONG: Couples the test to a specific corporate class
assert(handler is CompanyStandardRetryHandler)

// RIGHT: Asserts observable behavior
assert(await test_client.simulate_network_failure(attempts: 3) == SUCCESS)
```

This guarantees resilience and standards compliance across the enterprise, while letting individual teams and agents tailor their local code without framework bloat.

---

## The 3-Tier Hybrid Architecture

Modern engineering teams balance shared infrastructure and local code across three distinct tiers:

```text
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: Minimal Certified Runtime Packages (Binary Registries)│
│ Cryptography, token verification, telemetry wire formats    │
├─────────────────────────────────────────────────────────────┤
│ TIER 2: Executable Organizational Standards (Tests & Specs) │
│ Conformance test runners, OpenAPI schemas, linter rules     │
├─────────────────────────────────────────────────────────────┤
│ TIER 3: Locally Generated Application Code (Agent 1:1)      │
│ Projections, DTO mappers, specialized queries, validators   │
└─────────────────────────────────────────────────────────────┘
```

- **Tier 1 (Certified Binaries)**: Code that cannot safely be duplicated. Contains zero business logic and zero opinion on controller layout.
- **Tier 2 (Executable Standards)**: Conformance test fixtures, schemas, and linter configurations that run exclusively in CI pipelines.
- **Tier 3 (Local Code)**: Pure, explicit application logic written by agents. Clean, easy to read, and 100% isolated to the service.

---

## Decision Checklist Before Creating a Shared Package

1. **Is the requirement an identical runtime implementation or just a shared convention?**  
   $\rightarrow$ If convention: Use written guidelines and conformance tests.
2. **Does the logic change frequently or require immediate global rollouts?**  
   $\rightarrow$ If yes: Deploy as a Service API, not a binary package.
3. **Does the code contain business logic or domain rules?**  
   $\rightarrow$ If yes: Keep it in the owning service; don't leak business rules into generic packages.
4. **Can correctness be verified by black-box behavioral tests?**  
   $\rightarrow$ If yes: Generate local code and verify it in CI.
5. **Does the proposed package exist mainly to eliminate boilerplate?**  
   $\rightarrow$ If yes: Let the agent write the explicit code locally (see [[Designing Internal Packages as an Explicit, Composable Framework]]).
6. **What happens when an update introduces a subtle bug?**  
   $\rightarrow$ If upgrading a package risks breaking 40 services at once, prefer isolated local implementations.

---

## Related Notes

- **[[Designing Internal Packages as an Explicit, Composable Framework]]**: Guidelines for designing clean, composable internal packages without taking over application startup.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Providing reusable platform infrastructure while keeping application code transparent.
- **[[AI Changes the Economics of Software Libraries]]**: How near-zero generation costs alter the trade-off between external dependencies and local code.
- **[[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]**: Why magic frameworks and implicit reflection make code harder for agents to navigate.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: Why localized code duplication can provide a safer blast radius than shared package coupling.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: How codebases adapt their structure when machines write and maintain the implementation.
- **[[Testing in the Model, Agent, LLM Era]]**: Using automated conformance test suites as unambiguous architectural guardrails.
