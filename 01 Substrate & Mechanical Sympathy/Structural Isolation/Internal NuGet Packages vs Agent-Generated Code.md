---
title: Internal NuGet Packages vs Agent-Generated Code
tags:
  - dotnet
  - nuget
  - ai-agents
  - code-generation
  - software-architecture
  - maintainability
aliases:
  - Shared Libraries vs Generated Code
  - NuGet vs AI Generation
  - Reusable Implementation vs Repeatable Instruction
  - Internal Packages in the AI Era
---

# Internal NuGet Packages vs Agent-Generated Code

## Core Question & The Fundamental Mental Model

In the era of LLMs and coding agents, does it still make sense to maintain large internal corporate NuGet packages, or should organizations favor [[Designing Internal NuGet Packages as an Explicit, Composable Framework|internal packages designed as explicit composable frameworks]] alongside locally generated code?

Internal NuGet packages should **no longer be the default answer to repeated code**. The foundational architectural question is:

> **"Is this a reusable implementation, or merely a repeatable instruction?"**

- If it is a **repeatable instruction**, an agent can generate and maintain the explicit code locally inside each service.
- If correctness can be described externally, **conformance tests** can validate the implementation deterministically.
- If one exact implementation must be audited, trusted, and maintained centrally, a **package or service API** is still the superior abstraction.

### The Practical Triad

A simple, powerful heuristic governs the boundary:

> 1. **Use a Package** when the organization needs **one implementation** (e.g. cryptography, token validation, telemetry wire formats).  
> 2. **Use Instructions & Conformance Tests** when the organization needs **one standard** (e.g. endpoint structure, validation style, DTO mapping).  
> 3. **Use a Service** when the organization needs **one centrally controlled live behavior** (e.g. shared pricing ledgers, canonical fee calculation, billing state).

---

## Architectural Trade-Off Matrix

Before deciding whether to create a package or prompt an agent, evaluate the core engineering trade-offs:

| Architectural Vector | Shared NuGet Package | Locally Generated Code (Agent 1:1) | Service API (Runtime RPC) | Conformance Test Suite |
| :--- | :--- | :--- | :--- | :--- |
| **Blast Radius Isolation** | Low (Package upgrade regression cascades) | **High** (Zero shared runtime dependencies) | Moderate (Network failures, cascading latency) | **Maximum** (Tests evaluate, never execute in prod) |
| **Initial Implementation Velocity** | Slow (Build pipeline, packaging, release cycles) | **Fast** (Agent synthesizes 1:1 code in seconds) | Moderate (Infrastructure, deployment, routing) | Fast (Author test scenarios once) |
| **Auditability & Compliance** | High (Single audited binary artifact) | Moderate (Must scan all repositories) | **Maximum** (Single live inspection point) | High (Pass/fail gate in every CI pipeline) |
| **Upgrade & Rollout Friction** | High (Multi-repo dependency upgrade PRs) | Moderate/High (Requires agentic batch refactoring) | **Instantaneous** (Single central deployment) | **Low** (Update test package in CI) |
| **Runtime Performance** | **Maximum** (In-process memory call, zero network hop) | **Maximum** (In-process memory call, zero hop) | Lower (Network serialization, socket latency) | N/A (Build/CI time only) |
| **Cross-Language Interop** | Zero (.NET ecosystem only) | Low (Per-language agent generation) | **Maximum** (HTTP/gRPC standard protocol) | High (Generic HTTP/JSON contract runners) |
| **Risk of Hidden Abstraction** | High (Deep extension methods, framework magic) | **Low** (All logic explicit in local service code) | Low (Black-box API contract) | **Zero** (Defines expectations, not internals) |
| **Recommended Domain** | Security tokens, cryptography, OTel exporters | DTO mappers, CRUD handlers, validation rules | Shared ledgers, pricing engines, billing state | API schemas, security policies, latency limits |

---

## The Economic Shift: Why Cheap Code Changes Package Strategy

