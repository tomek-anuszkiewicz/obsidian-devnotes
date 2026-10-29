---
title: Managing the Full Lifecycle of Feature Flags
tags:
  - feature-flags
  - ci-cd
  - observability
  - ai-agents
  - software-engineering
aliases:
  - Feature Lifecycle Workflows
  - Progressive Rollout and Flag Cleanup
  - Automated Feature Flag Retirement
---

# Managing the Full Lifecycle of Feature Flags

A flag reaches full rollout, but its old branch remains in the code for a year. Nobody knows whether another environment, an old mobile client, or a background worker still depends on it. The difficult part of feature management is often the work after adding the boolean.

A flag should have an owner, purpose, type, scope, rollout policy, observation plan, and retirement decision. A durable workflow can track those obligations while agents perform investigations and prepare code changes. Routine progression can often be handled by the feature platform and deterministic rules.

## Start with the kind of flag

| Kind | Intended lifetime | What completion means |
| --- | --- | --- |
| Release flag | Temporary | Chosen behavior deployed, obsolete branch removed, flag retired |
| Experiment flag | Until evaluation is complete | Experiment decision recorded and follow-up implemented |
| Operational kill switch | Potentially long-lived | Ownership, defaults, and recovery procedure remain tested |
| Entitlement or product configuration | Potentially permanent | Supported configuration and authorization meaning remain explicit |
| Migration control | Bound to a migration plan | All required consumers and data reach the target state |

Do not apply one cleanup rule to all of these. A kill switch can be intentionally unused for a long time. An entitlement setting should not disappear because all current customers happen to receive the same value.

A flag also needs an evaluation context: user, tenant, request, device, or another stable unit. Select a unit that matches the behavior being changed. A tenant-level accounting feature can behave inconsistently if different requests within the same transaction take different paths.

## Give rollout an explicit state model

```text
Created -> Ready -> RollingOut -> Stabilizing -> Evaluated
RollingOut -> Paused or RolledBack
Evaluated -> CleanupReady -> CleanupInReview -> CleanupDeployed -> Archived
Any state -> NeedsDecision when required evidence is missing
```

The percentages are parameters, not the workflow itself. An illustrative sequence might expose one, five, twenty-five, fifty, and then one hundred percent of eligible tenants. Each transition needs enough evidence and a clear recovery action.

An example definition could include:

```yaml
flag: new-checkout
type: release
owner: checkout-team
assignment_unit: tenant
environments:
  - staging
  - production
stages_percent: [1, 5, 25, 50, 100]
guardrails:
  - payment_failure_rate
  - checkout_duration
business_review: checkout-outcome-plan
cleanup_condition: stable_and_recovery_window_closed
```

Actual thresholds, observation periods, and sample requirements depend on risk and traffic. A new color scheme and a payment-routing change should not inherit identical rollout policy simply because both use flags.

## Let the controller progress when the evidence is sufficient

The orchestrator can request a stage transition while the feature platform manages consistent assignment and exposure. Use the platform's tested allocation mechanism instead of implementing a new percentage algorithm in each agent.

| Evidence | Action under an illustrative policy |
| --- | --- |
| Required metrics are healthy and sample requirements are met | Advance one stage |
| Regression crosses the defined limit | Stop or restore the approved earlier configuration |
| Traffic is too low or telemetry is incomplete | Continue observing or request a decision |
| Business and operational metrics conflict | Investigate the trade-off |
| Full exposure is stable and required reviews are complete | Evaluate cleanup eligibility |

Missing telemetry is not a healthy signal. A flag can look successful because events stopped arriving. Monitor the measurement path, expected traffic, and data delays as part of rollout readiness.

Record the actual variation served with relevant outcomes. Stable cohort assignment and exposure data are necessary to interpret results. Check dependencies between flags and services; reverting one flag may not revert a dependent flag or undo a side effect already performed.

