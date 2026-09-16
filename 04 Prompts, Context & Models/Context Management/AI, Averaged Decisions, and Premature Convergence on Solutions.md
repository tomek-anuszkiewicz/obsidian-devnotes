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

Large language models tend to produce answers that are complete, coherent, polished, and easy to justify. In software engineering, this characteristic often creates a misleading sense of completeness. 

When an architectural or product problem is underspecified, a language model rarely pauses to flag missing constraints or demand clarification. Instead, it fills the gaps itself, generates the missing context from its pre-training distribution, and returns a fully realized design. At the same time, when asked to generate solutions, it typically converges on a narrow set of conventional patterns rather than exploring the broader trade-off space.

These two behaviors stem from the same root mechanic:

$$\text{Underspecified Requirements} + \text{Capable Model} = \text{Hidden Strategic Decisions Made by AI}$$

Large language models excel at completing incomplete problems. However, completion is fundamentally different from discovering the optimal architectural decision or product strategy for a specific engineering organization.

```text
Naive Direct Inference (Single-Path Collapse)
[Underspecified Requirements] ───> [Prior Distribution Sampling] ───> [Market-Average Default]
                                   (Silently invents constraints)     (Coherent, plausible, undifferentiated)

Deliberate Multi-Stage Exploration
                                   ┌── Path A: Event-Driven Reactive ─────────┐
                                   │                                          │
[Underspecified Requirements] ────>│── Path B: Synchronous Orchestrated ──────┼──> [Trade-Off Matrix] ──> [Human Strategic
      │                            │                                          │    (Context-Weighted)      Selection]
      └──> [Extract Hidden Gaps] ─>└── Path C: State Machine / In-Process ────┘
           (Flags unmade decisions)
```

---

## 1. The Problem of Underspecified Requirements

Engineering requirements from product stakeholders regularly arrive in an incomplete state:

> "We need an ingestion pipeline for third-party webhook events."

On the surface, this looks straightforward. In practice, it leaves critical architectural and business questions completely unanswered:

- What are the deduplication guarantees? Is at-least-once processing acceptable, or does downstream accounting require strict exactly-once semantics?
- What is the expected traffic distribution? Are we designing for a steady 50 requests per second, or sudden 10,000 rps bursts?
- How should the system behave during upstream vendor outages? Should it fail fast, buffer in durable storage, or degrade partially?
- What are the latency and cost budgets? Is a 500ms delay acceptable if it cuts infrastructure spend by 80%?
- Who has the authority to replay failed events or discard poisoned messages?

When an engineering team debates this requirement in a design review, these ambiguities surface immediately. The initial statement is probed, challenged, and refined into an explicit technical specification.

A language model bypasses this discovery phase entirely. It takes the sparse input, quietly invents the missing operational boundaries, and presents an end-to-end architecture as if those parameters were explicitly requested.

---

## 2. Hidden Decisions Disguised as Implementation Details

The danger is not simply that the model makes assumptions. Human engineers make assumptions constantly. The danger is that the model's assumptions remain invisible.

A model rarely emits an explicit disclaimer such as:

> "The prompt did not define retention requirements or consistency models, so I assumed a 30-day TTL and eventual consistency using DynamoDB."

Instead, it presents a concrete implementation where those choices are already baked into the schemas, infrastructure definitions, and application code:

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

In this generated snippet, several critical business and architectural policies were decided without engineering review:

- **Data retention:** Why 7 days instead of 90 days for audit compliance, or 24 hours to reduce storage costs?
- **Failure policy:** What happens after 3 retries? Does it route to a dead-letter queue, drop the message, or alert an on-call engineer?
- **Execution semantics:** Is processing synchronous or asynchronous?
- **Concurrency control:** Can a tenant submit concurrent payloads, or must events process in strict sequence?
- **Operational override:** Can an internal operator re-drive failed events manually?

Every one of these choices looks like mundane plumbing in the generated code. In reality, each represents a product or operational trade-off that directly affects operating costs, customer experience, and system reliability.

