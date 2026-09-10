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
---

## Core Question

In the era of LLMs and coding agents, does it still make sense to maintain internal team or corporate NuGet packages?

A possible alternative is:

- describe how a feature should behave,
    
- provide implementation guidelines and examples,
    
- let an agent generate the implementation inside each application,
    
- validate the result using independent conformance tests.
    

The answer depends on whether the organization needs a **shared implementation** or only a **shared standard**.

---

## Traditional Reasons for Internal NuGet Packages

Internal packages have usually been created to provide:

1. Code reuse
    
2. Consistent implementation across applications
    
3. Centralized bug fixes
    
4. Shared infrastructure abstractions
    
5. Standard project structure
    
6. Reduced boilerplate
    
7. Enforcement of organizational conventions
    

LLMs significantly reduce the cost of writing repetitive code. This weakens the argument that code should be packaged only because developers do not want to write it repeatedly.

However, agents do not automatically solve versioning, rollout, ownership, or consistency problems.

---

## Two Different Requirements

The most important distinction is between these two goals.

### Shared coding convention

> Every application should implement a feature in a similar way.

Examples:

- endpoint structure,
    
- validation style,
    
- mapping conventions,
    
- handler organization,
    
- naming conventions,
    
- error response format,
    
- logging conventions,
    
- dependency registration.
    

For this type of requirement, a shared runtime package may be unnecessary.

A combination of the following may be better:

- written implementation instructions,
    
- reference implementations,
    
- agent prompts,
    
- architecture tests,
    
- Roslyn analyzers,
    
- source templates,
    
- conformance tests.
    

The implementation can remain local to each application.

### Shared runtime behavior

> Every application must execute the same trusted implementation.

Examples:

- authentication and authorization logic,
    
- token validation,
    
- cryptography,
    
- request signing,
    
- audit logging,
    
- trace-context propagation,
    
- service discovery,
    
- protocol serialization,
    
- internal API clients,
    
- critical retry and timeout behavior,
    
- shared business calculations that must remain identical.
    

In these cases, an internal NuGet package still provides real value.

The goal is not merely to avoid rewriting code. The goal is to preserve one implementation, one ownership model, and one place where a defect can be fixed.

---

## Instruction-Driven Code Generation

Instead of providing a large internal framework, an organization can define an implementation contract.

For example:

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

An agent could receive an instruction such as:

```text
Implement this feature according to engineering-guidelines/api-endpoints.md.

Use the reference implementation only as an example.

Keep the implementation local to this service.

The result must pass the Company.ApiConformanceTests package.
```

This approach treats implementation instructions as a form of source material for the agent.

The application owns the generated code, while the organization owns the specification and verification rules.

---

## Executable Specifications

Written instructions alone are not sufficient.

Natural-language documents are often:

- ambiguous,
    
- incomplete,
    
- outdated,
    
- interpreted differently by different agents,
    
- difficult to enforce during later modifications.
    

Independent tests can act as an executable organizational specification.

Examples of behaviors that can be validated:

- error responses use the required schema,
    
- correlation identifiers are propagated,
    
- unauthorized requests are rejected correctly,
    
- sensitive data is not returned in errors,
    
- idempotency rules are respected,
    
- transient failures are retried,
    
- timeout limits are applied,
    
- OpenAPI documents contain required metadata,
    
- audit events are produced,
    
- logs contain required contextual fields.
    

The tests should verify behavior rather than implementation details.

Bad test:

```csharp
service.Should().BeOfType<CompanyRetryHandler>();
```

Better test:

```csharp
await AssertRetriesTransientFailureAsync(
    client,
    expectedAttempts: 3);
```

The first test forces a particular internal class.

The second test verifies the required behavior and allows each application to choose an appropriate implementation.

---

## Arbitrary Tests as an External Constraint

A useful model is to maintain a package containing only tests, test fixtures, or certification scenarios.

For example:

```text
Company.ApiConformanceTests
Company.SecurityConformanceTests
Company.ObservabilityConformanceTests
```

The application does not necessarily reference a shared production library.

Instead, its implementation is evaluated against an externally defined test suite.

This creates a separation between:

- the implementation owned by the application,
    
- the behavior required by the organization.
    

An agent can freely generate or modify the implementation as long as the conformance tests continue to pass.

This model resembles protocol compatibility testing more than traditional code reuse.

---

## Advantages of Local Agent-Generated Implementations

### Easier local customization

The implementation can match the architecture and constraints of the application instead of forcing every service through one corporate abstraction.

### Less framework coupling

