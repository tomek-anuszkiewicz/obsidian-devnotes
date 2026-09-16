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

Every internal shared library you publish—whether through npm, NuGet, Maven, Cargo, or Go modules—inevitably shapes your organization’s de facto corporate application framework. 

Shared code is not inherently problematic. The architectural failure occurs when a platform framework inverts control: moving from an application that composes modular tools to an all-knowing framework that hijacks application startup and hides infrastructure behind ambient magic.

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

### The Defining Rule

**Build a framework that is composed by the application, not a framework that configures the application on its behalf.**

The framework provides building blocks. The application explicitly selects, configures, orders, and wires them together.

**The Decision Invariant**: Build a shared package when it makes systems easier to understand, operate, and maintain. Rely on local code, clear documentation, and automated conformance tests when a package would obscure more than it simplifies (see [[Internal Shared Packages vs Agent-Generated Code]]).

When building systems alongside AI coding agents, magic shared packages become severe engineering bottlenecks. Coding agents cannot reliably navigate ambient framework hooks, reflection-based classpath scanning, or implicit dependency injection containers without guessing and hallucinating side effects (see [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]).

---

## The Trap: The All-in-One "Corporate Platform" Package

When platform teams attempt to standardize architectures across an organization, they frequently fall into the trap of shipping a monolithic starter package:

```text
company-starter-kit / Company.Platform
├── Ambient Logging Provider
├── Auto-registered Metrics Exporters
├── Hardcoded Retry & Timeout Policies
├── Mandatory Base Classes for Controllers/Handlers
├── Database Context Interceptors
└── Magic Bootstrap Method: app.UseCompanyPlatformDefaults()
```

This monolithic model introduces four major failure modes into your runtime and development lifecycle:

### 1. Hijacked Startup Lifecycle
The application surrenders control over initialization order, dependency lifetimes, and execution pipelines. When background workers, health checks, or database connections initialize via hidden hooks, diagnosing boot-time crashes or configuring custom shutdown hooks becomes an exercise in reverse-engineering the framework.

### 2. Dependency Bloat and Diamond Dependency Hell
Importing a shared package just for structured logging or a consistent error model silently pulls in three cloud SDKs, heavy serialization engines, and specific database drivers. When two downstream packages depend on conflicting major versions of a transitive serialization library, consumer builds break across the company.

### 3. The "Frozen Package" Problem
Because dozens of heterogeneous services consume the same platform package, modifying a single class or upgrading an underlying driver risks breaking unknown downstream workflows. The library becomes terrified of change. It was originally introduced to centralize best practices, but it quickly calcifies because it is too critical and dangerous to touch.

### 4. Architectural Colonization
Domain models are forced to inherit from proprietary company base classes, handle platform-specific interfaces, or wrap business outputs in non-standard transport envelopes (`CompanyResult<T>`). This leaks infrastructure concerns into core business logic, preventing services from evolving, refactoring, or migrating independently.

---

## Practical Rules for Composable Internal Packages

### 1. Minimal, Decoupled Dependencies
A shared package must depend strictly on what is necessary to fulfill its single responsibility. An authentication package should handle tokens and cryptographic signatures—it should never pull in database drivers, HTTP servers, or logging exporters.

```text
ANTIPATTERN (Monolithic Sprawl):
  Company.Platform ──► [Cloud SDKs + Logger + OpenTelemetry + DB Drivers + Serializers]

CLEAN COMPOSITION (Granular Blocks):
  Company.Telemetry.Contracts  (Zero external dependencies, pure interfaces)
  Company.Telemetry.Core       (Concrete exporter and tracer implementations)
  Company.Auth.Oidc            (Pure protocol parsing and token validation)
```

Split packages along operational boundaries. Provide lightweight contract packages containing zero runtime dependencies, letting application teams consume interfaces without inheriting heavy vendor SDKs.

### 2. Explicit Wiring Over Magic One-Liners
Consuming applications must wire up infrastructure components line by line inside their entry point. Avoid meta-packages that register everything automatically behind an opaque setup method.

