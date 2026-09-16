---
title: AI May Replace Some Source Generators with Explicit Generated Code
tags:
  - ai-agents
  - software-engineering
  - source-generators
  - metaprogramming
  - object-mapping
  - boilerplate
  - maintainability
  - clean-code
aliases:
  - AI May Replace Some Source Generators with Explicit Generated Code
  - Source Generators vs AI Code Generation
  - Explicit Generated Code with AI
  - Replacing Source Generators with LLMs
  - The Economics of Explicit Code
  - Convenience Generators vs Infrastructure Libraries
---

# AI May Replace Some Source Generators with Explicit Generated Code

Source generation solves a well-understood engineering problem: it allows libraries to replace slow, generic runtime mechanisms with specialized, type-safe code generated at compile time.

In ecosystems like C# (Roslyn source generators), Java (annotation processors), and Go (`go generate`), generators are routinely used for:

- Serialization and deserialization,
- Object-to-object mapping and DTO projections,
- Strongly typed API clients and RPC stubs,
- Dependency injection container wiring,
- Validation pipelines,
- Boilerplate design patterns (builders, factories, fluent interfaces),
- Strongly typed wrappers over loose data structures.

Their runtime performance is typically stellar because the generated output bypasses the performance tax of traditional enterprise abstractions:

- Zero reflection,
- Direct invocation instead of dynamic dispatch,
- Zero runtime metadata lookups or dictionary scans,
- Elimination of boxed generic abstractions,
- Minimal intermediate object allocations.

Instead of executing an opaque, one-size-fits-all runtime engine, the application executes straight-line code specialized for a concrete type.

```text
generic library
+ configuration / attributes
+ deterministic source generator
→ specialized compile-time code
```

Coding agents introduce an alternative path to the exact same specialization:

```text
requirements
+ existing code context
+ conventions
+ automated tests
+ LLM
→ explicit specialized code
```

The critical difference between these two approaches is not runtime performance. It is the **cost of expressing unusual requirements**.

---

## The Hidden Cost of Source Generators Is Their Configuration Model

A compile-time source generator must ingest requirements through a formally designed interface. Over time, that interface almost always expands into an intricate configuration surface:

```text
attributes
+ conventions
+ fluent configuration APIs
+ custom converters
+ compile-time extension points
+ escape hatches and overrides
+ special-case handling
```

Every single capability of a generator must first be anticipated, designed, implemented, tested, and shipped by the library author. 

When your business logic hits a scenario the library author didn't foresee, you hit a hard engineering bottleneck:

```text
user requirement
→ open issue on GitHub
→ wait for library author to design new configuration API
→ wait for generator to implement AST transform
→ test permutations against compiler versions
→ document the new behavior
→ release new package version
→ update dependency and configure it in the application
```

This dynamic creates an unavoidable ceiling. Every seasoned engineer has hit the familiar wall in documentation:

```text
not supported
planned for vNext
requires a custom converter plugin
workaround: drop down to manual code
```

A generator cannot produce an AST it was never taught to express.

---

## LLMs Operate Under a Different Constraint

An LLM does not need an exhaustive domain-specific language (DSL) to navigate edge cases. A developer can describe domain requirements directly, combining business rules, edge cases, and backward-compatibility quirks in plain terms:

```text
Map Order to OrderDto.

Use Customer.DisplayName as CustomerName.
Default Currency to EUR when it is missing.
Ignore InternalComment.
For legacy orders created before 2024,
calculate Total using the legacy formula.
```

The resulting implementation is completely straightforward:

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

For a traditional generator or mapping library, supporting that legacy condition might require an entirely new fluent hook, an attribute-based custom resolver, or abandoning the generator altogether for that model.

For an agent, it requires a single ternary operator in the generated assignment.

This creates a fundamental asymmetry:

```text
Source generator:
new requirement → new abstraction, DSL feature, or configuration hook

AI-generated code:
new requirement → a slightly different explicit implementation
```

---

## Flexible Authoring Can Produce Extremely Simple Runtime Code

One of the most practical properties of this pattern is that high flexibility during development does not require complex machinery at runtime.

