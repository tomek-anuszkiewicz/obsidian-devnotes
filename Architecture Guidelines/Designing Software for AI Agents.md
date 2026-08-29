## Agents Do Not Remove the Need for Architecture

Good architecture becomes more important when agents can generate changes at high speed.

An agent-friendly system should make it easy to answer:

1. Where should this change be made?
2. What behavior is expected?
3. How can correctness be verified?
4. What parts of the system must not change?

The most useful properties are:

- explicit dependencies,
- clear and mechanically enforced boundaries,
- a limited reasoning scope,
- deterministic build and test commands,
- executable architectural constraints,
- predictable and discoverable behavior,
- business concepts represented directly in code.

The goal is not to design code specifically for one generation of models. The goal is to build systems that can be understood reliably by any new participant, human or agent.

These are design heuristics rather than proven laws of agent behavior. Their value depends on the system, team, and operational context.

---

## Predictable and Discoverable Behavior Is Better Than Surprising Hidden Execution

Local code does not need to show every infrastructural concern. It should, however, make the business flow clear and make cross-cutting behavior easy to discover.

An explicit execution flow can be useful:

```csharp
authorization.Check(command, user);
validator.Validate(command);

await transaction.Execute(async () =>
{
    var result = await handler.Handle(command);
    await eventPublisher.Publish(result.Events);
});
```

This style is helpful when the ordering and scope of these operations are important to the business behavior. It is not automatically better than middleware, filters, decorators, or pipelines.

Centralized behavior can reduce duplication and make a system more consistent. For example, global exception handling may map known domain failures to HTTP responses while handlers allow unexpected exceptions to propagate. An agent can often continue this convention by inspecting neighboring handlers, tests, application registration, and middleware configuration. Repeating the same exception handling in every endpoint would make the system less consistent, not more explicit.

The real problem is behavior that is difficult to discover or that changes depending on undocumented ordering, runtime scanning, reflection, or exceptions to the normal convention.

Libraries, middleware, and abstraction are not the problem. Surprising and undiscoverable semantics are.

A popular library used conventionally can help both humans and agents. A small internal abstraction can also help by reducing the number of valid patterns. Problems begin when several layers of internal frameworks make the actual behavior difficult to trace or verify.

> Code length is not the same as cognitive complexity.

An agent may understand twenty simple classes more reliably than five short classes whose behavior depends on global registration, inheritance, runtime scanning, and undocumented conventions. Conversely, one consistent middleware may be easier to follow than exception handling duplicated across twenty handlers.

---

## Monoliths and Microservices Create Different Reasoning Boundaries

A tangled legacy monolith is difficult because:

- business logic is spread across unrelated locations,
- one change has unpredictable side effects,
- boundaries exist only in documentation,
- tests do not isolate behavior,
- hidden dependencies accumulate over time.

Microservices do not automatically solve this problem. They introduce additional complexity:

- multiple repositories,
- distributed contracts,
- event schemas,
- independent deployments,
- backward compatibility,
- partial rollouts,
- queues containing old messages,
- network failures and retries,
- cross-service observability.

A modular monolith is often a useful starting point:

- one repository,
- one local environment,
- one integrated verification process,
- strong internal module boundaries,
- explicit public contracts,
- independent business concepts,
- the possibility of extracting a service later when operational reasons justify it.

However, a modular monolith is not inherently the best architecture for agents. A large repository with weakly enforced boundaries, shared configuration, and implicit dependencies can require a very large reasoning context even when its folders are called modules. Extracting a service later is also not automatically easy: data ownership, contracts, transactions, and operational dependencies must already be understood.

Well-designed microservices can sometimes provide better boundaries for humans and agents:

- a smaller codebase for a particular change,
- explicit ownership of behavior and data,
- narrow external contracts,
- independent tests and deployment,
- a limited blast radius.

These benefits are real only when each service can be understood and verified without reconstructing a large distributed workflow. Otherwise, service boundaries merely replace in-process complexity with network, contract, rollout, retry, and observability complexity.