```typescript
// EXPLICIT APPLICATION STARTUP (Clear, Visible, Auditable)
import { createLogger } from "@company/telemetry-logging";
import { registerTracing } from "@company/telemetry-tracing";
import { configureOidcAuth } from "@company/auth-oidc";
import { errorHandlerMiddleware } from "@company/http-errors";

// 1. Explicit Service Registrations
const logger = createLogger({ serviceName: "orders-api", level: config.logLevel });
const tracer = registerTracing({ serviceName: "orders-api", exporterEndpoint: config.otelUrl });
const authProvider = configureOidcAuth({ authority: config.oidcAuthority, audience: "orders-api" });

// 2. Visible Middleware Composition
const app = createHttpServer();

app.use(tracer.correlationMiddleware());
app.use(logger.requestLoggingMiddleware());
app.use(errorHandlerMiddleware());
app.use(authProvider.authenticate());
app.use(authProvider.requireScopes(["orders:read", "orders:write"]));
```

While this approach requires a dozen lines of setup code instead of a single `app.useCompanyDefaults()`, explicit setup acts as **executable architectural documentation**. Any engineer or AI agent reading the entry point can trace precisely what middleware is running, what dependencies exist, and how data moves through the runtime.

### 3. Middleware Order Must Stay Visible in the Application
Execution order in an HTTP or messaging pipeline dictates security, resource usage, and correctness. 

If authentication runs *after* request body parsing, unauthenticated callers can send multi-megabyte payloads that consume server memory and trigger expensive garbage collection pauses before being rejected. If correlation ID extraction runs *after* error logging, unhandled exceptions will drop critical distributed tracing context.

A platform package should supply individual, reusable middleware components. The application entry point must wire them in plain sight. Never hide execution sequences inside monolithic wrapper methods.

### 4. Insulate Domain Logic from Package Types
Shared packages belong at the boundaries of your system (transport, serialization, external integrations). They must never invade core business logic:
- Domain entities must never inherit from internal framework classes.
- Command and query handlers must not extend platform-specific bases.
- Business services should return native language types, standard library errors, or domain models—not internal wrappers like `CompanyResponse<T>`.

When packages stay confined to the infrastructure layer, replacing or upgrading a library requires zero changes to core domain code.

### 5. Separate Mechanism from Policy
A library provides the **mechanism**; the consuming application decides the **policy**:
- **Mechanism (Provided by the Package)**: A utility that computes exponential backoff with full jitter, or an interceptor that tracks HTTP call duration.
- **Policy (Configured by the Application)**: The operational decision that payment processing endpoints must never automatically retry, while catalog read queries retry three times with a 250ms base delay and a strict 1-second timeout.

Hardcoding operational policies inside a library removes control from the engineers operating the service in production. Keep the utilities flexible and leave tuning parameters to local configuration.

### 6. Ship Conformance Tests Instead of Forcing Shared Binaries
Platform teams often distribute shared packages solely to force standardization across downstream systems (for example, standardizing JSON error shapes, propagating tracing headers, or enforcing `/healthz` endpoints).

Distributing shared binaries is not the only way to achieve standard behavior. **Shipping an automated conformance test suite often yields better architectural outcomes than enforcing a shared binary dependency** (see [[AI Changes the Economics of Software Libraries]]):

```text
┌─────────────────────────────────────────────────────────────┐
│          CORPORATE CONFORMANCE TEST SUITE                   │
│  - Verifies correlation ID header is propagated on egress   │
│  - Verifies standard RFC 7807 JSON envelope on 400 errors   │
│  - Verifies health check endpoint returns 200 OK            │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Validates black-box behavior)
                               ▼
   [Local Application Code (Implementation Owned Locally)]
```

With conformance suites, the platform team writes a containerized test harness or executable integration suite that verifies external system behavior over the network. Individual services implement their endpoints using whatever libraries or native language idioms make sense for their stack. The platform team enforces organizational standards without introducing dependency locks or runtime coupling.

