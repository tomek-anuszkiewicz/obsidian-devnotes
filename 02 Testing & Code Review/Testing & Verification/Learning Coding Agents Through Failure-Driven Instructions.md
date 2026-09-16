---
title: Learning Coding Agents Through Failure-Driven Instructions
tags:
  - ai-agents
  - agentic-coding
  - continuous-improvement
  - prompt-engineering
  - knowledge-distillation
  - software-engineering
aliases:
  - Failure-Driven Agent Learning
  - Instruction Tuning from Coding Failures
  - Procedural Memory for Coding Agents
  - Eval-Driven Instruction Engineering
  - Dual Optimization Loops
---

# Learning Coding Agents Through Failure-Driven Instructions

When developers hit a wall with an agent generating broken or off-target code, the instinctive reaction is either to silently fix the code by hand or to dump another paragraph of ad-hoc rules into a global prompt file like `AGENTS.md` or `.cursorrules`. Both reactions fail over time: manual fixes teach the harness nothing, while append-only instruction files quickly become bloated, contradictory, and degraded by context limits.

Instead of treating instructions as static prompts or dumping grounds for past grievances, treat them as **versioned, testable engineering artifacts that continuously evolve through failure analysis**. 

The goal is not merely to get an agent to eventually stumble into a passing test suite after eight repair cycles. The actual engineering objective is:

> **Maximize first-pass success: produce production-ready code with the minimum number of iterations by continuously refining the instructions, constraints, and operational context fed to the model.**

This architecture establishes two nested optimization loops.

```text
Ad-hoc Prompting ──► Project Instructions ──► Eval-Driven Rules ──► Organizational Procedural Memory
```

---

## 1. The Two Nested Optimization Loops

Agent-assisted software engineering operates across two distinct feedback loops that operate on different timeframes and address different failure modes.

```text
Outer Loop: Team Learning (Eval-Driven Instruction Tuning)
┌────────────────────────────────────────────────────────────────────────┐
│ Task Specification + Versioned Instructions (vN)                       │
│     │                                                                  │
│     ▼                                                                  │
│ Inner Loop: Code Generation & Deterministic Feedback                   │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ Agent Generates Code ──► Compiler / Lint / Tests ──► Pass / Fail   │ │
│ │      ▲                                              │              │ │
│ │      └────────── Local Fix Loop ────────────────────┘              │ │
│ └────────────────────────────────┬───────────────────────────────────┘ │
│                                  │ (Task Complete or Blocked)          │
│                                  ▼                                     │
│ Analyze Root Cause ──► Extract Invariant ──► Evaluate Historical Suite │
│                                  │                                     │
│                                  ▼                                     │
│              Commit Updated Instruction Set (vN+1)                     │
└────────────────────────────────────────────────────────────────────────┘
```

### The Inner Loop: Improve the Code
The inner loop is the local execution cycle running inside the developer's environment or CI container:

```text
task
  ↓
agent generates code
  ↓
compile / tests / static analysis / review
  ↓
failure
  ↓
agent fixes code
  ↓
...
  ↓
success
```

This inner loop is practical today because modern software environments provide strong, automated, and deterministic feedback:
- Compiler and typechecker errors
- Unit and integration tests
- Architectural boundary tests (e.g., NetArchTest, ArchUnit)
- Static analysis and security scanning
- Linters and formatters
- Performance benchmarks
- Repository-level validation scripts

The agent can query these tools, ingest the diagnostic output, and repeatedly modify its implementation until the automated checks pass. 

However, relying entirely on the inner loop leaves the system with complete operational amnesia. The agent will make the exact same architectural blunder on Friday that it made on Monday, burning compute, burning tokens, and requiring another five iterative compile-and-fix cycles to rediscover boundaries that were already known.

### The Outer Loop: Improve the Instructions
The outer loop operates above individual tasks, capturing diagnostic data from agent runs to upgrade the system's baseline guidance:

