---
title: Configuring and Testing Coding Agent Capabilities
tags:
  - ai-agents
  - agentic-harness
  - agent-configuration
  - software-engineering
  - testing
aliases:
  - Agent Capability Configuration
  - Testing Agent Rules and Skills
  - Agent Hooks and Audits
  - Steering Agents via Negative Boundaries
  - Negative Bounding in Agent Workflows
---

# Configuring and Testing Coding Agent Capabilities

As agent roles, skills, rules and tools multiply, a shared configuration becomes harder to inspect. The practical question is which capabilities an agent receives for a task, how it chooses them, and how to verify that the intended checks still run. This note focuses on that configuration; [[Agentic Coding Harness and Controlled Development Workflows]] covers the surrounding development process.

## Keep agent configuration scoped as it grows

A small repository can keep agents, rules, skills, workflows and tools in shared locations. An agent may have its own instructions while every skill and rule still sits in a common pool. As the pool grows, it becomes harder to tell what applies to a task, which agent can use which tool, and why a particular procedure ran. Split the configuration into smaller scopes: by agent role, kind of task, project or directory, whichever boundary reflects the work. Each scope needs clear instructions, relevant procedures and appropriate tool permissions. Moving files into separate folders alone does not establish these boundaries; the agent host must load and enforce the intended configuration.

Some systems package a scope as a plugin containing agents, rules, skills, workflows and tool access. Tools may include external MCP services as well as functions built into the host, such as searching files. Other systems expose different configuration units. The useful question is the same: what is available to this agent for this task, and what may it actually do?

Selection can be explicit: a task or workflow names the agent, rule or skill to use. It can also depend on descriptions that the agent matches to the current request. A good description improves the odds of selection, but does not guarantee it. Rules may be loaded for every task in a scope or only when a file or request matches; the exact controls vary by product. The configuration should make these choices inspectable rather than relying on a large shared pool and hoping the agent picks correctly.

Keep natural-language rules short enough to guide decisions the agent must make. Detailed instructions for every mechanical edge case can compete for attention and produce the rule overload described in [[Constraint Saturation and Rule Oscillation in Coding Agents]]. Short does not mean vague: a rule still needs a clear intent and scope. Put repeatable, measurable details in executable checks instead of asking the agent to remember them all.

## Steering agents via negative boundaries

A frequent mistake in repository instructions is prescriptive over-specification—attempting to dictate every internal method, variable name, and design decision in advance.

### The leaky nature of affirmative instructions

Affirmative instructions are inherently leaky: telling an agent what it *should* do does not stop it from doing everything else.

If you instruct an agent: *"Use the command pattern to handle this request"*, the model may follow that instruction while also introducing reflection, allocating large heap buffers inside a tight audio loop, or wrapping operations in generic `catch (Exception ex)` blocks. Affirmative instructions guide probability, but they leave an unbounded operational surface.

### Bounding by exclusion

A more reliable approach pairs wide implementation freedom with rigid negative boundaries (see [[Negative Knowledge and Explicit Architectural Dissents]]):

1. **Grant Implementation Latitude**: Allow the agent to choose local data structures, helper functions, and algorithm details within the target module scope.
2. **Erect 2–3 Explicit Negative Fences**: Clearly define forbidden anti-patterns:
   - Forbidden: Adding external package dependencies without prior approval.
   - Forbidden: Mutating database schemas or public API contracts in this task slice.
   - Forbidden: Introducing heap allocations, dynamic dispatch, or blocking I/O inside synchronous hot paths.
3. **Outcome**: The agent retains the flexibility to solve edge cases without getting stuck in brittle, over-specified prompts, while your architectural invariants remain protected against drift.

## Reusable agent skills

When a workflow is repeated frequently, it can become a skill rather than a long prompt.

```text
.agents/skills/implement-approved-step/
├── SKILL.md
├── references/
│   └── plan-template.md
└── scripts/
    └── verify.ps1
```

Example procedure:

```markdown
1. Read AGENTS.md, SPEC.md and PLAN.md.
2. Find the first approved step.
3. Confirm that its completion criteria are measurable.
4. Add or update tests.
5. Implement the minimal production change.
6. Run the specified verification.
7. Review the diff against the specification.
8. Mark the step completed only when all criteria pass.
9. Stop; never begin the next step automatically.
```

Skills remain mostly text, but they can also contain scripts, templates, examples and reference material.

### Skills as Native Code Functions (Beyond Shell Commands)

