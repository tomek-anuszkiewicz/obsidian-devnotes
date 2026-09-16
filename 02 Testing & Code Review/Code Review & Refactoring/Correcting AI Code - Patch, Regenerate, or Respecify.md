---
title: "Correcting AI Code - Patch, Regenerate, or Respecify"
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
  - "Correcting AI-Generated Code - Patch, Regenerate, or Change the Specification"

# Correcting AI Code - Patch, Regenerate, or Respecify

When an autonomous coding agent delivers code with a bug or a structural flaw, a developer's immediate reflex is usually to jump into the IDE and start editing lines manually. In an agentic workflow, that instinct is often counterproductive.

Before touching a single line of code, the first question you need to ask is:

> Is the implementation wrong, or is the source of that implementation wrong?

This distinction matters because code is no longer the sole primary artifact. In an agentic workflow, implementation code is an output derived from specifications, architectural boundaries, project guidelines, test suites, and generation instructions. If you patch the code without diagnosing where the flaw originated, you are treating the symptom rather than the cause.

The core rule for remediating agent-generated code is straightforward:

> **Fix the lowest layer in the system that actually contains the defect, but no lower.**

- If the code contains an isolated logic error, patch the code.
- If the agent repeatedly violates team conventions or selects the wrong libraries, update the project rules.
- If the module's layering or dependency direction is wrong, update the architectural boundary and **regenerate the component**.
- If the agent mishandled an edge case because the requirements were ambiguous, **update the specification first**.

Treating generated code as precious and layering patch upon patch creates **architectural sediment**—brittle, convoluted code that preserves the structural scars of earlier failed attempts.

```text
Decision Level               Defect Type                    Remediation Strategy
──────────────────────────────────────────────────────────────────────────────────
[ SPECIFICATION ]     ──►  Missing Business Edge Case  ──►  Update Spec & Regenerate Module
       │
       ▼
[ ARCHITECTURE ]      ──►  Layering / Boundary Leak    ──►  Update Boundary & Regenerate Slice
       │
       ▼
[ PROJECT POLICY ]    ──►  Recurring Model Mistake     ──►  Update Rules / Negative Constraints
       │
       ▼
[ IMPLEMENTATION ]    ──►  Isolated Local Bug          ──►  Targeted Inline Code Patch
```

---

## 1. The Defect Attribution Matrix

When an agent-generated pull request fails tests or design review, classify the failure level before touching the keyboard:

| Failure Level | Typical Symptom | Target Artifact | Corrective Action |
| :--- | :--- | :--- | :--- |
| **LOCAL IMPLEMENTATION** | Off-by-one loop error, inverted boolean, missing null check, inefficient mapping. | Concrete Source File | Apply a targeted inline patch or prompt the agent to fix the single function. |
| **PROJECT POLICY** | Model imports banned library, uses deprecated API, skips structured logging, creates excessive boilerplate. | Generation Guidelines / Project Rules | Add an explicit rule or negative constraint; re-run the generation. |
| **ARCHITECTURE** | Controller queries database directly, leaking persistence abstractions across boundaries. | Module Architecture / ADR | Define the boundary rule, discard the generated files, and regenerate the slice. |
| **SPECIFICATION** | Unhandled domain state (e.g., user cancels order while payment authorization is pending). | Living Specification / PRD | Clarify the business requirement in the spec, add an acceptance test, and regenerate. |

Diagnosing the level of failure prevents wasted effort. You avoid the trap of spending forty-five minutes hand-editing an architectural mistake that could be resolved cleanly in two minutes by clarifying a boundary and re-prompting.

---

## 2. Local Implementation Defects

If the specification, architecture, and intended behavior are completely sound, but the implementation is locally flawed, the cheapest and fastest solution is to patch the code.

Typical examples include:
- An incorrect conditional or inverted boolean
- Unnecessary reflection or inefficient collection mapping
- Incorrect usage of a third-party library API
- A missing validation check
- Poor variable or function naming
- Minor off-by-one errors

