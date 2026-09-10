---
title: Improving AI Models — From Scaling to Agent-Generated Training Data
tags:
  - ai-scaling
  - synthetic-data
  - training-data
  - model-training
  - reinforcement-learning
  - agent-generated-data
aliases:
  - Scaling Laws to Synthetic Data
  - Agent-Generated Training Data
---

The historical improvement of AI models is often described as a simple consequence of larger models and more compute.

That is increasingly incomplete. As analyzed in [[LLM Capability Reliability and the Shape of Progress|the shape of LLM progress]], progress has come from several successive layers:

```text
more parameters + more data + more compute
                ↓
better data and training efficiency
                ↓
instruction tuning and human feedback
                ↓
reasoning and test-time compute
                ↓
tool use and agent environments
                ↓
feedback from real-world AI work
```

The next generation of models may improve not only because they are larger, but because training loops incorporate [[Emergence, Latent Space Synthesis, and How Targeted Prompts Crystallize Insight|latent space synthesis and emergent capabilities]].

## The First Phase Was Mostly Scaling

Early transformer progress was strongly associated with scaling:

- larger models;
    
- larger datasets;
    
- more training compute.
    

Scaling laws showed relatively predictable improvements as these resources increased.

Later work, such as Chinchilla, demonstrated that model size alone was not enough.

A model could be too large relative to the amount of data used to train it.

This shifted attention from:

> How large is the model?

toward:

> How efficiently are model size, data, and compute balanced?

The important lesson was that better training could sometimes outperform simply making the model larger.

## Instruction Tuning Changed What "Better Model" Meant

The next major improvement came from teaching models how humans actually wanted them to behave.

Instruction tuning and RLHF showed that a much smaller model could sometimes be preferred over a much larger raw pretrained model.

This demonstrated an important distinction:

```text
knowledge contained in the model
!=
ability to use that knowledge effectively
```

A model may already contain useful capabilities but fail to expose them without appropriate post-training.

From this point onward, practical model quality increasingly depended on:

- instruction following;
    
- preference learning;
    
- reasoning behavior;
    
- refusal behavior;
    
- response structure;
    
- task-specific post-training.
    

## Reasoning Added Another Scaling Dimension

Reasoning models introduced another important mechanism.

Previously, scaling mostly meant:

```text
more compute during training
```

Now it can also mean:

```text
more compute while solving a problem
```

A model may explore several possibilities, verify intermediate conclusions, or spend more inference compute before producing an answer.

This means that capability no longer depends only on the static model.

It also depends on how much computation the system allows the model to perform during execution.

## Agents Add Yet Another Layer

For software engineering, a model increasingly operates inside an environment containing:

- a filesystem;
    
- source control;
    
- a compiler;
    
- tests;
    
- static analysis;
    
- documentation;
    
- terminals;
    
- browsers;
    
- APIs;
    
- issue trackers;
    
- other models.
    

The relevant system therefore becomes:

```text
model
+ reasoning
+ tools
+ environment
+ feedback loops
```

This makes it increasingly difficult to separate "model capability" from "agent capability".

A model that cannot reliably solve a coding task in one response may still solve it through:

```text
inspect
→ edit
→ compile
→ test
→ inspect failure
→ modify
→ test again
```

The apparent intelligence of the system can improve significantly even without an equally large improvement in the underlying base model.

## The Most Interesting New Resource May Be AI Work Itself

The rise of coding agents creates a new kind of training data.

Traditional code training data often looks like:

```text
repository
→ final source code
```

The model sees the result but not necessarily the process that created it.

Agent-assisted development can produce much richer traces:

```text
requirement
↓
model attempt
↓
compiler failure
↓
model correction
↓
test failure
↓
another correction
↓
human review
↓
business explanation
↓
final implementation
↓
successful CI
```

This contains much more information than the final source code alone.

The model can potentially learn:

- what solution was attempted;
    
- why it failed;
    
- what evidence revealed the failure;
    
- how the implementation was corrected;
    
- what business rule had been misunderstood;
    
- which final solution was accepted.
    

This is not merely learning code.

It is learning the process of software engineering.

## Human Corrections May Be Especially Valuable

Consider a simple interaction:

```text
Agent:
Changes the price after an order is confirmed.

Human:
This is incorrect.
After confirmation the price is immutable because the accounting
process assumes the invoice value cannot change.
```

This interaction contains several layers of information:

```text
problem
+
incorrect solution
+
reason it is incorrect
+
business knowledge
+
corrected solution
```

That may be much more valuable than another repository containing only the final implementation.

Human review of AI-generated code could therefore become an important source of training signal.

The same applies to strong human instructions supplied before generation.

A detailed specification teaches more than:

> Write this feature.

It exposes:

- constraints;
    
- invariants;
    
- expected trade-offs;
    
- architecture boundaries;
    
- business reasoning.
    

## Programming Has an Important Advantage: Verification Is Cheap

Software is unusually attractive for this kind of learning because many results can be checked automatically.

An agent can generate code and receive immediate feedback from:

```text
compiler
tests
integration tests
benchmarks
static analysis
security scanners
type systems
linters
```

