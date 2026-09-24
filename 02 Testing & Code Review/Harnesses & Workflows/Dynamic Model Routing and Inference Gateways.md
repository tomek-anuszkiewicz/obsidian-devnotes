---
title: Dynamic Model Routing and Inference Gateways
tags:
  - ai-agents
  - agent-harness
  - inference-gateway
  - model-routing
  - architecture
  - software-economics
  - system-design
aliases:
  - Model Routing Architecture
  - Inference Gateways
  - Dynamic Model Dispatching
  - The 5 Levels of Model Routing
  - Optimistic Local Execution Pattern
---

# Dynamic Model Routing and Inference Gateways

If an agent workflow contains model names such as `gpt-4o` or `claude-3-7-sonnet` throughout its code, changing providers becomes a code change. Routine work may consume expensive API tokens, and an outage or rate limit at one provider can stop the workflow altogether.

An inference gateway puts model selection between the agent and the provider APIs. The agent asks for a capability through a stable endpoint; the router decides whether the request should go to a local model or a cloud model.

For coding agents, a useful approach is to try routine work locally, run the compiler, type checker, linter, and tests, then send failures to a stronger cloud model (see [[Local vs Cloud and Hybrid Model Execution]] and [[Testing in the Model, Agent, LLM Era]]). The note's proposed saving is **60% to 80% of cloud token spending**, provided that the verification step catches the problems that matter and the fallback works reliably.

```text
Agent clients: OpenClaw/daemons, IDE extensions, CI/CD PR reviewers
       │  POST /v1/chat/completions (model: "auto")
       ▼
Inference gateway or in-process router
       ├─ Inspect context length, secrets, and JSON schema needs
       ├─ Optionally compare prompt embeddings (<5 ms)
       └─ Handle retries, fallbacks, and circuit breakers
              ├─ Local: DGX Spark / Mac Studio / vLLM
              │  $0.00 marginal token cost; local socket
              │  Formatting, tests, RAG triage
              └─ Cloud: Anthropic / OpenAI / Google
                 $3–$15 per million tokens; 200–500 ms network latency
                 Complex architecture and planning
```

## 1. Where the routing code runs

First decide whether each agent owns its routing logic or all clients call a shared gateway. Both arrangements can send requests to the same local and cloud models. They differ in which information the router can see and how many places the routing code must be maintained.

### Inside the agent process

The agent harness contains a routing interface or strategy class (see [[Agent Deployment and Execution Models]] and [[Agentic Coding Harness and Controlled Development Workflows]]). It inspects the current task and calls either a local `vLLM` endpoint through an OpenAI-compatible client or a provider SDK such as `anthropic-sdk-python`.

This works when the decision depends on state already inside the agent: the size of a git diff, AST complexity, compiler output held in memory, or the number of retries so far. Passing all of that through an HTTP request just to make a routing decision can be awkward.

The cost is duplication. If agents are written in Python, Go, and TypeScript, each implementation needs its own routing rules, fallbacks, and circuit breakers. Each copy must be tested and maintained.

### In a separate gateway

OpenClaw daemons, IDE integrations such as Cursor, CI runners, and local scripts can instead call one base URL, such as `http://localhost:4000` or an internal cluster address. A proxy such as LiteLLM Proxy, Portkey, or an Envoy-based AI gateway exposes an OpenAI-compatible `/v1/chat/completions` endpoint. Clients request aliases such as `smart-code-router`, `smart-route`, `cheap`, `heavy`, or `deep-reasoning`; the gateway maps those aliases to providers.

This gives the team one place for token accounting, provider credentials, connection pooling, rate limits, latency tracking, and failover. It adds a network hop, typically under a millisecond on loopback or a local subnet. It also means the router can act only on information included in the HTTP payload and headers.

```text
In-process:  agent → routing strategy → local vLLM client / cloud SDK
Gateway:     daemon, IDE, CI → shared HTTP proxy → local / cloud model
```

## 2. Five ways to route a request

These options range from assigning a model to each agent role to scoring every incoming prompt. A system can start with a simple rule and add other checks where the workload needs them.

### Level 1: Assign models by agent role

