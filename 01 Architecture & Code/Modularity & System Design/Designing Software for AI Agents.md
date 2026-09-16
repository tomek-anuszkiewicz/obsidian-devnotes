---
title: Designing Software for AI Agents
tags:
  - software-architecture
  - system-design
  - ai-agents
  - agentic-coding
  - modularity
  - observability
aliases:
  - Agent-Oriented Software Design
  - Building Software for AI Consumption
  - Principles of Agentic System Design
  - Designing Discoverable Codebases
---

# Designing Software for AI Agents: Architectural Predictability and Explicit Boundaries

Good architecture becomes significantly more critical when autonomous agents generate changes at high speed. 

When a human developer inherits a tangled codebase with hidden conventions, they lose hours in chat threads, design documents, and debugger sessions piecing together how things actually run. When an AI agent hits that same codebase, it burns context window tokens searching through disconnected files, hallucinates missing links, and generates diffs that subtly violate unstated invariants across the system.

Whether a change is written by a junior developer, a staff engineer, or a coding agent, an agent-friendly system makes four basic questions trivial to answer:

1. **Where should the change be made?** (Locality and ownership)
2. **What behavior is expected, and what invariants must not break?** (Contracts and business rules)
3. **How can correctness be verified quickly and deterministically?** (Test oracles and static analysis)
4. **What parts of the system are guaranteed to remain unaffected?** (Blast radius)

To satisfy these requirements, the architecture should prioritize:
- Explicit, typed dependencies over ambient runtime context.
- Mechanically enforced module boundaries rather than documentation-only rules.
- Limited reasoning scope per unit of work.
- Deterministic build, lint, and test commands that run in seconds.
- Executable architectural constraints enforced by the compiler or linter.
- Predictable, discoverable execution flows.
- Domain concepts represented directly in the type system rather than generic primitive types.

The objective is not to write code tailored to the idiosyncrasies of one specific model release. The goal is to build systems that can be reasoned about reliably by any new engineer or tool operating with limited context.

---

## Predictable and Discoverable Behavior Is Better Than Surprising Hidden Execution

Local code does not need to expose every infrastructural concern, but it must make the core business flow obvious and cross-cutting behaviors discoverable. 

Consider this explicit execution pipeline:

```csharp
authorization.Check(command, user);
validator.Validate(command);

await transaction.Execute(async () =>
{
    var result = await handler.Handle(command);
    await eventPublisher.Publish(result.Events);
});
```

This pattern makes the execution order, transaction boundary, and side-effect dispatch unmistakable. Any engineer or agent inspecting the handler immediately sees where the database commit occurs, when domain events fire, and where authorization runs.

Contrast that with an implicit, magic approach:

```csharp
// How are permissions evaluated? Does the attribute run before model binding?
// Is there an ambient database transaction wrapping this method?
// Does saving an entity automatically trigger outbox dispatch via reflection?
[CustomMagicFilter]
[TransactionalPipeline]
public Response Handle(Request req) => _service.DoThing(req);
```

When execution semantics are hidden behind dynamic runtime scanning, aspect-oriented magic, or undocumented filter ordering, both humans and language models struggle. An agent cannot reliably infer the order of execution from a class attribute if that attribute relies on an internal reflection registry configured three projects away.

### Centralize Infrastructure, Keep Domain Flow Visible

Explicit does not mean copy-pasting boilerplate across every endpoint. Centralizing generic technical infrastructure is often the cleanest choice:

- **Centralize generic technical plumbing**: Global exception filters that map domain exceptions to standard HTTP status codes, distributed tracing propagation, structured logging middleware, and metric collection.
- **Keep domain logic and state transitions local**: Authorization checks, input validation rules, domain state mutations, transaction scopes, and event publishing.

For example, having an application-wide middleware catch unhandled domain exceptions and serialize them into RFC-7807 problem details is standard and helpful. An agent can inspect neighboring endpoints, existing test suites, and middleware registration to see how errors surface. Duplicating try/catch blocks across fifty individual handlers would make the system noisier, not more maintainable.

The anti-pattern is behavior that changes based on undocumented ordering, runtime assembly scanning, dynamic proxying, or ad-hoc overrides. Libraries, middleware, and abstractions are not inherently bad; surprising and undiscoverable semantics are.

### Code Length Is Not Cognitive Complexity

