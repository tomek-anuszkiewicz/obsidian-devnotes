---
title: Software Engineering May Shift Toward Code Optimized for Agents
tags:
  - software-engineering
  - ai-agents
  - software-architecture
  - code-style
  - maintainability
  - developer-experience
aliases:
  - Agent-Optimized Codebases
  - Designing Code for LLM Maintainers
---

As LLMs and coding agents generate a growing share of software, an important question emerges:

> What does "good code" mean when humans are no longer its primary authors and maintainers?

This may affect not only how code is generated, but also architecture—driving the need for [[Designing Software for AI Agents|designing software specifically for AI agents]]—as well as team habits, code review, and the long-term evolution of software systems.

## What an LLM Generates Without Guidelines

If an LLM receives no project-specific guidance, it does not search for an objectively optimal solution; this makes [[In-Flight Documentation as the Primary Framework for Coding Agents|in-flight documentation]] critical for anchoring model behavior.

A better mental model is:

```text
common training patterns
+ framework conventions
+ documentation examples
+ model tuning toward clarity and safety
+ prompt context
→ generated solution
```

The result will often resemble a mainstream, idiomatic, broadly accepted solution.

For example, when asked to implement a feature in ASP.NET Core, the model may naturally prefer familiar patterns such as:

- dependency injection,
    
- async/await,
    
- EF Core,
    
- controllers or Minimal APIs,
    
- standard DTOs,
    
- common validation approaches.
    

This is not necessarily because these choices are universally best.

They are simply strong defaults available to the model.

Without additional context, asking an agent to implement something effectively means navigating opaque indirections, proving why [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code|hidden abstractions become more expensive in agent-maintained code]]. Specifically:

> Use your existing priors and fill in the missing architectural decisions yourself.

This is important because the model may produce something locally reasonable while violating assumptions that exist only inside the organization, rapidly exacerbating [[Software Entropy and the Zero-Friction Trap|software entropy]].

## Mainstream Code Has a Built-In Advantage

Consider two systems.

System A uses common patterns.

System B uses unusual internal libraries, custom infrastructure, and organization-specific conventions.

An agent may successfully generate code for either system if it receives good instructions.

However, there is an asymmetry when the code must later be analyzed or modified.

For a mainstream system:

```text
existing code
+ model's prior knowledge
→ substantial understanding
```

For a highly custom system:

```text
existing code
+ weak prior knowledge
→ incomplete understanding
```

The model can often infer the purpose of standard patterns because it has encountered similar structures many times.

With custom infrastructure, it may see what the code does without understanding why the architecture exists.

## The Training Paradox: Agents Must Code Differently Than the Humans Who Trained Them

This creates a fundamental contradiction:

> **Agents should program differently than humans, but they were trained almost exclusively on code written by humans.**

Human code was molded by human biological constraints:
- **Typing fatigue and mental drag**: Humans invented complex inheritance trees, meta-programming, and generic framework layers largely to avoid typing repetitive code.
- **Fear of duplication**: Humans dogmatized DRY because humans forget to update multiple copies and hate repetitive maintenance.

Agents operate under entirely different economics:
- Zero typing fatigue, instant search and mass-refactoring, but severe vulnerability to deep indirection, magic conventions, and hidden side effects.
- Optimal agent-native code is **explicit, flat, locally duplicated, and mechanically isolated** (e.g. 1:1 file-to-operation hierarchy with hard line limits).

However, because models are pre-trained on human repositories, their default prior is to emulate human patterns: creating speculative interfaces, unnecessary wrappers, and centralized abstractions. Without explicit architectural guidelines and mechanical constraints, agents naturally fall into the trap of writing code optimized for human typing rather than agentic reliability.

## Guidelines Are Not Only Generation Instructions

This leads to an important conclusion:

> Guidelines can influence how future agents interpret existing code, not only how they generate new code.

Suppose an organization has a custom operation runner:

```csharp
await operation.ExecuteAsync(
    context,
    policy: Policies.CustomerMutation);
```

The agent may observe that this pattern is common.

