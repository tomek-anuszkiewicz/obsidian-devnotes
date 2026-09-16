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

# Internal Shared Packages vs. Agent-Generated Code

## The Core Question: Reusable Implementation vs. Repeatable Instruction

When coding agents can write, test, and refactor code in seconds, spinning up an internal shared library for every repeated snippet is no longer the right default. The traditional instinct to consolidate all common patterns into a binary package needs to be re-evaluated around a practical distinction:

> **Is this a reusable implementation, or is it merely a repeatable instruction?**

- If it is a **repeatable instruction** (such as mapping a domain entity to a public DTO or standardizing an HTTP error response), an agent can generate and maintain explicit, zero-dependency code directly inside the service repository.
- If the organization requires cross-service consistency, **automated conformance test suites** can validate observable runtime behavior in CI without forcing every team onto the same dependency tree.
- If the organization requires one audited, certified implementation that must be patched and verified in a single place, a **shared package or service API** remains the correct architectural choice.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                      THE STRATEGIC TRIAD HEURISTIC                       │
├──────────────────────────────────────────────────────────────────────────┤
│ 1. USE A SHARED PACKAGE:                                                 │
│    When you need ONE CERTIFIED IMPLEMENTATION                            │
│    - Cryptographic routines, security token validation, mTLS drivers.    │
│    - Audited once, distributed as a binary, patched centrally.          │
├──────────────────────────────────────────────────────────────────────────┤
│ 2. USE INSTRUCTIONS & CONFORMANCE TESTS:                                 │
│    When you need ONE UNIFORM STANDARD                                    │
│    - Error envelopes (RFC 7807), logging formats, pagination params.     │
│    - Written locally by agents, verified via black-box tests in CI.      │
├──────────────────────────────────────────────────────────────────────────┤
│ 3. USE A SERVICE API:                                                    │
│    When you need ONE CENTRALLY CONTROLLED LIVE STATE                     │
│    - Billing engines, tax calculation, ledger accounting rules.          │
│    - Updated in real time without coordinated multi-service deployments. │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## The Economic Inversion: Why Cheap Code Redefines Packages

Historically, internal shared packages existed primarily to conserve developer hours:
1. They spared teams from typing out the same boilerplate across dozens of services.
2. They allowed bug fixes in shared logic to be written once rather than copied by hand.
3. They forced disparate teams to adhere to common patterns by inheriting shared classes.

When agents reduce the marginal cost of producing, testing, and updating explicit code to near zero, that economic balance shifts. The justification that *"we must publish a shared library because hand-writing this data mapper across twelve services wastes too much engineering time"* no longer holds up.

At the same time, code generation does not solve security governance, regulatory compliance, or operational blast radius. Letting an LLM generate custom cryptographic primitives or token-parsing routines across thirty separate codebases creates an unmaintainable security risk.

The boundary breaks down cleanly:
- **Agents eliminate packages whose sole purpose was boilerplate reduction.**
- **Agents reinforce packages whose core purpose is providing an audited, certified runtime implementation.**

Every package you introduce imposes a long-term maintenance tax: transitive dependency drift, build-tool lock-in, semantic versioning management, and coordinated upgrade cycles. When code generation is cheap, the operational cost of an unnecessary library often outweighs the effort of maintaining duplicated, decoupled code.

---

## Shared Conventions vs. Certified Implementations

To keep application codebases clean and avoid framework bloat, you need to separate two distinct organizational requirements: shared conventions and certified implementations.

### 1. Shared Conventions (Use Instructions and Tests, Not Binaries)

> *"Every service across the organization should format error responses and validation failures identically."*

Common examples:
- Standard HTTP Problem Details envelopes (RFC 7807).
- Request validation structures and structured logging key names.
- Directory layouts, CQRS handler skeletons, and DTO projection shapes.

For these requirements, shipping an internal binary library is an anti-pattern. Shared utility libraries typically pull in transitives—JSON serializers, logging drivers, web framework bindings—that eventually clash with the host service. When an application team needs to bump a major framework version, they often find themselves blocked waiting for the internal platform library to publish an update.

The better pattern is to distribute **clear markdown specifications, OpenAPI schemas, and an automated conformance test suite**. The agent generates local, explicit, idiomatic code inside the service, and the test suite runs in the CI pipeline to ensure the service adheres to the specification.

### 2. Certified Implementations (Use Shared Packages)

> *"Every service must execute the exact same mathematically verified, audited runtime implementation."*

