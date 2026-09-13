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
  - Internal NuGet Packages vs Agent-Generated Code
  - Shared Libraries vs Generated Code
  - NuGet vs AI Generation
  - Reusable Implementation vs Repeatable Instruction
  - Internal Packages in the AI Era
---

# Internal Shared Packages vs Agent-Generated Code

## Core Question & The Fundamental Mental Model

In the era of LLMs and autonomous coding agents, does it still make sense to maintain large internal corporate binary packages (across registries like NuGet, npm, Maven, Cargo, Go modules, or PyPI), or should organizations favor [[Designing Internal Packages as an Explicit, Composable Framework|internal packages designed as explicit composable frameworks]] alongside locally generated code?

Internal shared packages should **no longer be the default reflex for repeated code**. The foundational architectural question is:

> **"Is this a reusable implementation, or merely a repeatable instruction?"**

- If it is a **repeatable instruction**, an agent can generate and maintain explicit, zero-dependency code locally inside each service.
- If correctness can be described externally, **conformance test suites** can validate the implementation deterministically without forcing identical binary packages.
- If one exact, certified implementation must be audited, trusted, and maintained centrally, a **shared package or service API** remains the superior architectural boundary.

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                      THE STRATEGIC TRIAD HEURISTIC                      │
├─────────────────────────────────────────────────────────────────────────┤
│ 1. USE A SHARED PACKAGE:                                                │
│    When the enterprise requires ONE CERTIFIED IMPLEMENTATION             │
│    (e.g., Cryptography, token verification, telemetry wire formats).    │
├─────────────────────────────────────────────────────────────────────────┤
│ 2. USE INSTRUCTIONS & CONFORMANCE TESTS:                                │
│    When the enterprise requires ONE UNIFORM STANDARD                    │
│    (e.g., Endpoint structures, validation styles, DTO projections).     │
├─────────────────────────────────────────────────────────────────────────┤
│ 3. USE A SERVICE API:                                                   │
│    When the enterprise requires ONE CENTRALLY CONTROLLED LIVE STATE      │
│    (e.g., Ledger reconciliation, canonical pricing, billing rules).     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Architectural Trade-Off Matrix

Before deciding whether to publish a shared library or instruct an agent to synthesize local code, evaluate the core engineering vectors:

| Architectural Vector | Shared Binary Package | Locally Generated Code (Agent 1:1) | Service API (Runtime RPC) | Conformance Test Suite |
| :--- | :--- | :--- | :--- | :--- |
| **Blast Radius Isolation** | Low (Regression cascades across consumers) | **High** (Zero shared runtime dependencies) | Moderate (Network failures, cascading latency) | **Maximum** (Tests evaluate; never run in prod) |
| **Implementation Velocity** | Slow (Packaging, pipelines, release semver) | **Fast** (Agent synthesizes 1:1 code in seconds) | Moderate (Deployment pipelines, infrastructure) | Fast (Author test scenarios once) |
| **Auditability & Compliance** | High (Single audited binary artifact) | Moderate (Requires multi-repo search/indexing) | **Maximum** (Single runtime inspection point) | High (Continuous pass/fail CI gate) |
| **Upgrade & Rollout Friction** | High (Multi-repo dependency upgrade PRs) | Moderate/High (Requires automated refactoring) | **Instantaneous** (Single central rollout) | **Low** (Update test runner package in CI) |
| **Runtime Performance** | **Maximum** (Direct in-memory call, zero hop) | **Maximum** (Direct in-memory call, zero hop) | Lower (Network hop, serialization latency) | N/A (Build/CI verification only) |
| **Cross-Language Breadth** | Zero (Locked to single language runtime) | **High** (Agent synthesizes into any target stack) | **Maximum** (Standard JSON/Protobuf/gRPC contracts) | **High** (Universal contract runners) |
| **Risk of Hidden Abstraction**| High (Ambient extensions, container magic) | **Low** (All logic explicit in local service) | Low (Clean black-box interface) | **Zero** (Specifies behavior, not internals) |
| **Recommended Domain** | Cryptography, auth tokens, protocol drivers | DTO mappers, CRUD handlers, validation | Canonical pricing ledgers, billing state | API schemas, security policies, error format |

---

## The Economic Inversion: Why Cheap Code Redefines Package Boundaries

