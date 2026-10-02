---
title: Large-Scale Code Migration with AI Agents
tags:
  - ai-agents
  - migration
  - refactoring
  - software-engineering
  - testing
  - economics
aliases:
  - AI-Assisted Language Migration
  - Porting Large Codebases with Agents
  - Agent-Driven Code Migration
---

## Translation Becomes Cheaper, but the Migration Still Needs an Owner

AI agents can make it practical to move a substantial codebase to another language or runtime. They can inspect dependencies, translate modules, repair compilation errors, run comparisons, and review changes. This lowers the cost of producing a port; it does not automatically settle which behavior must survive, how the intermediate system ships, or who maintains the result.

The distinction matters economically. A rewrite may become worthwhile because it removes runtime overhead or enables a deployment model that the original implementation could not support. [[AI May Make Aggressive Code Optimization Economically Viable]] explains that performance argument. A migration can also improve maintainability, but translation and cleanup need separate acceptance criteria.

## What the Published Cases Actually Demonstrate

GitHub reports moving roughly 430,000 lines of production TypeScript in the Copilot runtime to Rust over about 14.5 weeks. The work produced 128 port PRs while the CLI continued to ship, including 35 stable releases. This was the runtime migration, not a claim that every part of Copilot became Rust. GitHub reports approximately $120,000 in attributed model usage; that figure is not an itemized total project cost. [GitHub's migration account](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)

Anthropic describes a weekend conversion of a Python library into roughly 165,000 lines of TypeScript. The account also describes discarded attempts before the successful third run and several later nights of testing. Its separate Bun migration passed the existing suite before merging, yet required fixes for 19 subsequent regressions. The headline production window therefore describes only part of the engineering effort, and passing the suite did not establish complete equivalence. [Anthropic's migration account](https://claude.com/blog/ai-code-migration)

These are evidence that large translations can be accelerated. They do not establish a universal cost per line, an unattended workflow for arbitrary repositories, or a result available within any particular consumer subscription.

## First Make the System Divisible

Consider moving an order calculator from TypeScript to Rust. Its arithmetic may look isolated, while its actual behavior depends on database reads, a mutable discount cache, currency rounding, callbacks, and the ordering of emitted events. Translating the arithmetic alone does not define a replaceable component.

Start with a dependency inventory: imports, callers, exported APIs, shared state, external effects, and configuration-dependent entry points. Deterministic tools can construct graphs and identify cycles. An agent can explain a cycle and propose a cut, but a static graph may miss reflection, runtime registration, consumers outside the repository, or a dependency through shared data.

For the calculator, a useful preparation step might keep the TypeScript behavior intact while extracting a pure calculation from database access. The boundary then receives explicit inputs and returns a result. The migration must still define numeric representation, error handling, cancellation, ownership of memory, and any callback lifetime across the language boundary.

If the agent cannot describe a boundary without unresolved shared state, the next task is a smaller refactoring in the original language. It might isolate cache ownership or replace an ambient dependency with an explicit input. This preparation is real migration work, even though it produces no target-language code. [[Refactoring Legacy Systems with AI Agents]] develops this incremental approach.

## Planning Can Be Automated Within Explicit Constraints

A practical planner can propose stages from the dependency graph: portable leaf functions first, stateful components next, and orchestration after the components it calls. A strongly connected group is a candidate for joint migration or preparatory separation; it is not proof that either option is safe.

Each proposed task needs a contract that another worker can execute and a reviewer can assess:

| Part of the task | Example for the order calculator |
|---|---|
| Scope | Calculation module and its boundary adapter |
| Prerequisites | Input model and rounding policy already defined |
| Preserved behavior | Results, errors, rounding, and event order |
| State and effects | No database writes inside the calculation |
| Verification | Original fixtures, differential cases, integration checks |
| Completion | Accepted port, adapter tests, and recorded remaining gaps |

The planner can revise this plan after discovering a hidden dependency. That revision should be explicit: a new prerequisite, a wider component boundary, or a task that requires an architectural decision. Quietly editing neighboring modules to make a local test pass defeats the partitioning.

Humans need not approve every translated expression. They do need to own uncertain behavior, architecture changes, deployment decisions, and acceptance of the verification strategy. GitHub's account describes both agents organizing substantial subwork and engineers directing boundaries and reviewing sensitive changes. That is a useful model for bounded autonomy, rather than evidence that supervision became unnecessary. [GitHub's migration account](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)

## The Framework Is More Than a Collection of Prompts

The execution layer needs isolated workspaces, bounded write scopes, prerequisite tracking, a place to record unresolved differences, and an integration owner. Separate workers can translate independent components. A reviewer compares behavior; the integration process establishes whether accepted components still work together.

Shared resources also need coordination. Several workers compiling a large workspace simultaneously can exhaust memory and make apparent productivity disappear into failed builds. A build queue with an enforced lease is stronger than asking agents to take turns. Likewise, protected baseline fixtures and write permissions enforce boundaries more reliably than a reminder in a prompt.

Independent review helps find different mistakes, but several agents can share the same mistaken interpretation. Compilation, regression tests, replay comparisons, architecture checks, and human decisions supply different kinds of evidence. A successful review conversation alone is not a release gate.

## A Mixed Implementation Can Be a Released Product

During an incremental migration, one component can run in Rust while another still runs in TypeScript. They cooperate through a boundary; they do not necessarily run two implementations of every request.

GitHub used native interop and thin TypeScript wrappers to replace components incrementally, and shipped public CLI releases during that mixed period. The mixed system was therefore more than an internal test artifact. [GitHub's migration account](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)

For a proposed migration, define who owns state on either side, how failures cross the boundary, and how to roll back a released component. Give each temporary adapter an owner and a removal condition. The condition includes consumers and operational readiness, not merely a passing unit test.

Differential execution is a separate technique: feed the same inputs to old and new implementations and compare observable results. Stateful operations need captured inputs and isolated effects. Sending both implementations a live payment or database mutation would change the system being measured. [[Testing in the Model, Agent, LLM Era]] explains the limits of such comparisons.

## Tests Preserve Observations, Not Every Line of the Original

A test suite does not require a translated program to retain dead branches, redundant intermediates, or the original decomposition. Several old functions may become one clearer expression while preserving every asserted result. Conversely, an agent may copy unnecessary code faithfully because it was asked for close semantic translation.

Passing tests cannot tell us how much irrelevant code disappeared. It also cannot distinguish an irrelevant branch from a rare behavior that the suite never exercised. Source comparison, dependency analysis, runtime observations, and an explicit decision about retired behavior answer different questions.

An odd behavior may be an accidental bug, or it may be compatibility that a consumer depends on. Preserve it during a behavior-preserving port until someone accepts changing it. A later cleanup can deliberately remove it with a separate rationale and checks. Do not let a failed migration test become permission to weaken the baseline.

This leaves room for substantial simplification, but makes it reviewable. [[AI Changes the Economics of Technical Debt]] addresses recurring cleanup; [[Refactoring Legacy Systems with AI Agents]] covers local transformations and deletion evidence.

## Count Preparation, Failed Attempts, and Maintenance

The cost of a successful translation run is only one part of the decision:

```text
total migration cost =
    reconnaissance and boundary preparation
  + harness, toolchain, and verification setup
  + experiments, discarded attempts, and model usage
  + compute, integration, review, and rollout
  + later maintenance of the port and its tooling
```

Record elapsed time separately from human effort and model expenditure. Cached input, parallel workers, retries, and builds also make token totals a poor substitute for a bill. When a report does not itemize preparation or infrastructure, keep those costs unknown rather than assuming they were negligible or enormous.

An early pilot should test the whole workflow on one representative boundary: translate, verify, integrate, ship or rehearse deployment, and maintain one subsequent change. A leaf helper alone may demonstrate syntax translation while missing the costs that dominate the real project.

## After the Port, Choose Where Future Changes Live

There are three distinct ownership models. None follows automatically from the ability to translate code:

| Model | How subsequent changes arrive | Continuing work |
|---|---|---|
| Target language becomes canonical | Features and fixes are implemented in the port | Maintain target-language design, tests, and tooling |
| Maintained fork follows upstream | Select relevant upstream changes and adapt them | Track versions, review semantic differences, resolve drift |
| Source remains canonical | Regenerate a target implementation for accepted source revisions | Maintain translation rules, verification, and release artifacts |

Regeneration on every release is a possible workflow, not a default consequence of these case studies. It needs a reliable way to detect changed behavior, preserve intentional target-specific choices, and reject incomplete output. Small upstream changes may instead be translated incrementally.

For regeneration, retain the accepted output and a release record: source revision, translation rules, tool and model versions, verification results, and reviewed exceptions. A later run may produce different code. Fixes made only to disposable output can vanish unless the source or translation process also captures them.

For a canonical port, engineers may use agents extensively to implement features, but ownership still includes design, review, debugging, and acceptance. An account saying that new development moved to Rust does not tell us whether people typed each feature or delegated its implementation.

The right choice depends on the product. An internally owned runtime can change its canonical language; a compatibility port of an active external library must account for future upstream releases. [[AI Changes the Economics of Software Libraries]] connects that continuing obligation to the economics of reuse.

## Related Notes

- [[AI May Make Aggressive Code Optimization Economically Viable]] — When migration or specialization can repay its full cost through lower resource use.
- [[Refactoring Legacy Systems with AI Agents]] — Preparing boundaries, performing local cleanup, and comparing behavior.
- [[AI Changes the Economics of Technical Debt]] — Using agent capacity for recurring maintenance without producing more debt.
- [[Testing in the Model, Agent, LLM Era]] — Protecting behavioral baselines and interpreting successful checks.
- [[AI Changes the Economics of Software Libraries]] — Port ownership, upstream changes, and the continuing value of shared maintenance.
