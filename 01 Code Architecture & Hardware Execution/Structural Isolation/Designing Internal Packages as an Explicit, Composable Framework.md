---
title: Designing Internal Packages as an Explicit, Composable Framework
tags:
  - software-architecture
  - package-management
  - framework-design
  - modular-design
  - maintainability
  - ai-agents
aliases:
  - Designing Internal Packages as an Explicit Composable Framework
  - Internal Framework Architecture
  - Explicit Composable Packages
  - Designing Internal Shared Libraries
  - The Frozen Package Problem
---

# Designing Internal Packages as an Explicit, Composable Framework

## Core Principle: The Framework Provides Building Blocks; The Application Composes Them

Internal shared libraries and private packages (whether distributed via npm, NuGet, Maven, Cargo, or Go modules) inevitably form an organization's corporate application framework.

Shared packages aren't inherently bad. The pathology starts when a framework inverts architectural control—**moving from an application that composes modular tools to an all-knowing framework that takes over application startup on its behalf**:

```text
HEALTHY MODEL: APPLICATION OWNS COMPOSITION
Framework Packages ──(provide discrete blocks)──► Consuming Application
                                                         │
                                                  Explicit Setup,
                                                  Visible Middleware Pipeline,
                                                  Local Operational Policy

UNHEALTHY MODEL: FRAMEWORK TAKES OVER STARTUP
Consuming Application ──(delegates control)──► Monolithic Corporate Platform
                                                         │
                                                  Hidden Ambient Registrations,
                                                  Magic Reflection Scanning,
                                                  Opaque Bootstrap Lifecycle
```

### The Defining Rule:
> **Build a framework that is composed by the application, not a framework that configures the application on its behalf.**  
> 
> The framework provides building blocks. The application explicitly selects, configures, orders, and wires them together.  
> 
> **The Decision Invariant**: Use a shared package when it makes systems easier to understand, operate, and maintain. Use local code, documentation, and conformance tests when a package would hide more than it simplifies (see [[Internal Shared Packages vs Agent-Generated Code]]).

When building systems with AI coding agents, magic shared packages turn into toxic bottlenecks. Coding agents cannot infer ambient framework hooks, reflection scanning, and implicit dependency injection containers without guessing and hallucinating side effects (see [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]).

---

## The Trap: The All-in-One "Corporate Platform" Package

When organizations try to enforce standards, platform teams often build a monolithic starter package:

```text
company-starter-kit / Company.Platform
├── Ambient Logging Provider
├── Auto-registered Metrics Exporters
├── Hardcoded Retry & Timeout Policies
├── Mandatory Base Classes for Controllers/Handlers
├── Database Context Interceptors
└── Magic Bootstrap Method: app.UseCompanyPlatformDefaults()
```

This pattern creates severe architectural problems:
1. **Hijacked Startup Lifecycle**: The application loses control over initialization order, dependency lifetimes, and execution pipelines.
2. **Dependency Bloat**: Importing a small logging utility silently pulls in three cloud SDKs, heavy serialization libraries, and database drivers.
3. **The "Frozen Package" Problem**: Because 40 different services use the package, changing a single line risks breaking unknown production workflows. The package becomes terrified of changes—**created to centralize updates, but too dangerous to touch**.
4. **Architectural Colonization**: Domain models are forced to inherit from company base classes or proprietary result envelopes, making it impossible to migrate or refactor services independently.

---

## Practical Rules for Composable Internal Packages

### 1. Minimal, Decoupled Dependencies
A package should only depend on what is strictly necessary for its single responsibility. An authentication library should never pull in database drivers or logging exporters:

```text
ANTIPATTERN (Monolithic Sprawl):
  Company.Platform ──► [Cloud SDKs + Logger + OpenTelemetry + DB Drivers + Serializers]

CLEAN COMPOSITION (Granular Blocks):
  Company.Telemetry.Contracts  (Zero external dependencies, pure interfaces)
  Company.Telemetry.Core       (Provider implementation)
  Company.Auth.Oidc            (Pure auth protocol handling)
```

### 2. Explicit Wiring Over Magic One-Liners
Consuming applications should wire up infrastructure pipelines explicitly line by line:

```text
EXPLICIT APPLICATION STARTUP (Clear, Visible, Auditable):
  services.add(logging_provider(service_name: "Orders"))
  services.add(telemetry_tracing())
  services.add(oidc_authentication(authority: config.auth_url))
  services.add(standard_error_handling())

  pipeline.use(trace_correlation_middleware())
  pipeline.use(request_logging_middleware())
  pipeline.use(authentication_middleware())
  pipeline.use(authorization_middleware())
```

While slightly more verbose than `services.add_company_platform_defaults()`, explicit setup serves as **executable architectural documentation**. A developer or coding agent reading this file immediately understands the active middleware and execution order.

