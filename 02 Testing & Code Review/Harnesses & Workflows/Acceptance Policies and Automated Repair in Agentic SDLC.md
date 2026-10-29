---
title: Acceptance Policies and Automated Repair in Agentic SDLC
tags:
  - ai-agents
  - code-review
  - verification
  - agentic-workflows
  - safety
aliases:
  - Deterministic Acceptance for Agent Changes
  - Policy-Driven Agent Repair Loops
  - Protected Acceptance Criteria
---

# Acceptance Policies and Automated Repair in Agentic SDLC

An agent changes a billing rule, rewrites the failing test, and reports success. Every command may have completed correctly while the accepted business behavior disappeared. The acceptance process needs a protected reference, evidence about the candidate, and authority separate from the implementer.

The useful boundary is between proposing a change and authorizing its effects. Agents can explore several implementations and review code probabilistically. A policy engine can still make a repeatable decision from a fixed set of evidence and approvals.

## Be precise about what is deterministic

For the same candidate, policy version, recorded findings, and valid approvals, the decision function should produce the same result. That does not imply that running the entire review again will produce identical findings. Models, flaky tests, changing services, and time-dependent inputs can change the evidence.

Preserve the evidence used for a decision. Record the candidate and base commits, specification revision, policy revision, tool versions, environment, check status, and required approvals. A JSON schema can ensure that a reviewer returned the expected fields; it cannot establish that the review is correct.

Separate two operations: replaying the policy decision from recorded evidence, and performing a new verification run. The first supports auditability. The second may find a previously missed defect. A disagreement is information to investigate, not a reason to rerun reviewers until one accepts the patch (see [[Building Determinism from Unpredictable Models]]).

## Protect the meaning of acceptance

| Change or finding | Detection approach | Example policy response |
| --- | --- | --- |
| Deleted or weakened acceptance assertion | Test diff, test inventory, semantic review | Require approval of changed behavior |
| Disabled test, reduced fixture, or skipped suite | Runner configuration and coverage of required checks | Block or request an explicit exception |
| Public or intermodule contract change | Schema/API comparison and ownership map | Require the designated contract decision |
| Change spans module boundaries | Dependency analysis and changed paths | Increase verification scope or request review |
| Infrastructure or identity change | IaC plan, policy checks, permission diff | Separate infrastructure approval |
| Changed CI gate or review policy | Protected paths and trusted baseline | Separate policy change workflow |
| Normal implementation defect | Failed test or substantiated review finding | Return to the repair loop |

The exact policy is organization-specific. A cross-module change is a useful escalation signal, but file count alone is a weak risk model. A generated rename may span ten modules; a one-line authorization change may affect every customer. Start conservatively, then calibrate scope and ownership rules against observed failures.

Protect against test weakening as well as deletion. Replacing an assertion with a non-null check, excluding a difficult fixture, turning a real database test into a permissive mock, or changing the test command can preserve a green badge while removing evidence. Mutation testing and coverage can help investigate this, but neither proves that business intent survived.