While agents can run terminal commands, building skills as native code functions (e.g. in Python or C#) provides:
1. **Pre-filtering Context (AST Parsers):** Instead of dumping a 3,000-line file into context, a native skill uses `ast` or `tree-sitter` to extract only the target class or method signature.
2. **Direct SDK Integration:** Interacting with GitHub (`PyGithub` / Octokit), cloud providers (`boto3`, Azure SDK), or databases directly avoids fragile CLI stdout parsing.
3. **Deterministic Sandboxing:** Skills can manage local Docker containers or ephemeral in-memory databases to validate migrations without side effects.

## Deterministic tools should enforce deterministic rules

Rules and audits have different jobs. A rule tells the agent how to approach the work; it influences the choices the model makes, but cannot guarantee that the model remembers or follows every instruction. An audit examines what the agent actually did. For example, a short rule can say, "Keep the domain layer independent of infrastructure." The agent uses that boundary while designing a change. An architecture test checks the resulting dependencies and reports a violation if an import crosses the boundary.

The audit can be repeatable and deterministic when it uses an executable check with a defined input and pass/fail result. This does not make the agent's whole task deterministic: the check only covers the property it measures. A model-based review of clarity or design may still be useful, but its judgment is not the same kind of mechanical gate. An LLM should not replace tools that can check a rule exactly.

| Concern | Preferred mechanism |
| --- | --- |
| Formatting | `.editorconfig` and formatter |
| Compiler warnings | `Directory.Build.props` |
| Module boundaries | architecture tests or static analysis |
| Unit and integration behavior | automated tests |
| Test quality | mutation testing |
| Dependency vulnerabilities | security scanner |
| Secret detection | secret scanner |
| Approval and design decisions | human plus specification |
| Planning and diagnosis | LLM agent |

The principle is:

> If a rule can be checked deterministically, let a deterministic tool check it. Use the LLM to interpret, plan and repair.

### Use hooks to make the audit run

A check sitting in a repository does nothing until something invokes it. A hook ties the audit to a defined event, so running it does not depend on the agent remembering an instruction such as "run verification before you finish." A Git `pre-commit` hook can run a validator before Git creates a commit and reject that commit when the check fails. It protects that commit boundary, but an agent may work through several edits without committing. Other triggers can check work sooner or after a larger unit of work:

- **Before an action:** validate or block a tool call before it can change state.
- **After a file write:** run a check relevant to that file, such as a formatter or note validator. A write event does not mean the agent has finished editing: it may make several writes, and an intermediate file may be incomplete. Either keep this check fast and tolerant of intermediate state, or collect changed paths and check them at a later task boundary.
- **After an agent task or turn:** check the accumulated diff and report failures even if no commit was made. Define the boundary in the host rather than assuming the end of a conversation is a reliable event.
- **On a schedule:** run periodic checks for drift that may appear between active tasks. This is usually a scheduled job rather than a lifecycle hook, but follows the same trigger-and-action pattern.

These checks provide feedback at different times. The host can make a failed audit block completion or return the failure to the agent for repair. If a hook only logs a warning, it provides visibility but does not enforce the rule. A post-action check can detect a bad change; it cannot undo an irreversible action that already ran. Keep prohibitions that must hold before execution at a pre-action gate or permission boundary (see [[Security Boundaries for Agents, RAG, and MCP]]). Test the trigger itself as well as the check: a correct validator is no help if the expected file write or task completion never invokes it.

### Test the configuration and the audit path

After changing an agent, rule, skill, permission or hook, run small representative tasks in an isolated workspace. For each task, record the expected selection, allowed tools, forbidden actions, expected hook events and required audit result before running the agent. Then inspect the trace, changed files and check output. The final answer alone cannot show whether the correct skill ran or whether a hook silently failed to fire.

Cover both expected use and unwanted activation:

- A task that needs a specialist agent or skill should select it and stay within its tool permissions.
- A similar task outside that scope should not select it or load unrelated rules.
- A changed file should invoke its relevant check at the configured boundary; an unrelated file should not invoke a costly check unnecessarily.
- A deliberately invalid change should make the audit fail and produce a visible failure or block completion, according to the intended policy. A valid change should pass.
- A task without a commit should still invoke any task-level audit; a commit should invoke its Git hook.
- A scheduled audit should run at its configured interval and report a deliberately stale artifact.

Keep these scenarios and rerun them after configuration changes. For description-based selection, try several realistic phrasings, including ambiguous and negative cases, because one successful prompt does not establish reliable routing. An executable audit can give a deterministic answer to a defined check, but the test must also prove that the right event invokes it and that a failed result has the intended effect. A Python-based runner can automate the scenarios and collect traces; the important artifact is the expected-versus-observed behavior, not the runner's language.

## Related notes

- **[[Agentic Coding Harness and Controlled Development Workflows]]** — The bounded implementation and review process in which this configuration runs.
- **[[Constraint Saturation and Rule Oscillation in Coding Agents]]** — Why detailed rule lists can compete for the agent's attention.
- **[[Building Determinism from Unpredictable Models]]** — What the host must enforce and when verification belongs in the work loop.
- **[[Learning Coding Agents Through Failure-Driven Instructions]]** — Improving instructions with repeated task evaluations.
