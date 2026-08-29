Reasoning quality depends not only on whether a model can follow a promising path, but also on whether it explores enough alternatives, evaluates them well, and verifies the final choice.

## 1. Reasoning Itself Is Learned Behavior

Planning, decomposing a problem, checking assumptions, exploring alternatives, and backtracking are not necessarily hard-coded algorithms.

They can emerge through training.

The model may learn patterns such as:

```text
understand problem
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

For a single problem, training may generate multiple candidate trajectories:

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
