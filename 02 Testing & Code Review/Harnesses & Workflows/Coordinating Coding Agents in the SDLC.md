---
title: Coordinating Coding Agents in the SDLC
tags:
  - ai-agents
  - software-engineering
  - agentic-workflows
  - ci-cd
  - system-design
aliases:
  - Coding Agent Coordination
  - Coordinating Concurrent Agent Repairs
  - Testing a Coding Agent Coordinator
---

# Coordinating Coding Agents in the SDLC

**When a new issue arrives, the system must decide whether to start a repair or send the new information to the agent already working on the same defect.** AutoGen described conversation-based agent orchestration in 2023. MetaGPT divided software work among specialized roles. In April 2026, OpenAI described Symphony, which manages Codex execution based on tracker state. [AutoGen](https://www.microsoft.com/en-us/research/blog/autogen-enabling-next-generation-large-language-model-applications/) · [MetaGPT](https://arxiv.org/abs/2308.00352) · [Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/)

## Coordinate work from intake through production

Work can start with a Jira issue, a pull request comment, a CI result, or a monitoring alert. Triage produces a task and a pull request. Review findings or CI failures go back to a worker. After human approval, the change moves toward deployment. A production signal can trigger another round of triage.

- **Pull requests and review.** Agents can review a change independently while CI runs tests and other required checks. The coordinator sends findings to the worker responsible for the repair or gives them to a replacement with the relevant context. After an edit, it checks results for the current commit. Once the required checks pass, the human receives the pull request, test results, and status of the findings. Repository policy governs the merge.

- **Deployment.** The pipeline records the commit or artifact, target environment, and deployment time. Deployment rules can require human approval. In a canary rollout, they can stop traffic from increasing if the error rate crosses a configured threshold. The coordinator passes the result and context to the person or agent responsible for responding. [GitHub Actions deployment rules](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) · [Argo Rollouts analysis](https://argo-rollouts.readthedocs.io/en/stable/features/analysis/)

- **Monitoring and response.** If Grafana reports an increase in 5xx errors after deployment, a diagnostic agent can compare metrics for the old and new versions, inspect logs in Kibana, and examine request traces. Timing helps narrow down which changes to investigate. The coordinator uses the evidence to attach the signal to an open incident or route it to triage as a new issue. [OpenTelemetry signals](https://opentelemetry.io/docs/concepts/signals/)

Links between the issue, repair, worker session, pull request, commit, deployed version, and incident determine where the next event should go. Components responsible for triage, code changes, and production response can share the same identifiers and work state. [[Designing an Agentic SDLC for Business Software]] describes the broader delivery model.

### Resolve review disputes and end repair loops

Count automated repair and review rounds at two levels. A **limit per pull request** caps the whole loop. A **limit per finding** lets the coordinator stop earlier when a specific problem persists. Give the finding an identifier that survives commits. Associate it with the rule, the behavior at issue, and the relevant code even if the reviewer rephrases the comment or the line number changes. A repeated webhook or retry of the same call after a technical failure does not count as a new round.

When either limit is exhausted and a finding remains open, stop automatic edits and escalate to a human. Escalate sooner if patches reverse earlier fixes, reviewers request incompatible changes, or repeated attempts produce no new evidence. Give the human the latest diff, disputed findings, attempted fixes, cited rules, and the decision to make. Distinguish blocking findings from suggestions.

A recurring dispute can reveal a difference between the author's and reviewer's instructions. Record the rule identifier and version, scope, priority, commit, and each agent's evidence. Determine whether the disagreement concerns a binding contract, a preference, or an unclear requirement. Resolve conflicting rules in the shared source of policy.

One hypothesis is that the author needs a short set of core behavior and safety rules, while the reviewer can apply a more detailed checklist against the same contract. Evaluate the total time, cost, and accepted quality, including the rounds spent on repair. The design of the review process and its instructions is a separate topic. See [[When Is an AI Agent’s Code Ready to Merge]], [[Constraint Saturation and Rule Oscillation in Coding Agents]], and [[How Much Guidance Does a Coding Agent Need]].

## What existing tools coordinate

- **OpenAI Symphony.** Symphony polls the tracker, assigns isolated workspaces, limits concurrency, and retries interrupted work. Its claim prevents a second dispatch for the same issue. Different issue identifiers can still refer to the same defect. [Symphony specification](https://github.com/openai/symphony/blob/main/SPEC.md#7-orchestrator-state-machine)

- **Linear and Jira.** Linear Triage Intelligence and Jira with Rovo look for potential duplicates. Linear documents automation that can send a new bug from triage to Codex or Claude Code and produce a draft pull request. Automatically routing a second issue to the session already fixing the defect remains a scenario to verify. [Linear Triage Intelligence](https://linear.app/docs/triage-intelligence) · [Linear Cloud Coding Agent](https://linear.app/docs/linear-cloud-coding-agent) · [Rovo in Jira](https://support.atlassian.com/organization-administration/docs/atlassian-intelligence-features-in-jira-software)

- **DeepSeek Super Agent.** In this research prototype, the router can attach a message to existing work when the message explicitly refers to it, for example through its issue or pull request. This shows how a coordinator can direct new evidence to an existing worker. [DeepSeek prototype](https://github.com/deepseek-ai/dsh-superagent-prototype) · [Router rules](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/004-prompts.md)

- **Anthropic Claude Code.** Experimental Agent Teams have a lead, a shared task list, and messaging between agents. Scheduled Tasks can run in response to GitHub events or an API call. Resuming the lead with `/resume` does not restore teammates that ran in the same process. [Agent Teams](https://code.claude.com/docs/en/agent-teams#limitations) · [Scheduled Tasks](https://code.claude.com/docs/en/routines)

- **Google Antigravity.** Teamwork divides approved work into milestones, delegates it, and hands off to a successor between milestones. The team keeps the plan and progress in workspace artifacts. Remote Agents store conversations with the project and can resume by identifier. Jules exposed a session messaging API. Google announced that Jules would become read-only after November 11, 2026. [Teamwork](https://antigravity.google/docs/teamwork/) · [Remote Agents](https://antigravity.google/docs/remote-agents/) · [Jules API](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/sendMessage) · [Jules turndown](https://jules.google/docs/changelog/)

- **Cursor Projects.** The coordinator delegates work, maintains shared project context, and reacts to events such as pull request and CI activity. It can message a worker during a turn or trigger its next turn. The Cloud Agents API can steer active work or start a follow-up with the existing conversation and workspace. [Cursor Projects](https://cursor.com/docs/agent/projects) · [Worker messaging](https://cursor.com/docs/release-notes/cloud-agents) · [Cloud Agents API](https://cursor.com/docs/cloud-agent/api/endpoints)

## Work through the login and token refresh cases

A worker is fixing a login bug when another issue reports an HTTP 401 during token refresh. The coordinator compares the report with the diagnosis and work already in progress. If the cause is shared, attach the new report and ask the same worker to verify it in the existing pull request. If the defects have different causes, create separate tasks even if the changes might touch the same files. Ask for more diagnosis when the evidence is inconclusive.

### Order repairs that affect the same contract

One repair might replace the token format while the other fixes refresh behavior for the old format. Separate branches isolate edits. Both pull requests can pass CI on their own and still break refresh when combined, even when Git finds a clean textual merge.

Record which change must land first when the dependency is clear. The dependent worker can prepare a reproducer or regression test while it waits, then implement against the new base. For a late collision, compare the cost of adapting the patch with the cost of implementing it again. If the old assumptions have expired, close the obsolete pull request with a reason and keep the issue, diagnosis, useful tests, and decisions for the next attempt. Verify the combined candidate before integration. [GitHub merge queue](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue)

### Test the coordinator and the model separately

**Test workflow rules.** Fix the starting repository and task state, the event sequence, and scripted agent responses. Assert the resulting state and side effects. A duplicate should preserve one active assignment and one pull request. A delayed success for an old commit must leave the current candidate unapproved. A replaced worker's write must be rejected. When the graph changes, test the new definition against saved execution histories. [Temporal event history and replay](https://docs.temporal.io/tasks)

**Test with a real model.** Allow several acceptable paths where evidence is ambiguous, such as detecting a dependency or escalating it for a decision. Check observable effects and hard rule violations over repeated runs. AI can draft small repositories, commit histories, issue pairs, and event sequences. Establish expected or acceptable outcomes independently of the agent under test. One fixture can have two pull requests that pass on their own and break a contract when combined. [[Observability and Controlled Improvement of Coding Agent Harnesses]] describes comparisons on the same work.

## Assign responsibilities across the coordinator and workers

In this design, each project uses one tracker. Triage returns the same result format for Jira, GitHub Issues, and Azure Boards so the coordinator can follow the same process for each source.

1. **Triage the report.** A coordinator, a separate module, or a human classifies it, finds related issues, and evaluates whether they share a cause. The result records the links, supporting evidence, and missing information.

2. **Check the repair and record the decision.** A registry links an issue or group of issues to active work, its owner, the session identifier, the repository, the branch, and any pull request. Attach a report to existing work when the cause is shared. For a separate repair, reserve the new unit of work in one transaction so concurrent events do not launch two workers for the same identified repair.

3. **Send information to the assigned worker.** Add the new evidence to its active turn or start another turn in the same session if it is waiting. With Codex App Server, use `turn/steer` with the active turn identifier, or `thread/resume` and `turn/start` for a saved session. If the turn ends before delivery, reread its state and route the message to the next turn. [Codex App Server](https://learn.chatgpt.com/docs/app-server)

4. **Keep enough state to resume.** Save the session history, working directory state, and a short record of the diagnosis, decisions, test results, and next action. On another machine, restore the branch or commit and any saved uncommitted changes from the workspace or a patch. If the original session cannot resume, give its work record and artifacts to a new session.

## Define a deterministic and durable workflow

Model a repair as a graph or state machine. A step runs code, calls an agent, or waits for an event such as a CI result or human approval. Edges describe allowed transitions. An agent can propose a duplicate and supply evidence. Code checks that the target repair is active and can accept the report. The same state and recorded events produce the same transition under the same rules.

**Workflow durability** lets the coordinator recover where a repair stopped and what it was waiting for. The engine can replay event history or load a checkpoint. Save the model result so recovery can reuse it. An operation interrupted before recording its result can run again, so check whether the previous attempt already opened the pull request before creating one. Workflow history, Codex session history, and the working directory each need their own persistence plan. [Temporal workflow recovery](https://docs.temporal.io/workflows) · [Activity retries](https://docs.temporal.io/activities)

### Workflow engines and agent graphs

- **Temporal, Dapr Workflow, and Azure Durable Functions** support orchestration in C# with recovery from recorded history. The workflow waits for external events, and separate activities handle model calls, API requests, and Git operations. Temporal and Dapr can run on infrastructure you manage. Durable Functions uses Azure Functions with a durable state backend. [Temporal .NET](https://docs.temporal.io/develop/dotnet) · [Temporal Self-hosted](https://docs.temporal.io/self-hosted-guide) · [Dapr Workflow .NET](https://docs.dapr.io/developing-applications/sdks/dotnet/dotnet-workflow/) · [Dapr on your own VMs](https://docs.dapr.io/operations/hosting/self-hosted/self-hosted-overview/) · [Durable Functions](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-code-constraints?tabs=csharp)

- **Elsa Workflows and Camunda 8** support visual process modeling. Elsa offers Elsa Studio and .NET code. With persistent storage it saves process instances and the points where they wait for events. Camunda executes BPMN models with human tasks, code-driven steps, and message waits. [Elsa Studio](https://docs.elsaworkflows.io/guides/studio) · [Elsa persistence](https://docs.elsaworkflows.io/guides/persistence) · [Camunda 8](https://docs.camunda.io/docs/components/concepts/concepts-overview/) · [BPMN events](https://docs.camunda.io/docs/components/modeler/bpmn/message-events/)

- **Microsoft Agent Framework and LangGraph** combine code, agents, and conditional transitions in a graph. Microsoft Agent Framework offers `WorkflowBuilder` in C#. LangGraph saves graph state with checkpoints. Persist checkpoints outside the process to survive a restart. A graph can handle triage or multi-agent review within a larger workflow. [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/) · [Microsoft Agent Framework checkpoints](https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints) · [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)

### A custom implementation in .NET

With one tracker and a simple flow, a .NET service and database can hold the workflow. Give each repair a `WorkId`, state, and links to issues, a Codex session, and a pull request. Store events by identifier, update the state atomically, and persist pending commands for execution after a restart. Implement retries, waiting, and concurrent reservations. An engine can supply those mechanisms. The application still defines duplicate detection and Codex integration. See [[Workflow Orchestration in Agentic Systems]].

Compare implementations with the same scenario. The workflow is waiting for review when a second issue joins the same repair. After a restart, late CI success for an old commit does not change the status of the current pull request. Delivering the same event again does not start a second worker or create a second pull request.

### Change a workflow while work is active

If a team wants new tests or review instructions to apply to open pull requests, it can use them at the next check. Record the policy used to assess each commit and rerun invalidated checks. Changes to the graph, state, or activity order may require existing executions to finish on the old definition or migrate explicitly. Temporal's replay requirements apply to SDLC workflows too. Choose the amount of versioning based on how long work stays active and what changes. [Temporal workflow versioning](https://docs.temporal.io/workflow-definition#versioning-workflows)

## Run Codex on virtual machines you manage

**Codex workers can run on virtual machines you manage in your own data center or cloud account.** Codex CLI runs commands and tests against the repository copy on the worker. A coordinator picks the machine and launches work through `codex exec` or Codex App Server. Command execution and model inference are separate deployment decisions. When using an external model, Codex still sends it the context needed for the task. [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) · [Integrating with a local Codex process](https://developers.openai.com/blog/codex-as-a-platform)

After a machine fails, confirm that the previous worker has stopped or lost write access before reassigning the repair. Give the replacement the saved session state and restore the branch, configuration, and uncommitted changes. Resume by session identifier and deliver any pending information in the next turn. Before retrying an interrupted operation, check its effect in the target system, for example whether the pull request already exists. [Resuming a saved session in Codex App Server](https://learn.chatgpt.com/docs/app-server)

Store session history and code state outside the disk that disappears with the machine. One option is a durable session directory per repair and a separate local SQLite database on each worker. Test takeover with the chosen configuration because some Codex state, such as goals stored in SQLite, requires preserving the database. See [[Isolated Engineering Environments for Coding Agents]]. [Codex on a network filesystem](https://learn.chatgpt.com/docs/environments/network-file-systems)

### Revoke publication rights when an assignment ends

When work closes, is cancelled, or is reassigned, invalidate the old assignment. If a worker has direct write access, the workflow record alone cannot stop it from publishing. A publication service can hold the credentials and check the current assignment before pushing code or changing a pull request. Reject requests from the old worker even if its machine reconnects. Revoke any direct write credentials before the replacement takes over. Reconcile writes already underway against the repository state.

## Topics to explore further

- **Observe changes after deployment.** Develop a separate note on observation after actual activation, regression criteria, and product outcomes. Connect it to [[Production Feedback and Safe Automated Recovery]], [[Managing the Full Lifecycle of Feature Flags]], and [[Measuring Business Outcomes After Software Delivery]].

- **Compare execution isolation.** Investigate NVIDIA OpenShell, Codex, Claude Code, Gemini or Antigravity, and GitHub Copilot. Determine where commands and model inference run, how each system enforces filesystem and network boundaries and handles credentials, and how the coordinator provisions an environment, recovers state, and revokes access.

- **Design automated review.** Compare a short set of author instructions with a more detailed reviewer checklist, settle which rules are binding, and test how the coordinator resolves conflicts and limits review rounds.

- **Evaluate agent behavior.** Develop reproducible repository fixtures and event sequences, define acceptable outcomes, and compare scripted workflow tests with repeated runs using a real model.

The documentation shows individual capabilities for triage, delegation, steering, and resumption. Validate them together for the selected tracker and product. Deliver two different issues close together, attach the second to the correct repair, pass its evidence to the worker, and restart the worker or coordinator. Confirm that the same repair resumes with its code and diagnosis. Check where the product processes issue content and code.
