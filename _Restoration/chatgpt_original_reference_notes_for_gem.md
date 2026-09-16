# Reference Style Baseline: Original Ground-Truth Engineering Notes

This document contains 6 original, uncorrupted reference notes written from the perspective of a Senior Technical Lead / Principal Architect. 

## Purpose for the AI Model / Custom Gem
Use these notes as the **gold standard style and tone reference** (few-shot context). When rewriting, restoring, or creating new architectural notes, strictly mirror the voice, structure, and communication traits demonstrated in these documents:

1. **Voice & Stance**:
   - Calm, conversational, authoritative, and deeply practical.
   - Sounds like a senior engineer explaining real-world systems over coffee or at an internal tech talk.
   - Zero sensationalist hooks, zero purple prose, zero manufactured drama, and zero academic fluff.
2. **Technical Depth & Grounding**:
   - Rich in concrete domain scenarios, real code mechanisms, and negative knowledge (what fails, what not to do).
   - Nuanced exploration of trade-offs and edge cases rather than rigid dogmatic rules.
3. **Structure & Visuals**:
   - Clean, organic headings matched to the problem.
   - Minimalist, functional data-flow diagrams rather than shouting ASCII decorative banners.

---

# Reference Note: Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize

---
title: Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize
tags:
  - ai-agents
  - code-review
  - software-engineering
  - quality-assurance
  - static-analysis
  - compliance
  - review
aliases:
  - Natural-Language Rules as Executable Policies
  - Agentic Review Rules
  - Semantic Code Review
---

Traditional software quality automation works best when a rule can be expressed precisely.

For example:

```text
Domain must not reference Infrastructure.
Every public endpoint must require authorization.
Result must never be negative.
All handlers must implement a particular interface.
```

Such rules can be encoded as:

- unit tests;
    
- architecture tests;
    
- static analyzers;
    
- compiler rules;
    
- type-system constraints;
    
- linters;
    
- CI checks.
    

This remains extremely valuable.

However, a large part of software engineering has never fit comfortably into this model.

Many important rules are not difficult because developers do not understand them.

They are difficult because they are expensive or nearly impossible to formalize.

LLM-based review agents may automate part of this previously human-only layer.

---

## Many Real Engineering Rules Are Semantic

#coding_standard

Consider rules such as:

> Do not introduce an abstraction unless it represents a meaningful boundary.

Or:

> Controllers should remain thin, but trivial request mapping does not need another service layer.

Or:

> Modules should communicate through their public contracts rather than reaching into each other's internals.

Or:

> Do not introduce a generic framework for a problem that exists only once.

Or:

> Business rules should remain visible in the domain code rather than being hidden inside infrastructure helpers.

These are meaningful architectural principles.

An experienced engineer can often recognize their violation immediately.

But encoding them as a deterministic test may require an enormous amount of machinery.

The problem is not lack of rules.

The problem is that the rules depend on:

- intent;
    
- context;
    
- naming;
    
- surrounding architecture;
    
- business meaning;
    
- exceptions;
    
- trade-offs;
    
- degree rather than binary classification.
    

Historically, this meant that enforcement depended on human attention.

---

## Human Attention Was the Missing Runtime

#review 

Architecture documents frequently contain sentences like:

```text
Prefer explicit dependencies.

Avoid leaking persistence concerns into the domain.

Do not create abstractions prematurely.

Cross-module access should happen through defined boundaries.
```

These rules may be well understood by the team.

But nothing actually executes them.

Their enforcement mechanism is approximately:

```text
developer remembers the rule
        +
reviewer remembers the rule
        +
reviewer notices the violation
```

This is fragile.

Even excellent reviewers:

- get tired;
    
- skim large changes;
    
- forget some guidelines;
    
- focus on the most obvious problem;
    
- have limited time;
    
- do not inspect every pull request with identical depth.
    

A review agent changes this because it can repeatedly interpret the same rule against every relevant change.

The document can become part of an active quality system rather than passive documentation.

---

# Natural-Language Rules Can Become Executable Policies

#coding_standard

Suppose a repository contains:

```text
docs/architecture/principles.md
docs/domain/invariants.md
docs/security/guidelines.md
docs/performance/guidelines.md
ADRs/
```

An architecture reviewer can receive these documents as part of its instructions.

For every pull request it can ask:

```text
Does this change violate any architectural principle?

If so:

- identify the concrete code;
- identify the relevant principle;
- explain why the rule applies;
- consider documented exceptions;
- estimate confidence;
- avoid commenting if evidence is weak.
```

This is not executable specification in the traditional deterministic sense.

It is closer to:

> natural-language executable policy.

The important change is that a rule no longer needs to be translated completely into code before it can be checked automatically.

---

## This Expands the Automatable Region of Engineering

Previously there were roughly two categories:

```text
Formalizable rule
    -> automation

Non-formalizable rule
    -> human review
```

Agents introduce a third layer:

```text
Formalizable rule
    -> deterministic automation

Semantically interpretable rule
    -> agentic verification

Ambiguous strategic decision
    -> human judgment
```

This potentially moves a large amount of work out of the purely human-review category.

Examples include checking whether:

- a new abstraction is justified;
    
- responsibilities remain in the correct module;
    
- domain logic is becoming infrastructure-dependent;
    
- error handling matches surrounding conventions;
    
- a change duplicates an existing capability;
    
- a public API behaves consistently with related APIs;
    
- a workaround violates an architectural direction;
    
- a class has accumulated too many unrelated responsibilities;
    
- a supposedly generic component is actually coupled to one use case.
    

These are exactly the kinds of things senior engineers traditionally catch during review.

---

# Agents Are Particularly Useful Because They Are Relentless

The advantage is not only that an LLM can understand such rules.

It can apply them every time.

A human may know twenty architectural principles perfectly but consciously evaluate only a subset during a particular review.

An agent can inspect every relevant PR against all twenty.

It does not care that:

- the change is repetitive;
    
- the pull request contains 100 files;
    
- this is the fiftieth review this week;
    
- the rule rarely catches anything;
    
- the same check has failed to find a problem for six months.
    

This makes agents particularly suitable for rules that are individually important but rarely violated.

Humans are bad at maintaining attention for checks that almost always produce:

```text
nothing wrong
```

Machines are excellent at it.

---

# But Agents Must Also Handle Formalizable Rules Well

There is an important danger in dividing the world too aggressively into:

```text
tests handle simple rules

LLMs handle difficult rules
```

An effective reviewer must still understand the rules that could have been expressed as deterministic tests.

For example:

```text
A price must never be negative.
```

Even if there is already a unit test for this invariant, an agent reviewing related code should understand that violating it is wrong.

Otherwise the agent has an incomplete model of the system.

The distinction should therefore not be:

> deterministic rules belong to tests and should be invisible to the agent.

Instead:

> deterministic tools are the authoritative verification mechanism, while the agent should also understand their meaning.

The agent should be capable of reasoning:

```text
This change appears capable of creating a negative price.

There is an invariant that prices cannot be negative.

I should inspect or run the relevant tests.
```

Then the deterministic test provides the strongest evidence.

---

## Formal Rules Should Usually Remain Deterministic

If something can be verified cheaply and precisely:

```text
Assert.True(result >= 0);
```

there is little benefit in replacing it with:

```text
Ask an LLM whether result >= 0 appears to hold.
```

The deterministic version is:

- cheaper;
    
- faster;
    
- reproducible;
    
- precise;
    
- easy to debug;
    
- independent of model behavior.
    

Agents should therefore usually sit above these mechanisms rather than replacing them.

A useful principle is:

> Formalize what is cheap to formalize. Use agents where formalization becomes disproportionately expensive.

---

# The Agent Can Connect Formal and Informal Rules

The interesting capability appears when an agent understands both.

Suppose an architecture document says:

> Module A must not depend on Module B's persistence model.

There may also be a deterministic architecture test forbidding direct references between certain namespaces.

The agent can detect a subtler case:

```text
There is no forbidden assembly reference.

However, Module A now copies the exact internal database representation
of Module B and depends on its persistence semantics.
```

The formal test passes.

The architectural intent may still be violated.

The agent operates one level above syntax.

Likewise:

```text
Unit test:
Price cannot be negative.
```

may pass.

But the reviewer may notice:

```text
The implementation clamps negative prices to zero,
which preserves the technical invariant but silently hides
an invalid business state.
```

A deterministic test sees compliance.

A semantic reviewer can question whether the implementation satisfies the underlying intent.

This interaction is potentially much more powerful than either approach alone.

---

