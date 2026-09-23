---
title: Token Optimization and Context Economics in Agentic Workflows
tags:
  - ai-agents
  - agentic-workflows
  - token-economics
  - context-engineering
  - system-design
  - prompt-caching
  - software-economics
  - developer-experience
aliases:
  - Token Economics in Agentic Workflows
  - Context Economics and Token Conservation
  - The Attentional Physics of Agentic Coding
  - Minimizing Token Burn in Autonomous Software Engineering
  - Subagent IO Tax and Context Hygiene
---

# Token Optimization and Context Economics in Agentic Workflows

> [!IMPORTANT]
> **Tokens affect what an agent sees, not just what you pay.** A large context costs money and makes it harder for the agent to keep the relevant code, constraints, and current decision in view. Longer sequences also increase the work involved in attention. Treat the context window as working memory that you fill deliberately.
>
> A useful working target is to spend roughly 80% of the budget on implementation, focused diffs, and verification, and no more than 20% on open-ended design and exploration. If the agent spends most of its time wandering through files, reading stale documentation, or debating a local variable name, fix the workflow.
>
> The practical tools are straightforward: match model and reasoning budget to the task; keep related code close together; give the agent a few clear rules; run deep checks at useful milestones; keep subagent output short; reuse identical results; and put repetitive work in scripts.

The rest of this note follows four parts of that workflow:

| Part | What belongs there |
| :--- | :--- |
| Decisions and steering | Stronger models for difficult design choices, short plans, explicit constraints, and a pause before broad changes. |
| Finding the right information | Code graphs, targeted upstream documentation, and tools loaded when needed. |
| Execution | Local scripts, cohesive feature code, fresh task sessions and worktrees, and tightly scoped subagents. |
| Inference and caching | Provider prompt caches, exact-match team caches, and, where appropriate, adapters for stable house style. |

---

## Where time and tokens disappear

Before changing inference settings, look at the habits that make an agent read or generate far more text than the task requires.

| Failure | What happens |
| :--- | :--- |
| Rule sprawl | Dozens of permanent instructions add thousands of tokens to repeated requests and compete for the agent's attention. |
| Checks on every tiny commit | The agent spends more time explaining or repairing checks against unfinished code than building the feature. |
| Long plans nobody reads | A four-page plan costs output tokens while the developer skips to the Git diff. |
| Style arguments | Several turns spent correcting a small naming or formatting choice cost more than editing it directly. |
| Starting too much at once | An agent changes ten files before the approach is settled; the team then pays to undo and redo the work. |
| Revisiting discarded work | A reverted commit draws the agent into investigating and reviving an approach that was already rejected. |
| Verbose subagent results | A child agent's large log consumes the parent agent's context. |
| Repository-wide refactoring too early | A bad assumption spreads through many files before the first useful failure appears. |

### Keep permanent rules short

After each agent mistake, it is tempting to append another rule to `RULES.md`. Two months later, 50 rules may occupy 6,000 tokens. Across 30 requests, that is up to `30 × 6,000 = 180,000` repeated input tokens, even before accounting for application code. Prompt caching can lower the charge for a stable prefix, but the text still occupies context.

The rules can also compete. With too many instructions, the agent may follow one and miss another, then change direction on the next turn. Keep the durable constraints that actually govern the work; put task-specific detail in the task.

### Write plans that developers will read

A developer can often inspect a colored Git diff faster than a four-page implementation essay. If the plan is too long, they click “Proceed” to see the code. The generated prose has then added latency and filled the conversation without helping the review.

For most tasks that need a plan, use around five bullets: which files will change, what interfaces must hold, what the implementation will do, and which commands will show whether it worked. Leave routine bug fixes and mechanical edits out of a heavyweight planning step.

### Edit small stylistic differences directly

Consider a six-turn exchange over a private variable name, brace placement, or a preferred builder pattern: the agent tries one shape, receives a correction, produces a hybrid, and finally breaks an import. Such an exchange can consume tens of thousands of tokens for a change a developer could make in seconds.

Let the agent do the substantial work: boilerplate, interfaces, tests, and wiring. If the remaining difference is a small local preference, edit that part directly. Save detailed instructions for conventions whose violation would actually affect the codebase.

### Keep failed experiments out of the next attempt

An agent that sees `Revert "add custom redis cache"` may inspect that diff, spend time explaining the failed design, and then bring it back. The old commit is useful history for a person, but it can distract an agent whose next task is already decided.