```text
task
+
instruction v12
  ↓
agent
  ↓
failure
  ↓
analyze why the failure happened
  ↓
extract a reusable lesson
  ↓
generate candidate instruction changes
  ↓
evaluate them
  ↓
instruction v13
```

Here, the system is not just solving:
> *How do we fix this immediate implementation?*

It is solving:
> *What context, rules, or architectural constraints should the agent have received so that this entire class of mistake would not occur in the first place?*

Over time, this loop converts repeated production failures into structured, permanent institutional knowledge.

---

## 2. Example: Enforcing Architectural Boundaries

Suppose an agent is assigned a straightforward backend feature:
> *"Add an endpoint returning customer order history."*

### The Naive Implementation
The agent inspects existing controllers, writes the endpoint, and wires it directly to the database context:

```text
[ HTTP Controller / Endpoint ]
             │
             │ (Direct database query: boundary violation)
             ▼
      [ DbContext ]
```

The unit tests pass. The database queries execute correctly. But the architecture test suite fails in CI because controllers are strictly forbidden from touching persistence primitives directly.

### Extracting the Systematic Rule
Instead of simply telling the agent to "fix this controller," the outer loop records the structural failure:

```text
Failure:
Controller accessed DbContext directly.

Underlying reason:
The agent lacked context regarding the application's clean architecture boundaries.

Candidate rule:
Controllers and transport adapters must delegate to application handlers and must not access persistence directly.
```

When this rule is integrated into the instruction context, the agent's baseline behavior changes across all subsequent tasks.

```text
[ HTTP Controller ] ──► [ Application Query Handler ] ──► [ DbContext / Storage ]
```

Rather than burning three iterations on a broken path:
```text
task ──► bad implementation ──► compiler/arch feedback ──► repair loop ──► success
```
the system achieves:
```text
task ──► correct implementation on turn one
```

---

## 3. The Critical Metric: First-Pass Success

Tracking raw task completion rates is a deceptive metric. An agent that eventually succeeds after eight compile-and-fix cycles is far more expensive—and far more frustrating to work with—than one that gets the implementation right on the first attempt.

Long repair loops introduce subtle technical debt. When an LLM spends five consecutive turns attempting to satisfy a compiler or lint rule, it often starts introducing defensive, bloated code—unnecessary null-coalescing operators, redundant type assertions, and weird wrapper abstractions—just to stop the linter from screaming.

### Core Metrics to Track
- **First-Pass Success Rate**: The percentage of tasks completed cleanly without requiring corrective repair cycles.
- **Average Iteration Depth**: The number of compile, test, and repair cycles per completed task.
- **Token and Compute Cost**: Total prompt and completion tokens spent per merged pull request.
- **Execution Latency**: End-to-end wall-clock time from task assignment to passing verification.
- **Regression Rate**: The frequency with which an agent's changes break existing tests in adjacent subsystems.
- **Human Review Overhead**: Engineering minutes spent auditing and correcting agent-authored pull requests.

A balanced optimization score looks like this:

$$\text{Score} = \text{Quality} - (\text{Cost}_{\text{iteration}} + \text{Cost}_{\text{tokens}} + \text{Cost}_{\text{latency}} + \text{Cost}_{\text{regression}} + \text{Cost}_{\text{review}})$$

The primary KPI for an organization's agent harness is simple:
> **How often can the agent produce an acceptable, production-ready pull request without corrective feedback?**

---

## 4. Avoiding the Append-Only Trap (Instructions as Code)

The fastest way to ruin an agent harness is the naive append-only approach:

```text
failure ──► append rule ──► failure ──► append rule ──► failure ──► append rule
```

Within a few months, your instruction file turns into a sprawling, 1,500-line dumping ground. When prompt instructions become bloated and repetitive, models suffer from rule oscillation and constraint saturation. They hyper-fixate on the rules at the very end of the prompt or those written in all-caps, while quietly ignoring foundational architectural constraints.