A common trap is attempting to minimize character or line count under the assumption that fewer lines mean simpler code for an agent.

An agent can analyze twenty simple, explicit, single-purpose classes with high precision. It frequently stumbles when working in a codebase of five hyper-concise classes whose behavior depends on complex generic inheritance trees, ambient runtime reflection, and dynamic conventions. Conversely, a single, predictable middleware pipeline is far easier to parse than identical error-handling logic copy-pasted inconsistently across twenty endpoints.

---

## Monoliths and Microservices Create Different Reasoning Boundaries

Agents do not have an inherent preference for monoliths or microservices. They are constrained by reasoning scope, execution context, and the speed of feedback loops.

A tangled legacy monolith is difficult to maintain because:
- Domain logic is scattered across disconnected managers, helpers, and utilities.
- Modifying a single method triggers unpredictable side effects in distant subsystems.
- Boundaries exist only as conventions in team wikis, easily bypassed by developers under deadline pressure.
- Test suites are slow, flaky, or rely on shared mutable database states.
- Hidden dependencies accumulate through uncontrolled database queries and circular references.

Microservices do not automatically eliminate these issues; they often shift the complexity into distributed systems concerns:
- Logic split across multiple distinct repositories.
- Distributed contract drift between services.
- Asynchronous event schema evolution and versioning headaches.
- Independent deployment pipelines requiring complex multi-stage rollouts.
- Backward compatibility requirements for inflight messages.
- Stale messages lingering in message queues during deployments.
- Partial failures, network retries, and idempotency tracking.
- Complicated end-to-end debugging across distributed log aggregators.

| Architectural Pattern | Why Agents Can Reason About It Well | Practical Operational Risks |
| :--- | :--- | :--- |
| **Modular Monolith** | Single repository, unified local compilation, fast integration test execution, compile-time type safety across domain boundaries. | Context bloat if the codebase grows massive; discipline lapses can turn modules into tightly coupled spaghetti if boundaries are not enforced by the compiler or build tools. |
| **Microservices** | Small, focused repositories; narrow context window footprint per task; explicit REST/gRPC contracts; isolated deployment blast radius. | Multi-repo orchestration; contract drift; slow local feedback loops requiring Docker Compose or remote dev clusters to verify integration work. |

A well-architected modular monolith is frequently the most practical baseline:
- A single repository simplifies codebase-wide search and symbol tracking.
- A consistent local runtime makes spinning up verification environments trivial.
- Clear module boundaries can be enforced via build configurations (e.g., project references, package visibility rules, or architecture unit tests).
- Strong public contracts make interactions between domains clear.
- Boundaries preserve the option to extract an isolated service later if operational, deployment, or scaling requirements justify it.

However, calling folders "modules" does not make a modular monolith clean. If modules share internal database tables, read from dynamic shared configurations, or call each other's internal services directly, an agent still has to load the entire repository into its working context to understand the impact of a small change. 

Similarly, extracting services later is only straightforward if data ownership, transactional boundaries, and external APIs were strictly isolated from the start.

---

## Communication Boundaries Should Be Explicit

To maintain clean module boundaries, communication between subsystems must be structured and typed. Reaching directly into foreign database tables or internal module classes destroys modularity.

Using CQRS-style commands and queries helps because they explicitly state intent and inputs:

```csharp
public sealed record CancelOrderCommand(
    Guid OrderId,
    Guid UserId);
```

Commands and queries handle internal module behavior, while selected contracts define the module's public boundary. When cross-module communication must happen asynchronously, integration events decouple execution timelines.

### Approach 1: The Module Facade

A module facade creates a single, discoverable entry point for external consumers:

```csharp
public interface IOrdersModule
{
    Task<CancelOrderResult> CancelOrder(
        CancelOrderCommand command,
        CancellationToken cancellationToken);
}
```

This pattern makes the surface area of the module immediately obvious to an agent browsing the project. The primary downside is interface bloat: over time, the facade can accumulate dozens of unrelated methods, turning into an unwieldy God interface that couples consumers to the whole module surface.

### Approach 2: Public Operation Handlers

Exposing dedicated, fine-grained handlers for individual operations keeps dependencies narrow:

```csharp
public interface ICancelOrderHandler
{
    Task<CancelOrderResult> Handle(
        CancelOrderCommand command,
        CancellationToken cancellationToken);
}
```

