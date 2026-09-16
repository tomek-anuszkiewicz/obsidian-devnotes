---
title: Finding Original Knowledge in an Internet Full of Repetition
tags:
  - open-web
  - knowledge-discovery
  - information-diet
  - synthetic-data
  - information-entropy
  - content-pollution
aliases:
  - Original Knowledge Scarcity
  - Internet Model Collapse and Search
---

# Finding Original Knowledge in an Internet Full of Repetition

Large language models are traditionally described as systems trained on massive web-scale text corpora. But in production data engineering, anyone working on pre-training, fine-tuning, or retrieval-augmented pipelines quickly runs into an unavoidable reality: **token volume does not equal information volume**.

A massive fraction of the open web consists of:

- Exact text repetitions and mirror sites,
- Content syndication and paraphrasing,
- Search engine optimization (SEO) rehashes of the same five concepts,
- Explanations of established, baseline knowledge,
- Summaries of summaries,
- An accelerating flood of synthetic, model-generated text recombining existing ideas.

This dynamic creates an acute challenge for training pipelines. If a dataset simply amasses more tokens without adding new state information, the model wastes compute learning redundant statistical representations of existing claims. At worst, recursively training models on derivative web content risks mode collapse and homogenization.

To sustain intelligence growth, future training systems need to identify not just grammatically fluent or high-scoring text, but information that is genuinely new. The critical engineering distinction is between **text novelty** and **information novelty**.

---

## Text Novelty Is Not Information Novelty

A document can be completely original at the lexical level while introducing zero new information.

Consider five articles explaining standard Raft consensus or a common database lock timeout:

```text
Underlying Knowledge Base
  │
  ├──► Article A (Technical blog post)
  ├──► Article B (Syndicated rewrite)
  ├──► Tutorial C (Step-by-step explainer)
  ├──► Summary D (Executive roundup)
  └──► AI-Generated E (Synthetic regurgitation)
```

All five documents can have entirely distinct vocabulary distributions, different sentence structures, and zero matching n-grams. To a standard n-gram deduplicator or a loose document-level MinHash filter, they appear distinct. 

Informationally, however, they are duplicates. Ingesting all five provides vanishingly small gradient utility during pre-training.

Conversely, a single unadorned log message or incident sentence can deliver high informational novelty:

> "We changed the retry timeout from 15 to 22 seconds because the payment provider begins rejecting the second retry after approximately 18 seconds."

That sentence will never win any style awards, but it records a concrete, empirical observation about a third-party failure mode that previously existed nowhere in the public corpus. 

For model training, that single sentence can be orders of magnitude more valuable than 50,000 words of generic network programming tutorials.

---

## Semantic Deduplication Is Only the Beginning

Production pre-training pipelines already run basic deduplication passes:

- Exact matching (URL deduplication, SHA-256 hashes),
- Near-duplicate detection (MinHash with Locality-Sensitive Hashing over token n-grams),
- Embedding-based document similarity (cosine distance over dense document vectors).

These approaches operate at the document level. That granularity is too coarse. A high-value technical document might be 90% boilerplate setup and 10% critical insight. 

A more effective ingestion pipeline operates at the level of **atomic claims**:

```text
Raw Document
  │
  ▼
[ Claim Extraction Engine ]
  │
  ├──► Claim A: "Postgres uses MVCC for concurrency control."
  ├──► Claim B: "WAL logs must be flushed before transaction commit."
  ├──► Claim C: "Connection pooling reduces backend fork overhead."
  └──► Claim D: "Under kernel 6.2, io_uring stalls on ext4 when journal commits collide."
```

When evaluated against a global knowledge corpus, the claim index yields a very clear picture:

```text
Claim A ──► Present in 100,000+ indexed documents (Consensus baseline)
Claim B ──► Present in 50,000+ indexed documents (Consensus baseline)
Claim C ──► Common reformulation of standard systems guidance
Claim D ──► No meaningful prior equivalent found across the temporal corpus
```

The document itself is largely redundant. The actual signal is isolated to `Claim D`.

Rather than treating the document as an atomic pass/fail artifact, ingestion pipelines must evolve toward granular extraction:

```text
Raw Ingestion
  ▼
Information Extraction
  ▼
Claim Clustering
  ▼
Novelty Detection
  ▼
Provenance Analysis
```

---

