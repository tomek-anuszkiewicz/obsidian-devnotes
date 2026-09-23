---
title: Fresh Contact With Reality May Become the Training Bottleneck
tags:
  - training-data
  - synthetic-data
  - model-training
  - empiricism
  - ai-scaling
  - epistemology
aliases:
  - Reality Bottleneck in AI Training
  - Contact with Reality vs Synthetic Loops
---

As language models consume more of the existing human knowledge corpus, the limiting resource for future training may gradually change.

The problem may no longer be:

> How do we obtain more tokens?

It may become:

> How do we obtain genuinely new information that previous models could not already reconstruct?

The Internet can continue producing enormous quantities of text while adding relatively little new knowledge.

Especially as AI-generated content becomes common, a growing fraction of new text may follow a loop such as:

```text
existing knowledge
→ LLM
→ reformulation
→ publication
→ another LLM
→ another reformulation
```

The number of tokens grows.

The amount of independent information does not necessarily grow at the same rate.

This suggests that **fresh contact with reality** may become one of the scarce resources in model training.

A closed synthetic loop that feeds model outputs back into subsequent training runs without external verification inevitably drifts. Without hard friction against external systems, the learning process risks recycling its own assumptions, amplifying subtle hallucinations, and narrowing diversity. Token volume explodes, but independent entropy collapses.

---

## Models Ultimately Need Someone to Discover Something

A model can:

- combine known ideas,
    
- search existing possibilities,
    
- generate hypotheses,
    
- derive consequences,
    
- produce synthetic examples.
    

But somewhere in the learning loop something eventually has to interact with reality.

For example:

```text
hypothesis
→ implementation
→ production deployment
→ unexpected behavior
→ investigation
→ new observation
```

The unexpected observation is something qualitatively different from another generated explanation.

It creates new information.

The same applies to:

- scientific experiments,
    
- software debugging,
    
- engineering failures,
    
- business decisions,
    
- medical observations,
    
- legal cases,
    
- manufacturing problems,
    
- security incidents,
    
- usability studies.
    

Human activity continuously produces such information because humans encounter situations not completely represented in existing datasets.

In production engineering, this is the difference between generating plausible distributed consensus logic and hitting thread contention under a specific Linux kernel version, silent hardware clock drift, or an unhandled network partition. Those operational failures cannot be derived purely by token prediction; they require collision with an unyielding execution environment.

---

## We May Deliberately Produce New Training Experiences

This leads to a strange possibility.

Instead of waiting for useful information to appear somewhere on the Internet, model developers could **commission new human experience specifically for training**.

A controlled experiment might look like:

```text
new problem
+
new environment
+
human expert
+
instrumentation
↓
new training trajectory
```

A software engineer could receive:

- an unfamiliar codebase,
    
- a newly created API,
    
- novel requirements,
    
- unusual constraints,
    
- access to documentation and normal development tools,
    

but no generative AI assistance.

The engineer then solves the problem manually.

The valuable output is not only the final code.

It includes the entire process:

```text
problem
→ interpretation
→ hypothesis
→ implementation
→ failure
→ debugging
→ revised hypothesis
→ solution
```

This creates information that could not simply have been copied from an existing solution.

The valuable training artifact is not the final patch or the pristine pull request. The real signal lives in the end-to-end trajectory of human reasoning against system feedback: mental modeling, diagnostic probing with debuggers and kernel logs (`strace`, `pprof`, `gdb`), and course corrections when an assumption breaks against runtime reality. That step-by-step resolution path cannot be synthesized simply by querying existing model weights.

---

## The Technological Reserve

An extreme thought experiment is a kind of **technological reserve**.

Imagine people with access to modern technology but deliberately isolated from generative AI for selected tasks.

They would still have:

- programming languages,
    
- documentation,
    
- compilers,
    
- debuggers,
    
- operating systems,
    
- databases,
    
- hardware,
    
- scientific instruments.
    

But they would have to discover solutions themselves.

Their economic role would not primarily be producing software efficiently.

Their role would be maintaining an **independent stream of human problem solving** from which future models could learn.

A literal permanent AI-free community is probably unnecessary and difficult to justify.

A more realistic version would consist of temporary, controlled AI-free environments.

People could use AI normally in everyday life while periodically performing selected tasks without it.

Senior engineers might use AI acceleration for routine feature plumbing in their day jobs, but participate in targeted, instrumented clean-room sprints where AI tooling is switched off to tackle genuinely novel system architectures, distributed race conditions, or low-level performance bottlenecks.

