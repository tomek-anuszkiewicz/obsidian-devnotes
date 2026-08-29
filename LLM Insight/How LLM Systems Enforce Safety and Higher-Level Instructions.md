Safety and higher-level constraints are not implemented in one place. They can come from trained behavior, instruction hierarchy, runtime policy, classifiers, evaluators, and tool restrictions.

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

The same is true for many organizational policies and compliance requirements.

---
