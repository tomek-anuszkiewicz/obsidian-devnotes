---
title: How Much Guidance Does a Coding Agent Need
tags:
  - ai-agents
  - agentic-coding
  - prompt-engineering
  - context-engineering
  - testing
aliases:
  - Finding a Minimal Effective Coding Prompt
  - Distilling Prompts from Corrective Conversations
  - Testing Prompt Removal Against Repository Examples
  - Replaying Coding Tasks Without Solution Leakage
  - Prompt Simplification as a Repository Matures
---

# How Much Guidance Does a Coding Agent Need

An agent finally produces the right implementation after a long exchange. The engineer has corrected a dependency, clarified a boundary, rejected an unnecessary abstraction, and explained an edge case. The original prompt contains none of those corrections. Starting from the same code with that prompt may produce the same mistakes again.

The useful question is how much of the accumulated guidance must appear in the next prompt. Some decisions need explicit wording. Others may now be obvious from maintained code. Some instructions may have stopped helping, or may cause extra exploration and verification without improving the result.

Treat the prompt as something to test and simplify for a particular model, repository snapshot, and family of tasks. The target is the smallest tested version that preserves acceptable results. A handful of successful runs cannot prove that it is the shortest possible prompt or that it will work equally well elsewhere.

## Keep the task fixed while testing the guidance

Separate the required behavior from advice about how to implement it. "Cancel only pending orders" defines the task. "Use the existing handler structure" guides the implementation. Removing a requirement and then relaxing the evaluator to match would change the problem rather than test whether the agent needed that guidance.

Record what the agent receives beyond the prompt being edited: system instructions, repository instruction files, loaded skills, available documentation, examples, tools, memory, and conversation history. A minimal user message can sit on top of a large amount of other guidance. The claim should be that this message works in that recorded environment.

Within a comparison, keep the model version, effort setting, harness, tool access, resource limits, and initial repository state fixed. Then change the prompt. A later experiment can change the examples or model, but it answers another question. [[Exploring Agent Harnesses]] describes the surrounding components that can affect the same task.

## Compare additions, removals, and references to code

Start with a small prompt containing the task, acceptance requirements, and essential project decisions. Compare it with the current instruction set. Add a clause only when there is a specific failure it might address; also test removing clauses that may have become redundant.

Useful candidate comparisons include:

| Candidate | Question it tests |
| :--- | :--- |
| Task plus minimal project guidance | What can the agent already do with the available code? |
| The same prompt plus one architectural instruction | Does the instruction prevent a named failure? |
| The same prompt plus a reference to selected code | Does an example communicate the needed structure? |
| The current prompt with a clause removed | Is that clause still necessary under these conditions? |
| References to production code instead of separate examples | Can maintained implementations now supply the guidance? |

Changing one clause at a time helps interpret the result, but clauses can interact. Two overlapping rules might each look removable while at least one is needed. Test the final combined prompt again after several removals. Likewise, an example and a short explanation may work together even when neither works well alone.

Record which example files the agent actually reads. A prompt that points to good code may succeed because it fixes discovery, while a longer architectural explanation might leave the agent reading the wrong implementation. [[Bootstrapping Coding Agents with a First Reference Implementation]] develops the separate problem of choosing and maintaining those examples.

## Recover missing guidance from the corrective conversation

Use the successful session as material for an agent that prepares candidate prompts. Give that agent the original request, corrections, accepted decisions, relevant diffs, verification results, and the final implementation. Its job is to explain what the initial prompt lacked.

Have it distinguish three kinds of feedback:

- **Requirements and decisions:** behavior or boundaries that the next implementation must preserve.
- **Repairs specific to an attempt:** instructions to remove a particular helper or fix a particular line after that attempt went wrong.
- **Rejected or superseded proposals:** ideas discussed during exploration that should not become current requirements.

For example, "remove this wrapper" might reflect a durable rule about ownership, or it might apply only to a wrapper that one failed attempt introduced. Copying it into a permanent prohibition would lose the reason for the correction. Ask the analyzing agent to identify the evidence for each proposed instruction and explain what failure it is meant to prevent. An engineer should resolve conflicts between the conversation, intended behavior, and final code.

The output can be a candidate prompt plus a record of why each clause exists. The executor only needs the candidate prompt and the normal permitted context. The record helps later reviewers decide whether a clause still earns its place.

This extends [[Learning Coding Agents Through Failure-Driven Instructions]]: the corrective session becomes evidence for a new prompt, whose effectiveness must still be measured. It does not change the underlying model's weights or make the conversation automatically available to future sessions.

## Give the analyzing agent history and the tested agent a clean start

The agent preparing the prompt needs the history. The agent testing it must not retrieve the old solution through another route. Otherwise a successful replay cannot tell us whether the prompt contained enough guidance.

Prepare an isolated copy of the intended starting tree and dependencies. A checkout of an earlier commit in the original repository is insufficient if the agent can inspect later branches, other references, or neighboring worktrees. An exported tree with no Git database is one option; if Git operations are part of the task, initialize a separate repository containing only the permitted starting state and any explicitly permitted history.

Start a fresh execution session without the old conversation, shared task memory, previous trial files, or access to the analyzing agent's output directory. Preserve allowed production examples because they are part of the experiment. Exclude the implementation being reconstructed and any later artifacts that reveal it. State the boundary explicitly rather than calling the setup "clean" merely because the working directory has no modifications.

Keep the real project and accepted implementation intact. Run resets inside the disposable evaluation copy. If the runner cannot restrict access to old conversations or neighboring repositories, report that limitation: a fresh chat alone is not proof of isolation.

