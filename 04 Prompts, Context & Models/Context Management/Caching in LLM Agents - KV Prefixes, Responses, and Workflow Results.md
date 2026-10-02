---
title: Caching in LLM Agents - KV Prefixes, Responses, and Workflow Results
tags:
  - llm
  - ai-agents
  - prompt-caching
  - context-engineering
  - inference-gateway
  - agentic-workflows
  - state-management
aliases:
  - KV Cache and Prefix Reuse
  - Prompt Caching in Coding Agents
  - Exact and Semantic Response Caching
  - Persistent Workflow Result Caching
  - Provider Context Caches
---

# Caching in LLM Agents - KV Prefixes, Responses, and Workflow Results

A coding agent can follow the same workflow many times while sending a different model request at every step. It reads another file, receives a compiler error, adds a tool result, or asks a new question. A cache of complete requests may find few duplicates. A provider's prompt cache can still help because much of the beginning of those requests may remain unchanged.

Another opportunity sits above the model call: save the result of an expensive workflow stage and reuse it when its dependencies still match. That can avoid repeated tool execution and model calls together.

These mechanisms preserve different things. Understanding what each one stores explains both its savings and the failures it can introduce. [[Token Optimization and Context Economics in Agentic Workflows]] discusses their place in the broader cost of completing and verifying a task.

## Different caches skip different work

| Mechanism | What is retained | What a hit skips |
| :--- | :--- | :--- |
| KV cache during generation | Per-layer attention keys and values for earlier tokens | Recomputing those representations for each new token |
| Prompt or prefix cache across requests | Reusable model state for an unchanged beginning of the input | Processing that part of a later request again |
| Exact response cache | A previous response under a precisely defined request key | A complete model call |
| Semantic response cache | Responses retrieved through similarity search and acceptance rules | A model call when an earlier answer is accepted as interchangeable |
| Workflow result cache | Outputs of a stage, together with its dependencies and validation records | Executing that stage again |

A checkpoint records progress so an interrupted run can continue. It can contain cached results, but recording progress and deciding whether an old result remains valid are separate responsibilities.

## What KV cache actually stores

In a conventional autoregressive transformer, a token can attend to earlier tokens but cannot use future tokens. Its attention layers produce numerical key and value vectors, abbreviated **K** and **V**. The model retains these vectors for the tokens it has already processed, separately for the relevant layers and attention heads.

When processing a new token, the model computes its query and its new K/V, then uses the retained K/V to attend to the preceding context. It still performs the new token's computations and reads the relevant earlier state. What it avoids is reconstructing the earlier key and value representations on every generation step. The [Hugging Face cache explanation](https://huggingface.co/docs/transformers/main/cache_explanation) describes this mechanism and the per-layer tensor layout.

There are two stages in a typical inference request:

1. **Prefill:** process the input sequence and construct the state needed to generate from it.
2. **Decode:** generate successive tokens, extending the KV cache as the sequence grows.

KV reuse inside one generation loop is distinct from retaining that state for later requests. A provider's prompt cache adds the second opportunity: a new request can start from compatible state that an earlier request already produced. The [OpenAI prompt-caching documentation](https://developers.openai.com/api/docs/guides/prompt-caching) explicitly describes caching KV tensors for a reusable input prefix.

This state belongs to inference. It does not update model weights or create a durable record that the agent completed a task. Earlier assistant messages or tool results can be part of a cached input prefix, but the model still generates the new response.

## A prefix is the unchanged beginning of the full model input

The visible user question is only part of the input. The host assembles instructions, tool definitions, history, selected documents, and other material before calling the model (see [[How LLM Systems Build Context]]). Prefix matching applies to that effective input and the settings that affect its rendering.

Consider two independent questions about the same source document. The brackets below represent logical blocks, not individual tokens:

```text
Request A: [instructions][tool definitions][document][question about latency]
Request B: [instructions][tool definitions][document][question about failures]
           <------------- shared prefix ------------->
```

The complete requests differ. Their shared beginning can still qualify for reuse. The provider processes the changing suffix and generates a new answer. Eligibility also depends on the model, minimum cacheable length, available saved boundaries, retention, and compatible request settings.