After an exploratory approach fails, start the next attempt from a clean worktree or reset the disposable branch if its changes can safely be discarded. Record the reason the approach failed in a short, explicit rule so the next agent does not rediscover it.

---

## Arrange the work so the agent can act with less context

### Match the model to the decision

Architecture and core invariants deserve a stronger model and more reasoning time. A localized bug, CSS adjustment, type import, or implementation of an approved plan often does not. Total cost includes input, output, and any billed reasoning tokens:

$$\text{Total cost} = \sum(\text{input tokens} \times \text{input price}) + \sum(\text{output tokens} \times \text{output price}) + \sum(\text{reasoning tokens} \times \text{reasoning price})$$

Use the stronger model to weigh difficult trade-offs and produce a short plan. Then use a faster model with little or no additional reasoning for the mechanical patch. Compile and run targeted checks. If a correction fails twice, stop and reconsider the missing assumption instead of looping. Straightforward fixes can start with execution immediately. This division applies to models and pricing where separate reasoning budgets and charges exist.

### Put code for one capability within reach

In a layered codebase, adding one order field may take the agent through a controller, command, validator, handler, entity, DTO, and mapper. An IDE makes those jumps cheap for a person. For an agent, each search and file read can be another tool call carrying the conversation context. Eight calls against a 25,000-token context can mean as many as `8 × 25,000 = 200,000` input tokens counted across requests, depending on the tool and caching setup.

A cohesive feature folder or a 150–500-line feature file can put the command, validation, domain rules, database projection, and errors near one another. The agent can read the relevant slice and patch it without eight speculative navigation steps. Do not take this to the opposite extreme: a 3,000-line file is hard to inspect and changes frequently enough to undermine reuse of a stable prompt prefix.

### Steer broad changes differently from local fixes

A small set of conditional rules is easier to apply than a large manual:

1. **Structural changes** to schemas, public APIs, or abstractions: propose two viable approaches, identify the affected code, and avoid local shims or monkey patches that hide the boundary change.
2. **Local fixes and mechanical edits**: make the smallest clear change; do not add abstractions or unrelated refactoring.

This gives the agent room to reason when foundations move and keeps it focused when the task is narrow.

### Run checks at the right cadence

Running the full test suite, static analysis, linting, and security checks after every tiny edit slows the loop and fills it with output about work still in progress.

Use a compiler or targeted module tests while editing. Run integration tests, broad lint checks, and architecture checks at a milestone, every chosen number of commits, or in a background job. These deeper checks still matter; they simply belong at a point where the code is stable enough to learn from their results.

### Give each task a fresh session

In a long conversation, old plans and discarded ideas remain in context. The agent may give them undue weight, and the repeated history costs tokens. Scope a session to one functional milestone. Once the work is verified, record concrete decisions in [[The Living Engineering Chronicle and Context Compaction|the engineering chronicle]], commit the code, and start the next task with a fresh session that points to those artifacts.

### Keep subagent results small

A subagent can read 20 files and run commands without putting those raw results in the parent agent's context. That benefit disappears if it returns a 3,000-word investigation.

Give the subagent a target path and a precise question rather than the full project roadmap. Ask for a diff, a status, or three factual bullets. For example, a child may spend 60,000 tokens investigating Bug #402 but return a 150-token finding to a parent whose context started at 4,500 tokens. Keep the raw logs in the child's task.

### Try a refactor on one piece first

Before changing dozens of files, apply the proposed refactor to one module, class, or service. Compile it, measure how much agent work it required, and inspect whether the result is actually easier to use. Only then repeat the pattern. A type mismatch found on file one is cheap; the same mismatch found after file fifteen can trigger a long chain of repairs.

---

## Use caching and ordinary tools where they fit

### Keep cacheable prompt content stable

Models maintain key/value data for tokens in context, and providers may cache shared prompt prefixes. A cache hit can reduce input charges and time to first token; the original note cites discounts of 75–90%, which depend on the provider and its terms. Longer contexts also take more memory for this cached state. The example estimates in the original note are about 0.5 GB at 2,048 tokens, 8 GB at 32,768, and 32 GB at 131,072 for a particular FP16 setup; actual figures depend on model architecture and deployment.

Prefix reuse works best when permanent instructions, tool descriptions, and stable repository information come first. Put the current diff, request, and other changing material later. A timestamp, process ID, or unstable file order near the beginning can prevent later requests from matching the cached prefix.

### Cache identical team requests by exact content