# Agents Can Escalate Rules Into Deterministic Tests

Agentic review can also help discover which informal rules should eventually become formal.

Imagine an agent repeatedly finds the same problem:

```text
Five pull requests introduced direct dependencies
from Domain to Infrastructure.
```

At that point the correct response may be:

> Stop asking the LLM to rediscover this every time.

Turn the rule into an architecture test.

The process becomes:

```text
informal principle
        |
agent repeatedly checks it
        |
pattern becomes stable
        |
rule can be formalized
        |
architecture test / analyzer added
```

This gives a useful migration path.

Agents can act as the exploratory layer from which deterministic rules emerge.

---

# The Reverse Is Also Useful

A deterministic check may reveal a violation without explaining its architectural significance very well.

For example:

```text
Architecture test failed:
Namespace X references namespace Y.
```

The agent can add context:

```text
This is prohibited because Y contains persistence-specific models.

The new reference causes the pricing module to depend on the current
database representation of customer data.

The intended integration point is CustomerContract.
```

The machine-verifiable test gives certainty.

The agent gives interpretation.

That combination can make automated checks much easier for developers to understand and fix.

---

# Some Tests May Become Ephemeral

Agents also make it possible to distinguish between permanent tests and tests created only for investigation.

Today a test usually means:

```text
write test
commit test
maintain test forever
```

An agent can instead generate a test to investigate a particular hypothesis.

For example:

```text
I suspect this cache fails when two requests initialize it concurrently.
```

The agent creates a temporary concurrency test, runs it repeatedly, and discovers the race.

The experiment itself does not necessarily need to remain in the repository.

If the discovered behavior represents an important regression risk, the test can then be promoted:

```text
agent-generated experiment
        |
bug reproduced
        |
important invariant discovered
        |
promote test
        |
permanent regression test
```

This separates:

```text
tests as permanent specification
```

from:

```text
tests as investigative instruments
```

Agents can make heavy use of the second category.

---

# Architecture Review May Become Continuous

The same idea applies especially well to architecture.

Today architecture is often enforced through a mixture of:

```text
architecture documents
ADRs
review culture
senior engineers
occasional architecture tests
```

With agents, every pull request can undergo an architecture review.

The reviewer can ask:

```text
Did this change create a new dependency direction?

Did an internal concept leak through a module boundary?

Was an abstraction introduced?

If so, does it have a meaningful reason to exist?

Does this change contradict an ADR?

Does it make a future migration significantly harder?

Is business logic moving into infrastructure code?

Does the new code follow the architecture or merely satisfy its syntax?
```

Most of these questions would be extraordinarily difficult to encode in conventional analyzers.

They are much closer to questions asked by an experienced architect.

---

# The Ideal System Uses Both Forms of Verification

The future quality stack may therefore look something like:

```text
              Human judgment
                    ▲
                    |
          Semantic agent review
                    |
       architecture / intent /
       context / trade-offs
                    ▲
                    |
        Deterministic verification
                    |
      tests / types / analyzers /
       linters / security tools
```

The layers complement each other.

Deterministic verification provides certainty where precise formalization is practical.

Agents extend automation into areas where semantic judgment is required.

Humans remain responsible for decisions where even the correct rule depends on business priorities, risk tolerance, or competing architectural goals.

---

# The Goal Is Not to Replace Rules With Prompts

A tempting mistake would be to conclude:

> If an LLM can inspect the code, we no longer need architecture tests, analyzers, or unit tests.

That would discard one of software engineering's strongest properties: deterministic verification.

A better model is:

```text
If a rule can cheaply become code:
    encode it.

If a rule is difficult to encode but understandable:
    let an agent enforce it.

If an agent repeatedly finds the same formalizable violation:
    consider turning it into code.

If the correct answer depends on strategic judgment:
    escalate it to a human.
```

This creates a continuum rather than a replacement.

---

# Review Agents Turn Human Attention Into a Scalable Resource

Historically, many engineering standards were enforced simply because experienced developers watched for them.

That created an unavoidable constraint:

```text
quality of enforcement
≈
available senior engineering attention
```

Agents weaken this dependency.

A senior engineer may define a principle once:

> Do not hide business decisions behind generic infrastructure abstractions.

Instead of expecting every reviewer to remember and enforce it forever, the principle can become part of an agent's permanent review instructions.

The human provides the judgment once.

The agent applies it thousands of times.

That may be one of the most important consequences of agentic code review:

> knowledge that previously existed only as human review intuition can become continuously executable organizational policy.

The strongest future systems will probably combine two capabilities:

> machines must be extremely reliable at rules that can be formalized, while also extending verification into rules that previously required human interpretation.

The first preserves the precision of traditional software engineering.

The second expands its reach.

---

# Reference Note: Comments May Become More Valuable in AI-Generated Code

---
title: Comments May Become More Valuable in AI-Generated Code
tags:
  - ai-agents
  - software-engineering
  - documentation
  - code-review
  - maintainability
  - intent-specification
aliases:
  - Code Comments in AI Era
  - Semantic Value of Comments in AI Code
---

The traditional rule for comments is often expressed as:

> Good code should explain what it does. Comments should explain why.

This distinction may become even more important in software increasingly written and modified by AI agents.

An agent can usually reconstruct the mechanics of code very well. It does not need comments that merely repeat the implementation.

For example:

```csharp
// Charge 50% if booking starts in less than 3 days.
if (booking.StartDate < DateTime.UtcNow.AddDays(3))
{
    cancellationFee = booking.TotalPrice * 0.5m;
}
```

The comment adds almost no information.

A much more valuable comment would be:

```csharp
// Cancellations within 72 hours are charged 50% because the supplier
// no longer refunds us after this point.
// Do not replace this with the standard hotel cancellation policy.
```

The code explains the mechanism.

The comment preserves information that cannot easily be reconstructed from the implementation:

- why the rule exists;
    
- where it comes from;
    
- whether it is intentional;
    
- which business constraint it represents;
    
- what apparently reasonable changes would be incorrect.
    

## Code Is Self-Documenting Syntactically, Not Semantically

Well-written code can communicate structure and behavior.

For example:

```csharp
ApplyNonRefundableSupplierCancellationFee();
```

This is much better than an obscure method name, but it still does not explain:

- why this supplier is treated differently;
    
- whether the behavior comes from a contract;
    
- whether it is temporary;
    
- which products it applies to;
    
- whether another similar rule should be reused;
    
- what assumptions the implementation depends on.
    

Historically, much of this knowledge lived outside the code:

- in developers' heads;
    
- Jira tickets;
    
- Slack conversations;
    
- meetings;
    
- old specifications;
    
- architecture documents.
    

Future agents modifying the code may never see any of those sources.

A comment located next to the implementation has a major advantage:

> It is very likely to enter the agent's context whenever the relevant code enters the context.

## Comments Can Act as Local Context Retrieval

Suppose an agent receives a task:

> Add partial cancellation support.

It retrieves the classes responsible for cancellations.

Any comments located inside those classes are naturally retrieved together with the implementation.

This makes comments a kind of very small, highly localized knowledge base.

They do not require the agent to know:

- that an ADR exists;
    
- which specification describes the rule;
    
- which ticket introduced it;
    
- what search query to use;
    
- which meeting contained the relevant discussion.
    

The knowledge is physically attached to the place where it matters.

This may make carefully written comments one of the most reliable forms of context delivery for future coding agents.

## Documentation Layers Still Have Different Roles

Comments should not replace specifications or architectural documentation.

Instead, the different layers can complement each other:

```text
Specification
    ↓
describes desired behavior and requirements

Architecture docs / ADRs
    ↓
describe system-wide decisions and trade-offs

Business comments
    ↓
preserve local intent, constraints and exceptions

Code
    ↓
contains the executable implementation
```

During the initial implementation, an agent may have access to the complete specification.

Several years later, another agent may receive only a small portion of the repository while working on an unrelated change.

The original specification may not enter its context at all.

A nearby comment probably will.

## Negative Knowledge May Be Especially Valuable

Some of the most useful comments may describe what must **not** be done.

For example:

```csharp
// Do not calculate this from Payment.Amount.
// Legacy bookings may already contain the agency margin there.
```

Or:

```csharp
// This check looks redundant, but some suppliers occasionally send
// the same reservation with different external IDs.
```

Or:

```csharp
// Intentionally executed before availability validation.
// Sales requires the original quoted price to remain available
// even when availability subsequently fails.
```

This is negative knowledge:

> A seemingly obvious implementation or refactoring is incorrect.

