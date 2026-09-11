---
title: Designing Internal Packages as an Explicit, Composable Framework
tags:
  - software-architecture
  - package-management
  - framework-design
  - modular-design
  - maintainability
  - ai-agents
  - mechanical-sympathy
aliases:
  - Designing Internal NuGet Packages as an Explicit, Composable Framework
  - Internal NuGet Framework Architecture
  - Explicit Composable NuGet Packages
  - Internal Package Framework Architecture
  - Explicit Composable Packages
  - Designing Internal Shared Libraries
---

# Designing Internal Packages as an Explicit, Composable Framework

## The Core Thesis & The Ownership Inversion

Internal shared libraries and private packages (whether distributed via NuGet, npm, Maven, Cargo, Go modules, or PyPI) inevitably form an organization's corporate application framework. This creates a critical architectural fork between [[Internal Shared Packages vs Agent-Generated Code|shared corporate packages vs localized agent-generated code]].

Shared packages are not inherently problematic. The pathology begins when a framework inverts architectural ownership—**moving from an application that composes modular tools to a framework that owns and configures the application on its behalf**:

```text
HEALTHY MODEL: APPLICATION OWNS COMPOSITION
  Framework Packages ──(provide discrete blocks)──► Consuming Application
                                                            │
                                                     Explicit Assembly,
                                                     Visible Middleware Pipeline,
                                                     Local Operational Policy

UNHEALTHY MODEL: FRAMEWORK OWNS APPLICATION
  Consuming Application ──(delegates control)──► Monolithic Corporate Platform
                                                            │
                                                     Hidden Ambient Registrations,
                                                     Magic Assembly Scanning,
                                                     Opaque Bootstrap Lifecycle
```

### The Defining Mental Model:
> **The framework provides the building blocks. The application explicitly selects, configures, orders, and composes them.**  
> 
> Build a framework that is composed by the application, not a framework that configures the application on its behalf.  
> 
> **The Decision Invariant**: Use a shared package when it makes the system easier to understand, change, and operate. Use local code, living documentation, and conformance tests when the package would hide more than it simplifies.

When [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code|hidden abstractions become expensive in agent-maintained code]], magic shared packages turn into toxic bottlenecks. Coding agents cannot infer ambient framework hooks, assembly scanning, and implicit dependency injection containers without massive token context waste and hallucinated side-effects.

---

## The Strategic Failure Mode: Frameworks That Own the Application

When organizations attempt to enforce enterprise standards, platform teams frequently build a monolithic starter package:

```text
Company.Platform / company-starter-kit / company-core
├── Ambient Logging Provider
├── Auto-registered Metrics Exporters
├── Hardcoded Retry & Timeout Policies
├── Mandatory Base Classes for Controllers/Handlers
├── Database Context Interceptors
└── Magic Bootstrap Extension Methods: app.UseCompanyPlatform()
```

This monolithic model introduces severe architectural rot:
1. **Silently Captures the Bootstrap Lifecycle**: Consuming applications lose control over the initialization order, dependency lifetimes, and runtime execution graph.
2. **Sprawling Transitive Dependency Hell**: Referencing a small utility package silently imports multiple cloud SDKs, heavy serialization engines, specific telemetry exporters, and database drivers.
3. **The "Frozen Package" Pathology**: Because dozens of disparate teams consume the package, changing a single line risks breaking unknown production services. The package becomes organizationally frozen—**created to centralize change, but too terrifying to ever touch**.
4. **Architectural Colonization**: Domain models are forced to inherit from company base classes, mediator interfaces, or proprietary result envelopes, making it impossible to migrate or refactor services independently.

---

## 12 Principles for Explicit, Composable Package Architecture

### 1. Keep Dependency Trees Minimal & Decoupled
A package must depend strictly on what is necessary for its singular, isolated responsibility. Adding an authentication library should never drag in database clients or logging exporters.

```text
ANTIPATTERN (Monolithic Sprawl):
  Company.Platform ──► [Cloud SDKs + Serilog + OpenTelemetry + DB Drivers + JSON Serializers]

PREFERRED (Decoupled Granular Blocks):
  Company.Telemetry.Core           (Zero external dependencies, pure contracts)
  Company.Telemetry.OpenTelemetry  (Provider adapter)
  Company.Telemetry.Exporters.Grpc (Explicit transport integration)
  Company.Authentication.Oidc      (Pure auth protocol handling)
```

Granular dependency graphs guarantee fewer version collisions, faster security patch cycles, lower binary bloat, and trivial package deprecation.

---

### 2. Configuration by Explicit Composition Over Ambient Magic
Consuming applications must compose infrastructure pipelines explicitly line by line.