Common examples:
- Security token validation (verifying JWT signatures, PASETO parsing).
- Low-level network protocol clients, connection poolers, and mTLS handshakes.
- Distributed tracing context injection and extraction (W3C `traceparent` headers).
- Financial arithmetic, compliance calculations, or regulatory tax rules that must run bit-for-bit identical across products.

In this scenario, a shared package provides real value. The priority here is not saving keystrokes; it is ensuring that your security and networking fundamentals are **audited once, tested under load, and patched everywhere via a single dependency bump when a vulnerability emerges**.

---

## Conformance Tests: Verify Behavior, Don't Force Binaries

Instead of forcing twenty microservices to import a base controller or inherit from a corporate framework class just to ensure consistent error handling, publish a **conformance test suite**.

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

Conformance tests must validate external runtime behavior rather than inspecting internal types, class hierarchies, or middleware registrations:

```python
# WRONG: Couples the test directly to an internal package class
def test_resilience_configuration(handler):
    assert isinstance(handler, CompanyStandardRetryHandler)
```

```python
# RIGHT: Asserts observable behavior over the network boundary
async def test_resilience_behavior(test_client):
    response = await test_client.simulate_network_failure(
        target_endpoint="/orders",
        drop_initial_requests=2
    )
    assert response.status_code == 200
    assert response.headers.get("x-retry-count") == "2"
```

This decoupling gives individual services room to maneuver. An agent can generate idiomatic, zero-dependency routing code in Go, Rust, or TypeScript that satisfies the contract completely. If the service team decides to rewrite their internal routing layer, their build will still pass as long as their external HTTP and messaging contracts remain intact.

---

## The 3-Tier Hybrid Architecture

A practical microservices architecture splits responsibilities cleanly across three distinct tiers:

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

### Tier 1: Minimal Certified Runtime Packages
- Distributed via internal package registries (npm, NuGet, PyPI, Artifactory).
- Handles things like cryptographic signatures, authentication token parsing, and raw wire-protocol networking.
- **Rule:** Contains zero domain business logic and stays out of the application's startup wiring or framework initialization.

### Tier 2: Executable Organizational Standards
- Distributed as contract definitions, OpenAPI/Protobuf specifications, linter configs, and executable test suites.
- Executed during the CI validation step to enforce compliance with corporate guidelines.
- **Rule:** Runs entirely out-of-band; introduces no runtime dependencies to the production service container.

### Tier 3: Locally Generated Application Code
- Written and refactored by agents directly inside the service repository.
- Handles DTO mappings, database queries, domain validation, and presentation formatting.
- **Rule:** Keeps its blast radius fully contained within the repository. A logic bug in an agent-generated mapper affects only that service, leaving the rest of the fleet alone.

---

## Decision Checklist Before Creating a Shared Package

Run through these questions before spinning up a new internal repository and package pipeline:

1. **Is the requirement an identical runtime implementation or just a shared convention?**  
   If it is a convention (like error payloads or logging fields), publish a specification and an automated conformance test. Let agents write the local code.
2. **Does the logic change frequently or require immediate global rollouts?**  
   If the logic changes often and you cannot wait for downstream teams to bump dependencies, expose it as a Service API over the network. Do not distribute volatile rules in a binary package.
3. **Does the code contain business logic or domain rules?**  
   Keep domain rules inside the service that owns the data. Extracting business rules into generic shared libraries inevitably causes domain leakage and tight coupling across service boundaries.
4. **Can correctness be verified by black-box behavioral tests?**  
   If you can write a test that sends an input and checks the output over an HTTP or messaging boundary, prefer local code generated by an agent, verified by a CI test suite.
5. **Does the proposed package exist mainly to eliminate boilerplate?**  
   If the goal is simply saving developers from typing boilerplate, skip the package. Let the agent write the explicit code directly in the service.
6. **What is the operational blast radius if an update introduces a subtle bug?**  
   If pushing a buggy patch to a shared package risks taking down forty downstream microservices simultaneously, prefer decoupled, service-local implementations.

---

## Related Notes

- **[[Designing Internal Packages as an Explicit, Composable Framework]]**: Designing clean, composable internal libraries that avoid hijacking application startup.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Providing platform infrastructure components while keeping application code explicit and transparent.
- **[[AI Changes the Economics of Software Libraries]]**: How near-zero generation costs alter the trade-offs between third-party dependencies and local code.
- **[[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]**: Why heavy reflection and magic framework abstractions make code harder for agents to navigate.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: Why localized code duplication can provide a safer operational blast radius than shared package coupling.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: How application architectures adapt when coding agents write and maintain the implementations.
- **[[Testing in the Model, Agent, LLM Era]]**: Using automated conformance test suites as architectural guardrails for agent-generated code.