### 3. Middleware Order Must Stay Visible in the Application
Pipeline execution order determines security and correctness. If authentication runs after request parsing, unauthenticated callers can trigger expensive memory allocations or denial-of-service vulnerabilities.

A package can supply individual middleware components, but the application entry point must wire them in visual sequence. Never hide execution sequences inside composite extension macros.

### 4. Insulate Domain Logic from Package Types
Shared packages must never invade domain logic:
- Business entities must never implement corporate package interfaces.
- Handlers should not inherit from platform base classes.
- Functions should return standard domain results or standard language types, not proprietary corporate wrappers (`CompanyResult<T>`).

### 5. Separate Mechanism from Policy
A package provides the **mechanism**; the application chooses the **policy**:
- **Mechanism (In Package)**: The utility that executes exponential backoff and jitter calculations.
- **Policy (In Application)**: The explicit configuration stating that payment calls must never retry, while read-only catalog queries retry up to 3 times with a 500ms timeout.

### 6. Ship Conformance Tests Instead of Forcing Shared Binaries
Often, teams distribute shared packages solely to guarantee consistent behavior across services (e.g., standard error envelopes, correlation header propagation, health checks).

In an agent-driven world, **shipping an automated conformance test suite is often far better than forcing everyone to use a shared binary** (see [[AI Changes the Economics of Software Libraries|the economics of software libraries]]):

```text
┌─────────────────────────────────────────────────────────────┐
│          CORPORATE CONFORMANCE TEST SUITE                   │
│  - Verifies correlation ID header is propagated on egress   │
│  - Verifies standard JSON error envelope on 400 errors      │
│  - Verifies health check endpoint returns 200 OK            │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Validates observable behavior)
                               ▼
   [Local Application Code (Implementation Owned Locally)]
```

The organization governs compliance through automated tests, while individual services remain free from rigid framework dependencies and version lock-in.

### 7. Documentation and Copy-Paste Can Beat a Package
For small, rarely changing patterns (like standard idempotency checks or hashing helpers), maintaining a private package introduces massive overhead: CI pipelines, release notes, version upgrades, and security scans.

Documenting the pattern clearly in an internal knowledge base allows an agent or developer to generate clean, locally owned code in seconds. Local ownership eliminates version conflicts and gives agents complete visibility into the code.

---

## 15-Point Decision Checklist Before Building an Internal Package

| # | Audit Question | Healthy Answer | Warning Sign |
| :--- | :--- | :--- | :--- |
| **1** | Does the package have one single responsibility? | Yes | "General utilities and helpers" |
| **2** | How many transitive third-party dependencies does it pull in? | Minimal / Zero | 10+ cloud SDKs and serializers |
| **3** | Can the application explicitly select every major feature? | Yes | Everything forced by default |
| **4** | Is middleware registration and order visible in the app? | Yes | Hidden behind `UseCompanyDefaults()` |
| **5** | Can this package be removed without rewriting domain code? | Yes | Domain entities inherit package types |
| **6** | Are we adding toggles to accommodate one team's special case? | No | Package has 25 boolean switches |
| **7** | Is the shared abstraction genuinely universal? | Yes | Full of environment-specific `if` checks |
| **8** | Is the package easier to maintain than clean local code? | Yes | Teams avoid upgrading due to breaking changes |
| **9** | Can the package be removed in under a day of work? | Yes | Removing it requires a multi-week rewrite |
| **10** | Is the public API surface small and tightly bounded? | Yes | All internal classes marked public |
| **11** | Does the package dictate operational policies (timeouts)? | No | Hardcoded retry loops inside library |
| **12** | Would an automated conformance test achieve compliance better? | Evaluated | Forcing binary package solely for compliance |
| **13** | Does the package have an active, designated team owner? | Yes | Abandoned repo with stale pull requests |
| **14** | Are breaking changes governed by SemVer and deprecation paths? | Yes | Ad-hoc releases that break consumers |
| **15** | Do maintainers feel safe releasing updates to production? | Yes | Fear of breaking downstream services |

---

## Related Notes

- **[[Internal Shared Packages vs Agent-Generated Code]]**: Deciding when to build a shared library versus letting agents generate locally owned boilerplate.
- **[[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]**: Why magic frameworks, implicit reflection, and heavy base classes trip up coding agents.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Creating paved-road infrastructure without hijacking application startup.
- **[[Designing Software for AI Agents]]**: Core architectural patterns favoring explicit composition over ambient framework magic.
- **[[AI Changes the Economics of Software Libraries]]**: How cheap code generation changes the trade-off between shared binary packages and local code.
- **[[OpenTelemetry]]**: Instrumenting distributed tracing and metrics cleanly without proprietary platform wrappers.
- **[[Testing in the Model, Agent, LLM Era]]**: Using automated conformance test suites to verify architectural boundaries without enforcing shared code.