LaunchDarkly distinguishes [percentage, progressive, and guarded rollouts](https://launchdarkly.com/docs/fed-docs/home/releases/releasing). Guarded rollouts can monitor selected metrics and perform configured rollback. Its [management documentation](https://launchdarkly.com/docs/home/releases/managing-guarded-rollouts) also describes behavior for insufficient samples and dependent flags. Availability and exact behavior should be checked against the installed service and plan; these references were checked on 2026-10-29.

[OpenFeature](https://openfeature.dev/docs/reference/intro/) provides a vendor-neutral API specification for flag evaluation. That interface can reduce application coupling to a provider, but it does not supply the organization's ownership, rollout, or cleanup policy by itself.

## Treat flag changes as production changes

Changing targeting can expose new behavior without deploying a binary. Apply identity, audit, and approval rules to flag configuration as well as code. A coding agent that can edit every production flag has substantial operational authority even if it cannot deploy.

Use narrow operations with expected current state, allowed target stage, and an idempotency key. Reject stale requests if another controller or person changed the flag. Serialize competing rollout and incident actions. An emergency disable should have a defined relationship to ordinary scheduled progression so a timer cannot immediately re-enable the failed feature.

Test default behavior when the flag service is unavailable. Cached values, fallback values, and startup defaults affect both safety and what users experience. A flag name or boolean alone does not define that behavior.

## Full rollout is a milestone, not automatic retirement

Before cleanup, examine configuration across relevant environments and cohorts. Confirm that no tenant overrides, prerequisite flags, jobs, clients, or older deployments still require the alternative path. Define how long the rollback option must remain available.

The business evaluation can also affect cleanup. A stable feature may still be under an experiment, or the product owner may decide to change or remove it. Keep that decision connected to the feature's lifecycle rather than infer success from reaching one hundred percent (see [[Measuring Business Outcomes After Software Delivery]]).

An agent can prepare the cleanup investigation. It can search repositories, inspect active deployments, identify tests and configuration, and describe the behavior that should remain. Search both literal keys and wrappers or generated references. Absence from a text search is not proof that dynamically constructed references do not exist.

LaunchDarkly documents [flag archiving and restoration](https://launchdarkly.com/docs/home/flags/archive), including checks around use and readiness. Platform lifecycle signals can inform the investigation, but the application owner still needs evidence about consumers outside the platform's visibility.

## Make cleanup an ordinary verified code change

Consider this simplified C# example:

```csharp
if (await featureManager.IsEnabledAsync("NewCheckout"))
{
    await newCheckout.ProcessAsync(order);
}
else
{
    await oldCheckout.ProcessAsync(order);
}
```

After the new behavior is accepted and the old path is no longer supported, cleanup can remove the condition and call `newCheckout.ProcessAsync(order)` directly. The change may also remove obsolete dependencies, configuration, tests specific to the retired behavior, and monitoring that no longer answers a useful question.

Removing old tests is still a change to evidence. Route it through the acceptance policy with the retirement decision attached. Preserve tests for the behavior that remains and for relevant invariants. A cleanup agent does not receive a blanket exception to test protection.

Submit the cleanup candidate to normal review, integration tests, and deployment. Confirm that the deployed consumers no longer need the flag before archiving it. Retain the flag record and decision history according to policy. Deleting configuration too early can change the behavior of an old client that falls back to a different value.

## Keep cleanup compatible with recovery

Once the old branch is gone, disabling the flag may no longer restore the old behavior. Once the flag is archived, an old application release may use a fallback. Record how cleanup changes the recovery procedure.

For example, a release may be safe to roll back only while a flag record and old schema remain available. Close that window explicitly. The removal of those resources should invalidate earlier recovery claims rather than leave a stale "rollback supported" badge (see [[Production Feedback and Safe Automated Recovery]]).

If several services remove a flag independently, track the deployment of every relevant consumer. A merged cleanup pull request in one repository does not complete a distributed retirement.

## Make forgotten work visible

Track temporary flags past their expected retirement date, missing owners, rollout stages waiting on evidence, and cleanup changes waiting to deploy. Measure time spent in each state. A growing set of abandoned flags increases combinations to test and makes later code harder to understand.

Use a durable scheduler to trigger review or cleanup eligibility checks. The agent does not need to remember a date in a long-lived conversation. Failed cleanup attempts should leave a recorded blocker and next action, not silently reset the due date.

Repeated cleanup failures are process evidence. They may justify a better reference analyzer, a clearer rule for dynamically named flags, or changes to deployment ownership. Test such improvements through the harness evaluation process rather than automatically adding more instructions after every failure.

## Related notes

- **[[Designing an Agentic SDLC for Business Software]]** — Places flag work in a durable product lifecycle.
- **[[Acceptance Policies and Automated Repair in Agentic SDLC]]** — Governs code and test changes during cleanup.
- **[[Measuring Business Outcomes After Software Delivery]]** — Evaluates the value of the activated behavior.
- **[[Production Feedback and Safe Automated Recovery]]** — Connects flags to containment and release compatibility.
