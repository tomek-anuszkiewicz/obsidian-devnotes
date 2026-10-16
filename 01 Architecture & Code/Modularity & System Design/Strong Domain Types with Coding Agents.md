---
title: Strong Domain Types with Coding Agents
tags:
  - type-systems
  - domain-driven-design
  - ai-agents
  - software-architecture
  - code-generation
aliases:
  - The Economics of Strong Domain Types
  - Replacing Primitives with Domain Types
  - Compiler Feedback for Domain Rules
  - Validated Values and Typed State Transitions
---

## More Safety at Comparable Cost

My view is that coding agents make stronger domain types and explicit rules a practical way to increase software safety at comparable development and maintenance cost. We can afford to express more rules in code because agents handle much of the additional implementation work, while compilers enforce the distinctions during subsequent changes.

Dedicated types require constructors, conversions, serializers, database mappings, and updates to callers. An agent can perform much of that repeated work, while the resulting structure lets the compiler reject mistakes that previously depended on developer attention. [[Agent Advantage — Relentless, Methodical Work]] discusses that broader advantage. Generators and reusable libraries can already remove some of the work; AI assistance is another option for the remaining project-specific changes.

The benefit can continue during maintenance. Changing a parameter from `NetAmount` to `GrossAmount`, for example, exposes callers still passing the former. Changing the meaning of an existing `GrossAmount` leaves the type unchanged and may produce no diagnostics. Rounding policy, persistence compatibility, and external contracts still need deliberate review and tests.

The examples below explain why I consider this worthwhile: distinct identifiers prevent swapped arguments, controlled construction preserves validation rules, state types restrict operations, and explicit results expose cases that callers need to handle. Each adds structure with a specific purpose. The guarantees have defined limits, and runtime behavior still needs testing, as explained in [[Formal Verification and Runtime Safety Boundaries]].

## Distinguish Values That Must Not Be Interchanged

In C#, a small set of declarations can separate values that otherwise share the same representation:

```csharp
public readonly record struct CustomerId(Guid Value);
public readonly record struct OrderId(Guid Value);
public readonly record struct NetAmount(decimal Value);
public readonly record struct GrossAmount(decimal Value);

public interface IPaymentService
{
    void Charge(CustomerId customer, GrossAmount amount);
}
```

With these declarations, passing an `OrderId` or a `NetAmount` to `Charge` fails to compile. The compiler supplies record equality and other routine members, so even without AI the declarations themselves are inexpensive. Much of the continuing work sits where these types meet storage, transport formats, and existing APIs. [C# records](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/record)

The distinction must survive those boundaries. If every caller immediately extracts `.Value` and passes raw primitives through the application, the compiler loses the information. Implicit conversions can also weaken the intended separation. Prefer explicit conversions at a small number of adapters, where their meaning can be reviewed.

These wrappers establish identity, not numeric validity or provenance. `GrossAmount` can still contain a negative number, and someone can incorrectly construct it from a net amount. Currency needs its own representation if mixing currencies is a relevant failure. The domain determines which distinctions deserve types.

## Make Construction Establish a Local Rule

Suppose a price must be nonnegative and use a supported currency. A `Price` type can expose a factory that checks both conditions, keep its constructor private, and expose immutable values. The factory returns either a valid price or a validation error. Ordinary consumers then receive an object whose construction has established those conditions.

The value check happens at runtime, where the input is available. The type and its API preserve the result of that check for later operations. A type name alone does not prove that validation happened.

The extra work includes defining useful errors, deciding rounding rules, and making JSON and database adapters use the same construction path. Historical data may fail the new rules and need an explicit migration decision. An agent can implement those adapters and update callers once the policy is clear.

Representation matters. A C# value type can be created with `default`, which does not run a custom constructor. A struct intended to guarantee a positive value must account for its zero-initialized state. A class with controlled construction avoids that particular path, but callers still need a policy for missing values. [C# structure initialization](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/struct)

## Give Process States Different APIs

A single order object with a status string and several optional fields permits combinations such as a draft with a shipping confirmation. Separate state types can restrict which operations accept which values:

```csharp
public interface IOrderWorkflow
{
    ValidatedOrder Validate(DraftOrder order);
    PaidOrder Pay(ValidatedOrder order);
    Shipment Ship(PaidOrder order);
}
```

This interface sketch shows successful transitions; a real API must also represent failures. The state types and their construction rules are deliberately omitted here. To make the design meaningful, callers must not be able to create a `PaidOrder` freely without the required evidence.

The compiler can reject passing a `DraftOrder` directly to `Ship`. Implementing that restriction requires more types, controlled construction, transition functions, persistence mapping, and handling for rejected transitions. This is a concrete case where additional code can prevent misuse of an API.

An in-memory state object does not establish that a database row is still current, and a C# reference can be reused. Shipping still needs concurrency control and protection against duplicate execution. The type also cannot decide whether "paid" means authorized, captured, or settled. That is a business decision, as explored in [[Why Business Logic Is the Hardest Part of Agentic Coding]].

## Represent Outcomes That Require Different Actions

A payment request can succeed, be rejected, or leave its outcome unknown after a connection failure. Returning `false` for both rejection and uncertainty discards information needed by the caller. An explicit result can carry a receipt for success, a reason for rejection, and an operation identifier for reconciliation when the outcome is unknown.

This creates more code: result variants, mappings from provider responses, and handling at each caller. It also makes the required decisions visible. In a language with exhaustive matching, the compiler can reject a handler that omits a variant. Rust's `match` provides this check; a wildcard arm can absorb newly added variants, so the handling style matters. [Exhaustive matching in Rust](https://doc.rust-lang.org/book/ch06-02-match.html)

In C#, introducing a class hierarchy alone does not provide the same exhaustive-match guarantee. Check what the chosen language and analyzer actually enforce. The result model still helps reviewers see the cases, but claiming that every caller must handle each one requires an enforced check.

## Compiler Diagnostics Become Part of the Editing Loop

Once a rule is represented in a type or signature, the agent gets feedback tied to a concrete location: this operation requires a customer identifier, a gross amount, or an order in a particular state. It can inspect the mismatch, correct the implementation, and compile again. Rust also exposes structured diagnostics containing error codes, source locations, and optional suggested replacements. These are useful inputs to tools; they do not make a suggested change correct for the business. [Rust compiler JSON diagnostics](https://doc.rust-lang.org/rustc/json.html)

The quality of this loop depends on preserving the rule. An agent can make an error disappear by weakening a parameter to a primitive, inserting an unjustified conversion, or replacing a precise outcome with a generic fallback. Review should establish why the new code satisfies the intended distinction. A successful build only confirms the constraints that remain encoded.

This is one reason stronger static checks may become more valuable when agents write code. [[Programming Languages May Evolve Differently in the Age of AI]] places that mechanism in the broader discussion of language choice. It applies to application types in existing languages as well as to language features such as Rust's ownership rules.