The choice should therefore follow deployment, scaling, isolation, organizational, and domain requirements. Agents do not inherently prefer monoliths or microservices. They benefit from systems in which the relevant scope, contracts, ownership, and verification procedure are easy to discover.

---

## Communication Boundaries Should Be Explicit

CQRS-style commands and queries can help because they express intent clearly:

```csharp
public sealed record CancelOrderCommand(
    Guid OrderId,
    Guid UserId);
```

Commands and queries can remain inside a module, while selected operations form its public contract. Modules should not directly access another module's internal classes or database tables. Integration events can be used for intentional asynchronous communication.

### Module facade

A module facade provides one visible entry point:

```csharp
public interface IOrdersModule
{
    Task<CancelOrderResult> CancelOrder(
        CancelOrderCommand command,
        CancellationToken cancellationToken);
}
```

This makes the module boundary obvious, but the interface can grow into a large facade that couples consumers to an entire module.

### Public operation handlers

Public handlers are an alternative:

```csharp
public interface ICancelOrderHandler
{
    Task<CancelOrderResult> Handle(
        CancelOrderCommand command,
        CancellationToken cancellationToken);
}
```

This makes the dependency narrow and usually makes navigation from the request to its implementation straightforward. The cost is a larger number of public types and the risk of exposing too much of the module. Only intentional module entry points should be public; implementation handlers can remain internal.

### Mediator or dispatcher

A mediator offers uniform dispatch and centralized pipeline behavior, but introduces indirection. It is a good fit when request-to-handler navigation is predictable and its pipeline is documented and tested. It becomes problematic when global dispatch, registration, or pipeline behavior is difficult to discover.

There is no universally best choice between a module facade, public handlers, and a mediator. The important properties are that:

- the public operations of a module are identifiable,
- the request-to-implementation path is easy to navigate,
- cross-cutting behavior can be discovered,
- data and behavior ownership are clear,
- module boundaries are mechanically enforced.

---

## Model Data to Eliminate Interpretation

A large explicit model is often safer than a compact ambiguous one.

Avoid designs where:

- currency depends on product type,
- `null` means several unrelated things,
- zero means either a real value or absence,
- one field represents supplier cost in one context and customer price in another,
- margin is hidden inside the final number,
- the meaning of data depends on execution order.

Do not minimize the number of fields. Minimize the number of possible interpretations.

---

## Separate Inputs, Intermediate Results, and Final Outputs

Do not use one mutable `PricingContext` whose fields gradually change meaning.

Prefer explicit stages:

```text
supplier data
→ validation
→ normalization
→ product costs
→ currency conversion
→ product adjustments
→ package combination
→ package adjustments
→ profit policy
→ customer price
→ explanation and audit trail
```

Each meaningful stage should have a clear input and output. Separate types are particularly useful when a stage changes the meaning, ownership, validity guarantees, or lifecycle of the data. They should not be introduced mechanically when they only create repetitive mapping without adding semantic information.

Example categories:

```csharp
HotelSupplierQuote
NormalizedHotelCost
HotelPricingResult
PackagePricingResult
ProfitValidationResult
```

This makes data provenance and responsibility visible without requiring a distinct type for every incidental implementation step.

## Practical Working Rules

### For architecture

- Prefer predictable and discoverable behavior over surprising hidden execution.
- Keep business flow explicit, but centralize infrastructural concerns when consistent middleware, decorators, or pipelines make them easier to apply and verify.
- Use popular libraries conventionally when they fit, but allow small internal abstractions when they reduce ambiguity.
- Avoid unnecessary internal frameworks.
- Keep business functionality local where possible and make unavoidable cross-cutting behavior easy to find.
- Enforce module boundaries mechanically.
- Use types to represent meaning.
- Do not encode business state through `null`, zero, or magic values.
- Keep side effects and transaction boundaries visible or readily traceable.
- Treat modular monoliths and microservices as architectural trade-offs, not as agent-specific defaults.
- Choose module facades, public handlers, or mediator dispatch according to discoverability, coupling, and consistency rather than fashion.