Applications are not tied to a large internal framework that may become difficult to evolve.

### More explicit code

Business and infrastructure behavior remains visible inside the application.

Developers and agents can inspect the complete execution path without navigating through multiple package layers.

### Independent evolution

Different applications can adopt new approaches without waiting for a shared package release.

### Easier removal

Generated local code can be refactored or deleted without dealing with a framework dependency.

### Reduced pressure to create premature abstractions

A pattern does not have to become a reusable package immediately.

The organization can first document and validate the pattern and only package it when a genuinely stable abstraction emerges.

---

## Entity Framework as an Example of the Same Shift

Entity Framework illustrates a broader consequence of cheap agent-generated code.

An ORM is valuable partly because it allows developers to express data access with relatively little application code. An agent does not have the same cost constraint. It can generate a dedicated SQL query, execute it through a lower-level database API, and map the result explicitly into the exact structure required by the operation.

Instead of:

```text
LINQ query
→ Entity Framework
→ query translation
→ generated SQL
→ materialization
```

an application may increasingly contain:

```text
request
→ specialized SQL
→ data reader
→ explicit mapping
→ response
```

This produces more local code, but it may also provide:

- more predictable SQL,
- fewer unnecessary columns and joins,
- no accidental tracking,
- less ORM-specific runtime behavior,
- easier performance analysis,
- a more explicit execution path,
- mapping specialized for the exact result shape.

The generated implementation can approach an almost inline data pipeline: the query and mapping exist specifically for one use case rather than being expressed through a general-purpose object-relational abstraction.

The trade-off is that the application now owns more database-access code. Schema changes, provider differences, transaction handling, retries, parameterization, and mapping correctness must still be handled reliably.

Therefore, the important question is not whether an agent *can* replace Entity Framework. It is whether the ORM provides enough value beyond reducing the amount of code that must be written.

In many applications, Entity Framework will remain useful because it provides a mature unit-of-work model, change tracking, migrations, relationship management, provider abstraction, and a well-understood programming model. But for performance-sensitive reads, narrow handlers, reporting queries, or simple CRUD operations, agents may make explicit SQL and generated mapping economically attractive even when a developer would previously have chosen an ORM mainly to avoid boilerplate.

This is the same general pattern as with internal libraries:

> When writing code becomes cheap, abstractions must justify themselves by more than the number of lines they eliminate.

---

## Risks of Generated Local Implementations

### Multiple sources of truth

If twenty services contain generated copies of similar logic, there are twenty implementations to inspect and maintain.

### Uneven adoption of fixes

A security or reliability fix may be applied in some repositories but not others.

### Local divergence

Teams may modify generated code in incompatible ways.

### Repeated review cost

Even when an agent writes the implementation, humans may still need to review the same type of code in many repositories.

### Complex migrations

A global behavioral change may require multiple pull requests, deployments, and compatibility phases.

### False confidence from tests

Tests validate only the behavior they cover.

An implementation may pass all conformance tests while still containing:

- performance problems,
    
- resource leaks,
    
- race conditions,
    
- unsafe defaults,
    
- maintainability problems,
    
- untested security weaknesses.
    

Tests do not remove the need for architecture and code review.

---

## Advantages of Internal NuGet Packages

### One implementation

Critical behavior exists in one place.

### Centralized fixes

A defect can be corrected in the package and distributed through dependency updates.

### Clear ownership

A team can be responsible for the component and its lifecycle.

### Auditable behavior

Security-sensitive and protocol-sensitive code can be reviewed and certified centrally.

### Lower implementation variance

Applications are less likely to accidentally implement slightly different versions of the same mechanism.

### Stable contracts

A package can provide a well-defined API that remains stable while its internal implementation changes.

---

## Risks of Internal NuGet Packages

### Hidden complexity

Important behavior may be buried behind extension methods and framework conventions.

```csharp
services.AddCompanyPlatform();
```

This may register dozens of services, policies, handlers, and background processes that are difficult to discover.

### Excessive abstraction

Packages often become internal frameworks that attempt to support every possible application.

### Version fragmentation

Different services may use different package versions, so a central package does not automatically guarantee one production behavior.

### Slow organizational change

A package change may require coordination across many teams and repositories.

### Dependency coupling

Applications may be forced to adopt unrelated dependencies or architectural decisions.

### Accidental business logic centralization

Shared packages may gradually absorb business rules that should belong to specific domains.

---

## Business Logic Should Usually Not Be Hidden in Shared Packages

A corporate package should not become a place for unrelated business behavior.

Business logic usually belongs in the application or domain that owns it.

