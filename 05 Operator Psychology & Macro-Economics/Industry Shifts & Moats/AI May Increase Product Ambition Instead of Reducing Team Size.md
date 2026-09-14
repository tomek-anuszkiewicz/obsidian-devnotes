---
title: AI May Increase Product Ambition Instead of Reducing Team Size
tags:
  - future-of-work
  - economics
  - team-dynamics
  - productivity
  - product-management
  - software-engineering
aliases:
  - Jevons Paradox in Software Engineering
  - Product Ambition in AI Era
---

# AI May Increase Product Ambition Instead of Reducing Team Size

> [!IMPORTANT]
> **Executive Architectural Thesis**: The prevailing macroeconomic assumption that *"10x developer productivity necessitates 10x fewer software engineers"* is a manifestation of the **Lump of Labor Fallacy**. Because market demand for software is highly elastic, collapsing the marginal cost of code creation does not trigger organizational downsizing; it triggers the **Jevons Paradox**. Time saved on boilerplate plumbing and routine CRUD is immediately reinvested into expanding product ambition, surface area, and architectural sophistication—enabling lean engineering strike teams to conquer domains that previously required enterprise-scale headcount.

```text
           THE JEVONS PARADOX IN SOFTWARE ENGINEERING VELOCITY
THE CONTRACTION FALLACY (Lump of Labor Myth):
  10x Code Velocity ---> Fire 90% of Engineers ---> Same Bounded Product Shipped Cheaply
  * Fails: Assumes market software demand is fixed and static

THE JEVONS PARADOX EXPANSION REALITY:
+-------------------------------------------------------------------------+
| [ UNIT COST OF CODE COLLAPSES BY 90% ]                                  |
+------------------------------------|------------------------------------+
                                     v (Software Demand Is Highly Elastic)
+-------------------------------------------------------------------------+
| PRODUCT AMBITION MULTIPLIER (Unaddressed Backlog Becomes Economical)    |
| * Real-time event streaming, sub-second predictive edge caches          |
| * Deep multi-agent customer workflows, sovereign local offline sync     |
| * Autonomous self-healing runtime telemetry and automated verification  |
+------------------------------------|------------------------------------+
                                     v
+-------------------------------------------------------------------------+
| EXPANDED COMPETITIVE MOAT (Conquering Entire Industry Verticals)        |
| Elite 8-person squads build systems previously requiring 100 developers |
+-------------------------------------------------------------------------+
```

## Executive Summary & Core Architectural Invariants

1. **Refutation of the Lump of Labor Fallacy**: The assumption that 10x developer productivity leads to 10x fewer engineers treats software demand as a finite, fixed quantity. In reality, software demand is extraordinarily elastic.
2. **The Jevons Paradox in Software Engineering**: As the unit cost of authoring software collapses, the total consumption and deployment of software skyrockets, unlocking projects that were previously deemed economically unjustifiable.
3. **The Product Ambition Multiplier**: Time saved on boilerplate CRUD and routine plumbing is immediately redirected toward complex, ambitious feature horizons: real-time streaming, edge predictive engines, and multi-agent workflows.
4. **Scale Inversion in Engineering Strike Teams**: Rather than downsizing an 8-person team into a solitary developer maintaining a legacy system, top-tier organizations keep the team intact and equip them to conquer markets that previously demanded 100 engineers.
5. **Competitiveness Bounded by Execution Speed**: Organizations that treat AI purely as a headcount reduction mechanism are rapidly out-competed by aggressive competitors who use AI to exponentially increase feature scope and product fidelity.

---

A common assumption about AI in software development is:

> If every engineer becomes more productive, companies will need fewer engineers.

This will probably be true in some parts of the market.

A small team will be able to build products that previously required extensive capital, unlocking a new market for [[AI May Create a New Market for Small, Custom Business Software|small, custom business software]]. Standard applications, internal tools, integrations, prototypes, and conventional business systems may require substantially fewer people.

But a simple model is incomplete:

```text
2× developer productivity
→ 2× fewer developers
```

