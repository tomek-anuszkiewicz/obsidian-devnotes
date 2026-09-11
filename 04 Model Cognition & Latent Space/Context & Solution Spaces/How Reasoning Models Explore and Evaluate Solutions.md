---
title: How Reasoning Models Explore and Evaluate Solutions
tags:
  - reasoning-models
  - llm
  - search-trees
  - evaluation
  - chain-of-thought
  - self-correction
aliases:
  - Reasoning Model Search Strategies
  - Solution Exploration and Verification in LLMs
---

# How Reasoning Models Explore and Evaluate Solutions

> [!IMPORTANT] Executive Architectural Thesis: Trajectory Exploration, Process Supervision, and Search Completeness
> Reasoning capability in frontier models is not a hard-coded symbolic algorithm; it is a **learned behavioral policy trained via test-time trajectory exploration and reinforcement learning**.  
> - **Search-Space Failure Outweighs Reasoning Failure**: An agent or evaluator model may evaluate candidates $A, B, C$ with flawless mathematical rigor; however, if the globally optimal architectural pattern $D$ was omitted during the initial expansion phase, the system commits a locally optimal failure.
> - **Outcome vs Process Supervision**: Outcome Reward Models (ORMs) verify only the destination, rewarding accidentally correct guesses that used broken logic. Process Reward Models (PRMs) score individual intermediate deduction steps, preventing error propagation.
> - **Tripartite Quality Partition**: Debugging reasoning breakdowns requires strictly isolating **Context Quality** (retrieval completeness), **Reasoning Quality** (deductive step integrity), and **Answer Quality** (synthesized communication).

