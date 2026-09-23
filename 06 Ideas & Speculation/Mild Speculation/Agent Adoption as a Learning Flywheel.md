---
title: Agent Adoption as a Learning Flywheel
tags:
  - ai-agents
  - agent-adoption
  - organizational-learning
  - feedback-loops
  - flywheel-effect
aliases:
  - Agent Adoption Flywheel
  - Organizational Learning with Agents
---

## Core idea

When people attempt to use an AI agent for a task that current models cannot perform reliably, those attempts may help make the task feasible for future models.

The important shift is that future training data will increasingly contain not only:

- human-written code,
    
- documentation,
    
- tutorials,
    
- final solutions,
    

but also complete interaction trajectories:

- what the user wanted to achieve,
    
- what the model attempted,
    
- where it failed,
    
- which tools it used,
    
- what feedback it received,
    
- how the result was corrected,
    
- and which final outcome was accepted.
    

This creates a feedback loop between model adoption and model capability.

> Today's unsuccessful attempts to use agents can become part of the infrastructure and training signal that makes tomorrow's agents successful.

---

## The self-reinforcing cycle

The process may look like this:

```text
People expect agents to automate task A
→ they try to automate task A with an imperfect model
→ the model fails in observable ways
→ users correct it and build supporting tools
→ new examples, evaluations, and workflows are created
→ future models learn from these patterns
→ task A becomes more reliable
→ more people begin using agents for task A
→ even more useful data is generated
```

In that sense, agent adoption can resemble a self-fulfilling prophecy.

People act as though a task will eventually become automatable. Their attempts create the conditions that make the automation possible.

However, it is not magic and it is not a prophecy in the literal sense. The improvement comes from real work:

- experimentation,
    
- feedback,
    
- evaluation,
    
- process formalization,
    
- tool development,
    
- and environmental adaptation.
    

---

## Why trying matters

If nobody attempts to delegate a particular task to an agent, relatively little data is created about:

- how users naturally describe the task,
    
- which context the agent usually lacks,
    
- what mistakes occur most often,
    
- which actions must be performed,
    
- what a successful result looks like,
    
- when human escalation is necessary.
    

A future model may become more intelligent in general, but it will still struggle with a process that has never been clearly exposed, described, tested, or instrumented.

Therefore:

> A model cannot learn a real operational workflow only from the abstract idea that such a workflow exists.

Someone must attempt it.

The early attempts may be inefficient, but they reveal the hidden structure of the task.

---

## From static artifacts to execution trajectories

Traditional training data usually contains static artifacts:

```text
problem → final solution
```

Agent interactions can provide a much richer structure:

```text
goal
→ initial plan
→ attempted action
→ tool output
→ failure
→ diagnosis
→ correction
→ verification
→ accepted result
```

For example, an early model may be asked to perform a software migration.

Its first attempt may:

- update only part of the code,
    
- break backward compatibility,
    
- miss deployment configuration,
    
- fail tests,
    
- require several human corrections.
    

The full interaction can reveal a better strategy:

1. inspect dependencies,
    
2. identify compatibility constraints,
    
3. introduce a transitional version,
    
4. migrate callers incrementally,
    
5. run tests,
    
6. deploy safely,
    
7. remove the old path later.
    

A future model may learn the general structure of this migration, rather than merely memorizing the final patch.

---

## Verification is the key

Model-generated data is not automatically useful.

A model generating code and then declaring that its own code is correct provides a weak learning signal.

A dangerous loop is:

```text
model generates output
→ the same model judges the output
→ the output is accepted without external verification
→ future models train on the result
```

This can reinforce:

- hidden bugs,
    
- shallow reasoning,
    
- stylistic uniformity,
    
- incorrect assumptions,
    
- and plausible but unverified solutions.
    

A stronger loop uses external evidence:

```text
model generates several solutions
→ compiler rejects invalid ones
→ tests reject incorrect ones
→ benchmarks reject inefficient ones
→ security analysis rejects unsafe ones
→ humans review architectural decisions
→ verified solutions are retained
```

The crucial resource is therefore not only generated data.

It is **generated data combined with a reliable quality signal**.

Useful verification mechanisms include:

- compilation,
    
- automated tests,
    
- integration tests,
    
- formal verification,
    
- static analysis,
    
- security scanning,
    
- performance benchmarks,
    
- production monitoring,
    
- user acceptance,
    
- expert review.
    

---

## The model does not learn only from success

Failures can be highly valuable when they are properly labeled.

A useful failed trajectory contains:

```text
attempt
→ observable failure
→ explanation or diagnostic signal
→ correction
→ successful verification
```

This teaches more than a clean final answer because it exposes:

- common wrong approaches,
    
- misleading assumptions,
    
