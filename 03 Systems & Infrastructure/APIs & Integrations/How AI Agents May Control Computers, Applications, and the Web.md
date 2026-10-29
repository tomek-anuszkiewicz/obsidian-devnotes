---
title: How AI Agents May Control Computers, Applications, and the Web
tags:
  - ai-agents
  - computer-use
  - gui-automation
  - browser-agents
  - api-design
  - operating-systems
aliases:
  - Computer Use by AI Agents
  - "Semantic Application Interfaces for Agents"
  - "Agent-Operable Software Capabilities"
---

An agent can understand a user's request while lacking a reliable way to perform it. Applications and operating environments expose capabilities at several levels, from explicit business operations to command-line interfaces and browser structure.

This article follows the design of those operable interfaces and the separation of capability from presentation. [[Executing Cross-Application Tasks with Computer-Use Agents]] develops execution across applications, choosing a fallback interface, verifying effects, and controlling permissions and untrusted content. A voice command is one way to request the work; the application contracts determine how the work can be done.

For decades, interacting with a computer has largely meant interacting with graphical user interfaces.

Humans learned where to click:

```text
open application
→ find menu
→ select option
→ fill form
→ click Save
```

AI agents may gradually introduce another layer:

```text
user intent
→ agent
→ available capabilities
→ execution
```

The important change is not voice recognition.

Speech recognition has already been good enough for many years.

The missing piece has been the ability to translate:

> "Do this for me."

into:

```text
understand the goal
→ discover available capabilities
→ create a plan
→ execute actions
→ observe the result
→ recover from problems
```

Modern LLMs provide much of the reasoning layer.

The remaining transformation is about giving them reliable **hands**.

---

## Agents Already Have Several Ways to Control Software

There is unlikely to be one universal mechanism.

Instead, agents will probably use a hierarchy of techniques.

### Semantic Tools and APIs

This is the most reliable approach.

An application explicitly exposes operations such as:

```text
searchMovies(query)

playMovie(id)

createInvoice(customer, items)

sendMessage(contact, message)

loadLatestSave()

createCalendarEvent(...)
```

The agent does not need to know where a button is located.

It understands the capability directly.

This idea appears today in several forms:

- normal application APIs,

- tool calling,

- MCP servers,

- OS-level application actions,

- application intents,

- skills and connectors.

The exact protocol is less important than the architectural idea:

> Applications describe what they can do in machine-readable form.

---

## MCP Is Part of a Larger Pattern

MCP is interesting because it provides a common way for agents to discover and invoke tools.

Instead of hard-coding every integration:

```text
agent
├── custom Spotify integration
├── custom filesystem integration
├── custom Git integration
├── custom database integration
└── custom Home Assistant integration
```

the model becomes closer to:

```text
agent
      ↓
tool discovery layer
      ↓
┌─────────────┬─────────────┬─────────────┐
filesystem    Spotify       database
MCP           MCP           MCP
```

The agent can inspect:

- available tools,

- descriptions,

- parameters,

- schemas,

- resources,

- permissions.

MCP therefore fits naturally into computer control, but it is not limited to interactive computer control.

The same mechanism can be used by:

- coding agents,

- workflow orchestrators,

- scheduled agents,

- enterprise automation,

- research systems,

- voice assistants.

Voice is simply one possible entry point.

Under the hood, MCP standardizes this discovery and invocation over JSON-RPC transports (typically stdio for local processes or SSE/HTTP for remote services). By publishing typed schemas, argument constraints, and tool descriptions upfront, the protocol lets an agent inspect capabilities on the fly rather than requiring hardcoded API adapters or burning prompt tokens on brittle tool glue code.

---

## CLI May Become More Important, Not Less

Linux already has much of the infrastructure an agent needs.

For decades it has exposed functionality through:

```text
shell
CLI tools
stdin/stdout
exit codes
pipes
systemd
D-Bus
filesystem
Unix sockets
SSH
REST APIs
```

Humans sometimes find these interfaces difficult.

LLMs are unusually well suited to them.

An agent can:

```text
run command
→ read stdout
→ inspect error
→ run --help
→ change parameters
→ combine another command
→ verify result
```

This means CLI may experience a strange renaissance.

Not because humans suddenly prefer terminals, but because **agents are excellent terminal users**.

An application with a good CLI may already be significantly more agent-friendly than an application exposing only a GUI.