A more realistic possibility is:

```text
fewer developers per project
+
many more economically viable projects
+
more ambitious products
```

AI may reduce the amount of labor required per unit of functionality while simultaneously increasing product ambition, proving that [[AI Productivity Is Limited by the Delivery System|delivery systems bound organizational output]] rather than sheer typing speed.

As teams scale their scope, protecting against [[Software Decay and the Hidden Costs of Frictionless AI Code|software entropy]] becomes the defining architectural challenge. The important question is therefore not only:

> How many people will be required to build today's software?

It is also:

> What software becomes worth building once development becomes dramatically cheaper, and how should companies handle this when deciding [[How Should Companies Use the Productivity Gains from AI|how to reinvest productivity dividends]]?

---

## Software Demand Is Not Fixed

The simplest automation model assumes a fixed amount of work:

```text
fixed product scope
÷
higher productivity
=
fewer engineers
```

But software organizations rarely have a fixed and complete list of useful work.

They usually have:

- features that were never prioritized;
    
- weak user experiences;
    
- missing integrations;
    
- manual internal processes;
    
- unsupported customer cases;
    
- insufficient observability;
    
- technical debt;
    
- products that were previously too expensive to build;
    
- ideas that were never tested because implementation cost was too high.
    

When development becomes cheaper, more of this work becomes economically viable.

The likely effect is therefore not only:

```text
same demand
+ higher productivity
→ less labor
```

It may also be:

```text
lower development cost
→ more viable projects
→ more experiments
→ more functionality
→ higher user expectations
→ continued demand for engineering work
```

This distinction matters because software demand is highly elastic.

There is an enormous amount of useful software that is not built today simply because the expected value does not justify the development cost.

---

## The Long Tail of Software That Does Not Exist Yet

A large amount of organizational work is still performed using:

- spreadsheets;
    
- email;
    
- manual copying;
    
- disconnected SaaS tools;
    
- paper workflows;
    
- ad hoc scripts;
    
- undocumented operational knowledge;
    
- people manually coordinating processes between systems.
    

This is not necessarily because nobody could automate these processes.

Often the economics are simply unfavorable.

A custom application might solve the problem, but building and maintaining it may cost more than the inefficiency it removes.

AI can change that threshold.

Custom software may become economically reasonable for:

- small manufacturers;
    
- clinics;
    
- property managers;
    
- logistics companies;
    
- restaurants;
    
- small wholesalers;
    
- local service businesses;
    
- small professional firms;
    
- individual departments inside larger organizations;
    
- specialized workflows serving only a few dozen users.
    

This can create a very large long tail of narrow, highly customized systems.

Instead of:

```text
one generic SaaS product
serving thousands of organizations
through extensive configuration
```

we may increasingly see:

```text
shared infrastructure
+ reusable capabilities
+ AI-assisted development
→ thousands of slightly different applications
```

Some of these systems may be temporary.

Some may serve only one company.

Some may serve only one department.

Some may exist only as long as a particular business process exists.

Historically, such software would often have been too expensive to justify.

With agents, much of it may become ordinary.

---

## Previous Productivity Improvements Did Not Eliminate Software Work

Software development has already experienced major increases in productivity.

Examples include:

- high-level programming languages;
    
- managed runtimes;
    
- databases;
    
- open-source libraries;
    
- web frameworks;
    
- cloud infrastructure;
    
- container platforms;
    
- infrastructure as code;
    
- continuous integration;
    
- software-as-a-service components.
    

Each reduced the amount of manual work required to build a given capability.

A modern development team does not normally implement:

- its own operating system;
    
- networking stack;
    
- database engine;
    
- cryptographic primitives;
    
- authentication system;
    
- payment infrastructure;
    
- deployment scheduler.
    

Yet demand for software engineers continued to grow for long periods.

The productivity gains were used to create:

- more applications;
    
- more specialized systems;
    
- better user interfaces;
    
- more integrations;
    
- faster delivery;
    
- larger product portfolios;
    
- software for smaller markets and narrower business problems.
    

