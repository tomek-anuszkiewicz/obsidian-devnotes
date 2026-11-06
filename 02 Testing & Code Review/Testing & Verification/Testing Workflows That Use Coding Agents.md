---
title: Testing Workflows That Use Coding Agents
tags:
  - testing
  - ai-agents
  - agentic-workflows
  - code-review
  - verification
aliases:
  - Regression Testing for Agent Workflows
  - Evaluating Agent Review and Repair Loops
  - Testing Coordinators with Scripted Agent Responses
---

# Testing Workflows That Use Coding Agents

A coding agent fixes an order cancellation bug. CI passes, but the patch also weakens the test that protects paid orders from cancellation. The reviewer flags the change. The coding agent pushes a new commit, and a successful CI result arrives for the previous one. What should the coordinator do next?

That pull request gives us three tests. Can the reviewer identify the weakened assertion? Does the coordinator wait for checks on the new commit? Does the patch that eventually reaches merge still prevent paid orders from being cancelled?

## Start Each Run from the Same State

Keep a small repository at a known commit, the task description, the acceptance checks, and any inputs the workflow needs. For the cancellation case, include a pending order that should be cancellable and a paid order that should remain intact. Keep these checks outside the patch the coding agent can change. A green run of the repository's own suite can hide a weakened assertion. [[Trustworthy Test Oracles for Coding Agents]] explains how to protect accepted expectations during a repair.

For a skill comparison, give each version a clean copy of the repository and a fresh session. Keep the model, other instructions, and available tools fixed. For the coordinator, also restore the open pull request, its current commit, saved workflow state, and the sequence of incoming events. Use isolated copies of anything the workflow can write to.

## Evaluate the Agent's Decisions and Their Effects

Give the reviewer two similar pull requests. One weakens an assertion to make CI pass. The other changes an assertion to match a documented and approved requirement change. Grade whether the reviewer flags the first patch with evidence and accepts the second on that point. For the coding agent, run the protected behavioral checks against the resulting patch. If a skill is supposed to load automatically, include a task where the user never names it. [[Configuring and Testing Coding Agent Capabilities]] covers how rules and skills are made available to the agent.

A trace records observable steps such as tool calls, arguments, and results. An eval uses criteria to score a run, its resulting artifacts, or both. Record the actions that matter to the contract and allow different valid ways to reach the result. Repeat the same scenarios with the live model and compare how often each version misses a defect or blocks a valid change. Anthropic describes this approach, OpenAI shows how to capture Codex events with `codex exec --json`, and Google's Agent Development Kit can grade tool use and task outcomes. [Anthropic agent evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) · [Codex skill evals](https://developers.openai.com/blog/eval-skills) · [Google agent evaluation](https://adk.dev/evaluate/)

## Script Agent Responses to Test the Coordinator

Feed the coordinator a review finding, a repair, or a disagreement with supporting evidence. Deliver a duplicate review event or a late CI success for the previous commit. Assert that the duplicate starts no second repair, that the current commit still waits for its checks, and that the merge API is never called with stale approval. Try the relevant event orders, including delivery after a restart. Test the adapter separately against the real interface so scripted responses reflect how it reports refusals, incomplete results, and transport failures.

When a dispute requires a change to the business contract, the coordinator sends the person making that decision the current diff, the evidence from both sides, and the question to resolve. In a coordinator test, supply the decision as an event. Check that approval applies to the reviewed change and that a later commit which changes the approved behavior requires a new decision. [[Closing the Loop Between Coding Agents and Code Review]] describes how to carry evidence through repair and escalation.

## Compare Old and New at the Merge Boundary

A workflow port can run both implementations against the same starting state, events, and scripted agent responses. Compare which commit each version makes eligible to merge, what each writes to external systems, and when each asks for a human decision. Apply the same acceptance checks to both. Agreement with the old implementation can preserve a bug, and a passing comparison covers the exercised cases. [[Large-Scale Code Migration with AI Agents]] develops this use of differential execution.

Run a small end-to-end case with the actual agent as well. If the reviewer correctly flags the weakened assertion but the bad patch still becomes eligible for merge, the reviewer eval can pass while the workflow test fails. The shared scenario gives you the evidence to check whether the repair preserved the rule and whether the coordinator verified the commit it was about to merge.