---

## 3. Why Default Assumptions Favor the Statistical Average

When a language model fills in missing specifications, it pulls from its pre-training distribution: public documentation, open-source repositories, tutorials, and standard architectural templates.

This knowledge base gives the model a broad grasp of standard engineering practices:
- Standard REST conventions
- Popular cloud patterns (e.g., API Gateway to Lambda to DynamoDB)
- Widely documented microservice patterns
- Common operational defaults (exponential backoff, standard connection pools)

Because these defaults come from broad industry consensus, the generated design is almost always reasonable, syntactically clean, and easy to justify.

However, "reasonable" is not the same as optimal. A solution can be statistically sensible across thousands of public repositories while being completely wrong for a company's specific operating environment. 

A startup running on lean margins may deliberately favor a boring, monolithic SQLite design to avoid distributed systems overhead. A high-frequency trading platform may deliberately discard standard message queues in favor of kernel-bypass networking. A company's competitive advantage often lives precisely in the areas where it deliberately rejects standard market patterns.

---

## 4. The Impact on Competitive Advantage and Architectural Diversity

Consider what happens when multiple engineering teams ask an LLM the same fundamental question:

> "Design a scalable event processing pipeline for multi-tenant SaaS."

If those teams provide minimal operational context, the model will output nearly identical architectures for each of them: an API Gateway, a managed message bus (such as SQS or Kafka), worker pools running in containers or serverless functions, and an established document store or relational database.

```text
Team A ──┐
Team B ──┼──> [LLM with Minimal Context] ──> Standard Cloud Architecture
Team C ──┘                                   (Kafka + Workers + Document DB)
```

The teams certainly gain advantages:
- Accelerated initial scaffolding
- Lower implementation effort
- Standard, well-documented conventions
- Avoidance of beginner architectural bugs

However, they lose differentiation. When every team builds on the same default suggestions, their technical foundations, cost curves, and operational bottlenecks converge toward the industry average.

This leads to a distinct engineering paradox:

**AI accelerates implementation speed while flattening strategic and architectural diversity.**

Systems become cleaner and more idiomatic in an absolute sense, but functionally indistinguishable across the broader market. When engineering organizations routinely accept the model's first plausible output, the technology stack regresses to the median of public training data.

---

## 5. Premature Convergence on Solutions

This dynamic surfaces in another common scenario: evaluating alternative solutions for an already well-defined problem.

Suppose the engineering team understands its constraints and asks:

> "What are the viable patterns to handle cache invalidation across distributed edge nodes?"

The model returns three common designs:
1. Short TTLs with conditional HTTP `If-None-Match` requests.
2. Centralized pub/sub message broadcasting to purge nodes on update.
3. Key-based versioning where URLs include content hashes.

The team reviews these options, evaluates the trade-offs, and chooses Option 2.

This process appears disciplined and rational. However, it relies on an unverified premise: that Options 1, 2, and 3 accurately represent the full landscape of practical solutions.

If an alternative approach—such as using a distributed transactional database with change-data-capture streaming directly to edge workers—was never surfaced, the downstream comparison is flawed. The critical failure occurred before the evaluation even started: the search space collapsed too early.

---

## 6. The Asymmetry Between Generation and Evaluation

This failure mode highlights an important mechanical characteristic of large language models:

**A model's ability to evaluate a proposed solution is often far superior to its ability to surface that solution spontaneously during open generation.**

If an engineer notices the gap and asks:

> "Why didn't you consider using change-data-capture directly from the primary database to trigger edge invalidations via lightweight worker scripts?"

The model will often analyze the suggestion with high technical precision:

> "That is an effective alternative. Under your write-heavy workload, CDC eliminates the overhead of managing a dedicated pub/sub broker, guarantees causal ordering, and avoids race conditions between cache purging and database commits."

This asymmetry reveals a crucial distinction:

The model already possessed the necessary information to validate and score the CDC approach. Yet during top-down generation, the higher token probabilities associated with conventional pub/sub architectures dominated the search path, crowding out the more specialized design.