```text
+----------------------------------------------------------------------------------------------------+
|               REASONING TRAJECTORY EXPLORATION & SUPERVISION TOPOLOGY                              |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ Problem Formulation & Grounded Context ]                                                        |
|                       │                                                                            |
|                       ▼                                                                            |
|  [ Trajectory Search & Expansion ]                                                                 |
|         │                                                                                          |
|         ├── Path A: [ Step 1 ] ──► [ Step 2 ] ──► [ Flawed Step 3 ] ──► [ Result A ]               |
|         │              │              │                 │                     │                    |
|         │              ▼              ▼                 ▼ (PRM Catches Drop)  ▼ (ORM Blind Pass)   |
|         │            PRM=0.9        PRM=0.8          PRM=0.1 ──► [Prune]     Outcome=True?         |
|         │                                                                                          |
|         └── Path B: [ Step 1 ] ──► [ Step 2 ] ──► [ Step 3 ] ───────► [ Result B ] (Optimal)       |
|                        │              │                 │                     │                    |
|                        ▼              ▼                 ▼                     ▼                    |
|                      PRM=0.95       PRM=0.98         PRM=0.99            Deterministic Pass        |
|                                                                                                    |
|  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ DECOUPLED EVALUATION PIPELINE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  |
|                                                                                                    |
|  [ Context Quality ] ────────► [ Search-Space Breadth ] ──────► [ Process-Step Verification ]      |
|  (Did RAG retrieve             (Did the search include           (Did PRMs and test oracles        |
|   all missing invariants?)      the global optimum D?)            verify intermediate deductions?) |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

## Executive Summary & Core Architectural Invariants

1. **Reasoning as Learned Policy, Not Hard-Coded Logic**:
   Chain-of-thought decomposition, assumption testing, and backtracking are emergent behavioral policies acquired through test-time search and reinforcement learning, rather than rigid, deterministic algorithms.

2. **The Primacy of Search-Space Completeness Over Evaluator Precision**:
   Evaluating candidates $A, B$, and $C$ with flawless mathematical rigor yields a sub-optimal solution if the globally optimal architectural pattern $D$ was omitted during initial candidate expansion. Search-space deficiency dominates reasoning failure in complex architecture.

3. **Superiority of Process Supervision Over Outcome Supervision**:
   Outcome Reward Models (ORMs) evaluate only the final output, creating severe vulnerabilities to reward hacking and accidentally correct answers derived from hallucinated logic. Process Reward Models (PRMs) score every intermediate deductive step, isolating logical errors at the point of origin.

4. **Tripartite Separation of System Failure Modes**:
   Diagnosing reasoning breakdowns requires isolating three distinct orthogonal stages: *Context Quality* (completeness of retrieved invariants), *Reasoning Quality* (deductive step integrity), and *Answer Quality* (synthesizing and communicating conclusions).

5. **Decoupling Candidate Generation from Verification**:
   Frontier models exhibit an asymmetry between generation and verification: they often fail to independently generate optimal counter-intuitive patterns, yet can reliably verify, critique, and select them when presented as candidate alternatives. Production harnesses must decouple generation, critique, and verification into distinct passes.

---

Reasoning quality depends not only on whether a model can follow a promising path, but also on whether it explores enough alternatives, evaluates them well, and verifies the final choice.

## 1. Reasoning Itself Is Learned Behavior

Planning, decomposing a problem, checking assumptions, exploring alternatives, and backtracking are not hard-coded algorithms; as explored in [[How Modern LLM Systems Build Context, Reason, and Stay Constrained|how modern LLMs build context and reason]], they represent learned cognitive behaviors.

They can emerge through training, forming the basis of [[Improving AI Models - From Scaling to Agent-Generated Training Data|agent-generated reasoning data and test-time compute]].

The model may learn patterns such as:

```text
understand problem (drawing on [[How Context Narrows an AI's Solution Space|context constraints]])
→ identify unknowns
→ decompose problem
→ generate hypotheses
→ test them
→ detect contradiction
→ try another approach
→ verify result
```

because training rewarded reasoning patterns that produced better outcomes.

---

## 2. Training Can Explore Multiple Reasoning Paths

When exploring alternatives, models must balance creative hypothesis generation against [[AI, Averaged Decisions, and Premature Convergence on Solutions|premature convergence on averaged solutions]]. For a single problem, training may generate multiple candidate trajectories:

```text
problem
 ├── reasoning A → result A
 ├── reasoning B → result B
 ├── reasoning C → result C
 └── reasoning D → result D
```

An evaluator can then assign rewards:

```text
A → 0.2
B → 0.95
C → 0.6
D → 0
```

Training does not literally memorize:

> Use path B for this exact question.

Instead, model parameters are adjusted so that behaviors associated with successful trajectories become more likely on future problems.

---

## 3. Evaluating Reasoning Is Hard

There are two basic approaches.

### Outcome supervision

Only the final answer is checked.

```text
reasoning
   ↓
final answer
   ↓
correct / incorrect
```

This works well when there is a strong verifier.

Examples:

```text
math → check result
code → run tests
SQL → execute query
chess → use engine
planning → run simulation
```

But a correct result can occasionally come from flawed reasoning.

---

## 4. Process Supervision Evaluates Intermediate Steps

Instead of only evaluating the answer, the system can evaluate the reasoning path itself.

Example:

```text
step 1 ✓
step 2 ✓
step 3 ✗
step 4 ✗
```

A Process Reward Model can learn to score such reasoning.

This helps distinguish:

```text
good reasoning → good result
```

from:

```text
bad reasoning → accidentally good result
```

---

## 5. Models Can Evaluate Other Models

Where deterministic verification is impossible, another model can act as a judge.

```text
generator model
      ↓
candidate reasoning
      ↓
judge model
      ↓
score
```

The judge might evaluate:

```text
correctness
logical consistency
unsupported assumptions
coverage of alternatives
tool usage
uncertainty handling
efficiency
```

This makes evaluation scalable.

But it introduces another problem:

> What if the judge has the same blind spots as the generator?

---

## 6. Search-Space Failure Can Be Worse Than Reasoning Failure

Suppose the model proposes:

```text
A
B
C
```

and the judge correctly concludes:

```text
B is best.
```

But the genuinely best solution was:

```text
D
```

which was never generated.

Then the evaluator performed perfectly on the wrong search space.

This suggests that strong agents need to separate:

```text
1. search
2. critique
3. evaluation
4. verification
5. selection
```

instead of simply:

```text
generate → judge → answer
```

A model may be very good at evaluating a solution once someone mentions it, while still being bad at discovering that solution independently.

---

## 7. Context Retrieval Has the Same Failure Mode

The same problem occurs before reasoning even starts.

Imagine the real relevant information is:

```text
A B C D E
```

but retrieval returns:

```text
A B C
```

The model can reason perfectly over A, B, and C and still reach the wrong conclusion.

Therefore there are at least three separate quality problems:

```text
CONTEXT QUALITY
Did the system retrieve the right information?

REASONING QUALITY
Did the model analyze it correctly?

ANSWER QUALITY
Did it communicate the conclusion correctly?
```

A bad answer does not necessarily mean that the reasoning model itself was weak.

The system may simply have provided the wrong context.

---

## Relationship to the Knowledge Graph

- **[[AI, Averaged Decisions, and Premature Convergence on Solutions]]**: Explores how models prematurely converge on conventional solutions instead of exploring divergent solution trees.
- **[[How Context Narrows an AI's Solution Space]]**: Examines the interaction between contextual filtering and search space pruning.
- **[[Emergence, Latent Space Synthesis, and How Targeted Prompts Crystallize Insight]]**: How human engineering prompts act as search seeds that steer reasoning models toward novel intersections.
- **[[LLM Coding Agents Reliability]]**: Empirical analysis of where reasoning chains break down during multi-step software tasks.
- **[[Improving AI Models - From Scaling to Agent-Generated Training Data]]**: Details how reasoning models are trained on verifiable agent trajectories and process supervision.
