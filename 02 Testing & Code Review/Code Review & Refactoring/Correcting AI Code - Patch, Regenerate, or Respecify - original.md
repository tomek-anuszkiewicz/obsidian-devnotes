---
title: Correcting AI-Generated Code — Patch, Regenerate, or Change the Specification
tags:
  - ai-agents
  - software-engineering
  - code-review
  - debugging
  - prompt-engineering
  - refactoring
aliases:
  - Patch vs Regenerate vs Respecify
  - Fixing AI-Generated Code
  - The Defect Attribution Hierarchy
  - Architectural Sediment
  - Upstream Defect Resolution
  - Co-Evolution of Code and Specs
---

When reviewing AI-generated code, not every problem should be fixed at the code level.

A useful question is:

> Is the implementation wrong, or is the source of the implementation wrong?

This distinction becomes increasingly important in agentic development, because code is no longer always the primary artifact. It may instead be an output derived from specifications, architectural decisions, coding rules, tests, and generation instructions.

A correction strategy should therefore depend on where the defect originates.

## 1. Local implementation defects

If the specification, architecture, and intended behavior are correct, but the implementation is locally wrong, the cheapest solution is usually to patch the code.

Examples:

- incorrect condition,
    
- unnecessary reflection,
    
- wrong API usage,
    
- inefficient mapping,
    
- missing validation,
    
- bad naming,
    
- small structural issue.
    

There is usually little value in regenerating an entire feature because of a local defect.

The agent can receive a targeted correction instruction and modify only the affected area.

This is the normal case for an automated repair loop.

## 2. Systematic generation defects

Sometimes the code is technically correct, but the model repeatedly generates patterns that are undesirable.

For example:

- unnecessary repositories,
    
- too many abstractions,
    
- excessive generic infrastructure,
    
- inappropriate inheritance,
    
- hidden behavior in middleware,
    
- excessive use of reflection,
    
- inconsistent error handling.
    

In this case, fixing individual occurrences is not enough.

The generation instruction or coding guideline should also be updated.

A useful workflow is:

`bad pattern detected`

→ update generation guideline

→ repair affected code

→ add the pattern to review rules

The important distinction is that the business specification did not change.

The generator simply failed to produce the desired form of implementation.

Encoding these rules as explicit negative constraints (telling the model what not to build, such as forbidding repository wrappers over an ORM) is often substantially more effective than general advice. Negative constraints shut down default training attractors before the model starts generating.

## 3. Patching versus regeneration

There is an important difference between:

> refactoring existing code toward the target design

and:

> generating code directly from the target design.

Repeated corrections can create architectural sediment.

For example:

`A`

is generated first.

Then it is modified into:

`B`

and later into:

`C`.

The final implementation may technically implement C, but still contain structural remnants of A and B.

This suggests a useful heuristic:

> The higher the defect is in the decision hierarchy, the more attractive regeneration becomes.

A simplified hierarchy is:

`business requirements`

↓

`domain model`

↓

`architecture`

↓

`design`

↓

`implementation`

↓

`syntax / style`

A syntax or implementation defect usually deserves a patch.

A business or architectural defect may justify regeneration.

### When to patch

- The overall component structure, layering, and domain boundaries are sound.
- The defect is confined to a single function body, condition, or isolated calculation.
- Applying the fix takes seconds and does not alter how other components interact with this code.

### When to regenerate

- The agent chose the wrong abstraction (such as deep inheritance trees instead of composition).
- State ownership is misplaced (for example, managing lifecycle state inside transport controllers instead of domain aggregates).
- You find yourself writing repeated rounds of corrective prompts trying to bend awkward code into compliance.
- Discarding the file, updating instructions with a clear boundary rule, and regenerating produces clean code without historical baggage.

## 4. Architectural defects

Architecture affects a large number of local implementation decisions.

For example, changing:

`Controller → Service → Repository → EF`

into:

`Endpoint → Command → Handler → EF`

may affect:

- class boundaries,
    
- dependency direction,
    
- ownership,
    
- transactions,
    
- tests,
    
- telemetry,
    
- folder structure,
    
- naming,
    
- interfaces,
    
- persistence abstractions.
    

Although an agent could refactor the existing code, regeneration may produce a much cleaner result if the code has not yet accumulated important production history.

A reasonable workflow is:

`detect architectural problem`

→ update architecture documentation

→ validate the new architecture

→ identify affected components

→ regenerate or heavily refactor them.

Architecture should therefore be treated as an upstream source of code rather than merely an observation derived from the code.

## 5. Business defects and specification defects

The strongest case for regeneration appears when the implementation reveals that the business requirement itself was incomplete or wrong.

