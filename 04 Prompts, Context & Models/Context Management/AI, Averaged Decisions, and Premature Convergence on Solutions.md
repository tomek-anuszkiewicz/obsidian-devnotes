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

## Introduction

Large language models tend to produce answers that are complete, coherent, polished, and well justified.

This is useful, but it creates an important risk.

When a problem is underspecified, the model often does not stop and expose the missing information. Instead, it fills in the gaps and produces a complete solution.

At the same time, when asked to solve a problem, the model may immediately converge on a small set of conventional solutions rather than systematically exploring the full solution space.

These are two sides of the same broader problem:

**AI is very good at completing incomplete problems, but completion is not the same as discovering the best decision or the best solution for a particular company.**

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
    

If people analyzed the problem themselves or discussed it during a meeting, these questions would often emerge naturally.

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

```python
# Example: The model silently resolves core business rules inside a data model
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

class WebhookPayload(BaseModel):
    event_id: str
    tenant_id: str
    payload: dict
    # Hidden business decisions made by the model:
    # 1. Hardcoded 3-retry maximum before message dropping
    max_retries: int = 3
    # 2. Hardcoded 7-day retention window
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))
    # 3. Silent assumption that tenants cannot override delivery guarantees
    is_idempotent: bool = True
```

Consider how easily this sneaks into production code. A generated data model hardcodes a 7-day retention TTL and a 3-retry ceiling. If downstream consumers expect a 90-day window for regulatory compliance or need failed events held in a dead-letter queue for manual re-drive, the system fails silently at runtime. The developer reviewing the pull request sees clean, idiomatic typing, but the model has quietly resolved core policies around data lifecycle, delivery guarantees, and backpressure without a single engineering discussion.

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

Take a concrete systems scenario: designing cache invalidation across distributed edge nodes. When asked for architectures, an LLM typically defaults to well-trodden paths like short TTLs with conditional HTTP `If-None-Match` requests or pub/sub cache purge broadcasting. If an architect explicitly asks, *"Why not stream Change Data Capture (CDC) events directly from the database write-ahead log to lightweight edge workers?"*, the model instantly provides a rigorous technical breakdown: it recognizes that CDC eliminates the dedicated message broker, avoids race conditions between cache purging and DB commits, and guarantees causal ordering. The model already possesses the operational knowledge to validate and score the pattern, but the high token probabilities of conventional pub/sub designs crowded it out during initial generation.

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

True diversity requires exploring orthogonal architectural axes: comparing an asynchronous distributed queue backed by worker pools against an append-only log, an in-memory ring buffer with kernel-bypass networking, or a synchronous backpressure-driven streaming model. Prompting for raw volume only yields cosmetic variations of the same underlying failure domain.

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

To operationalize this in an engineering pipeline, require the model to emit a structured decision manifest alongside any architecture proposal:

```json
{
  "implicit_assumptions_made": [
    {
      "area": "Retry and Failure Semantics",
      "assumed_default": "3 retries with exponential backoff before message discard",
      "alternative_options": ["Block partition to guarantee strict ordering", "Route directly to DLQ after 1 failure"],
      "business_impact": "Potential silent data loss if poison pills are discarded without alerting"
    },
    {
      "area": "Data Retention",
      "assumed_default": "Hardcoded 30-day TTL in database records",
      "alternative_options": ["Infinite retention with cold-tier S3 offload", "24-hour transient buffer"],
      "business_impact": "Direct impact on storage cost and legal compliance audits"
    }
  ],
  "delegated_authority_breaches": [
    "Model resolved consistency tier (eventual consistency) without product sign-off"
  ]
}
```

Extracting this structured artifact before writing code prevents invisible drift and catches policy assumptions before they become entrenched in production schemas.

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

In practice, this means establishing an explicit operational contract for what the model can decide autonomously:

- **Safe for model autonomy:** Writing idiomatic scaffolding, generating deterministic test fixtures, refactoring purely structural interfaces, and analyzing time/space complexity.
- **Requires human architectural ownership:** Choosing consistency tiers and isolation levels, fixing data retention and compliance windows, establishing blast-radius boundaries, and selecting irreversible build-versus-buy trade-offs.

When an LLM hits an ambiguity that crosses into human architectural ownership—such as whether stale reads are acceptable during a database failover—it must halt and surface the trade-off rather than silently picking an eventual consistency default.

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

**the beginning of the search, not the result of the search.** (See [[How Reasoning Models Explore and Evaluate Solutions]] and [[How Context Narrows an AI's Solution Space]]).

## Related notes

- **[[How Reasoning Models Explore and Evaluate Solutions]]** — Search trees, evaluation functions, and test-time compute in reasoning models.
- **[[How Context Narrows an AI's Solution Space]]** — How context framing and attractors restrict the model's exploratory radius.
- **[[How Targeted Prompts Steer Model Solution Spaces]]** — Steering model attention toward non-obvious solution regimes.
- **[[Designing Software Architecture with LLM Assistance]]** — Countering model convergence on generic, unverified architectural designs.
