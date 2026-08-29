A modern LLM system is not just a model that receives a question and immediately generates an answer.

A more useful mental model is:

```text
user request
    ↓
context preparation
    ↓
reasoning / search
    ↓
candidate answer
    ↓
verification / policy checks
    ↓
final answer
```

The quality of the final response therefore depends not only on the raw intelligence of the model, but also on how the surrounding system prepares information, explores possible solutions, verifies results, and enforces higher-level rules.

---

## 1. The Model Does Not Start With an Empty Context

When a user asks a question, the model may receive substantially more information than the visible prompt.

The effective context may include:

```text
- platform and system instructions
- developer or application instructions
- the current user request
- previous messages in the conversation
- selected memories about the user
- relevant information from previous conversations
- retrieved documents
- web search results
- tool outputs and API responses
- current metadata such as time or environment
```

Conceptually:

```text
                    ┌─ system instructions
                    ├─ application instructions
                    ├─ current conversation
                    ├─ memory
USER QUESTION ──────┼─ previous conversation retrieval
                    ├─ RAG
                    ├─ web search
                    ├─ tools / APIs
                    └─ metadata
                             ↓
                       context window
                             ↓
                           model
```

This means that many apparent "model capabilities" are actually capabilities of the whole system around the model.

---

## 2. Some Knowledge Is Inside the Model, Some Is Retrieved

The model itself contains knowledge acquired during training.

For stable questions, such as:

> What is TCP?

it may answer directly from what has been encoded in its parameters.

But the model cannot rely on its internal knowledge for everything.

For recent, private, specialized, or highly detailed information, the system may perform retrieval.

---

## 3. Parametric Knowledge Has Uneven Reliability

Knowledge stored in model parameters is not equally reliable across all topics.

Some concepts appear frequently and consistently in training data, so the model may have a strong internal representation of them. Other facts may belong to the long tail of the training distribution: rare hardware details, obscure APIs, niche historical facts, unusual legal provisions, or highly specialized technical behavior.

Conceptually:

```text
frequent, consistent knowledge
→ stronger parametric representation
→ lower need for external grounding

rare, specialized, conflicting knowledge
→ weaker or less stable representation
→ greater value from retrieval and verification
```

This does not mean that the model has a simple internal meter saying:

> I know this fact with 92% confidence.

A model may show signals of uncertainty, but these signals are imperfect. In particular, it can produce a plausible-looking answer in a weakly represented area without realizing that one detail is wrong.

This is one source of subtle or "soft" hallucinations:

```text
mostly correct structure
+ plausible terminology
+ one invented or slightly incorrect detail
→ convincing but unreliable answer
```

Retrieval helps by moving part of the burden from parametric memory to explicit evidence.

```text
model knowledge
+ retrieved documentation
+ current sources
+ tool results
→ grounded answer
```

The model weights are not strengthened or updated during this process. The retrieved information is added to the current context so that the model can reason over it.

For this reason, retrieval is particularly valuable when a question is:

- rare or highly specialized,
- easy to confuse with similar facts,
- dependent on exact values, flags, versions, or dates,
- current or rapidly changing,
- controversial or supported by conflicting sources,
- costly to answer incorrectly.

A useful rule of thumb is:

> The more specific, niche, and externally verifiable a claim is, the more valuable grounding becomes.

This also suggests a reliability hierarchy for many factual tasks:

```text
1. tool-derived evidence
   compiler, test, API, database query, measurement

2. retrieved evidence
   documentation, authoritative sources, RAG, web search

3. parametric knowledge
   what the model remembers from training
```

The hierarchy is not absolute, but for concrete factual claims it is often safer to verify than to rely on memory alone.

---

## 4. Web Search Is a Form of External Retrieval

When the model searches the web, the process can roughly be thought of as:

```text
question
   ↓
search query
   ↓
search index / web sources
   ↓
selected documents or snippets
   ↓
model context
   ↓
reasoning
```

The model does not necessarily download every page directly.

The search system may use:

- search indexes,
    
- cached copies,
    
- crawled documents,
    
- snippets,
    
- external search providers,
    
- direct page retrieval.
    

A publisher may also prevent particular AI crawlers from indexing its content.