AI may continue this historical pattern at a much higher level of abstraction.

The difference is that AI may reduce not only the cost of individual technical components, but the cost of translating an idea into an entire working system.

---

## AI Changes the Cost of Attempting an Idea

Many software ideas are not rejected because they are impossible.

They are rejected because they are too expensive relative to their expected value.

AI may lower the cost of:

- prototyping;
    
- testing a product hypothesis;
    
- entering an unfamiliar codebase;
    
- integrating systems;
    
- building internal tools;
    
- maintaining small niche products;
    
- supporting specialized customer workflows;
    
- preparing migrations;
    
- creating experimental products.
    

As the cost of trying an idea decreases, organizations can test more ideas.

Most experiments will still fail.

But the total amount of experimentation can increase substantially.

```text
cheaper implementation
→ more experiments
→ more discovered opportunities
→ more follow-up development
```

This can create additional engineering demand rather than merely compressing the existing workload.

The relevant economic unit changes from:

```text
How expensive is this project?
```

toward:

```text
Is the expected value even slightly higher
than the now much lower implementation cost?
```

That can move a huge number of previously marginal ideas into the viable category.

---

## AI Can Increase Product Ambition

Lower development cost does not only create more projects.

It can also change what companies attempt within an existing project.

An organization can use AI-driven productivity in several ways:

```text
same team
→ same product faster

smaller team
→ similar product at lower cost

same team
→ better product

same team
→ more products and experiments
```

Different companies will choose differently.

A business maintaining a conventional internal system may reduce the required team size.

A company competing in a fast-moving product market may reinvest productivity gains into:

- higher quality;
    
- stronger differentiation;
    
- deeper integrations;
    
- new capabilities;
    
- more experiments;
    
- faster iteration;
    
- better reliability;
    
- better personalization.
    

This is why higher productivity does not mechanically translate into proportional reductions in employment.

The target itself moves.

---

## The Standard Product Will Become More Demanding

A product that appears sophisticated today may look basic after AI-assisted experiences become normal.

Users may increasingly expect:

- natural-language interaction;
    
- personalization;
    
- proactive assistance;
    
- automation of repetitive work;
    
- immediate integration with other systems;
    
- support for unusual cases;
    
- faster responses to feedback;
    
- accessibility by default;
    
- rapid product evolution.
    

Features that are currently premium may become baseline expectations.

This creates an important feedback loop:

```text
AI improves product capability
→ users experience better products
→ expectations rise
→ yesterday's advanced features become normal
```

AI can therefore simultaneously:

```text
lower the cost of reaching today's standard
```

and:

```text
raise tomorrow's standard
```

The required effort does not necessarily disappear.

It moves toward a more ambitious target.

---

## Commodity Software Will Require Smaller Teams

Some categories of software are likely to become highly commoditized.

Examples include:

- standard CRUD applications;
    
- simple workflow systems;
    
- conventional websites;
    
- basic mobile applications;
    
- common platform integrations;
    
- lightweight reporting tools;
    
- disposable prototypes;
    
- simple model-based assistants.
    

A small team may assemble such a product from:

```text
foundation model
+ standard components
+ common integrations
+ interface
+ billing
```

The technical entry barrier will fall.

There will likely be a large market of inexpensive, similar, rapidly created applications.

In this part of the market, team sizes may shrink substantially.

But this does not imply less software.

It may instead mean:

```text
much smaller team per application
×
much larger number of applications
```

---

## Custom Software May Compete More Strongly With SaaS

One important consequence may be a change in the boundary between buying software and building it.

Today companies often purchase broad SaaS products because custom development is too expensive.

They accept:

- unused functionality;
    
- awkward workflows;
    
- complicated configuration;
    
- compromises imposed by a generic data model;
    
- integration work;
    
- licensing costs.
    

If custom development becomes cheap enough, the calculation changes.

Instead of asking:

> Which existing product is closest to our process?

organizations may increasingly ask:

> Why not generate or build something that matches our process directly?

This does not mean shared platforms disappear.