- missing context,
    
- recovery strategies,
    
- and decision points.
    

An unlabeled failure is much less useful.

If the user accepts broken code, or if nobody checks whether the task worked, the resulting data may train future systems in the wrong direction.

---

## The hidden value of early adopters

Organizations that start using agents early may initially pay a higher cost.

They must:

- supervise agents,
    
- correct mistakes,
    
- create integrations,
    
- improve documentation,
    
- build tests,
    
- define escalation paths,
    
- and redesign some processes.
    

An organization that waits may later gain access to a much stronger model without paying all of those early experimentation costs.

However, the waiting organization may still lack:

- machine-readable documentation,
    
- well-defined workflows,
    
- internal evaluations,
    
- acceptance tests,
    
- safe execution environments,
    
- reusable agent tooling,
    
- knowledge of where agents can be trusted.
    

An early adopter may eventually possess:

```text
better future model
+ prepared environment
+ internal task history
+ verified workflows
+ company-specific evaluations
+ known failure modes
```

The long-term advantage may come less from access to a unique model and more from having prepared the organization to use models effectively.

$$\text{Organizational Capability} = \text{Frontier Model} + \text{Execution Harness} + \text{Verified Domain History} + \text{Automated Oracles}$$

When foundation models are commoditized via API, model weights cease to be an organizational moat. The durable advantage is the internal substrate: an execution harness where agents can run, fail safely in isolated sandboxes, and be verified deterministically against proprietary business invariants.

---

## The environment also becomes easier for agents

Progress happens along two separate curves.

## 1. Models become more capable

Models improve at:

- reasoning,
    
- planning,
    
- long-context understanding,
    
- tool use,
    
- error recovery,
    
- code generation,
    
- multimodal input,
    
- and autonomous execution.
    

## 2. The world becomes more agent-friendly

Humans redesign systems to make them easier for agents to operate.

Examples include:

- stable APIs,
    
- MCP servers and similar interfaces,
    
- structured documentation,
    
- explicit schemas,
    
- machine-readable runbooks,
    
- automated tests,
    
- sandbox environments,
    
- observable workflows,
    
- declarative infrastructure,
    
- clear repository boundaries,
    
- structured logs,
    
- deterministic build processes.
    

A future agent may succeed not only because the model is smarter, but also because the environment has been made more legible and controllable.

---

## Agent failure often reveals process failure

An agent may appear incapable of executing a company process because the process itself is poorly defined.

The process may depend on:

- undocumented knowledge,
    
- intuition of one senior employee,
    
- hidden exceptions,
    
- inconsistent naming,
    
- informal approvals,
    
- manual access to multiple systems,
    
- unclear success criteria.
    

Trying to automate the process forces the organization to answer:

```text
What is the input?
What is the desired output?
Which rules apply?
Which exceptions exist?
How do we detect success?
How do we detect failure?
When must a human intervene?
```

Therefore, attempting to use an agent is also a method of process discovery.

The organization does not only teach the agent how to perform the task.

It discovers what the task actually is.

---

## Software development is particularly suitable

Code is especially useful for this learning loop because many properties can be checked automatically.

A generated change can be evaluated by asking:

- Does it compile?
    
- Do existing tests pass?
    
- Does it preserve the public API?
    
- Does it introduce regressions?
    
- Is it faster?
    
- Does it use less memory?
    
- Does it pass security analysis?
    
- Does it conform to architectural boundaries?
    

This makes software development a strong environment for synthetic training data and iterative agent improvement.

The human does not necessarily need to manually write the final code.

The human can instead provide:

- requirements,
    
- constraints,
    
- tests,
    
- architecture,
    
- review,
    
- and acceptance criteria.
    

---

## The most valuable artifact may not be code

In an agent-driven development process, the highest-value human contribution may shift away from writing every implementation detail.

More durable assets may include:

- precise specifications,
    
- executable tests,
    
- architecture decisions,
    
- benchmark suites,
    
- examples of expected behavior,
    
- failure classifications,
    
- migration constraints,
    
- rollback procedures,
    
- and acceptance criteria.
    

A useful task record could contain:

```text
task description
repository state before the change
model-generated patch
compiler output
test results
benchmark results
review comments
final accepted patch
production outcome
```

This is more valuable than storing only the final code because it captures both the solution and the path used to validate it.

In practice, a structured task record captures the full execution trajectory:

```json
{
  "task_id": "MIGRATE-AUTH-0042",
  "base_commit": "a1b2c3d4",
  "prompt": "Migrate internal token validation to standard OAuth2 JWT verification across user-service",
  "agent_trajectory": [
    {
      "step": 1,
      "thought": "Inspect existing auth middleware and parse token verification logic.",
      "tool_call": "read_file",
      "arguments": { "path": "src/middleware/auth.go" },
      "result": "package middleware\nimport (...)"
    },
    {
      "step": 2,
      "thought": "Update JWT parsing to use standard jwt-go library.",
      "tool_call": "edit_file",
      "arguments": { "path": "src/middleware/auth.go", "diff": "..." },
      "result": "File updated successfully."
    },
    {
      "step": 3,
      "thought": "Run unit test suite to verify token parsing.",
      "tool_call": "run_command",
      "arguments": { "command": "go test ./src/middleware/..." },
      "result": "FAIL: TestTokenValidation - signature invalid: key format mismatch"
    },
    {
      "step": 4,
      "thought": "The public key parsing logic expects PEM-encoded blocks. Update key loader.",
      "tool_call": "edit_file",
      "arguments": { "path": "src/middleware/keys.go", "diff": "..." },
      "result": "File updated successfully."
    },
    {
      "step": 5,
      "thought": "Re-run unit tests.",
      "tool_call": "run_command",
      "arguments": { "command": "go test ./src/middleware/..." },
      "result": "PASS: ok  user-service/src/middleware 0.42s"
    }
  ],
  "human_review": {
    "approved_by": "lead-architect",
    "notes": "Good recovery on key parsing. Added defensive error handling on missing headers."
  },
  "final_commit": "e5f6a7b8"
}
```

These structured traces capture the initial context, the compiler or test failure, the diagnostic reasoning, and the verified resolution. Retaining multi-step execution logs turns everyday developer corrections into high-signal datasets for internal fine-tuning, retrieval-augmented prompt harnesses, and regression test suites.

---

## A more realistic model of progress

The naive expectation is:

```text
current agent cannot do the task
→ wait for a better model
→ future agent magically succeeds
```

A more realistic process is:

```text
current agent cannot do the task
→ people try anyway
→ failures expose missing context
→ processes are formalized
→ tests and tools are added
→ successful trajectories are recorded
→ future models improve
→ the environment becomes easier to operate
→ the task becomes reliable
```

Future capability is therefore produced jointly by:

- better foundation models,
    
- accumulated interaction data,
    
- external verification,
    
- improved tooling,
    
- and redesigned organizational processes.
    

---

## Important limitation

An individual user should not assume that every conversation or correction automatically trains the next generation of models.

For a particular interaction to contribute, several things must happen:

1. the data must be available for training,
    
2. the task and outcome must be interpreted correctly,
    
3. privacy and licensing constraints must allow its use,
    
4. the failure and success signals must be extracted,
    
5. the example must be selected as useful training material.
    

The broader effect is therefore statistical and ecosystem-wide, rather than a guaranteed direct relationship between one user's correction and a future model.

Even when public foundation models cannot train on proprietary logs due to data retention policies or licensing constraints, the flywheel still operates inside the organization. Engineering teams capture this value locally:

- Hardening internal CI/CD pipelines and isolated sandbox harnesses.
- Building domain-specific fine-tuning datasets tailored to private APIs and architectural patterns.
- Curating golden evaluation suites to benchmark new model releases against real internal regressions.

---

## Practical conclusion

It makes sense to experiment with agents before they are fully reliable, but the experiments should create durable value even when the agent fails.

A good experiment should leave behind:

- clearer documentation,
    
- better tests,
    
- explicit process rules,
    
- reusable tools,
    
- recorded failure modes,
    
- structured task histories,
    
- or improved architecture.
    

This avoids a situation where the user performs expensive trial-and-error work that benefits only the model provider or the wider industry.

The best early adoption strategy is:

> Use today's imperfect agents to improve both the task and the environment in which tomorrow's agents will operate.

---

## Mental model

```text
Trying creates data.
Failures expose structure.
Verification creates truth.
Truth improves training.
Better models increase adoption.
Adoption creates more data.
```

Or more compactly:

> Agents will not become capable merely because we wait.  
> They become capable partly because people try, fail, verify, formalize, and try again.

## Related Notes

- [[The 5-Layer System Stack for Agentic Software Engineering]] - Layer 5: Compounding organizational knowledge and flywheel economics.
- [[Competitive Advantage in the Age of Commodity AI]] - Where defensibility lives when model intelligence is commoditized.
- [[What Should Organizations Preserve from AI-Assisted Development]] - Capturing negative trajectories, review comments, and domain invariants.
- [[The Most Valuable Software Training Data May Be Private]] - The strategic value of proprietary corporate execution history.
- [[Learning Coding Agents Through Failure-Driven Instructions]] - Turning agent execution breakdowns into durable constraints.
- [[Improving AI Models - From Scaling to Agent-Generated Training Data]] - Harnessing execution feedback to train frontier models.
