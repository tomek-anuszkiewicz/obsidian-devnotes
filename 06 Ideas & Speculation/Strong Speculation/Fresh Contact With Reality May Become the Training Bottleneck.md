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
  - "Independent Experience for Model Training"
---

A system can generate more explanations and candidate solutions while learning little that is independent of its existing knowledge. Improvement depends on what happens when those candidates encounter new observations, tests, experiments, or difficult real work.

This article develops the proposed bottleneck of independent experience, including commissioned expert tasks, deliberately created learning environments, and feedback from reality. [[Capturing Expert Work as Training Experience]] follows the complementary collection problem: preserving the sequence of attempts, failures, evidence, and human decisions inside ordinary work. Producing an experience and retaining enough of it to learn from are separate requirements.

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

A closed synthetic loop that feeds model outputs back into subsequent training runs without external verification inevitably drifts (see [[Improving AI Models — From Scaling to Agent-Generated Training Data]]). Without hard friction against external systems, the learning process risks recycling its own assumptions, amplifying subtle hallucinations, and narrowing diversity. Token volume explodes, but independent entropy collapses, accelerating the data degradation dynamics described in [[AI May Break the Old Economic Model of the Open Web]].

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

This would not be a general market for artisanal software. The organization would pay for an independent problem-solving trajectory that existing models have not already shaped. If a person and an agent produce the same ordinary application, manual authorship alone still gives the application little additional operational value (see [[Handwritten Code May Not Become a Luxury Good]]).

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

It is **fresh contact with reality** (see [[The Most Valuable Software Training Data May Be Private]]).

## Related notes

- **[[Improving AI Models — From Scaling to Agent-Generated Training Data]]** — Harnessing execution feedback and reality collisions to train frontier models.
- **[[The Most Valuable Software Training Data May Be Private]]** — The strategic value of private operational trajectories over public scraping.
- **[[What Should Organizations Preserve from AI-Assisted Development]]** — Capturing negative trajectories, rejection logs, and empirical evidence.
- **[[AI May Break the Old Economic Model of the Open Web]]** — Autophagous data loops and the collapse of ad-supported web content.
