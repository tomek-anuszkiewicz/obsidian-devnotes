---
title: Handwritten Code May Not Become a Luxury Good
tags:
  - software-engineering
  - future-of-work
  - developer-experience
  - economics
  - craftsmanship
  - commodity-ai
aliases:
  - The Economic Value of Handwritten Code
  - Software Craftsmanship After AI
  - Why Handwritten Software Is Not Traditional Craft
  - Manual Coding as Craft
  - When Coding Stops Being the Product
---

# Handwritten Code May Not Become a Luxury Good

Some programmers genuinely enjoy writing code. They like the rhythm of implementation, the direct contact with the system, and the feeling that every branch exists because they put it there. As coding agents take over more implementation, those programmers may lose the part of the job they valued most (see [[Developer Satisfaction, Identity, and Burnout in the Age of Coding Agents]]).

It is tempting to compare them to craftspeople. Factories did not eliminate handmade furniture, watches, or ceramics. People still pay more for objects made by a skilled person.

That comparison may not carry over to most software.

A customer can see the material, finish, variation, and history of a handmade table. In ordinary software, the customer sees whether the system works. If two applications behave the same way, the fact that one was typed line by line and the other was generated with an agent usually does not improve the user experience.

Manual programming can remain difficult, satisfying, and professionally important while losing much of its value as a production method.

## The job changes before the title does

An engineer can keep the same title while doing very different work.

The old workflow emphasized:

- implementing a solution directly;
- learning the system while writing it;
- debugging one's own decisions;
- refining local code until it felt right.

The emerging workflow emphasizes:

- defining the actual problem;
- giving an agent the relevant context;
- stating constraints and forbidden approaches;
- comparing possible implementations;
- checking behavior and failure modes;
- accepting responsibility for the result.

This is not simply the old job with faster autocomplete. It changes where attention goes and where an engineer gets satisfaction.

## Preference and ability are separate problems

Some engineers may be capable of directing agents but dislike spending their day writing specifications and auditing generated diffs. Others may want to adapt but never become particularly good at decomposing work, supplying context, or finding the plausible mistake in a large generated change.

Learning a new framework normally leaves the basic work intact. The developer still reads code, writes code, runs it, and fixes it. Agent-assisted development changes the division of labor. The engineer performs less of the implementation and more supervision, experimentation, review, and process design (see [[AI Changes the Role and Training of Software Engineers]]).

Years of programming experience do not automatically make that transition pleasant or intuitive. They can provide the judgment needed to catch bad output, but the engineer still has to express that judgment through constraints, tests, review, and reusable procedures.

## Why software is different from physical craft

The production method is often part of the value of a physical object. A buyer may care who made it, what material they selected, how it was finished, and whether every piece is slightly different.

For most business software, the production method is hidden behind the result. Users care whether an invoice is correct, a payment is processed once, a report loads quickly, and their data remains safe. They rarely receive additional value because a person manually typed the implementation.

The organization sees a similar trade-off. If an agent-assisted team can deliver the required behavior faster and at lower cost, a team that insists on manual implementation has to explain what the extra time buys. "A human wrote every line" is not enough unless it produces some observable property that matters.

This makes handwritten code closer to hand-drawn technical plans than to handmade furniture. The drawing may require skill and provide satisfaction, but the client primarily needs an accurate design that can be built.

## Manual coding still has important uses

Losing a broad production premium does not make manual programming useless.

Engineers may still write code by hand because it is the best way to:

- learn how a runtime, protocol, or data structure behaves;
- build the mental models needed to review generated code;
- investigate a failure that the agent keeps misunderstanding;
- work on a small performance-critical or safety-critical component;
- explore a genuinely new problem that has few reliable examples;
- create software as art, play, or personal craft.

The important distinction is why someone pays for the work. A company may pay for independent problem-solving evidence, a hard performance result, a security guarantee, or expertise at a frontier problem. It is not necessarily paying a premium for the keystrokes themselves (see [[Fresh Contact With Reality May Become the Training Bottleneck]]).

Manual implementation may therefore move from the normal way of producing software to a deliberate method of training, investigation, and specialist work (see [[The First AI-Native Generation of Software Engineers]]).

## Market pressure makes the change difficult to refuse

Once some teams deliver useful changes faster with agents, customers and managers adjust their expectations. A team that returns to a fully manual workflow may need more time and more people to produce the same visible result.

The market does not need agents to be perfect. It only needs agent-assisted work to be sufficiently effective that refusing it creates a persistent disadvantage (see [[AI May Become an Irreversible Part of Software Development]]).

This is why personal preference may not preserve the old role. An engineer can still love manual implementation, just as someone can love drawing technical plans by hand. The activity can remain worthwhile even when employers stop buying much of it as a separate service.

## Commodity AI does not eliminate scarce expertise

If every company uses similar general-purpose models with generic instructions, many outputs will converge on familiar architectures, products, and compromises. Access to the model then becomes a baseline rather than a durable advantage.

That does not make engineering expertise worthless. It changes what clients and employers pay for.

The scarce contribution may be the ability to:

- identify a problem worth solving;
- understand the domain well enough to spot a false assumption;
- provide context that a public model does not have;
- force an implementation to respect unusual operational constraints;
- design tests that distinguish plausible code from correct behavior;
- connect customer feedback and production failures to the next change;
- simplify or reject generated work instead of accepting it because it is cheap.

Two people can use the same model and produce very different results. One accepts the default answer. The other brings private knowledge, technical judgment, and a reliable verification process that pushes the model beyond the average pattern (see [[Competitive Advantage in the Age of Commodity AI]]).

## AI may increase the difference between engineers

An inexperienced operator can use AI to produce more code than before. That can make their output look similar to the work of a stronger engineer for a while.

The difference appears when the requirements conflict, the reference material is wrong, the system fails under load, or several reasonable designs have different long-term costs. The stronger engineer knows what to question, what evidence to request, and when the generated solution should be deleted rather than repaired.

AI can therefore compress the difference in visible implementation speed while increasing the difference in judgment and outcomes. It gives both engineers more leverage, but leverage amplifies the quality of the decisions applied through it.

## Core thesis

Handwritten code may retain educational, specialist, artistic, and personal value without becoming a significant luxury market.

The economic premium is more likely to move away from manual authorship and toward the things that generic generation does not provide by itself: problem selection, domain knowledge, constraints, verification, feedback from reality, and responsibility for the result.

The future expert may write fewer lines than before. That does not make the expert less important. It means that the valuable part of the work has moved.

## Related notes

- **[[Developer Satisfaction, Identity, and Burnout in the Age of Coding Agents]]** — What engineers may lose when direct implementation becomes supervision and review.
- **[[AI Changes the Role and Training of Software Engineers]]** — Which abilities become scarce when writing syntax is no longer the main bottleneck.
- **[[Competitive Advantage in the Age of Commodity AI]]** — Why generic models commoditize common solutions while private context and feedback loops remain difficult to copy.
- **[[AI May Become an Irreversible Part of Software Development]]** — How staffing, delivery expectations, and organizational processes make AI adoption difficult to reverse.
- **[[The First AI-Native Generation of Software Engineers]]** — Why manual implementation may remain necessary for training even after it becomes less common in production.
- **[[Fresh Contact With Reality May Become the Training Bottleneck]]** — The narrow case in which human-only work may command a premium because it creates independent evidence.