Terminal I/O is dense, structured text, which makes it remarkably cheap on token consumption compared to parsing massive DOM snapshots or decoding high-resolution screen frames. Applications that expose structured output flags like `--json` provide deterministic exit codes, explicit error streams, and parseable output that make automated recovery and command piping trivial for an agent.

---

## Operating Systems Are Starting to Expose Capabilities to Agents

Operating systems can provide another control layer.

Instead of an agent knowing application-specific implementation details, applications can register semantic actions such as:

```text
SendMessage
OpenDocument
CreateReminder
PlayMedia
SearchContent
```

Apple's App Intents and Microsoft's emerging App Actions are examples of this direction.

The OS can become a capability registry:

```text
                    agent
                      ↓
              capability registry
                      ↓
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
    system         application     service
    actions          actions         tools
```

This is much more powerful than traditional voice assistants based on a fixed list of predefined commands.

Instead of forcing the model to guess regex patterns against voice phrases, the operating system functions as a typed local broker. Applications register parameter schemas and execution handlers directly with the OS daemon, allowing the model to discover, inspect, and invoke actions within structured OS-level permission and isolation boundaries.

---

## The Web May Be Even More Agent-Friendly

Web applications already share a common execution environment:

```text
browser
HTML
DOM
JavaScript
HTTP
URLs
forms
accessibility tree
```

Even without explicit cooperation from a website, an agent can often interact with it through the DOM or accessibility layer.

For example:

```text
find button with role="button" and name="Buy"
→ click
```

This is considerably better than looking at pixels.

Browser automation tools such as Playwright already demonstrate how powerful this model is.

Targeting the accessibility (ARIA) tree rather than the raw DOM or visual viewport filters out rendering noise, CSS styling hacks, and responsive layout shifts. Automation engines like Playwright can latch onto deterministic semantic roles and names, giving the agent a stable interaction handle without bloating the context window with megabytes of styling tags and script noise.

---

## Web Applications Can Also Expose Semantic Agent Tools

An emerging direction is for websites to explicitly expose operations to agents.

Instead of forcing the agent to reproduce human interaction:

```text
click Search
→ type destination
→ click dates
→ select passengers
→ click Search
```

the application could expose:

```text
searchFlights(
    origin,
    destination,
    dates,
    passengers
)
```

Technologies such as WebMCP explore exactly this idea.

This gives the web the same capability model being developed for desktop applications:

```text
GUI        → human

semantic tools
           → agent
```

A website does not have to abandon its interface.

It simply gains another interface.

---

## Applications May Need an Agent Interface

Software has traditionally been designed primarily around its GUI.

A developer asks:

> How should the user create an invoice?

and designs:

```text
Invoices
→ New
→ Customer
→ Add items
→ Save
```

In an agent-oriented world, another question becomes equally important:

> What capability does the application provide?

The answer could be:

```text
CreateInvoice(customer, items)
```

That capability may then be exposed through several interfaces:

```text
                     CreateInvoice
                           │
           ┌───────────────┼───────────────┐
           ↓               ↓               ↓
          GUI             REST            CLI
                                           
           ↓               ↓               ↓
         human           system           scripts

                           +
                           
                     MCP / App Action
                           ↓
                         agent
```

The GUI becomes one client of the underlying application capabilities rather than the only way to operate the system.

---

## This May Change Software Architecture

Agent-friendly applications may increasingly separate:

```text
business capability
```

from:

```text
human interaction
```

Instead of embedding important behavior directly inside UI workflows:

```text
button click
→ validation
→ business logic
→ database
```

applications may increasingly look like:

```text
business capability
        ↑
   ┌────┼─────┐
   │    │     │
  GUI  API   agent
```

This is good architecture even without AI.

Agents may simply provide a much stronger economic reason to adopt it.

---

## Related Notes

- [[WebMCP - Turning Web Applications into Agent-Native Toolkits]] — Exposing semantic web application capabilities directly to browser agents.
- [[New Developer Technologies May Need to Be Agent-Ready from Day One]] — Designing interfaces that agents can operate programmatically.
- [[Proactive Software — From Reactive Systems to Autonomous Agents]] — Evolution from reactive button-clicking to autonomous software systems.
- [[Workflow Orchestration in Agentic Systems]] — Orchestrating multi-step computer automation tasks safely.