Such knowledge may be particularly important for agents.

An agent performing a local refactoring may see:

```text
strange condition
→ appears redundant
→ simplify it
```

A good comment changes the reasoning to:

```text
strange condition
→ explicitly intentional
→ represents a business constraint
→ preserve unless the requirement itself changes
```

## Clean Code Does Not Eliminate Business Context

The argument that "good code should not require comments" is reasonable when applied to comments describing mechanics.

Comments such as:

```csharp
// Iterate through users.
```

are usually unnecessary.

But business rationale cannot always be encoded through better naming or cleaner abstractions.

A method called:

```csharp
IsEligibleForLegacyCancellationCompensation()
```

still does not explain why legacy cancellation compensation exists.

The useful distinction may therefore become:

> Minimize comments explaining implementation.

> Maximize comments preserving intent, business meaning, invariants, constraints, exceptions and non-obvious decisions.

## Agents Can Produce Their Own Future Context

There is another important consequence.

When an agent implements a feature, it already has the specification in its context.

Instead of converting that specification only into executable code, it can also preserve the parts of the specification that future developers or agents will need.

A useful instruction could be:

> Whenever the implementation encodes a non-obvious business rule, invariant, exception or constraint that cannot be reconstructed from the code itself, preserve that information as a concise comment near the relevant code.

The process then becomes:

```text
task specification
       │
       ▼
     agent
    /     \
   ▼       ▼
code     durable intent
         comments
```

The code is the executable result of the specification.

The comments preserve selected parts of its semantics.

## Comments May Become Part of Designing Code for Agents

Traditionally, comments were primarily written for human maintainers.

In agent-heavy development, another audience appears:

> the future model receiving a limited slice of the repository as context.

This changes how comments can be evaluated.

The question is no longer only:

> Will another developer understand this?

It also becomes:

> If an agent sees only this file two years from now, what important information could it incorrectly infer?

Comments can protect against those incorrect inferences.

This suggests that codebases optimized for agentic development may intentionally preserve more business context next to the implementation.

Not more comments in general.

Better comments.

Especially comments explaining:

- why a rule exists;
    
- which business concept it represents;
    
- which invariant must remain true;
    
- why an unusual implementation is intentional;
    
- which tempting simplification would be wrong;
    
- which external constraint shaped the implementation;
    
- which assumptions future changes must preserve.
    

In this sense, comments may become part of **context engineering for future coding agents** rather than merely an aid to human readability.

## Redefining Low-Level and Architectural Documentation

The ability of LLMs to analyze code and explain its mechanics on demand accelerates two major shifts:

1. **Obsolescence of Low-Level Comments and Descriptive Docs:**
   - Comments explaining *how* a function works or what steps it takes are now pure noise.
   - Broad architectural documentation that merely describes component relationships or data flows is easily reconstructed on the fly by an agent analyzing the codebase.

2. **From Structural Documentation to Decision Records:**
   - Documentation shifts almost entirely from *descriptive* (what exists) to *decisional* (why it was built this way).
   - High-level architecture docs remain valuable only as **guardrails and trade-offs** (e.g., ADRs, system constraints, performance budgets) that prevent agents from making architectural refactorings that break unstated non-functional requirements.

---

# Reference Note: Designing APIs for LLM-Generated Integration Code

---
title: Designing APIs for LLM-Generated Integration Code
tags:
  - api-design
  - ai-agents
  - software-architecture
  - integration
  - developer-experience
  - documentation
aliases:
  - Agent-Friendly API Design
  - APIs for LLM Integrations
---

## Goal

When using an LLM coding agent, the goal is not necessarily for the agent to call an API directly.

Instead, the agent should be able to:

1. understand the requested business operation,
    
2. discover which external API capability provides it,
    
3. find the correct generated client,
    
4. choose the correct client method,
    
5. generate application code that uses that method correctly.
    

A useful mental model is:

```text
Business requirement
        ↓
Discover business capability
        ↓
Find appropriate client
        ↓
Find appropriate operation
        ↓
Generate application code
        ↓
Generated client
        ↓
REST API
```

## Internal vs External APIs

It is useful to distinguish between internal and external APIs.

### Internal APIs

Internal APIs may:

- reflect internal service architecture,
    
- expose implementation-specific concepts,
    
- use internal data representations,
    
- change relatively freely,
    
- depend on concepts already understood inside the system.
    

### External APIs

External APIs should:

- provide stable contracts,
    
- avoid leaking internal implementation details,
    
- expose business concepts rather than internal mechanics,
    
- remain compatible over time,
    
- use terminology meaningful to consumers.
    

This distinction becomes even more important for LLM-generated code.

The easier it is to understand the business meaning of an operation, the easier it is for an agent to select it correctly.

---

## OpenAPI as the Source of Truth

For REST APIs, OpenAPI should describe not only the HTTP contract, but also the semantics of the operation.

A weak specification:

```yaml
/users/{id}/sessions:
  delete:
    operationId: deleteSessions
```

A better specification:

```yaml
/users/{userId}/sessions:
  delete:
    operationId: revokeUserSessions
    summary: Revoke all active sessions for a user
    description: |
      Revokes all active authentication sessions belonging
      to the specified user.

      Use this operation when access for the user must be
      immediately invalidated.

      This operation does not delete the user account.
```

The description should answer questions such as:

- What does this operation do?
    
- When should it be used?
    
- When should it not be used?
    
- What are the preconditions?
    
- What side effects does it have?
    
- What are the important failure modes?
    

Negative guidance can be especially useful.

For example:

```yaml
description: |
  Permanently deletes a draft invoice.

  Only draft invoices can be deleted.

  Do not use this operation for issued invoices.
  Issued invoices must be cancelled using cancelInvoice.
```

This helps the agent choose the correct business operation rather than matching only on words such as "delete".

---

## Prefer Business-Oriented Operations

Operations should clearly express intent.

Prefer:

```text
cancelInvoice
revokeUserSessions
reserveInventory
approveOrder
```

over vague operations such as:

```text
updateEntity
executeAction
changeStatus
processRequest
```

CRUD operations are perfectly fine when the business operation really is CRUD.

For example:

```http
DELETE /drafts/{id}
```

is appropriate if the object is actually deleted.

But a business operation such as cancelling an issued invoice should probably be represented explicitly:

```http
POST /invoices/{id}/cancel
```

rather than pretending that cancellation is equivalent to deletion.

The important principle is:

> The API should expose business capabilities, not merely database mutations.

---

## Generate Strongly Typed Clients

The coding agent should normally not construct HTTP requests manually.

Instead of generating:

```csharp
await httpClient.DeleteAsync(
    $"/users/{userId}/sessions");
```

prefer a generated typed client:

```csharp
await identityClient.RevokeUserSessionsAsync(
    userId,
    cancellationToken);
```

The client can be generated from OpenAPI using tools such as:

- Kiota,
    
- NSwag,
    
- OpenAPI Generator.
    

The flow becomes:

```text
OpenAPI
   ↓
Client generator
   ↓
Strongly typed client
   ↓
LLM-generated application code
```

This significantly reduces the space in which the agent can make mistakes.

It no longer needs to reconstruct:

- the URL,
    
- HTTP method,
    
- serialization format,
    
- request schema,
    
- response schema,
    
- query parameter names.
    

Instead, it chooses a typed method.

---

## Preserve Documentation in Generated Clients

Ideally, descriptions from OpenAPI should become XML documentation or equivalent comments in the generated client.

For example:

```csharp
public interface IInvoicesClient
{
    /// <summary>
    /// Cancels an issued invoice while preserving it for audit.
    /// Do not use for draft invoices.
    /// </summary>
    Task CancelInvoiceAsync(
        Guid id,
        CancellationToken cancellationToken);

    /// <summary>
    /// Permanently deletes a draft invoice.
    /// Issued invoices cannot be deleted.
    /// </summary>
    Task DeleteDraftInvoiceAsync(
        Guid id,
        CancellationToken cancellationToken);
}
```

This is particularly useful for coding agents because the most relevant semantic information is available directly next to the methods they are expected to use.

If the generated client loses all API descriptions, much of the semantic value of OpenAPI is lost.

---

## Client Discoverability

Having good generated clients is not enough.

The agent must also be able to discover which client provides a given capability.

Prefer domain-oriented names:

```text
IIdentityClient
IOrdersClient
IBillingClient
IInvoicesClient
```

instead of implementation-oriented names:

```text
IServiceAClient
IBackendClient
IApiV2Client
```

Likewise, operation names should expose intent clearly:

