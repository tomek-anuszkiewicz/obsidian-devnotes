---
title: AI Changes the Economics of Software Libraries
tags:
  - economics
  - software-engineering
  - open-source
  - libraries
  - ai-agents
  - code-generation
aliases:
  - Economics of Software Libraries
  - Build vs Buy vs Generate
---

# AI Changes the Economics of Software Libraries

> [!IMPORTANT]
> **Executive Summary & Architectural BLUF**:  
> For decades, the primary justification for pulling in an external open-source library was simple: *"I do not want to spend two weeks typing this code manually."* When AI coding agents reduce the marginal cost of code authoring to near zero, this fundamental economic calculation inverts.
> - **The Collapse of "Convenience" Libraries**: Libraries that exist merely to reduce syntactic boilerplate (mapping utilities, fluent builders, trivial wrappers, result types) transform from productivity boosters into **liability taxes**—introducing supply-chain risk, dependency conflicts, and version lock-in.
> - **The Enduring Moat: Hard Algorithmic Domain Truth**: Libraries survive and thrive only when they encapsulate deep domain physics, battle-tested cryptographic primitives, hardware-accelerated kernels, complex network protocol state machines, or formal regulatory compliance where local reinvention carries unacceptable liability.

### Comparative Matrix: The Economic Re-Evaluation of Software Libraries

| Dimension | Boilerplate & Convenience Libraries | Mid-Tier Utility Packages | Deep-Domain & Hard Substrate Libraries |
| :--- | :--- | :--- | :--- |
| **Pre-AI Rationale** | High adoption: Saved developers dozens of hours writing mechanical glue code. | Moderate adoption: Standardized team patterns across multiple services. | Mandatory adoption: Impossible or reckless to implement independently. |
| **Agentic Era Viability** | **Rapidly Obsolete**: Generated inline as explicit, zero-dependency, local domain code. | **Heavy Scrutiny**: Kept only if cross-service protocol contracts require strict runtime parity. | **Indispensable**: Cryptographic engines, SQLite engines, AV1 codecs, TLS stacks. |
| **Dependency Tax vs. Benefit** | **Negative ROI**: Supply-chain vulnerabilities and framework upgrade breaking changes exceed value. | **Neutral/Fragile ROI**: High blast-radius when version drift fractures microservices. | **Massively Positive ROI**: Hundreds of person-years of edge-case hardening in physical reality. |
| **Agent Interaction** | Agent writes custom, unrolled, compiler-friendly local implementation in 3 seconds. | Agent writes integration glue around package APIs. | Agent generates safe, typed FFI/IPC bindings against the rock-solid C/Rust kernel. |
| **Maintenance Burden** | Zero external maintenance; localized blast radius. | Continuous dependency updating and semantic version bump churn. | Isolated to stable vendor patch releases and security advisories. |

---

AI code generation does not necessarily make software libraries obsolete.

It changes the reason for using them.

Historically, one of the strongest arguments for a library was simple:

> I do not want to write this code myself.

If an agent can generate hundreds or even thousands of lines of local code cheaply, that argument becomes much weaker, altering the balance between [[Internal Shared Packages vs Agent-Generated Code|internal packages vs agent-generated code]].

The more important question becomes:

> Do we want to own and maintain this implementation ourselves?

This directly influences how organizations manage [[Designing Internal Packages as an Explicit, Composable Framework|internal libraries as composable frameworks]] and reshape the software ecosystem.

## Libraries That Mainly Save Typing Are Under Pressure

Some libraries exist primarily to reduce boilerplate, but when code is disposable, maintaining external dependencies can silently compound [[Software Entropy and the Zero-Friction Trap|software entropy]].

Examples may include:

- simple validation frameworks,
    
- mapping helpers,
    
- small wrappers,
    
- fluent APIs,
    
- trivial retry helpers,
    
- convenience abstractions,
    
- simple result types,
    
- lightweight formatting or parsing utilities.
    

Historically, writing the equivalent code manually had a meaningful cost.

With agents, that cost may become negligible.

Instead of introducing a dependency, an agent may generate a narrow implementation tailored exactly to the application.

This changes an old productivity assumption:

```text
more abstraction
→ less code
→ higher productivity
```

into something closer to:

```text
more explicit local code
→ easier agent reasoning
→ fewer dependencies
→ easier customization
```

The number of lines of code may become much less important than before.

## Validation Is a Good Example

A validation library may allow something concise such as:

```csharp
RuleFor(x => x.Email)
    .NotEmpty()
    .EmailAddress();
```

An agent can instead generate explicit application code:

```csharp
if (string.IsNullOrWhiteSpace(request.Email))
    return Error.EmailRequired;

if (!EmailValidator.IsValid(request.Email))
    return Error.InvalidEmail;
```

The second version may be longer, but that may matter much less if nobody had to type it manually.

It may also be easier for future agents to understand and modify because the behavior is explicit and local.

The important question therefore becomes:

> What does the library provide beyond reducing the amount of code?

If the answer is "not much", the dependency becomes easier to question.