The training system can therefore obtain relatively objective signals such as:

```text
compiles = yes
tests = 142 / 142
benchmark = +8%
memory usage = -12%
security checks = pass
```

This makes programming well suited to reinforcement learning and synthetic-data generation.

Instead of relying entirely on humans to label outputs, machines can automatically verify large numbers of attempts.

## Synthetic Data Is Not Necessarily Model Copying Itself

There is an important distinction between two forms of synthetic data.

A dangerous loop would be:

```text
model generates output
↓
output is blindly added to training data
↓
next model learns the same mistakes
↓
repeat
```

This can amplify errors and reduce diversity.

A much more useful loop is:

```text
model generates many candidates
↓
tests / verifiers / humans evaluate them
↓
bad outputs are rejected
↓
good outputs are retained
↓
failure information may also be retained
↓
next model trains on the filtered experience
```

The crucial component is verification.

Synthetic data becomes valuable when it represents exploration plus selection, rather than uncontrolled self-imitation.

## Coding Agents Can Generate Their Own Curriculum

This creates an interesting feedback loop:

```text
better model
↓
better coding agent
↓
agent attempts harder real-world tasks
↓
new failure modes appear
↓
humans and automated systems correct them
↓
new high-value training data is created
↓
next model improves
```

The current generation of models therefore does something historically unusual.

It helps create the dataset that may train its successors.

The world is gradually producing not only:

```text
human-generated knowledge
```

but also:

```text
human ↔ AI collaboration traces
```

These traces did not exist at meaningful scale before AI assistants became widely used.

## Today's Failures May Become Tomorrow's Training Examples

Suppose today's agent struggles with:

> Refactor this legacy system while preserving compatibility during a rolling deployment.

Thousands of engineers may attempt similar tasks with AI.

Their interactions produce examples such as:

```text
prompt
→ incorrect patch
→ CI failure
→ human review
→ explanation
→ corrected patch
→ successful deployment
```

If enough of these traces are collected and selected appropriately, future models may learn the class of problem that today's models struggle with.

This creates a potentially powerful phenomenon:

> Failed attempts to use today's agents may become part of the reason tomorrow's agents succeed.

Using an imperfect model can therefore indirectly generate information about the exact boundary of its capabilities.

## Future Progress May Come From Several Curves at Once

Instead of imagining a single model-quality curve, it may be better to think about several overlapping curves:

```text
base-model capability
training-data quality
post-training
reasoning
test-time compute
tool use
agent orchestration
verification
real-world feedback
```

Some of them may eventually slow down.

Others may still be accelerating.

This explains why reaching saturation on one benchmark does not necessarily imply that AI progress itself is saturating.

The meaningful benchmark may change from:

```text
Can the model write this function?
```

to:

```text
Can the agent complete this two-hour engineering task?
```

and eventually:

```text
Can the agent autonomously complete this multi-day engineering project?
```

## The Shape of Future Progress May Therefore Change

Future models may not improve primarily through:

```text
GPT-N
=
GPT-(N-1)
× much more parameters
```

A more plausible combination is:

```text
pretraining                    ↑
data quality                   ↑↑
synthetic verified data        ↑↑↑
reinforcement learning         ↑↑↑
reasoning                      ↑↑
test-time compute              ↑↑
tool use                       ↑↑↑
agent environments             ↑↑↑
real-world feedback            ↑↑↑
human corrections              ↑↑
```

The relative importance of raw model scaling may decrease while the importance of the learning environment increases.

## The Long-Term Shift

The first generation of language models primarily learned from artifacts humans had already created:

- books;
    
- websites;
    
- source code;
    
- discussions;
    
- documentation.
    

Future generations may increasingly learn from attempts to perform work.

That dataset contains not just answers, but trajectories:

```text
goal
→ reasoning
→ action
→ failure
→ feedback
→ correction
→ success
```

This may be a much richer training signal.

For software engineering in particular, the model may gradually move from learning:

> What does good code look like?

toward learning:

> How does an engineer get from an imperfect understanding of a requirement to a verified working system?

If this feedback loop continues, progress in coding AI may remain significant even if improvements from simple model scaling begin to slow.

The next major gains may come from the interaction between better models, better tools, automatic verification, and the enormous new corpus of human–AI collaboration being created today.

---

## Relationship to the Knowledge Graph

- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Analyzes the autophagous degradation loop (Model Collapse) and how deterministic verification gates turn synthetic data into evolutionary training signals.
- **[[The Most Valuable Software Training Data May Be Private]]**: Explores why real-world execution trajectories from private repositories are far more valuable than public web scrapings.
- **[[Fresh Contact With Reality May Become the Training Bottleneck]]**: Details why models risk inbred degradation without continuous empirical grounding in physical and business reality.
- **[[Testing in the Model, Agent, LLM Era]]**: How compilers, test suites, and mutation engines act as the automated objective evaluators required for process supervision.
- **[[LLM Coding Agents Reliability]]**: Empirical examination of how trajectory-trained models improve reliability over one-shot LLM generators.