A package may make sense when the business concept itself is genuinely shared and centrally governed, for example:

- a company-wide tax calculation,
    
- a regulated fee calculation,
    
- a shared risk-scoring algorithm,
    
- a canonical identity-matching algorithm.
    

Even then, it may be better to expose the capability through a service API rather than distribute the algorithm as a package, especially when:

- updates must take effect immediately,
    
- the implementation depends on frequently changing data,
    
- auditability is important,
    
- multiple technology stacks consume it.
    

---

## NuGet Package, Generated Code, or Service API

A useful decision model is:

### Use a NuGet package when

- all consumers use .NET,
    
- the logic should execute locally,
    
- runtime performance matters,
    
- offline execution is required,
    
- the implementation is stable,
    
- one reviewed implementation is valuable,
    
- updates can be distributed through package upgrades.
    

### Use generated local code when

- the code is mostly structural or repetitive,
    
- local customization is expected,
    
- implementation differences are acceptable,
    
- behavior can be validated externally,
    
- the code is easy to understand and review,
    
- the abstraction would otherwise hide too much.
    

### Use a service API when

- behavior must be changed centrally,
    
- consumers use multiple technology stacks,
    
- the logic depends on centralized state or data,
    
- immediate rollout is important,
    
- strict audit and governance are required,
    
- the organization needs one live version rather than many deployed package versions.
    

---

## A Hybrid Model

The likely future model is not the complete removal of internal packages.

It is a smaller set of carefully selected runtime packages combined with executable standards and agent-generated application code.

### Layer 1: Small shared runtime

Use NuGet packages for:

- security primitives,
    
- telemetry foundations,
    
- protocol clients,
    
- stable contracts,
    
- critical algorithms,
    
- low-level infrastructure integrations.
    

### Layer 2: Executable organizational standards

Use:

- conformance tests,
    
- architecture tests,
    
- analyzers,
    
- CI policies,
    
- security scanning,
    
- compatibility test suites.
    

### Layer 3: Locally generated code

Generate:

- endpoints,
    
- handlers,
    
- validators,
    
- mapping code,
    
- application-specific adapters,
    
- dependency registration,
    
- configuration,
    
- boilerplate integrations.
    

This model avoids building a large corporate framework while still preserving consistency where consistency matters.

---

## Decision Questions

Before creating an internal NuGet package, ask:

1. Do we need one implementation or only one expected behavior?
    
2. Must every application execute exactly the same code?
    
3. Is local customization desirable or dangerous?
    
4. Does a fix need to be applied centrally?
    
5. Can the requirement be verified through black-box tests?
    
6. Is the proposed package mainly eliminating boilerplate?
    
7. Would generated code be easier to understand than the abstraction?
    
8. Will the package hide business behavior?
    
9. How will version upgrades be enforced?
    
10. What happens when one application cannot upgrade?
    
11. Would a service API provide better central control?
    
12. Is the abstraction already stable, or are we packaging it prematurely?
    

---

## Practical Rule

A useful rule is:

> Use a package when the organization needs one implementation.  
> Use instructions and conformance tests when the organization needs one standard.  
> Use a service when the organization needs one centrally controlled live behavior.

LLMs reduce the cost of producing code.

They do not eliminate:

- coordination,
    
- ownership,
    
- rollout,
    
- compatibility,
    
- versioning,
    
- auditing,
    
- maintenance.
    

Therefore, agents will probably reduce the number of internal NuGet packages whose main purpose is boilerplate reuse.

They will not eliminate packages whose purpose is to provide a trusted, shared runtime implementation.

---

## Mental Model

Internal NuGet packages should no longer be the default answer to repeated code.

The first question should be:

> Is this a reusable implementation, or merely a repeatable instruction?

If it is a repeatable instruction, an agent can generate the code.

If correctness can be described externally, conformance tests can validate it.

If one exact implementation must be trusted and maintained centrally, a package or service is still the better abstraction.
---

## Relationship to the Knowledge Graph

- **[[Designing Internal NuGet Packages as an Explicit, Composable Framework]]**: Principles for designing shared libraries that compose explicitly without framework lock-in.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Reusable platform blocks versus domain-specific application code.
- **[[AI Changes the Economics of Software Libraries]]**: How AI shifts the economics from heavy centralized dependencies to decentralized agent-maintained code.
- **[[Software Entropy and the Zero-Friction Trap]]**: Why localized code duplication can provide cleaner blast-radius isolation than shared package dependencies.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: The shift toward explicit, self-contained implementations maintained by coding agents.