But it may not know that the call also establishes:

```text
authorization
+ transaction boundaries
+ tenant context
+ auditing
+ event publication
+ retry behavior
```

Without that knowledge, it may eventually bypass the abstraction and call the database directly.

A guideline such as:

```text
All business mutations must execute through OperationRunner.

OperationRunner establishes authorization, transaction boundaries,
tenant context, auditing and event publication.

Direct persistence from application code is forbidden.
```

changes more than generation behavior.

It changes the agent's interpretation of the surrounding code.

Something that previously looked like unnecessary ceremony now becomes an architectural invariant.

## Guidelines Can Shape the Future Evolution of the System

This means architectural instructions may become part of the system itself.

Traditionally, documentation often described:

> How we write software here.

For agents it can additionally mean:

> How future agents should interpret and evolve this software.

Source code explains the current state.

Guidelines explain the intended direction.

Rationale explains how to generalize the rule when a new situation appears.

A particularly useful format may therefore be:

```text
We optimize for X because Y.

Therefore prefer A over B.

Exception: C.
```

rather than only:

```text
DO A.
DON'T DO B.
```

The rationale gives the agent enough semantic context to reason about cases that were not explicitly documented.

## Agent-Friendly Does Not Mean Mainstream

A custom architecture is not necessarily bad for agents.

The more important distinction may be:

```text
regular vs irregular
explicit vs implicit
documented vs tribal
predictable vs exception-heavy
```

A highly unusual architecture can still be easy for agents if it has:

- stable rules,
    
- consistent structure,
    
- clear boundaries,
    
- canonical examples,
    
- explicit rationale,
    
- few undocumented exceptions.
    

Conversely, a mainstream architecture can become difficult if years of inconsistent changes create multiple competing patterns.

A useful principle is:

> Agent-friendly code is not necessarily standard code. It is code whose rules are easy to infer and remain stable.

## Team Habits Become Part of the Model Context

Formal guidelines are only one source of information.

Agents also learn the local development culture from the repository itself.

In practice, their effective context may be:

```text
formal guidelines
+ existing code
+ naming conventions
+ folder structure
+ repeated architectural decisions
+ tests
+ examples
+ review outcomes
→ local programming culture
```

This makes team habits extremely important.

If a team consistently prefers:

- explicit dependencies,
    
- simple methods,
    
- stable module boundaries,
    
- similar solutions for similar problems,
    
- limited hidden behavior,
    

the repository becomes easy to extrapolate from.

If instead the project contains:

```text
multiple ways of solving the same problem
+ historical layers
+ ad-hoc abstractions
+ undocumented exceptions
+ old and new styles mixed together
```

the agent receives contradictory evidence.

The problem is no longer simply that the AI is weak.

The repository itself does not clearly answer:

> How should software be written here?

## A New Form of Context Debt

This suggests a new type of technical debt.

Beyond code debt and documentation debt, organizations may accumulate:

```text
context debt
```

or:

```text
agent comprehension debt
```

A system may work perfectly while being difficult for agents to modify because important meaning exists only in the heads of experienced employees.

For example:

```text
Never call X from Y.
```

If this rule survives only as tribal knowledge, an agent entering the repository has no reliable way to discover it.

In an agent-heavy environment, architecture knowledge may increasingly need to exist as repository-accessible context.

## Humans May Need to Adapt to Agent-Generated Code

An even deeper possibility is that the agent should not always adapt to human coding preferences.

Humans may need to adapt some of their expectations to code that is easier for agents to generate, analyze, and modify.

Traditional software engineering evolved around human limitations.

Humans benefit from:

- fewer lines of code,
    
- reduced repetition,
    
- abstractions that compress recurring behavior,
    
- familiar idioms,
    
- structures that reduce manual editing.
    

Agents have a different cost model.

Generating another 100 explicit lines may be almost free.

As a result, an agent may sometimes prefer code that humans consider verbose.

For example:

```csharp
foreach (var order in orders)
{
    if (!IsEligible(order))
        continue;

    var normalized = Normalize(order);

    if (normalized.Amount <= 0)
        continue;

    validOrders.Add(normalized);
}
```