This creates an important tension:

```text
allow AI indexing
→ greater visibility in AI answers
→ potentially fewer direct visits

block AI indexing
→ retain more control
→ potentially disappear from AI-driven discovery
```

The old SEO problem is therefore gradually becoming a broader problem of optimizing information for AI retrieval and answer systems.

---

## 5. Conversation History Is Another Source of Context

The current conversation is usually one of the strongest contextual signals.

Instead of answering:

```text
isolated prompt → response
```

the system can answer:

```text
conversation so far
+
new message
→ response
```

However, context windows are finite.

For long conversations, systems may need to:

- retain recent messages directly,
    
- summarize older parts,
    
- retrieve only relevant fragments,
    
- discard information that appears irrelevant.
    

So a model does not necessarily receive the entire raw history of a long conversation on every turn.

---

## 6. Memory and Previous Conversations Behave Like Retrieval

Information from older conversations can be handled similarly to RAG.

Rather than loading every historical conversation, a system can retrieve relevant facts.

Conceptually:

```text
years of conversations
        ↓
retrieval
        ↓
relevant facts
        ↓
current context
```

For example:

```text
user works mainly with .NET
user prefers modular monoliths
the previous discussion concerned agentic code review
```

may be enough context for the current question.

This makes personal memory effectively another knowledge source available to the agent.

---

## 7. RAG Extends the Model With External Knowledge

In a company environment, the same principle can be applied to:

```text
Git repositories
Jira
Confluence
architecture documents
meeting transcripts
incident reports
product specifications
databases
```

Suppose someone asks:

> Why does the payment retry mechanism behave like this?

A useful agent might perform:

```text
question
   ↓
find payment module
   ↓
find architecture decision
   ↓
find related Jira tickets
   ↓
find recent implementation changes
   ↓
retrieve relevant code
   ↓
reason
```

The naive form of RAG:

```text
question embedding
→ nearest 10 text chunks
→ LLM
```

is therefore only the simplest version.

More advanced retrieval can use:

- semantic similarity,
    
- keyword search,
    
- metadata,
    
- dependency graphs,
    
- document hierarchy,
    
- timestamps,
    
- authorship,
    
- source code structure,
    
- previous retrieval results.
    

---

## 8. Reasoning Can Control Retrieval

The system does not have to collect all information before reasoning begins.

Instead, reasoning and retrieval can form a loop:

```text
initial context
      ↓
reason
      ↓
"I am missing X"
      ↓
retrieve X
      ↓
reason again
      ↓
"I should verify Y"
      ↓
retrieve Y
      ↓
continue
```

This produces a more agent-like process:

```text
REASON
  ↓
RETRIEVE
  ↓
REASON
  ↓
RETRIEVE
  ↓
VERIFY
```

The model can therefore actively decide what information it needs.

For example:

> Why did latency increase after the latest deployment?

An agent might create subquestions:

```text
What changed in the deployment?
Which endpoints became slower?
Did database latency change?
Did resource limits change?
Was an external dependency affected?
```

and then query:

```text
Git
logs
metrics
deployment configuration
tickets
architecture documentation
```

before reaching a conclusion.

---

## 9. Reasoning Itself Is Learned Behavior

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

## 10. Training Can Explore Multiple Reasoning Paths

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

## 11. Evaluating Reasoning Is Hard

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

## 12. Process Supervision Evaluates Intermediate Steps

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

## 13. Models Can Evaluate Other Models

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

## 14. Search-Space Failure Can Be Worse Than Reasoning Failure

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

## 15. Context Retrieval Has the Same Failure Mode

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

## 16. Some Instructions Sit Above the User

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

## 17. Safety Is Not Implemented in One Place

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

## 18. Some Safety Behavior Is Trained Into the Model

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

## 19. Runtime Instructions Still Matter

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

## 20. Classifiers Can Inspect the Input

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

## 21. The Output Can Also Be Evaluated

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

## 22. A Safety Judge Can Be Another LLM

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

## 23. Why Multiple Layers Are Necessary

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

## 24. Some Rules Cannot Live Permanently Inside Model Weights

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