Internal libraries were historically created to solve human labor constraints:
1. Eliminating tedious developer boilerplate typing.
2. Centralizing bug fixes across multiple repositories.
3. Enforcing consistent architectural patterns.
4. Sharing complex infrastructure wiring.

When generative models reduce the marginal cost of producing explicit code to near zero, the economic equation inverts, illustrating how [[AI Changes the Economics of Software Libraries|AI changes the economics of software libraries]]. The historical argument—*"We must publish a shared package because writing this mapper across twelve microservices is too painful"*—completely evaporates.

However, **agents do not automatically solve organizational coordination, ownership, versioning, or security governance**. Blindly scattering unconstrained generated code across hundreds of repositories quickly triggers [[Software Entropy and the Zero-Friction Trap|software entropy and the zero-friction trap]]. 

Therefore, coding agents will eliminate packages whose sole reason for existence was **boilerplate avoidance**, while strengthening packages whose purpose is to provide an **auditable, certified runtime implementation**.

---

## Two Distinct Requirements: Shared Convention vs. Certified Runtime Behavior

To avoid building bloated internal frameworks, software architects must strictly distinguish between two fundamentally different organizational requirements:

### 1. Shared Coding Convention
> *"Every application should structure and implement this capability in a consistent manner."*

Examples:
- Endpoint URI routing and response envelopes,
- Request validation patterns and problem-details formats,
- Data transfer object (DTO) projections,
- CQRS and handler directory organization,
- Logging structure and telemetry attribute tags.

For these requirements, **a shared runtime binary package is an architectural anti-pattern**. It introduces unnecessary binary coupling, transitive dependency version conflicts, and rigid upgrade cycles.

The superior agent-native approach combines:
- Written living architectural guidelines and schemas,
- Minimal reference implementations,
- Precise prompt instructions and linting rules,
- Conformance test suites.

The implementation remains 100% local, explicit, and independently evolvable within each service without cross-repo dependency friction.

### 2. Shared Certified Runtime Behavior
> *"Every application must execute the exact same mathematically verified, certified implementation."*

Examples:
- Security token validation and signature verification,
- Cryptographic hashing, key exchange, and zero-knowledge primitives,
- Internal mTLS and request signing protocols,
- Security audit event streaming pipelines,
- Distributed trace-context propagation (W3C TraceContext headers),
- Regulatory business calculations that must remain bit-for-bit identical across the enterprise.

In these scenarios, **a shared package provides massive real value**. The objective is not avoiding boilerplate typing; the objective is preserving **one certified implementation, one audited security boundary, and one place to patch critical zero-day vulnerabilities**.

---

## The New Paradigm: Instruction-Driven Generation & Executable Specifications

Instead of shipping sprawling, monolithic corporate frameworks, platform teams publish an **Implementation Contract**:

```text
/engineering-contracts
  api-endpoints.spec.md
  error-handling.spec.md
  telemetry-attributes.spec.md
  authorization-rules.spec.md

/reference-patterns
  SampleEndpoint
  SampleBackgroundWorker
  SampleIntegrationClient

/conformance-tests
  ApiContractTests
  SecurityContractTests
  ObservabilityContractTests
```

An agent modifying a service receives an actionable constraint envelope:
```text
Implement this endpoint according to engineering-contracts/api-endpoints.spec.md.
Use reference-patterns/SampleEndpoint as structural inspiration.
Keep all code local, explicit, and zero-dependency within this service.
The resulting endpoint must pass the Organization.ApiConformanceTests suite.
```

### Executable Specifications Over Ambiguous Prose
Natural language documentation is inherently underspecified and subject to stochastic drift across foundation model versions.

Independent **conformance test suites** act as an unambiguous, executable organizational specification:
- Error responses strictly adhere to standard problem details envelopes (RFC 7807).
- Distributed tracing correlation IDs are extracted and forwarded across outbound requests.
- Unauthorized calls return standard 401/403 payloads with zero information leakage.
- Sensitive credentials and tokens are masked from all log streams.
- Idempotency tokens are respected on duplicate commands.

#### Verifying Behavioral Contracts, Not Implementation Classes
Conformance tests must verify external, observable runtime behavior rather than coupled type hierarchies:

```text
// ANTIPATTERN: Enforcing rigid class inheritance
assert(service.implementation_type == "CompanyRetryHandler")

// CORRECT: Enforcing observable behavioral resilience
assert(await test_client.simulate_transient_failure(attempts = 3) == SUCCESS)
```

