Source generation solves an important software engineering problem: it allows libraries to replace generic runtime mechanisms with specialized code generated at compile time.

In C#, source generators are commonly used for areas such as:

- serialization,
    
- object mapping,
    
- API clients,
    
- dependency injection,
    
- validation,
    
- boilerplate code,
    
- strongly typed wrappers.
    

Their performance can be excellent because the generated code often avoids:

- reflection,
    
- dynamic dispatch,
    
- metadata lookup,
    
- generic runtime abstractions,
    
- unnecessary allocations.
    

Instead of executing a generic abstraction, the application runs code specialized for a concrete type or use case.

```text
generic library
+ configuration
+ deterministic source generator
→ specialized code
```

AI introduces another way of achieving similar specialization.

```text
requirements
+ existing code
+ conventions
+ tests
+ LLM
→ explicit specialized code
```

The important difference is not primarily performance.

It is the **cost of expressing unusual requirements**.

## The Hidden Cost of Source Generators Is Their Configuration Model

A source generator must understand requirements through a formally designed interface.

This usually grows into some combination of:

```text
attributes
+ conventions
+ fluent configuration
+ custom converters
+ extension points
+ overrides
+ special cases
```

Every capability must first be anticipated and implemented by the library author.

A new requirement may therefore mean:

```text
user requirement
→ design new configuration API
→ implement generator support
→ test combinations
→ document behavior
→ release new library version
→ configure it in the application
```

This creates an unavoidable limitation.

There will always be cases where the documentation says:

```text
not supported
planned for the next version
requires a workaround
requires a custom converter
requires dropping to manual code
```

The generator cannot generate something that its authors did not teach it how to express.

## LLMs Have a Different Constraint

An LLM does not need a complete DSL describing the space of possible implementations.

A developer can instead describe the desired behavior directly:

```text
Map Order to OrderDto.

Use Customer.DisplayName as CustomerName.
Default Currency to EUR when it is missing.
Ignore InternalComment.
For legacy orders created before 2024,
calculate Total using the legacy formula.
```

The resulting implementation may simply be:

```csharp
return new OrderDto
{
    Id = order.Id,
    CustomerName = order.Customer.DisplayName,
    Currency = order.Currency ?? "EUR",
    Total = order.CreatedAt < LegacyCutoff
        ? CalculateLegacyTotal(order)
        : order.Total
};
```

For a traditional generator, the legacy condition may require a new feature in the configuration model.

For an LLM, it may only require another line of code.

This creates a major asymmetry:

```text
Source generator:

new requirement
→ new abstraction or configuration capability

AI-generated code:

new requirement
→ slightly different implementation
```

## Flexible Authoring Can Produce Extremely Simple Runtime Code

One of the most interesting properties of this approach is that AI flexibility does not require runtime flexibility.

The development process can be highly flexible:

```text
natural language
+ code context
+ tests
+ LLM
```

while the result can remain extremely explicit:

```text
if (...)
{
    ...
}
```

There does not need to be:

- reflection,
    
- a mapping engine,
    
- a rule interpreter,
    
- a runtime DSL,
    
- an AI model in production,
    
- or even a special library.
    

The intelligence exists primarily during development.

The production system receives ordinary code.

This produces an attractive combination:

```text
very flexible authoring
+
very explicit implementation
+
very simple runtime
```

## AI Can Remove Both Runtime and Compile-Time Abstractions

Traditional evolution often looked like this:

```text
runtime abstraction
        ↓
compile-time specialization
        ↓
source generator
```

For example, a reflection-based mapper may evolve into a source-generated mapper.

AI introduces another possible step:

```text
runtime abstraction
        ↓
source generator
        ↓
AI-generated explicit code
```

A source generator removes runtime abstraction by producing specialized code.

AI may sometimes remove the **generator abstraction itself**.

Instead of:

```text
mapping library
+ attributes
+ configuration
+ generator
→ generated mapper
```

the project may simply contain:

```text
mapping requirements
+ agent instructions
→ Mapper.cs
```

The resulting code is committed to the repository and treated like ordinary application code.

## Explicit Code May Become Cheaper Than Abstraction

Historically, abstractions were partly justified because explicit code was expensive to write and maintain.

Writing hundreds of mappings, adapters, DTO conversions, builders, or API wrappers manually was tedious.

A library could replace:

```text
30 lines of repetitive code
```

with:

```text
one line of configuration
```

That was a strong productivity advantage.

AI changes the economics.

If an agent can create and update those 30 lines cheaply, the comparison becomes different:

```text
cost of maintaining abstraction
vs.
cost of generating explicit code
```

The explicit implementation may have several advantages:

- easier debugging,
    
- no hidden behavior,
    
