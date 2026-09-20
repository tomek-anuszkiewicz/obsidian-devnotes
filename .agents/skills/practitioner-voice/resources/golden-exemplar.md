---
title: "Golden Exemplar: Software Engineering May Shift Toward Code Optimized for Agents"
description: "Canonical reference essay defining the benchmark for cadence, pacing, aphoristic clarity, lightweight ASCII flow, and thesis-driven headings in practitioner writing."
role: golden-exemplar
---

# Golden Exemplar: The Essayist Standard

This document serves as the absolute stylistic and rhetorical benchmark for notes across this vault. It illustrates the caliber of an essay written by an elite practitioner (in the tradition of Martin Fowler, Paul Graham, Rich Hickey, or Kent Beck).

Key hallmarks to observe:
1. **Immediate Punch (No Fluff)**: The opening rejects platitudes in three sentences: *"The interesting question is not whether coding agents can generate more code than a human can type. They obviously can. The deeper question is..."*
2. **Thesis-Driven Headings**: Every header states an active engineering insight (`1. The Main Shift: Reduce Human Friction Less, Reduce Machine Ambiguity More`), never a passive category label.
3. **Pacing & Restraint**: Short paragraphs (1–3 sentences) that allow ideas to breathe without suffocating the reader with redundant elaboration.
4. **Aphoristic Anchors**: High-signal mental models that stick permanently (*"The repository is also the memory of the engineering team"*, *"Agents are not paid by the character"*).
5. **Lightweight Vertical ASCII Flow**: Minimalist diagrams using down-arrows (`↓`) that guide the eye downward without heavy, distracting border boxes.
6. **Sober Anti-Dogmatism**: Grounding principles in real trade-offs and warning against over-optimizing for the trend (*"Do not optimize for agent convenience at the expense of runtime reality"*).

---

## The Exemplar Text

