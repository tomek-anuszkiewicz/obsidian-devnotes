---
title: AI, Averaged Decisions, and Premature Convergence on Solutions
tags:
  - llm
  - reasoning-models
  - decision-making
  - exploration-vs-exploitation
  - cognitive-bias
  - consensus-seeking
aliases:
  - Premature Convergence in LLMs
  - Averaged Solutions Problem
---

# AI, Averaged Decisions, and Premature Convergence on Solutions

> [!IMPORTANT] Executive Architectural Thesis: Overcoming Premature Convergence and Statistical Averaging
> Large Language Models naturally optimize for statistical plausibility across their general pre-training distribution. When presented with underspecified requirements, an LLM will rarely pause to expose ambiguities; instead, it silently fills conceptual gaps with conventional defaults disguised as technical implementation details:
> $$\text{Underspecified Requirements} + \text{Capable Model} = \text{Invisible Strategic Decisions Made by AI}$$
> This produces **premature convergence on the market average**—a solution that is coherent, polished, and technically plausible, yet strategically undifferentiated. Counteracting premature convergence requires shifting the agent's interaction model from **Answer Oracle** (`Question -> Complete Answer`) to **Exploratory Engine** (`Question -> Decomposition -> Missing Invariants -> Multi-Path Divergence -> Trade-Off Matrix -> Human Selection`).