Failure analysis must be an active filtering and refinement pipeline:

```text
                      Agent Mistake Observed
                                │
                                ▼
                       Extract Core Lesson
                                │
                                ▼
                   Check Existing Knowledge
                                │
                                ▼
               Generalize & Detect Contradictions
                                │
                                ▼
                    Draft Candidate Formulations
                                │
                                ▼
                Evaluate Against Historical Tasks
                                │
                   ┌────────────┴────────────┐
                   ▼                         ▼
          [ Measurable Delta ]       [ Neutral / Regressive ]
                   │                         │
                   ▼                         ▼
             Instruction vNext             Discard
```

Instructions must be managed with the exact same engineering discipline applied to production source code:
- **Versioned**: Tracked in Git with explicit commit histories and changelogs.
- **Tested**: Evaluated against historical benchmark tasks before being pushed to production prompts.
- **Reviewed**: Subject to peer review by senior engineers before merging.
- **Refactored**: Regularly consolidated to eliminate overlapping or redundant guidance.
- **Pruned**: Ruthlessly deleted when framework upgrades, linter additions, or architectural changes make them obsolete.

---

## 5. Evaluating and A/B Testing Rule Formulations

Different phrasings of the exact same architectural constraint yield wildly different completion patterns. 

Consider three candidate formulations for keeping persistence out of the transport layer:

### Version A (Strict Proscription)
```text
Do not access DbContext from controllers.
```

### Version B (Architectural Boundary Definition)
```text
Controllers are transport adapters only.
They may validate transport-level input and invoke application handlers,
but must not access persistence directly.
```

### Version C (Procedural / Step-by-Step)
```text
Before modifying an HTTP endpoint:
1. Identify the application handler.
2. Place persistence access inside the handler.
3. Keep the controller limited strictly to transport concerns.
```

These candidate rules should not be evaluated on aesthetic preference. Run them against a benchmark suite of historical tasks representing typical controller modifications and evaluate the trade-offs:

| Instruction Variant | Success Rate | Avg. Attempts | Cost / Overhead |
| :--- | :---: | :---: | :---: |
| **Current Baseline** | 82% | 2.1 | Low |
| **Version A** | 84% | 1.9 | Low |
| **Version B** | 91% | 1.4 | Medium |
| **Version C** | 92% | 1.3 | High |

While Version C provides the lowest iteration count, its procedural verbosity consumes significantly more prompt tokens on every call. Version B might represent the superior engineering trade-off: a 9% bump in reliability with minimal context overhead. 

The objective is finding the optimal balance of:
$$\text{Quality} \times \text{Reliability} \times \text{Iteration Count} \times \text{Token Cost}$$

The longest, most pedantic prompt is rarely the best system-level choice.

---

## 6. Preventing Instruction Overfitting

A critical failure mode when optimizing instructions is local overfitting:

```text
task fails
  ↓
tweak instruction for that exact edge case
  ↓
rerun that specific task
  ↓
task passes
  ↓
declare victory and commit
```

Tweaking instructions solely to pass the task that just failed almost always results in over-indexing on an isolated symptom. You end up with hyper-specific rules that teach the model how to solve yesterday's bug while breaking its ability to generalize across tomorrow's features.

Instruction engineering should follow the same disciplined dataset splits used in standard machine learning workflows:

```text
TRAIN SET
Historical failures and reference tasks
  ↓
Optimize candidate instructions

VALIDATION SET
Distinct tasks across adjacent modules
  ↓
Check whether the rule generalizes without unintended side effects

HOLDOUT SET
Unseen production tasks
  ↓
Measure actual first-pass success rate improvement
```

If a candidate rule improves the order management endpoints on the train set but degrades performance on identity management tasks in the validation set, it cannot be merged without refinement.

---

## 7. Behavioral RAG: Loading Rules on Demand

