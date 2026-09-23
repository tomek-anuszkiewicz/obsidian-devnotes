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