## Primary Information vs. Recombined Information

To score training value accurately, we have to distinguish between two distinct classes of data:

### Recombined Information

Knowledge reconstructed from claims that already exist in the corpus. This includes:

- Framework tutorials,
- Documentation summaries,
- Technical explainers,
- Derivative engineering blog posts,
- SEO landing pages,
- Most synthetic text generated by current LLMs.

This data follows a simple transformational path:

$$\text{Existing Knowledge} \xrightarrow{\text{Transformation}} \text{Secondary Content}$$

Secondary content can be helpful for refining conversational style, formatting, or pedagogy during supervised fine-tuning (SFT), but it contributes almost no new world knowledge to base model pre-training.

### Primary Information

Knowledge generated through direct interaction with physical or operational reality:

- Empirical experiment results,
- Production incident postmortems,
- Low-level kernel and hardware debugging traces,
- Profiling traces and performance benchmarks under stress,
- Detailed logs of failed implementation approaches,
- Industrial and scientific measurements,
- Real-world trade-offs discovered during system implementation.

This data follows an empirical path:

$$\text{Physical / Operational Reality} \xrightarrow{\text{Direct Observation}} \text{Primary Information}$$

This path captures boundary conditions, unpredicted system interactions, and empirical measurements that a model could not have derived theoretically from its training weights.

---

## Detecting Human-Written Text Is the Wrong Problem

Much of the industry has focused on building "AI vs. Human" text classifiers. For data curation, this frames the problem incorrectly.

A language model can easily fabricate text that mimics technical depth:

> "We deployed the system to production and observed a 17% reduction in CPU utilization across our worker fleet."

The sentence reads like an empirical engineering report. Yet it can be entirely synthesized without any underlying system having ever run. 

```text
Appears to be Primary Information ≠ Contains Primary Information
```

The engineering problem is not: *"Was this token sequence generated by a human keyboard or a transformer decoder?"*

The engineering problem is: *"Does this claim demonstrate verifiable provenance from an independent interaction with reality?"*

Detecting authorship is a game of stylistic cat-and-mouse. Verifying **information provenance** is an exercise in data validation, causal consistency, and citation auditing.

---

## Signs of Experiential Knowledge

Text reflecting first-hand operational contact with reality consistently exhibits distinct technical markers:

- **Specific environmental parameters**: Exact kernel versions, compiler flags, hardware configurations, network topologies, or runtime versions.
- **Asymmetric or counter-intuitive results**: Results that diverge from generic documentation or theoretical behavior.
- **Documented negative space**: Explicit catalogs of approaches that failed, timed out, leaked memory, or degraded throughput.
- **Empirical causal links**: Explanations derived from runtime instrumentation rather than first-principles assumptions.
- **Local constraint trade-offs**: Concessions forced by physical realities (e.g., thermal throttling, disk I/O saturating PCI lanes, database lock contention).

Compare these two statements:

> **Generic Formulation:**  
> "Increasing worker process concurrency can improve application request throughput up to the limit of available compute resources."

> **Experiential Formulation:**  
> "After scaling the service from 4 to 8 workers on an `m6i.2xlarge`, request throughput improved by only 12%. Profiling via `perf` showed that the bottleneck shifted directly to PostgreSQL connection pool contention; the application threads were spending 41% of their runtime blocked on `HikariCP` connection acquisition."

The first statement is generic, recombined theory. The second contains empirical state data: it links specific instance sizing, unexpected scaling curves, profiling tools, and an exact bottleneck. 

We can define this property as **experientiality**: the degree to which text bears the structural fingerprints of real-world friction.

---

## The Automated Media Radar: Mining Long-Form Transcripts

This challenge of isolating novel, experiential insights is not limited to web crawlers indexing text; it applies directly to how engineers consume long-form media (podcasts, conference panels, architecture deep-dives).

In modern media streaming, algorithms incentivize creators to maximize watch time and session duration. As a result, technical panels are routinely padded out to 60 or 90 minutes with introductory banter, recycled high-level generalities, and well-known industry consensus.

For an experienced engineer, a 60-minute technical discussion typically contains an asymmetric ratio: **roughly 1 to 2 minutes of genuine empirical signal** (e.g., an engineer mentioning an undocumented hardware behavior under high load, an obscure compiler bug, or a counter-intuitive production failure mode), surrounded by 58 minutes of conversational noise.