```text
EXPLICIT APPLICATION COMPOSITION (Readable, Auditable):
  Initialize AppConfig
  services.Add(CompanyLogging(options => options.ServiceName = "Orders"))
  services.Add(OpenTelemetryTracing())
  services.Add(OidcAuthentication(authority: config.AuthUrl))
  services.Add(ProblemDetailsErrorHandling())

  pipeline.Use(TraceCorrelationHeader())
  pipeline.Use(RequestLogging())
  pipeline.Use(Authentication())
  pipeline.Use(Authorization())
  pipeline.Use(DomainRouting())
```

While more verbose than a single opaque call (`services.AddCompanyPlatformDefaults()`), explicit configuration serves as **executable architectural documentation**. An autonomous agent or human reviewer inspecting the entrypoint immediately understands the active middleware, pipeline order, and active providers.

---

### 3. Middleware and Pipeline Ordering Must Be Locally Visible
Pipeline execution order dictates security and transactional integrity. If authentication runs after request parsing, unauthenticated callers can trigger expensive memory allocations or resource exhaustion. 

A package may provide individual middleware blocks, but the application entrypoint must explicitly register them in visual sequence. Never hide execution sequences inside composite extension macros.

---

### 4. Modularity Must Enable Clean Replacement
Every infrastructure package must be replaceable at the application boundary without requiring modifications to domain logic, handlers, or database schemas.

If an application transitions from a legacy proprietary telemetry collector to standard [[OpenTelemetry]] pipelines, only the startup registration layer should change:
- Domain services, commands, and query handlers must remain completely untouched.
- If removing a shared package requires rewriting business rules, the package boundary has leaked.

---

### 5. Prioritize Replaceability Over Endless Configuration Flags
When a package tries to support every edge case by accumulating dozens of configuration toggles, it becomes an unmaintainable state machine:

```text
POOR DESIGN (Configuration Bloat):
  loggingOptions.UseCustomJsonFormatter = true
  loggingOptions.DisableHeaders = false
  loggingOptions.EnableAsyncCloudBuffer = true
  loggingOptions.BypassSamplingForErrors = true
  loggingOptions.LegacySinkFallback = true
```

Instead of a single monolithic module with 30 boolean switches, decompose into composable plug-in components. Replaceability via clean interfaces is infinitely superior to combinatorial configuration matrices.

---

### 6. Avoid the Multi-Consumer Feature Trap
A shared library frequently starts with a sharp, elegant purpose. Soon, disparate teams request conflicting customizations:
- Team A needs AWS SigV4 signing; Team B requires GCP Workload Identity.
- Team C demands Kafka stream integration; Team D uses RabbitMQ.

Platform teams must resist the urge to wedge every consumer request into the shared core. When consumers require fundamentally conflicting mechanics, **the abstraction boundary is wrong**. Keep the shared core lean, spin out specialized adapter modules, or leave consumer-specific logic in local application code.

---

### 7. Narrow Public API Surfaces
Expose the absolute minimum number of public types, constructors, and interfaces.
- Keep helper utilities, serialization details, and internal state machines private or package-internal.
- A tiny public surface minimizes semantic coupling, simplifies semantic versioning, eliminates accidental misuse, and makes AI agent reasoning trivial.

---

### 8. Insulate Domain Logic from Infrastructure Package Types
Shared packages must never invade the domain layer:
- Domain aggregates must never implement proprietary corporate package interfaces.
- Handlers must not inherit from platform base classes.
- Operations should return standard domain results or standard language types, not proprietary corporate wrapper envelopes (`CompanyResult<T>`).

---

### 9. Separate Core Contracts, Implementations, and Test Doubles
Decompose large operational domains into distinct structural tiers:
1. **Abstractions / Contracts**: Pure interfaces and value models with zero heavy third-party dependencies.
2. **Implementations / Adapters**: Concrete protocol drivers (e.g. gRPC, HTTP, storage engines).
3. **Test Fixtures & Fakes**: In-memory test doubles, mock harnesses, and contract assertions packaged specifically for consumer test suites.

---

### 10. The Conformance Test Alternative (Verify Behavior, Don't Force Binaries)
Organizations often distribute shared binary packages merely to ensure uniform system behavior (e.g. standard error envelopes, correlation header propagation, rate-limit responses).

In an agent-driven ecosystem where [[AI Changes the Economics of Software Libraries|AI changes the economics of software libraries]], **distributing automated conformance test suites is frequently superior to distributing shared binary code**:

```text
┌─────────────────────────────────────────────────────────────┐
│          ORGANIZATIONAL CONFORMANCE TEST SUITE              │
│  - Assert correlation ID header propagated on egress        │
│  - Assert RFC 7807 problem details returned on 400 errors    │
│  - Assert JWT issuer validation matches corporate PKI       │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Validates externally observable behavior)
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │ Local Application Service (Implementation Owned Locally) │
  └─────────────────────────────────────────────────────────┘
```

The enterprise governs contracts and guarantees compliance through rigorous verification oracles, while applications retain complete freedom to tailor implementations without framework lock-in.

---

### 11. Living Documentation and Local Code Over Rigid Shared Packages
For small, infrequently changing patterns (e.g., standard request idempotency checks, specialized hash calculations), maintaining a published corporate package introduces massive overhead (CI/CD pipelines, release notes, version upgrades, security scans).

A documented architectural pattern paired with sample implementations and tests in an internal knowledge base allows coding agents to generate locally owned, zero-dependency code in seconds. Local ownership eliminates version conflicts and gives agents full semantic visibility.

---

### 12. Separate Mechanism from Policy
A package should provide the **mechanism**; the consuming application must explicitly define the **policy**.
- **Mechanism (Inside Package)**: The engine capable of executing exponential backoff, jitter calculation, and socket reconnection.
- **Policy (Inside Application)**: The explicit decision that a specific payment request must never retry, while a read-only catalog query retries up to 3 times with a 500ms timeout.

---

## 15-Point Decision Matrix for Internal Packages

Before publishing or expanding an internal shared package, audit it against these 15 invariant criteria:

| # | Invariant Audit Question | Healthy Answer | Warning Sign |
| :--- | :--- | :--- | :--- |
| **1** | Does the package have one single, unambiguous responsibility? | Yes | "General utilities and helpers" |
| **2** | How many transitive third-party dependencies does it introduce? | Minimal / Zero | 10+ cloud SDKs and serialization engines |
| **3** | Can the application explicitly select every major capability? | Yes | All capabilities forced by default |
| **4** | Is middleware registration and order visible in the application? | Yes | Hidden behind `UsePlatformDefaults()` |
| **5** | Can this package be replaced without touching domain code? | Yes | Domain classes inherit from package types |
| **6** | Are we adding configuration switches to accommodate one team's edge case? | No | Package has 20+ boolean flags |
| **7** | Is the shared abstraction truly universal across all consumers? | Yes | Requires multiple environment-specific conditionals |
| **8** | Is the package easier to maintain than clean, locally owned code? | Yes | Teams avoid upgrading due to breaking changes |
| **9** | Can the package be removed in under a day of focused work? | Yes | Complete rewrite required to decouple |
| **10** | Is the public API surface tightly bounded and encapsulated? | Yes | All internal classes exposed as `public` |
| **11** | Does the package dictate operational policies (timeouts, retries)? | No | Hardcoded retry loops inside the library |
| **12** | Would a conformance test suite achieve compliance more cleanly? | Evaluated | Forcing binary package solely for compliance |
| **13** | Does the package have a clearly designated, active engineering owner? | Yes | Orphaned repository with stale pull requests |
| **14** | Are breaking changes governed by SemVer, changelogs, and deprecation paths? | Yes | Ad-hoc releases that break consumers |
| **15** | Do maintainers feel completely safe releasing updates to production? | Yes | Fear of breaking downstream services |

---

## Related Notes

- [[Internal Shared Packages vs Agent-Generated Code|Internal Shared Packages vs Agent-Generated Code]]: Evaluating binary package dependencies against zero-dependency agent generation.
- [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code|Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]: Why magic frameworks and implicit DI containers impede agent reasoning.
- [[Standardizing Service Infrastructure with Reusable Blocks|Standardizing Service Infrastructure with Reusable Blocks]]: Creating paved-road service platforms without taking over application startup or hiding execution flow.
- [[Designing Software for AI Agents|Designing Software for AI Agents]]: Architectural guidelines favoring explicit composition over ambient framework magic.
- [[AI Changes the Economics of Software Libraries|AI Changes the Economics of Software Libraries]]: How cheap code generation shifts the build-versus-buy trade-off for internal shared libraries.

---

## Relationship to the Knowledge Graph

- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: Structuring software libraries for maximum machine readability and minimal ambient state.
- **[[Data Access Economics with Coding Agents - ORMs vs Explicit SQL]]**: Applying composable modular package principles to data persistence layers.
- **[[Software Entropy and the Zero-Friction Trap]]**: Preventing internal shared frameworks from compounding architectural debt across multi-repo organizations.
- **[[Testing in the Model, Agent, LLM Era]]**: Utilizing automated conformance test oracles to decouple architectural governance from binary package distributions.