Structuring operations as dedicated 1:1 handlers (one file per command/query and its corresponding handler) makes tracing code straightforward. When an agent searches for the consumer of `CancelOrderCommand`, symbol navigation leads straight to `CancelOrderHandler`. The trade-off is an explosion of public types and files. To prevent leaks, keep internal pipeline handlers internal and only expose deliberate boundary handlers publicly.

### Approach 3: In-Process Mediators or Dispatchers

Mediators provide uniform dispatch and simplify pipeline concerns like cross-cutting metrics, logging, and validation:

```csharp
var result = await mediator.Send(new CancelOrderCommand(orderId, userId));
```

This decouples the caller from the handler implementation, but it introduces indirection. If the dispatch mechanism relies on reflection-based assembly scanning, jump-to-definition breaks in standard IDE tooling, making it harder for an agent to trace the request directly to the implementation. 

Mediators work well when handler resolution is predictable, statically discoverable, and the pipeline order is clearly documented and tested. If dynamic registration hides which handler executes, the mediator becomes a liability.

There is no single winner among facades, discrete handlers, and mediators. The non-negotiable requirements are:
- Public operations for a given domain are easy to identify via file structure or explicit interfaces.
- The path from caller to execution is directly traceable using standard symbol lookup.
- Cross-cutting behaviors are discoverable.
- Data and behavior ownership remain clearly isolated.
- Boundary rules are mechanically enforced by compiler rules or static architecture tests (e.g., NetArchTest, ArchUnit).

---

## Model Data to Eliminate Interpretation

Ambiguous domain models force both humans and agents to make guesses. When data semantics are implicit, agents often introduce subtle bugs by misinterpreting what a field represents under different conditions.

A model with more fields that are explicitly named is almost always safer than a compact, overloaded model.

```
AMBIGUOUS / OVERLOADED MODEL:
class Booking {
    double amount;        // Wholesale cost? Retail price? Including or excluding tax?
    int status;           // What does 0 mean? Unprocessed, failed, or cancelled?
    String metadata;      // Untyped JSON string with varying fields based on status
    DateTime? processed;  // Does null mean queued, in-flight, or skipped?
}

EXPLICIT / SELF-DOCUMENTING MODEL:
class Booking {
    Money supplier_cost_net;
    Money customer_price_gross;
    BookingStatus lifecycle_status; // Explicit enum: PendingPayment, Confirmed, Cancelled
    AuditTrail audit_record;        // Strongly-typed structured payload
    ProcessingSchedule schedule;   // Distinct state machine representation
}
```

Key rules for domain modeling:
- **Ban multi-purpose nulls**: Never use `null` to simultaneously represent "value not yet loaded", "value does not exist", and "value not applicable". Use explicit optional types or dedicated state representations.
- **Eliminate magic sentinel values**: Do not use `0`, `-1`, or empty strings to signify infinite retries, disabled features, or system-level accounts. Use dedicated enums or nullable value objects with validation.
- **Eliminate context-dependent fields**: A single field like `price` must not mean supplier cost during ingesting and retail customer price during checkout. Name them `SupplierCostNet` and `CustomerPriceGross`.
- **Make margins and calculations explicit**: Do not store only the final calculated value if intermediate values represent distinct business realities. Store the base cost, the margin rate, and the final price.
- **Avoid temporal coupling in data**: The meaning of a property should not depend on the order in which methods were executed on the object.

Do not try to minimize the count of classes or fields. Minimize the count of valid interpretations an engineer or agent must evaluate.

---

## Separate Inputs, Intermediate Results, and Final Outputs

A common anti-pattern in complex domains is the mutable bag pattern: passing a single `OrderContext` or `PricingContext` through a dozen classes, gradually mutating its properties, appending flags, and changing the semantics of internal fields as the calculation progresses.

Agents struggle with this pattern because understanding the state of the context at step seven requires simulating steps one through six in memory.

Instead, model multi-step workflows as a pipeline of distinct, immutable transformations:

```text
[ Raw Supplier Data ]
         │
         ▼
[ Validation Stage ]    ──► [ Validated Supplier Data ]
         │
         ▼
[ Normalization Stage ] ──► [ Normalized Cost Model ]
         │
         ▼
[ Pricing Rules Engine] ──► [ Customer Price Package ]
         │
         ▼
[ Audit Generator ]     ──► [ Audited Final Record ]
```