### 7. Documentation and Copy-Paste Can Beat a Package
For small, low-churn utilities (such as computing HMAC signatures, generating deterministic idempotency keys, or normalizing headers), maintaining a shared package introduces high lifecycle overhead: separate source repositories, CI pipelines, semantic versioning gates, release notes, and vulnerability patching.

For stable, low-complexity patterns, clear documentation and a reference implementation are superior to a shared package. Engineers and AI coding agents can drop clean, locally owned code directly into the service in seconds. Local ownership avoids dependency conflicts entirely, allows immediate refactoring, and keeps the full implementation visible to automated tooling.

---

## 15-Point Decision Checklist Before Building an Internal Package

Before writing a shared library, run your design through this diagnostic checklist to ensure it stays a modular building block rather than an invasive corporate platform:

| # | Diagnostic Question | Healthy Answer | Warning Sign |
| :--- | :--- | :--- | :--- |
| **1** | Does the package have one single responsibility? | Yes; clear, narrow functional scope. | Marked as "common", "utils", or "platform". |
| **2** | How many transitive third-party dependencies does it pull in? | Minimal or zero dependencies. | Pulls in heavy cloud SDKs, ORMs, and serializers. |
| **3** | Can the application explicitly select every major feature? | Yes; features are opted into individually. | Importing the package forces a standard runtime stack. |
| **4** | Is middleware registration and order visible in the app? | Yes; wired explicitly in the application entry point. | Opaque setup via a single `app.UseDefaults()` call. |
| **5** | Can this package be removed without rewriting domain code? | Yes; isolated entirely to the infrastructure layer. | Business entities inherit from platform base classes. |
| **6** | Are we adding toggles to accommodate one team's special case? | No; unique workflows are handled locally by the service. | Library contains dozens of custom conditional switches. |
| **7** | Is the shared abstraction genuinely universal? | Yes; works identically across domains and environments. | Littered with environment checks and team-specific forks. |
| **8** | Is the package easier to maintain than clean local code? | Yes; solves a legitimately complex, high-churn technical problem. | Teams avoid updating dependencies to avoid breaking changes. |
| **9** | Can the package be removed in under a day of work? | Yes; interfaces are cleanly separated from application code. | Removing the package requires a multi-week service rewrite. |
| **10** | Is the public API surface small and tightly bounded? | Yes; exposes only necessary functions and interfaces. | All classes and internal utilities exposed publicly. |
| **11** | Does the package dictate operational policies? | No; consumers control timeouts, retries, and allocations. | Hardcoded retry loops and unconfigurable timeouts. |
| **12** | Would an automated conformance test achieve compliance better? | Evaluated; package is only built if binary sharing is necessary. | Forcing a shared binary solely to validate wire formats. |
| **13** | Does the package have an active, designated team owner? | Yes; dedicated team maintains, triages, and documents it. | Orphaned repository with pending bug reports. |
| **14** | Are breaking changes governed by SemVer and deprecation paths? | Yes; documented upgrade paths and release cadences. | Unannounced breaking changes across minor versions. |
| **15** | Do maintainers feel safe releasing updates to production? | Yes; comprehensive unit and integration test suites. | Changes delayed out of fear of breaking downstream callers. |

---

## Related Notes

- **[[Internal Shared Packages vs Agent-Generated Code]]**: Determining when to build a shared binary library versus letting coding agents generate and maintain locally owned implementations.
- **[[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]**: The hidden costs of magic frameworks, implicit reflection, and inheritance hierarchies when working with automated coding tools.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Building an organizational paved road using modular infrastructure components without hijacking the application startup lifecycle.
- **[[Designing Software for AI Agents]]**: Architectural design patterns that favor explicit composition and local transparency over ambient framework behavior.
- **[[AI Changes the Economics of Software Libraries]]**: How cheap, accurate code generation shifts the engineering calculus between maintaining shared packages and writing bespoke local code.
- **[[OpenTelemetry]]**: Implementing distributed tracing, metrics, and structured logging without wrapping standard APIs in proprietary internal abstractions.
- **[[Testing in the Model, Agent, LLM Era]]**: Applying automated conformance test suites to validate architectural boundaries and network behaviors without forcing shared runtime dependencies.