Therefore, an engineering team should never treat a model's initial list of alternatives as an exhaustive survey of the solution space. It is merely a collection of high-probability continuations based on the phrasing of the prompt.

---

## 7. Mechanics of Solution-Space Collapse

Language models generate text by sampling likely continuations given a prompt context. When asked to brainstorm technical approaches, the model naturally favors patterns that are:
- Heavily documented in public technical literature
- Frequently discussed in standard engineering forums
- Closely tied to the specific keywords in the prompt

A specialized or counter-intuitive design may carry lower token probabilities in the base distribution, even when it is technically superior for the problem at hand.

This dynamic triggers **solution-space collapse**: the model converges prematurely on a cluster of common designs, effectively hiding less conventional approaches from the engineering team.

---

## 8. Why Requesting Higher Output Volume Fails

A common workaround is to simply ask the model for more options:

> "Give me ten different solutions instead of three."

This rarely produces genuine conceptual diversity. Instead of discovering distinct architectural paradigms, the model usually outputs ten minor variations of the same underlying pattern:

1. Standard microservice with an SQS queue.
2. Standard microservice with a RabbitMQ queue.
3. Serverless Lambda worker consuming from an SQS queue.
4. Serverless worker consuming from an event bridge.
5. Containerized worker running on ECS with a Redis queue.

While these options differ in infrastructure tooling, they belong to the exact same architectural class: an asynchronous distributed queue backed by background compute workers.

True diversity in technical design requires exploring fundamentally different *classes* of solutions—such as comparing an asynchronous queue against an append-only log, an in-memory ring buffer, or a synchronous backpressure-driven streaming model.

---

## 9. Separating Exploration from Selection

To prevent premature convergence and uncover hidden assumptions, engineering teams should decouple the decision process into clear, distinct phases.

Instead of jumping directly from problem to recommendation:

$$\text{Problem} \longrightarrow \text{Selected Solution}$$

Use an explicit multi-stage discovery pipeline:

$$\text{Problem} \longrightarrow \text{Decomposition} \longrightarrow \text{Assumption Extraction} \longrightarrow \text{Divergent Exploration} \longrightarrow \text{Coverage Audit} \longrightarrow \text{Trade-Off Scoring} \longrightarrow \text{Human Selection}$$

---

## 10. Phase 1: Problem Framing and Invariant Identification

Before generating architectures, pin down the fundamental constraints of the problem.

Direct the model to identify:
- What hard physical or business constraints exist (e.g., network latency boundaries, regulatory requirements)?
- Which assumptions are treated as facts without empirical backing?
- Who are the system's consumers, and what failure modes can they tolerate?
- What constitutes success: p99 latency, development velocity, monthly cloud spend, or maintainability by a small team?
- Which trade-offs are completely non-negotiable?

The objective here is not to solve the problem. The objective is to define its true boundaries.

---

## 11. Phase 2: Detecting Missing Decisions

Before designing an architecture, require the model to explicitly flag every area where the requirements leave technical or business behavior ambiguous.

A reliable prompt pattern is:

```text
Review the following requirements. Do NOT propose an architecture or write code yet.
Identify every area where the requirements fail to uniquely determine how the system 
should behave. 

Categorize findings into:
1. Invariant / Confirmed Fact
2. Hard Technical Constraint
3. Unverified Assumption
4. Unmade Business / Product Decision
5. Open Technical Choice
```

This prompt forces the model to expose hidden decisions before they disappear into implementation details.

---

## 12. Phase 3: Exploring Diverse Solution Classes

Once the constraints are clear, direct the model to explore deliberately distinct classes of solutions rather than searching for a single "correct" answer.

Explicitly mandate exploration across different architectural philosophies:

```text
Propose four fundamentally different architectural approaches to solve this problem. 
Each proposal must belong to a distinct structural class:

1. The Minimalist Path: The simplest design possible using boring, existing infrastructure 
   (e.g., standard relational DB, in-process processing, monolithic worker).
2. The Scaled Asynchronous Path: The standard cloud-native pattern (event buses, distributed queues, 
   decoupled worker pools).
3. The Radical Simplicity Path: An approach that avoids new software entirely by leveraging 
   existing platform capabilities or adjusting business processes.
4. The Unconventional / High-Performance Path: An approach that prioritizes extreme throughput 
   or strict consistency at the cost of higher upfront complexity.
```

This framing prevents the model from generating five minor variations of a message queue, forcing it to explore across radically different complexity and operational footprints.

---

## 13. Phase 4: Running a Coverage Audit

After gathering an initial set of options, challenge the completeness of the exploration. Treat the first pass as an incomplete draft.

Use adversarial prompts to push the boundaries:

> "Review the four approaches proposed above. What fundamentally different architectural paradigm is completely unrepresented in this list?"

> "Assume our cloud provider suffers a major pricing shift, making managed queues and serverless functions 10x more expensive. How would we solve this problem using only long-lived processes and direct network protocols?"

> "Assume the architecture we like best is completely banned by compliance. What is the next best alternative, and what compromises does it force us to make?"

This step runs a second exploration pass, exposing blind spots in the initial brainstorm.

---

## 14. Phase 5: Multi-Perspective Stress Testing

Another effective way to escape statistical averages is to analyze the problem through deliberately constrained operational viewpoints.

For example:

- **The Early-Stage Startup View:** *"How would we design this if we had only two engineers, an absolute hard budget of $150 per month, and a requirement to ship within 72 hours?"*
- **The High-Reliability Enterprise View:** *"How would we design this if every data loss event carried a direct $50,000 regulatory fine, requiring complete deterministic audit trails and zero data loss across multi-region failures?"*
- **The Zero-New-Services View:** *"How would we solve this if the infrastructure operations team strictly prohibited introducing any new database engines, message brokers, or managed services?"*

These prompts do not simulate abstract personas; they apply concrete engineering constraints that force the model out of its default generation paths.

---

## 15. Phase 6: Grounded Trade-Off Evaluation

Only after establishing a genuinely diverse set of candidates should the team evaluate them.

The evaluation must score options against criteria that reflect the company's real constraints, rather than generic industry metrics:

```markdown
| Evaluation Dimension | Option 1: Monolithic DB Worker | Option 2: Event-Driven SQS/Lambda | Option 3: Redis In-Memory Ring Buffer |
| :--- | :--- | :--- | :--- |
| **Operational Simplicity** | High (uses existing Postgres instance) | Low (requires new IAM, queues, DLQs) | Medium (requires Redis cluster management) |
| **Cost at 5,000 rps** | High (DB connection limits, compute scaling) | Medium (serverless invocation costs scale linearly) | Low (in-memory, highly dense) |
| **Recovery / Replayability** | High (standard SQL updates/transactions) | High (DLQ re-drive tooling) | Low (volatile memory, requires WAL dumps) |
| **Failure Blast Radius** | High (shared database resource contention) | Low (isolated serverless workers) | Medium (isolated cache, but stateful) |
| **Reversibility of Design**| High (migration away is straightforward) | Low (deep vendor SDK coupling) | Medium (standard key/value patterns) |
```

The engineering team, not the language model, must assign the weights to these evaluation criteria. The model's role is to highlight the trade-offs, not decide which trade-offs the business should accept.

---

## 16. Phase 7: Selection and Decision Logging

When an option is finally selected, capture the rationale along with an explicit record of what was considered and discarded.

A complete Architectural Decision Record (ADR) should detail:
1. The chosen architecture and why it won.
2. The specific assumptions required for this choice to remain valid.
3. The alternative approaches that were actively rejected, along with the concrete reasons for rejection.
4. The operational changes that would invalidate this decision and require revisiting the design.

Documenting rejected alternatives protects the team from revisiting the same debates months later when production traffic shifts.

---

## 17. Enforcing Explicit Decision Logs