## Test Libraries May Face a Similar Change

Mocking frameworks are another interesting example.

A framework can make a test double concise:

```csharp
var repo = new Mock<IRepository>();
repo.Setup(x => x.Get(123)).Returns(customer);
```

But an agent can cheaply generate an explicit fake:

```csharp
public sealed class CustomerRepositoryFake : IRepository
{
    public Customer? Result { get; set; }

    public Customer? Get(int id) => Result;
}
```

Explicit fakes may have several advantages:

- they are ordinary code;
    
- debugging is straightforward;
    
- there is less reflection or proxy magic;
    
- agents can reason about them easily;
    
- domain-specific behavior is simple to add;
    
- there is no coupling to a mocking framework.
    

Mock libraries will not necessarily disappear.

However, one of their historical advantages — avoiding tedious hand-written test doubles — becomes much weaker.

The same may apply to:

- fixture builders,
    
- test-data helpers,
    
- small assertion libraries,
    
- test setup DSLs.
    

## Some Libraries Remain Extremely Valuable

A completely different class of libraries derives its value from accumulated engineering knowledge.

SQLite is a good example.

An agent could theoretically be asked to write an embedded relational database, but that misses the point.

The value of SQLite includes:

- decades of testing,
    
- crash recovery,
    
- ACID guarantees,
    
- locking behavior,
    
- query optimization,
    
- storage format stability,
    
- performance tuning,
    
- interoperability,
    
- enormous numbers of edge cases.
    

The same logic applies to areas such as:

- cryptography,
    
- TLS,
    
- database engines,
    
- database drivers,
    
- HTTP stacks,
    
- compression,
    
- media codecs,
    
- complex standards parsers,
    
- distributed consensus,
    
- serialization formats.
    

In these cases, the hard part is not producing code.

The hard part is knowing whether the implementation is correct.

## Cost of Creation and Cost of Ownership Diverge

AI dramatically reduces the cost of creating software.

It does not eliminate the cost of owning it.

A locally generated replacement becomes:

```text
our code
our bugs
our vulnerabilities
our compatibility problem
our migration problem
our support burden
```

This suggests that one of the most important questions in future dependency decisions will be:

> Do we want to own this problem for the next ten years?

AI reduces:

```text
cost of creation
```

much more than it reduces:

```text
cost of verification
cost of maintenance
cost of compatibility
cost of responsibility
```

This distinction may become more important than the number of lines saved by a dependency.

## Popular Libraries Benefit From Distributed Testing

Widely used libraries gain another advantage:

```text
millions of deployments
→ unusual edge cases discovered
→ fixes contributed
→ everyone benefits
```

A private implementation is tested mainly against the cases encountered by one organization.

AI can fix a bug quickly once it is discovered.

It cannot automatically provide the accumulated operational experience of millions of other deployments.

This is one of the strongest forms of value created by mature ecosystems.

## Tooling and Ecosystem Matter

A mature library is often more than its source code.

It may come with:

- documentation,
    
- IDE support,
    
- analyzers,
    
- debugging tools,
    
- profiling support,
    
- telemetry integrations,
    
- community knowledge,
    
- examples,
    
- compatibility layers,
    
- third-party integrations.
    

An agent can generate a retry mechanism quickly.

It cannot instantly recreate the surrounding ecosystem that a mature resilience library may already have.

## Sometimes We Want a Canonical Implementation

There are also areas where creativity is undesirable.

Examples include:

- URL encoding,
    
- Unicode normalization,
    
- date and time handling,
    
- JWT parsing,
    
- SQL escaping,
    
- HTTP semantics,
    
- cryptographic primitives.
    

A locally generated implementation may look reasonable while still being subtly incorrect.

In such areas, "almost correct" can be worse than obviously incomplete.

A trusted library serves as a canonical implementation of complex semantics.

## Generated Code May Sometimes Be Faster

It is easy to assume that mature libraries will always outperform agent-generated code because they contain years of optimization.

That can be true, especially for complex infrastructure.

But the opposite can also happen.

Generic libraries often need to support:

- many configuration options,
    
- multiple execution paths,
    
- abstractions,
    
- reflection,
    
- dynamic dispatch,
    
- expression trees,
    
- adapters,
    
- extensibility hooks,
    
- compatibility layers.
    

A generated implementation can know the exact use case in advance.

It may therefore remove entire layers of indirection.

Instead of a generic pipeline such as:

```text
application
→ abstraction
→ configuration
→ reflection
→ generic dispatcher
→ actual operation
```

an agent may generate something much closer to:

```text
application
→ actual operation
```

The resulting code may be almost inline.

This can provide advantages such as:

- fewer allocations,
    
- fewer virtual calls,
    
- less reflection,
    
- fewer branches,
    
- simpler data flow,
    
- better opportunities for compiler inlining,
    
- easier optimization by the JIT or native compiler.
    

This is especially interesting because abstraction historically had a human productivity benefit.

If agents remove much of the cost of writing repetitive explicit code, some abstraction may no longer be worth its runtime or cognitive cost.