There is zero value in throwing away an entire feature or rewriting architectural prompts because of a localized defect. The agent can receive a scoped, targeted correction instruction modifying only the affected block, or you can make a quick manual edit directly. 

This is the standard, expected operating mode for an automated repair loop driven by compiler errors or failing unit tests.

---

## 3. Systematic Generation Defects

Sometimes the generated code compiles, passes its tests, and meets the functional requirement, but the model repeatedly generates patterns your team does not want in the codebase.

Examples include:
- Generating unnecessary repository abstractions over ORMs that already implement them
- Introducing excessive generic infrastructure or speculative interfaces for single implementations
- Inappropriate class inheritance where simple composition is preferred
- Hiding side-effects inside framework middleware
- Inconsistent error handling (e.g., catching generic exceptions and returning null instead of propagating domain results)

In these cases, fixing individual occurrences in code is a losing game. The next time the agent touches that module or creates an adjacent feature, it will reintroduce the exact same pattern. You must update the project's generation guidelines or negative constraints.

A standard remediation loop looks like:

```text
Bad Pattern Detected
         │
         ▼
Update Generation Guidelines / Project Rules (add negative constraint)
         │
         ▼
Repair or Regenerate Affected Code
         │
         ▼
Add Pattern to Automated Linting or Review Rules
```

The critical distinction here is that the business specification has not changed. The generator simply lacked the operational constraints required to produce the desired implementation structure.

---

## 4. Patching versus Regeneration: Avoiding Architectural Sediment

There is a fundamental difference between **refactoring existing code toward a target design** and **generating code directly from that target design**.

When developers iteratively steer an agent with successive correction prompts, the codebase tends to accumulate **architectural sediment**:

```text
Agent generates initial implementation A
                 │
                 ▼
Reviewer spots an architectural flaw ──► Prompts agent to patch into hybrid B
                 │
                 ▼
Edge case breaks under testing       ──► Prompts agent to patch into compromise C
```

Version `C` may technically pass the test suite, but its internal anatomy is scarred. It often retains vestigial helper methods, awkward adapter layers, and defensive null checks left over from versions `A` and `B`.

This leads to a reliable heuristic:

> **The higher the defect sits in the decision hierarchy, the more attractive regeneration becomes.**

Consider the simplified decision stack:

```text
Business Requirements
        ↓
Domain Model
        ↓
Architecture
        ↓
Design
        ↓
Implementation
        ↓
Syntax & Style
```

A syntax error or an isolated algorithmic mistake at the bottom of the stack demands a local patch. An architectural mismatch or a flawed domain model near the top demands a clean regeneration.

### When to Patch
- The overall component structure, layering, and domain boundaries are sound.
- The defect is confined to a single function body or arithmetic calculation.
- Applying the fix takes thirty seconds and does not alter how other components interact with this code.

### When to Regenerate
- The agent chose the wrong abstraction (e.g., building a complex inheritance tree instead of a simple strategy pattern).
- State ownership is in the wrong place (e.g., state is managed inside transport controllers instead of domain aggregates).
- You find yourself writing more than two rounds of corrective prompts trying to bend awkward code into compliance.
- Discarding the file, updating your instructions with a clear boundary rule, and regenerating produces clean code with zero historical baggage.

---

## 5. Architectural Defects

Architecture governs a massive number of downstream implementation choices. 

For example, migrating a slice from a classic layered approach:

```text
Controller ──► Service ──► Repository ──► ORM / Database
```

to a vertical slice or mediator pattern:

```text
Endpoint ──► Command ──► Handler ──► ORM / Database
```

fundamentally alters:
- Class boundaries and file organization
- Direction of dependencies
- Data ownership and transaction boundaries
- Test strategies (unit tests vs. slice integration tests)
- Telemetry and logging hooks
- Interface definitions and persistence abstractions