To prevent models from silently burying product and architectural decisions in code, teams should require the model to produce a structured decision manifest alongside any proposed design.

An example schema for extracting these hidden choices:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ArchitecturalDecisionManifest",
  "type": "object",
  "properties": {
    "implicit_assumptions_made": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "area": { "type": "string", "description": "e.g., Retention, Retry, Concurrency" },
          "assumed_default": { "type": "string" },
          "alternative_options": { "type": "array", "items": { "type": "string" } },
          "business_impact": { "type": "string" }
        },
        "required": ["area", "assumed_default", "alternative_options", "business_impact"]
      }
    },
    "delegated_authority_breaches": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Decisions embedded in code that require human product/security sign-off"
    }
  },
  "required": ["implicit_assumptions_made", "delegated_authority_breaches"]
}
```

If an LLM generates an architecture for an ingestion pipeline, its decision manifest should explicitly state:

- *"I assumed failed payloads should retry up to 3 times with exponential backoff before being discarded to a DLQ. Alternative: halt the processing partition to guarantee strict ordering."*
- *"I assumed tenant metadata can be cached in worker memory with a 60-second TTL. Alternative: query the primary database on every call to support instantaneous permission revocations."*

Making these assumptions explicit allows engineers to review and adjust them before writing code.

---

## 18. Using Proprietary Context to Counter the Regression to the Mean

The most effective safeguard against generic, averaged designs is grounding the model in proprietary engineering context.

If an LLM is given only a generic problem statement, it relies entirely on public market patterns. But when supplied with internal technical context, its generation space shifts:

- Internal Architectural Decision Records (ADRs)
- Post-mortem reviews and root-cause analyses from prior production outages
- Real telemetry baselines, traffic patterns, and cost breakdowns
- Company-specific compliance rules and security standards
- Long-term infrastructure roadmaps and operational constraints

$$\text{Generic Model} + \text{Public Documentation} \longrightarrow \text{Averaged Market Solution}$$

$$\text{Generic Model} + \text{Internal Systems Telemetry and Constraints} \longrightarrow \text{Context-Specific Architecture}$$

A standard model provided with deep internal context will reject a generic multi-region distributed pattern if your post-mortems show that your team repeatedly struggles to manage distributed consensus across regions. Internal engineering reality acts as a strong counterweight to the pull of the statistical average.

---

## 19. Defining the Boundaries of Model Authority

Even when equipped with deep internal context, an LLM should never have the authority to make every decision autonomously.

Clear boundaries must separate technical implementation from strategic choice:

```text
+-------------------------------------------------------------------------------+
|                        DECISION AUTHORITY BOUNDARY                            |
+-------------------------------------------------------------------------------+
| SAFE FOR AI AUTONOMY                 REQUIRES HUMAN SYSTEM ARCHITECT          |
|                                                                               |
| - Implementing idiomatic boilerplate  - Setting consistency / isolation tiers |
| - Generating unit / integration tests - Determining data retention / privacy  |
| - Drafting structural interfaces      - Defining blast-radius boundaries      |
| - Analyzing time/space complexity     - Accepting regulatory / compliance risk|
| - Synthesizing trade-off matrices     - Choosing build vs buy trade-offs      |
+-------------------------------------------------------------------------------+
```

When a model encounters a design choice that crosses these boundaries, its instructions should forbid it from inventing a default. Instead, it must stop and escalate:

> *"The requirements do not specify whether stale reads are acceptable during failover events. Because this affects billing reconciliation, this is a product risk that requires an explicit engineering decision before proceeding."*

---

## 20. Shifting the Interaction Model: From Oracle to Engine

The default interaction with an AI assistant follows a simple pattern:

$$\text{User Prompt} \longrightarrow \text{Model Answer}$$

For production system design, this interaction model is dangerous. It encourages passive acceptance of plausible, averaged architectures.

A much safer interaction model treats the AI as an exploration and verification engine:

```text
[Engineering Problem]
         │
         ▼
[Decomposition & Invariant Analysis] ───> Flags hidden product decisions
         │
         ▼
