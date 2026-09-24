---
title: How LLM Systems Enforce Safety and Higher-Level Instructions
tags:
  - safety
  - llm
  - alignment
  - instruction-hierarchy
  - guardrails
  - system-prompts
aliases:
  - Safety Guardrails in LLMs
  - Instruction Hierarchy and Policy Enforcement
---

Safety and higher-level constraints are not implemented in one place. They can come from trained behavior, instruction hierarchy, runtime policy, classifiers, evaluators, and tool restrictions.

Relying exclusively on a system prompt breaks down against adversarial jailbreaks; relying exclusively on post-training alignment fails when enterprise policies and legal statutes change faster than training runs; and relying purely on output filters fails because unsafe tool actions may have already executed. Production governance splits safety across parametric alignment, context hierarchies, pre-inference classifiers, deterministic execution sandboxes, and post-inference evaluators.

## 1. Some Instructions Sit Above the User

Another source of context consists of instructions that the user is not supposed to override.

Examples include rules concerning:

```text
safety
harmful instructions
privacy
legal or policy constraints
abusive behavior
tool permissions
instruction hierarchy
```

Conceptually:

```text
platform / system rules
        ↓
application instructions
        ↓
user instructions
        ↓
retrieved content
```

A user can ask the model to behave differently, but lower-level instructions should not override higher-level rules.

These instructions are "immutable" from the user's perspective, although they are not necessarily literally embedded as immutable code inside the neural network.

Context assembly is not a flat string where every token carries equal authority. In [[How LLM Systems Build Context]], runtime input must be organized into an explicit hierarchy. Retrieved external documents (such as web search results or RAG context) must be treated as untrusted data, never as executable control instructions.

When context windows are loaded with competing or contradictory constraints across different levels, models can exhibit [[Constraint Saturation and Rule Oscillation in Coding Agents]], thrashing between conflicting instructions. Keeping behavior predictable requires establishing the platform layer as authoritative and immutable from the user's perspective.

---

## 2. Safety Is Not Implemented in One Place

A common misconception is that safety behavior comes from a single hidden prompt such as:

```text
Never answer dangerous questions.
```

In practice, a robust system can use several layers.

```text
                    user request
                         ↓
                 input classifier
                         ↓
                system instructions
                         ↓
                      model
                         ↓
                candidate response
                         ↓
                output evaluator
                         ↓
                     user
```

This is defense in depth.

Because LLMs are probabilistic sequence predictors, relying on a single prompt directive easily breaks down against roleplay framing, encoded payloads, or nested hypothetical questions. A robust defense-in-depth architecture splits governance between probabilistic controls (system prompts, parametric alignment, LLM judges) and deterministic controls (sandboxes, network egress rules, and strict API token scoping).

---

## 3. Some Safety Behavior Is Trained Into the Model

Post-training can make safe behavior intrinsically more likely.

The model can learn patterns such as:

```text
dangerous operational request
→ refuse the dangerous part
→ provide safe adjacent information
```

rather than needing a runtime rule for every possible situation.

This makes safety more robust than relying exclusively on prompt instructions.

Post-training techniques like RLHF, DPO, and Constitutional AI embed refusal reflexes directly into the model weights. Confronted with direct exploit requests, the model's base probability distribution favors refusal regardless of prompt manipulation. The main engineering challenge here is avoiding over-refusal: coarse alignment blocks benign operational tasks like killing a hung process or analyzing a synthetic vulnerability. A properly aligned model refuses the actionable exploit while providing the safe, adjacent technical mechanics.

---

## 4. Runtime Instructions Still Matter

Some constraints are easier to change as instructions than by retraining the entire model.

For example:

```text
current policy
product-specific restrictions
tool permissions
organization rules
temporary restrictions
```

These can be supplied to the model at runtime.

This is especially important for rules that may change frequently.

Updating weights via fine-tuning is slow, expensive, and difficult to audit. Conversely, runtime instructions can be updated in milliseconds. If an enterprise disables a specific database tool or legal updates disclosure terms for a specific jurisdiction, those changes are injected at runtime via prompt wrappers, avoiding costly retraining cycles.

---

## 5. Classifiers Can Inspect the Input

A separate model or classifier can evaluate the request before the main model sees it.

For example:

```text
request
   ↓
classifier
   ↓

low risk
→ normal flow

elevated risk
→ stronger constraints

prohibited category
→ restricted response
```

This classifier does not need to be the same model that generates the answer.

A dedicated input guardrail model—typically a fast cross-encoder, a small language model, or a lightweight classification head—scans inbound prompts for jailbreak patterns and prompt injections. Dropping malicious requests at ingress avoids burning latency and token budget on large reasoning models. Classifiers also inspect untrusted third-party documents fetched during RAG before injecting them into the context window, neutralizing indirect prompt injection attacks before they reach the primary model.

