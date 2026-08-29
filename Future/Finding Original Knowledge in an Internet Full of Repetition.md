Large language models are usually described as systems trained on enormous amounts of text.

But the amount of text is not the same as the amount of information.

A large part of the Internet consists of:

- repetitions,
    
- summaries,
    
- paraphrases,
    
- SEO content,
    
- explanations of already known concepts,
    
- copies of copies,
    
- increasingly AI-generated recombinations of existing knowledge.
    

This suggests an interesting possibility:

> Future training systems may need to identify not merely high-quality text, but information that is genuinely new.

The important distinction is between **text novelty** and **information novelty**.

---

## Text Novelty Is Not Information Novelty

A document can be completely original at the textual level while adding almost no new information.

For example, thousands of articles may explain the same concept using different wording.

```text
same knowledge
→ article A
→ article B
→ tutorial C
→ summary D
→ AI-generated explanation E
```

All five documents may be lexically different.

Informationally, however, they may be almost identical.

Conversely, one short sentence can contain genuinely new information:

> We changed the retry timeout from 15 to 22 seconds because the payment provider begins rejecting the second retry after approximately 18 seconds.

The sentence may be stylistically unremarkable, but it records an observation that did not previously exist in the public corpus.

For model training, the second type of data may be much more valuable.

---

## Semantic Deduplication Is Only the Beginning

Current data pipelines already attempt to remove:

- exact duplicates,
    
- near duplicates,
    
- highly similar documents,
    
- semantically redundant examples.
    

But a more advanced system could operate at the level of **claims** rather than documents.

Imagine decomposing a document into:

```text
Claim A
Claim B
Claim C
Claim D
```

and comparing each claim with the existing knowledge corpus.

The system could discover:

```text
A → already present in 100,000 documents
B → already present in 20,000 documents
C → common reformulation of existing knowledge
D → no meaningful earlier equivalent found
```

The interesting part of the document is then not the document itself.

It is `Claim D`.

Training pipelines could therefore evolve from:

```text
document filtering
```

toward:

```text
information extraction
→ claim clustering
→ novelty detection
→ provenance analysis
```

---

## The More Interesting Target Is Primary Information

An even more important distinction may be between:

### Recombined information

Knowledge reconstructed from things already known.

Examples include:

- tutorials,
    
- summaries,
    
- explainers,
    
- derivative blog posts,
    
- most SEO content,
    
- many AI-generated articles.
    

and:

### Primary information

Knowledge produced through interaction with reality.

Examples include:

- experiment results,
    
- incident reports,
    
- debugging discoveries,
    
- production metrics,
    
- failed approaches,
    
- customer observations,
    
- benchmark results,
    
- scientific measurements,
    
- engineering trade-offs discovered during implementation.
    

The difference can be simplified as:

```text
existing knowledge
→ transformation
→ secondary content
```

versus:

```text
reality
→ observation
→ new information
```

The second pipeline creates something the model could not previously know.

---

## Detecting Human-Written Text Is the Wrong Problem

It might seem that the goal should be to detect whether something was written by a human.

But that is not really what matters.

An LLM can easily generate text such as:

> We deployed the system and observed a 17% reduction in CPU usage.

The sentence looks like a report of real experience.

It may nevertheless be completely fabricated.

Therefore:

```text
looks like primary information
≠
contains primary information
```

The useful question is not:

> Was this text written by a human?

It is:

> Does this information appear to originate from an independent interaction with reality?

Human-vs-AI detection is therefore much less interesting than **information provenance detection**.

---

## Signs of Experiential Knowledge

A model could potentially learn to identify content that is likely to contain first-hand observations.

Such content often contains:

- precise context,
    
- concrete measurements,
    
- unexpected outcomes,
    
- failed attempts,
    
- trade-offs,
    
- implementation-specific details,
    
- causal explanations discovered experimentally,
    
- contradictions with conventional wisdom,
    
- local constraints unavailable in public documentation.
    

For example:

> After moving the service from four to eight workers, throughput improved only 12%. Profiling showed that the database connection pool, not CPU capacity, had become the bottleneck.

This has a different informational character from:

> Increasing the number of workers can improve application throughput.

The second statement is generic knowledge.

The first contains an observation.

We could call this property:

> **experientiality**

---

## A Future Knowledge-Mining Pipeline

A future training system might combine an LLM with a massive searchable corpus.

The architecture could look roughly like:

```text
raw corpus
    ↓
semantic indexing
    ↓
claim extraction
    ↓
claim clustering
    ↓
temporal provenance analysis
    ↓
novelty estimation
    ↓
credibility estimation
    ↓
training-value scoring
```