Internal packages were traditionally created for several core reasons:
1. Code reuse,
2. Consistent implementation across applications,
3. Centralized bug fixes,
4. Shared infrastructure abstractions,
5. Standard project structure,
6. Reduced developer boilerplate typing,
7. Enforcement of organizational conventions.

LLMs fundamentally alter this equation by reducing the mechanical cost of producing code to near zero, illustrating how [[AI Changes the Economics of Software Libraries|AI changes the economics of software libraries]]. This severely weakens the historical argument: *"We must package this because writing it across ten microservices is too tedious."*

However, **agents do not automatically solve organizational coordination, ownership, versioning, or auditing**. Blindly generating unconstrained code across hundreds of repositories quickly triggers [[Software Entropy and the Zero-Friction Trap|software entropy and the zero-friction trap]]. 

Therefore, agents will eliminate packages whose sole purpose was **boilerplate avoidance**, while reinforcing packages whose purpose is to provide a **trusted, auditable runtime implementation**.

---

## Two Distinct Requirements: Convention vs. Runtime Behavior

To avoid building bloated internal frameworks, architects must strictly distinguish between two fundamentally different organizational requirements:

### 1. Shared Coding Convention
> *"Every application should implement a feature in a similar way."*

Examples:
- Endpoint URI and routing structure,
- Validation style and error response format,
- DTO mapping conventions,
- CQRS/Handler directory organization,
- Naming conventions and logging formats,
- Dependency injection registration structure.

For this requirement, **a shared runtime binary package is an anti-pattern**. It introduces unnecessary coupling and version lock-in.

The superior agent-native approach is a combination of:
- Written implementation instructions (living architectural specs),
- Reference implementations,
- Agent instruction prompts,
- Roslyn analyzers and architecture fitness tests (ArchUnit),
- Conformance test suites.

The implementation remains 100% local, explicit, and independently evolvable within each service.

### 2. Shared Runtime Behavior
> *"Every application must execute the exact same trusted, certified implementation."*

Examples:
- Authentication, token validation, and signature verification,
- Cryptographic hashing and key management,
- Internal request signing and mTLS configuration,
- Audit logging pipelines and security telemetry,
- Distributed trace-context propagation (W3C TraceContext headers),
- Critical retry, circuit breaker, and timeout policies,
- Canonical business calculations that legally must remain identical across the enterprise.

In these cases, **an internal NuGet package provides massive real value**. The goal is not avoiding boilerplate; the goal is preserving **one certified implementation, one clear security boundary, and one place where a critical vulnerability can be patched**.

---

## The New Mechanics: Instruction-Driven Generation & Executable Specifications

Instead of shipping a sprawling, opinionated enterprise framework, the platform team provides an **Implementation Contract**:

```text
/engineering-guidelines
  api-endpoints.md
  error-handling.md
  observability.md
  authorization.md

/reference-implementations
  SampleEndpoint
  SampleBackgroundJob
  SampleApiClient

/conformance-tests
  ApiContractTests
  SecurityContractTests
  ObservabilityContractTests
```

An agent can receive an instruction such as:
```text
Implement this endpoint according to engineering-guidelines/api-endpoints.md.
Use reference-implementations/SampleEndpoint only as structural inspiration.
Keep all code local and explicit to this service.
The resulting endpoint must pass the Company.ApiConformanceTests suite.
```

### Executable Specifications Over Ambiguous Prose
Written markdown guidelines alone are insufficient because natural language is inherently underspecified and interpreted probabilistically by LLMs.

Independent **conformance test suites** act as an unambiguous, executable organizational specification:
- Error responses strictly adhere to `RFC 7807 ProblemDetails`,
- Correlation IDs are properly extracted and forwarded in outgoing headers,
- Unauthorized requests return HTTP 401/403 with zero information leakage,
- Sensitive fields (passwords, tokens) are never emitted into log streams,
- Idempotency keys are respected on retried commands.