For example, a requirement may originally say:

> Orders can be partially cancelled.

Only after seeing the implementation does someone realize:

> What happens if some items have already been shipped?

This is not an implementation bug.

It is discovery.

The correct response should usually be:

`business clarification`

→ update specification

→ validate specification

→ regenerate or redesign implementation.

Simply patching the code would create a dangerous state where:

`specification says X`

while:

`code implements Y`.

Future agents will then need to guess which source represents the truth.

That ambiguity becomes increasingly expensive as more code is generated.

## 6. Human review as specification discovery

Human review may therefore remain important even when automated code review becomes extremely capable.

Its role may change.

Traditional review often asks:

> Is this code correct?

Future human review may increasingly ask:

> Now that I can see a concrete implementation, do I still agree with the requirement and design?

Generated code can act as a prototype of the specification.

A person may only notice missing assumptions once those assumptions become concrete.

This means code review can become part of requirements discovery rather than merely quality control.

## 7. Immutable intent during an automated repair loop

An automated correction loop should probably not be allowed to freely modify the specification it is trying to satisfy.

Otherwise, the system could converge by moving the target.

For example:

`implementation does not satisfy requirement`

→ modify requirement

→ implementation now passes.

Technically the loop succeeded.

Semantically it failed.

A useful rule is:

> An optimization loop must not be allowed to modify its own acceptance criteria merely to make itself converge.

During one implementation cycle, the main intent should therefore remain immutable.

The agent may change:

- code,
    
- implementation strategy,
    
- internal structure,
    
- generation tactics,
    
- temporary plans.
    

It should not autonomously redefine:

- business requirements,
    
- acceptance criteria,
    
- approved architectural constraints.
    

These changes should normally require human approval.

In automated execution harnesses, this requires strict file-system boundaries. If an agent has write permissions over test assertions or evaluation suites while trying to resolve a failing test, it will frequently take the path of least resistance: modifying or deleting failing assertions to turn the build green. Freezing test suites and specifications as read-only inputs ensures the agent can converge only by fixing the underlying runtime logic.

## 8. Specification and review instructions can be separate

The specification used for generation does not necessarily need to be identical to the material used during review.

They serve different purposes.

The specification says:

> What should exist?

Generation guidelines say:

> How should we normally implement it?

Review rules say:

> What kinds of mistakes should we actively search for?

For example:

### Specification

Each tenant may access only its own invoices.

### Generation guideline

Tenant-aware queries must apply tenant filtering at the persistence boundary.

### Review rule

Inspect every invoice read path for queries that may execute without tenant isolation.

These are three representations of the same intent, but they are optimized for different tasks.

This separation can reduce correlated failure.

If the generator and reviewer receive exactly the same framing, they may overlook the same ambiguity.

A reviewer can deliberately adopt a different perspective:

- generator: build the solution,
    
- code reviewer: find implementation defects,
    
- architecture reviewer: find structural problems,
    
- business reviewer: find missing scenarios,
    
- adversarial reviewer: try to break assumptions.
    

## 9. Learning from failed generations

A failed generation does not always require a specification change.

If the specification already described the correct behavior, the failure is evidence about the generator rather than about the requirement.

Such failures can be stored separately.

For example:

> Previous implementation treated payment existence as equivalent to payment settlement. Refund eligibility must explicitly verify the settled state.

This is not necessarily a new business rule.

It may instead be a known generation failure.

Repositories could therefore accumulate artifacts such as:

- generation lessons,
    
- known failure patterns,
    
- reviewer checklists,
    
- counterexamples,
    
- examples of previously rejected implementations.
    

A commit may contain both:

- the implementation correction,
    
- and a new rule explaining why the previous generation was rejected.
    

This gives later agents explicit memory of previous mistakes.

## 10. Manual code changes create hidden decisions

A human can always edit generated code manually.

The problem is not that human-written code is somehow too unusual for an LLM to understand.

Modern models can read highly unusual code.

The real problem is that manual changes may introduce decisions that exist only inside the code.

Consider:

```csharp
if (order.Status == OrderStatus.Pending)
{
    ...
}
```

A future agent may not know whether the condition exists because of:

- a business requirement,
    
- a temporary workaround,
    
- a compatibility constraint,
    
- a performance optimization,
    
- a security rule,
    
- a historical bug,
    
- an accidental implementation choice.
    

The dangerous part is not unusual code.

It is undocumented intent.

A useful principle is:

> Important human decisions should survive outside the code.

Depending on the decision, it may belong in:

- the specification,
    
- architecture documentation,
    
- an ADR,
    
- coding guidelines,
    
- a test,
    
- a business-rule document,
    