The temporal dimension is particularly important.

Imagine the following history:

```text
2018 → source A reports observation X
2019 → source B discusses X
2020 → hundreds of articles repeat X
2023 → thousands of AI-generated pages explain X
```

Without provenance analysis, all of these documents appear to be training data.

With provenance analysis, the system can recognize that most of the informational value originated in the first few sources.

The rest primarily increases repetition.

---

## The LLM Should Not Be the Database

A model trained on the Internet may have a rough internal representation of which ideas are common and which are unusual.

But model weights are a poor provenance database.

A better system would combine:

```text
LLM reasoning
+
large semantic index
+
publication timestamps
+
source relationships
+
citation graphs
+
document history
```

The LLM could reason about whether a claim is novel.

The external system could verify whether similar claims already existed.

This makes the task much closer to **knowledge archaeology** than ordinary search.

---

## Training Value Could Be Explicitly Estimated

A future dataset pipeline could assign each piece of information a score such as:

```text
TrainingValue =
    Novelty
  × Credibility
  × Experientiality
  × InformationDensity
  × Importance
```

Consider two examples.

### Generic tutorial

```text
Novelty:            very low
Credibility:        medium
Experientiality:    very low
InformationDensity: low
```

There may already be tens of thousands of equivalent documents.

### Internal production postmortem

```text
Novelty:            high
Credibility:        high
Experientiality:    very high
InformationDensity: high
```

A few pages of the second type could potentially contain more useful new information than thousands of pages of public explanatory content.

---

## Corporate Data Becomes Extremely Interesting

This makes private organizational data especially valuable.

Companies accumulate enormous amounts of information in:

- source code,
    
- commit history,
    
- pull requests,
    
- code reviews,
    
- Jira tickets,
    
- Slack conversations,
    
- architecture discussions,
    
- incident reports,
    
- production metrics,
    
- experiments,
    
- meeting recordings,
    
- customer support conversations.
    

Much of this information never reaches the public Internet.

More importantly, it often represents the point where new knowledge is created.

Public content frequently follows the chain:

```text
knowledge
→ article
→ explanation
→ summary
→ paraphrase
→ another summary
```

Private operational data is much closer to:

```text
problem
→ experiment
→ failure
→ observation
→ decision
```

The latter may have much higher marginal training value.

---

## The Scarce Resource May Become New Information, Not Tokens

Early language-model development benefited enormously from simply increasing the amount of training text.

But eventually the problem changes.

There may be practically unlimited numbers of new tokens while the amount of genuinely new information grows much more slowly.

Especially with generative AI, the Internet can expand rapidly through:

```text
existing information
→ LLM
→ more text
→ another LLM
→ still more text
```

The number of tokens increases.

The amount of knowledge may barely change.

This suggests a possible future bottleneck:

> The scarce resource for model improvement may not be text. It may be fresh contact with reality.

---

## A New Kind of Crawler

Traditional web crawlers ask:

> What pages exist?

Search engines ask:

> Which pages are relevant?

Future training-data systems may ask:

> Where did something genuinely new enter the information ecosystem?

Such a system could search for:

- first reports,
    
- original experiments,
    
- unique measurements,
    
- unusual failure cases,
    
- primary sources,
    
- novel engineering observations,
    
- previously unseen combinations of constraints.
    

Instead of a web crawler, it would behave more like a:

> **novel knowledge miner**

Its purpose would be to find places where someone appears to have discovered, measured, tested, or observed something that was not already represented in the corpus.

---

## A Potential Feedback Loop

There is also a broader implication.

Humans and AI agents increasingly produce software, experiments, analyses, and decisions together.

Those activities generate new evidence:

```text
model proposes solution
→ human or system tries it
→ reality produces result
→ result is recorded
→ future model learns from it
```

The valuable training signal is not necessarily the generated solution.

It may be the **interaction between the generated solution and reality**.

Failures may be particularly valuable because they reveal constraints that were absent from the original model.

This creates a potential learning loop:

```text
existing model
→ attempt
→ real-world feedback
→ new information
→ curated training data
→ better model
```

The important part is that the loop must eventually touch reality.

Pure model-to-model generation cannot create the same kind of information indefinitely.

---

## Core Insight

The future of training-data selection may move from:

> Find more high-quality text.

toward:

> Find information that the model could not already reconstruct from what it knows.

And eventually toward:

> Find evidence that someone actually interacted with reality and learned something from it.

This shifts the most valuable resource from **content production** to **knowledge production**.

The Internet contains enormous amounts of the former.

The latter may become increasingly scarce — and increasingly valuable.