A contract can change compatibly and still need ownership approval. Adding an optional field may preserve wire compatibility while changing data ownership or client expectations. Run compatibility analysis separately from the decision about who may approve a contract change. [oasdiff](https://www.oasdiff.com/) provides OpenAPI comparison, and [Buf breaking checks](https://buf.build/docs/breaking/) check Protobuf compatibility under selected rules.

The implementer may propose a policy change as a separate artifact. It must not use that proposal to accept its own current patch. Trusted verification should load policy and baseline tests from a protected revision or separate source. Running a script from the candidate checkout without checking whether the candidate changed it defeats the boundary.

## Combine executable checks with focused semantic review

Build, type checks, formatters, architecture tests, schema diffs, and repeatable integration tests should evaluate properties that tools can express precisely. AI can reduce the cost of creating custom Roslyn analyzers, AST checks, or dependency rules, but those checkers need their own positive and negative examples.

Semantic reviewers handle questions that remain difficult to formalize: whether a name hides a domain distinction, whether a direct SQL query bypasses a module contract, or whether a fallback silently changes business meaning. Give each reviewer a narrow question, relevant code, the governing rule, and accepted examples. Running one large prompt over every concern risks shallow coverage (see [[LLMs as a Code Review Team]]).

A different model can provide another perspective, but vendor diversity does not guarantee independent errors. Separate context, independent evidence gathering, and different verification methods matter too. A reviewer should demonstrate a suspected defect through a path, counterexample, or test when feasible. The original implementation summary is context, not proof.

Review routing also needs verification. If a router fails to request the authorization reviewer, every selected reviewer can pass while the important check never runs. Determine required check classes from trusted scope information and audit the selected set. Keep "not run," "not applicable," "failed," and "passed" distinct.

## Make domain naming an enforceable convention

A company may use `Customer`, `Account`, and `Subscriber` for the same concept in different services, or accidentally use `Customer` for three different concepts. A terminology reviewer needs a domain vocabulary with definitions, owning contexts, translations, and examples. It cannot solve the problem with a global word replacement.

For example, a billing account can represent a payer while a CRM customer represents a commercial relationship. Preserve that distinction. Require an explicit mapping where the concepts meet. Within a context, flag unexplained synonyms, inconsistent identifiers, and names that imply the wrong responsibility.

Mechanical naming rules belong in analyzers where possible: suffixes, forbidden dependency names, or required identifier types. Semantic checks can assess responsibility and meaning. After the company decides a recurring case, record the example and test the reviewer against it. Consistency should reduce reconstruction work, not force every module into an unsuitable architecture (see [[Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize]]).

## Return evidence that another executor can use

This illustrative report is an application contract, not a vendor API:

```json
{
  "task_id": "BILLING-142",
  "candidate": "candidate-commit-id",
  "base": "base-commit-id",
  "specification": "billing-refund-v3",
  "policy": "acceptance-v7",
  "check_id": "DOMAIN-017",
  "status": "failed",
  "finding_id": "refund-payer-mismatch",
  "severity": "blocking",
  "location": "Billing/RefundHandler.cs",
  "claim": "The refund can be assigned to a different payer.",
  "evidence": ["artifact:refund-payer-counterexample"],
  "expected_behavior": "Refund the payer recorded on the original payment.",
  "repair_scope": "Billing implementation and additional technical tests",
  "requires_decision": false
}
```

Validate required fields and references before using the report. A missing artifact or a timeout is not a passing check. The finding should describe the violated behavior, not force the fixer's first implementation choice. Attach enough context for a new agent to repair the problem without reading an entire earlier session.

The policy result can be `accept`, `repair`, `await_decision`, `blocked`, or `cancelled`. Derive it from evidence completeness, blocking findings, risk requirements, and approvals. If a test service is unavailable, retrying that service is different from asking the coding agent to rewrite correct code.

## Keep routine violations inside a bounded repair loop

When a finding is within the approved task, the orchestrator starts a repair using the pinned candidate and report. The repair produces a new candidate. Checks invalidated by the change run again, and any required integration gate still applies before acceptance. An old passing result is reusable only if its dependencies truly remain unchanged.

Track attempts by task and finding. Stop or escalate when the agent repeatedly returns to the same patch, alternates between incompatible fixes, exceeds cost or time limits, cannot reproduce the finding, or discovers that the required change exceeds its authority.

Avoid treating "three attempts" as a universal rule. A cheap compiler fix and a long migration test have different costs. Use explicit per-task limits and observe progress: a new failing case, a smaller reproducer, or a resolved dependency may justify another attempt. More explanation without new evidence may not.

| Situation | Appropriate next action |
| --- | --- |
| Clear implementation defect within scope | Repair and verify |
| Contradictory semantic findings | Compare evidence and governing rules; obtain another focused check if useful |
| Conflicting mandatory rules | Request a policy decision |
| Unavailable dependency | Retry or replace the environment under the existing policy |
| Changed acceptance meaning | Request approval of a revised specification or contract |
| Repeated patch oscillation | Stop automatic edits and present the conflict |

A semantic reviewer disagreement does not always need a human immediately. The orchestrator can seek a counterexample, check priority, or consult accepted cases. A human becomes necessary when evidence cannot resolve the issue within the allowed budget or the decision belongs to a person. [[Constraint Saturation and Rule Oscillation in Coding Agents]] covers the recurring-rule failure pattern.

## Make escalation a small, concrete decision

An escalation packet should say what decision is needed, why the automated path stopped, what behavior each option produces, which evidence supports it, and which earlier agreement would change. Include the attempted fixes and their failures so that the next person does not repeat them.

For example: "The refund policy requires the original payer, but the imported record has no payer identifier. Reject the refund, request manual resolution, or approve a documented fallback?" That is more useful than "review failed; please inspect 27 files."

Human approval should bind to the relevant behavior, evidence, and candidate scope. It should expire or require reconsideration when a later patch changes what was approved. Record an exception with a reason and owner; do not bury it in an unstructured comment that the next automated run cannot interpret.

## Verify the combined result before integration

Independent branches can each pass while their combination fails. Recheck the merge candidate against the required base or integration queue. Contract changes, migrations, and shared vocabulary are particularly vulnerable to this problem.

Separate merge permission from deployment permission. Acceptance of code does not imply that an agent may modify production infrastructure. A trusted delivery controller can consume the accepted artifact and enforce release-specific conditions. Recovery tests and rollout conditions belong in that decision as well (see [[Production Feedback and Safe Automated Recovery]]).

## Develop the policy catalog as software

Every rule needs a purpose, scope, owner, evidence requirements, severity, and examples of both violations and acceptable cases. Measure false findings, missed defects, repair attempts, and decision cost. A rule that produces constant noise can undermine the whole review process.

AI can draft new checks from repeated failures. Validate them on representative historical and held-out changes before enforcing them. Keep evaluation criteria protected from the system proposing optimizations. A cheaper process that accepts broken changes is a regression (see [[Observability and Controlled Improvement of Coding Agent Harnesses]]).

## Related notes

- **[[Designing an Agentic SDLC for Business Software]]** — Places the acceptance process within the whole product lifecycle.
- **[[Executable Architecture Tests for Coding Agent Guardrails]]** — Makes structural boundaries executable.
- **[[Reviewing AI-Generated Code]]** — Presents meaningful evidence when a person must make the decision.
- **[[Agentic Coding Harness and Controlled Development Workflows]]** — Provides the execution loop and repository workflow around the policy.