---

## Human-Only Work Could Become Valuable Precisely Because It Is Inefficient

This produces an interesting economic inversion.

Today companies value AI because it makes knowledge workers faster.

In a future where almost everyone uses AI, certain organizations might pay a premium for work performed **without AI**.

Not because manual work is more productive.

Because it produces independent training evidence.

A future job description might effectively say:

> Solve previously unseen engineering problems without generative AI. Your work process will be recorded and used to improve future models.

The strange result is:

> The more common AI-assisted work becomes, the more informationally valuable some deliberately AI-free work may become.

Human-only reasoning becomes scarce data.

---

## Professional Humans as Training-Data Producers

This could create new categories of work.

For example:

### Human coding experts

Experienced developers manually solve novel software problems.

### Expert problem solvers

Mathematicians, engineers, lawyers, scientists, physicians, or other specialists work through difficult cases specifically created to generate useful training trajectories.

### Frontier experts

Experts work on problems for which neither humans nor current models have established answers.

The final category may be particularly important.

The real value is not merely:

```text
human does what AI can already do
```

but:

```text
human explores where existing AI knowledge ends
```

Such people effectively become **producers of frontier knowledge**.

---

## Training Data Could Become Something We Manufacture

Historically, much of model training has depended on data that already existed:

```text
humans create Internet
→ models scrape Internet
→ models learn
```

A future model could increasingly rely on:

```text
identify missing capability
→ design novel problems
→ hire experts
→ observe attempts
→ collect outcomes
→ train next model
```

Training data becomes an intentionally manufactured product.

The process begins to resemble experimental science.

You do not merely search for existing observations.

You design situations that generate observations worth learning from.

---

## AI-Free Data Is Only One Part of the Picture

There is another dataset that may be at least as valuable.

Instead of removing the model, observe humans **working with the model**.

The trajectory becomes:

```text
human
+
model A
→ proposal
→ human correction
→ second proposal
→ test
→ failure
→ human explanation
→ successful solution
```

This reveals exactly where the current model's knowledge ends.

For the next generation, these interactions contain extremely useful signals.

For example:

```text
Model:
Use solution A.

Human:
That fails because production has constraint X.

Model:
Then use solution B.

Human:
That passes the normal tests but creates race condition Y.

Human:
Changes it to C.

Production:
C works.
```

The resulting training example contains much more than a successful implementation.

It contains:

```text
A looks plausible but fails because X
B looks plausible but fails because Y
C succeeds
```

This is almost a ready-made curriculum for the next model.

Consider an agent that proposes a familiar implementation for a concurrent service. A human rejects it because measurements from the real workload show contention that the local tests did not reproduce. A second implementation passes those tests but introduces a lock-ordering risk. The human changes the boundary again, and production telemetry shows whether the change actually helped.

That trajectory records more than the final code. It records which plausible approaches failed, what evidence exposed each failure, and which change survived contact with production.

---

## Two Kinds of Human Training Environments

Future training systems may therefore use two complementary environments.

### AI-free environments

```text
human
→ novel problem
→ independent solution
```

These preserve an independent source of human reasoning.

### AI-observed environments

```text
human + current model
→ interaction
→ corrections
→ failures
→ successful outcome
```

These reveal the shortcomings of the current generation.

The second category could become vastly larger because it can be integrated into normal work.

---

## Work Itself Could Become Training Data

This leads to an even broader possibility.

Instead of asking people to explicitly create training examples, ordinary work could become an **instrumented stream of experience**.

For software development:

```text
screen
+
IDE events
+
opened files
+
documentation searches
+
terminal commands
+
compiler output
+
tests
+
git changes
+
spoken commentary
+
final outcome
```

Together these form something much richer than source code.

They form a:

> **multimodal human work trajectory**

The model does not only see what was produced.

It sees how the result emerged.

---

## Final Code Loses Most of the Experience

A repository often preserves:

```text
before.cs
after.cs
```

perhaps accompanied by:

```text
Fix concurrency issue
```

But the real process may have been:

```text
hypothesis A
↓
implementation A
↓
test failure
↓
investigation
↓
unexpected observation
↓
hypothesis B
↓
documentation lookup
↓
discovery C
↓
final implementation
```

Most of this knowledge disappears when the final commit is created.

The final artifact tells us:

> What worked?

The trajectory can additionally tell us:

> What looked reasonable but did not work?

> What evidence changed the developer's mind?

> Which clue was important?

> Which assumptions were incorrect?

> Why was one design chosen over another?

That missing history may be extremely valuable training material.

A typical git commit tells a lossy story:

```diff
-  cache.Set(key, val)
+  workerPool.Submit(func() { cache.Set(key, val) })
```

Accompanied by a one-line message: `fix: resolve request latency spike under burst traffic`.

The real diagnostic work underneath was an extensive sequence: initial hypothesis (cache is too small), metric verification (cache hit rate was actually 94%), profiling with `pprof` (identifying lock contention on the mutex during request bursts), a failed try-lock experiment that dropped updates, and a final architectural pivot to offload writes to a bounded worker pool with graceful draining. Capturing that diagnostic history provides the causal context that clean git diffs erase.

---

## Think-Aloud Workflows Could Capture Some of It

One way to preserve this information is surprisingly simple:

> People occasionally say what they are thinking while working.

A developer might say:

> "I don't want to make this a singleton because this object appears to contain request-specific state."

Later:

> "Interesting — the tests failed because this handler is also used from the background worker."

Combined with the recorded work environment, this provides:

```text
belief
→ action
→ evidence
→ contradiction
→ updated belief
→ solution
```

The voice recording itself is not the important artifact.

The important artifact is the synchronized combination of:

```text
what the person saw
+
what they believed
+
what they did
+
what happened
```

---

## Continuous Narration Is Probably Unnecessary

Having people constantly verbalize every thought would likely be distracting and inefficient.

Much expert reasoning is also:

- automatic,
    
- intuitive,
    
- partially unconscious,
    
- difficult to verbalize.
    

A senior engineer may simply say:

> "Something smells wrong here."

Then immediately inspect exactly the three files needed to locate the bug.

They may not be able to fully explain why their intuition directed them there.

This does not make the trajectory useless.

The system also observes:

- which code they inspected,
    
- what they ignored,
    
- which search query they used,
    
- where they navigated next,
    
- what they changed,
    
- whether the hypothesis succeeded.
    

The model can potentially reconstruct part of the implicit reasoning from behavior.

---

## Lightweight Narration May Be Enough

A more realistic workflow would ask humans to explain only high-value moments.

For example:

> "I'm checking X because..."

> "I rejected this solution because..."

> "This result surprised me."

> "My previous assumption was wrong."

> "This is the architectural decision."

A development environment could even provide something equivalent to:

```text
🎙 Explain decision
```

The developer records ten or twenty seconds of explanation.

The system automatically attaches:

- current code,
    
- diff,
    
- open files,
    
- test results,
    
- task description,
    
- relevant history.
    

A tiny amount of human narration could therefore enrich a much larger automatically collected context.

---

## The AI Could Interview the Human

An even better approach may be not to interrupt the worker until something informationally interesting happens.

The system observes:

```text
developer implements A
→ tests pass
→ developer deletes A
→ implements B
```

Instead of recording continuous commentary, the AI asks:

> Why did you abandon solution A even though the tests passed?

The developer answers:

> Because it shared mutable state between requests. The current tests don't exercise concurrent execution.

That ten-second explanation may be more valuable than an hour of ordinary narration.

Future training-data systems could therefore actively search for moments such as:

- rejected solutions,
    
- surprising test failures,
    
- reversals of decisions,
    
- manual overrides of AI suggestions,
    
- unusual debugging paths,
    
- differences between expected and observed behavior.
    

Then they could conduct tiny contextual interviews.

---

## Documentation May Expand From State to Discovery

Traditional documentation primarily records:

```text
what the system is
```

Future knowledge systems may increasingly preserve:

```text
how we discovered
what the system should be
```

This includes:

- abandoned designs,
    
- surprising constraints,
    
- failed experiments,
    
- reasoning behind decisions,
    
- observations that changed assumptions.
    

Instead of documentation being produced only after the work, parts of it could be extracted automatically from the work trajectory itself.

---

## Privacy and Incentives Become Central

Such a system creates obvious social problems.

Recording:

- screens,
    
- speech,
    
- work behavior,
    
- mistakes,
    
- decision processes,
    

can easily become invasive employee surveillance.

Therefore a useful training-data ecosystem would require strong boundaries around:

- informed participation,
    
- compensation,
    
- ownership,
    
- confidentiality,
    
- customer data,
    
- trade secrets,
    