An internal inference gateway, backed for example by Redis or SQLite, can reuse results for genuinely identical requests across developers or CI runs. One possible key is:

```text
SHA256(Model_ID + Temperature + System_Prompt + Target_File_Hash + Instruction)
```

If the input and model settings are identical, a cached review can return quickly without another model call. Match exact bytes for code-sensitive tasks. A similarity cache might treat `if (ptr != null)` and `if (ptr == null)` as nearly the same text even though they have opposite behavior. Cache invalidation and the price of running the gateway still need to be counted; an exact hit avoids a new inference call.

### Let scripts do deterministic work

Do not ask a model to read a 4,000-line changelog, find the insertion point, and rewrite the entire file if a script can append one entry. In the example from the original note, that path cost about 80,000 tokens and 12 seconds, while calling `python scripts/append_log.py --entry "Refactored payment gateway"` required a short tool request and roughly 40 milliseconds of local work. The numbers illustrate the difference between generating text and executing a known operation.

Compilers, AST parsers, linters, and shell scripts should handle operations with clear rules. Give their concise results to the agent when a decision is needed.

### Search code structure when text search misses the relationship

Code is connected through calls, types, and interface implementations. A text search for “invoice processing” may miss a `StripeGateway` call in a file with different wording. A code graph built from AST information, such as a Graphify or Tree-sitter index, can answer a dependency question directly:

```text
GetDependencies(process_invoice) -> [OrderRepo, StripeClient, TaxCalculator]
```

A small graph result can replace a run of speculative searches and file reads. Vector search still helps find text, but the graph is the better fit when the question is “what calls this?” or “what does this depend on?”

### Expose focused tools through MCP

MCP gives an agent a consistent way to call tools while the implementation can be a local AST script, a Redis cache, a dependency graph, or a documentation lookup. The agent needs the tool signature and a compact result; it does not need to read the script's internals or the whole data source. A small focused server can be straightforward to build, although the implementation size depends on the operation.

This is useful for current framework APIs. When an agent uses an outdated .NET, Angular, Azure, or TypeScript example, it can spend many turns fixing compiler errors or inventing compatibility code. A targeted documentation call, such as `mcp__dotnet_docs__get_signature("DefaultAzureCredential")`, can return the relevant current signature and a short example. A tool that dumps the entire HTML page, including navigation and footer, loses that advantage.

Tool descriptions themselves consume context. If ten broad integrations expose 70 or more schemas, the agent may carry thousands of tokens of tool definitions through ordinary coding turns. Keep a few basic file and terminal tools available and load database, cloud, or browser tools when the task needs them.

### Consider adapters for stable company conventions

In a large, fairly uniform codebase, repeatedly describing internal naming, error handling, and library conventions can use substantial prompt space. A LoRA adapter trained on carefully selected pull requests and reference designs is one way to make those conventions part of the model's behavior, reducing the repeated style prompt.

That adapter captures established patterns, not the current state of the repository. Pair it with fresh code retrieval for dependencies and revise it when core frameworks change substantially.

### Make code and intent easier to read

A long condition combining bit masks, order totals, trial status, and tenant policy forces an agent to reconstruct the meaning before editing it:

```text
if (user.Flags & 0x08 != 0 && (order.Total > 500 || user.Tier == 3) && !order.IsTrial && (tenant.Policy == null || tenant.Policy.AllowBypass))
```

Names for the meaningful parts make the rule visible:

```text
bool isVipCustomer = (user.Flags & 0x08 != 0) && (order.Total > 500 || user.Tier == 3);
bool isEligibleForDiscount = isVipCustomer && !order.IsTrial;
bool policyAllowsBypass = tenant.Policy?.AllowBypass ?? true;

if (isEligibleForDiscount && policyAllowsBypass)
```

This reduces the need to rederive the entire Boolean expression and makes mistakes easier to spot. A concise `// INVARIANT: ...` comment can also explain a surprising business rule, vendor behavior, or hardware constraint next to the code. That gives the agent a reason to preserve a necessary edge case instead of “cleaning it up.” See [[Comments May Become More Valuable in AI-Generated Code]].

### Do not send screenshots when text will do

A full browser or desktop screenshot can cost far more context than a short text description. The original note estimates 1,500–4,000 visual tokens for a 1080p capture and over 6,000 for some 4K or multi-monitor captures, depending on the image processing mode. If each browser step keeps another 2,500-token screenshot in conversation history, five images account for about 12,500 tokens; repeated transmission over ten turns can add up to roughly 150,000 input tokens.