#### Verifying Behavior, Not Implementation Details
The test suite must verify external behavioral contracts, never internal class hierarchies:

```csharp
// Anti-Pattern: Enforcing rigid class coupling
service.Should().BeOfType<CompanyRetryHandler>();

// Correct: Enforcing behavioral compliance
await AssertRetriesTransientFailureAsync(client, expectedAttempts: 3);
```

The first test forces every application into a shared framework class. The second verifies the required resilience behavior while allowing each application to choose an implementation optimized for its local architecture.

---

## Case Study: Entity Framework as an Example of the Same Shift

Entity Framework (EF Core) illustrates the broader consequence of cheap agent-generated code.

Historically, Object-Relational Mappers (ORMs) were adopted largely because humans hated writing tedious data-access code, mapping `SqlDataReader` columns, and managing parameter collections:

```text
Traditional ORM Pipeline:
LINQ query → Entity Framework → query translation → generated SQL → materialization
```

In the agentic era, an agent does not suffer from typing fatigue. It can generate a specialized SQL query, execute it via raw ADO.NET / Dapper, and map the columns directly into specialized records:

```text
Agent-Generated Data Pipeline:
request → specialized SQL → data reader → explicit 1:1 mapping → response
```

This produces more local code, but it also delivers:
- 100% predictable, tuned SQL without surprise Cartesian explosions or unexpected `N+1` queries,
- Zero unneeded columns or joins,
- Zero hidden change-tracking overhead or memory retention,
- Instant debugger stepping and transparent execution paths.

> **The General Architectural Principle**:  
> When writing code becomes cheap, abstractions must justify themselves by more than the number of lines they eliminate.

Entity Framework remains valuable for complex domain state mutations, transactional units of work, and schema migrations. But for high-throughput reads, reporting queries, or discrete microservice handlers, agents make explicit SQL and generated mapping economically superior.

---

## Comparative Analysis: When to Use Each Approach

### 1. When to Use a NuGet Package
- All consumers use the .NET runtime,
- Logic must execute in-process for maximum microsecond latency,
- High-performance, zero-allocation memory pipelines are required,
- Offline execution is necessary (cannot make network calls to a service),
- The implementation is stable and changes infrequently,
- Audited, single-source security or protocol verification is legally required,
- Updates can be distributed asynchronously through standard package dependency managers.

### 2. When to Use Generated Local Code
- The code is structural, repetitive, or glue logic (DTOs, mappers, CRUD handlers),
- Local service customization is expected or desirable,
- Minor implementation variations across services do not harm system integrity,
- Behavior can be fully certified by an external test suite,
- The code is self-contained and easily understood by any developer or subsequent agent,
- Creating an abstraction would hide critical execution flow or introduce premature complexity.

### 3. When to Use a Service API
- Behavior must be updated centrally with **instantaneous global effect** (zero client redeployments),
- Calling applications span multiple languages and tech stacks (.NET, Node, Python, Go),
- Logic depends on centralized, authoritative transactional state (e.g. inventory ledger, payment gateway),
- Strict auditing, access control, and rate-limiting must be enforced at a single physical gateway,
- The organization cannot tolerate version fragmentation across deployed binaries.

---

## Risks of Each Strategy

### Risks of Internal NuGet Packages
1. **Hidden Complexity ("The Extension Method Trap")**:
   ```csharp
   services.AddCompanyPlatform();
   ```
   A single magical extension method secretly registers dozens of interceptors, policies, background workers, and middleware, making local execution impossible to trace.
2. **Version Fragmentation**: Service A runs v1.2, Service B runs v2.4, and Service C runs v3.1. The organization has the illusion of a shared library, but in production, it runs dozens of incompatible implementations.
3. **Dependency Hell & Lock-in**: Shared packages drag in transitive dependencies (e.g. specific versions of Newtonsoft.Json, Polly, or gRPC) that block consuming services from upgrading their own dependencies.
4. **Accidental Domain Centralization**: Shared libraries become a dumping ground for half-baked business rules that belong inside specific domain services.

