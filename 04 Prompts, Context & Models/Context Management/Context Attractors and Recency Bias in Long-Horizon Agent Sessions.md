---
title: Context Attractors and Recency Bias in Long-Horizon Agent Sessions
tags:
  - llm
  - context-window
  - cognitive-bias
  - self-attention
  - agent-dialogue
  - prompt-engineering
  - model-cognition
aliases:
  - Context Attractors in LLMs
  - Attention Gravity Trap
  - Recency Echo Chamber in Agent Sessions
  - Hyper-Fixation in Long Contexts
---

# When an Agent Keeps Returning to the Same Idea

Long conversations can give an agent useful context. They can also make one repeatedly discussed idea far too influential. You spend several turns on instruction cache behavior, then ask about hiring, an API, or service monitoring. The agent still finds a way to bring the cache into its answer. I call that recurring idea a **context attractor**.

The output may sound thoughtful. That is part of the problem: a capable model can build a persuasive explanation around a connection that the current question does not warrant. Conversation compaction can carry the same fixation forward if its summary preserves the dominant topic and drops the objections and limits discussed along the way.

My practical response is to work in short, focused sessions, record decisions in Markdown, and start a fresh session from that record. If I control the agent harness and need to shorten the conversation, I would also consider dropping old turns while retaining the active instructions and files, instead of repeatedly summarizing the whole exchange.

## Why a longer conversation can start giving worse answers

A long architecture discussion seems to build shared understanding. You establish vocabulary, revisit deployment constraints, and refine decisions together. The agent appears to remember the trade-offs from earlier turns. That context is valuable when a problem spans several components.

But repeated discussion can give one topic a disproportionate place in the conversation. After dozens of turns, the agent may treat that topic as the likely explanation for the next issue, even when the issue has changed. Its own previous answers repeat and reinforce the theme. What looks like accumulated insight can become a habit of reaching for the same explanation.

Consider a session that has spent many turns on L1 instruction cache thrashing, the Ship of Theseus problem, or formal verification oracles. Those subjects are legitimate in their own discussions. The warning sign comes when a later question about a message broker, hiring, or a different part of the system receives an answer organized around one of them.

### What the model is doing with the conversation

A transformer works over the tokens available in its active context. Self-attention relates the current tokens to earlier tokens; its standard form is:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

During inference, the KV cache holds representations of earlier tokens so the model can reuse them. A repeated discussion leaves many references to the same idea in the active history. This makes it easier for the model to draw on that idea again when forming an answer. The formula alone does not prove that the most repeated concept will win every time; the engineering observation is that repetition can skew the answer toward a familiar theme.

Imagine a conversation with 4,200 tokens discussing L1 instruction cache behavior and 180 discussing network topology. Those numbers are illustrative. If the next question is about network topology, I want the answer to follow that question. If it returns to L1i thrashing, the earlier discussion is crowding out the current task.

### The failure looks plausible

This drift rarely produces broken prose. It produces answers with a clean argument for the wrong priority:

| Current task | Answer pulled toward the old topic |
| --- | --- |
| Design an engineering interview process | Screen candidates for CPU cache line invalidation profiling. |
| Review maintainability problems in a web API | Diagnose microarchitectural stalls while overlooking poor boundaries. |
| Build an observability dashboard | Prioritize hardware counters over business metrics and service objectives. |

A reviewer may initially read these answers as creative connections. The useful check is simpler: does this topic actually explain the problem in front of us, or did the agent bring it along from the previous discussion?

## How compaction can preserve the fixation

When a conversation grows too large, an agent harness may summarize earlier turns and continue from that summary. This frees context space, but it also changes what the next model call receives.

A summary of a 150-turn discussion may give the most frequently repeated idea a prominent place. If the summarizer states it as a settled principle, the next session of reasoning inherits a stronger claim than the conversation actually established. Qualifications, counterexamples, and disagreements can disappear in the compression.

The sequence is easy to recognize:

1. A subject appears often, so the summary treats it as central.
2. The harness puts that summary back into the agent's working context, possibly among high-priority instructions.
3. The original debate is no longer visible. The agent sees the conclusion without the reasons to question it.

Repeated compaction can repeat this process. A tentative idea from the first conversation may return as an unquestioned assumption. That is the trap: the summary helps the agent remember something, but may change *how certain* it seems and *where it applies*.

## The trade-off: enough context, without letting one topic take over

Very short, disconnected prompts are awkward for architecture work. The agent needs system boundaries, deployment constraints, and data flows to discuss cross-system consequences. Otherwise, you keep repeating the same information and it can miss a constraint established earlier.

An indefinitely growing thread has the opposite problem. Recent or heavily repeated ideas can dominate later answers, while compaction may strip away the nuance that kept those ideas in check. The goal is to carry forward decisions and relevant constraints without carrying forward every turn of the debate.

## A way to work with long-running engineering tasks

### Keep each conversation focused

For an architecture decision, interface, or bug, try a session of roughly **5 to 15 turns**. Treat 15 as a working limit, not a property of the model. Use those turns to explore the options and challenge the agent's reasoning.

At the end, have the agent write the concrete decisions and useful findings into a standalone Markdown document. Commit the document to Git, close the chat, and start a fresh conversation with that file as context. This keeps the decisions available while clearing the live conversation history. The next session can inspect the written reasoning instead of inheriting every repeated phrase from the discussion.

### If you control the harness, consider dropping old turns

When the context limit forces the harness to shorten a session, one option is a FIFO sliding window: remove enough of the oldest raw turns to make room while keeping the base instructions, active files, current decisions, and instructions relevant to the task.

This removes old repetitions directly. A recursive summary may preserve them and give them more authority. FIFO pruning also loses older details, so the decisions you need later belong in the committed Markdown document. The amount to prune and the choice between pruning and summarizing are harness settings to evaluate on the actual task.

### Redirect the agent when it fixates

You can also intervene during the current session. State the task and exclude the irrelevant theme explicitly. For example:

> We are designing the operational health check for the ingress proxy. Do not use L1 cache invalidation, mechanical sympathy, or zero-cost abstractions to explain it. Evaluate Linux network socket states and TCP connection backlogs.

This makes the relevant scope clear. It is a useful immediate correction when the agent keeps returning to the old subject, although a fresh session and a written decision record are a cleaner way to move on after a long discussion.

## Related notes

- **[[AI, Averaged Decisions, and Premature Convergence on Solutions]]**: Models can settle too quickly on familiar answers; here, the familiar answer comes from the conversation itself.
- **[[Constraint Saturation and Rule Oscillation in Coding Agents]]**: Competing prompt rules can crowd one another out, much as a repeated topic can crowd out other constraints.
- **[[How Context Narrows an AI's Solution Space]]**: Context helps rule out unsuitable solutions, but too much emphasis on one idea can narrow the options too far.
- **[[How Targeted Prompts Steer Model Solution Spaces]]**: Targeted instructions and exclusions can bring an answer back to the current task.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: The harness can enforce focused sessions and control how context is shortened.
- **[[Proxy Metrics and Operational Invariants in AI Systems]]**: Historical assumptions and proxy measures can reinforce themselves in an agent workflow.