Order matters because the retained state depends on what came before each token and where it occurred. Putting the same document after different instructions does not necessarily produce interchangeable KV state. In [vLLM's documented implementation](https://docs.vllm.ai/en/latest/design/prefix_caching/), a cached block is identified using both its tokens and the preceding prefix. Finding the same words later in a different context is insufficient for ordinary prefix reuse.

If a document changes, the earlier instructions and tools may still match. If the first instruction changes, the reusable beginning may become much shorter. The older entry need not be deleted; the new request simply no longer matches it beyond the relevant change and eligible boundary.

This is exact contextual reuse. Embedding similarity does not establish that two token sequences have the same attention state.

## Why changing agent requests can still reuse a prefix

An agent often appends messages rather than rebuilding every earlier part:

```text
Call 1: [instructions][tools][task]
Call 2: [instructions][tools][task][assistant tool call][tool result]
Call 3: [instructions][tools][task][assistant tool call][tool result][next turn]
```

A saved prefix can remain useful as this history grows. This does not guarantee that every previously generated token is already in a reusable entry: providers save and search particular boundaries, and retained state can expire. It does explain why "every request is different" is a stronger objection to whole-response caching than to prefix caching.

Several ordinary harness behaviors reduce reuse:

- changing a timestamp or environment description near the beginning;
- adding, removing, or reordering tool definitions;
- rebuilding a file bundle in a different order;
- rewriting earlier messages or replacing history with a summary;
- changing a model or setting that alters the rendered input.

Keep reusable instructions and reference material stable when practical, and append changing task data later. Preserve message roles and tool-result relationships. Moving untrusted retrieved content into a privileged instruction merely to obtain a cache hit changes its authority as well as its position.

Compaction illustrates the trade-off. Replacing a long history with a shorter summary can lose part of the previous prefix cache while improving the next task's context. Retaining obsolete history for cache hits can waste memory and impair the agent's decisions (see [[The Living Engineering Chronicle and Context Compaction]]).

## What the inference server has to retain

KV state can occupy substantial memory. For a conventional decoder with a full KV cache at each layer, an approximate payload size is:

```text
2 × layers × retained tokens × KV heads × head dimension × bytes per value
```

The factor of two accounts for K and V. As an illustrative configuration, 32 layers, 8 KV heads, a head dimension of 128, FP16 values, and 32,768 retained tokens produce about **4 GiB** of KV payload for one sequence, before allocation overhead. This is a worked configuration, not a memory estimate for Claude, Gemini, or an OpenAI model. Different attention architectures, shared prefixes, quantization, and sliding windows change the calculation.

Servers must allocate, share, and eventually reclaim this state while serving concurrent requests. The [PagedAttention paper](https://arxiv.org/abs/2309.06180) explains how growing KV allocations, fragmentation, and duplication limit serving capacity. vLLM demonstrates block sharing and eviction; [LMCache](https://docs.lmcache.ai/) is an example of infrastructure for retaining and transferring KV state. These public implementations explain possible mechanisms without establishing which implementation a closed provider deploys.

OpenAI documents that reusable state resides on individual machines and that routing and expiry affect whether a request finds it. Providers do not expose every allocation, transfer, or eviction decision. A matching input therefore establishes an opportunity for reuse, not an unconditional hit.

Cached tokens still belong to the logical context. Reusing their processing does not give the model a larger context window or eliminate the attention work of new tokens. Savings primarily affect repeated input processing and time to first token; output generation remains work the server must perform.

## Hosted provider caches and what the client can observe

The API behavior below was checked on **2026-10-03**. Model thresholds, retention options, and prices should be read from the linked provider documentation rather than treated as universal constants.

| Provider | Documented reuse and controls |
| :--- | :--- |
| OpenAI | [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) reuses compatible exact prefixes on supported models. Retention and controls vary by model. Requests must reach an available matching entry; cache accounting and routing keys do not substitute for prefix agreement. |
| Claude | [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) uses `cache_control` for automatic or explicit boundaries. The prefix hierarchy is `tools`, then `system`, then `messages`. Documented TTL options are five minutes and one hour. |
| Gemini | [Context caching](https://ai.google.dev/gemini-api/docs/caching) includes automatic prefix reuse. The Interactions API currently supports implicit caching only. [The generateContent API](https://ai.google.dev/gemini-api/docs/generate-content/caching) also supports explicit cache objects referenced by subsequent requests, with a configurable TTL. |

Codex is an agent client. The provider serving its selected model owns the inference cache; changing the location of the agent's tools does not move the provider's KV tensors to the developer's machine. Provider API documentation establishes the documented API behavior, not every hidden choice in a subscription-backed application.

Use exposed usage records to check actual reuse. OpenAI Responses reports cached input tokens in `usage.input_tokens_details.cached_tokens`. Claude separates `cache_read_input_tokens`, `cache_creation_input_tokens`, and uncached `input_tokens`. Gemini reports cached-token usage through `usage_metadata` for generateContent and `usage.total_cached_tokens` for Interactions. A continued conversation alone does not prove a cache hit.

Cached-input prices also do not establish the same conversion for a product's subscription allowance. Input reads, cache writes or storage, fresh input, and output can have different billing rules.

## Response caching needs the dependencies of the answer

An application library or gateway can store a complete model response and return it without invoking the provider. An exact cache requires a key that identifies the work precisely enough for the application.

That normally includes the relevant conversation, instructions, tool schemas, model and generation settings, output format, source-data versions, and caller scope. Use unambiguous structured serialization when constructing the key. Preserve the order and exact content whose meaning matters; sorting conversation messages or stripping whitespace from source code can change the task.

An identical question can require a different answer after a source file, dependency, database record, or authorization scope changes. A gateway only knows about external changes that the application represents in its request or cache metadata. Hashing one target file cannot validate a review that depends on surrounding code.

Even for a valid hit, response caching preserves a previous sampled result. A retry intended to obtain a different candidate must bypass that entry or use a separate attempt identity. A cached response containing a tool call also does not prove the action already succeeded: execution and side effects need their own state and idempotency rules.

There are several places to implement this:

| Solution | Cache placement and role |
| :--- | :--- |
| [LiteLLM](https://docs.litellm.ai/docs/proxy/caching) | Gateway or SDK response caching, with exact and semantic backends including local memory, disk, Redis/Valkey, and Qdrant. |
| [Bifrost](https://docs.getbifrost.ai/features/semantic-caching) | Gateway caching with direct request hashing and optional embedding-based lookup after a direct miss. |
| [GPTCache](https://github.com/zilliztech/GPTCache) | Application library for semantic response reuse, with configurable storage and similarity evaluation. |
| [RedisVL](https://redis.io/docs/latest/develop/ai/redisvl/api/cache/) | Semantic cache library with TTL, distance thresholds, and metadata filters. |
| [Cloudflare AI Gateway](https://developers.cloudflare.com/ai-gateway/features/caching/) | Hosted gateway response caching for identical requests. |
| [Portkey](https://portkey.ai/docs/product/ai-gateway/cache-simple-and-semantic) | Gateway response caching with simple and semantic modes. |

These are different integration points, not interchangeable installations. Check that the actual route passes through the cache: a provider passthrough endpoint can bypass gateway caching even when the gateway's normalized endpoint supports it.

## Semantic similarity is only a candidate for answer reuse

"Delete files older than 30 days" and "delete files newer than 30 days" describe the same subject but require opposite behavior. Likewise, `if (ptr != null)` and `if (ptr == null)` differ at exactly the point that controls execution. A vector score measures proximity under an embedding model and distance metric; a score of 0.95 is not a 95% probability that the old answer remains correct.

Agent histories create another failure. A new request may contain the entire previous history plus one short tool result. The two inputs can be extremely close in embedding space even though the agent must now take a different action. [LiteLLM documents](https://docs.litellm.ai/docs/proxy/caching_semantic) that semantic caching on such traffic can replay stale responses and repeat tool calls, and that increasing the similarity threshold does not reliably solve this.

Semantic response reuse fits bounded questions with stable answer dependencies better than an unrestricted tool-calling loop. Filter by relevant user scope, data version, task category, and other exact constraints before accepting a similarity match. Reuse should depend on whether the answer is interchangeable for the task, not just whether two prompts discuss the same topic. Search can also retrieve an earlier result as context for fresh reasoning instead of returning it as the final answer.

## A custom endpoint is different from an HTTPS tunnel

An agent can use a local response cache while calling a remote model. A library can intercept calls inside the application; a gateway can expose an endpoint the client deliberately selects (see [[Dynamic Model Routing and Inference Gateways]]).

HTTPS encrypts a connection to its selected endpoint. With an application gateway, the client connects to the gateway, which can read the request and establish a separate connection to the provider. An ordinary forwarding proxy can instead tunnel HTTPS without seeing model content. [Claude Code's network documentation](https://code.claude.com/docs/en/network-config) distinguishes proxy configuration and trusted certificate configuration for TLS inspection. Encrypted transport by itself does not rule out an explicitly configured gateway.

| Client | Documented endpoint configuration |
| :--- | :--- |
| Codex CLI and desktop | A provider `base_url` in user configuration. The gateway must preserve [Responses API behavior](https://learn.chatgpt.com/docs/enterprise/gateway-compatibility), streaming, continuation, and tool calls. See [client setup](https://learn.chatgpt.com/docs/enterprise/connect-to-a-gateway). |
| Claude Code CLI | `ANTHROPIC_BASE_URL` and the appropriate credentials; see [gateway setup](https://code.claude.com/docs/en/llm-gateway-connect). |
| Claude Desktop | The app's [third-party inference configuration](https://claude.com/docs/third-party/claude-desktop/gateway), rather than assuming it reads the CLI environment variable. |
| Gemini CLI | `GOOGLE_GEMINI_BASE_URL` for Gemini API-key authentication and `GOOGLE_VERTEX_BASE_URL` for Vertex AI; see [configuration](https://geminicli.com/docs/reference/configuration/). |

Endpoint compatibility and authentication are separate. In [Claude Code](https://code.claude.com/docs/en/llm-gateway#subscriptions-and-gateways), setting only the base URL can preserve subscription login, while supplying gateway credentials changes the active credential and billing path. Gemini CLI documents its [token-caching feature](https://geminicli.com/docs/cli/token-caching/) for API-key and Vertex AI access, distinguishing it from Google OAuth through Code Assist. These differences prevent a general claim that selecting any gateway preserves an existing subscription.

A gateway must also preserve provider cache controls and the full agent protocol. A successful text response does not verify a streamed tool call, its matching result, and the next turn. If the agent runs on a remote server, its `localhost` endpoint is on that server, not automatically on the developer's computer.

## Persist stage results when the workflow is the repeated unit

For a repeated repository analysis, save the file inventory, extracted structures, dependency analysis, generated changes, and verification reports as distinct stage outputs. Each result needs input and dependency identities, the stage's code or prompt version, relevant model settings, completion status, and the validation appropriate to that stage.

A file existing on disk does not establish successful completion or current validity. A crash can leave a partial output, and an unchanged prompt can read changed external data. Record completed output consistently with its metadata, and compare dependency versions before reuse. If one source changes, recompute the affected stage and its dependants; retain unrelated valid results.

There are concrete implementations of this pattern. [LangGraph node caching](https://docs.langchain.com/oss/python/langgraph/graph-api#node-caching) supports a cache key function and TTL. [Prefect task caching](https://docs.prefect.io/v3/concepts/caching) relies on persisted results and configurable key policies. [Nextflow resume](https://docs.seqera.io/nextflow/cache-and-resume) checks a matching task identity together with the presence of its outputs.

[Claude Code dynamic workflows](https://code.claude.com/docs/en/workflows#resume-after-a-pause) provide a narrower agent-native example: a resumed run can return saved results from completed agents in the same session. A changed prompt or failed earlier agent can force later work to run again, and a fresh session starts a new run. This is saved execution progress, not a universal cache of equivalent tasks across sessions.

Long-running agents require more than warm model state. After an interruption, they must reconstruct control flow, pending work, external state, and the outcome of side effects. A write can succeed before its completion is recorded, so recovery also needs idempotent operations or reconciliation. [[Workflow Orchestration in Agentic Systems]] develops these durable-execution concerns. KV state can expire while an agent is stopped; a durable checkpoint can still allow the agent to resume with a freshly processed context.

## Measure savings at the layer that actually skips work

Track cached input tokens separately from avoided model calls and reused workflow stages. Measure time to first token, complete task duration, output generation, embedding calls, cache storage, retries, and the checks that decide whether a reused result is valid. A high hit rate can conceal stale answers or an agent repeatedly taking the same action.

For changing agent loops, stable prefixes offer input reuse without requiring identical complete requests. For genuinely repeated calls, exact response caching can avoid inference. For repeated workflows, persisted stage outputs can avoid larger units of work. Compare these choices by the cost of a verified result, including failures and invalidation, rather than selecting the cache with the highest reported hit rate.

## Related notes

- **[[Token Optimization and Context Economics in Agentic Workflows]]** — Context budgets, usage accounting, and the cost of completing a task.
- **[[Local vs Cloud and Hybrid Model Execution]]** — Memory capacity and hardware trade-offs when inference runs locally.
- **[[Dynamic Model Routing and Inference Gateways]]** — Where a gateway runs and which task information it can observe.
- **[[Workflow Orchestration in Agentic Systems]]** — Persistent execution state, retries, and recovery around external side effects.