More likely, the market separates into layers:

```text
durable systems of record
shared infrastructure
identity
payments
communication
data platforms
foundation models
```

with increasingly custom software built on top.

The application layer may become much more fluid.

---

## Frontier Products Will Continue to Consume Talent

At the competitive frontier, organizations will try to build products that cannot be reproduced by connecting the same public model to a standard interface.

Differentiation may depend on:

- proprietary data;
    
- domain knowledge;
    
- original product design;
    
- specialized models;
    
- new interaction patterns;
    
- difficult integrations;
    
- exceptional reliability;
    
- security;
    
- operational scale;
    
- research and experimentation.
    

These products will still require human:

- judgment;
    
- invention;
    
- taste;
    
- domain understanding;
    
- system design;
    
- risk assessment;
    
- product leadership.
    

AI can accelerate execution, but it does not eliminate uncertainty about what should be built.

The strongest companies may use productivity gains to move the frontier rather than reduce staffing.

---

## AI Raises Both the Floor and the Ceiling

AI will probably raise the minimum capability of a small or average team.

A few people may create a product that previously required a much larger organization.

This raises the floor:

```text
small teams can build much more
```

But leading organizations receive the same tools.

They can combine AI with:

- experienced engineers;
    
- strong product judgment;
    
- proprietary knowledge;
    
- large datasets;
    
- efficient delivery systems;
    
- significant capital;
    
- research capacity.
    

This raises the ceiling:

```text
the best teams can attempt much more difficult products
```

AI therefore does not necessarily equalize competition.

It may expand the entire range of what teams can build.

---

## Human Inventiveness Remains Scarce

Implementation may become cheaper while good direction remains limited.

Organizations still need to decide:

- which problem is worth solving;
    
- which users matter;
    
- which behavior creates real value;
    
- which ideas should be rejected;
    
- when a familiar pattern is insufficient;
    
- which risks are acceptable;
    
- how a product should differ from alternatives.
    

AI can generate many plausible implementations and product variants.

Generating possibilities is not the same as selecting a meaningful direction.

As execution becomes cheaper, the relative importance of product judgment may increase.

A company may build the wrong product faster than before.

And if organizations can afford to attempt ten times more ideas, deciding which ideas deserve attention may become even more important.

---

## Research and Development Still Matter

AI can accelerate R&D by helping with:

- literature analysis;
    
- hypothesis generation;
    
- prototyping;
    
- experiment preparation;
    
- data analysis;
    
- comparison of alternatives.
    

But R&D exists because the answer is not known in advance.

The organization may not know:

- whether a capability is technically possible;
    
- whether users will value it;
    
- which approach will work;
    
- which metric represents success;
    
- whether the result is reliable;
    
- whether it can be scaled safely.
    

Cheaper experiments do not remove this uncertainty.

They make it possible to explore more of it.

```text
faster experimentation
→ more hypotheses tested
→ more opportunities discovered
→ more ambitious research
```

AI may therefore increase the amount of R&D organizations can justify.

---

## Teams May Change Composition More Than Size

Even when the number of people remains similar, their work may change.

There may be less demand for:

- repetitive implementation;
    
- boilerplate;
    
- manual translation of specifications into standard code;
    
- memorizing framework APIs;
    
- routine configuration work.
    

There may be more demand for:

- domain expertise;
    
- product engineering;
    
- system design;
    
- evaluation;
    
- data engineering;
    
- security;
    
- reliability;
    
- observability;
    
- experimentation;
    
- agent orchestration.
    

A team may manually write much less code while producing a much more capable product.

The scarce resource may gradually move from:

```text
ability to implement software
```

toward:

```text
ability to understand a problem,
design the right system,
and judge whether the result is good
```

---

## Smaller Technical Teams Do Not Always Mean Smaller Companies

AI may allow fewer developers to implement and maintain a technical system.

But successful products may redirect resources into:

- research;
    
- design;
    
- customer discovery;
    
- operations;
    
- safety;
    
- compliance;
    
- support;
    
- domain expertise.
    