Rather than burning human attention on linear audio or video streams, an agent pipeline can act as an **Automated Media Radar**:

```text
60-Minute Technical Audio/Video Stream
         │
         ▼
[ Automated Audio-to-Text Pipeline (Whisper / Local STT) ]
         │
         ▼
Raw Transcript Stream
         │
         ▼
[ Personal Agent Diffing Engine ] ◄── Personal Knowledge Base (e.g., Obsidian)
         │
         ├──► DISCARD Consensus (K⁺): Known architecture principles (e.g., ~54 mins)
         ├──► DISCARD Known Bad (K⁻): Fallacies codified in rejection logs (e.g., ~4 mins)
         │
         ▼
Atomic Novelty Extract: S \ (K⁺ ∪ K⁻)
"At 42:15, speaker details a deterministic instruction cache invalidation 
issue when multiplexing async task handlers under high core concurrency on ARM64."
         │
         ▼
Structured Markdown Card Ingested into Knowledge Inbox (10-second human review)
```

### Operational Mechanics

1. **Continuous Audio Ingestion**: An always-on background worker (see [[Always-On Autonomous Agents - The 24-7 Local Operating System]]) monitors target technical feeds, downloading audio tracks and processing them through speech-to-text engines immediately upon release.
2. **Topological Claim Comparison**: The agent extracts atomic assertions from the transcript and compares them against the engineer's personal vault (using the techniques from [[How Personal AI Models Reconcile External Knowledge]]).
3. **Triaging the Information Space**:
   - **Consensus Space ($K^+$)**: Well-trodden architectural axioms are ignored or aggregated into a confidence counter.
   - **Known Anti-patterns ($K^-$)**: Discredited practices or buzzwords cataloged in [[Negative Knowledge and Explicit Architectural Dissents]] are filtered out immediately.
   - **Novel Signal ($S \setminus (K^+ \cup K^-)$)**: Unseen empirical claims, unique performance metrics, or unexpected edge cases are crystallized into isolated notes with exact timestamps and context.
4. **Attention Inversion**: The engineer stops passively consuming long-form content. The agent inverts the workflow: turning hours of ambient conversation into a short, high-density diff review.

---

## A Practical Knowledge-Mining Pipeline

Building a data curation system capable of identifying genuine technical novelty requires shifting from simple scrapers to an end-to-end knowledge-mining architecture:

```text
Raw Corpus (Web, Transcripts, Repositories)
                     │
                     ▼
             Semantic Indexing
                     │
                     ▼
             Claim Extraction
                     │
                     ▼
             Claim Clustering
                     │
                     ▼
        Temporal Provenance Analysis
                     │
                     ▼
             Novelty Estimation
                     │
                     ▼
            Credibility Scoring
                     │
                     ▼
           Training Value Scoring
```

### The Role of Temporal Provenance

The temporal dimension is critical to filtering out derivative noise. Consider the lifecycle of an engineering insight:

```text
2018 ──► Source A publishes original postmortem documenting issue X
2019 ──► Source B writes an analysis referencing X
2020 ──► 200 technical blog posts reword and summarize X
2023 ──► 5,000 AI-generated pages publish explanations of X
```

A naive web scraper that samples randomly across this corpus will assign roughly 99.9% of its training compute to downstream echoes of X. 

A pipeline with temporal provenance analysis traces the citation and timestamp topology back to the root:

- It recognizes that nearly 100% of the informational entropy originated with Source A in 2018.
- It identifies that the subsequent thousands of pages add zero marginal entropy.
- It downweights or drops the derivative iterations, keeping only the primary source and any later documents that introduced new empirical observations.

---

## The LLM Should Not Be the Database

It is tempting to think an LLM can evaluate claim novelty internally based entirely on its parametric memory:

> *"Ask the model if it already knows this fact."*

This approach fails at scale. Neural network weights are a lossy, distributed associative memory. They are effective at fuzzy pattern matching and generalized reasoning, but they make terrible provenance databases. A model cannot reliably distinguish between:

- A fact it knows with high certainty because it saw it 10,000 times,
- A fact it is hallucinating because of token-association probabilities,
- A claim that looks novel simply because the prompt framed it unconventionally.

A robust architecture decouples the reasoning engine from the index:

```text
┌────────────────────────────────────────────────────────┐
│                   Reasoning Engine                     │
│    (LLMs evaluated on claim extraction and logic)     │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                External Index Substrate                │
│  - Dense Semantic Vector Indices (HNSW / ScaNN)        │
│  - Publication Timestamps & Web Archive Snapshots      │
│  - Document Revision Histories (Git logs, edit deltas) │
│  - Citation & Inbound Link Graphs                      │
└────────────────────────────────────────────────────────┘
```

The LLM extracts structured claims from raw text. The external index verifies whether identical or semantically equivalent claims already exist in the historical record. 

This shifts data ingestion from passive text scraping to **knowledge archaeology**.

---

## Scoring Marginal Training Value

To filter pre-training and fine-tuning datasets programmatically, pipelines can score candidate data using a composite value function:

$$\text{TrainingValue} = \text{Novelty} \times \text{Credibility} \times \text{Experientiality} \times \text{InformationDensity} \times \text{DomainImportance}$$

### Evaluating the Components

- **Novelty**: The inverse frequency of the extracted claim across the historical corpus. High score = claim introduces unseen causal relationships or parameter combinations.
- **Credibility**: The reliability of the source environment. Scored via domain reputation, author verification, reproducible test cases, and internally consistent technical data.
- **Experientiality**: The density of operational markers—profiler outputs, real-world metrics, hardware telemetry, negative failure modes, and concrete constraints.
- **InformationDensity**: The ratio of atomic technical claims to total token count. High score = direct, unpadded documentation; low score = SEO fluff and conversational filler.
- **DomainImportance**: The relevance of the claim to target operational capabilities (e.g., systems programming, distributed debugging, hardware synthesis).

### Comparative Evaluation

#### Scenario A: Generic Web Tutorial

```text
Document: "Understanding Goroutines in Go"
Novelty:            Very Low (1/10)   - Thousands of equivalent explainers exist
Credibility:        Medium   (5/10)   - Accurate syntax, standard examples
Experientiality:    Very Low (1/10)   - Uses synthetic `time.Sleep()` demonstrations
InformationDensity: Low      (2/10)   - 1,500 words to communicate basic syntax
---------------------------------------------------------------------------------
Training Value: Negligible
```

#### Scenario B: Production Postmortem

```text
Document: "Postmortem: Goroutine Leak in Ingress Controller Under TLS Renegotiation"
Novelty:            High      (8/10)  - Documents an unindexed runtime edge case
Credibility:        High      (9/10)  - Production metrics, reproducible stack traces
Experientiality:    Very High (9/10)  - Core dump analysis, pprof traces, mitigation
InformationDensity: High      (8/10)  - Dense failure timeline and configuration diffs
---------------------------------------------------------------------------------
Training Value: Extremely High
```

Ten pages of internal engineering postmortems provide vastly more gradient information to an engineering model than 10,000 pages of standard web tutorials.

---

## Why Organizational Data Is High-Entropy

This value equation explains why private corporate repositories are becoming the most valuable training corpora on the planet (see [[The Most Valuable Software Training Data May Be Private]]).

Public web content is heavily incentivized toward marketing, brand management, and SEO. It tends to sanitize failure and present tidy, after-the-fact explanations.

Private engineering systems capture real-world friction as it happens:

- Git commit histories and pull request review debates,
- Incident management channels and outage timelines,
- Jira/Linear issue trackers detailing persistent, unsolved bugs,
- Architecture decision records (ADRs) with explicit trade-off analyses,
- Unfiltered production APM traces, memory profiles, and query plans,
- Customer support escalation threads detailing undocumented software behavior.

The public web follows a derivative path:

$$\text{Knowledge} \longrightarrow \text{Blog Post} \longrightarrow \text{Tutorial} \longrightarrow \text{Summary} \longrightarrow \text{SEO Variant}$$

Private operational data lives where raw systems collide with real-world constraints:

$$\text{Problem} \longrightarrow \text{Hypothesis} \longrightarrow \text{Failure} \longrightarrow \text{Instrumentation} \longrightarrow \text{Production Fix}$$

The latter path contains massive informational entropy. It captures systems failing at their operational boundaries, which is precisely the data required to teach models how to reason through complex, real-world failures.

---

## The Real Bottleneck: Fresh Contact With Reality

Early breakthroughs in large language models came from brute-force data scaling: throw larger web scrapes at wider transformer architectures. 

