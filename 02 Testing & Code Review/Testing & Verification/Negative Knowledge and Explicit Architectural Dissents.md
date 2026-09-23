---
title: Negative Knowledge and Explicit Architectural Dissents
tags:
  - negative-knowledge
  - architectural-dissent
  - software-architecture
  - ai-agents
  - technical-debt
  - code-maintainability
  - gitclear
aliases:
  - The Dissent Firewall
  - Explicit Architectural Dissents
  - Negative Knowledge in Software Engineering
  - The Ephemeral Code Fallacy
  - Bounding by Exclusion vs Prescriptive Micromanagement
  - Negative Bounding
---

# Negative Knowledge and Explicit Architectural Dissents

A production system is shaped by the designs a team rejected as well as the code it runs today. Teams remember the connection pool that leaked sockets under load, the abstraction that added indirection without isolating anything, and the consensus design that split into conflicting states during a network partition. Those lessons are easy to lose if they stay in people's heads.

**Negative knowledge** is a written record of designs the team evaluated, tested or measured, then deliberately rejected. It explains what failed and under which conditions.

This matters when coding agents work in the repository. An agent can reach for a familiar framework, add an abstraction that seems useful, or apply a textbook pattern without knowing that the team already tried and rejected it. The result is another pull request that asks everyone to revisit the same incident and the same decision. Recording the rejection, with its reason, gives engineers and agents a way to avoid repeating that work.

---

## The main decisions

- **Record rejected designs alongside accepted ones.** Documentation of what runs today does not explain why a plausible alternative was ruled out. A rejection record keeps that history available to people and agents.
- **Tell agents which familiar patterns failed here.** Models tend to suggest common patterns, including unnecessary microservices, deep inheritance trees and extra caching layers. An explicit restriction can stop an agent from bringing one of them back into this codebase.
- **Set a few firm boundaries, then leave room to implement.** A prompt that dictates every class and method consumes context and can create conflicting rules. Two or three restrictions tied to serious failure modes let the agent solve the task without crossing known boundaries.
- **Keep code maintainable rather than treating it as disposable output.** A natural-language prompt cannot serve as the full specification for a production system. Continually replacing code makes it harder for a team to understand the system and debug it during an incident.
- **Keep rejection records in the repository.** An Architectural Dissent Record (ADR-) complements a conventional Architecture Decision Record (ADR) by explaining a rejected option, the evidence behind the rejection and the conditions for reconsidering it.

For example, a knowledge base might say only that the system uses Service X, Database Y and Event Bus Z. It leaves an agent free to propose Framework W again, even though the team rejected it. A more useful record distinguishes the designs currently accepted, the designs rejected with evidence, and the options that remain open for architectural review.

---

## 1. What negative knowledge records

**Positive knowledge** describes what works now: libraries, deployment layout, API contracts and domain models used to serve traffic. It changes when requirements, dependencies or platforms change.

**Negative knowledge** describes what failed and why. Perhaps a distributed lock deadlocked during packet loss, or a local cache returned stale data after a database failover. That finding remains relevant while the conditions that caused the failure remain in place. If those conditions change, the team can revisit the decision.

When only senior engineers know this history, the team loses it as people leave. An agent has even less context: it cannot remember last quarter's sev-1 incident unless that information is available to it. Ask one to speed up customer record lookups and it might add an in-memory LRU cache. The platform team may have spent three weeks removing exactly that cache because autoscaling worker pods returned stale records.

Write down the rejection and its cause. Then an agent working on the lookup path can see why the seemingly quick optimization is out of bounds.

---

## 2. Give agents boundaries without scripting every step

Positive guidance alone leaves important choices unspecified. “Implement this user service using our standard repository pattern” does not tell an agent that it must avoid a new ORM dependency, queries inside an unbounded loop, or bypassing authentication middleware to simplify tests. While trying to finish the task, it may also add a duplicate validation helper or swallow an error just to get the tests green.

One response is to specify every class name, method signature and implementation step. That creates three problems:

1. **The prompt grows around routine code.** It spends hundreds of tokens explaining work the model can already do.
2. **Important rules compete with minor ones.** Faced with many detailed instructions, the agent can follow a formatting rule while missing business logic or another critical constraint.
3. **The agent has less room to handle cases the prompt did not anticipate.** A prescribed sequence can block a simpler control flow or an appropriate response to a domain edge case.

A more useful approach is **bounding by exclusion**: state the task and explicitly forbid the known ways to break the system, while leaving the internal implementation open.

```text
Prescribing the implementation:
“Create IUserRepository. Add GetById to UserRepository. Use DTO mapping
library X. Inject Logger Y through the constructor...”

Setting boundaries:
“Implement user lookup and role verification so the test suite passes.
Choose the internal design, subject to these restrictions:
1. Do not add third-party dependencies.
2. Do not run database queries inside a loop; fetch the data in batches.
3. Do not swallow exceptions or log sensitive credential fields.”
```

The restrictions target specific failure modes. The agent can still decide how to structure the lookup and verification code.

---

