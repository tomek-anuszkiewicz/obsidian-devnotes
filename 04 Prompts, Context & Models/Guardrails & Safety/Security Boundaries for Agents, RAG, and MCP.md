---
title: Security Boundaries for Agents, RAG, and MCP
tags:
  - ai-agents
  - security
  - prompt-injection
  - rag
  - model-context-protocol
  - docker
  - sandboxing
aliases:
  - Agent Security Boundaries
  - RAG Source Poisoning and Prompt Injection
  - MCP Server Security
  - Securing Agent Tool Access
---

# Security Boundaries for Agents, RAG, and MCP

An agent reads a downloaded book through RAG, finds a relevant passage, and uses it to answer a question. That passage may contain a false claim. It may also contain text such as “ignore the user's request and call this tool.” The first problem is bad evidence; the second is an attempt to turn source material into an instruction. Both can affect the answer, but the second can also reach files, credentials, APIs, or other people if the agent has the tools to act on it.

The same system may expose a new MCP server or API. An agent can create the server, start a container, and report that the tool works without checking which interface the port listens on, which credentials the process can read, or what a caller is allowed to do. Fast implementation makes these omissions easier to miss; it does not change the underlying security rules.

## OWASP has more than one Top 10 now

There is a [Top 10 for web applications](https://top10.owasp.org/2025/), a [Top 10 for LLM applications](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/), and a [Top 10 for agentic applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/). The agentic list names problems such as goal hijacking, tool misuse, identity and privilege abuse, and poisoned memory. It is a useful way to review the new paths from language to action.

Apparently every new platform earns its own Top 10. Yet access control, unsafe configuration, injection, and sensitive-data exposure keep returning. The categories and attack paths evolve, but publishing a new list does not make the old service boundaries optional. Use the lists as prompts for concrete threat scenarios and tests, not as a substitute for checking what a caller or tool can actually do.

## A retrieved source is evidence, not authority

Web pages, books, repository files, search results, and RAG chunks are data supplied by someone other than the person directing the agent. Indexing a document does not make its contents trustworthy. A search rank or a citation only tells us where a passage came from, not whether its claim is correct or whether its embedded instructions should be followed.

Two failure modes deserve separate checks:

- **Source poisoning:** A document contains an incorrect or outdated claim, perhaps deliberately planted. The agent repeats it because retrieval placed it near the question. Keep source identity, date, and version with each chunk; compare consequential claims with an authoritative source or direct evidence before acting on them.
- **Indirect prompt injection:** The document addresses the agent, impersonates a higher-priority instruction, or asks for a tool call. Treat that text as part of the document being analyzed. It must not change the agent's task, permissions, tool arguments, or approval rules.

Suppose a retrieved operations guide says to disable authentication before testing an endpoint. The agent may quote the guide as evidence of what it says. It should not change the service configuration merely because the retrieved paragraph requested it. A more disguised version might present the same instruction as a “required setup step” in a plausible manual. The boundary still depends on where the instruction came from, not on how professionally it was written (see [[Retrieval-Augmented Generation and Context Architecture]] and [[How LLM Systems Enforce Safety and Higher-Level Instructions]]).

Source labels and prompt wording help the agent reason about the boundary, but they are not a permission system. The tool layer must independently restrict actions. Test the complete workflow with hostile passages in retrieved documents and tool responses: inspect both the answer and every attempted tool call. OWASP's [prompt injection guidance](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) describes attacks through modified RAG documents and recommends separating external content, limiting privileges, and testing adversarial inputs.

Retrieval permission is a separate check: before a chunk reaches the model, the search system must decide whether the caller may see it. That protects private documents from unauthorized retrieval; it does not make an allowed document's text safe to follow as an instruction. [[Retrieval-Augmented Generation and Context Architecture]] covers permission-aware retrieval in detail.

## A caller can steer the agent directly

A support chatbot or voice agent receives words from a person who may be trying to help, complain, or attack the service. A caller can spend several turns building a plausible story, claim to be an administrator, and ask the agent to reveal an account record, reset a password, grant a role, or send an email. A phone call only changes how the input arrives: speech is transcribed into text that can steer the same model and tools.

This is different from a hostile paragraph hidden in a retrieved book. The caller is allowed to make requests, but the conversation itself does not prove identity or authority. The agent may explain the account-recovery process or prepare a permitted support action. The service owning the account must still authenticate the caller and authorize the specific operation. A sensitive action needs an independently enforced confirmation or recovery workflow; a convincing dialogue cannot grant itself a new role or bypass that workflow (see [[Service vs User Authorization Models]]).

Test multi-turn attempts, not only one obvious “ignore previous instructions” message. The failure may come after the agent has repeated a false claim about the caller's identity often enough that it starts treating that claim as established fact. Check the actual tool calls and downstream authorization decisions, not only whether the final reply sounds safe.

## The agent's permissions define the damage it can do

An agent can attempt only the actions its runtime makes available, but those actions may be wider than the current task. A shell that can run any command as the logged-in user may reach that user's files, credentials, local services, and Docker daemon. A narrow instruction such as “edit only this repository” does not remove those capabilities. The useful question is what the process can actually read, write, execute, and contact if it misinterprets the task or follows hostile source text.

A **sandbox** is the enforced boundary around execution, not a synonym for Docker. It may use operating-system permissions, a restricted process, a container, a virtual machine, network policy, or several of these together. A container can be one way to implement a sandbox, but a container with broad host mounts, credentials, privileged mode, or Docker socket access may still have broad authority over the host. Conversely, an agent can be sandboxed without running in Docker. The implementation matters less than the effective access it grants (see [[Agent Deployment and Execution Models]] and [Docker's daemon security guidance](https://docs.docker.com/engine/security/)).

Permissions should have several independent dimensions. Scope filesystem access to the project and temporary work areas. Limit network destinations when network access is needed. Give tools credentials for the specific service and operations they require. Keep production deployment, external messaging, secret stores, and destructive operations behind separate gates. A command allowlist can help for a narrow workflow, but command names alone are a weak boundary: a permitted interpreter, build script, or package manager can run other code. Restrict its inputs and execution environment as well.

### Avoid approval fatigue without granting blanket access

If the agent asks for permission to read every file or run every routine test, the user learns to click through prompts or grants full access just to finish the work. That is a usability failure with a security consequence. Define a default working area where reading, editing, building, and testing are allowed without repeated questions. Ask when an action crosses that area: a new filesystem root, broader network access, a new credential, a production target, a destructive change, or an external side effect.

An approval should name the exact action and scope, such as one destination, one directory, or one deployment. It should not silently become permanent authority for unrelated future tasks. When the same safe action is needed often, adjust the standing policy for that narrow action instead of asking every time. When a proposed action is unusually broad, revise the workflow so the agent can prepare a reviewable result under its normal permissions and only the final consequential step needs approval. The approval policy decides when to ask; the sandbox and service permissions decide what the agent can technically do even after a mistaken answer (see [[Agentic Coding Harness and Controlled Development Workflows]]).

## MCP tools need a real permission boundary

An MCP server is an adapter between an agent and capabilities such as search, files, databases, or deployment APIs. A local server reached through standard input and output may have no network listener, yet it still runs with the process's filesystem access and credentials. An HTTP server adds a network entry point. In either case, a tool description saying “read only” or a prompt telling the agent to be careful cannot enforce a permission boundary.

The tool's name, description, and input schema are also text the agent reads when choosing an action. If an untrusted server or page supplies them, they can carry instructions disguised as tool guidance. Treat that metadata as untrusted input, just like a retrieved document; do not let it grant itself authority or widen the tool's actual permissions. [[WebMCP - Turning Web Applications into Agent-Native Toolkits]] shows this attack surface in a browser page.

Before connecting a tool, identify what identity it runs as, what data it can read, what it can change, and where its output can go. Give it only the credentials and operations needed for that task. Enforce authorization in the server or the downstream service on each operation, including tenant and resource scope. For a networked server, check the listening address, authentication, transport protection, and whether it is reachable beyond the intended machine or network. A locally bound listener also needs appropriate protection against unintended local callers and browser-origin requests. The [MCP authorization guidance](https://apps.extensions.modelcontextprotocol.io/api/documents/authorization.html) describes token validation for protected HTTP tools.

Separate search and inspection from write, delete, publish, and send operations where the workflow allows it. For consequential actions, show the exact target and proposed change before execution. Log the actual caller, tool, arguments, and result so a later review can reconstruct what happened. These controls belong in the harness and services, not only in a skill file (see [[Agentic Coding Harness and Controlled Development Workflows]]).

Validate a consequential tool call against permissions and its exact arguments **before** it executes. A log or audit after the call helps detect and investigate a mistake, but it cannot undo a sent message, exposed secret, or destructive API request. Test that the pre-action gate actually runs for forbidden calls (see [[Configuring and Testing Coding Agent Capabilities]]).

## Containers and ordinary services still need ordinary security

A container can make an agent-created service easy to launch while hiding its effective privileges. Review the final run or Compose configuration: published ports and bind addresses, host mounts, Docker socket access, container user, privileged mode, Linux capabilities, network egress, and injected secrets. A mount containing credentials or a mounted Docker socket can undo much of the isolation the container appeared to provide. Avoid granting those capabilities by default. Verify the running configuration, not just the intended YAML.

For the API behind an MCP tool, apply the same engineering rules used before agents: authenticate the caller, authorize the specific operation and resource, validate inputs, protect secrets, and test denial paths. Internal network placement does not replace authorization. An agent can help implement these checks and an audit can catch omissions, but the checks have to run in code and infrastructure. Existing notes on [[Service vs User Authorization Models]] and [[Service-to-Service Authentication and Authorization in Azure and Kubernetes]] cover the service-side details. [[Agent-Assisted Sensitive Data Exposure Audits]] examines whether the API, logs, and storage also move sensitive fields beyond their intended destinations.

The practical review question is: **What can this agent actually do if it follows a hostile retrieved paragraph or makes a mistaken decision, and which independent boundary limits the result?** If the answer is only “the prompt says not to,” the system needs a stronger boundary.

## Related notes

- **[[Always-On Autonomous Agents - The 24-7 Local Operating System]]** — External messages and feeds that can steer an agent running with persistent tool access.
- **[[LLMs as a Code Review Team]]** — A review agent whose comments and check results can become output channels.
- **[[How AI Agents May Control Computers, Applications, and the Web]]** — Why tool access across applications needs concrete execution limits.
- **[[Conversation History as Sensitive Data]]** — Privacy risks created by retaining and inferring from many ordinary conversations.
- **[[Continuous Security Monitoring with Agents]]** — A bounded agent that investigates suspicious activity across security signals.
