---
title: Observability and Controlled Improvement of Coding Agent Harnesses
tags:
  - ai-agents
  - observability
  - agentic-harness
  - continuous-improvement
  - token-economics
  - evaluation
aliases:
  - Coding Agent Telemetry
  - Harness Baseline and Candidate Experiments
  - Shadow Evaluation of Agent Workflows
  - Measuring Skills and Subagent Value
---

# Observability and Controlled Improvement of Coding Agent Harnesses

A new naming rule makes code more consistent, but changes that previously passed after one implementation now require five repair rounds. The final build remains green. Without execution data, the team sees the benefit and misses the increasing cost.

Useful telemetry connects the work, the configuration that performed it, the evidence it produced, and the cost of reaching an accepted result. That connection supports an improvement loop: observe failures, propose a bounded change, compare it with the current configuration, and promote it only when the evidence supports doing so.

## Collect facts at the layer that owns them

| Source | Facts it can report reliably | Context it usually lacks |
| --- | --- | --- |
| Model provider | Reported token usage, request identifiers, response status | Business task and acceptance meaning |
| Agent runtime | Tool calls, session events, exposed delegation events, errors | Why a company workflow required this activity |
| Tool service | Actual operation, duration, output status, denied access | Whether its result solved the larger task |
| Orchestrator | Task, phase, attempt, trigger, waiting time, workflow version | Every internal model computation |
| CI and reviewers | Checks, findings, evidence, candidate identity | Total cost across all prior attempts |
| Delivery and incident systems | Deployment outcome, regressions, recovery | Which prompt instruction caused an earlier choice |

Prefer native runtime events and provider usage reports to asking the agent to estimate its own token consumption. Add organization-specific context at the orchestrator. A tool wrapper can report that a database query took twelve seconds; the workflow supplies the fact that this query was part of reproducing a particular incident.

Use an existing collector and observability backend where practical. Logs explain events, traces connect work across components, and metrics support aggregate trends. A separate experiment registry can retain comparable task outcomes and configuration versions. [[OpenTelemetry — Architecture, Signals, and Collector]] describes the infrastructure; specialized tools such as Langfuse or LangSmith are options when their tracing and evaluation features fit the process.

## Use a common identity across the execution

Carry stable identifiers for the task, execution, attempt, candidate commit, specification, workflow, policy, model, and harness configuration. A trace identifier helps connect runtime events, but a long business workflow may span several traces, services, and days. Keep the durable workflow identifier as well.

An illustrative event could be:

```json
{
  "event_id": "evt-0042",
  "task_id": "BILLING-142",
  "execution_id": "run-19",
  "attempt": 2,
  "phase": "repair",
  "candidate": "candidate-commit-id",
  "harness_version": "harness-v12",
  "policy_version": "acceptance-v7",
  "triggering_findings": ["DOMAIN-017"],
  "operation": "tool.completed",
  "tool": "test.run",
  "duration_ms": 12400,
  "outcome": "failed",
  "artifact": "artifact:billing-test-report"
}
```

Deduplicate events on ingestion and retain their origin. A reconnect may replay an event. A worker crash may leave a started operation without a matching completion. Report such gaps rather than silently treating missing usage or missing failures as zero.

Store configuration identifiers that resolve to exact contents, not just labels such as "latest prompt." Record the model identifier reported by the provider, runtime version, tools, retrieval configuration, policy, relevant repository state, and environment image. If a provider does not expose an immutable model revision, record that limitation in comparisons.

## Separate usage, cost, elapsed time, and value

Token counts are useful even when they are not the billing unit. An API-priced run can have an estimated cost calculated from usage and the applicable rate card. A subscription run should not be assigned that estimate as though it were an actual invoice. Keep `billing_mode`, `reported_usage`, `estimated_cost`, and reconciled charges separate.

Input, cached input, output, and reasoning categories can overlap depending on provider semantics. Cached input may already be included in total input, and reasoning output may already be included in total output. Do not add every reported field together. Check whether a report covers one call, one turn, or the entire resumed session before aggregating it. Store raw reports so an adapter bug can be corrected later.

Latency has similar traps. The sum of child-agent durations is work consumed; it is not elapsed time when children run concurrently. Separate model time, tool time, queue time, environment startup, verification, and waiting for a person. Measure both the critical path and total resources.

