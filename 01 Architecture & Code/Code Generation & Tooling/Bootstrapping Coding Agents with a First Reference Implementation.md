---
title: Bootstrapping Coding Agents with a First Reference Implementation
tags:
  - ai-agents
  - agentic-coding
  - software-architecture
  - code-generation
  - context-engineering
aliases:
  - Building the First Good Example for a Coding Agent
  - From Temporary Examples to Production Code
  - Choosing Reference Implementations for Agents
  - Delaying Canonical Patterns Until They Are Tested
---

# Bootstrapping Coding Agents with a First Reference Implementation

The first implementation can take a long conversation with a coding agent. You correct where validation belongs, how the operation changes state, and what should happen when a dependency fails. Later, a similar feature takes a short request because the agent can inspect the implementation you already worked through.

That suggests a useful way to start a project: use a small prompt, build a few examples, and eventually point the agent at real code. Whether that is enough needs checking. The first implementation may contain workarounds, decisions that apply only to that operation, or mistakes that its tests do not catch. Treat it as a candidate example while further work reveals which parts are worth repeating.

## The first example contains decisions the prompt may never have stated

Consider an illustrative order cancellation feature. The original request says to add a cancellation endpoint. During review, the engineer adds several corrections:

- The HTTP endpoint calls an application handler; it does not update the order directly.
- The handler checks the allowed state transition.
- The state change and an outgoing event are stored in the same database transaction.
- A repeated request must not produce a second cancellation event.

The resulting implementation may be good, but the original prompt still says only to add an endpoint. The successful session had more guidance than that prompt: it included every correction, code inspection, and test result along the way. Repeating the original request in an empty component does not reproduce those inputs.

Some of the corrections describe general project conventions. Others describe cancellation behavior. Some may have been temporary repairs to an abandoned attempt. Record the accepted decisions while their reasons are still available, and distinguish them from the sequence of edits that happened to reach the result. [[In-Flight Documentation as the Primary Framework for Coding Agents]] explains how to keep this record current during implementation.

An agent can help recover those decisions from the conversation and final diff. The proposed record still needs review: the latest code is evidence of what was implemented, while the engineer's accepted requirements establish what was intended.

## Let further implementations test the proposed pattern

Build another operation that seems to need the same structure. Then try a case that differs in a meaningful way. A local order state change and a refund involving a remote provider may share the transport and handler boundaries, but they cannot necessarily share the same transaction design. Copying the first handler mechanically could leave a database transaction open while waiting for a network call.

This is where a provisional example becomes useful. Review which parts the agent reused correctly, which parts needed correction, and which details should remain specific to the operation. There is no fixed number of implementations after which a pattern becomes reliable. Several near-identical examples may reveal less than one ordinary case and one case that exposes a limit.

Passing behavior tests is part of that review. Also inspect ownership of state, dependency direction, transaction scope, and failure handling. A test that observes a cancelled order may pass even if the agent put persistence code in the endpoint. The distinction is developed in [[Tests Are for Verification, Not Architectural Navigation]].

Once the examples support a common design, identify the implementation that expresses it most clearly. A working file with layers of previous attempts is a poor teaching example when a simpler current implementation exists. Preserve the reason for the pattern, including the conditions under which it does not apply.

## Use a small prompt and a deliberate set of examples

A short prompt plus selected code is a reasonable starting configuration to test. The prompt should state the task and decisions the agent cannot safely infer. The examples can show naming, file placement, dependency use, and the ordinary flow of an operation.

For example, a hypothetical repository might use this guidance alongside the new feature's requirements:

```text
Use src/orders/cancel_order.py as the reference for the endpoint-to-handler
boundary and recording an outgoing event with a local state change.
Its cancellation transition rules are specific to that operation.
```

The scope matters. "Copy this implementation" could transfer behavior that is wrong for the new operation. Naming what the example demonstrates gives the agent a basis for deciding which parts to reuse.

The prompt does not have to describe every line of the reference file. It may still need to explain a deliberate exception, why an old implementation should be avoided, or which invariant must survive a change. A newer model may understand familiar programming techniques with less explanation; it cannot be assumed to know an unpublished project decision.

Anthropic's [context engineering guidance](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) recommends starting with minimal sufficient guidance and selecting diverse examples instead of listing every edge case. This is a practical starting point, not a measured guarantee that a small prompt will work for a particular repository. Compare it with alternatives using [[How Much Guidance Does a Coding Agent Need]].

## Move the examples into maintained code when the evidence supports it

A separate example directory can help while production code is incomplete or inconsistent. Later it creates another copy to maintain. The example may keep using an old API after production code changes, leaving the agent with two apparently valid conventions.

Before retiring that directory, compare two prompt variants against the same repository snapshot: one that uses the separate examples and one that points to selected production implementations. Keep the task requirements and evaluation criteria unchanged. Check ordinary cases and exceptions, and review whether the agent actually read the intended files.

If the production references provide equally useful guidance on those tasks, the separate examples may no longer justify their maintenance cost. Retain material that still serves a distinct purpose, such as a rare failure case absent from production code or a small teaching example that makes a complicated contract understandable. Removal follows the comparison; it is not an automatic stage every project must reach.

The codebase can then carry much of the guidance previously written into the prompt. This is one concrete consequence of the argument in [[Software Engineering May Shift Toward Code Optimized for Agents]]: consistent, explicit code gives later agents something useful to extend.

## Verify that the agent can find and recognize the right example

Having a good implementation somewhere in the repository is different from putting it in the agent's working context. Compare an explicit file reference with a more general instruction to follow existing conventions. If only the explicit reference works, retain that pointer or improve how the reference is discovered.

Inspect the file reads when a trial fails. Did the agent miss the example, read an obsolete implementation, or read the right code and still make the wrong change? Those observations suggest different repairs. More prose about the architecture will not necessarily fix all three.

[Agent Retrieval Bench](https://arxiv.org/abs/2607.24882) studies file selection separately from patch generation and reports that different retrieval methods perform best on different measures and tasks. Its results support testing discovery as a separate step; they do not establish a best retrieval method for every project.

Reference code also needs continued review. OpenAI's [harness engineering account](https://openai.com/index/harness-engineering/) describes agents reproducing uneven patterns already present in the repository, followed by work to detect and clean up those patterns. When an example becomes obsolete, update its pointers and explain its replacement. Otherwise a short prompt can keep directing agents toward a design the team has abandoned.

## Revisit the prompt after the code has matured

Keep the initial prompt provisional too. After several implementations and reviews, try removing guidance that the maintained examples now express clearly. Preserve requirements whose intent is not visible in code, and measure whether the shorter version increases corrections or produces unwanted variations.

For this comparison, hold the repository snapshot fixed while changing the prompt. A shorter prompt on a later, richer codebase may work well, but that observation alone does not show that shortening caused an improvement. It shows that the new combination is a candidate for future work.

The useful milestone is a new task that an agent completes from the available prompt and code without needing the same corrective conversation again. Repeat that check as the examples, model, and project conventions change. [[How Much Guidance Does a Coding Agent Need]] covers how to recover candidate prompts from past conversations and test them without exposing the previous solution.

## Related notes

- **[[Learning Coding Agents Through Failure-Driven Instructions]]** — Turning recurring corrections into candidate guidance and comparing it on other tasks.
- **[[Negative Knowledge and Explicit Architectural Dissents]]** — Preserving why an attractive alternative was rejected when that reason is not visible in the final implementation.