The authoring environment can be fluid and dynamic:

```text
natural language instructions
+ existing codebase context
+ unit and contract tests
+ coding agent
```

While the resulting artifact in your repository remains boring, explicit, and direct:

```csharp
if (order.IsExpedited)
{
    dto.Priority = PriorityLevel.High;
}
```

There is no need for:
- Runtime reflection,
- An intermediary mapping engine,
- A dynamic rule interpreter,
- An opaque configuration DSL,
- An AI model running in your production environment,
- Or even an external runtime library dependency.

The cognitive load and edge-case resolution happen during the authoring step. The production environment simply executes ordinary, readable, high-performance code.

```text
very flexible authoring
+
very explicit implementation
+
very simple runtime
```

---

## AI Can Remove Both Runtime and Compile-Time Abstractions

Historically, backend architectures evolved along a clear path:

```text
runtime reflection abstraction
        ↓
compile-time specialization
        ↓
custom source generator
```

For example, a reflection-heavy object mapper (like classic AutoMapper) was replaced by a compile-time source generator (like Mapster or Mapperly) to strip away runtime reflection overhead.

Coding agents introduce another step in this progression:

```text
runtime abstraction
        ↓
source generator
        ↓
AI-generated explicit code
```

A source generator removes the *runtime* abstraction by emitting specialized code behind the scenes during compilation. 

An agent can remove the **generator abstraction itself**.

Instead of pulling in a complex setup:

```text
mapping library
+ framework attributes
+ fluent configuration profiles
+ Roslyn generator package
→ synthetic generated mapper
```

The project simply contains:

```text
mapping requirements
+ agent instructions
→ Mapper.cs
```

The resulting file is committed directly to source control and treated as standard application code. It can be viewed, navigated, and debugged in any IDE without fighting generator cache synchronization, read-only decompiled symbols, or build-order dependencies.

---

## Explicit Code May Become Cheaper Than Abstraction

Historically, abstractions were justified because manual boilerplate was expensive to write and error-prone to maintain.

Writing hundreds of DTO mappings, builders, or adapter functions by hand was grueling work. A tired engineer updating property assignments across 40 models would inevitably introduce silent bugs: transposing fields, missing a null check, or forgetting an enum mapping.

Adopting a library that replaced:

```text
30 lines of repetitive procedural code
```

with:

```text
1 line of declarative configuration
```

was an obvious productivity win.

Agentic workflows invert that economic calculation:

```text
cost of maintaining an abstraction and its tooling
vs.
cost of generating and updating explicit code
```

If an agent can reliably draft, refactor, and update those 30 lines of explicit mapping code in seconds—verified immediately by a unit test—the balance shifts. 

Explicit implementations offer concrete systems advantages:
- **Instant debuggability**: Breakpoints land on exact lines of code; call stacks are shallow and direct.
- **Zero hidden behavior**: No magic convention lookups matching field names behind the scenes.
- **Zero tooling friction**: No generator plugin version mismatches across IDEs, CI runners, or compiler updates.
- **Trivial local overrides**: Handling a one-off special case requires editing an `if` statement, not inventing a plugin architecture.
- **Predictable compilation**: Plain code compiles everywhere, every time, without relying on synthetic Roslyn or AST hooks.

Paradoxically, agent-assisted workflows can result in codebases with:

```text
more physical lines of code
but
substantially less conceptual complexity
```

---

## Removing Abstractions Can Also Improve Performance

Explicit, straightforward code routinely outperforms generic abstractions simply because there are fewer layers between the source and the CPU.

Consider a generic call site:

```csharp
mapper.Map<OrderDto>(order);
```

Compare that with direct assignments emitted by an agent:

```csharp
var dto = new OrderDto(
    order.Id,
    order.Customer.Name,
    order.Items.Count,
    order.Total.Amount);
```

When code is written this directly, modern compilers (C2, Roslyn, LLVM) and JIT runtimes have full visibility into the execution path:
- The entire constructor call can be aggressively inlined,
- Dead fields and redundant conditional branches are eliminated at compile time,
- Constants propagate cleanly across method boundaries,
- There are no virtual call indirections or interface dispatch lookups,
- Zero intermediate allocations or transient arrays are generated to pass parameters.

