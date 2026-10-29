---
title: Production Feedback and Safe Automated Recovery
tags:
  - ai-agents
  - observability
  - incident-response
  - ci-cd
  - database-migrations
  - reliability
aliases:
  - Agent-Assisted Production Investigation
  - Bounded Autonomous Incident Recovery
  - Compatibility Evidence for Rollback
---

# Production Feedback and Safe Automated Recovery

A release passes its tests, reaches production, and gradually makes invoice processing slower. By the time an engineer opens the incident, an agent could already have collected the deployment timeline, compared affected tenants, inspected traces, and prepared a reproducer. That can shorten diagnosis without giving the agent unrestricted permission to change production.

The delivery process needs a return path from observed behavior to investigation, correction, verification, and observation of the correction. It also needs a separate path for safe containment while the permanent fix is still being developed.

## Start from existing operational signals

Use service metrics, logs, distributed traces, deployment events, infrastructure changes, feature-flag exposure, and business events. Preserve the time window, environment, service version, and affected cohort. A broad alert such as "latency increased" is much more useful when linked to the release and configuration actually serving those requests.

Deterministic alerts remain appropriate for known conditions: health checks, error budgets, queue growth, missing heartbeats, and established limits. Statistical detection can identify changes against a baseline. An LLM can help interpret several signals and investigate ambiguous cases; it should not be the only mechanism noticing that a critical service is unavailable.

Slow drift needs different comparisons from an immediate outage. A query can become expensive as data grows, traffic can shift toward a costly customer class, or a cache can hide a regression until it expires. Compare like workloads and account for seasonality, configuration, data volume, and infrastructure changes. A rising chart does not identify a root cause by itself.

## Make the investigation reconstructible