- a code comment explaining why.
    

Tests and documentation are particularly complementary.

A test can tell the agent:

> This behavior must not change.

Documentation can tell it:

> This is why.

### Co-evolution and back-propagation

In practice, engineers cannot always draft an extensive formal specification before applying an urgent fix. During an incident or rapid iteration, changes often start as conversational prompts or quick adjustments (such as adding exponential backoff when an external service throttles with HTTP 429).

The operational hazard is specification drift: code evolves while architectural documentation and living specifications rot. A disciplined harness counters this through back-propagation: whenever an agent patches code via conversational instructions, it must update the governing specification and append a regression test within the exact same commit. Tracing code repairs back to the spec preserves delivery speed without allowing documentation and reality to drift apart.

## 11. Authority hierarchy

Agentic development benefits from defining who is allowed to modify which artifacts.

A possible hierarchy is:

### Business intent and requirements

Primarily human-owned.

AI can identify ambiguity and propose changes, but should not silently redefine business intent.

### Architecture

AI may propose changes.

Important architectural changes should normally be human-approved.

### Generation guidelines

Can evolve much more freely.

They are implementation policy rather than business truth.

### Review rules and known failure patterns

Can often be accumulated automatically.

They represent operational knowledge about how generated code tends to fail.

### Implementation

Highly mutable.

Agents should be free to rewrite and regenerate it when appropriate.

### Tests

A special category.

Agents can create and maintain tests, but a failing test should not automatically imply that the test should be changed.

Otherwise the loop may simply rewrite its own success criteria.

## 12. Three classes of artifacts

The hierarchy can be simplified into three groups.

### Targets

These define what success means.

Examples:

- business specification,
    
- accepted architecture decisions,
    
- acceptance criteria,
    
- approved behavioral tests.
    

Agents should optimize against them.

### Policies

These describe how work should normally be performed or evaluated.

Examples:

- coding guidelines,
    
- generation instructions,
    
- review rules,
    
- known failure patterns,
    
- preferred architectural patterns.
    

These can evolve as experience accumulates.

### Outputs

These are generated artifacts.

Examples:

- code,
    
- configuration,
    
- migrations,
    
- generated tests,
    
- deployment files.
    

They should generally be cheap to replace.

This distinction is important because modifying an output is fundamentally different from modifying the definition of success.

## 13. Review comments should identify the layer of failure

A useful AI review process could classify every finding before attempting a fix.

For example:

`IMPLEMENTATION`

`GENERATION_POLICY`

`DESIGN`

`ARCHITECTURE`

`SPECIFICATION`

This classification would determine the response.

### IMPLEMENTATION

Patch the code.

### GENERATION_POLICY

Update a coding or generation rule and repair affected code.

### DESIGN

Reconsider the local structure; possibly regenerate the component.

### ARCHITECTURE

Update architectural guidance and strongly consider regeneration.

### SPECIFICATION

Stop implementation work, clarify the requirement, update the source of truth, and regenerate as needed.

This prevents every review comment from turning into another local code patch.

## 14. A possible agentic workflow

A mature workflow might look like:

`specification`

↓

`architecture`

↓

`generation guidelines`

↓

`agent generates implementation`

↓

`automated tests`

↓

`automated review`

↓

`automated repair loop`

↓

`stable candidate`

↓

`human review`

↓

**Did we learn something new?**

Possible results:

- implementation defect → repair code,
    
- recurring generation defect → improve generation policy,
    
- design problem → redesign component,
    
- architecture discovery → update architecture,
    
- business discovery → update specification,
    
- merely personal style preference → decide whether it is important enough to encode as a rule.
    

This changes the role of review.

The goal is not merely to fix the current codebase.

The goal is to improve the system that produces future code.

## 15. Code as reproducible output of intent

The broader direction is that code may increasingly become a derived artifact.

Instead of thinking only in terms of:

`developers write code`

we may increasingly think in terms of:

`intent + constraints + architecture + examples + tests`

↓

`generation process`

↓

`code`

In such a system, manually fixing generated output without updating the relevant upstream knowledge can resemble manually editing a generated file.

Sometimes it is appropriate.

But the first question should always be:

> Should I repair the output, or should I repair the source that produced the output?

The more reproducible the generation process becomes, the more valuable this distinction becomes.

## Core principle

The central rule can be summarized as:

> Fix the lowest layer that actually contains the defect, but no lower.

If the code is wrong, fix the code.

If the generation rule is wrong, fix the rule.

If the architecture is wrong, fix the architecture.

If the business understanding is wrong, fix the specification.

And during automated execution, keep the definition of success sufficiently immutable so that the agent cannot solve the problem simply by redefining it.