The generated implementation sits as close to manually optimized, inline code as possible. AI does not have to substitute high-performance compile-time generators with slower generic runtimes; it can emit explicit, specialized code tailored to the exact domain context.

---

## Convenience Generators vs. Deep Infrastructure Libraries

Not every source generator is a candidate for replacement. The software landscape divides sharply between **convenience generation** and **deep infrastructure knowledge**.

```text
AI easily replaces code-generation convenience.
AI is much less likely to replace accumulated infrastructure knowledge.
```

### Convenience Generators (High Replacement Surface)
These exist primarily to save human developers from typing boilerplate:
- DTO mappers and entity projection,
- Builder and factory pattern generators,
- Simple CRUD wrappers and repository facades,
- Basic property change notifications (`INotifyPropertyChanged`),
- Trivial HTTP client wrappers over interfaces.

Their historical pitch was simple: *You don't have to write this tedious code yourself.* 

When the cost of writing and updating that code drops to zero, the maintenance burden of the generator plugin and its idiosyncratic DSL often outweighs its benefits.

### Deep Infrastructure Generators (Low Replacement Surface)
Now consider a high-performance JSON serializer, a Protobuf compiler, or a cryptographic code emitter.

A production-ready serialization engine (like `System.Text.Json` source generation or FlatBuffers) encapsulates years of hardened, low-level engineering:
- Escaping and sanitization edge cases,
- Direct UTF-8 byte stream parsing without string allocations,
- Cross-platform numerical and floating-point edge cases,
- ISO-8601 date parsing variations and timezone offsets,
- Polymorphic type discriminators,
- Unaligned memory reads and SIMD optimizations,
- Rigorous compliance with external RFCs and network specifications,
- Defense against serialization vulnerabilities (e.g., hash-collision DoS).

An agent can generate an object mapper in seconds. It cannot reliably improvise the edge-case coverage and hardware-level performance of an audited, battle-tested serialization engine.

| Category | Typical Tooling | Recommended Approach | Technical Rationale |
| :--- | :--- | :--- | :--- |
| **Convenience Boilerplate** | DTO mappers, builder patterns, simple API adapters | **Emit explicit application code** | Primary goal was saving developer keystrokes; business edge cases are far simpler to maintain in plain code. |
| **Formal Schema Compilers** | Protobuf, gRPC, OpenAPI stubs, FlatBuffers | **Retain deterministic generators** | Cross-language network boundaries demand bit-for-bit deterministic contracts derived from an authoritative schema. |
| **Deep Infrastructure** | High-performance serializers, crypto routines, regex engines | **Rely on mature core libraries** | Encapsulates decades of low-level optimization, memory safety audits, and strict RFC standards compliance. |

---

## Deterministic Builds vs. Development-Time Generation

Source generators retain one massive technical advantage over LLMs: **strict determinism**.

A traditional compiler generator runs a deterministic state machine:

```text
formal AST / schema
+ deterministic transformation rules
→ predictable, bit-for-bit identical output
```

Because of this, a source generator belongs cleanly inside the continuous compilation loop. It can run on every developer keystroke and every CI run with complete reproducibility.

An LLM behaves probabilistically:

```text
context
+ instructions
+ model weights
→ plausible implementation
```

Attempting to run an LLM as a step inside an automated build toolchain is a severe anti-pattern. Doing so introduces network latency, variable API costs, rate-limiting failures, and non-reproducible releases where identical source code produces divergent binaries.

The robust architecture keeps AI strictly in the authoring loop:

```text
PROVEN PATTERN: AI AT DEVELOPMENT TIME
Developer / Spec ──► Coding Agent ──► Explicit Source Code (Committed to Git)
                                                ↓
                                      Normal Compiler / Toolchain
                                                ↓
                                      Deterministic Test Suite & CI
```

The agent writes or refactors plain source code. The human reviews it. The code is committed to Git. From that point onward, the build pipeline remains completely deterministic, fast, and reproducible.