Use a lookup table: a `CommitMessageGenerator` or `DocstringFormatter` calls a local 7B model; a `TestScaffolder` calls a local 14B or 32B model; a `SystemArchitect` calls a stronger cloud model. Local inference can run on a developer workstation or an on-premises machine.

The same mapping covers commit messages, docstrings parsed from ASTs, and basic mock fixtures. Architecture work, complex refactoring plans, and changes spanning dependent files go straight to the cloud. The router does not need to inspect the prompt, so the selection is deterministic and adds effectively no decision latency. Mechanical tasks do not accidentally consume cloud tokens.

### Level 2: Inspect the request before dispatch

The gateway can make several decisions from measurable properties of the request:

1. **Context size.** A prompt below **16k tokens** with small attachments is a candidate for local inference. A **64k to 128k+ token** prompt, such as a repository indexing pass or analysis of megabytes of logs, may go directly to the cloud. The KV cache for a large prompt can exhaust local GPU memory; a larger provider cluster can handle that memory demand across its infrastructure (see [[Token Optimization and Context Economics in Agentic Workflows]]).
2. **Sensitive data.** A regex and AST scan looks for private keys, database connection strings, JWTs, and identifiable customer data. If it finds them, the gateway blocks cloud egress and restricts the request to a local, isolated endpoint. [[Agent-Assisted Sensitive Data Exposure Audits]] covers the wider data-flow review when sensitive fields move through APIs, logs, and stores.
3. **Required output format.** When a request must satisfy a complex JSON schema, it can go to a local engine with constrained decoding, such as `vLLM` with Outlines or `llama.cpp` with GBNF grammars. The grammar restricts token generation to valid syntax and can avoid repeated cloud calls to repair malformed JSON.

### Level 3: Compare the prompt with known task types

Role and token count do not always indicate what the user is asking. A small local embedding model, such as `bge-small-en-v1.5` or `all-MiniLM-L6-v2`, can encode the prompt and compare it by cosine similarity with stored reference vectors for task categories. The proposed CPU time is **2–4 ms** on one core; tools such as `semantic-router` are presented as a way to keep this check below **5 ms**.

For example, “How do I invert a binary tree in memory?” could score **0.89** against a syntax and standard algorithms cluster and **0.32** against a distributed concurrency cluster. The router sends that request locally. Standard algorithms, syntax questions, and basic unit tests follow the same path. Concurrency bugs, race conditions, and architectural trade-offs go to a stronger model.

The reference vectors are prepared ahead of time. The gateway embeds only the incoming prompt and compares it with those stored categories when the request arrives.

### Level 4: Try locally, then check the result

Coding tasks have a useful feedback loop: the agent can run a compiler, linter, static analyzer, type checker, or test suite against its change. Let a local open-weights model try the task, verify the result, and escalate when the local attempt fails. This avoids having to predict from the prompt alone whether the local model is capable of doing the work.

```text
Task: refactor a database query to avoid N+1 queries
  → Local model attempts change ($0.00 marginal token cost; example: 2.5 s)
  → Run unit tests, linter, and type checker
      ├─ Pass: accept the change; no cloud inference charge
      └─ Fail after up to two local repairs:
           send original request, failed git diff, and exact error output
           to a stronger cloud model
```

A capable local model may resolve some routine engineering tickets, such as off-by-one fixes, straightforward interfaces, boilerplate updates, and mock tests. The useful share has to be measured on the team's own workload. Keep repair attempts bounded so that repeated local failures do not consume more time than an escalation would.

When escalation is needed, send the cloud model the **original task, the failed local diff, and the precise compiler or test trace**. It sees what was attempted and why that attempt failed, which can help it fix the problem on the first try and reduce expensive calls.

### Level 5: Use a trained routing classifier

RouteLLM-style routing uses a small preference model trained on many comparisons between model answers. The proposed implementations include a fine-tuned BERT classifier or a lightweight matrix-factorization scoring layer. Instead of a fixed rule, the router assigns a score from `0.0` for a simple prompt to `1.0` for one needing stronger reasoning.

## 3. What the gateway does when a model is unavailable

Routing must also handle failures. A local model can run out of GPU memory; a cloud provider can return `429 Too Many Requests`; the internet connection can drop. The agent should receive a usable response from another permitted endpoint when one is available.

