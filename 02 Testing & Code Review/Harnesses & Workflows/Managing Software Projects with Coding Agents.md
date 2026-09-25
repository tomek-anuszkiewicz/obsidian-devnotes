---
title: Managing Software Projects with Coding Agents
tags:
  - ai-agents
  - agentic-workflows
  - project-planning
  - roadmap-maintenance
  - code-review
aliases:
  - Living Roadmaps for Agentic Development
  - Just-in-Time Task Design for Coding Agents
  - Managing Agentic Project Flow
  - Human Control of Agent-Maintained Roadmaps
---

# Managing Software Projects with Coding Agents

A coding agent can implement a change faster than a team can decide whether the change is worth making, understand its consequences, review it, and deploy it. A project plan should reflect those different speeds. The team needs a durable direction and a careful decision about the work it starts now. It does not need detailed tickets for every possible change months in advance.

The practical arrangement is a living roadmap whose detail increases as an item approaches execution. The agent maintains context and prepares candidate tasks; people choose the next work, accept substantive changes to direction, and review the result. The measure of progress is a verified change in the product, not the amount of code or planning text produced.

## Keep strategic constraints separate from the order of work

Some early decisions have a long reach: technology, data ownership, cloud services, deployment model, and how services communicate. They can be revisited, but changing them after several features depend on them has a real cost. Record the choice, its reason, rejected alternatives, and the circumstances that would justify reconsideration. The agent should treat these as current constraints while planning tasks. If implementation reveals a reason to change one, it should surface a new strategic decision rather than quietly revise the architecture inside a feature task (see [[In-Flight Documentation as the Primary Framework for Coding Agents]] and [[Designing Software Architecture with LLM Assistance]]).

The ordered roadmap has a different job. A plain text file or spreadsheet can list possible work in priority order. Near the top are items likely to be taken next; lower down are less certain ideas. Moving an item upward means making it more concrete in light of the current system and business goals. Moving it downward, rewriting it, or removing it is normal when the project learns something new.

Once the team selects work for execution, the agent needs a narrower active plan: the next steps, current constraints, and checks. This is a distinction in purpose, not a requirement for two particular files. The active plan should drop detailed entries for verified completed steps so old instructions do not compete with the next task in the agent's context. The ordered roadmap can still retain distant possibilities (see [[Active Backlog Pruning and Context Hygiene in Agentic Roadmaps]]).

The task is the shortest-horizon plan. Form it just before execution from the current roadmap item, code, documentation, and team decisions. It needs a bounded result and a way to check it; it does not need to predict discoveries the work itself will make. The implementation plan may live in the session if its details will not be needed later. Record decisions that future work depends on (see [[Agentic Software Development Workflows]]).

Some tasks should reduce uncertainty before implementation. A short experiment may establish whether an integration is viable, which failure mode matters, or which of two designs meets a constraint. Its accepted outcome can be a decision to abandon an approach. Treating every task as a promise to ship code would hide that learning.

Estimates also have two different sources of uncertainty: whether the agent can produce a workable change, and how long people will need to validate and integrate it. One task may take an hour; another may take days despite a quick first draft. A short sprint can still be a useful commitment, but detailed allocation far ahead of execution can become stale. The team can keep dated milestones while using a flow board to see where current tasks wait.

## Spend human attention where decisions become consequential

Much of the material an agent needs is for the agent to read: business goals, current specifications, architecture, a domain vocabulary, past decisions, and the evolving roadmap. People do not need to inspect every editorial change to every document. They should keep the broad strategic points in view and inspect a roadmap item closely as it reaches the top. They can then compare it with what the team is building now and with decisions made a month or two earlier.

That depends on distinguishing editing from deciding. The agent can rewrite a distant idea for clarity. If it changes the priority of a major item, alters a milestone, retires an assumption, or claims a problem has been solved, it should show the proposed change, the new evidence, and which earlier decision it affects. The team accepts or rejects the substantive change. Otherwise several plausible edits can leave a written roadmap that no longer matches the team's mental model.

Meeting notes, recordings, tickets, and an engineering diary can help recover why a decision was made. A useful agent answer identifies the contemporaneous source, the alternatives considered, and any unresolved risk. It should distinguish that record from a present-day interpretation and say when the source is missing. Retrieval makes historical information accessible; it does not by itself create shared understanding (see [[LLM Agents and Institutional Memory in Software Teams]] and [[The Living Engineering Chronicle and Context Compaction]]).

The shared vocabulary matters for the same reason. The agent can use agreed names while writing code and documentation and flag inconsistent terminology before review. It should flag a possible semantic distinction instead of automatically forcing two different domain concepts under one name. The team settles the meaning; the agent applies the convention consistently afterward (see [[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]]).

## Manage the whole delivery flow

An agent finishing implementation does not finish the task. The change still has to be understood, tested, reviewed, integrated, deployed, and observed in operation. A board becomes useful when several people need to see who owns each stage and where work is waiting. It need not replace the simple ordered roadmap that guides what enters the flow.

If agent output arrives faster than people can review it, more parallel coding increases the queue of unverified changes. Limit the number of tasks in progress and give review priority when that queue grows. The person directing the task should understand the generated solution well enough to explain its assumptions and failure modes; another person reviews it independently. Passing tests and an apparently clean diff are evidence, but neither proves that the team understands what it is accepting (see [[AI Productivity Is Limited by the Delivery System]] and [[Reviewing AI-Generated Code]]).

Agents can reduce review cost by producing small coherent changes and commits, running meaningful checks, identifying risky paths, and helping resolve merge conflicts. A conflict that Git can merge automatically can still be a conflict in behavior, so verify the combined system. Avoid expanding a focused task with every adjacent improvement the agent can cheaply generate: the added code still needs human attention.

Deployment and production observation complete the feedback loop. Tests, logging, alerts, and operational checks can make a change easier to assess, but their existence is not a substitute for reviewing their meaning. A fast implementation is valuable when the delivery system can turn it into reliable learning (see [[AI Productivity Is Limited by the Delivery System]]).

## Use milestones to test direction, not to pretend certainty

A flexible roadmap still needs dated checkpoints. A milestone names an observable product state the team intends to reach. The agent can compare that state with what works, what has passed review, what is waiting for deployment, and which decisions remain open. It should report the concrete gap and any threat to the date rather than manufacture a precise percentage of completion from closed tickets.

After a change or experiment, feed the result back into the current specification and the roadmap. Some results confirm the plan; others expose a missing task, a bad assumption, or a reason to stop. Cheap agent execution makes this learning loop faster, but human review, integration, and the effects of deployment still cost time. The team controls direction and task intake. The agent helps keep the plan and its supporting context current enough for the next decision.