As a team accumulates dozens of hard-won lessons, injecting every single rule into every prompt blows out the model's context window, runs up API costs, and dilutes the model's attention over long input sequences.

Instead of maintaining a massive, monolithic instructions file, organize instructions by domain, runtime, and architectural boundary:

```text
instructions/
├── architecture/
│   ├── boundaries.md
│   ├── messaging.md
│   └── persistence.md
├── dotnet/
│   ├── ef-core.md
│   ├── cancellation.md
│   └── serialization.md
├── business/
│   ├── pricing.md
│   ├── reservations.md
│   └── authorization.md
└── testing/
    ├── integration-tests.md
    └── test-data.md
```

When an agent is assigned a task such as:
> *"Implement cancellation for hotel room reservations"*

the runtime harness dynamically resolves the task's context and retrieves only the matching operational modules:

```text
architecture/boundaries.md
business/reservations.md
business/authorization.md
testing/integration-tests.md
```

This is **Behavioral RAG**. Instead of retrieving informational text to answer a factual question, the harness retrieves targeted operational constraints and execution procedures required to complete a specific task correctly.

---

## 8. Compressing Knowledge and Rule Garbage Collection

Over time, independent failures lead to overlapping, redundant instructions across different rule files:

```text
Never instantiate HttpClient manually.

Use IHttpClientFactory.

External integrations must use typed clients.

Handlers should not construct HttpClient directly.
```

Leaving all four statements in place wastes context and forces the model to process noisy, fragmented constraints. A background meta-agent or a prompt engineer can periodically sweep the instruction base, identify semantic overlap, and consolidate the rules into a single structural invariant:

```text
External HTTP integrations must use the project's registered typed clients.
Application code must not instantiate HttpClient directly.
```

The compressed instruction set is then executed against the regression benchmark suite. If the first-pass success rate holds steady, the redundant rules are permanently pruned.

This mechanism serves as a **garbage collector for agent memory**, keeping instructions tight, dense, and unambiguous.

---

## 9. High-Leverage Code Review: The "Don't Patch in Silence" Rule

Not every architectural or domain failure can be caught by a compiler, static analysis tool, or unit test. The most insidious bugs are syntactically and functionally valid, but fundamentally violate domain logic:

> *"The code compiles and the tests pass, but this domain model does not reflect how our business actually works."*

For example, a senior engineer reviewing a pull request might note:
```text
A hotel reservation is not cancelled immediately upon receiving the HTTP request.
Cancellation creates an asynchronous request that must be evaluated against our refund 
and inventory policies before being confirmed or rejected.
```

### Traditional Code Review vs. Compounding Code Review

In traditional code review, this insight is ephemeral:

```text
Traditional Review:
agent makes mistake ──► human explains domain nuance ──► agent patches PR ──► insight lost in PR history
```

In a compounding, learning-oriented harness, that same human comment becomes a permanent system asset:

```text
Compounding Review:
agent makes mistake ──► human explains domain nuance ──► insight encoded into rule/test
                              │
                              ▼
                added to behavioral regression suite
                              │
                              ▼
                future agents avoid the entire category of error
```

### The Don't-Patch-in-Silence Rule
To stop organizational knowledge from bleeding out through quick manual fixes, engineering teams should enforce a clear operational principle: **never silently patch an agent's architectural or domain mistake by hand.**

1. **The Silent Fix Anti-Pattern**: A developer spots an architectural violation or a clumsy abstraction in an agent-authored branch. To save two minutes, the developer manually rewrites the code, commits it, and merges the PR. The immediate problem is solved, but the system learned nothing. The next agent will make that exact same mistake tomorrow.
2. **Codify the Correction**: Instead of silently patching the code, spend two minutes encoding the correction into an architectural rule file, an example pair, or a failing architecture test.
3. **Compound Team Velocity**: By treating recurring mistakes as defects in the system's operational context rather than isolated annoyances, the entire engineering organization moves faster with every pull request.