[Orthogonal Exploration Pass]         ───> Discovers distinct design classes
         │
         ▼
[Coverage Audit & Adversarial Checks] ───> Breaks premature consensus
         │
         ▼
[Context-Weighted Trade-Off Matrix]   ───> Evaluates against real constraints
         │
         ▼
[Human Selection & ADR Logging]      ───> Preserves engineering ownership
```

In this framework, the model does not serve as an oracle that dictates how software should be built. It functions as an analytical engine that exposes hidden assumptions, broadens the search space, surfaces edge cases, and accelerates trade-off analysis.

---

## 21. Core Failure Modes and Pragmatic Countermeasures

| Observed Failure Mode | Root System Mechanic | Practical Countermeasure |
| :--- | :--- | :--- |
| **Hidden Decision Injection** | Model completes underspecified prompts by silently sampling defaults from training data. | Require an explicit decision manifest flagging every unmade business choice before generating code. |
| **Solution-Space Collapse** | High-probability tokens dominate the output, crowding out non-standard patterns. | Mandate exploration across four distinct structural classes (e.g., minimalist, standard cloud, radical simplicity, high-performance). |
| **The "More Solutions" Illusion** | Asking for more options yields minor tactical variations of the same root architecture. | Constrain candidates along orthogonal design axes rather than requesting raw item counts. |
| **Evaluation Asymmetry** | Models struggle to surface non-obvious designs spontaneously, but evaluate them effectively when prompted. | Supply external candidate architectures manually and use the model to stress-test their trade-offs. |
| **Regression to the Mean** | Unconstrained models generate standard patterns that match the broader market. | Ground the prompt with proprietary constraints, historical post-mortems, and internal infrastructure limits. |

---

## Conclusion

Language models automate far more than boilerplate code. Left unmonitored, they can quietly narrow technical possibilities, making strategic decisions that an engineering team never consciously reviewed.

Because an LLM samples from an enormous corpus of public documentation and code, its output will usually look clean, plausible, and easy to justify. That is precisely why this problem is subtle. The model does not generate broken designs; it generates the **statistical average of industry designs**.

The opportunity in using modern AI tools is not simply generating code faster. It lies in using the model to widen the search space, surface unstated assumptions, and stress-test trade-offs before an architecture is locked into place.

Keep two practical principles in mind:

1. **Do not use language models merely to generate final answers. Use them to expose hidden decisions and expand the set of viable alternatives before committing to a design.**
2. **A model will frequently fail to generate an optimal solution during open-ended brainstorming, yet analyze that exact solution with high precision once it is supplied in the context.**

The first design returned by a language model should almost never be the final architecture. It is simply the starting point of the search.

---

## Related Notes

- [[Competitive Advantage in the Age of Commodity AI]] — Why accepting default AI recommendations commoditizes technical strategy and how deliberate architectural variance builds defensibility.
- [[How Context Narrows an AI's Solution Space]] — Analysis of the attention mechanisms and prompt constraints that restrict a model's exploratory paths.
- [[How Reasoning Models Explore and Evaluate Solutions]] — A deep dive into search algorithms, multi-path exploration, and how models evaluate alternatives.
- [[How Targeted Prompts Steer Model Solution Spaces]] — Practical techniques for using targeted prompt constraints to guide models out of their default probability distributions.
- [[Designing Software Architecture with LLM Assistance]] — Operational patterns for using LLMs during architectural design while preventing superficial completeness.
- [[Refactoring Legacy Systems with AI Agents]] — How language models anchor on existing git history and patterns when modernizing legacy codebases.
- [[Software Engineering May Shift Toward Code Optimized for Agents]] — Examining system architectures optimized for automated machine maintenance rather than manual human editing.
- [[AI Changes the Role and Training of Software Engineers]] — Why senior engineering requires shifting from syntax generation to problem framing and trade-off verification.
- [[Proxy Metrics and Operational Invariants in AI Systems]] — The operational risks of letting automated systems optimize for proxy metrics over causal system performance.