---

## 6. The Output Can Also Be Evaluated

Checking only the user's intent is not enough.

A seemingly harmless request can generate an unsafe answer, while a sensitive topic can sometimes be discussed safely.

So the system can instead evaluate:

```text
USER REQUEST
+
GENERATED RESPONSE
+
POLICY
```

and ask:

```text
Is this response allowed?
Does it contain harmful operational detail?
Did it unnecessarily refuse?
Can it be made safer while remaining useful?
```

This allows more nuanced behavior than simply classifying entire topics as allowed or forbidden.

Evaluating the full triplet handles nuances that simple keyword blocklists miss. A request asking how attackers exploit unquoted service paths might trigger basic keyword filters, but if the response explains the theoretical mechanics and remediation steps without providing a copy-paste exploit script, an output evaluator can safely approve it.

### Deterministic Sandboxes and Tool Boundaries

When an agent has access to external tools—such as shell execution, database clients, or file APIs—evaluating text output after the fact is completely inadequate (see [[LLM Capability, Reliability, and the Shape of Progress]]). If an agent executes a destructive tool call, checking the final conversational output cannot reverse the mutation.

Safety checks for autonomous systems must intercept tool actions before execution:

```text
model generates tool call
          ↓
deterministic parameter validation & policy gate
          ↓
execution inside hard sandbox (cgroups / read-only FS / restricted network)
          ↓
tool result returned to context
```

Mechanical controls enforce the boundary:
- **Isolated Execution Environments**: Shell and code execution run inside ephemeral containers with strict CPU/memory quotas, unprivileged non-root users, and read-only filesystems.
- **Least-Privilege Scoping**: Database and API access use scoped credentials tied to the authenticated user rather than broad service keys ([[Service vs User Authorization Models]]).
- **Tool Parameter Schema Validation**: Disallowed paths, out-of-range parameters, or unauthorized target addresses are blocked deterministically via strict schemas (such as Pydantic or JSON Schema) before the network or operating system handles the call.

---

## 7. A Safety Judge Can Be Another LLM

The architecture can therefore look like:

```text
main model
   ↓
candidate answer
   ↓
safety judge
   ↓
allow / modify / refuse
```

The judge may itself be trained specifically to interpret policy.

In more complex systems, several specialized evaluators may exist:

```text
security evaluator
privacy evaluator
safety evaluator
quality evaluator
tool-permission evaluator
```

The main model is therefore only one component in a larger decision system.

When an evaluator flags a violation, the system typically takes one of three paths:
1. **Hard Refusal**: Return a deterministic fallback message to the user.
2. **Redaction**: Mask or strip leaked PII, API tokens, or operational secrets while keeping the rest of the response intact.
3. **Self-Correction Loop**: Route the rejection reason back into the main model as a steering directive to regenerate a compliant answer.

---

## 8. Why Multiple Layers Are Necessary

Every approach has failure modes.

### Only training

The model may encounter:

```text
new jailbreaks
new situations
distribution shift
ambiguous requests
```

### Only instructions

The model may misinterpret or fail to follow them.

### Only classifiers

They produce false positives and false negatives.

### Only output checking

Unsafe intermediate tool actions could already have happened.

### Only deterministic sandboxing

Sandboxes protect compute and network perimeters, but cannot prevent toxic outputs, data exfiltration through user-facing text, or hallucinated logic.

Therefore a stronger design is:

```text
training
+
instruction hierarchy
+
input checks
+
tool restrictions
+
output evaluation
+
monitoring
```

---

## 9. Some Rules Cannot Live Permanently Inside Model Weights

Rules such as:

> Do not provide illegal instructions.

sound simple but depend on:

```text
country
jurisdiction
date
age
licensing
context
purpose
```

Law changes faster than model weights.

Therefore the system may require:

```text
stable learned behavior
+
current instructions
+
current external information
```

Attempting to bake jurisdiction-specific compliance laws directly into neural weights guarantees obsolescence within months. The system architecture must decouple stable foundation reasoning and safety reflexes (in weights) from dynamic jurisdictional rules, licensing limits, and organizational policies (in context and deterministic policy engines). This separation keeps the system compliant, auditable, and maintainable over time.

## Related notes

- **[[Service vs User Authorization Models]]** — Preventing agent privilege escalation across tool calling and API integration layers.
- **[[Proxy Metrics and Operational Invariants in AI Systems]]** — Designing deterministic checks and invariant validation over probabilistic classifiers.
- **[[LLM Capability, Reliability, and the Shape of Progress]]** — Externalizing reliability from model weights into deterministic harnesses.
- **[[Formal Verification and Runtime Safety Boundaries]]** — Mathematical and schema-based verification replacing probabilistic evaluation.