Anthropic's [agent evaluation guide](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) reports trials gaining an advantage by inspecting Git history from earlier trials. It also recommends independent starting environments and repeated trials. These are practical reasons to verify the information boundary before interpreting the score.

## Test both reconstruction and reuse

Replaying the original task asks whether the prompt captures enough of the decisions previously supplied through correction. It is useful even if the prompt describes that task quite specifically. This can produce a reproducible specification for rebuilding the component.

Reusable project guidance has a stronger requirement. It must help with other tasks whose solutions were not used to write the prompt. Keep some representative tasks aside for that check. Include cases where the proposed pattern applies and cases where copying it would be wrong. A rule about storing local state and an outgoing event together should not cause the agent to keep a database transaction open across an unrelated network call.

Use development tasks to propose changes, validation tasks to choose among candidates, and reserved tasks for a final comparison. Repeatedly examining the reserved failures and rewriting the prompt against them turns those tasks into development material. Add new reserved tasks when that happens.

Run each candidate more than once where feasible. Keep failures and resource-limit exits in the results. Report the number of tasks and trials, variation between runs, and uncertainty; a small difference in a small sample may be inconclusive. A single success after many attempts does not establish that the prompt reliably works on the first attempt.

## Define what an acceptable result means before comparing prompts

Use independent checks for the required behavior and review the parts that automated tests do not establish. Preserve the evaluator outside the executor's writable scope, and evaluate the final artifact with that unchanged evaluator. Agent-authored tests can provide additional evidence, but weakening a test must not turn a failed implementation into a measured success.

The acceptance requirements should be available to the agent. Hidden evaluation inputs can test those requirements without exposing the expected implementation. Hidden requirements would make the comparison unfair.

| Measure | Evidence to inspect |
| :--- | :--- |
| Required behavior | Independent tests and relevant runtime outcomes |
| Architecture and scope | State ownership, dependencies, transaction boundaries, unnecessary changes |
| Corrective effort | Human interventions and revisions needed before acceptance |
| Reliability | Outcomes across repeated trials and different tasks |
| Total cost | Model usage, tool execution, retries, elapsed time, and human review |

Keep these dimensions visible. A single combined score can hide a meaningful regression. Decide which quality losses are unacceptable before selecting the cheaper prompt. A model can assist with architectural review under a concrete rubric, but check its judgments against human review rather than letting the same agent declare its own solution successful. [[Tests Are for Verification, Not Architectural Navigation]] explains why behavior tests alone do not settle the architecture.

Compare the full run cost. A shorter prompt may cause more file reads, while a longer prompt may trigger unnecessary checks. The study [Prompt-Induced Waste in Coding Agents](https://arxiv.org/abs/2608.01347v6) reports interactions between prompt wording, inference effort, and harness behavior. Its results motivate measuring cost per successful task under controlled conditions rather than using input token count alone.

## Check whether another instruction can address the failure

When a candidate fails, inspect what happened before expanding it. Did the agent miss a project fact, fail to find the right file, misunderstand a requirement, lack a way to observe the application, or make an implementation error despite having the relevant information?

A difficult task may remain difficult after adding instructions, skills, and examples. The trace can show that the agent saw the intended pattern and still failed to apply it. It cannot establish exactly which patterns were present in the model's training data. Diagnose from observable behavior and test a specific proposed repair.

The September 2026 revision of [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988v3) found no general improvement in task success from repository context files in its evaluated settings, despite agents following instructions; costs increased. A separate [two-agent study](https://arxiv.org/abs/2607.27250) covering 17 tasks likewise found no measurable correctness gain and attributed examined failures primarily to implementation difficulties. These studies bound claims about context files in their settings. They do not prove that local conventions, missing requirements, or carefully chosen examples are unnecessary.

Automatic prompt search can help propose candidates. [GEPA](https://arxiv.org/abs/2507.19457v2) uses execution feedback to propose and evaluate prompt changes. An optimizer still depends on the tasks, feedback, and objective it receives. Its winning prompt needs the same independent check before becoming project guidance.

## Repeat the comparison as the repository and model change

At the start of a component, a prompt may need to explain choices for which the code offers no example. After several implementations have been reviewed, an explicit file reference may communicate much of the same information. Test that shorter prompt at the later repository snapshot, keeping the snapshot fixed across its candidate runs.

This does not require preserving the first successful prompt as a permanent rule. Its wording may encode temporary limitations or details that the code now expresses better. It also does not require deleting every separate example: some examples explain rare cases more clearly than production code can.

When changing models, compare the current prompt with simpler candidates again. Improved general coding ability is a reason to try the experiment, not evidence that every project-specific instruction is redundant. Keep the task contract and required enforcement intact while testing how much explanatory guidance the new model needs.

Version the selected prompt together with the repository revision, model and harness settings, permitted context, evaluation tasks, and results. Save the previous accepted version so a later regression can be investigated. The result is a prompt supported by evidence for a known environment, which can be revisited when that environment changes.

## Related notes

- **[[Constraint Saturation and Rule Oscillation in Coding Agents]]** — Why accumulated instructions can interfere with one another and how to test their removal.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]** — Recording accepted decisions before they disappear into an old conversation.
- **[[Configuring and Testing Coding Agent Capabilities]]** — Testing the tools, skills, and audit triggers held fixed during a prompt comparison.
- **[[How Context Narrows an AI's Solution Space]]** — How code and other context affect the choices available to the model.