The engineering organization may become more compact while the total organization continues to grow.

Productivity gains can change the allocation of labor without simply eliminating it.

---

## Product Quality Is a Moving Frontier

The relevant comparison is not between:

```text
today's product built manually
and
today's product built with AI
```

It is between:

```text
today's competitive standard
and
the future standard created by AI-enabled competitors
```

A product built cheaply by a small team may be sufficient in a stable or commodity market.

In a competitive market, companies will continue investing until the marginal improvement no longer justifies the cost.

Better tools move that point outward.

This has happened repeatedly in software:

- websites became richer rather than merely cheaper;
    
- cloud systems became more distributed rather than simply requiring fewer administrators;
    
- mobile applications gained more capabilities rather than remaining simple;
    
- analytics systems processed more data rather than only reducing reporting teams.
    

AI may create the same effect across a broader range of engineering work.

---

## A Polarized Software Market

The market may become increasingly divided.

At one end:

- very small teams;
    
- low development costs;
    
- huge numbers of niche applications;
    
- highly customized internal systems;
    
- rapid imitation;
    
- disposable software;
    
- weak technical differentiation.
    

This is where the long tail may expand dramatically.

A system serving one warehouse, clinic, department, restaurant chain, or specialized workflow may become economically reasonable.

At the other end:

- deeply integrated systems;
    
- proprietary data and workflows;
    
- substantial research;
    
- high reliability requirements;
    
- strong product differentiation;
    
- significant human and computational investment.
    

The middle may face the greatest pressure.

A conventional product with neither a major cost advantage nor meaningful differentiation may struggle against both:

```text
cheap AI-assisted custom alternatives
```

and:

```text
highly ambitious market leaders
```

---

## Working Hypothesis

> AI will significantly reduce the labor required to build software at today's standard, but it will also increase the number of economically viable software projects, the expected quality of software, and the ambition of leading organizations.

A stronger version is:

> Fewer developers may be required per project, while dramatically more projects become worth building.

And another consequence follows:

> Commodity software will increasingly be built by small teams, while companies operating at the product frontier will reinvest AI-driven productivity into greater scope, quality, experimentation, and differentiation.

The overall equation may therefore look less like:

```text
2× productivity
→ 2× fewer developers
```

and more like:

```text
higher productivity
→ lower cost per capability
→ smaller teams per project
→ many more viable projects
→ higher expectations
→ more ambitious products
→ continued demand for engineering and product judgment
```

---

## Mental Model

Do not treat software demand as fixed.

The incomplete model is:

```text
higher developer productivity
→ fewer developers
```

A better model is:

```text
higher developer productivity
→ lower development cost
```

and then two effects happen simultaneously:

```text
lower cost
→ fewer people required per project
```

but also:

```text
lower cost
→ more problems worth solving
→ more custom software
→ more experiments
→ more products
```

while competition creates another loop:

```text
better tools
→ better products
→ higher user expectations
→ greater product ambition
```

So the final effect may be:

```text
less labor per unit of software
×
many more units of software
×
higher complexity per competitive product
```

AI will probably reduce team sizes in some areas.

It may simultaneously cause software to spread into places where custom development has never previously been economically justified.

The central question is therefore not only how many people are required to build the same product.

It is how much more software society will choose to build once software creation becomes cheap.
---

## Relationship to the Knowledge Graph

- **[[AI May Create a New Market for Small, Custom Business Software]]**: Channeling increased engineering capacity into addressing long-tail operational needs.
- **[[From AI-Assisted Teams to Cross-System Feature Ownership]]**: Expanding developer scope from isolated components to entire cross-system features.
- **[[How Should Companies Use the Productivity Gains from AI]]**: Strategic options for reinvesting agentic productivity into product breadth and quality.
- **[[AI Productivity Is Limited by the Delivery System]]**: Why scaling product ambition requires removing delivery, testing, and deployment bottlenecks.
- **[[Competitive advantage in the age of commodity AI]]**: Outperforming competitors by tackling harder, more ambitious domain problems.