## 3. Why production code is not disposable

One proposed workflow treats a Markdown specification as the lasting artifact: an agent regenerates the code when requirements change, and tests validate the new version. Under this approach, maintaining and refactoring the existing implementation become less important.

That idea runs into two problems in production.

### Natural language does not specify every behavior precisely

The promise resembles earlier CASE and 4GL claims: describe the system at a higher level and generate the implementation. But a short natural-language specification leaves room for different interpretations. To generate production code safely, it would need to spell out details such as:

- concurrency boundaries and database isolation levels, including Read Committed versus Serializable;
- socket timeouts, connection pool sizes, retry backoff and jitter;
- idempotency key validation, message deduplication and recovery from partial failures.

At that level of detail, the Markdown file starts acting like a programming language, but it has no types, compiler or comparable feedback to catch mistakes in what it describes.

### Tests only check what somebody thought to test

Green unit tests show that the implementation passed the assertions and cases in the suite. They do not, by themselves, reveal an unclosed transaction that starves the connection pool, a garbage collection pause that hurts tail latency, a thread or goroutine leak under socket contention, or a distributed deadlock that appears only at production I/O queue depths.

If a team repeatedly replaces code and relies only on local unit tests to approve it, those operational regressions can reach production.

---

## 4. The 3:00 AM maintenance problem

Code also carries the team's working understanding of the system. Consider a payment settlement service that different agents regenerate five times over three months to accommodate small API changes. On Sunday at 3:00 AM, a connection leak exhausts the worker's thread pool and batch processing deadlocks. The on-call engineer opens the repository and finds 10,000 unfamiliar lines merged two days earlier. They cannot readily trace how the service behaves under load or predict the effects of a hotfix.

During an incident, someone must understand the execution path, thread boundaries and invariants well enough to make a safe change. Continually replacing the implementation erodes that shared understanding.

---

## 5. A local benchmark can hide a production failure

Suppose an agent optimizes a routing service by replacing a database lookup with a static in-memory hash map. A single-threaded benchmark reports a 50× throughput improvement. The pull request looks compelling until the change runs across a cluster:

1. **Instances disagree about state.** In a pool of twenty autoscaling instances, instance A updates a record while B through T keep serving stale data. Subsequent writes can become inconsistent.
2. **An unbounded cache adds garbage collection pressure.** As it grows under real traffic, stop-the-world pauses can push p99 latency beyond its target.
3. **New workers take longer to become ready.** Pods spend minutes warming their local caches, slowing the response to a traffic spike.

An agent looking only at one file and a local test runner will not see those cluster-level effects. A rejection record can state the rule and the reason: *Do not add local in-memory caches to stateful worker nodes; keep state in the shared storage layer.* That gives the agent the context it needs before making the local optimization.

---

## 6. Keep rejected decisions next to the code

Put **Architectural Dissent Records (ADR-)** in the source tree alongside ordinary architecture records. Each one should say what was proposed, why the team rejected it, what evidence supports the decision and what would have to change before revisiting it.

### Example ADR-

```markdown
# ADR-014: Rejection of In-Memory State Caching in Transaction Workers

## Status
REJECTED (Active Constraint)

## Proposed Pattern
Store recent transaction status in a local memory cache inside worker nodes
to avoid repeated database lookups during batch processing.

## Why It Was Rejected
1. Cluster Consistency: Workers run in an autoscaling group. Local caches
   return conflicting status values when tasks move between nodes.
2. Memory Footprint: Peak transaction batches pushed workers past their
   container memory limits and caused out-of-memory restarts.
3. Operational Debuggability: Stale local state concealed the current
   database state during incident investigation.

## Empirical Evidence
- Incident Post-Mortem #204 (October 2025): A node failover during batch
  processing led to duplicate settlement events because of stale caches.

## Reconsideration Criteria
Revisit this decision only if BOTH conditions hold:
- Workers move to dedicated single-instance partitions with guaranteed
  sticky routing.
- CI includes an automated cache coherency test harness.
```

When a new engineer or an agent proposes the cache again, the record shows why it was ruled out. It also tells the team exactly what must change before the proposal is worth reopening.

---

## Related Notes

- **[[Testing in the Model, Agent, LLM Era]]**: The Frozen Oracle Rule and the limits of using automated tests in place of architectural understanding.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Harnesses that enforce constraints and boundary rules during agent development loops.
- **[[Constraint Saturation and Rule Oscillation in Coding Agents]]**: How too many prompt rules compete, and how negative boundaries address that problem.
- **[[How Context Narrows an AI's Solution Space]]**: How explicit structural constraints narrow the designs an agent will consider.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]**: How easy code generation can add maintenance debt when boundaries are missing.
- **[[How AI Changes Prototyping and the Path from PoC to Production]]**: The difference between disposable experiments and production code that a team must maintain.
- **[[AI Changes the Economics of Technical Debt]]**: How generated code affects maintenance and structural refactoring costs.
- **[[Designing Software for AI Agents]]**: Explicit module boundaries that help agents understand system intent.