```text
RevokeUserSessionsAsync
CancelInvoiceAsync
ReserveInventoryAsync
```

This allows a coding agent to search the repository by business concepts.

Example reasoning:

```text
Requirement:
"When an employee is disabled, invalidate all login sessions."

↓ search for:
session
revoke session
identity

↓ find:
IIdentityClient

↓ inspect methods:
RevokeUserSessionsAsync

↓ generate:
await identityClient.RevokeUserSessionsAsync(...)
```

The repository itself becomes a semantic index of available capabilities.

---

## Repository Guidance for Agents

The agent should be explicitly told how external integrations are organized.

For example, an `AGENTS.md`, repository instruction, or coding skill may contain:

```text
When integrating with another service:

1. Search existing generated clients by business concept.
2. Inspect method names and documentation.
3. Prefer generated clients over direct HTTP calls.
4. If the correct operation is unclear, inspect the source OpenAPI specification.
5. Do not invent endpoint URLs or construct REST requests manually when a generated client exists.
```

The instruction tells the agent **how to discover and use capabilities**.

The OpenAPI specification tells it **which capabilities exist and what they mean**.

These are different responsibilities.

---

## OpenAPI Does Not Always Need to Be Read Directly

If the generated client is well named and well documented, the coding agent may not need to inspect `swagger.json` for every task.

In the common case:

```text
Business requirement
        ↓
Search generated clients
        ↓
Inspect documented methods
        ↓
Generate code
```

OpenAPI remains the authoritative contract and can be consulted when additional details are needed.

For example:

- detailed error responses,
    
- optional parameters,
    
- lifecycle constraints,
    
- response schemas,
    
- operation semantics not fully exposed by the generated client.
    

Therefore, a useful hierarchy is:

```text
OpenAPI
   ↓
Generated typed client
   ↓
Generated documentation/comments
   ↓
Coding agent
```

---

## Error Responses Should Also Be Semantic

Avoid responses such as:

```json
{
  "errorCode": 3817
}
```

Prefer errors that expose the state and possible resolution:

```json
{
  "code": "invoice_already_issued",
  "message": "Issued invoices cannot be deleted.",
  "suggestedOperation": "cancelInvoice"
}
```

This is useful both for generated application code and for an LLM trying to understand the intended workflow.

---

## The Same Principle Applies Beyond REST

The same architecture can be applied to other integration styles.

### GraphQL

Use:

- well-described schema fields,
    
- meaningful query and mutation names,
    
- introspection,
    
- generated typed GraphQL clients.
    

Example:

```graphql
"""
Cancels an issued invoice while preserving it for audit.
Do not use for draft invoices.
"""
cancelInvoice(id: ID!): Invoice!
```

### Messaging

Use message contracts plus AsyncAPI.

For example:

```text
RevokeUserSessions
```

should be clearly distinguishable from:

```text
UserSessionsRevoked
```

The first may be a command that application code sends.

The second is an event produced as a result of processing that command.

AsyncAPI can describe:

- messages,
    
- payload schemas,
    
- channels/topics,
    
- send/receive direction,
    
- headers,
    
- operation semantics.
    

A coding agent can then generate or discover the correct publisher abstraction.

---

## Preferred Architecture

A good integration architecture for LLM-generated code is:

```text
                       Business requirement
                                ↓
                           Coding agent
                                ↓
                 Discover business capability
                                ↓
                     Strongly typed interface
                                ↓
           ┌────────────────────┼────────────────────┐
           │                    │                    │
        OpenAPI             GraphQL              AsyncAPI
           │                    │                    │
         REST                GraphQL             Messaging
```

The important abstraction presented to the coding agent should usually be a **typed, semantically named application client**.

Transport details should remain underneath it.

---

## Core Principle

A useful rule is:

> External integrations should expose well-documented formal contracts, generate strongly typed clients from those contracts, and make those clients easy for coding agents to discover by business capability.

The coding agent should prefer those generated clients over constructing transport-level calls directly.

A well-designed API therefore becomes more than a machine-readable protocol description.

It becomes part of the semantic environment from which the LLM can infer:

- what capabilities exist,
    
- which capability matches the requested business operation,
    
- how it should be called,
    
- and which operations must not be confused with one another.

---

# Reference Note: Designing Software Architecture with LLM Assistance

---
title: Designing Software Architecture with LLM Assistance
tags:
  - software-architecture
  - system-design
  - ai-agents
  - llm
  - decision-making
  - tradeoff-analysis
aliases:
  - LLM-Assisted Software Architecture
  - Architecture Exploration with AI
---

## Core idea

LLMs can significantly accelerate architectural exploration, but they are not reliable guarantees of completeness.

They are good at:

- exploring unfamiliar technologies,
    
- generating design alternatives,
    
- extracting constraints from available context,
    
- comparing trade-offs,
    
- producing prototypes,
    
- identifying common risks,
    
- reviewing an existing proposal.
    

They are weaker at:

- discovering constraints that were never documented,
    
- recognizing questions that neither the user nor the model knows should be asked,
    
- distinguishing a true requirement from an accidental property of the current implementation,
    
- understanding organizational and domain knowledge that exists only in people’s heads,
    
- reliably signaling that the problem description is incomplete.
    

The main risk is not only hallucination.

A more subtle risk is that the model fills missing information with a plausible, typical scenario. The result may be coherent and professionally justified, even though it depends on assumptions that were never confirmed.

This creates an illusion of completeness.

---

## The model may provide a plausible answer instead of revealing missing knowledge

When the description is incomplete, an LLM tends to complete the story.

For example, it may implicitly assume that:

- eventual consistency is acceptable,
    
- operations are idempotent,
    
- messages may be retried safely,
    
- status transitions are linear,
    
- no external system reads the database directly,
    
- a relational database is suitable,
    
- rolling deployments do not create compatibility problems.
    

These assumptions may be reasonable in a typical system, but they may be false in the actual one.

The dangerous part is that a reasonable answer can look like an evidence-based answer.

A model can generate:

- a clean architecture,
    
- a detailed justification,
    
- diagrams,
    
- migration steps,
    
- code,
    
- a list of advantages and disadvantages.
    

This can make the user accept the proposal without examining the assumptions behind it.

Therefore:

> A fluent and internally consistent answer should not be treated as evidence that the problem was understood completely.

---

## Constraints may come from business logic

Technical constraints often originate in business requirements.

The reasoning chain should be:

```text
Business requirement
→ required system property
→ architectural constraint
→ technology choice
```

Examples:

```text
Business rule:
A customer must never be charged twice.

Required property:
Duplicate execution must be safe or prevented.

Architectural consequence:
Idempotency, deduplication, transactional boundaries, or unique operation identifiers are required.
```

```text
Business rule:
The user must immediately know whether a reservation succeeded.

Required property:
The result cannot rely only on eventual consistency.

Architectural consequence:
A purely asynchronous workflow may be insufficient.
```

```text
Business rule:
The organization must reconstruct why a decision was made years later.

Required property:
Historical state and decision inputs must be preserved.

Architectural consequence:
Audit records, versioning, immutable logs, or event history may be required.
```

A technology choice such as a database type may therefore be derived from the domain rather than being a purely technical preference.

At the same time, a stated constraint such as “we must use SQL Server” should be questioned.

It may represent:

- a real organizational standard,
    
- existing expertise,
    
- licensing constraints,
    
- integration dependencies,
    
- transactional requirements,
    
- direct reporting access,
    
- or only historical habit.
    

The model should ask what underlying requirement makes the constraint necessary.

---

## Categories of constraints

It is useful to divide constraints into three groups.

### Explicit constraints

These are written in:

- requirements,
    
- tickets,
    
- documentation,
    
- ADRs,
    
- contracts,
    
- security policies.
    

The model can usually handle them well if they are clearly provided.

### Discoverable constraints

These are not explicitly documented, but can be inferred from:

- code,
    
- tests,
    
- schemas,
    
- deployment manifests,
    
- integrations,
    
- production data,
    
- telemetry,
    
- incident history.
    

Finding them requires a dedicated discovery phase.

### Hidden constraints

These exist only in:

- people’s experience,
    
- manual processes,
    
- informal agreements,
    
- organizational politics,
    
- undocumented customer behavior,
    
- historical exceptions.
    

The model cannot discover them unless some trace of them is available.

This is the most dangerous category.

---

## Do not start with architecture selection

A weak process is:

```text
Problem description
→ architecture proposal
→ implementation
```

A stronger process is:

```text
Problem description
→ confirmed facts
→ missing information
→ assumptions
→ required system properties
→ design alternatives
→ attempt to invalidate alternatives
→ conditional recommendation
→ implementation
```

The first phase should be constraint discovery, not solution generation.

The model should first identify:

- what is known,
    
- what is inferred,
    
- what is assumed,
    
- what is unknown,
    
- what can be interpreted in multiple ways,
    
- what information could reverse the decision.
    

Only then should it propose technologies or architecture.

---

## Separate facts, inferences, assumptions, and unknowns

Important design analysis should not be presented as one continuous narrative.

A useful classification is:

### Confirmed fact

Supported by a trusted source.

Example:

> Deployments are rolling and old instances may run for up to thirty minutes.

### Inference

Logically derived from confirmed facts.

Example:

> Database changes must remain compatible with both application versions.

### Assumption

Used temporarily because information is missing.

Example:

> No external reporting system reads the modified table directly.

### Unknown

Not yet established.

Example:

> Whether message ordering must be preserved across all customers.

### Typical practice

A common recommendation that may not apply here.

Example:

> Using a message broker for long-running operations.

This classification prevents plausible assumptions from silently becoming requirements.

---

## Ask what could reverse the recommendation

One of the most valuable questions is:

> Which missing information could make your recommendation completely different?

Other useful questions include:

- Under what conditions is this solution wrong?
    
- Which assumption has the greatest effect on the decision?
    
- What did you assume even though I did not provide it?
    
- What must be true for this design to work?
    
- Which of those conditions have not been verified?
    
- What system property would make another alternative preferable?
    
- Which parts of the recommendation come from my context, and which come from generic best practices?
    

A good recommendation should be conditional.

For example:

> If delayed consistency is acceptable, operations are idempotent, and the team can operate the broker, asynchronous messaging is a strong option. If the user requires an immediate authoritative result, a synchronous transactional path may be more appropriate.

This is more useful than declaring one architecture universally best.

---

## Ask for the whole solution space, not only several technologies

When asked for “a few options,” the model may generate several variations of the same idea.

Instead, request options from different strategic categories:

- the simplest solution,
    
- a solution using existing infrastructure,
    
- an incremental solution,
    
- a reversible experiment,
    
- a conservative solution,
    
- a long-term target architecture,
    
- a less obvious but realistic option,
    
- a non-technical process change,
    
- changing or removing the requirement,
    
- doing nothing for now.
    

For every option, require:

- applicability conditions,
    
- assumptions,
    
- benefits,
    
- risks,
    
- operational cost,
    
- migration path,
    
- rollback difficulty,
    
- validation method,
    
- information that could change its evaluation.
    

---

## The model may prefer solutions it can implement comfortably

Even when the user asks a neutral question and does not suggest an answer, the resulting recommendation is not necessarily neutral.

An LLM tends to favor solutions that are:

- common in its training data,
- well documented,
- represented by many public examples,
- easy to explain using familiar patterns,
- easy for the model to turn into plausible code.

The model does not have to consciously decide, “I will choose this because I can implement it.” The bias arises indirectly:

```text
Familiar and high-probability approach
→ proposed more often
→ justified more fluently
→ implemented more successfully by the same model
```

This correlation is useful, because implementability matters. However, it can also narrow the solution space.

> The solution the model can describe and generate most confidently is not necessarily the solution that best fits the problem.

### Earlier context can anchor the recommendation

The bias can be triggered by merely mentioning a technology earlier in the conversation.

For example, if SQL Server, Kafka, Temporal, Kubernetes, microservices, or event sourcing appeared anywhere in the preceding discussion, the model may assign that technology more importance than it deserves. It may interpret the mention as:

- an implicit preference,
- an available part of the infrastructure,
- a constraint that should be preserved,
- evidence that the user expects the technology to be used,
- or the intended direction of the conversation.

This can happen even when the technology was mentioned only as an example, comparison point, rejected idea, or unrelated background detail.

The effect is a form of contextual anchoring:

```text
Technology appears in the context
→ becomes more available during generation
→ shapes the alternatives and evaluation criteria
→ is more likely to be recommended
```

Therefore, a neutral-sounding question asked after discussing a specific technology is not fully context-neutral. The model may produce a high-quality answer to the solution space implied by the conversation rather than reconsidering the entire solution space from first principles.

To reduce contextual anchoring:

- state explicitly that previously mentioned technologies are examples, not requirements,
- ask the model to solve the problem once without using any technologies already mentioned,
- request alternatives derived only from confirmed requirements,
- ask which recommendations would disappear if the earlier technology names were removed from the conversation,
- use a fresh context or an independent reviewer for important decisions,
- distinguish technologies that are required, available, preferred, merely considered, and explicitly rejected.

A useful instruction is:

> Treat every previously mentioned technology as non-binding unless it appears in the confirmed constraints. Derive the required system properties first, then generate alternatives without privileging technologies already present in the conversation.

A particularly risky workflow is:

```text
The model selects the criteria
→ selects the technology
→ justifies its own selection
→ implements it
→ reviews its own result
```

The entire chain may be internally consistent while optimizing for an unverified interpretation of the problem. A convincing implementation can then be mistaken for evidence that the architectural choice was correct.

To reduce this bias:

- separate solution selection from implementation,
- ask for alternatives from genuinely different strategic categories,
- require the model to distinguish problem fit from its confidence in implementation,
- explicitly include less familiar or harder-to-generate approaches when they may fit the constraints,
- let a human define or approve the evaluation criteria,
- use an independent review that does not inherit the original recommendation as a fact,
- evaluate the architecture before showing how easily code can be generated for it.

A useful question is:

> Is this solution recommended because it best satisfies the confirmed constraints, or because it is popular, well documented, and easy for the model to implement?

The model cannot perfectly inspect its own internal reasoning, so its answer should not be treated as proof. The question is still valuable because it forces an explicit comparison between problem fit, ecosystem familiarity, and implementation confidence.

For important decisions, ask the model to report these dimensions separately:

| Dimension | Question |
| --- | --- |
| Problem fit | How well does the option satisfy confirmed requirements and constraints? |
| Evidence quality | Which parts are supported by project evidence rather than generic practice? |
| Implementation confidence | How reliably can the model produce and test the implementation? |
| Ecosystem familiarity | Is the recommendation favored because examples and documentation are abundant? |
| Decision uncertainty | Which missing information could change the ranking? |

Implementation confidence is a legitimate criterion, but it should be visible and weighted deliberately rather than silently determining the architecture.

---


## Review the problem across multiple dimensions

A model should be asked to inspect the problem from several perspectives, not only technology selection.

Useful dimensions include:

- business rules and invariants,
    
- state transitions,
    
- data ownership,
    
- consistency,
    
- transactions,
    
- concurrency,
    
- ordering,
    
- duplication and idempotency,
    
- retries and timeouts,
    
- partial failures,
    
- integration contracts,
    
- version compatibility,
    
- deployment strategy,
    
- rollback,
    
- migration,
    
- security and trust boundaries,
    
- privacy,
    
- auditability,
    
- retention,
    
- performance,
    
- scale,
    
- observability,
    
- diagnostics,
    
- operational support,
    
- cost,
    
- team expertise,
    
- vendor lock-in,
    
- reversibility.
    

The purpose is not to generate an enormous checklist for every decision.

The purpose is to identify which dimensions can materially change this specific decision.

---

## Use the model in multiple roles

A single model can be prompted to perform different reviews.

### Domain analyst

Extracts:

- business rules,
    
- actors,
    
- invariants,
    
- states,
    
- exceptions,
    
- ambiguous behavior.
    

### Architect

Generates design alternatives and trade-offs.

### Skeptic

Searches for:

- hidden assumptions,
    
- missing constraints,
    
- failure scenarios,
    
- cases that invalidate the recommendation.
    

### Operator

Checks:

- deployment,
    
- monitoring,
    
- rollback,
    
- support procedures,
    
- failure recovery,
    
- maintenance cost.
    

### Security reviewer

Checks:

- trust boundaries,
    
- sensitive data,
    
- authorization,
    
- abuse scenarios,
    
- compliance implications.
    

### Migration reviewer

Checks:

- old and new versions running together,
    
- schema compatibility,
    
- staged rollout,
    
- backfill,
    
- rollback,
    
- external consumers.
    

Using multiple roles does not make the model automatically correct.

It forces the reasoning to be examined from different angles.

---

## Exploration mode and commitment mode

LLMs are especially valuable because they reduce the cost of experimentation.

They allow teams to:

- explore unfamiliar approaches,
    