---

## 10. What Can Be Automated Today?

Understanding where the automated feedback loop excels versus where it requires human mediation dictates how you structure your evaluation pipeline:

### Strong Automatic Feedback (Fully Automatable Inner & Outer Loops)
These domains provide immediate, high-fidelity deterministic signals that an agent harness can self-heal and optimize against with zero human intervention:
- Compilation and type verification
- Unit and integration tests
- Architecture boundary rules (e.g., dependency direction)
- Linters and code formatters
- Static analysis and vulnerability scanning
- Performance benchmarks and memory profiling
- Repository conventions and file path naming rules

For these vectors, an outer-loop harness can automatically monitor failure rates, test candidate instruction adjustments, and commit prompt updates directly to the repository.

### Weak Automatic Feedback (Requires Human Insight)
These areas cannot be evaluated purely through deterministic execution and still require human engineering judgment:
- Domain modeling and entity boundary definitions
- Architecture trade-offs (e.g., choosing between sync RPC vs. event-driven messaging)
- Unclear or conflicting business semantics
- Long-term maintainability and readability
- Unnecessary abstractions and premature generalizations
- Conceptual alignment with product intent

Even in these subjective areas, the human engineer only needs to supply the core structural insight once. The outer-loop harness transforms that review insight into reusable operational context, ensuring the model never trips over the same conceptual hurdle again.

---

## 11. System Evolution Over Model Upgrades

A foundational shift occurs when you stop relying on LLM model upgrades to fix your team's velocity issues:

**The underlying foundation model can remain completely static, while the system around it becomes dramatically more intelligent, capable, and efficient.**

```text
Foundational LLM
+
Repository Context
+
Fast Deterministic Feedback (Compilers, Linters, Tests)
+
Behavioral Regression Suite
+
Versioned Organizational Instructions
+
Curated Examples of Production Patterns
+
Structured Failure History
+
On-Demand Behavioral Retrieval
+
Closed-Loop Review Feedback
```

After sufficient iterations through the outer loop, a standard, off-the-shelf foundation model running inside a disciplined harness will easily outperform a newer, larger, unguided model operating on raw prompts. The competitive advantage is not the raw model weights; it is the accumulated, versioned operational memory of your engineering organization.

---

## The Mental Model

The evolution of agent-assisted software engineering follows a clear maturity curve:

```text
Prompt Engineering
  ↓
Instruction Engineering
  ↓
Eval-Driven Instruction Development
  ↓
Organizational Agent Learning
```

The enduring asset of a high-performing software team is not a collection of massive, monolithic prompt files. It is an evolving engineering harness comprising:
- Curated reference tasks
- Historical failure profiles
- Codified domain rules
- Representative structural examples
- Targeted behavioral retrieval pipelines
- Automated evaluation suites

The ultimate operational goal:
> **Every meaningful agent failure must increase the probability that future agents avoid that entire class of mistake.**

Through this disciplined dual-loop architecture, an organization systematically builds its own **procedural memory for software engineering agents**.

---

## Related Notes
- [[Agentic Coding Harness and Controlled Development Workflows]] — Designing execution environments that bridge LLM generation with deterministic tools.
- [[Constraint Saturation and Rule Oscillation in Coding Agents]] — Managing prompt density and avoiding failure modes when models are given too many conflicting rules.
- [[Negative Knowledge and Explicit Architectural Dissents]] — Documenting and retrieving rejected approaches to keep agents on approved paths.
- [[How LLM Systems Build Context]] — Context window management, working memory constraints, and token optimization strategies.
- [[Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification]] — Operational strategies for determining whether to fix code locally or update the specification.
- [[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]] — Leveraging secondary agent workflows to catch nuanced architectural violations before human review.
- [[Testing in the Model, Agent, LLM Era]] — Structuring test suites to serve as high-signal, automated feedback loops for generative models.
