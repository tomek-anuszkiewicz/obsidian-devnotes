---
title: Finding Original Knowledge in an Internet Full of Repetition
tags:
  - open-web
  - knowledge-discovery
  - information-diet
  - synthetic-data
  - epistemology
  - content-pollution
aliases:
  - Original Knowledge Scarcity
  - Internet Model Collapse and Search
---

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

When training pipelines simply amass tokens without introducing new state information, the model burns compute refining redundant statistical representations of consensus claims. Worse, repeatedly training on derivative web content risks mode collapse and representational homogenization across generations.

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

To a standard n-gram deduplicator or document-level MinHash filter, those five variations appear completely distinct. Informationally, ingesting all five yields vanishingly small gradient utility during pre-training while consuming precious token budget.

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
    

Standard document-level filtering—whether via URL hashes, MinHash with Locality-Sensitive Hashing (LSH) over token n-grams, or dense embedding cosine similarity—is simply too coarse. A high-value production postmortem might consist of 90% generic setup and standard framework boilerplate, yet contain a 10% core of critical, unindexed operational insight.

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
    

Secondary content remains useful for dialing in conversational tone, instruction formatting, or pedagogy during supervised fine-tuning (SFT), but it contributes almost zero net-new world knowledge to base model pre-training.

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

This empirical path captures boundary conditions, runtime interactions, and hardware failure modes that a model could never derive theoretically from its existing weights.

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

Detecting authorship inevitably turns into a superficial game of stylistic cat-and-mouse. Verifying information provenance, on the other hand, is an engineering exercise in empirical validation, causal consistency, and citation auditing.

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

## Automated Media Radar: Mining Long-Form Transcripts

This challenge of isolating novel, experiential insights is not limited to web crawlers indexing text; it applies directly to how engineers consume long-form technical media such as podcasts, conference panels, and architecture discussions.

Because platform algorithms reward watch time and session duration, technical panels are routinely padded out to an hour or more with pleasantries, recycled generalities, and established consensus. For an experienced engineer, a 60-minute technical discussion typically contains an asymmetric ratio: roughly one to two minutes of genuine empirical signal—such as an engineer describing an undocumented hardware behavior under load, an obscure compiler bug, or a counter-intuitive production bottleneck—surrounded by 58 minutes of conversational noise.

Rather than burning human attention on passive listening, a local agent pipeline can act as an automated radar:

1. **Continuous Ingestion**: An always-on background worker runs audio streams through a local speech-to-text model (such as Whisper) as soon as new episodes drop (see [[Always-On Autonomous Agents - The 24-7 Local Operating System]]).
2. **Claim Extraction and Diffing**: The system extracts atomic assertions from the transcript and diffs them against an existing knowledge base (see [[How Personal AI Models Reconcile External Knowledge]]).
3. **Filtering Consensus and Anti-patterns**: The pipeline discards well-trodden architectural axioms as baseline consensus, filters out known failure modes already cataloged in dissent logs (see [[Negative Knowledge and Explicit Architectural Dissents]]), and isolates only unseen empirical claims or unexpected edge cases.
4. **Attention Inversion**: The workflow inverts linear listening into an asynchronous review, delivering a concise markdown summary with exact timestamps for rapid human verification.

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

A crawler sampling the open web at random will assign the vast majority of its compute budget to downstream echoes of an insight. Temporal provenance analysis traces citation and timestamp topology back to the root event, downweighting derivative iterations and preserving only the primary record alongside any subsequent documents that report verified new measurements.

---

## The LLM Should Not Be the Database

A model trained on the Internet may have a rough internal representation of which ideas are common and which are unusual.

But model weights are a poor provenance database.

Neural network weights are a lossy, distributed associative memory. They excel at fuzzy pattern matching and synthesis, but they cannot reliably distinguish between a claim remembered with high certainty due to extreme training frequency, a statistical hallucination, or an idea that merely appears novel due to prompt phrasing.

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

Decoupling the reasoning engine from an external substrate—such as vector indices (HNSW/ScaNN), web archive snapshots, git revision logs, and inbound citation graphs—allows the model to handle claim extraction while immutable indices verify temporal priority.

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

Evaluating these factors requires concrete heuristics:

- **Novelty**: Inverse frequency of the claim across the historical corpus, prioritizing unseen causal links or parameter configurations.
- **Credibility**: Source verification, reproducible test cases, and internal consistency of technical data.
- **Experientiality**: Density of operational markers—profiler traces, benchmark metrics, hardware telemetry, and recorded failure modes.
- **Information Density**: Ratio of verified technical claims to total token count, filtering out boilerplate and conversational padding.
- **Importance**: Alignment with critical runtime capabilities, such as distributed systems reliability, memory safety, or systems debugging.

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

Public engineering content is heavily distorted by marketing, brand management, and SEO incentives; it systematically sanitizes failure in favor of tidy, retrospective narratives. Private operational systems capture friction at the physical boundaries—where query planners fail under load, locks deadlock, and deployments crash. That collision data carries the highest informational entropy, providing the precise training signal required for models to reason through non-trivial production failures (see [[The Most Valuable Software Training Data May Be Private]]).

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

Rather than optimizing for PageRank or domain authority, a novelty crawler actively traverses dependency and citation graphs to isolate the single terminal commit, issue thread, or telemetry record where an empirical observation first entered the ecosystem.

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

A closed loop of model-to-model synthetic text generation inevitably degrades into statistical self-referential drift. By contrast, an agent loop anchored to physical or operational reality—where proposed solutions must compile, pass execution sandboxes, survive production traffic, or satisfy hardware constraints—creates a self-sustaining stream of high-entropy training data.

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