| Failure | Gateway action |
| :--- | :--- |
| Local CUDA out-of-memory error | Retry the request against a cloud model. |
| Cloud HTTP 429 | Back off and try another cloud provider or a local model; temporarily stop using the rate-limited endpoint. |
| Internet outage | Use local models only, with reduced reasoning capability if necessary. |

Here is the original configuration example for a centralized LiteLLM-style proxy. It illustrates a local coding endpoint with Claude and Gemini fallbacks, bounded retries, timeouts, and a 60-second cooldown:

```yaml
model_list:
  # The primary coding engine running on an on-premise local appliance
  - model_name: agent-coding-stack
    litellm_params:
      model: openai/qwen2.5-coder:32b
      api_base: http://dgx-spark.local:8000/v1
      api_key: "none"
    model_info:
      fallbacks: ["anthropic/claude-3-7-sonnet", "google/gemini-2.5-pro"]
      max_retries: 2
      timeout: 30

  # High-reasoning cloud fallback endpoints
  - model_name: anthropic/claude-3-7-sonnet
    litellm_params:
      model: anthropic/claude-3-7-sonnet-20250219
      api_key: "os.environ/ANTHROPIC_API_KEY"
    model_info:
      fallbacks: ["google/gemini-2.5-pro"]
      max_retries: 3
      timeout: 60

  - model_name: google/gemini-2.5-pro
    litellm_params:
      model: gemini/gemini-2.5-pro
      api_key: "os.environ/GEMINI_API_KEY"

router_settings:
  routing_strategy: "cost-based"
  fallbacks:
    - "agent-coding-stack": ["anthropic/claude-3-7-sonnet", "google/gemini-2.5-pro"]
  allowed_fails: 3
  cooldown_time: 60
```

In the first case, the proxy catches a local CUDA allocation failure caused by an oversized context and retries through Claude 3.7 Sonnet without ending the agent's run. In the second, it backs off after a cloud `429`, tries another provider such as Gemini 2.5 Pro, and leaves the primary provider alone for **60 seconds** while its rate limit recovers. If the WAN connection fails, it sends work to local endpoints so the agent's loop can continue, although a local model may be less capable.

## 4. Three ways this setup can go wrong

### Asking another LLM to route every call

An 8B model can read each prompt and choose a destination, but doing that at every agent step adds **400–800 ms** of generation time and another round of tokens before the real work begins. The note's target is a routing decision below **5 ms**. Role assignments, regex checks, and small CPU embedding comparisons fit that target better than a generation call.

### Saving tokens while wasting engineering time

A 3B or 7B model may be adequate for mechanical tasks but a poor choice for system design, changes across modules, or sensitive database migrations. It can invent APIs, miss edge cases, and leave a senior engineer with two hours of repair work. At an engineering cost above **$100 per hour**, saving a few cents on the API call is a bad trade.

### Accepting local code without verification

The local-first loop depends on an automated check. Without a substantial test suite, strict type checking, or a deterministic compiler pass, broken local output can slip into the repository (see [[Testing in the Model, Agent, LLM Era]] and [[Building Determinism from Unpredictable Models]]). When the change cannot be checked automatically, the note recommends sending that task directly to a stronger cloud model. Passing a check supports the decision to accept a change only to the extent that the checks cover the relevant behavior.

## Related notes

- **[[Local vs Cloud and Hybrid Model Execution]]** — Hardware limits, unified memory, and the economics of local versus cloud inference.
- **[[Token Optimization and Context Economics in Agentic Workflows]]** — Token use, model tiers, and exact-hash proxy caching.
- **[[Always-On Autonomous Agents - The 24-7 Local Operating System]]** — Background agents that use local gateways for routine work.
- **[[Agent Deployment and Execution Models]]** — Boundaries between the agent runtime, inference gateway, and execution sandbox.
- **[[Agentic Coding Harness and Controlled Development Workflows]]** — Agent harnesses, sandboxes, and boundaries on the changes agents can make.
- **[[Testing in the Model, Agent, LLM Era]]** — Tests and harness fixtures for checking local attempts.
- **[[Competitive Advantage in the Age of Commodity AI]]** — Orchestration, routing, and continuous domain evaluation beyond access to a model.