Each stage takes a validated, strongly-typed input and produces a separate, strongly-typed output. 

Consider a pricing pipeline structured as explicit stages:

```csharp
public record HotelSupplierQuote(
    string SupplierCode, 
    decimal RawRate, 
    string Currency);

public record NormalizedHotelCost(
    Guid HotelId, 
    Money BaseCostUtc);

public record HotelPricingResult(
    Guid HotelId, 
    Money CustomerPrice, 
    decimal MarginApplied);

public record PackagePricingResult(
    IReadOnlyList<HotelPricingResult> LineItems, 
    Money TotalPackagePrice);

public record ProfitValidationResult(
    bool IsViable, 
    Money NetMargin, 
    IReadOnlyList<string> PolicyViolations);
```

Using explicit types for intermediate steps provides major engineering advantages:
- **Data provenance is traceable**: An agent reading `HotelPricingResult` knows exactly what inputs were required to calculate it without tracing through raw supplier feeds.
- **Isolated unit tests**: The normalization step can be tested across hundreds of edge cases with small, focused unit tests that don't need database mocks or dynamic service setups.
- **Defensive state transitions**: An operation that requires a `NormalizedHotelCost` cannot accidentally be invoked with a raw, unvalidated `HotelSupplierQuote`.

This rule should be applied thoughtfully. Do not introduce boilerplate mapping types for trivial CRUD operations that perform no transformations. Separate types are valuable whenever data passes across a trust boundary, changes ownership, or transitions through a distinct business lifecycle state.

---

## Practical Working Rules

### Architecture and Boundaries
- **Keep domain flows direct**: An engineer or agent should be able to navigate from an API endpoint or message consumer to its core domain handler in seconds using standard symbol search.
- **Enforce module boundaries mechanically**: Do not rely on directory naming conventions or team discipline. Use compiler barriers, project references, internal access modifiers, or automated architectural fitness tests to catch boundary violations during CI.
- **Make transactions and side effects obvious**: Avoid hiding database commits or domain event dispatching inside mysterious framework lifecycle hooks. Keep boundaries visible in the execution flow.
- **Choose communication patterns pragmatically**: Use module facades, 1:1 public operation handlers, or mediator pipelines based on the discoverability and operational coupling of your system, not based on architectural trends.
- **Treat architecture as an operational trade-off**: Modular monoliths and microservices solve different organizational and scaling problems. Choose based on deployment constraints, data boundaries, and operational complexity.

### Code and Data Design
- **Eliminate guesswork in data models**: Never use `null`, zero, or magic strings to encode domain state. Use typed enums, discriminated unions, or dedicated state types.
- **Avoid single mutable context objects**: Structure multi-step calculations as staged transformations where data flows from explicit inputs to separate, immutable outputs.
- **Centralize generic infrastructure, isolate business decisions**: Move technical concerns like logging and exception translation into consistent middleware, but keep domain logic, validation, and authorization visible in the handler.
- **Favor standard library patterns**: Use well-known libraries in their default, conventional configurations. Build small internal helper functions when they reduce repetitive boilerplate, but avoid large, custom, reflection-heavy internal frameworks that obscure how the application actually executes.
- **Verify with fast, deterministic tests**: Pair explicit architecture with automated unit and integration tests that run locally in seconds. A clear architecture tells an agent where to make a change; a fast test suite tells it immediately whether that change was correct.

---

## Related Notes

- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: How generative velocity accelerates structural entropy and why mechanical boundaries are necessary.
- **[[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]**: The hidden costs of dynamic reflection, implicit magic, and deep indirection when machines maintain code.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: How layouts, typing disciplines, and structural patterns adapt for automated readers.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Structuring project context, interfaces, and specifications for agentic workflows.
- **[[Data Access Economics with Coding Agents - ORMs vs Explicit SQL]]**: Evaluating persistence layers, contract testing, and query maintainability with coding agents.
- **[[Scaling a Modular Monolith with Local-or-Remote Module Execution]]**: Implementing module boundaries that preserve unified local reasoning while allowing distributed runtime execution.
- **[[Testing in the Model, Agent, LLM Era]]**: How deterministic automated tests serve as the ground truth verification layer for agent-generated code.