Useful outcome measures include cost per accepted task, first-pass acceptance rate, repair rounds, time to verified result, human intervention time, and regressions found after delivery. Include failed and abandoned attempts in the costs of a cohort. Reporting only successful executions makes a wasteful configuration look efficient.

Compare similar classes of work. A migration, a documentation edit, and a UI experiment should not be treated as equally difficult samples. Also keep tails visible: a reasonable median can hide a few executions consuming most of the budget.

## A concrete Codex integration boundary

As checked on 2026-10-29, the official [non-interactive mode documentation](https://learn.chatgpt.com/docs/non-interactive-mode) describes JSON event output and a `turn.completed` usage object including input, cached input, output, and reasoning output fields. Use the installed version's documented schema; do not assume that another SDK release exposes exactly the same object.

For example, a collector around `codex exec --json` can record completion events and associate them with the workflow execution. Preserve the full usage object and validate its accounting semantics before computing totals. An SDK adapter can serve the same purpose, but its interface should be checked against the pinned package rather than copied from an older example.

The official [advanced configuration documentation](https://learn.chatgpt.com/docs/config-file/config-advanced) also describes opt-in OpenTelemetry event export, including tool and approval events. Its documented configuration keeps user-prompt logging disabled unless explicitly enabled. Configure the exporter and collector for the installed runtime; support for individual signals and fields can vary.

OpenTelemetry maintains a separate [GenAI semantic conventions repository](https://github.com/open-telemetry/semantic-conventions-genai). Record the conventions version used by an adapter. Common field names help comparison, but they do not make different vendors' usage semantics identical.

## Observe actions without inventing access to thoughts

Tool calls, file reads, delegation, retries, and externally visible decisions can be instrumented. Reading `SKILL.md` can show that a skill was loaded. A wrapped skill invocation can show that a procedure was started. Neither proves that every instruction affected the eventual implementation.

Likewise, a model's retrospective explanation of why it "thought for a long time" is a hypothesis. Compare it with timestamps, API latency, tool failures, context size, and actual edits. Do not build process accounting around hidden reasoning that the runtime does not expose or around unsupported claims about what the model attended to.

Useful spans are practical: repository search, dependency installation, implementation, test execution, reviewer invocation, repair, and environment recovery. They can reveal repeated whole-repository searches, identical failed commands, or unnecessary serial checks without needing the model's private reasoning.

## Find unused or ineffective capabilities

A migration skill unused for three months may be functioning perfectly if there were no migrations. A contract-review skill unused during twenty public API changes suggests a routing problem. Measure opportunities as well as invocations.

| Question | Evidence |
| --- | --- |
| Was the capability relevant? | Eligible task class and trusted scope analysis |
| Was it made available? | Loaded configuration and permissions |
| Was it selected? | Runtime or wrapper invocation event |
| Did it complete useful work? | Artifact and independently checked result |
| Was it worth its cost? | Comparison with the same task without it |

Low usage can mean poor discoverability, broken activation, overlap with another capability, or genuine redundancy. Diagnose those possibilities before removing it. Rare safety checks can have high value even when ordinary task averages do not show it.

Test additions and removals. A smaller instruction set can perform better by removing contradictions or irrelevant context, but fewer tokens alone do not prove improvement. [[Configuring and Testing Coding Agent Capabilities]] covers configuration checks, while [[How Much Guidance Does a Coding Agent Need]] describes controlled guidance comparisons.

## Attribute expensive repairs to findings carefully

Associate a repair with the findings that triggered it. Follow the patch and subsequent checks. If a naming rule repeatedly causes architecture violations, inspect whether the rules conflict, whether the vocabulary is ambiguous, or whether the initial implementation guidance is missing an example.

Cost attribution is often shared: one repair can address several findings, and one check can discover several defects. Keep the relationship explicit instead of charging the full repair to every rule. Use marginal comparisons when deciding whether a rule actually increases or reduces total cost.

A reviewer with many findings is not automatically valuable. Count confirmed defects, rejected findings, reproducibility, and escaped failures. A rule can appear cheap because it misses everything. A stricter rule can legitimately cost more because it prevents expensive production failures.

## Use traces to propose parallel work

Look for independent activities on the critical path, such as separate read-only analyses or checks against the same immutable candidate. Do not assume that activities are independent because they touch different files. Shared schemas, test databases, build caches, and mutable workspaces can introduce hidden ordering requirements.

A proposed parallel version should specify isolated workspaces, dependency ordering, result collection, and verification of the combined outcome. Measure coordination cost and total token usage as well as elapsed time. Delegation can save parent context while increasing total compute.

## Run two controlled improvement loops

The delivery loop changes product code until it satisfies protected requirements. The improvement loop changes the harness to make future delivery more reliable or efficient. Keep their evaluation authority separate.

A reactive trigger might be rising repair cost for a particular rule. An exploratory trigger might allocate a small periodic budget to testing another instruction, tool, reviewer configuration, or model. Random variation can generate candidates, but arbitrary mutation of live production controls is not a safe experiment.

An analyzing agent can inspect traces and propose a hypothesis: "Providing the domain glossary before implementation will reduce naming repair rounds." Record the proposed change, expected mechanism, affected task classes, quality constraints, and experiment budget. Preserve alternatives such as improving a tool or fixing the environment; every failure does not call for another prompt rule.

[MIPROv2](https://dspy.ai/current/api/optimizers/MIPROv2/) searches combinations of instructions and examples. [GEPA](https://dspy.ai/current/api/optimizers/GEPA/overview/) uses execution feedback to propose changes and evaluate candidates. These provide concrete optimization techniques, but their existence does not establish that optimizing a metric will improve a company's full SDLC.

## Compare baseline and candidate on the same work

Start both variants from the same repository snapshot, task, specification, environment, and verification criteria. Give each a fresh session and isolated mutable resources. Do not let the candidate inherit the baseline's solution or let both variants post comments, merge, deploy, or notify customers. A shadow execution creates evaluation artifacts; the authorized production path remains explicit.

Use representative tasks across relevant risk classes, including difficult and rare cases. Repeat enough tasks to see execution variability. Compare paired differences where both versions execute the same task. Preserve raw outcomes so that a large benefit on trivial edits cannot hide a regression on migrations.

Quality and policy constraints come first. Then compare the intended optimization target: cost, verified latency, intervention burden, or first-pass success. A candidate need not win on every task. It needs evidence of useful performance on the intended population within agreed regression limits.

Decide the stopping and promotion procedure before observing the results. Repeatedly checking an ordinary fixed-sample significance test and stopping at the first favorable result can mislead. Use a planned evaluation size or an appropriate sequential procedure. Several weeks of running is not itself a sample-size justification. If the evidence is insufficient, keep the candidate unpromoted.

Maintain held-out tasks that the candidate-generating process cannot inspect. Otherwise the optimization loop can learn the benchmark instead of improving general behavior. Treat graders and acceptance tests as protected evaluation infrastructure. An LLM-based evaluator can contribute evidence, but its preferences and blind spots also need calibration.

## Promote a version and keep watching it

```text
Proposed -> Offline evaluation -> Shadow evaluation
         -> Limited adoption -> Promoted -> Monitored
Any evaluation stage -> Rejected or Needs more evidence
Monitored -> Roll back configuration if regression is confirmed
```

Store the candidate's lineage, evaluation data, decision, and rollback target. Keep an explicit owner for promotion rules. A model update, tool change, or repository shift can invalidate earlier results, so revisit comparisons when the operating conditions change.

Experiments consume resources too. Limit concurrency, select informative tasks, and stop candidates that clearly violate constraints. An illustrative economic check is whether the expected saving across future comparable tasks exceeds the evaluation and maintenance cost. That forecast is uncertain; it should not excuse accepting worse correctness.

Start small: collect task outcomes and runtime events, identify one costly repeatable failure, test one change, and compare results. A reliable evaluation loop is more useful than a large collection of unconnected dashboards.

## Related notes

- **[[Learning Coding Agents Through Failure-Driven Instructions]]** — Uses failures to propose better instructions.
- **[[Token Optimization and Context Economics in Agentic Workflows]]** — Explains concrete sources of execution cost.
- **[[Constraint Saturation and Rule Oscillation in Coding Agents]]** — Describes conflicting instructions and repeated repair.
- **[[Acceptance Policies and Automated Repair in Agentic SDLC]]** — Defines the evidence the improvement process must preserve.
- **[[Conversation History as Sensitive Data]]** — Explains why telemetry content needs access and retention controls.