instead of a compact LINQ pipeline.

Or it may place 20 lines of validation directly at the beginning of a function instead of hiding them behind a generic validator.

From a traditional human perspective, this may look repetitive or unsophisticated.

From an agent perspective, the benefits may include:

- explicit control flow,
    
- local semantics,
    
- easy insertion of new conditions,
    
- simpler debugging,
    
- simpler instrumentation,
    
- fewer hidden abstractions,
    
- easier automated transformation.
    

## More Code May No Longer Mean More Maintenance Cost

Historically, an approximate relationship existed:

```text
more code
→ more typing
→ more code to read
→ more manual maintenance
→ higher cost
```

Agentic development weakens this relationship.

Sometimes the new relationship may be closer to:

```text
more explicit code
→ negligible generation cost
→ easier local reasoning
→ easier automated modification
```

This does not mean duplication becomes free.

If a business rule is copied into 100 places and later must change consistently, the duplication still creates risk.

However, duplication in the agentic era gains three decisive architectural advantages:
1. **Guaranteed minimal blast radius**: When logic is duplicated locally inside each operation rather than shared via a fragile common abstraction, modifying Operation A physically cannot break Operation B.
2. **Effortless synchronization**: LLM agents can search the entire repository, identify all semantic duplicates in seconds, and update them consistently.
3. **No typing or cognitive drag**: Generating or modifying 10 specialized, self-contained implementations costs an agent no more effort than modifying a single shared framework.

Instead of asking:

> Is this duplicated?

we now ask:

> Does this duplication create unmanageable synchronization risk, or does it safely isolate the blast radius?

In many cases, **isolated blast radius is vastly superior to the hidden coupling of shared abstractions.**

## Some Traditional Best Practices May Need Re-Evaluation

Many engineering practices were optimized partly for human authoring cost.

For example:

```text
DRY at all costs
```

may become something closer to:

```text
avoid dangerous semantic duplication,
but prefer local explicitness when abstraction creates hidden behavior
```

Likewise, a team that historically created a shared abstraction after seeing the same code three times may reconsider.

Instead of:

```text
repeat three times
→ create framework
```

the future workflow may be:

```text
repeat three times
→ ask whether the duplication creates real synchronization risk
→ abstract only if the abstraction reduces semantic complexity
```

This could lead to more:

- generated inline code,
    
- explicit loops,
    
- direct control flow,
    
- specialized implementations,
    
- fewer generic frameworks,
    
- fewer reflection-heavy abstractions.
    

The source code may become larger while remaining easier for agents to evolve.

## Human Review Becomes the Meeting Point of Two Worlds

This creates tension during code review.

The agent may implicitly optimize for:

```text
correctness
local explicitness
predictability
easy transformation
low hidden coupling
performance
```

while the human reviewer may instinctively optimize for:

```text
brevity
elegance
familiar idioms
low visible duplication
abstraction
human reading comfort
```

These priorities overlap, but they are not identical.

This explains a common modern reaction to AI-generated code:

> This is bad code. I could write it better.

Sometimes that is true.

The generated code may genuinely contain:

- poor complexity,
    
- unnecessary allocations,
    
- excessive I/O,
    
- security problems,
    
- incorrect concurrency,
    
- duplicated business rules,
    
- architectural violations.
    

But sometimes "better" only means:

```text
shorter
more idiomatic
more abstract
closer to how I personally write code
```

That distinction becomes increasingly important.

## "Not Optimal" Must Mean Something Concrete

When reviewing agent-generated code, saying that something is "not optimal" is insufficient.

The question should be:

> Not optimal according to which objective?

Real problems remain real:

- O(n²) where O(n) is practical,
    
- unnecessary database round trips,
    
- excessive allocations on a hot path,
    
- broken authorization boundaries,
    
- inconsistent business behavior,
    
- hidden coupling,
    
- difficult migrations,
    
- unpredictable side effects.
    

But objections such as:

```text
20 lines instead of 8
foreach instead of LINQ
explicit validation instead of a fluent framework
local implementation instead of generic abstraction
```

need additional justification.

They may still be wrong choices.

But they are not automatically wrong merely because an experienced human would have written something more compact.

## Human Review Could Accidentally Reduce Agent-Friendliness

There is a particularly interesting failure mode:

```text
agent generates explicit code
↓
human reviewer sees duplication
↓
human extracts abstraction
↓
future agent must understand abstraction
↓
more hidden semantics appear
↓
system becomes harder for agents to modify
```

The human reviewer may believe they improved the code according to traditional standards while actually increasing the semantic distance between visible code and runtime behavior.

This does not mean abstractions are bad.

It means abstractions need to justify themselves through actual reduction of complexity, not merely reduction of line count.

## Code Review May Shift Toward Consequences

A future review may ask less often:

> Would I personally write it this way?

and more often:

- Is the behavior correct?
    
- Are the invariants preserved?
    
- Are security boundaries respected?
    
- Are side effects obvious?
    
- Is data flow understandable?
    
- Does duplication create synchronization risk?
    
- Does the abstraction genuinely simplify reasoning?
    
- Can future agents safely modify this area?
    
- Are tests sufficient to constrain future transformations?
    

This moves review from style policing toward verification of intent and consequences.

## Source Code May No Longer Be Primarily for Human Authors

The traditional model is:

```text
human writes
→ human reads
→ human modifies
```

An increasingly common future model may be:

```text
human specifies
→ agent writes
→ human validates
→ agent modifies
```

If this becomes dominant, source code still needs to remain understandable to humans.

But it may no longer need to be optimized primarily for the experience of manually writing and editing every line.

This resembles, in a limited way, how developers already treat compiler-generated output.

We do not manually rewrite generated IL because it is aesthetically unpleasant.

Its purpose is different.

Source code will not become machine code, but part of it may gradually move in the same direction:

> human-auditable, but primarily machine-produced and machine-modified.

## The Emerging Design Goal

The future optimization target may therefore become:

```text
human understanding
+ agent understanding
+ agent modification
+ predictable future generation
```

rather than exclusively:

```text
human readability
+ human typing efficiency
```

A useful principle may be:

> Generate code optimized for machines to evolve, while keeping its intent auditable by humans.

This does not justify arbitrary generated complexity.

It suggests that some traditional aesthetic preferences may become less important, while explicitness, regularity, semantic locality, and machine-legible architecture become more important.

## The Deeper Shift

The largest change brought by coding agents may not be that software can be written faster.

It may be that we gradually change:

- what we consider good source code,
    
- which abstractions we create,
    
- how much duplication we tolerate,
    
- how architecture is documented,
    
- how teams establish conventions,
    
- what code reviewers optimize for,
    
- and ultimately who source code is designed for.
    

In this world, guidelines are not merely style rules.

They are part of the mechanism that shapes future software evolution.

Team habits are not merely culture.

They become training signals available inside the repository.

And human review is not simply a final aesthetic check.

It becomes the boundary where human intent is reconciled with code increasingly optimized for machine generation and machine modification.
---

## Relationship to the Knowledge Graph

- **[[Designing Software for AI Agents]]**: Core heuristics for architecting software for agent discoverability and deterministic verification.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Replacing heavy code scaffolding with in-flight documentation as the primary agent framework.
- **[[Software Entropy and the Zero-Friction Trap]]**: The emergence of agent-native defaults (flat 1:1 hierarchy, localized duplication) to combat entropy.
- **[[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]**: Why non-local, implicit behaviors become technical liabilities in agentic repos.
- **[[AI May Replace Some Source Generators with Explicit Generated Code]]**: Replacing complex offline code generators with explicit, agent-maintained source code.
- **[[Comments May Become More Valuable in AI-Generated Code]]**: How explanatory comments protect intentional non-standard business logic from agentic flattening.
- **[[AI Changes the Role and Training of Software Engineers]]**: The cognitive inversion and new role of engineers as architects and verification controllers.