## 25. The Solution Space Is Narrowed by Jurisdiction, Culture, Language, and Local Norms

A model does not reason over every theoretically possible solution equally.

Before reasoning, the effective solution space is often narrowed by contextual factors such as:

```text
- country and jurisdiction
- language
- culture
- local social norms
- professional conventions
- organizational rules
- industry standards
```

This narrowing is often necessary.

For example, if a user asks for legal advice in Poland, the agent should not reason over a generic mixture of Polish, US, German, and UK law.

A better process is:

```text
user question
    ↓
determine jurisdiction
    ↓
Poland
    ↓
retrieve current Polish legal sources
    ↓
reason within Polish law
    ↓
answer
```

The same applies to other domains.

A question about employment, taxation, healthcare, construction, business registration, or consumer rights may have completely different valid answers depending on the country.

---

### Jurisdiction Is a Hard Contextual Filter

Legal constraints should be treated differently from cultural preferences.

For example:

```text
all technically possible solutions
            ↓
Polish law
            ↓
legally available solutions
```

A solution that is common in another country may simply not exist in the local legal system.

Therefore an agent should first determine:

```text
Which jurisdiction applies?
What is the relevant date?
Which regulations are currently in force?
```

Only then should it perform detailed reasoning.

Language can be a useful signal, but it is not enough.

A Polish-language question does not necessarily mean that Polish law applies, just as an English-language question does not necessarily imply US law.

The system should use stronger evidence when available:

```text
explicit country
user location
type of institution
company location
contract jurisdiction
currency
legal terminology
previous context
```

If jurisdiction remains ambiguous and materially affects the answer, it should be treated as an unresolved variable rather than silently assumed.

---

### Current Law Should Be Retrieved, Not Merely Remembered

Law is a particularly important example because it changes over time.

The model may have learned a general structure of Polish law during training, but that does not guarantee that its internal knowledge reflects the current legal state.

A robust agent should therefore use:

```text
model knowledge
+
jurisdiction
+
current date
+
current authoritative sources
```

rather than relying only on model memory.

Conceptually:

```text
legal question
    ↓
identify jurisdiction
    ↓
identify relevant legal domain
    ↓
retrieve current legislation / authoritative sources
    ↓
reason
    ↓
answer
```

This reduces two different errors:

```text
wrong jurisdiction
and
outdated law
```

---

### Culture Is a Softer Filter

Culture works differently.

It does not usually determine whether something is legally possible.

Instead, it influences what appears normal, reasonable, polite, practical, or socially acceptable.

For example, the same workplace problem may produce different default recommendations depending on local expectations around:

```text
management hierarchy
working hours
employee autonomy
negotiation
privacy
directness
social benefits
```

So the model may effectively reason over:

```text
technically possible
    ↓
legally possible
    ↓
culturally plausible
    ↓
socially acceptable
    ↓
recommended solutions
```

This is useful because advice should normally fit the user's environment.

But it also creates a risk.

The model may mistake:

```text
"this is uncommon here"
```

for:

```text
"this is not a valid solution"
```

---

### Language Changes the Prior, but Should Not Define Reality

Different languages expose the model to somewhat different distributions of training data.

A question asked in Polish may more readily activate:

```text
Polish institutions
Polish terminology
Polish examples
local social assumptions
```

while the same question in English may more strongly activate international or US-centric material.

This is useful as a prior.

But language should not become a hard constraint.

The correct relationship is:

```text
language
→ useful clue about context

not

language
→ automatic jurisdiction
```

---

## 26. Hard and Soft Contextual Constraints Should Be Separated

A strong agent should distinguish between constraints that genuinely limit the solution space and constraints that merely influence what is conventional.

### Hard constraints

```text
physics
mathematics
current law
contractual obligations
available resources
security restrictions
```

### Soft constraints

```text
culture
social convention
industry habit
organizational preference
architectural fashion
"this is how we normally do it"
```

This distinction matters because good reasoning sometimes requires challenging a soft constraint.

For example:

```text
"We cannot do X."
```

may actually mean:

```text
"We normally do not do X."
```

Those are very different statements.

---

## 27. Context Can Narrow the Solution Space Correctly or Incorrectly