The future tradeoff may therefore be:

```text
generic reusable implementation
vs
generated specialized implementation
```

rather than simply:

```text
slow custom code
vs
optimized library
```

Mature libraries will still dominate when their performance comes from deep algorithmic knowledge, careful low-level optimization, or years of profiling.

But generated code may perform surprisingly well when the main overhead of a library comes from generality.

## Compliance, Certification, and Liability Matter

In some domains, correctness alone is not enough.

Organizations may also care about:

- certification,
    
- security review,
    
- compliance,
    
- vendor support,
    
- contractual guarantees,
    
- liability.
    

This is especially relevant in areas such as:

- payments,
    
- identity,
    
- healthcare,
    
- cryptography,
    
- accounting,
    
- safety-critical systems.
    

"We generated our own implementation" may be technically possible while remaining organizationally unacceptable.

Sometimes a library is purchased partly because someone else is willing to stand behind it.

## AI May Change Forking and Customization

Today, when a library almost fits a use case, teams often:

```text
configure it
→ wrap it
→ extend it
→ fork it
```

With agents, another option becomes practical:

```text
study the required behavior
→ generate a narrow implementation
```

This may especially affect libraries whose APIs have become complicated mainly because they must support every imaginable use case.

A small application may prefer a generated implementation of the 10% of functionality it actually needs.

## Open Source May Become More Valuable as Knowledge

Open-source libraries may gain another role.

They are not only reusable packages.

They are also repositories of tested engineering knowledge.

Agents can use open-source code to:

- understand edge cases,
    
- explain behavior,
    
- generate adapters,
    
- prepare patches,
    
- study implementation strategies,
    
- port ideas to another platform.
    

The value of open source may therefore shift partly from:

```text
reusable binary
```

toward:

```text
reusable knowledge
+ tested implementation
```

## Agents May Actually Increase the Value of Good Libraries

Libraries and generated code are not necessarily competitors.

A well-documented, predictable library can be an excellent primitive for an agent.

For an agent:

```text
Use library X to perform Y
```

is often a more reliable task than:

```text
Invent an implementation of Y and correctly handle every relevant edge case.
```

The most mature libraries may therefore become even more useful because agents can compose them efficiently.

## The Library Ecosystem May Polarize

The ecosystem may gradually separate into different classes:

```text
tiny convenience dependency
        ↓
generate locally

small generic abstraction
        ↓
often questionable

medium complex library
        ↓
case by case

mature infrastructure component
        ↓
use established implementation

critical infrastructure
        ↓
strong preference for trusted ownership
```

The middle of the ecosystem may come under the most pressure.

Very small abstractions become cheap to generate.

Very complex components remain expensive to verify and maintain.

## Paid Libraries Face a New Competitive Pressure

AI also lowers the cost of reimplementing functionality from commercial libraries.

Suppose a company pays for a library providing:

```text
A
B
C
D
```

but only uses:

```text
A
B
```

Previously, rebuilding those capabilities may have been economically irrational.

With agents, the company may decide that a narrow internal implementation is cheaper than continuing to pay the license fee.

This weakens a traditional moat:

> We wrote a large amount of code, therefore reproducing the product is too expensive.

The strongest commercial defenses increasingly become things such as:

- continuous maintenance,
    
- support,
    
- certification,
    
- proprietary data,
    
- ecosystem effects,
    
- integrations,
    
- cloud services,
    
- legal guarantees,
    
- security expertise,
    
- trust,
    
- deep domain knowledge.
    

The raw amount of code becomes a weaker barrier.

There is, however, an important legal distinction between implementing similar functionality and copying a protected implementation.

Licenses, copyright, patents, trade secrets, and the way the original implementation was accessed still matter.

AI lowers the economic cost of reimplementation.

It does not remove intellectual-property law.

## A Better Mental Model

The future distinction may not primarily be:

```text
library
vs
custom code
```

It may instead be:

```text
commodity code
vs
accumulated knowledge
```

AI dramatically reduces the value of commodity code.

It reduces the value of accumulated knowledge much less.

This leads to a broader conclusion:

> AI does not make libraries obsolete. It changes the reason for using them.

Historically, a common reason was:

> I do not want to write this code.

Increasingly, the stronger reason may be:

> I do not want to own this problem.

That shift may become one of the most important changes in how software dependencies are evaluated in the age of AI agents.
---

## Relationship to the Knowledge Graph

- **[[Designing Internal Packages as an Explicit, Composable Framework]]**: Re-evaluating shared library architecture when code generation is cheap.
- **[[Internal Shared Packages vs Agent-Generated Code]]**: The trade-off between pulling a shared dependency and letting agents generate self-contained code.
- **[[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]**: Why third-party black-box libraries can hinder agentic reasoning.
- **[[Software Entropy and the Zero-Friction Trap]]**: Using localized duplication rather than heavy external libraries to limit blast radius.
- **[[AI May Create a New Market for Small, Custom Business Software]]**: How cheap implementation enables bespoke, zero-dependency software solutions.