- no framework-specific DSL,
    
- no dependency on a generator,
    
- easier local customization,
    
- straightforward compiler optimization,
    
- fewer constraints imposed by library design.
    

Paradoxically, AI may therefore produce codebases with:

```text
more physical lines of code
but
less conceptual complexity
```

## Removing Abstractions Can Also Improve Performance

Explicit generated code may sometimes outperform generic abstractions precisely because there is less machinery involved.

Instead of:

```csharp
mapper.Map<OrderDto>(order);
```

the agent may generate direct assignments:

```csharp
var dto = new OrderDto(
    order.Id,
    order.Customer.Name,
    order.Items.Count,
    order.Total.Amount);
```

The compiler and JIT can then see the actual operations directly.

This may allow:

- aggressive inlining,
    
- dead-code elimination,
    
- constant propagation,
    
- fewer indirect calls,
    
- fewer intermediate objects,
    
- simpler control flow.
    

The generated implementation can become very close to manually optimized, almost inline code.

The important point is that AI does not necessarily replace optimized source generation with slower generic code.

It may instead generate **even more specialized explicit code for the concrete application**.

## Convenience Generators Are More Exposed Than Infrastructure Libraries

Not every source generator is equally vulnerable to this change.

The strongest candidates for replacement are generators whose main purpose is avoiding repetitive application code:

```text
mapping
DTO conversion
builders
adapters
simple validators
API wrappers
binding
boilerplate
simple proxies
```

Their historical value often came from:

> You do not have to write these repetitive lines yourself.

If AI makes writing those lines nearly free, that value decreases.

More infrastructure-heavy generators are different.

Consider serialization.

A mature serializer must correctly handle issues such as:

- escaping,
    
- UTF-8 encoding,
    
- numerical formats,
    
- dates,
    
- polymorphism,
    
- nullability,
    
- collections,
    
- buffering,
    
- streaming,
    
- custom converters,
    
- standards compliance,
    
- security edge cases.
    

A mature library contains years of accumulated knowledge and testing.

Generating a few lines of serialization code is easy.

Reproducing the reliability of a mature serialization ecosystem is not.

Therefore the likely distinction is:

```text
AI can easily replace code-generation convenience.

AI is much less likely to replace accumulated infrastructure knowledge.
```

## Deterministic Source Generation Still Has Important Advantages

Source generators also retain a major property that LLMs do not naturally provide: determinism.

A traditional generator performs something close to:

```text
formal input
+ deterministic rules
→ predictable output
```

This makes it appropriate as part of every build.

AI works more like:

```text
context
+ instructions
+ model
→ plausible implementation
```

It is therefore more naturally part of the development process than the compilation process.

A healthy model may be:

```text
AI generates or updates code
↓
code is reviewed and committed
↓
normal deterministic build
↓
tests verify behavior
```

rather than calling an LLM during every compilation.

## Source Generators and AI Can Also Complement Each Other

This is not necessarily a replacement story.

A useful division may emerge:

```text
AI
→ understands intent and unusual requirements

source generator
→ performs formal repetitive transformation
```

For example, AI may determine the desired model and configuration, while a deterministic generator handles the mechanical implementation.

Another possibility is:

```text
source generator handles 95% of cases
AI generates explicit code for the exceptional 5%
```

The boundary can be expressed simply:

> Source generators are excellent when code follows formal rules.

> LLMs are powerful when code follows human intent.

If the transformation is:

```text
schema → serializer
interface → proxy
type metadata → generated registration code
```

a deterministic generator remains very attractive.

If the requirement is:

```text
map these models,
except this field has different business meaning,
legacy records behave differently,
and these three special cases must remain backward compatible
```

an LLM may have a substantial advantage.

## A Possible Future: Instructions Instead of Framework Features

This may eventually change what some developer tools look like.

Today a library often needs:

```text
API
+ configuration model
+ documentation
+ extension system
+ source generator
```

A future alternative may sometimes be:

```text
small runtime library
+
README with agent instructions
+
tests
```

The instructions explain how application-specific code should be generated.

Instead of waiting for the library to support another configuration option, the agent simply writes the additional explicit code.

This suggests a broader shift:

> A natural-language instruction for an agent may sometimes replace an API, DSL, configuration system, or source-generation feature.

The strongest libraries will therefore increasingly need to provide value beyond saved typing.

Their durable value will come from things such as:

- correctness,
    
- difficult algorithms,
    
- standards compliance,
    
- security,
    
- interoperability,
    
- accumulated edge-case handling,
    
- stable ownership,
    
- extensive testing.
    

Where the primary value is merely generating repetitive application code, AI-generated explicit implementations may become a surprisingly strong competitor.