For web interaction, first use a concise accessibility tree or structured DOM when it contains the needed controls. Crop an image to the relevant component when appearance matters. After viewing it, carry forward a one-line finding rather than the image data where the workflow allows that. Compiler errors, terminal output, and source code should travel as text: screenshots use more context and can misread punctuation or casing.

---

## Put the approach into the daily workflow

| Task | Model or tool | Reasoning budget | Working approach |
| :--- | :--- | :--- | :--- |
| Architecture and core invariants | Strong cloud model | High, for example 8k–16k tokens | Evaluate the trade-offs; return a short plan. |
| Concurrency and complex refactoring | Strong cloud model | Medium, for example 2k–4k tokens | Check races and transaction boundaries. |
| Routine feature | Fast model | Low or none | Implement the agreed plan. |
| Local bug or syntax repair | Fast or local model | Little or none | Make a focused change and run the relevant test. |
| Formatting and AST linting | Script or linter | None | Run deterministic tooling. |

The budgets above are examples, not requirements for every model or task.

### Pause before broad execution

For a structural or multi-file change, inspect the relevant code, outline the implementation in roughly five bullets, and get agreement on the direction before a broad rewrite. The original protocol suggests limiting initial exploration to three tool calls and waiting for an explicit “OK” or “Proceed.” If the developer redirects the approach, revise the plan before changing the files. This avoids paying first to write an unwanted design and then to revert it.

### Stop a bad loop early

If an agent visibly starts importing the wrong library, rewriting unrelated structure, or misunderstanding the central requirement, stop that generation rather than allowing the whole change to land. If it fails to fix the same compiler or test error after two attempts, identify the missing constraint or make the correction directly. Do not keep feeding the same failure back into an unchanged approach.

A separate worktree gives an exploratory attempt a clean starting point:

```bash
git worktree add ../agent-task-sandbox main
cd ../agent-task-sandbox
```

It separates the experiment from uncommitted changes in the main working tree. Discard or reset an experiment only when its work is no longer needed.

### Keep test data compact

Reading a 1,500-line JSON fixture to understand one test case fills context with unrelated fields. When appropriate, build the needed object in the test:

```text
order = OrderBuilder.Create()
                    .WithStatus(OrderStatus.Pending)
                    .WithItem(price: 100, quantity: 1)
                    .Build();
```

The agent then sees the values that matter without loading a large mock file.

### Record approaches that already failed

Keep a short `ARCHITECTURAL_DISSENTS.md` with the rejected approach, why it failed, and the chosen replacement:

```markdown
# Architectural Dissents & Prohibited Paths
- Do not use distributed locks in the ingestion pipeline; they caused thread starvation in v2.4. Use local partition hashing.
- Do not wrap database queries in generic repository interfaces; use explicit SQL projections.
- Do not import library X for async queues; it blocks the native event loop. Use the internal bounded channel.
```

A compact record of these decisions can save a long investigation into paths the team has already tried.

---

## The operating principle

Spend context on the decision in front of the agent. Use scripts for predictable operations, code graphs for structural questions, current documentation for changing APIs, stable prefixes and exact matching for cache reuse, and deeper checks when a milestone is ready. Keep old experiments, raw subagent logs, huge fixtures, and repeated screenshots out of the active conversation when they no longer help. These choices reduce repeated inference work and make the relevant constraints easier to see.

### Related notes

- [[Agentic Coding Harness and Controlled Development Workflows]] — the agent's execution loop and controls.
- [[The Living Engineering Chronicle and Context Compaction]] — `DIARY.md` and milestone summaries outside the active context.
- [[Active Backlog Pruning and Context Hygiene in Agentic Roadmaps]] — removing completed work from active plans.
- [[Dynamic Model Routing and Inference Gateways]] — model routing, gateways, and caches.
- [[WebMCP - Turning Web Applications into Agent-Native Toolkits]] — semantic browser tools in place of repeated visual capture.
- [[Context Attractors and Recency Bias in Long-Horizon Agent Sessions]] — the effect of long conversations on the agent's current decisions.
- [[Local vs Cloud and Hybrid Model Execution]] — local and cloud model costs and hardware.
- [[Negative Knowledge and Explicit Architectural Dissents]] — recording failed approaches.
- [[Comments May Become More Valuable in AI-Generated Code]] — comments that preserve intent next to implementation.
- [[Token Optimization and Context Economics in Agentic Workflows v2]] — progressive disclosure, short plans, cohesive features, and subagent output boundaries.