```markdown
title: "Software Engineering May Shift Toward Code Optimized for Agents"
tags:
  - software-engineering
  - ai-agents
  - software-architecture
  - code-style
  - maintainability
  - developer-experience
  - agentic-development
aliases:
  - "Software Engineering May Shift Toward Code Optimized for Agents"
  - "Optimizing Software Engineering and Code for Agents"
  - Agent-Optimized Codebases
  - Designing Code for LLM Maintainers
  - Source Code as a Machine-Maintained Artifact
  - The Deeper Shift in Software Engineering

# Software Engineering May Shift Toward Code Optimized for Agents

The interesting question is not whether coding agents can generate more code than a human can type.

They obviously can.

The deeper question is what happens to software engineering when the dominant loop for changing a production codebase becomes:

Human specifies
      ↓
Agent investigates
      ↓
Agent proposes / implements
      ↓
Human verifies
      ↓
Agent tests / repairs / refactors
      ↓
Human accepts

That loop changes the economics of source code.

For decades, software engineering optimized heavily around the limitations of human developers. We avoided repetitive code because humans had to type it. We built abstractions to reduce visual noise. We split code into small units because humans have limited working memory. We created conventions and framework magic to make common operations disappear from individual call sites.

Those decisions were often reasonable.

But some of their original benefits become less important when the developer is no longer typing most of the implementation. At the same time, some of their hidden costs become more important: indirection, fragmented context, implicit behavior, and architecture that is easy for an experienced human to remember but difficult for a tool to reconstruct from the repository.

That suggests a shift in what we optimize for.

The target is not "code that is easy for an LLM to read" at the expense of everything else.

The target is:

Code that is easy for a human to audit, easy for an agent to reason about and modify, and predictable enough that tests and runtime behavior can expose mistakes quickly.

This is a different optimization problem from classic code-style debates.

## The Development Loop Is Changing

Traditional development looks roughly like this:

Human writes
    ↓
Human reads
    ↓
Human modifies
    ↓
Human tests

Agent-assisted development increasingly looks like this:

Human specifies intent
    ↓
Agent reads the repository
    ↓
Agent changes the code
    ↓
Agent runs tests
    ↓
Human audits the result
    ↓
Agent performs the next change

The important change is not simply that an agent writes the code.

The important change is that the same repository may be inspected and modified by many future agent sessions that have no memory of the original design discussion.

A senior engineer can remember why a strange boundary exists.

An agent starting a new task cannot.

It sees the repository that we left behind.

That makes source code, tests, documentation, examples, and repository structure part of the communication channel between one engineering session and the next.

A useful mental model is:

        Human engineering intent
                 │
                 ▼
      ┌────────────────────────┐
      │ Repository              │
      │                         │
      │ code                    │
      │ tests                   │
      │ docs                    │
      │ examples                │
      │ structure               │
      │ conventions             │
      └────────────────────────┘
                 │
                 ▼
        Future coding agent

The repository is no longer just an implementation.

It is also the memory of the engineering team.

## 1. The Main Shift: Reduce Human Friction Less, Reduce Machine Ambiguity More

A lot of familiar software engineering advice is based on an implicit assumption:

Writing more code is expensive.

For a human developer, that is often true.

Typing repetitive mappings is expensive. Remembering boilerplate is expensive. Maintaining six parallel implementations is expensive. Reading large repetitive structures is tiring.

An agent changes only part of that equation.

Generating another thirty explicit lines is usually cheap.

Understanding thirty lines containing three layers of indirection is not necessarily cheap.

That leads to a useful inversion:

Traditional concern:

too much code
    ↓
more typing
    ↓
more reading
    ↓
higher maintenance cost

Agent-assisted concern:

more explicit code
    ↓
more generated text
    ↓
usually cheap

hidden behavior
    ↓
more repository exploration
    ↓
more inference
    ↓
higher risk of a wrong modification

This does not mean verbosity is automatically good.

It means that line count is a weaker signal than it used to be.

The more useful question becomes:

How much of the behavior can a future maintainer understand from the code currently in front of them?

## 2. Agents Are Very Good at Generation and Surprisingly Dependent on Context

A coding agent does not arrive with the architecture in its head.

It reconstructs the architecture from the material we give it.

That means an unguided agent tends to fall back on patterns that are common in its training data, framework defaults, and examples in the repository.

A simplified model looks like this:

public coding patterns
+ framework conventions
+ examples in the repository
+ prompt
+ tests
+ local instructions
----------------------------
→ generated implementation

The problem is not that mainstream patterns are inherently bad.

The problem is that a model cannot know which parts of those patterns are wrong for the particular system unless the repository tells it.

Suppose a system has this invariant:

All writes affecting an Order must go through OrderMutationExecutor.

OrderMutationExecutor establishes:
- authorization
- transaction boundaries
- tenant isolation
- audit records
- event publication

Direct writes from request handlers are forbidden.

An experienced developer who has worked on the system for five years may know this automatically.

A new agent does not.

If the repository makes the executor look like unnecessary ceremony, an agent can easily "simplify" it:

handler
    ↓
repository

instead of:

handler
    ↓
OrderMutationExecutor
    ├── authorization
    ├── transaction
    ├── tenant boundary
    ├── audit
    └── event publication

The resulting code can compile.

It can pass a surprisingly large number of tests.

It can still violate the architecture.

This is where context debt becomes important.

## 3. Context Debt Is the Agentic Version of Tribal Knowledge

Traditional technical debt is easy to describe:

The code works, but its structure makes future change unnecessarily difficult.

Documentation debt is similarly obvious:

The implementation and its documentation no longer agree.

Context debt is different:

The system works, but important architectural intent exists only in the heads of the people who built it.

For a human team, this is already dangerous.

For an agent-heavy team, it becomes worse because the next maintainer may not be a person who has accumulated that institutional memory.

Consider:

Never call BillingService directly from OrderProcessingWorker.

All billing requests must be dispatched through the
billing queue because settlement must not happen inside
the worker transaction.

If that rule exists only in Slack, someone's memory, or a conversation from three years ago, it effectively disappears when an agent begins a maintenance task.

The repository needs to carry the rule.

That does not necessarily mean writing a huge architecture document.

Often a short statement next to the relevant code is enough:

// Billing is intentionally dispatched asynchronously.
// Do not call BillingService directly here.
// Settlement must not execute inside the worker transaction.

The point is not documentation for documentation's sake.

The point is to prevent a future maintenance pass from having to guess.

## 4. The Repository Becomes Part of the Agent's Programming Model

Agents learn local architecture from much more than an instructions file.

They see:

repository instructions
+ existing code
+ tests
+ directory structure
+ naming conventions
+ examples
+ repeated patterns
+ comments
+ configuration
+ previous implementation choices

Together these form the local programming culture of the repository.

This has an important consequence:

A repository with inconsistent architecture is effectively giving the agent contradictory instructions.

Imagine a codebase where:

Service A → repositories → EF Core
Service B → Dapper
Service C → generic repository
Service D → raw SQL
Service E → CQRS handlers
Service F → controllers with business logic

An agent asked to add a new feature has to infer which of those patterns is actually authoritative.

It may choose the most common one.

That does not mean it chose the right one.

This is why consistency becomes more valuable in agent-maintained systems.

Not because uniformity is aesthetically pleasing.

Because repeated local patterns reduce the number of architectural decisions the agent has to rediscover.

## 5. Predictability Matters More Than Mainstream Architecture

An internal architecture does not have to look like a framework tutorial to be agent-friendly.

The useful distinction is:

predictable      vs. surprising
explicit         vs. implicit
local            vs. ambient
documented       vs. tribal
consistent       vs. exception-heavy

A deliberately unusual architecture can work very well when its rules are consistent.

For example:

Every business mutation follows:

Handler
  ↓
OperationExecutor
  ↓
Domain operation
  ↓
Persistence
  ↓
Outbox

That may be completely custom.

The important part is that the same shape appears everywhere and the rules are visible.

The opposite is a system where the actual behavior depends on some combination of:

controller
  ↓
implicit middleware
  ↓
ambient request context
  ↓
decorator
  ↓
interceptor
  ↓
ORM behavior
  ↓
hidden retry policy
  ↓
repository

A human who knows the framework can reconstruct this.

An agent can reconstruct it too, but only if it loads all the relevant pieces into context.

That is where the cost appears.

Every hidden dependency creates another question:

"What else happens when this method is called?"

The more often the answer is "something somewhere else", the harder safe automated modification becomes.

## 6. Hidden Behavior Is Expensive Because Agents Modify Locally

This is one of the most important practical consequences of agentic development.

An agent commonly receives a local task:

Add support for this status transition.

It opens the handler.

It modifies the handler.

If the handler contains the complete operational story, this is relatively safe.

If important behavior is distributed across implicit layers, the agent has to reconstruct the whole execution path before it can know what a local change means.

For example:

Visible code:

UpdateOrderStatus(...)

Actual runtime behavior:

UpdateOrderStatus
    ↓
decorator
    ↓
authorization interceptor
    ↓
ambient tenant context
    ↓
transaction middleware
    ↓
ORM change tracker
    ↓
save interceptor
    ↓
audit publisher
    ↓
outbox

The problem is not that any single layer is unreasonable.

The problem is that a local edit has a non-local semantic footprint.

That makes automated reasoning harder.

This suggests a useful architectural preference:

Keep important side effects close enough to the operation that changing the operation does not require remembering the entire framework.

That does not mean "never use middleware" or "never use interceptors".

It means:

Do not hide correctness-critical behavior behind layers that a maintainer must reconstruct from memory.

## 7. Explicitness Becomes More Valuable

Agents are not paid by the character.

That changes the trade-off around explicit code.

Consider:

return orders
    .Where(IsEligible)
    .Select(Normalize)
    .Where(o => o.Amount > 0)
    .ToList();

versus:

var validOrders = new List<Order>();

foreach (var order in orders)
{
    if (!IsEligible(order))
        continue;

    var normalized = Normalize(order);

    if (normalized.Amount <= 0)
        continue;

    validOrders.Add(normalized);
}

return validOrders;

Neither form is universally superior.

The interesting difference appears when an agent has to modify the code.

Suppose the next task is:

Add a metric when an order is rejected for an invalid amount, and log the reason.

The explicit version gives the agent a very obvious insertion point:

if (normalized.Amount <= 0)
{
    metrics.InvalidAmount++;
    logger.LogDebug(...);
    continue;
}

The chained expression requires restructuring the pipeline.

That restructuring is still easy for many agents.

But it introduces an unnecessary transformation before the requested change.

The broader principle is more important than the example:

When two implementations have similar runtime characteristics, prefer the one whose control flow is easiest to inspect and modify mechanically.

Explicit code is especially attractive around:

- state transitions
- failure handling
- transaction boundaries
- authorization
- external calls
- persistence
- retries
- concurrency
- resource ownership

These are the places where ambiguity becomes expensive.

## 8. This Does Not Mean "Never Abstract"

There is an easy mistake to make here.

Once engineers discover that agents handle explicit code well, they can overcorrect:

"Abstractions are bad. Everything should be inline."

That is not the conclusion.

Good abstractions still matter.

The question changes from:

"Does this remove duplication?"

to:

"What problem does this abstraction solve?"

A useful abstraction usually does at least one of these:

- isolates a failure boundary
- enforces an invariant
- defines a stable domain concept
- owns a resource or lifecycle
- hides genuinely complex implementation details
- provides a contract that multiple components independently depend on

A weak abstraction often exists primarily to avoid typing repetitive code.

Consider:

15 lines of straightforward DTO mapping

Creating:

GenericMappingBase<TSource, TDestination>

may save some lines.

But now a change to the base class can affect unrelated features.

The abstraction has converted local duplication into shared coupling.

This is the distinction between two kinds of duplication:

### Semantic Duplication

Dangerous duplication copies business meaning.

Examples:
- tax calculation
- discount rules
- credit limits
- authorization policy
- settlement rules

If those rules appear in three places, they can diverge. That is real maintenance risk.

### Syntactic Duplication

Often harmless duplication repeats implementation mechanics.

Examples:
- DTO declarations
- simple mappings
- small validation blocks
- local loops
- request construction

Repeating these structures can be cheaper than creating an abstraction that couples unrelated features.

A useful test is:

> If these two pieces of code evolve for different business reasons, should changing one change the other?

If the answer is no, sharing them may be unnecessary.

## 9. Semantic Locality Can Matter More Than File Minimalism

Agent workflows also change the trade-off around file organization.

Traditional codebases often spread a single operation across many files:

CancelOrderCommand.cs
CancelOrderValidator.cs
CancelOrderHandler.cs
CancelOrderResult.cs
OrderCancelledEvent.cs
CancelOrderTests.cs

This can be perfectly manageable for a human who knows the project.

But an agent implementing a change now has to discover the relationship between all of these artifacts.

The alternative is a vertically cohesive slice:

CancelOrder.cs:
- input
- validation
- handler
- local result
- local helper
- local event

The benefit is not "one file is always better". The benefit is semantic locality.

A future maintenance pass can often understand the operation without opening six unrelated files.

This is especially useful when the components:
- always change together
- have no independent lifecycle
- are not reused elsewhere
- form one coherent business operation

The goal is not to create giant files. It is to find a useful boundary:

too fragmented
      ↓
hard to gather context

too large
      ↓
hard to navigate, review, and edit

A practical target is often a bounded vertical slice rather than a universal file-size rule. The exact line count should follow cohesion and reviewability, not become a new dogma.

A 250-line file can be excellent. A 500-line file can be fine. A 1,000-line file may still be coherent. A 150-line file can already be too large if it contains unrelated responsibilities.

The architectural rule is more important than the number:

> Keep the complete operational context together until the context itself becomes harder to work with than the fragmentation would have been.

## 10. File Boundaries Are Also Context Boundaries

There is another reason locality matters.

Agents explore repositories through tools.

A fragmented feature often produces a sequence like:

read handler
    ↓
search validator
    ↓
read validator
    ↓
search result type
    ↓
read result
    ↓
search repository
    ↓
read repository

Each step adds more context. More context is not automatically bad. But every additional exploration step creates opportunities for:
- wrong assumptions
- stale assumptions
- tool noise
- missed files
- incomplete understanding
- unnecessary token usage

A cohesive slice can collapse much of that into:

read one file
    ↓
understand operation
    ↓
modify operation

The important point is not that models possess some special hard limit where 500 lines is magic.

The practical point is simpler:

Agents reason more reliably when the information required for a decision is easy to retrieve and presented together.

Semantic locality is therefore a repository-design concern, not merely a formatting preference.

## 11. Do Not Optimize for Agent Convenience at the Expense of Runtime Reality

There is a temptation to push this idea too far:

"Explicit code is good for agents, therefore explicit code is also automatically faster."

That is not a safe rule.

Sometimes explicit code is faster. Sometimes a compiler already eliminates the abstraction.

Do not sacrifice runtime correctness, memory safety, or production efficiency simply to produce flatter code for an LLM. The goal is code that is auditable by humans, legible to agents, and true to the substrate it executes upon.
```