The same mechanism that makes an answer locally relevant can also hide good alternatives.

Consider:

```text
all possible solutions
         ↓
country
         ↓
law
         ↓
culture
         ↓
organization
         ↓
professional convention
         ↓
candidate solutions
         ↓
reasoning
```

Some of these filters are desirable.

For a Polish legal question, removing non-Polish legal solutions is correct.

For an architectural question, however, removing an unusual design simply because it is uncommon may be a mistake.

The agent therefore needs to know not only:

> What constraints exist?

but also:

> Why does each constraint exist, and is it actually binding?

---

## 28. A Better Context-Aware Reasoning Process

For problems strongly dependent on local context, a better workflow is:

```text
1. Identify the relevant context.
   - country
   - jurisdiction
   - language
   - organization
   - industry
   - date

2. Separate hard constraints from soft norms.

3. Retrieve current external information where necessary.

4. Generate solutions within the hard constraints.

5. Identify which solutions were excluded only because of convention.

6. Challenge those soft assumptions when useful.

7. Evaluate the remaining alternatives.

8. Answer in the user's local context.
```

This produces an important distinction:

```text
LOCALIZATION
"What answer fits this user's environment?"

vs.

CONSTRAINT VALIDATION
"Which parts of that environment truly limit the solution?"
```

A good agent needs both.

---

## 29. Context Failure Is Another Distinct Failure Mode

This adds another failure category to the overall model.

An AI system can fail because:

```text
1. it retrieved the wrong information,
2. it reasoned incorrectly,
3. it evaluated the alternatives badly,
4. it failed to generate an important alternative,
5. or it applied the wrong contextual frame.
```

The fifth case includes situations such as:

```text
using US law for a Polish legal question
using outdated Polish law
assuming US workplace norms in Europe
assuming enterprise conventions for a startup
treating a cultural habit as a technical limitation
```

So before asking whether the model's reasoning was correct, it is sometimes necessary to ask:

> Was it reasoning inside the correct world?
# The Full Agent Loop

Putting everything together gives a more realistic architecture:

```text
                       USER PROBLEM
                            │
                            ▼
                    POLICY / SAFETY
                       PRE-CHECK
                            │
                            ▼
                    CONTEXT PLANNING
                  What information is needed?
                            │
       ┌────────────────────┼─────────────────────┐
       ▼                    ▼                     ▼
 conversation             memory                 RAG
 history                    │                     │
       │                    │                     │
       ├──────────────┬─────┴─────────────┬───────┤
       ▼              ▼                   ▼       ▼
     web            tools              APIs      code
       │              │                   │       │
       └──────────────┴──────────┬────────┴───────┘
                                 ▼
                         CONTEXT ASSEMBLY
                                 │
                                 ▼
                              REASON
                                 │
                    ┌────────────┴─────────────┐
                    │ missing information?    │
                    └────────────┬─────────────┘
                                 │
                               yes
                                 ↓
                           more retrieval
                                 │
                                 ↺
                                 │
                                 ▼
                      generate alternatives
                                 │
                                 ▼
                              critique
                                 │
                                 ▼
                            verification
                                 │
                                 ▼
                              selection
                                 │
                                 ▼
                         candidate answer
                                 │
                                 ▼
                    safety / policy evaluator
                                 │
                                 ▼
                            FINAL ANSWER
```

---

# The Important Shift in Perspective

It is increasingly misleading to think of an AI system as:

```text
prompt → LLM → answer
```

A better model is:

```text
prompt
   ↓
context selection
   ↓
retrieval
   ↓
reasoning
   ↓
additional retrieval
   ↓
solution-space exploration
   ↓
critique
   ↓
verification
   ↓
policy enforcement
   ↓
answer
```

The "intelligence" of the system is therefore distributed across several components.

A better model alone may improve the system, but so can:

- better context retrieval,
    
- better memory,
    
- better search,
    
- better reasoning strategies,
    
- better exploration of alternatives,
    
- better evaluators,
    
- better tools,
    
- better verification,
    
- better safety and policy enforcement.
    

The future progress of AI agents may therefore come as much from improving this entire loop as from increasing the raw capability of the underlying language model.