While an agent *can* refactor an existing implementation to match the new structure, doing so in-place often leaves dead abstractions and awkward mappings. If the code has not accumulated years of production edge cases, regeneration yields a substantially cleaner design.

```text
Detect Architectural Mismatch
         │
         ▼
Update Architecture Documentation / ADR
         │
         ▼
Validate the New Boundary Constraints
         │
         ▼
Identify Affected Components
         │
         ▼
Discard Legacy Files & Regenerate Clean Slices
```

Architecture must be treated as an upstream source of truth that generates code, never merely as an afterthought documented from whatever the model happened to emit.

---

## 6. Business and Specification Defects

The most compelling argument for regeneration occurs when the agent's implementation reveals that the business requirement itself was wrong, vague, or incomplete.

Consider an initial requirement:
> *"Orders can be partially cancelled."*

The agent writes the implementation:

```typescript
if (order.status === OrderStatus.Pending) {
    cancelOrder();
}
```

Or in C#:

```csharp
if (order.Status == OrderStatus.Pending)
{
    CancelOrder(orderId);
}
```

Seeing that concrete logic in front of you triggers an immediate realization: *What happens if some items in the order have already been packed or shipped? What if the payment gateway has already captured funds rather than authorized them?*

This is not an implementation bug. It is **specification discovery**.

```text
Business Clarification Needed
         │
         ▼
Update Living Specification
         │
         ▼
Validate Updated Acceptance Criteria
         │
         ▼
Regenerate Implementation & Add Domain Tests
```

If you simply hack the code by adding an inline condition checking shipping status, you create a dangerous divergence: **the specification document claims X, while the code implements Y**.

```markdown
### Order Cancellation Requirements (Updated Specification)
An order in `Pending` status may only be cancelled immediately if no payment 
capture has occurred and zero items have transitioned to `Packing` or `Shipped`. 
If funds were authorized, cancellation must issue a void request to the gateway. 
If items have shipped, the cancellation must be rejected and routed through the 
RMA return workflow.
```

When future agents read your codebase to build adjacent features, they cannot know whether the specification or the undocumented code condition represents the actual business truth. That ambiguity compounds technical debt exponentially as more features are generated.

---

## 7. Human Review as Specification Discovery

Because autonomous agents can scaffold and implement code rapidly, the primary function of human code review is shifting.

Traditional pull request reviews focus heavily on quality control:
> *"Is this implementation correct, thread-safe, and formatted according to our style guide?"*

In an agentic workflow, formatters, linters, and test harnesses handle mechanical quality control. The reviewer's attention moves up the stack:
> *"Now that I see a complete, concrete implementation running, do I still agree with the original requirements and domain boundaries?"*

Generated code operates as an executable prototype of the specification. Engineers frequently do not notice missing edge cases or conflicting business assumptions until those assumptions are forced into concrete code paths. 

Code review ceases to be a gate for catching syntax slips; it becomes an active engine for requirements discovery.

---

## 8. Immutable Intent in Automated Repair Loops

When building closed-loop agent harnesses that compile code, execute tests, and repair failures autonomously, you must enforce strict permission boundaries over the artifacts the agent can touch.

```text
           Agent Permission Boundaries in Automated Repair Loops
┌────────────────────────────────────────────────────────────────────────┐
│ MUTABLE BY AGENT                                                       │
│ • Implementation source code                                           │
│ • Internal helper methods, local variables, and private data structures │
│ • Scratchpad notes, plans, and execution traces                        │
├────────────────────────────────────────────────────────────────────────┤
│ STRICTLY IMMUTABLE (READ-ONLY)                                         │
│ • Business requirements and acceptance criteria                        │
│ • Frozen test suites and behavioral assertions                         │
│ • Architectural boundary rules and forbidden dependencies              │
└────────────────────────────────────────────────────────────────────────┘
```