That strategy is hitting diminishing returns. The volume of new tokens generated every day is growing exponentially, but the volume of genuinely new information is not.

When AI systems train primarily on recursive loops of web text:

```text
Existing Corpus
      │
      ▼
Language Model
      │
      ▼
Synthetic Web Content (SEO blogs, summaries, automated pages)
      │
      ▼
Next-Generation Model Ingestion
```

The overall token volume scales continuously, but the underlying knowledge base stays flat. The data pipeline essentially trains on permutations of its own prior outputs.

The primary bottleneck for machine intelligence is not token availability. **The bottleneck is fresh contact with reality.**

---

## Building the Novelty Crawler

Traditional search engine spiders evaluate the web with two baseline questions:

- **Web Crawlers**: *"What URLs exist, and has their content changed?"*
- **Search Indices**: *"Which pages match this query, and which have the highest PageRank?"*

A modern training-data crawler operates on a fundamentally different question:

> *"Where did a genuinely new observation, measurement, or discovery enter the global information ecosystem?"*

This type of system behaves as a **novel knowledge miner**. It actively searches for:

- First reports of emerging software bugs and zero-day vulnerabilities,
- New, uncataloged hardware failure modes,
- Scientific benchmark anomalies,
- Direct telemetry from physical systems,
- Empirical engineering postmortems containing reproducible traces,
- Unprecedented combinations of systems constraints.

Its objective is to ignore the thousands of mirrors and find the single terminal where someone observed, measured, or debugged something that was not previously present in the corpus.

---

## The Reality Feedback Loop

This dynamic points toward a sustainable architecture for model improvement. As software engineers, researchers, and systems use LLMs to automate tasks, they run those models against external reality:

```text
Model Proposes Solution
         │
         ▼
System / Human Attempts Execution
         │
         ▼
[ Physical Reality / Compiler / Runtime ] ──► Returns Hard Failure or Success
         │
         ▼
Empirical Result Recorded (Traces, Errors, Fixes)
         │
         ▼
Curated as High-Entropy Training Data
         │
         ▼
Next-Generation Model Updated
```

The training signal here is not the model's generated output. **The signal is the collision between that output and the runtime environment.**

Failures are exceptionally high-signal training artifacts because they expose boundary conditions that were missing from the model's original world representation.

A closed loop of model-to-model synthetic text generation eventually degrades into statistical self-referential drift. But a loop anchored to empirical reality—where outputs are continuously tested against compilers, physical hardware, production runtimes, and verified user metrics—creates a continuous stream of genuine, high-entropy training data.

---

## Core Principles

1. **Information entropy over token volume**: Billions of tokens that repackage known claims offer negligible training value. Prioritize informational delta over surface-level prose length.
2. **Provenance over authorship classification**: Don't waste time trying to classify text as "human" or "synthetic." Focus on verifying whether the underlying assertions originate from genuine, reproducible interactions with reality.
3. **Claim-level indexing**: Decompose documents into discrete, verifiable claims. Discard boilerplate consensus and isolate the local anomalies, trade-offs, and failure logs.
4. **Decouple reasoning from storage**: Use the LLM to extract and analyze claims, but rely on an external, immutable, timestamped index to determine provenance and novelty.
5. **Reality is the scarce resource**: Raw content production is cheap and increasingly automated. Verified knowledge production—grounded in empirical observation, measurement, and operational failure—is rare, high-entropy, and the true foundation of model improvement.

---

## Technical Context & References

- [[The Most Valuable Software Training Data May Be Private]]: Explores why closed operational systems (incident logs, internal pull requests, architecture threads) contain the dense empirical signal the public web lacks.
- [[Always-On Autonomous Agents - The 24-7 Local Operating System]]: System architecture for running persistent, local background agents that ingest, transcribe, and diff external data streams.
- [[How Personal AI Models Reconcile External Knowledge]]: Mechanics of using personal knowledge bases to diff incoming content streams against an established worldview.
- [[Negative Knowledge and Explicit Architectural Dissents]]: The design rationale for explicitly logging anti-patterns, rejected approaches, and failures as first-class knowledge objects.
- [[How AI Breaks the Economic Model of the Open Web]]: Examines how the proliferation of synthetic web scraping breaks open web publishing incentives, driving the best operational data behind corporate firewalls.