- build prototypes quickly,
    
- compare several options,
    
- generate test harnesses,
    
- simulate migrations,
    
- investigate new libraries,
    
- prepare disposable proofs of concept.
    

This supports a more experimental architecture process:

```text
Hypothesis
→ cheap prototype
→ measurement
→ criticism
→ decision
```

However, fast implementation must not be confused with understanding.

The model greatly reduces the cost of entering a new solution, but may not equally reduce the cost of understanding:

- its failure model,
    
- operational complexity,
    
- long-term maintenance,
    
- migration difficulty,
    
- scaling behavior,
    
- guarantees and limitations,
    
- organizational impact.
    

Therefore it is useful to distinguish two modes.

### Exploration mode

Optimize for speed and learning.

- Generate many ideas.
    
- Try unfamiliar technologies.
    
- Accept explicitly labeled temporary assumptions.
    
- Build disposable prototypes.
    
- Avoid production-level completeness.
    
- Prefer reversible experiments.
    

### Commitment mode

Optimize for correctness and reversibility.

- Confirm constraints.
    
- Verify primary documentation.
    
- Test failures and edge cases.
    
- Review operational requirements.
    
- Remove hidden assumptions.
    
- Plan migration and rollback.
    
- Record the architecture decision.
    
- Require human approval.
    

The dangerous transition is when an exploration prototype silently becomes production architecture.

---

## The best role of the model

The model should not be treated as an authority that produces the architecture.

It is better used as an accelerator for:

- knowledge exploration,
    
- question generation,
    
- constraint discovery,
    
- option generation,
    
- trade-off analysis,
    
- prototype creation,
    
- adversarial review,
    
- documentation,
    
- verification planning.
    

The human remains responsible for confirming the model of reality on which the architecture depends.

The most important question is not:

> Did the model produce a reasonable solution?

It is:

> Is the solution based on confirmed properties of this system, or on plausible defaults borrowed from typical systems?

---

## Practical conversation pattern

### Phase 1: problem discovery

Ask the model not to design anything yet.

Request:

- confirmed facts,
    
- inferred consequences,
    
- assumptions,
    
- unknowns,
    
- ambiguities,
    
- missing dimensions,
    
- questions ranked by decision impact.
    

### Phase 2: constraint verification

For each important claim, identify:

- its source,
    
- confidence,
    
- effect on the architecture,
    
- method of verification.
    

### Phase 3: option generation

Generate alternatives from meaningfully different categories.

Do not allow an unconditional recommendation.

### Phase 4: adversarial review

Assume each proposal is wrong.

Search for:

- domain properties that invalidate it,
    
- partial failure scenarios,
    
- hidden consumers,
    
- deployment problems,
    
- migration traps,
    
- operational costs,
    
- POC-to-production gaps.
    

### Phase 5: conditional recommendation

State:

- the preferred option,
    
- the assumptions under which it is preferred,
    
- the conditions that would change the recommendation,
    
- unresolved risks,
    
- required experiments or measurements.
    

### Phase 6: implementation

Provide the implementing agent with:

- business goal,
    
- global invariants,
    
- approved architecture,
    
- local module context,
    
- neighboring contracts,
    
- known assumptions,
    
- required tests,
    
- prohibited changes.
    

---

## Reusable prompt: discovery before design

```text
Help me analyze this architecture problem, but do not propose a solution yet.

First, separate the available information into:

- confirmed facts,
- conclusions derived from those facts,
- working assumptions,
- missing information,
- typical practices that may not apply to this system.

Do not fill missing information with standard assumptions without labeling them explicitly.

Identify all important dimensions of the problem, including dimensions I may not know to ask about:

- business rules and invariants,
- data and consistency,
- transactions and concurrency,
- ordering, retries, and idempotency,
- partial failures,
- integrations,
- performance and scale,
- security and privacy,
- audit and retention,
- deployment, migration, and rollback,
- observability and operations,
- cost and team expertise.

Prepare the questions whose answers could materially change the architecture decision. Rank them by impact.

Also identify:

- assumptions you would otherwise make from the description,
- the riskiest assumptions,
- missing information that could completely reverse the recommendation,
- questions that an inexperienced person might not know to ask.

Stop after the problem analysis and questions. Do not select technologies or architecture yet.
```

---

## Reusable prompt: generating alternatives

```text
Based only on confirmed facts and explicitly stated assumptions, generate meaningfully different solution options.

Include:

- the simplest option,
- an option using the current system,
- an incremental option,
- a reversible option,
- a conservative option,
- a long-term target option,
- a less obvious but realistic option,
- changing the requirement or avoiding a technical solution.

For each option, provide:

1. What it solves.
2. The conditions it requires.
3. Its assumptions.
4. When it is a good choice.
5. When it is a bad choice.
6. Costs and risks.
7. Operational consequences.
8. Migration and rollback difficulty.
9. A cheap experiment that could validate it.
10. Missing information that could change its evaluation.

Do not present any option as unconditionally best.
```

---

## Reusable prompt: adversarial review

```text
Assume the proposed solution is wrong.

Find:

- hidden assumptions,
- missing constraints,
- edge cases,
- unusual domain properties,
- concurrency problems,
- partial failures,
- retry and duplication issues,
- migration and deployment risks,
- operational costs,
- organizational dependencies,
- cases where the solution works in a proof of concept but fails in production.

Then answer:

1. What must be true for the solution to work?
2. Which of those conditions have not been verified?
3. What could completely reverse the recommendation?
4. What tests, measurements, documents, code analysis, or stakeholder conversations would verify the assumptions?
5. Which parts come from the actual context, and which come only from generic best practices?
```

---

## Final mental model

An LLM answer is not the architecture.

It is a proposal generated from a model of the system.

That model contains:

- facts,
    
- inferred consequences,
    
- assumptions,
    
- omissions,
    
- generic patterns.
    

The first task is therefore not to validate the proposed technology.

The first task is to validate the model of reality that produced the proposal.

LLMs make it possible to explore more options, learn faster, and run cheaper experiments. They should increase the amount of reversible experimentation, not the amount of irreversible architectural risk.

---

# Reference Note: Developing Features with AI Coding Agents

---
title: Developing Features with AI Coding Agents
tags:
  - ai-agents
  - software-engineering
  - agentic-workflows
  - feature-development
  - testing
  - code-review
aliases:
  - Feature Development with Agents
  - End-to-End Agentic Feature Lifecycle
---

## A Strong Workflow for Larger Features

A useful process is:

```text
repository analysis
→ behavioral specification
→ examples and decision tables
→ acceptance tests
→ human review
→ implementation of one vertical slice
→ architectural review
→ full implementation
→ independent skeptical review
→ documentation update
```

### Step 1: Repository Analysis

The agent should first locate:

- existing business flows,
    
- data models,
    
- integration points,
    
- transactions,
    
- existing tests,
    
- compatibility risks,
    
- hidden assumptions.
    

It should not modify the code yet.

### Step 2: Behavioral Specification

The specification should include:

- business objective,
    
- terminology,
    
- rules,
    
- exceptions,
    
- negative cases,
    
- side effects,
    
- compatibility requirements,
    
- non-functional constraints,
    
- explicit out-of-scope items.
    

### Step 3: Tests Before Implementation

The agent can prepare:

- business-rule tests,
    
- acceptance tests,
    
- regression tests,
    
- API contract tests,
    
- integration tests.
    

New tests may initially fail. That confirms that they detect the missing behavior.

### Step 4: Human Review of Meaning

The reviewer should not focus only on test implementation quality.

The main questions are:

- Does the test describe the correct business behavior?
    
- Did the agent invent an unstated rule?
    
- Are negative cases present?
    
- Are priorities between rules correct?
    
- Is the test coupled to one implementation unnecessarily?
    
- Does the test preserve an accidental legacy behavior?
    

### Step 5: Freeze the Acceptance Contract

The implementing agent should not freely modify approved acceptance tests.

It may add technical tests, but changes to the accepted business contract require another review.

### Step 6: Implement a Small Vertical Slice

Instead of generating the whole feature at once, implement one full path from entry point to result.

This reveals whether the architecture is appropriate before dozens of files are created.

---

## Tests Are Executable Specifications, but Not Complete Specifications

A test demonstrates an expected example.

It does not always explain:

- why the rule exists,
    
- what a domain term means,
    
- what must not be simplified,
    
- why two similar cases differ,
    
- which behavior is historical but still required.
    

The strongest combination is:

```text
business decision
+ examples or decision table
+ acceptance tests
+ explicit implementation
```