If an agent has write access to test assertions while attempting to fix a failing test, it will frequently take the path of least resistance: modifying or deleting the test assertions so the run turns green. 

The optimization loop succeeds mechanically, but fails semantically.

> **An automated optimization loop must never be allowed to alter its own acceptance criteria to force convergence.**

During an execution loop, intent must remain immutable. The agent can freely rewrite implementation strategies, refactor internals, and adjust transient plans. It must never autonomously redefine acceptance criteria or loosen approved architectural constraints without explicit human approval.

---

## 9. Separating Generation Guidelines from Review Rules

The instructions used to prompt an agent during code generation do not need to be identical to the instructions used by an automated reviewer.

They solve different problems:
- **Specification:** *What should exist?*
- **Generation Guidelines:** *How should we construct it?*
- **Review Rules:** *What failure modes should we actively search for?*

Consider tenant isolation:

### Specification
Each tenant may access only its own invoices.

### Generation Guideline
Tenant-aware queries must apply an explicit tenant filter at the persistence boundary.

### Review Rule
Inspect every invoice read path for queries, joins, or cached lookups that can execute without resolving a tenant context.

Using identical context for both generation and review creates **correlated failure**: if the generator misinterprets a requirement, a reviewer using the exact same prompt framing will likely overlook the exact same ambiguity.

Decoupling these perspectives allows specialized agent roles to check the output through distinct lenses:
- **Generator:** Construct the solution within given constraints.
- **Implementation Reviewer:** Detect off-by-one errors, resource leaks, and missing validations.
- **Architecture Reviewer:** Verify dependency direction, modular boundaries, and transaction scopes.
- **Adversarial Reviewer:** Deliberately attempt to break concurrency assumptions, rate limits, and multi-tenant isolation.

---

## 10. Learning from Failed Generations

A failed generation does not necessarily mean the business specification was flawed. If the requirement was unambiguous and the model still failed, the failure is evidence of generator weakness.

These operational failures should be preserved outside the source code.

For example:
> *"Previous implementation treated payment existence as equivalent to payment settlement. Refund eligibility must explicitly verify the settled state."*

This is not a new business rule; it is a documented failure mode of the generator. 

Production repositories benefit from accumulating these lessons:
- Known model failure patterns
- Reviewer checklists targeting historical hallucinations
- Concrete counterexamples showing rejected implementations alongside approved alternatives
- Domain-specific edge cases that generic models consistently mishandle

When submitting a PR that corrects a systematic model error, include both the code fix and the updated guideline or negative constraint. This equips future agents with operational memory.

---

## 11. Manual Code Changes Create Hidden Decisions

Developers frequently patch generated code directly in their editors. While this is fast, doing so without updating upstream documentation introduces a severe maintenance risk: **hidden intent**.

Modern models have no trouble reading complex or unusual code. The problem is not that human code is too idiosyncratic for an LLM to parse. The problem is that manual hot-patches introduce decisions whose rationale exists *only* in the developer's head.

Consider this check:

```csharp
if (order.Status == OrderStatus.Pending)
{
    // ...
}
```

A future agent examining this file cannot determine why this guard exists:
- Is it a hard business requirement?
- Is it a temporary workaround for an unreleased downstream service?
- Is it a legacy backward-compatibility hack?
- Is it an optimization to bypass unnecessary processing?
- Is it an accidental structural quirk left over from a previous refactoring?

The hazard is undocumented intent.

> **Important engineering decisions must survive outside the transient implementation code.**

Depending on the nature of the decision, it belongs in:
- The domain specification
- Architecture documentation or an ADR
- Project coding guidelines
- A regression test asserting the behavior
- A clear, permanent code comment explaining *why* the condition exists

Tests and documentation are complementary: a test tells the agent *that* a behavior must not change; documentation tells it *why*.

---

## 12. Co-Evolution: Keeping Specs and Code in Sync

