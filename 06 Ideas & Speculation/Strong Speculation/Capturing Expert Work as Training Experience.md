---
title: "Capturing Expert Work as Training Experience"
tags:
  - training-data
  - ai-agents
  - knowledge-management
  - privacy
  - model-training
aliases:
  - "Expert Work Trajectories as Training Data"
  - "Preserving Discovery Behind Final Artifacts"
  - "Capturing Human AI Collaboration and Decisions"
---

A repository records the final patch, but the useful discovery may have happened earlier: an initially plausible design failed, a benchmark contradicted an assumption, or an expert identified the constraint that changed the solution. The final artifact does not necessarily preserve that sequence.

Capturing the work trajectory means connecting actions, observations, rejected options, and explanations with the result. Occasional narration or short contextual questions can add meaning without requiring continuous commentary. Collection still needs a purpose, consent, access limits, and incentives that do not turn an expert learning system into opaque surveillance.

Work performed independently without an assistant can expose one kind of expert reasoning. Observing a person working with an assistant provides another: where the suggestion failed, which evidence the person checked, and how they corrected the course. The comparison below treats those as complementary sources of experience.

The sections below develop those collection choices and the possible value of new experience. [[Fresh Contact With Reality May Become the Training Bottleneck]] explains why independent contact with a problem matters in the first place. The objective here is to retain useful evidence about how a result was reached, rather than assuming a clean final artifact contains the entire lesson.

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

Define the learning question and the events needed to answer it before collecting an indiscriminate stream of activity. Preserve provenance and meaningful decision points, make ownership and access explicit, and distinguish an observed trajectory from an explanation later inferred about it.

## Related Notes

- [[Fresh Contact With Reality May Become the Training Bottleneck]] — Independent experience, commissioned tasks, and external validation boundaries.
- [[The Most Valuable Software Training Data May Be Private]] — The value and ownership of organizational experience unavailable in public artifacts.
- [[What Should Organizations Preserve from AI-Assisted Development]] — Selecting the intent, evidence, failed branches, and decisions worth retaining.