The first approach forces every microservice into an identical binary inheritance tree. The second guarantees resilience while allowing individual applications to use language-native, hardware-optimized local implementations.

---

## The 3-Tier Hybrid Enterprise Architecture

The most resilient architecture in an agent-augmented engineering organization is a **3-Tier Hybrid Model**:

```text
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: Minimal Certified Runtime Packages (Binary Registries)│
│ Cryptography, token verification, OTel wire formats, drivers│
├─────────────────────────────────────────────────────────────┤
│ TIER 2: Executable Organizational Standards (Tests & Specs) │
│ Conformance test runners, OpenAPI schemas, linter rules     │
├─────────────────────────────────────────────────────────────┤
│ TIER 3: Locally Generated Application Code (Agent 1:1)      │
│ Projections, DTO mappers, specialized queries, validators   │
└─────────────────────────────────────────────────────────────┘
```

### Tier 1: Minimal Certified Runtime Packages
- Contains only code that **cannot safely be duplicated**: cryptographic signing, OpenTelemetry exporters, security token validation, proprietary network protocols.
- Zero business logic, zero opinions on controller structure, zero heavy frameworks.

### Tier 2: Executable Organizational Standards
- Platform teams ship packages or test containers containing **only test fixtures, conformance assertions, and static analyzers**.
- Consuming applications reference these test harnesses in their CI pipelines, never in production runtime dependencies.

### Tier 3: Locally Generated Application Code
- Agents author explicit, tailored endpoints, validation rules, and data queries inside each service.
- Local code complies with Tier 2 test suites and consumes Tier 1 primitives where certified execution is required.

---

## Architectural Decision Checklist

Before creating, expanding, or approving an internal package, audit it against these six questions:

1. **Is the requirement an identical runtime implementation or merely a shared convention?**  
   $\rightarrow$ If convention: Use instructions and conformance tests.
2. **Does the logic change frequently or require immediate global rollout?**  
   $\rightarrow$ If yes: Deploy as a Service API, not a binary package.
3. **Does the code contain proprietary or regulated business calculations?**  
   $\rightarrow$ If yes: Keep in the owning domain service, not a generic package.
4. **Can correctness be validated externally through behavioral assertions?**  
   $\rightarrow$ If yes: Generate local code and enforce with a test suite.
5. **Does the package introduce heavy transitive dependencies or hidden startup magic?**  
   $\rightarrow$ If yes: Refactor into explicit, modular composable blocks or local code.
6. **What is the blast radius if an update introduces a subtle bug?**  
   $\rightarrow$ If package upgrades risk breaking 50 services at once, consider isolated local implementations.

---

## Related Notes

- [[Designing Internal Packages as an Explicit, Composable Framework|Designing Internal Packages as an Explicit, Composable Framework]]: Principles for designing shared libraries that compose explicitly without framework lock-in.
- [[Standardizing Service Infrastructure with Reusable Blocks|Standardizing Service Infrastructure with Reusable Blocks]]: Reusable platform blocks versus domain-specific application code.
- [[AI Changes the Economics of Software Libraries|AI Changes the Economics of Software Libraries]]: How AI shifts the economics from heavy centralized dependencies to decentralized agent-maintained code.
- [[Software Entropy and the Zero-Friction Trap|Software Entropy and the Zero-Friction Trap]]: Why localized code duplication can provide cleaner blast-radius isolation than shared package dependencies.
- [[Software Engineering May Shift Toward Code Optimized for Agents|Software Engineering May Shift Toward Code Optimized for Agents]]: The shift toward explicit, self-contained implementations maintained by coding agents.

---

## Relationship to the Knowledge Graph

- **[[Data Access Economics with Coding Agents - ORMs vs Explicit SQL]]**: Evaluating when data mapping should be generated locally versus managed by shared data libraries.
- **[[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]**: The operational cost of hidden framework magic in shared corporate libraries.
- **[[Testing in the Model, Agent, LLM Era]]**: Using conformance test suites as unambiguous architectural guardrails for coding agents.
- **[[The 5-Layer System Stack for Agentic Software Engineering]]**: Situating shared packages in Layer 1 (Substrate) vs. Layer 2 (Verification Oracles).