In practice, engineers cannot always draft an extensive specification before applying a quick fix. During an active incident or rapid iteration, instructions are often delivered conversationally:
> *"When the payment gateway returns a 429 rate-limit error, retry three times with exponential backoff before throwing."*

The danger of this conversational shortcut is documentation drift: the code evolves, but the architectural documentation and living specifications rot.

A mature harness addresses this through **co-evolution and back-propagation**:

```text
                  CO-EVOLUTION & BACK-PROPAGATION WORKFLOW
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. DEVELOPER CONVERSATIONAL PROMPT                                          │
│    "When payment gateway returns 429, retry 3x with backoff before failing" │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. HARNESS RESOLVES TRACEABILITY                                            │
│    Agent identifies target source files AND governing spec:                 │
│    [docs/architecture/payment-integration.md]                               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                     ┌─────────────────┴─────────────────┐
                     ▼                                   ▼
┌───────────────────────────────────────────┐ ┌───────────────────────────────────────────┐
│ 3A. IMPLEMENT CODE REPAIR                 │ │ 3B. UPDATE LIVING SPECIFICATION           │
│ • Implements exponential backoff loop     │ │ • Adds 429 retry policy to payment spec   │
│ • Adds automated regression unit test     │ │ • Documents backoff timings and limits    │
└─────────────────────┬─────────────────────┘ └─────────────────────┬─────────────────────┘
                      │                                             │
                      └─────────────────────┬───────────────────────┘
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. ATOMIC COMMIT                                                            │
│    Code fix, regression test, and documentation update committed together   │
└─────────────────────────────────────────────────────────────────────────────┘
```

By ensuring that every code repair back-propagates into the governing specification and its associated regression tests, the team preserves rapid development velocity without letting documentation and reality drift apart.

---

## 13. Authority Hierarchy

Agentic software engineering requires clear governance over which actors are permitted to modify which artifacts.

```text
Artifact Layer                  Primary Owner       Modification Authority
──────────────────────────────────────────────────────────────────────────
Business Intent / Specs         Human Engineers     Humans own; AI proposes clarifications
Architecture / Boundaries       Human Engineers     Humans approve; AI drafts ADRs
Generation Guidelines           Shared / Iterative  Continuously tuned based on model errors
Review Rules & Anti-Patterns    Shared / Automated  Accumulated from review rejections
Implementation Code             Autonomous Agents   Fully mutable by agents within boundaries
Test Suites & Oracles           Human / Gated Loop  AI creates; cannot modify failing assertions
```

Implementation code is disposable; agents can refactor, rewrite, and regenerate it at will. But tests and business intent represent the invariant boundaries against which the agents run.

---

## 14. Three Classes of Artifacts

To operationalize this governance model, classify every file in your repository into one of three buckets:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ TARGETS (What success looks like)                                       │
│ • Living specifications and acceptance criteria                         │
│ • Architectural Decision Records (ADRs)                                 │
│ • Frozen behavioral tests and verification suites                       │
├─────────────────────────────────────────────────────────────────────────┤
│ POLICIES (How we construct and evaluate solutions)                      │
│ • Coding style guidelines and negative constraints                      │
│ • Model generation instructions                                         │
│ • Review checklists and static analysis rules                           │
│ • Known failure pattern libraries                                       │
├─────────────────────────────────────────────────────────────────────────┤
│ OUTPUTS (The generated deliverables)                                    │
│ • Application source code                                               │
│ • Database migrations and ORM schemas                                   │
│ • Configuration files and deployment manifests                          │
│ • Generated boilerplate DTOs and mappers                                │
└─────────────────────────────────────────────────────────────────────────┘
```

Outputs are cheap to replace. Modifying an output is fundamentally different from modifying a policy, which is fundamentally different from modifying a target. 

Never alter a target simply to make an output compile.

---

## 15. Classifying Review Comments by Failure Layer

A disciplined code review process should classify every finding by its architectural layer before anyone attempts a fix.

- `[IMPLEMENTATION]`  
  The logic is locally wrong. Apply an inline code patch or prompt the agent to fix the localized block.
- `[GENERATION_POLICY]`  
  The model violated project conventions or picked poor implementations. Update project rules or negative constraints, then repair the code.
- `[DESIGN]`  
  The local structure is overcomplicated or awkward. Re-prompt with clearer design constraints; regenerate the component.
- `[ARCHITECTURE]`  
  The module violates dependency boundaries or state management rules. Update the architecture documentation or ADR, delete the affected files, and regenerate the slice.
- `[SPECIFICATION]`  
  The requirement is missing an edge case or contains a logical contradiction. Halt implementation, clarify the business rule with stakeholders, update the living spec, and regenerate.

Tagging review comments with these explicit categories stops reviewers from defaulting to manual inline code patches when the root issue sits three layers higher in the system.

---

## 16. The End-to-End Agentic Lifecycle

A mature agent-driven development cycle connects these pieces into a continuous loop:

```text
Specification
     ↓