---

## Source Generators and AI Can Complement Each Other

This transition is not an absolute replacement. In practice, the two approaches often work well together:

1. **The 95/5 Split**: A deterministic source generator handles 95% of standard, uniform structures across a system. The agent writes explicit, specialized implementations for the messy 5% of legacy models or non-standard interfaces that break the generator's configuration model.
2. **Schema-First Generation**: An agent drafts and updates a formal schema (such as an OpenAPI specification or Protobuf definition) based on conversational product requirements, while a formal generator handles the strict mechanical translation of that schema into wire-level network code.

The clean separation of concerns comes down to this:

> **Source generators excel when code follows rigid, formal, uniform rules.**  
> **LLMs excel when code must accommodate messy, evolving human intent.**

If the problem is purely mechanical:
```text
protobuf schema → wire-format serializer
interface → dynamic proxy
class metadata → dependency injection registration
```
A deterministic generator remains the right tool for the job.

If the problem involves real-world business context:
```text
map these entities,
except this field maps differently based on user region,
legacy records require fallback calculations,
and three specific edge cases must remain backward-compatible
```
An explicit implementation produced by an agent will be far simpler to build, read, and maintain than wrestling with a generator's DSL.

---

## A Shift in Tooling: Instructions Instead of Framework Overhead

This shift will change how libraries and developer tools are designed.

Historically, a library author had to build and maintain an extensive footprint:

```text
Core API
+ complex configuration system
+ custom fluent DSL
+ extension points / plugin architecture
+ dedicated compile-time source generator
+ extensive documentation explaining configuration quirks
```

A modern alternative can be dramatically simpler:

```text
minimal runtime core
+
concise markdown instructions for agents
+
deterministic test suite
```

The instructions explain to the agent how specialized code should be constructed for the application. Instead of waiting for a library maintainer to build a configuration flag for a unique use case, the agent simply writes the necessary procedural code directly.

A natural-language instruction paired with an agent can often replace an entire layer of configuration DSLs, attributes, and generator plugins.

Because of this, developer tooling can no longer compete merely by saving human developers from typing boilerplate. The durable value of software libraries will increasingly reside where it belongs:
- Absolute correctness in difficult domains,
- Complex, non-trivial algorithms,
- Formal standards and protocol compliance,
- Hardened memory safety and security boundaries,
- Deep, low-level hardware optimizations,
- Exhaustive test suites and edge-case handling.

Where the primary role of a tool was simply saving keystrokes on repetitive application code, explicit implementations written by agents will increasingly prove simpler, faster, and far easier to maintain.

---

## Practical Rules for Engineering Teams

1. **Default to explicit procedural code over mapping frameworks**: Let agents generate and maintain direct, line-by-line conversion functions instead of pulling in reflection mappers or specialized generator plugins to handle simple DTO transformations.
2. **Commit generated code to source control**: Treat agent-authored code as standard application source. It should be tracked in Git, reviewed in pull requests, and easily indexed by standard IDEs.
3. **Never place an LLM inside the build loop**: CI/CD pipelines, compiler stages, and production release packaging must remain 100% deterministic and offline-capable. Keep AI generation in the local authoring workflow.
4. **Use tests to catch schema drift**: When using explicit mapping functions instead of compile-time AST generators, rely on automated contract and round-trip unit tests. If an entity field changes, a failing test provides an immediate, unambiguous signal for an agent to update the mapping.
5. **Do not reinvent core infrastructure**: Use agents to write boilerplate application glue, business logic, and DTO projections. Continue to rely on battle-tested, audited third-party libraries for serialization, cryptography, protocol negotiation, and storage.

---

## Related Notes

- [[Software Engineering May Shift Toward Code Optimized for Agents]]
- [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]
- [[AI May Make Aggressive Code Optimization Economically Viable]]
- [[In-Flight Documentation as the Primary Framework for Coding Agents]]
- [[Programming Languages May Evolve Differently in the Age of AI]]
- [[Testing in the Model, Agent, LLM Era]]