```text
+----------------------------------------------------------------------------------------------------+
|               PREMATURE CONVERGENCE VS DELIBERATE MULTI-PATH SEARCH                                |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  NAIVE DIRECT INFERENCE (Single-Path Greedy Collapse)                                              |
|  [Underspecified Prompt] ───> [Greedy Prior Sampling] ───> [Averaged Industry Default]            |
|                               (Silently invents gaps)       (Coherent, plausible, uncompetitive)   |
|                                                                                                    |
|  DELIBERATE EXPLORATION ENGINE (Multi-Path Divergence & Human Bounds)                              |
|                                      +── Path A: Event-Driven Reactive ─────────+                  |
|                                      |                                          |                  |
|  [Underspecified Prompt] ──> [Gap Extraction] ──+── Path B: Synchronous Orchestrated ───+──> [Trade-Off Matrix] |
|                              (Exposes assumptions)                               |    (Human Strategic  |
|                                      +── Path C: Decentralized Mesh ────────────+     Selection)        |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

## Executive Summary & Core Architectural Invariants

1. **The Law of Invisible Strategic Decisions**:
   When presented with underspecified requirements, capable language models do not halt to query missing invariants; they greedily sample the highest-probability path across their public pre-training distribution. Business decisions, architectural trade-offs, and edge-case policies are silently converted into mundane implementation details without human awareness.

2. **The Commoditization Trap of the Statistical Median**:
   Greedy single-path generation produces solutions that represent the market average: syntactically clean, idiomatic, and plausible, yet completely undifferentiated. Relying on unconstrained model generation erodes proprietary competitive moats by steering product and technical architecture toward generic industry tropes.

3. **Exploratory Engine Over Answer Oracle**:
   To prevent premature collapse, the agent's cognitive pipeline must be inverted: transforming the model from an oracle that generates definitive answers into an exploratory engine that decomposes requirements, extracts implicit assumptions, and maps orthogonal solution trajectories.

4. **Asymmetry of Solution Generation and Verification**:
   Reasoning models frequently fail to generate optimal or counter-intuitive solutions during initial top-down inference, yet can rigorously evaluate, critique, and verify them when explicitly prompted. Effective engineering harnesses the model for multi-candidate verification and trade-off scoring rather than single-shot synthesis.

5. **Preservation of Explicit Human Decision Boundaries**:
   Architectural and product governance requires establishing strict boundaries where the AI is prohibited from inventing defaults. Decisions involving domain risk, cost-latency trade-offs, regulatory boundaries, and competitive differentiation must be explicitly surfaced to human operators before code generation begins.

---

## Introduction

Large language models tend to produce answers that are complete, coherent, polished, and well justified, but in software engineering this frequently leads to [[Designing Software Architecture with LLM Assistance|superficial architectural completeness]].

This is useful, but it creates an important risk.

When a problem is underspecified, the model often does not stop and expose the missing information. Instead, it fills in the gaps and produces a complete solution.

At the same time, when asked to solve a problem, the model may immediately converge on a small set of conventional solutions rather than systematically exploring the full solution space, a phenomenon directly examined in [[How Context Narrows an AI's Solution Space|how context narrows an AI's solution space]].

These are two sides of the same broader problem. As detailed in [[How Reasoning Models Explore and Evaluate Solutions|how reasoning models explore and evaluate solutions]], **AI is very good at completing incomplete problems, but completion is not the same as discovering the best decision or the best solution for a particular company.**

---

## 1. The Problem of Underspecified Requirements

The business may say:

> We need feature A.

But A may leave many important questions unanswered.

For example:

- What exactly should happen in a particular edge case?
    
- Which customer segment has priority?
    
- Is speed more important than cost?
    
- Is flexibility more important than simplicity?
    
- What should happen when an external dependency fails?
    
- Should the user be allowed to override a particular decision?
    
- How should this feature support the company's broader strategy?
    

If people analyzed the problem themselves or discussed it during a meeting, these questions would emerge naturally, or they can be unlocked when [[Emergence, Latent Space Synthesis, and How Targeted Prompts Crystallize Insight|targeted prompts force latent space synthesis]].

The initial requirement A would gradually become a more precise requirement B.

An LLM can skip this process.

It receives A and silently invents B in order to produce a complete answer.

This creates a useful formula:

**underspecified requirements + capable model = hidden decisions made by the model**

---

## 2. The Hidden Decision Problem

The dangerous part is not simply that the model makes assumptions.

Humans make assumptions as well.

The problem is that the assumptions may become invisible.

The model does not necessarily say:

> The specification does not define this behavior, so I am assuming X.

Instead, it may simply generate a design in which X already exists.

A business or product decision can therefore become disguised as an implementation detail.

For example, the generated system may implicitly decide:

- how long data should be retained,
    
- whether a failed request should be retried,
    
- whether an operation is synchronous or asynchronous,
    
- whether the user can have multiple active items,
    
- who is allowed to override a decision,
    
- what happens when information is incomplete.
    

Every one of these may look technical in the generated implementation.

But some of them may actually represent significant business decisions.

---

## 3. Why the Model's Default May Not Be the Company's Best Decision

When the model has to fill a gap, it usually has access to broad general knowledge.

It can draw from:

- common market practices,
    
- popular product patterns,
    
- common UX conventions,
    
- standard architecture patterns,
    
- frequently seen business models,
    
- publicly documented best practices,
    
- its training data.
    

This makes its assumptions likely to be reasonable.

But reasonable is not the same as optimal.

The resulting decision may be:

**statistically sensible, but strategically wrong for the specific company.**

A company may intentionally want to behave differently from the market.

Its competitive advantage may exist precisely in those differences.

---

## 4. The Connection to Competitive Advantage

Suppose ten companies ask similar models:

> How should we solve problem A?

If each company provides only limited context, the models may produce similar solutions.

The companies gain:

- faster execution,
    
- lower development cost,
    
- better access to established practices,
    
- fewer obvious mistakes.
    

But they may simultaneously lose differentiation.

This creates a paradox:

**AI can increase execution efficiency while reducing strategic diversity.**

The products may become better in an absolute sense, but more similar to each other.

The same compressed body of market knowledge is being used by everyone.

If all companies accept the model's default decisions, AI becomes a force that pushes products toward the center of the distribution.

---

# 5. A Second Problem: Premature Convergence on Solutions

There is another version of the same problem.

Suppose the problem itself is already understood.

We ask:

> What are the possible solutions?

The model generates:

- solution A,
    
- solution B,
    
- solution C.
    

We compare them and choose B.

This appears to be a rational process.

But it assumes that A, B, and C adequately represent the relevant solution space.

That assumption may be false.

There may be a solution D that the model simply failed to generate.

If D is actually the best approach, the later comparison between A, B, and C is already compromised.

The mistake happened before the evaluation started.

---

## 6. Generation Ability Is Not the Same as Evaluation Ability

A particularly interesting LLM behavior exposes this problem.

The model may fail to propose solution D.

But when a human says:

> What about D?

the model may immediately respond:

> Yes. D is a very strong solution and under these constraints may actually be better than A, B, and C.

This reveals an important distinction:

**the ability to evaluate a solution is not the same as the ability to generate that solution.**

A model may contain enough knowledge to recognize that D is good once D appears in the context.

Yet its initial generation process may never surface it.

This means that:

**the model's list of solutions should not automatically be interpreted as the set of solutions.**

It is only a set of solutions that happened to be generated.

---

## 7. Why This Happens

LLMs are fundamentally generative systems.

When asked for possible solutions, they tend to generate high-probability continuations.

Therefore, the first solutions produced are often:

- common,
    
- conventional,
    
- well documented,
    
- widely discussed,
    
- semantically close to the way the problem was phrased.
    

A genuinely different solution may have lower probability even if it would be better.

This can cause what we might call:

**solution-space collapse**

or:

**premature convergence**

The search converges too early around a few obvious approaches.

---

## 8. More Answers Do Not Necessarily Solve the Problem

Simply asking:

> Give me ten solutions instead of three.

does not guarantee diversity.

The model may produce ten variations of essentially the same concept.

For example:

- microservice,
    
- slightly different microservice,
    
- event-driven microservice,
    
- serverless version of the microservice,
    
- microservice with a queue.
    

Technically these are different answers.

Conceptually, they may occupy one small part of the solution space.

What matters is not the number of solutions.

What matters is the **diversity of solution classes**.

---

# 9. Separate Exploration from Selection

A better AI-assisted decision process should deliberately separate several stages.

Instead of:

**problem → best solution**

use:

**problem → assumptions → solution-space exploration → coverage check → evaluation → selection**

Each stage has a different purpose.

---

## 10. Step 1: Problem Framing

Before solving anything, determine what the actual problem is.

Questions may include:

- What outcome are we trying to achieve?
    
- What constraints actually exist?
    
- Which constraints are assumptions rather than facts?
    
- Who is affected?
    
- What does success mean?
    
- Which trade-offs matter?
    

The goal is not yet to find a solution.

The goal is to define the problem correctly.

---

## 11. Step 2: Detect Missing Decisions

The model should explicitly identify places where the available information does not uniquely determine the behavior of the solution.

A useful instruction is:

> Before proposing a solution, identify every place where the requirements do not uniquely determine what should happen.

The model can classify information as:

- fact,
    
- requirement,
    
- constraint,
    
- assumption,
    
- business decision,
    
- technical decision,
    
- unresolved question.
    

This makes hidden decisions visible.

---

## 12. Step 3: Explore the Solution Space

Only after the problem is sufficiently clear should the model start generating possible approaches.

But the goal should not be:

> Give me the best solution.

Instead:

> Explore fundamentally different classes of solutions.

For example:

- the simplest possible solution,
    
- the conventional industry solution,
    
- a solution using existing infrastructure,
    
- a solution requiring new infrastructure,
    
- build versus buy,
    
- technical solution versus organizational solution,
    
- automation versus process change,
    
- a solution that removes the need for the feature entirely,
    
- centralized versus decentralized approach,
    
- synchronous versus asynchronous approach,
    
- short-term tactical solution,
    
- long-term strategic solution,
    
- a deliberately unconventional solution.
    

This encourages breadth rather than immediate convergence.

---

## 13. Step 4: Perform a Coverage Check

After generating possible solutions, the model should challenge its own search.

For example:

> Which fundamentally different solution classes are missing from this list?

or:

> Find approaches that do not resemble any of the solutions already proposed.

or:

> Assume the currently preferred solution is forbidden. What would we do instead?

This creates a second exploration pass.

It is similar to an adversarial review of the brainstorming process itself.

---

## 14. Multiple Perspectives Can Improve Exploration

Another useful technique is to deliberately change the perspective used to search the solution space.

For example:

> How would a startup with almost no infrastructure solve this?

> How would a large regulated enterprise solve it?

> How would we solve it if adding another service was forbidden?

> How could we solve it without writing new software?

> How could we eliminate the underlying need instead?

> What would an organization optimizing purely for operational simplicity choose?

The purpose is not to simulate personalities.

The purpose is to force the model into different regions of the solution space.

---

## 15. Step 5: Evaluation

Only once a reasonably broad solution space exists should the model evaluate the alternatives.

The comparison should use criteria that actually matter to the company.

For example:

- implementation cost,
    
- operational complexity,
    
- time to market,
    
- scalability,
    
- reversibility,
    
- security,
    
- customer experience,
    
- organizational capability,
    
- strategic alignment,
    
- maintainability,
    
- vendor dependence,
    
- future optionality.
    

The model can help analyze these trade-offs.

But the criteria should preferably come from the company rather than being silently invented by the model.

---

## 16. Step 6: Selection

Selection should happen only after exploration and evaluation.

At this stage the model may recommend an option.

But ideally the recommendation should include:

- why it wins,
    
- which assumptions it depends on,
    
- what alternatives were rejected,
    
- what would have to change for another solution to become preferable.
    

This prevents the recommendation from looking more certain than it really is.

---

# 17. Decision Logs

A useful safeguard is to require an explicit decision log.

After creating a design, the model should be able to answer:

> What decisions did you have to make in order to produce this solution?

For example:

- I assumed users can have only one active cart.
    
- I assumed failed requests should be retried.
    
- I assumed eventual consistency is acceptable.
    
- I assumed administrators can manually change the state.
    
- I assumed data should be retained for 30 days.
    

This can reveal that part of what appeared to be implementation was actually product or business design.

---

# 18. Company Context as Protection Against Averaging

Another line of defense is providing the model with proprietary company context.

This may include:

- product history,
    
- internal documentation,
    
- Jira issues,
    
- historical architectural decisions,
    
- meeting recordings,
    
- experiment results,
    
- customer feedback,
    
- operational data,
    
- known failures,
    
- strategy,
    
- internal constraints,
    
- domain knowledge.
    

Then the model no longer has to rely mainly on generic public knowledge.

A simplified comparison is:

**public model + public knowledge → averaged solution**

**public model + unique company context → company-specific solution**

This means that proprietary context can itself become a source of competitive advantage.

---

# 19. The Boundary of the Model's Authority

Even with excellent context, the model should not necessarily be allowed to make every decision.

Some decisions should remain explicitly outside its authority.

The correct response may sometimes be:

> The available information does not determine this. This is a product decision.

A strong agent therefore needs more than problem-solving capability.

It also needs the ability to recognize:

**the boundary of its decision-making authority.**

---

# 20. The Role of AI Should Change

The default interaction with AI often looks like:

**question → answer**

For important business and engineering decisions, a better model is:

**question → decomposition → missing decisions → exploration → challenge → comparison → decision**

In such a process, AI is not primarily the oracle that gives the answer.

It becomes a tool for:

- exposing hidden assumptions,
    
- expanding the search space,
    
- generating alternatives,
    
- challenging existing ideas,
    
- comparing trade-offs,
    
- identifying missing information,
    
- accelerating evaluation.
    

This is potentially much more valuable than simply asking it for the solution.

---

# 21. Main Risk

The broad risk can be summarized as follows:

**AI can silently reduce the size of the decision space before humans realize that a decision has been made.**

It can do this in two ways.

First, it fills in missing requirements.

Second, it proposes a limited set of solutions and makes that set appear complete.

Both mechanisms push toward plausible, conventional, averaged outcomes.

---

# 22. Main Remedy

The remedy is to design AI-assisted workflows that preserve the distinction between:

**what is known, what is assumed, what is possible, and what has actually been chosen.**

Instead of asking:

> What should we do?

ask the model to help answer, in sequence:

1. What problem are we actually solving?
    
2. What information is missing?
    
3. Which decisions have not yet been made?
    
4. What fundamentally different solution classes exist?
    
5. Which classes might still be missing?
    
6. What are the trade-offs between them?
    
7. Which solution best fits our specific context?
    
8. Which decisions should remain human or business decisions?
    

---

# Conclusion

AI can automate far more than implementation.

If used carelessly, it can also automate the narrowing of possibilities and the making of decisions that the organization never consciously made.

Because LLMs draw from a huge body of existing knowledge, their answers will often be sensible, polished, conventional, and easy to justify.

That is precisely what makes the problem subtle.

The model does not have to produce a bad answer to reduce competitive advantage.

It may produce an excellent **average answer**.

The strategic opportunity is therefore not merely to use AI more often.

It is to use AI in a way that prevents premature convergence and preserves deliberate decision-making.

A useful principle is:

**Do not use AI only to produce answers. Use it to expose decisions and expand the space of possible answers before choosing one.**

And an equally important principle is:

**A model may be very good at recognizing a strong solution once it sees it, while still failing to generate that solution during its initial search.**

Therefore, the first answer produced by an LLM should often be treated as:

**the beginning of the search, not the result of the search.**

---

## Relationship to the Knowledge Graph

- **[[Competitive advantage in the age of commodity AI]]**: Details why accepting averaged LLM answers commoditizes strategy and why cognitive audacity creates defensible moats.
- **[[How Context Narrows an AI's Solution Space]]**: Explores the computational and attention mechanisms that prematurely restrict the model's exploratory boundaries.
- **[[How Reasoning Models Explore and Evaluate Solutions]]**: Analyzes tree search, multi-path generation, and how reasoning models evaluate divergent alternatives.
- **[[Emergence, Latent Space Synthesis, and How Targeted Prompts Crystallize Insight]]**: How targeted practitioner prompts act as crystallization seeds to force models outside the averaged prior.
- **[[Refactoring Legacy Systems with AI Agents]]**: Details the *Frankenstein Intermediate Phase* where LLMs anchor on legacy git history and rationalize flawed hybrid complexity.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: Analyzes the compounding hallucination risk when reviewers force agents off their high-probability manifold through ad-hoc local mandates.
- **[[AI Changes the Role and Training of Software Engineers]]**: Explains why senior engineers must lead by framing non-obvious questions rather than accepting default proposals.
- **[[Statistical Bias, Proxy Variables, and Causal Invariants in AI Systems]]**: Analyzes how models substitute aggregate statistical proxies for causal reality, committing the ecological fallacy and trapping decision pipelines in self-fulfilling feedback loops.