- what may be recorded,
    
- what may be used for training,
    
- retention and deletion.
    

People may willingly generate high-value training trajectories if they understand the purpose and participate under explicit terms.

The same mechanism becomes very different if imposed as permanent workplace surveillance.

This may create a market rather than merely an internal monitoring system:

> Experts explicitly sell carefully scoped pieces of their work experience as training data.

From an operational perspective, this requires rigorous client-side data hygiene: local automated redaction of API keys, credentials, PII, and customer payloads before telemetry ever leaves the machine. Data collection must be strictly bound to consented, designated clean-room sandboxes or specific debugging sessions, preventing background telemetry from devolving into opaque corporate surveillance.

---

## Human Experience Factories

At sufficient scale, organizations could deliberately operate something resembling **human experience laboratories**.

Not content farms producing articles.

Facilities producing novel problem-solving experience.

For example:

```text
software engineers
scientists
mathematicians
lawyers
mechanical engineers
domain specialists
```

would receive carefully selected novel problems.

Their job would be to:

- investigate,
    
- experiment,
    
- make decisions,
    
- fail,
    
- revise assumptions,
    
- solve problems,
    
- explain important discoveries.
    

The product is not primarily the document or implementation they produce.

The product is:

> **new information generated through interaction with a problem.**

---

## Models Could Help Design Their Own Future Training Data

This eventually creates a fascinating feedback loop.

A current model can identify areas where it is uncertain or repeatedly fails.

It can help design tasks targeting those weaknesses.

Humans then encounter those tasks and generate real outcomes.

```text
model identifies weakness
→ new experiment is designed
→ human attempts it
→ reality provides feedback
→ experience is recorded
→ next model learns
```

The current model therefore helps determine:

> What experiences should humans generate so that the next model becomes better?

This is substantially different from pure synthetic data generation because the loop still contains an external source of evidence.

For example, a model struggling with consensus edge cases in distributed Raft implementations can generate a targeted reproduction harness with subtle network jitter and partition scenarios. A human specialist or deterministic execution harness attempts the problem, the compiler and kernel provide unforgiving binary pass/fail telemetry, and the resulting debugging trajectory is captured to train the successor model.

---

## The Essential Boundary Is Contact With Reality

Synthetic data can be extraordinarily useful.

Models can:

- generate exercises,
    
- create alternative explanations,
    
- explore search spaces,
    
- critique answers,
    
- simulate possibilities.
    

But a closed loop such as:

```text
model
→ synthetic data
→ model
→ synthetic data
```

ultimately risks recycling its own assumptions.

The most valuable loop contains some independent source of feedback:

```text
model
→ hypothesis
→ human / experiment / environment
→ observable outcome
→ new information
→ model
```

The critical component is not necessarily the human.

It is **external reality**.

Humans currently happen to be one of the most flexible mechanisms for connecting models with it.

That external friction does not always have to be a human mind. A deterministic compiler, a physical robot arm, an eBPF network probe, a silicon testbench, or a production telemetry stream under real user traffic all serve as unforgiving verification oracles. The non-negotiable invariant is that the validation boundary lives outside the model's own statistical priors.

---

## A Strange Future Economic Role for Humans

This produces a counterintuitive possibility.

As AI becomes better at performing existing intellectual work, one of the remaining high-value human roles may be:

> encountering situations from which AI has not yet learned.

Humans may increasingly contribute not merely by producing artifacts but by producing **experience**.

The future knowledge worker could therefore simultaneously be:

```text
worker
+
experimenter
+
sensor
+
teacher
```

Every difficult problem solved in the real world can potentially become training evidence for the next generation.

---

## Core Insight

The future bottleneck in model training may not be a shortage of text.

It may be a shortage of **independent new experience**.

As existing knowledge becomes increasingly absorbed by models and increasingly recombined into synthetic content, fresh observations become more valuable.

This may create entirely new mechanisms for producing training data:

```text
controlled AI-free problem solving
+
expert-created novel tasks
+
human-AI work trajectories
+
spoken explanations
+
instrumented work environments
+
micro-interviews after important decisions
+
real-world experiments
```

The most valuable dataset of the future may therefore not look like a larger copy of the Internet.

It may look like:

> **millions of carefully captured episodes in which humans, machines, or both encountered reality, discovered something they did not previously know, and recorded how that discovery happened.**

In such a world, the scarce resource is no longer content.

It is **fresh contact with reality**.
