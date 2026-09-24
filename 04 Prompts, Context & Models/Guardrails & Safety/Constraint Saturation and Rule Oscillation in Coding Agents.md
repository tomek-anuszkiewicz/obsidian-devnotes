---
title: Constraint Saturation and Rule Oscillation in Coding Agents
tags:
  - ai-agents
  - software-engineering
  - prompt-engineering
  - code-review
  - system-design
  - agentic-harness
  - bounded-rationality
aliases:
  - Rule Thrashing in Agentic Coding
  - The Over-Constrained Agent
  - Constraint Oscillation Trap
  - Whack-a-Mole Rule Thrashing
---

# When Coding Agents Get Stuck Between Too Many Rules

> [!IMPORTANT] Adding another instruction can make the next edit worse
> A few clear rules help an agent avoid basic mistakes. Keep adding rules for every edge case, though, and the agent has to juggle more requirements while working on each change. It may fix one violation, introduce another, and then undo its first fix. Give the rules a clear order of priority, load the ones relevant to the task, split the work into passes, and let compilers, formatters, and linters check what they can check reliably.

This note calls that back-and-forth **rule oscillation**. Imagine an agent follows each of 30 rules with an independent probability of 95%. In that simplified example, the chance of following all 30 is only about 21%:

$$P(\text{following all } M \text{ rules}) = \prod_{i=1}^{M} p_i \approx p^M$$

The calculation illustrates how small per-rule failure rates add up. It depends on the independence assumption; it is not a measured failure rate for a particular agent.

## How another rule turns into another failure

When a team builds an [[Agentic Coding Harness and Controlled Development Workflows|agentic coding harness]], a natural response to an agent mistake is to add a rule to the repository instructions. Over a few sprints, those instructions can grow into a collection of system prompts, [[Learning Coding Agents Through Failure-Driven Instructions|files written after earlier failures]], large `SKILL.md` definitions, static analysis checklists, architectural requirements, and policies for review by multiple agents.

Some requirements are quite specific: no heap allocations on a hot path, immutable data structures, one class per file, or a strict 300-line limit. Each may have a reason behind it. The trouble starts when the agent must satisfy all of them during one edit. Adding a few rules initially improves the result; after a point, more instructions can make the agent less reliable. That is the failure mode described here and in [[LLM Coding Agents — Reliability, Uncertainty, and Subtle Errors|coding agent reliability]].

Here is what the loop looks like in code:

1. The agent inlines a routine to remove an allocation from a hot path. This satisfies **Rule A**.
2. A test or linter reports that the file now exceeds a 400-line limit, or that its responsibilities should be split. This is **Rule B**.
3. The agent splits the code, then crosses a package boundary through an internal import. It has violated **Rule C**.
4. It moves code again to respect that boundary and brings back the allocation that Rule A prohibited.
5. The next retry starts the same sequence. Each pass uses more tokens and context while the code keeps changing without converging. Repeated patches can also contribute to the instability discussed in [[Software Decay and the Hidden Costs of Frictionless AI Code]] and obscure the architectural trade-offs behind [[AI May Make Aggressive Code Optimization Economically Viable|aggressive optimization]].

The requirements need not be logically impossible. Given enough time, an engineer could often design a solution that satisfies them all. The agent's problem is keeping every requirement in view while making local changes and responding to the latest failure.

## Why the agent loses track

An agent has limited context and does not keep a separate, dependable engineering notebook of every earlier decision. A difficult local problem can dominate the work in front of it. While it works through pointer arithmetic, concurrent state changes, a relational query, cache alignment, a zero-copy buffer, or a precise lifetime, a distant architectural instruction may receive less effective attention.

Feedback can make the problem worse. If the most recent message says, “The file is too long,” the next edit may focus on splitting the file. The agent may then overlook why it had inlined the code two turns earlier. It optimizes the current fix while losing sight of the earlier constraint. The loop can continue even when the original set of rules is consistent.

The simple probability example puts numbers on another part of the problem. If following each rule had an independent 95% chance, then following *all* $M$ rules would have a probability of $0.95^M$:

| Rules to follow | Chance per rule | Chance of following all rules in this example |
| :--- | :--- | :--- |
| 5 | 95% | About 77.4% |
| 15 | 95% | About 46.3% |
| 25 | 95% | About 27.7% |
| 30 | 95% | About 21.5% |

These figures are an illustration, not a prediction: real rules are neither equally difficult nor independent. They do show why success on each individual requirement would not guarantee success on the entire list. Appending another instruction after every mistake does not, by itself, solve the compound problem.

## Where the back-and-forth shows up in a codebase

The same pattern appears in several familiar design choices:

| Rules in tension | What the agent keeps changing |
| :--- | :--- |
| Object-oriented wrappers and a zero-allocation, low-latency path | It adds wrapper classes for a cleaner structure, then removes them from the hot loop to avoid allocations. |
| Limits on file length or file count and small, single-purpose modules | It puts several classes into one file to reduce the file count, then splits them when the file exceeds a line limit. |
| DRY and isolation between modules | It moves repeated logic into a shared utility package, then duplicates the logic again to avoid coupling across module boundaries. |
| Immutability and throughput in a state machine | It replaces mutable buffers with immutable records, sees warnings about garbage collection or memory churn, and switches back. |

In each case, a local correction can reverse an earlier decision. The agent needs to know which rule matters more in that part of the system and when the two goals require a deliberate design choice.

## Put the rules in an order the agent can use

A flat checklist makes every instruction look equally urgent. Give the agent an explicit order of priority:

1. **Technical correctness:** the code compiles, passes tests and type checks, and respects memory safety.
2. **Domain and security boundaries:** data integrity, transaction scopes, authorization checks, and preventing data loss.
3. **Operational and performance limits:** latency targets, allocation limits, query count caps, and hot-path performance.
4. **Style and organization:** names, line limits, file structure, and comment formatting.

If a style rule conflicts with correctness or a security boundary, the agent should keep the higher-priority requirement. State that directly in the harness instructions. The order does not make performance or style irrelevant; it tells the agent what to preserve when a quick fix would trade away something more important.

## Load rules when they apply

Do not put the whole engineering handbook into every task. Select rules based on the files the agent is changing:

- Load hot-path memory rules for modules under `src/core/engine/**` or files marked `@performance-critical`.
- Load API validation and payload rules when the agent changes controllers, routes, or schemas.
- Start an ordinary feature task with a small set of three to five core architectural guidelines.

This leaves room for the local constraints the task actually needs, without asking the agent to carry unrelated rules throughout the run.

## Work through the objectives in passes

Asking for complete business logic, optimized memory use, documentation, formatting, and static verification in one generation gives the agent several competing targets at once. Run the work in stages instead:

1. **Make it work:** implement the business logic and get the unit tests passing. Leave line limits, formatting, and small optimizations for later.
2. **Refine the working code:** profile the relevant paths, reduce allocations, and check the performance budget.
3. **Run the tools:** format the code, sort imports, and apply deterministic linter fixes. Prettier or Ruff can handle the formatting where they fit the project.

Each pass has a clear immediate objective. The agent still needs to preserve the higher-priority constraints established earlier; the stages prevent it from trying to optimize every dimension during the same edit.

## Stop retries that return to the same code

The harness can watch file diffs or AST changes across retries. If file `F` alternates between two shapes, or the diff at iteration $N+2$ reverses the change from iteration $N$, stop the loop. Compare diff hashes if that is sufficient to detect the repeated changes.

Report the rules involved, for example: “The agent is alternating between the 300-line limit and the zero-allocation rule. The retry loop has stopped and needs an engineer to decide how to satisfy both.” This gives a reviewer a concrete conflict to resolve instead of another superficial patch. [[Reviewing AI-Generated Code]] covers that kind of back-and-forth in review.

## Let deterministic tools check mechanical rules

An agent does not need to remember import ordering or a maximum line length if a formatter or linter can check it. The same applies to rules a compiler flag, an AST script, or an architecture test such as ArchUnit can enforce. Remove those checks from the prompt and run the tools as part of the workflow.

Use natural-language instructions for domain decisions and architectural trade-offs that those tools cannot evaluate. This reduces the number of mechanical details the agent must hold in context while it works on the design.

## Practical rules of thumb

1. **Treat every new prompt rule as a cost.** A few rules can prevent common mistakes; a growing list can increase the chance that one of them gets lost or causes another retry.
2. **Look for loss of context before declaring the rules contradictory.** The agent may simply be focusing on the latest failure and overlooking an earlier decision.
3. **Set priorities explicitly.** Correctness and domain or security boundaries take precedence over formatting and file-length preferences.
4. **Separate the work into passes.** Get correct code first, refine performance, and let tools handle formatting and other mechanical checks.
5. **Detect repeated diffs and stop.** If the agent moves between the same two implementations, show the conflict to an engineer instead of spending more retries on it.

## Related notes

- **[[Agentic Coding Harness and Controlled Development Workflows]]** — execution loops, retry limits, and escalation when the agent cannot converge.
- **[[Learning Coding Agents Through Failure-Driven Instructions]]** — the risk of adding a rule to `AGENTS.md` for every edge-case failure.
- **[[Reviewing AI-Generated Code]]** — recognizing superficial fixes that undo one another during review.
- **[[How Context Narrows an AI's Solution Space]]** — when constraints help narrow the search and when too many make the work harder.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]** — using deterministic checks without filling the prompt with mechanical instructions.
- **[[LLM Coding Agents — Reliability, Uncertainty, and Subtle Errors]]** — how per-rule failure can accumulate when an agent handles many rules at once.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]** — replacing long generic rule lists with concise guidance for the task at hand.
- **[[AI May Make Aggressive Code Optimization Economically Viable]]** — Navigating the tension between zero-allocation hot paths and modular code aesthetics.