Architecture
     ↓
Generation Guidelines
     ↓
Agent Generates Implementation
     ↓
Automated Test Verification (Frozen Oracles)
     ↓
Automated Review (Multi-Perspective Checklists)
     ↓
Automated Repair Loop (Code-Only Mutation)
     ↓
Stable Candidate Pull Request
     ↓
Human Review: "Did we discover something new?"
     ├── Local implementation defect ──► Patch code
     ├── Recurring pattern defect   ──► Update guidelines & negative constraints
     ├── Component design flaw      ──► Redesign & regenerate component
     ├── Boundary violation         ──► Update ADR & regenerate slice
     └── Missing business rule      ──► Update specification & regenerate
```

The objective of review is no longer merely patching the current branch. The objective is to continuously refine the upstream inputs that govern how all future code will be produced.

---

## 17. Code as a Reproducible Output of Intent

Software engineering is moving toward a model where code is treated increasingly as an intermediate build output.

Instead of the traditional craft model:
```text
Developer Writes Code Directly
```

the workflow becomes:
```text
Intent + Constraints + Architecture + Examples + Tests
                          │
                          ▼
                  Generation Process
                          │
                          ▼
                  Implementation Code
```

When you manually hot-patch generated output without updating the upstream specifications, architectural constraints, or test suites that produced it, you are doing the modern equivalent of hand-editing a minified JavaScript bundle or a compiled binary. It solves the immediate problem, but it guarantees that the next build cycle will either overwrite your work or inherit your confusion.

Whenever you encounter a defect in generated code, pause before editing the lines:

> **Fix the lowest layer that actually contains the defect, but no lower.**

If the code is wrong, patch the code. If the guideline is wrong, fix the guideline. If the architecture is wrong, update the architecture. And if the business understanding is incomplete, fix the specification.

---

## Related Notes

- **[[Testing in the Model, Agent, LLM Era]]**: Test oracles, behavioral verification, and why test suites must remain immutable during automated repair loops.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Techniques for maintaining living specifications alongside code to prevent context drift.
- **[[Learning Coding Agents Through Failure-Driven Instructions]]**: Turning recurring generation bugs into durable negative rules and automated evaluation benchmarks.
- **[[Negative Knowledge and Explicit Architectural Dissents]]**: Using negative constraints to prevent common model anti-patterns more effectively than prescriptive prompting.
- **[[Developing Features with AI Coding Agents]]**: Deconstructing complex business epics into verifiable technical specifications for autonomous execution.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: The risks of unconstrained code generation and how architectural resets combat technical debt.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Building deterministic execution harnesses that constrain agent repairs to safe boundaries.
- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Why domain modeling and ambiguous edge cases remain the primary bottleneck in autonomous software generation.
- **[[Refactoring Legacy Systems with AI Agents]]**: Applying boundary enforcement and clean-slate regeneration to modernize legacy codebases.