### Risks of Local Agent-Generated Code
1. **Multiple Sources of Truth**: 20 services contain 20 copies of similar logic; discovering where a bug lives requires multi-repo scanning.
2. **Uneven Security Patching**: When an algorithm flaw is discovered, an agent must be dispatched to patch and PR all 20 repositories, risking that neglected repositories remain vulnerable.
3. **Local Divergence**: Teams instruct agents to tweak local code over time, gradually drifting away from the original organizational standard.
4. **False Confidence from Conformance Tests**: Tests only validate what they explicitly assert. Generated local code may pass all tests while introducing subtle thread-safety bugs, memory leaks, or unoptimized query patterns.

---

## The Architectural Solution: A 3-Layer Hybrid Model

The most resilient enterprise architecture in the agentic era is a **3-Layer Hybrid Model**:

```text
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: Minimal Shared Runtime (Internal NuGet)            │
│ Core crypto, auth tokens, telemetry wire formats, protocol  │
├─────────────────────────────────────────────────────────────┤
│ LAYER 2: Executable Organizational Standards (Tests & Specs)│
│ Conformance test packages, OpenAPI contracts, Roslyn rules  │
├─────────────────────────────────────────────────────────────┤
│ LAYER 3: Locally Generated Application Code (Agent 1:1)     │
│ Endpoints, DTO projections, specialized queries, validators │
└─────────────────────────────────────────────────────────────┘
```

### Layer 1: Minimal Shared Runtime Packages
- Contains only code that **cannot safely be duplicated**: cryptographic signing, OpenTelemetry exporters, security token validation, proprietary network protocols.
- Zero business logic, zero opinions on controller structure, zero heavy frameworks.

### Layer 2: Executable Organizational Standards
- The organization ships NuGet packages containing **only test fixtures, conformance assertions, and analyzers**:
  ```text
  Company.ApiConformanceTests
  Company.SecurityConformanceTests
  ```
- Consuming applications reference these test packages in their test projects, never in production runtime dependencies.

### Layer 3: Locally Generated Application Code
- Agents author explicit, tailored endpoints, validation rules, and data queries inside each microservice.
- Local code complies with Layer 2 test suites and consumes Layer 1 primitives where certified execution is required.

---

## Architectural Decision Checklist

Before creating or maintaining an internal package, run through these six questions:

1. **Is the requirement an identical implementation or merely a shared convention?**  
   $\rightarrow$ If convention: Use instructions and conformance tests.
2. **Does the logic change frequently or require immediate global rollout?**  
   $\rightarrow$ If yes: Deploy as a Service API, not a package.
3. **Does the code contain proprietary or regulated business calculations?**  
   $\rightarrow$ If yes: Keep in the owning domain service, not a generic package.
4. **Can correctness be validated externally through behavioral assertions?**  
   $\rightarrow$ If yes: Generate local code and enforce with a test suite.
5. **Does the package introduce heavy transitive dependencies or hidden startup magic?**  
   $\rightarrow$ If yes: Refactor into explicit, modular composable blocks or local code.
6. **What is the blast radius if an update introduces a subtle bug?**  
   $\rightarrow$ If package upgrades risk breaking 50 services at once, consider isolated local implementations.

---

## Relationship to the Knowledge Graph

- **[[Designing Internal NuGet Packages as an Explicit, Composable Framework]]**: Principles for designing shared libraries that compose explicitly without framework lock-in.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Reusable platform blocks versus domain-specific application code.
- **[[AI Changes the Economics of Software Libraries]]**: How AI shifts the economics from heavy centralized dependencies to decentralized agent-maintained code.
- **[[Software Entropy and the Zero-Friction Trap]]**: Why localized code duplication can provide cleaner blast-radius isolation than shared package dependencies.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: The shift toward explicit, self-contained implementations maintained by coding agents.