The agent should not be allowed to define both the implementation and the meaning of correctness without independent human review.

Otherwise, it can write tests that confirm its own incorrect interpretation.

---

## Practical Working Rules

### For feature development

- Analyze before modifying.
    
- Write or approve the behavioral specification.
    
- Use examples and decision tables.
    
- Review acceptance tests before implementation.
    
- Freeze approved business tests.
    
- Implement one vertical slice first.
    
- Separate mechanical changes from business changes.
    
- Require a skeptical second review.

---

# Reference Note: Hidden Abstractions May Become More Expensive in Agent-Maintained Code

---
title: Hidden Abstractions May Become More Expensive in Agent-Maintained Code
tags:
  - software-architecture
  - ai-agents
  - abstraction
  - code-maintainability
  - simplicity
  - software-engineering
aliases:
  - Cost of Hidden Abstractions with Agents
  - Explicit vs Magic Abstractions in AI Era
---

Modern software engineering often tries to remove repetitive concerns from local code.

Instead of explicitly writing validation, authorization, retries, transactions, logging, tracing, error mapping, and other infrastructure in every operation, we move them into reusable mechanisms such as:

- middleware,
    
- interceptors,
    
- decorators,
    
- dependency injection,
    
- HTTP message handlers,
    
- framework filters,
    
- MediatR behaviors,
    
- Entity Framework interceptors and query filters,
    
- global exception handling,
    
- conventions,
    
- assembly scanning,
    
- ambient context.
    

This can make individual methods extremely small.

For example:

```csharp
public Task<Response> GetOrder(GetOrderRequest request)
{
    return mediator.Send(request);
}
```

The method appears simple.

However, the actual execution may look more like:

```text
HTTP request
→ authentication middleware
→ authorization middleware
→ exception middleware
→ request validation
→ MediatR
→ logging behavior
→ transaction behavior
→ handler
→ Entity Framework query filter
→ database interceptor
→ SQL
→ response mapping
→ serialization
```

The local code is simple, but the semantics are not.

This distinction may become increasingly important when software is primarily modified by agents.

## Local Simplicity Is Not the Same as Semantic Simplicity

An agent working on a method must understand more than the code visible inside the method.

Consider:

```csharp
await httpClient.SendAsync(request);
```

The request may implicitly include:

- authentication headers,
    
- correlation identifiers,
    
- retry policies,
    
- circuit breakers,
    
- timeouts,
    
- telemetry,
    
- logging,
    
- tenant context.
    

The important behavior is distributed across configuration and framework mechanisms.

Similarly:

```csharp
context.Orders.ToListAsync();
```

may actually mean:

```text
load Orders
where TenantId == CurrentTenant
excluding soft-deleted records
using an interceptor-defined database command behavior
```

because of global query filters and other Entity Framework configuration.

The problem is therefore not simply abstraction.

The deeper problem is **non-local semantics**.

The meaning of a line of code depends on code that is not locally visible.

## Hidden Execution Context Is Particularly Difficult

Some dependencies are not passed explicitly at all.

They may come from:

```text
HttpContext
AsyncLocal
Activity.Current
ClaimsPrincipal
current tenant services
current culture
scoped dependency resolution
feature flags
environment configuration
```

A method can therefore appear to depend on:

```csharp
Process(Order order)
```

while its real inputs include:

```text
order
current user
tenant
feature configuration
current transaction
request metadata
culture
authorization context
```

This makes the true dependency graph much larger than the function signature suggests.

Humans often tolerate this because experienced developers gradually learn the architecture.

An agent entering a repository for a single task must rediscover it.

## Dynamic Dependency Injection Makes the Problem Worse

Constructor injection itself is usually relatively easy to understand.

The situation becomes more difficult when implementations depend on runtime context:

```csharp
services.AddScoped<IPriceCalculator>(sp =>
{
    var context = sp.GetRequiredService<OperationContext>();

    return context.Channel switch
    {
        Channel.Web => new WebPriceCalculator(),
        Channel.Api => new ApiPriceCalculator(),
        _ => new DefaultPriceCalculator()
    };
});
```

Local code may only contain:

```csharp
priceCalculator.Calculate(order);
```

but the implementation that actually runs depends on external state.

Similar problems appear with:

- keyed services,
    
- decorators,
    
- assembly scanning,
    
- open generic registrations,
    
- conditional registration,
    
- plugin architectures.
    

The call site no longer tells the agent what code it is calling.

## Interceptors and Pipelines Can Hide Business-Relevant Semantics

Cross-cutting abstractions become especially problematic when they contain behavior that changes the meaning of an operation.

A call such as:

```csharp
repository.Save(order);
```

may secretly perform:

```text
authorization
→ validation
→ transaction creation
→ audit logging
→ persistence
→ event publication
→ cache invalidation
```

Some of these are infrastructure concerns.

Others are part of the operation's semantics.

The distinction matters.

A generic timing metric being invisible is usually harmless.

A transaction boundary, retry policy, tenant filter, authorization rule, or business validation being invisible can fundamentally change how an agent should modify the operation.

## Agents May Change the Economics of Explicit Code

Traditional software engineering strongly rewards removing repetition.

The reasoning is understandable:

```text
duplication
→ more code
→ more maintenance
→ more opportunities for inconsistency
```

This encourages patterns such as:

```text
DRY
→ centralize behavior
→ hide repeated mechanics behind abstractions
```

But agents reduce the cost of producing and maintaining repetitive code.

This creates the possibility of a different tradeoff:

```text
some duplication
→ greater semantic locality
→ easier reasoning
→ safer automated modification
```

The goal does not need to be eliminating abstractions.

It may instead be eliminating **invisible semantics**.

## Explicit Execution Pipelines

One possible direction is to make important operation semantics visible directly in the operation definition.

Instead of:

```csharp
return mediator.Send(request);
```

an operation might resemble:

```csharp
return Operation
    .From(request)
    .Validate<GetOrderValidator>()
    .Authorize<ReadOrderPolicy>()
    .Retry(ExternalPolicies.Read)
    .Execute<GetOrderHandler>()
    .ValidateResponse<GetOrderResponseValidator>()
    .MapErrors<OrderHttpErrors>()
    .Return();
```

The exact syntax is not important.

The important property is that the execution graph becomes visible:

```text
request
→ validation
→ authorization
→ retry policy
→ execution
→ response validation
→ error mapping
→ response
```

An agent can reason about the operation without reconstructing several layers of framework configuration.

## This Does Not Mean Eliminating All Abstraction

Some abstractions should remain hidden.

For example, an ASP.NET action can reasonably receive:

```csharp
GetOrderRequest request
```

without explicitly handling:

```text
TCP
HTTP parsing
TLS
UTF-8
JSON tokenization
object allocation
deserialization
```

These are implementation mechanisms.

The operation usually does not care how the DTO was produced.

Similarly, returning a response object does not require the business operation to explicitly handle HTTP serialization or socket writes.

A useful boundary may therefore be:

```text
framework owns mechanics
operation owns semantics
```

The framework can hide how input becomes a DTO.

The operation should make visible the decisions that influence what the operation means.

## Infrastructure Can Be Implicit More Safely Than Business Semantics

Not all hidden behavior has the same cost.

Relatively safe candidates for implicit handling include:

```text
generic logging
tracing
request timing
metrics
compression
correlation IDs
serialization
```

More dangerous hidden behavior includes:

```text
authorization
tenant selection
business validation
transaction boundaries
retry behavior
idempotency
cache semantics
feature flags
currency or locale selection
handler selection
error interpretation
```

A possible rule is:

> Infrastructure may be implicit. Business-relevant semantics should preferably be explicit.

The boundary will not always be perfect, but it provides a useful design direction.

## Global Configuration Still Has Value

Making behavior explicit does not require copying implementation details into every operation.

For example, retry may still be centrally configured:

```csharp
RetryPolicies.ExternalRead
```

could define:

```text
3 attempts
exponential backoff
jitter
retry on timeout
retry on HTTP 502/503/504
```

while the operation only says:

```csharp
.Retry(RetryPolicies.ExternalRead)
```

This separates two different concerns:

```text
local code:
WHAT semantic policy applies

central configuration:
HOW that policy works
```

This may be a particularly useful compromise.

Global configuration defines reusable policy.

The call site explicitly declares that the policy participates in the operation.

## Named Semantics Are Better Than Silent Global Behavior

Compare:

```csharp
await client.SendAsync(request);
```

where retry is silently injected by global `HttpClient` configuration,

with:

```csharp
await request
    .Retry(RetryPolicies.ExternalRead)
    .Execute();
```

The second version still uses abstraction.

However, the abstraction leaves a visible semantic trace.

The agent immediately knows that:

```text
this operation may execute more than once
```

That knowledge can affect decisions about:

- idempotency,
    
- database writes,
    
- external side effects,
    
- request identifiers,
    
- duplicate handling.
    

The exact implementation of retry remains reusable and centrally controlled.

## Large Applications Already Struggle With Truly Global Policies

This approach may also address a problem that exists even without AI.

In a large system containing:

```text
hundreds of endpoints
many modules
multiple databases
different external integrations
different SLA requirements
different business risks
```

a single global policy is rarely actually global.

It gradually becomes:

```text
default behavior
except Payments
except Reporting
except legacy integration
except bulk operations
except endpoint X
unless attribute Y exists
unless interface Z is implemented
```

The centralized configuration eventually becomes another complex program.

The apparent simplicity of each endpoint is paid for by complexity elsewhere.

Module-level or operation-class policies may therefore scale better:

```text
system defaults
→ module defaults
→ operation category
→ explicit operation override
```

For example:

```text
Catalog:
    external reads may retry

Payments:
    commands do not retry unless explicitly idempotent

Reporting:
    long timeout
    read-only transaction semantics
```

The policy implementation remains centralized, while the semantic choice stays close to the operation.

## Abstractions Could Become Mechanically Expandable

There is another possible solution that does not require removing existing abstractions.

Future frameworks and development tools could expose the resolved semantics of an operation.

The source might contain:

```csharp
.Retry(RetryPolicies.ExternalRead)
```

while an agent can request:

```text
resolve RetryPolicies.ExternalRead
```

and receive:

```text
max attempts: 3
backoff: exponential
jitter: enabled
retry:
  timeout
  502
  503
  504
```

The same mechanism could resolve an entire endpoint:

```text
GetOrder

authentication:
    required

authorization:
    ReadOrderPolicy

validation:
    GetOrderValidator

tenant:
    request tenant

transaction:
    read-only

retry:
    ExternalRead
    attempts: 3

handler:
    GetOrderHandler

cache:
    OrderById
    TTL: 5 minutes
```

This suggests an important property for future abstractions:

> Abstractions should be mechanically expandable.

Documentation is useful.

A machine-readable resolved execution model is much more useful to an agent.

## Good Abstractions for Agents May Optimize for Different Things

Traditional APIs often optimize for:

```text
few lines
few parameters
minimal boilerplate
maximum reuse
```

Agent-oriented APIs may increasingly optimize for:

```text
semantic locality
explicit dependencies
visible execution flow
mechanically discoverable behavior
predictable composition
```

This does not imply that code must become low-level.

For example:

```csharp
.RetryTransient(3)
```

is still an abstraction.

It hides backoff implementation, timers, exception matching, and scheduling.

But it preserves the fact that matters semantically:

```text
the operation may execute multiple times
```

By contrast:

```csharp
.ExecuteUsingStandardEnterprisePolicies()
```

may hide almost everything the agent needs to know.

A useful distinction is therefore:

> A good abstraction reduces syntax without hiding important semantics.


## Business Meaning Should Be Encoded in the Same Vocabulary

Semantic locality is not only about where behavior executes.

It is also about whether the code uses the same concepts and vocabulary as the domain, documentation, API contracts, database schema, tests, and operational descriptions.

Consider:

```csharp
if (payment != null)
{
    ...
}
```

In a particular system, this may implicitly mean:

```text
the invoice is unpaid
```

A developer who has worked on the system for years may know that convention.

An agent may not.

The agent sees evidence:

```text
Payment exists
```

but must infer the business conclusion:

```text
invoice is unpaid
```

That inference may be correct, incorrect, or missed entirely.

Compare that with:

```csharp
if (payment.Status == PaymentStatus.Unpaid)
{
    ...
}
```

or:

```csharp
if (payment.IsUnpaid)
{
    ...
}
```

Now the business concept is explicitly represented in the code.

This matters particularly when the same concept appears elsewhere in the system.

Suppose the documentation says:

```text
retry unpaid payments
```

the API specification contains:

```text
paymentStatus: unpaid
```

and tests are named:

```text
ShouldRetryUnpaidPayment
```

An agent searching for or reasoning about "unpaid payment" can directly associate all of these artifacts with:

```csharp
PaymentStatus.Unpaid
```

It has a much weaker semantic connection to:

```csharp
payment != null
```

The same problem appears with sentinel values and technical representations:

```csharp
amount == 0
endDate == null
retryCount == -1
status == 2
customerId != null
```

These values may encode business meanings such as:

```text
free
active
unlimited retries
awaiting payment
customer assigned
```

but the meaning is not present in the expression itself.

A more agent-friendly model exposes the conclusion:

```csharp
price.IsFree
subscription.IsActive
retryPolicy.IsUnlimited
payment.Status == PaymentStatus.Unpaid
order.HasAssignedCustomer
```

This suggests a broader rule:

> Prefer code that encodes business conclusions rather than only technical evidence from which those conclusions must be inferred.

The principle extends beyond source code.

Ideally, the same domain vocabulary should appear consistently in:

```text
domain model
API contracts
database schema
tests
documentation
events and messages
logs and telemetry
```

For example:

```text
Documentation:
    unpaid payment

Code:
    PaymentStatus.Unpaid

API:
    paymentStatus = "unpaid"

Database:
    payment_status = "unpaid"

Event:
    PaymentBecameUnpaid

Test:
    ShouldRetryUnpaidPayment
```

This creates **semantic alignment across artifacts**.

For an agent, that alignment has several benefits:

- repository search becomes more reliable,
- embeddings and RAG retrieval are more likely to connect relevant artifacts,
- documentation can be mapped to implementation more directly,
- fewer hidden conventions must be reconstructed,
- code review requires less inference,
- generated changes are more likely to use the correct business concept.

Comments can help:

```csharp
// A non-null Payment means the invoice has not been paid yet.
if (payment != null)
```

but comments are weaker than encoding the meaning in the model itself.

They can become stale, they may not participate in all tooling, and they still leave the underlying representation semantically indirect.

Documentation or schema descriptions are also useful when the technical representation cannot be changed.

For example, if a legacy database uses:

```text
payment_state = 2
```

then the schema or mapping layer should make the meaning mechanically discoverable:

```text
2 = unpaid
```

or preferably expose it to application code as:

```csharp
PaymentStatus.Unpaid
```

This leads to another useful design principle:

> Use the same business vocabulary across code, contracts, schemas, tests, and documentation whenever practical.

For humans, this reduces the amount of institutional knowledge needed to understand the system.

For agents, it reduces the number of semantic translations that must be inferred before a change can be made safely.

In this sense, agent-friendly code should not merely be readable.

It should be **semantically searchable and cross-referenceable**.


## Semantic Locality May Become an Architectural Goal

We can think about code as having different levels of semantic locality.

High semantic locality:

```csharp
CalculatePrice(order, customer, pricingRules);
```

The important inputs are visible.

Lower semantic locality:

```csharp
priceCalculator.Calculate(order);
```

The implementation must be discovered.

Even lower semantic locality:

```csharp
priceCalculator.Calculate(order);
```

where dependency injection selects the implementation based on runtime context.

Very low semantic locality:

```csharp
priceCalculator.Calculate(order);
```

where the result also depends on:

```text
current tenant
feature flags
ambient user
interceptors
global cache
transaction context
dynamic configuration
```

The textual code can remain equally short while the reasoning cost increases dramatically.

For agent-maintained systems, **semantic locality may become as important as traditional measures such as coupling, cohesion, and duplication**.

## The Likely Direction Is Not "No Abstractions"

The more realistic direction is:

```text
hide mechanisms
expose semantic decisions
centralize implementation
localize intent
make abstractions inspectable
```

This could lead to code that is somewhat more verbose than today's most heavily abstracted application architectures.

But the code may also become:

- easier for agents to modify,
    
- easier for humans to review,
    
- easier to test,
    
- easier to analyze statically,
    
- less dependent on institutional knowledge,
    
- safer to refactor automatically.
    

The important shift may therefore not be from abstraction to no abstraction.

It may be from:

```text
implicit, non-local behavior
```

toward:

```text
explicit, composable, mechanically discoverable behavior
```

In software increasingly written and maintained by agents, the cost of repetition may fall while the cost of hidden semantics becomes much more visible.

That could change what we consider "clean" architecture.

---