Existing observability platforms already provide useful investigation components. Grafana documents [Sift analyses](https://grafana.com/docs/grafana-cloud/ai-tools/machine-learning/sift/analyses/) for telemetry checks such as log patterns, deployment changes, and resource contention. Evaluate such capabilities before writing another diagnostic system. Their findings still need to be tied to the incident's scope and evidence; they do not establish authority to change production.

Give an investigator controlled access to the evidence needed for a specific incident. Useful operations include reading deployment history, comparing traces, retrieving bounded log excerpts, inspecting configuration, and running approved diagnostic queries.

The investigation should build a timeline and distinguish observations from hypotheses. For example:

| Record | Meaning |
| --- | --- |
| p95 duration increased after deployment for one tenant cohort | Observation tied to a query and time window |
| The new query shape may bypass an index | Hypothesis |
| The same query plan reproduces the slowdown on a representative dataset | Supporting experiment |
| Previous application version remains compatible with current writes | Separate recovery evidence |

Search commits and deployment changes as candidate explanations. A temporally adjacent commit is a suspect, not proof of causation. Record alternative causes and missing evidence. If the agent proposes a fix, require a reproducer that fails for the relevant reason before the change and checks the intended behavior afterward.

Keep production investigation separate from destructive experimentation. Reproduce migrations, query changes, and failure injection in approved test environments. [[Production-Like Test Data for Coding Agents]] describes how to obtain a bounded dataset when the defect depends on real relationships.

## Distinguish diagnosis, containment, and permanent repair

An agent that understands an incident may recommend disabling a flag, stopping a rollout, restoring a prior artifact, or escalating. Those actions require different authority from reading logs.

Define three levels explicitly:

1. **Observe and diagnose:** read approved evidence and prepare an investigation.
2. **Execute preapproved remediation:** request a narrow, tested operation when its conditions hold.
3. **Propose new production changes:** create a repair artifact that goes through the relevant delivery and approval process.

Do not turn the second level into a generic production terminal. A recovery tool should accept a service, incident, expected current deployment, approved target, and eligibility evidence. A trusted controller checks live state and performs the operation.

If a known failure can be handled by established metrics and a release controller, an LLM need not execute the recovery. For example, [Argo Rollouts analysis](https://argo-rollouts.readthedocs.io/en/stable/features/analysis/) supports metric-driven analysis associated with rollout progression. AI can investigate less obvious situations while deterministic controllers handle known actions.

## Bind recovery to tested eligibility

An illustrative recovery policy might allow returning a service to the previous artifact when the new release is within its recovery window, the observed regression meets defined criteria, and the prior version is compatible with current state.

| Condition | Consequence |
| --- | --- |
| Canary fails a required health criterion | Abort progression under release policy |
| Recent release correlates with errors and compatibility evidence is valid | Permit the tested rollback procedure |
| Latency rises without a clear release relationship | Continue diagnosis or escalate |
| Schema or data transition invalidated the prior version | Do not apply the ordinary application rollback |
| Another deployment has replaced the candidate | Re-evaluate; the original recovery request is stale |
| Recovery already ran for the same incident and target | Return the recorded result or verify current state |

Use live preconditions or version checks so an agent cannot accidentally revert a later unrelated release. Serialize conflicting deployment and recovery actions. Make retries idempotent, limit repeated reversals, and define a cooldown or escalation condition when the system fails to stabilize.

After an action, verify both service health and business invariants. A dashboard returning to green does not establish that payments were reconciled or that messages were not lost. Record the operation, result, remaining uncertainty, and required follow-up. Automatic containment should still leave an accountable incident record.

## Application rollback and data rollback are different operations

Returning from application version N to N-1 does not rewind the database. N may have written a new enum value, removed information, changed an event format, or performed an external side effect. The old binary can start successfully and still misinterpret that state.

Require a supported compatibility matrix for each release strategy:

| Combination | Question |
| --- | --- |
| Application N with schema N | Does the new release work? |
| Application N-1 with schema N | Can the prior application run after the schema change? |
| Application N with schema N-1 | Is application-first deployment supported, if the strategy requires it? |
| Application N-1 reading data written by N | Does rollback preserve meaning as well as syntax? |
| Mixed producer and consumer versions | Can services coexist during rollout and recovery? |

Not every combination must be supported. Record the permitted deployment order and verify the combinations that the process relies on. Include cached values, messages, background jobs, and long-lived clients where relevant; the database schema alone does not define compatibility.

Agent execution can reduce the effort of building and running this matrix. It cannot establish compatibility merely by generating many tests. The expected behavior and tested combinations need an independent reference.

## Design migrations around a recovery strategy

[Parallel change](https://martinfowler.com/bliki/ParallelChange.html), also called expand and contract, separates expansion, migration of consumers and data, and removal of the old interface. This gives old and new code a deliberate coexistence period.

For a database change, add the new representation first, migrate with observable progress, move readers and writers, and remove the old representation only after the required recovery window closes. Check consistency during coexistence. Dual writes can fail partially, so they need an explicit repair and reconciliation strategy.

An executable `Down` migration is useful when it genuinely reverses the change. It is not evidence of lossless recovery. Splitting or merging fields, discarding detail, and accepting new data can make reversal ambiguous. Restore-from-backup, forward repair, and application rollback have different consequences for availability and data loss.

Microsoft's [EF Core deployment guidance](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/applying) recommends reviewing and testing generated migrations before production. In this proposed process, the acceptance artifact should additionally state what recovery is supported and under which data conditions.

An agent can automate rehearsals: build a representative dataset, run the migration, interrupt it at defined points, retry, verify invariants, run old and new applications, and measure duration and locking. Keep destructive trials off the live production database.

## Publish a recovery assessment with the release

```yaml
release: billing-N
application_rollback:
  target: billing-N-minus-1
  supported: true
  schema_reversal_required: false
  evidence: compatibility-run-184
  preconditions:
    - legacy_columns_retained
    - new_payment_status_not_enabled
data_recovery:
  reversible_without_loss: false
  procedure: approved-forward-repair-or-restore
review_required_when:
  - contract_phase_started
  - another_release_changes_the_schema
```

This is an illustrative manifest. Its evidence must refer to actual tested artifacts, and its preconditions must be checked against live state before recovery. A stale `supported: true` is dangerous once a later migration removes the old fields.

Recovery confidence also depends on data scale, replication, external services, and the realism of rehearsal environments. Report those limits rather than turning one successful test into an unconditional guarantee.

## Return the permanent fix to the normal SDLC

Once the agent has a reproducer and a proposed correction, create a bounded implementation task with the incident evidence. Run independent verification, compatibility checks, and the normal release process. An incident's urgency may select a predefined expedited workflow; it should not silently remove the checks that make recovery safe.

After release, compare the relevant operational behavior and close the incident only when the required evidence is present. Keep a follow-up if data reconciliation, cleanup, or a deeper cause remains unresolved.

A missed defect can also produce a proposed new test, analyzer, diagnostic tool, or harness improvement. That proposal belongs to a separately evaluated process change. One incident does not justify an untested rule applied to every future task (see [[Observability and Controlled Improvement of Coding Agent Harnesses]]).

## Related notes

- **[[Designing an Agentic SDLC for Business Software]]** — Connects production observation with implementation and business decisions.
- **[[Isolated Engineering Environments for Coding Agents]]** — Enforces separate development and operational capabilities.
- **[[Managing the Full Lifecycle of Feature Flags]]** — Uses activation controls for bounded exposure and containment.
- **[[Testing in the Model, Agent, LLM Era]]** — Relates generated tests to behavioral evidence.
