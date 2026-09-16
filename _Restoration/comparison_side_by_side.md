# Side-by-Side Restoration Comparison: Original vs. Restored Notes

> [!NOTE]

> This document provides a direct, row-by-row comparative evaluation of the reference notes.

> Left column: Original reference note (pre-deconstruction).

> Right column: Restored note synthesized by **Gemini 3.8 Flash (High Thinking)**.



---

## Note: Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize

**Metrics**: Original: **2174 words** | Restored: **528 words** | Compression: **-75.7%**


<table style='width: 100%; table-layout: fixed; border-collapse: collapse; margin-bottom: 24px;'>

  <tr style='background-color: var(--background-secondary-alt); border-bottom: 2px solid var(--background-modifier-border);'>

    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Original Input Note (2174 words)</th>

    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Restored Note - Gemini Flash High-Thinking (528 words)</th>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<strong style='color: var(--text-accent);'>Overview / Introduction</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>﻿--- title: Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize tags:   - ai-agents   - code-review   - software-engineering   - quality-assurance   - static-analysis   - compliance   - review aliases:   - Natural-Language Rules as Executable Policies   - Agentic Review Rules   - Semantic Code Review ---  Traditional software quality automation works best when a rule can be expressed precisely.  For example:  ```text Domain must not reference Infrastructure. Every public endpoint must require authorization. Result must never be negative. All handlers must implement a particular interface. ```  Such rules can be encoded as:  - unit tests;      - architecture tests;      - static analyzers;      - compiler rules;      - type-system constraints;      - linters;      - CI checks.       This remains extremely valuable.  However, a large part of software engineering has never fit comfortably into this model.  Many important rules are not difficult because developers do not understand them.  They are difficult because they are expensive or nearly impossible to formalize.  LLM-based review agents may automate part of this previously human-only layer.  ---  ## Many Real Engineering Rules Are Semantic  #coding_standard  Consider rules such as:  &gt; Do not introduce an abstraction unless it represents a meaningful boundary.  Or:  &gt; Controllers should remain thin, but trivial request mapping does not need another service layer.  Or:  &gt; Modules should communicate through their public contracts rather than reaching into each other&#x27;s internals.  Or:  &gt; Do not introduce a generic framework for a problem that exists only once.  Or:  &gt; Business rules should remain visible in the domain code rather than being hidden inside infrastructure helpers.  These are meaningful architectural principles.  An experienced engineer can often recognize their violation immediately.  But encoding them as a deterministic test may require an enormous amount of machinery.  The problem is not lack of rules.  The problem is that the rules depend on:  - intent;      - context;      - naming;      - surrounding architecture;      - business meaning;      - exceptions;      - trade-offs;      - degree rather than binary classification.       Historically, this meant that enforcement depended on human attention.  ---  ## Human Attention Was the Missing Runtime  #review   Architecture documents frequently contain sentences like:  ```text Prefer explicit dependencies.  Avoid leaking persistence concerns into the domain.  Do not create abstractions prematurely.  Cross-module access should happen through defined boundaries. ```  These rules may be well understood by the team.  But nothing actually executes them.  Their enforcement mechanism is approximately:  ```text developer remembers the rule         + reviewer remembers the rule         + reviewer notices the violation ```  This is fragile.  Even excellent reviewers:  - get tired;      - skim large changes;      - forget some guidelines;      - focus on the most obvious problem;      - have limited time;      - do not inspect every pull request with identical depth.       A review agent changes this because it can repeatedly interpret the same rule against every relevant change.  The document can become part of an active quality system rather than passive documentation.  ---  # Natural-Language Rules Can Become Executable Policies  #coding_standard  Suppose a repository contains:  ```text docs/architecture/principles.md docs/domain/invariants.md docs/security/guidelines.md docs/performance/guidelines.md ADRs/ ```  An architecture reviewer can receive these documents as part of its instructions.  For every pull request it can ask:  ```text Does this change violate any architectural principle?  If so:  - identify the concrete code; - identify the relevant principle; - explain why the rule applies; - consider documented exceptions; - estimate confidence; - avoid commenting if evidence is weak. ```  This is not executable specification in the traditional deterministic sense.  It is closer to:  &gt; natural-language executable policy.  The important change is that a rule no longer needs to be translated completely into code before it can be checked automatically.  ---  ## This Expands the Automatable Region of Engineering  Previously there were roughly two categories:  ```text Formalizable rule     -&gt; automation  Non-formalizable rule     -&gt; human review ```  Agents introduce a third layer:  ```text Formalizable rule     -&gt; deterministic automation  Semantically interpretable rule     -&gt; agentic verification  Ambiguous strategic decision     -&gt; human judgment ```  This potentially moves a large amount of work out of the purely human-review category.  Examples include checking whether:  - a new abstraction is justified;      - responsibilities remain in the correct module;      - domain logic is becoming infrastructure-dependent;      - error handling matches surrounding conventions;      - a change duplicates an existing capability;      - a public API behaves consistently with related APIs;      - a workaround violates an architectural direction;      - a class has accumulated too many unrelated responsibilities;      - a supposedly generic component is actually coupled to one use case.       These are exactly the kinds of things senior engineers traditionally catch during review.  ---  # Agents Are Particularly Useful Because They Are Relentless  The advantage is not only that an LLM can understand such rules.  It can apply them every time.  A human may know twenty architectural principles perfectly but consciously evaluate only a subset during a particular review.  An agent can inspect every relevant PR against all twenty.  It does not care that:  - the change is repetitive;      - the pull request contains 100 files;      - this is the fiftieth review this week;      - the rule rarely catches anything;      - the same check has failed to find a problem for six months.       This makes agents particularly suitable for rules that are individually important but rarely violated.  Humans are bad at maintaining attention for checks that almost always produce:  ```text nothing wrong ```  Machines are excellent at it.  ---  # But Agents Must Also Handle Formalizable Rules Well  There is an important danger in dividing the world too aggressively into:  ```text tests handle simple rules  LLMs handle difficult rules ```  An effective reviewer must still understand the rules that could have been expressed as deterministic tests.  For example:  ```text A price must never be negative. ```  Even if there is already a unit test for this invariant, an agent reviewing related code should understand that violating it is wrong.  Otherwise the agent has an incomplete model of the system.  The distinction should therefore not be:  &gt; deterministic rules belong to tests and should be invisible to the agent.  Instead:  &gt; deterministic tools are the authoritative verification mechanism, while the agent should also understand their meaning.  The agent should be capable of reasoning:  ```text This change appears capable of creating a negative price.  There is an invariant that prices cannot be negative.  I should inspect or run the relevant tests. ```  Then the deterministic test provides the strongest evidence.  ---  ## Formal Rules Should Usually Remain Deterministic  If something can be verified cheaply and precisely:  ```text Assert.True(result &gt;= 0); ```  there is little benefit in replacing it with:  ```text Ask an LLM whether result &gt;= 0 appears to hold. ```  The deterministic version is:  - cheaper;      - faster;      - reproducible;      - precise;      - easy to debug;      - independent of model behavior.       Agents should therefore usually sit above these mechanisms rather than replacing them.  A useful principle is:  &gt; Formalize what is cheap to formalize. Use agents where formalization becomes disproportionately expensive.  ---  # The Agent Can Connect Formal and Informal Rules  The interesting capability appears when an agent understands both.  Suppose an architecture document says:  &gt; Module A must not depend on Module B&#x27;s persistence model.  There may also be a deterministic architecture test forbidding direct references between certain namespaces.  The agent can detect a subtler case:  ```text There is no forbidden assembly reference.  However, Module A now copies the exact internal database representation of Module B and depends on its persistence semantics. ```  The formal test passes.  The architectural intent may still be violated.  The agent operates one level above syntax.  Likewise:  ```text Unit test: Price cannot be negative. ```  may pass.  But the reviewer may notice:  ```text The implementation clamps negative prices to zero, which preserves the technical invariant but silently hides an invalid business state. ```  A deterministic test sees compliance.  A semantic reviewer can question whether the implementation satisfies the underlying intent.  This interaction is potentially much more powerful than either approach alone.  ---  # Agents Can Escalate Rules Into Deterministic Tests  Agentic review can also help discover which informal rules should eventually become formal.  Imagine an agent repeatedly finds the same problem:  ```text Five pull requests introduced direct dependencies from Domain to Infrastructure. ```  At that point the correct response may be:  &gt; Stop asking the LLM to rediscover this every time.  Turn the rule into an architecture test.  The process becomes:  ```text informal principle         | agent repeatedly checks it         | pattern becomes stable         | rule can be formalized         | architecture test / analyzer added ```  This gives a useful migration path.  Agents can act as the exploratory layer from which deterministic rules emerge.  ---  # The Reverse Is Also Useful  A deterministic check may reveal a violation without explaining its architectural significance very well.  For example:  ```text Architecture test failed: Namespace X references namespace Y. ```  The agent can add context:  ```text This is prohibited because Y contains persistence-specific models.  The new reference causes the pricing module to depend on the current database representation of customer data.  The intended integration point is CustomerContract. ```  The machine-verifiable test gives certainty.  The agent gives interpretation.  That combination can make automated checks much easier for developers to understand and fix.  ---  # Some Tests May Become Ephemeral  Agents also make it possible to distinguish between permanent tests and tests created only for investigation.  Today a test usually means:  ```text write test commit test maintain test forever ```  An agent can instead generate a test to investigate a particular hypothesis.  For example:  ```text I suspect this cache fails when two requests initialize it concurrently. ```  The agent creates a temporary concurrency test, runs it repeatedly, and discovers the race.  The experiment itself does not necessarily need to remain in the repository.  If the discovered behavior represents an important regression risk, the test can then be promoted:  ```text agent-generated experiment         | bug reproduced         | important invariant discovered         | promote test         | permanent regression test ```  This separates:  ```text tests as permanent specification ```  from:  ```text tests as investigative instruments ```  Agents can make heavy use of the second category.  ---  # Architecture Review May Become Continuous  The same idea applies especially well to architecture.  Today architecture is often enforced through a mixture of:  ```text architecture documents ADRs review culture senior engineers occasional architecture tests ```  With agents, every pull request can undergo an architecture review.  The reviewer can ask:  ```text Did this change create a new dependency direction?  Did an internal concept leak through a module boundary?  Was an abstraction introduced?  If so, does it have a meaningful reason to exist?  Does this change contradict an ADR?  Does it make a future migration significantly harder?  Is business logic moving into infrastructure code?  Does the new code follow the architecture or merely satisfy its syntax? ```  Most of these questions would be extraordinarily difficult to encode in conventional analyzers.  They are much closer to questions asked by an experienced architect.  ---  # The Ideal System Uses Both Forms of Verification  The future quality stack may therefore look something like:  ```text               Human judgment                     Ôû▓                     |           Semantic agent review                     |        architecture / intent /        context / trade-offs                     Ôû▓                     |         Deterministic verification                     |       tests / types / analyzers /        linters / security tools ```  The layers complement each other.  Deterministic verification provides certainty where precise formalization is practical.  Agents extend automation into areas where semantic judgment is required.  Humans remain responsible for decisions where even the correct rule depends on business priorities, risk tolerance, or competing architectural goals.  ---  # The Goal Is Not to Replace Rules With Prompts  A tempting mistake would be to conclude:  &gt; If an LLM can inspect the code, we no longer need architecture tests, analyzers, or unit tests.  That would discard one of software engineering&#x27;s strongest properties: deterministic verification.  A better model is:  ```text If a rule can cheaply become code:     encode it.  If a rule is difficult to encode but understandable:     let an agent enforce it.  If an agent repeatedly finds the same formalizable violation:     consider turning it into code.  If the correct answer depends on strategic judgment:     escalate it to a human. ```  This creates a continuum rather than a replacement.  ---  # Review Agents Turn Human Attention Into a Scalable Resource  Historically, many engineering standards were enforced simply because experienced developers watched for them.  That created an unavoidable constraint:  ```text quality of enforcement Ôëê available senior engineering attention ```  Agents weaken this dependency.  A senior engineer may define a principle once:  &gt; Do not hide business decisions behind generic infrastructure abstractions.  Instead of expecting every reviewer to remember and enforce it forever, the principle can become part of an agent&#x27;s permanent review instructions.  The human provides the judgment once.  The agent applies it thousands of times.  That may be one of the most important consequences of agentic code review:  &gt; knowledge that previously existed only as human review intuition can become continuously executable organizational policy.  The strongest future systems will probably combine two capabilities:  &gt; machines must be extremely reliable at rules that can be formalized, while also extending verification into rules that previously required human interpretation.  The first preserves the precision of traditional software engineering.  The second expands its reach.</p>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Overview / Introduction</strong><hr style='margin: 4px 0 8px 0;'><h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Executable Architecture Policies</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Traditional static analysis handles deterministic invariants:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Domain must not reference Infrastructure.
Every public endpoint must require authorization.
Result must never be negative.
All handlers must implement a particular interface.</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Deterministic checkers enforce syntax, AST patterns, and types well.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>However, critical architectural rules rely on context and semantic intent:</p>
<li style='margin-left: 18px;'>Avoid premature abstractions.</li>
<li style='margin-left: 18px;'>Keep controllers thin without redundant mapping layers.</li>
<li style='margin-left: 18px;'>Prevent domain logic leaks into infrastructure helpers.</li>
<li style='margin-left: 18px;'>Restrict cross-module communication to public contracts.</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>Encoding these semantic rules into linters costs too much time.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Reviewers traditionally enforced these standards from memory.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Agent Runtime for Natural-Language Rules</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Feed architecture documentation directly into the review agent context:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>docs/architecture/principles.md
docs/domain/invariants.md
docs/security/guidelines.md
ADRs/</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Prompt the agent to inspect incoming pull requests:</p>
<li style='margin-left: 18px;'>Pinpoint the violating lines.</li>
<li style='margin-left: 18px;'>Cite the breached policy or ADR.</li>
<li style='margin-left: 18px;'>Explain the architectural conflict.</li>
<li style='margin-left: 18px;'>Suppress output when confidence falls below threshold.</li>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Three-Tier Quality Stack</h4>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Human Review       -&gt; Strategic architectural trade-offs
Agentic Review     -&gt; Semantic policy and intent checks
Deterministic CI   -&gt; Types, linters, unit tests, analyzers</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Review agents eliminate manual auditing fatigue.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>They audit 100-file pull requests without skimming.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>They evaluate rarely violated rules on every commit.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Deterministic Tests vs. Semantic Inspection</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Never replace fast deterministic checks with LLM prompts.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Deterministic checks remain authoritative, cheap, and reproducible:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Assert.True(result &gt;= 0);</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Reserve agents for rules where formalization costs too much.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Use agents to catch semantic bypasses of formal rules.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>#### Case 1: Invariant Circumvention</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>A price invariant states that values cannot fall below zero.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>A developer clamps negative inputs to zero.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>The deterministic unit test passes:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>// Unit test passes
Assert.True(price &gt;= 0);</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>The agent flags the bug: Clamping silently masks invalid domain state.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>#### Case 2: Structural Decoupling Evasion</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>An architecture test forbids importing Module B from Module A.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>The test passes because Module A copies Module B internal schemas directly.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>The agent flags semantic coupling despite zero direct project references.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Bidirectional Feedback Loop</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>#### 1. Promote Agent Findings to Deterministic Analyzers</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Track repeated agent detections.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>If an agent repeatedly catches infrastructure imports in domain code, write an AST analyzer.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Automate the check permanently.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Free the agent context for novel patterns:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Informal Principle -&gt; Agent Audits PRs -&gt; Pattern Stabilizes -&gt; Static Analyzer Rule Added</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>#### 2. Explain Deterministic Failures</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Use agents to explain static analysis failures.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>A linter flags: `Namespace X references Namespace Y`.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>The agent provides context:</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>`Namespace Y contains raw database entities. Use CustomerContract instead.`</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Ephemeral Investigative Tests</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Agents can generate throwaway tests to validate hypotheses during review.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>An agent suspects a race condition in a cache implementation.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>It writes a temporary test and executes it:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Agent Generates Test -&gt; Reproduces Concurrency Bug -&gt; Promotes to Regression Suite</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>If the race reproduces, promote the test to the regression suite.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Otherwise, discard the scratchpad test.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Continuous Architecture Checklist</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Run these semantic checks on every pull request:</p>
<li style='margin-left: 18px;'>Does this diff introduce a one-off generic framework?</li>
<li style='margin-left: 18px;'>Does domain logic leak into infrastructure adapters?</li>
<li style='margin-left: 18px;'>Does this change contradict recorded ADR decisions?</li>
<li style='margin-left: 18px;'>Does the new abstraction justify its operational cost?</li>
    </td>

  </tr>

</table>



---

## Note: Comments May Become More Valuable in AI-Generated Code

**Metrics**: Original: **1249 words** | Restored: **419 words** | Compression: **-66.5%**


<table style='width: 100%; table-layout: fixed; border-collapse: collapse; margin-bottom: 24px;'>

  <tr style='background-color: var(--background-secondary-alt); border-bottom: 2px solid var(--background-modifier-border);'>

    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Original Input Note (1249 words)</th>

    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Restored Note - Gemini Flash High-Thinking (419 words)</th>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<strong style='color: var(--text-accent);'>Overview / Introduction</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>﻿--- title: Comments May Become More Valuable in AI-Generated Code tags:   - ai-agents   - software-engineering   - documentation   - code-review   - maintainability   - intent-specification aliases:   - Code Comments in AI Era   - Semantic Value of Comments in AI Code ---  The traditional rule for comments is often expressed as:  &gt; Good code should explain what it does. Comments should explain why.  This distinction may become even more important in software increasingly written and modified by AI agents.  An agent can usually reconstruct the mechanics of code very well. It does not need comments that merely repeat the implementation.  For example:  ```csharp // Charge 50% if booking starts in less than 3 days. if (booking.StartDate &lt; DateTime.UtcNow.AddDays(3)) {     cancellationFee = booking.TotalPrice * 0.5m; } ```  The comment adds almost no information.  A much more valuable comment would be:  ```csharp // Cancellations within 72 hours are charged 50% because the supplier // no longer refunds us after this point. // Do not replace this with the standard hotel cancellation policy. ```  The code explains the mechanism.  The comment preserves information that cannot easily be reconstructed from the implementation:  - why the rule exists;      - where it comes from;      - whether it is intentional;      - which business constraint it represents;      - what apparently reasonable changes would be incorrect.       ## Code Is Self-Documenting Syntactically, Not Semantically  Well-written code can communicate structure and behavior.  For example:  ```csharp ApplyNonRefundableSupplierCancellationFee(); ```  This is much better than an obscure method name, but it still does not explain:  - why this supplier is treated differently;      - whether the behavior comes from a contract;      - whether it is temporary;      - which products it applies to;      - whether another similar rule should be reused;      - what assumptions the implementation depends on.       Historically, much of this knowledge lived outside the code:  - in developers&#x27; heads;      - Jira tickets;      - Slack conversations;      - meetings;      - old specifications;      - architecture documents.       Future agents modifying the code may never see any of those sources.  A comment located next to the implementation has a major advantage:  &gt; It is very likely to enter the agent&#x27;s context whenever the relevant code enters the context.  ## Comments Can Act as Local Context Retrieval  Suppose an agent receives a task:  &gt; Add partial cancellation support.  It retrieves the classes responsible for cancellations.  Any comments located inside those classes are naturally retrieved together with the implementation.  This makes comments a kind of very small, highly localized knowledge base.  They do not require the agent to know:  - that an ADR exists;      - which specification describes the rule;      - which ticket introduced it;      - what search query to use;      - which meeting contained the relevant discussion.       The knowledge is physically attached to the place where it matters.  This may make carefully written comments one of the most reliable forms of context delivery for future coding agents.  ## Documentation Layers Still Have Different Roles  Comments should not replace specifications or architectural documentation.  Instead, the different layers can complement each other:  ```text Specification     Ôåô describes desired behavior and requirements  Architecture docs / ADRs     Ôåô describe system-wide decisions and trade-offs  Business comments     Ôåô preserve local intent, constraints and exceptions  Code     Ôåô contains the executable implementation ```  During the initial implementation, an agent may have access to the complete specification.  Several years later, another agent may receive only a small portion of the repository while working on an unrelated change.  The original specification may not enter its context at all.  A nearby comment probably will.  ## Negative Knowledge May Be Especially Valuable  Some of the most useful comments may describe what must **not** be done.  For example:  ```csharp // Do not calculate this from Payment.Amount. // Legacy bookings may already contain the agency margin there. ```  Or:  ```csharp // This check looks redundant, but some suppliers occasionally send // the same reservation with different external IDs. ```  Or:  ```csharp // Intentionally executed before availability validation. // Sales requires the original quoted price to remain available // even when availability subsequently fails. ```  This is negative knowledge:  &gt; A seemingly obvious implementation or refactoring is incorrect.  Such knowledge may be particularly important for agents.  An agent performing a local refactoring may see:  ```text strange condition ÔåÆ appears redundant ÔåÆ simplify it ```  A good comment changes the reasoning to:  ```text strange condition ÔåÆ explicitly intentional ÔåÆ represents a business constraint ÔåÆ preserve unless the requirement itself changes ```  ## Clean Code Does Not Eliminate Business Context  The argument that &quot;good code should not require comments&quot; is reasonable when applied to comments describing mechanics.  Comments such as:  ```csharp // Iterate through users. ```  are usually unnecessary.  But business rationale cannot always be encoded through better naming or cleaner abstractions.  A method called:  ```csharp IsEligibleForLegacyCancellationCompensation() ```  still does not explain why legacy cancellation compensation exists.  The useful distinction may therefore become:  &gt; Minimize comments explaining implementation.  &gt; Maximize comments preserving intent, business meaning, invariants, constraints, exceptions and non-obvious decisions.  ## Agents Can Produce Their Own Future Context  There is another important consequence.  When an agent implements a feature, it already has the specification in its context.  Instead of converting that specification only into executable code, it can also preserve the parts of the specification that future developers or agents will need.  A useful instruction could be:  &gt; Whenever the implementation encodes a non-obvious business rule, invariant, exception or constraint that cannot be reconstructed from the code itself, preserve that information as a concise comment near the relevant code.  The process then becomes:  ```text task specification        Ôöé        Ôû╝      agent     /     \    Ôû╝       Ôû╝ code     durable intent          comments ```  The code is the executable result of the specification.  The comments preserve selected parts of its semantics.  ## Comments May Become Part of Designing Code for Agents  Traditionally, comments were primarily written for human maintainers.  In agent-heavy development, another audience appears:  &gt; the future model receiving a limited slice of the repository as context.  This changes how comments can be evaluated.  The question is no longer only:  &gt; Will another developer understand this?  It also becomes:  &gt; If an agent sees only this file two years from now, what important information could it incorrectly infer?  Comments can protect against those incorrect inferences.  This suggests that codebases optimized for agentic development may intentionally preserve more business context next to the implementation.  Not more comments in general.  Better comments.  Especially comments explaining:  - why a rule exists;      - which business concept it represents;      - which invariant must remain true;      - why an unusual implementation is intentional;      - which tempting simplification would be wrong;      - which external constraint shaped the implementation;      - which assumptions future changes must preserve.       In this sense, comments may become part of **context engineering for future coding agents** rather than merely an aid to human readability.  ## Redefining Low-Level and Architectural Documentation  The ability of LLMs to analyze code and explain its mechanics on demand accelerates two major shifts:  1. **Obsolescence of Low-Level Comments and Descriptive Docs:**    - Comments explaining *how* a function works or what steps it takes are now pure noise.    - Broad architectural documentation that merely describes component relationships or data flows is easily reconstructed on the fly by an agent analyzing the codebase.  2. **From Structural Documentation to Decision Records:**    - Documentation shifts almost entirely from *descriptive* (what exists) to *decisional* (why it was built this way).    - High-level architecture docs remain valuable only as **guardrails and trade-offs** (e.g., ADRs, system constraints, performance budgets) that prevent agents from making architectural refactorings that break unstated non-functional requirements.</p>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Semantic Comments vs. Syntax Echoes</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>LLMs parse syntax without help.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>They fail when inferring unstated business rules.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Do not explain code mechanics in comments.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Record intent, external constraints, and invariants directly in source files.</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>// BAD: Repeats the code.
// Charge 50% if booking starts in less than 3 days.
if (booking.StartDate &lt; DateTime.UtcNow.AddDays(3)) {
    cancellationFee = booking.TotalPrice * 0.5m;
}

// GOOD: Preserves business constraints.
// Suppliers stop refunds 72 hours before booking starts.
// Do not replace this with the standard hotel cancellation policy.
if (booking.StartDate &lt; DateTime.UtcNow.AddDays(3)) {
    cancellationFee = booking.TotalPrice * 0.5m;
}</code></pre>
    </td>

  </tr>

  <tr style='background-color: var(--background-secondary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Anchor Context Next to Code</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Agents fetch files locally during edits.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>They miss external tickets, chat threads, and design docs.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Comments placed next to code enter the context window automatically.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Clean method names show what runs, not why contracts exist:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>ApplyNonRefundableSupplierCancellationFee();</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Method names omit contract sources, date rules, and vendor quirks.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Use comments to supply these hidden constraints.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Separate system knowledge across distinct tiers:</p>
<li style='margin-left: 18px;'>Specs: Define product goals.</li>
<li style='margin-left: 18px;'>ADRs: Track global trade-offs.</li>
<li style='margin-left: 18px;'>Source comments: Anchor local invariants and exceptions.</li>
<li style='margin-left: 18px;'>Code: Runs the logic.</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>Coding models refactor single files without reading parent specs.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Source comments preserve business rules when specs drop out of context.</p>
    </td>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Negative Knowledge and Guard Comments</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Models often refactor defensive code into generic patterns.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Negative knowledge records forbidden changes and deliberate anomalies.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Use guard comments to stop broken edits:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>// Do not calculate this from Payment.Amount.
// Legacy bookings store agency margins there.</code></pre>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>// Keep this check.
// Suppliers occasionally send duplicate records with distinct external IDs.</code></pre>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>// Run this before checking availability.
// Sales insists that quoted prices persist when inventory calls fail.</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Without comments, models apply naive logic:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>strange code -&gt; looks redundant -&gt; delete</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Negative knowledge updates the prompt context:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>strange code -&gt; deliberate rule -&gt; keep</code></pre>
    </td>

  </tr>

  <tr style='background-color: var(--background-secondary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Instruct Agents to Preserve Constraints</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Direct coding agents to store downstream context when building features.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Use this prompt rule in agent pipelines:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Preserve non-obvious business rules as concise comments next to the code.</code></pre>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Spec -&gt; Agent -&gt; Executable Code + Invariant Comments</code></pre>
    </td>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Invariant Checklist</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Write comments to prompt future models.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Audit comments with one test:</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>What will an agent break if it reads only this file?</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Always record:</p>
<li style='margin-left: 18px;'>Upstream business logic driving the rule.</li>
<li style='margin-left: 18px;'>Non-obvious domain invariants.</li>
<li style='margin-left: 18px;'>Deliberate workarounds for external vendor bugs.</li>
<li style='margin-left: 18px;'>Tempting cleanups that break system guarantees.</li>
    </td>

  </tr>

</table>



---

## Note: Designing APIs for LLM-Generated Integration Code

**Metrics**: Original: **1447 words** | Restored: **541 words** | Compression: **-62.6%**


<table style='width: 100%; table-layout: fixed; border-collapse: collapse; margin-bottom: 24px;'>

  <tr style='background-color: var(--background-secondary-alt); border-bottom: 2px solid var(--background-modifier-border);'>

    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Original Input Note (1447 words)</th>

    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Restored Note - Gemini Flash High-Thinking (541 words)</th>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<strong style='color: var(--text-accent);'>Overview / Introduction</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>﻿--- title: Designing APIs for LLM-Generated Integration Code tags:   - api-design   - ai-agents   - software-architecture   - integration   - developer-experience   - documentation aliases:   - Agent-Friendly API Design   - APIs for LLM Integrations ---  ## Goal  When using an LLM coding agent, the goal is not necessarily for the agent to call an API directly.  Instead, the agent should be able to:  1. understand the requested business operation,      2. discover which external API capability provides it,      3. find the correct generated client,      4. choose the correct client method,      5. generate application code that uses that method correctly.       A useful mental model is:  ```text Business requirement         Ôåô Discover business capability         Ôåô Find appropriate client         Ôåô Find appropriate operation         Ôåô Generate application code         Ôåô Generated client         Ôåô REST API ```  ## Internal vs External APIs  It is useful to distinguish between internal and external APIs.  ### Internal APIs  Internal APIs may:  - reflect internal service architecture,      - expose implementation-specific concepts,      - use internal data representations,      - change relatively freely,      - depend on concepts already understood inside the system.       ### External APIs  External APIs should:  - provide stable contracts,      - avoid leaking internal implementation details,      - expose business concepts rather than internal mechanics,      - remain compatible over time,      - use terminology meaningful to consumers.       This distinction becomes even more important for LLM-generated code.  The easier it is to understand the business meaning of an operation, the easier it is for an agent to select it correctly.  ---  ## OpenAPI as the Source of Truth  For REST APIs, OpenAPI should describe not only the HTTP contract, but also the semantics of the operation.  A weak specification:  ```yaml /users/{id}/sessions:   delete:     operationId: deleteSessions ```  A better specification:  ```yaml /users/{userId}/sessions:   delete:     operationId: revokeUserSessions     summary: Revoke all active sessions for a user     description: |       Revokes all active authentication sessions belonging       to the specified user.        Use this operation when access for the user must be       immediately invalidated.        This operation does not delete the user account. ```  The description should answer questions such as:  - What does this operation do?      - When should it be used?      - When should it not be used?      - What are the preconditions?      - What side effects does it have?      - What are the important failure modes?       Negative guidance can be especially useful.  For example:  ```yaml description: |   Permanently deletes a draft invoice.    Only draft invoices can be deleted.    Do not use this operation for issued invoices.   Issued invoices must be cancelled using cancelInvoice. ```  This helps the agent choose the correct business operation rather than matching only on words such as &quot;delete&quot;.  ---  ## Prefer Business-Oriented Operations  Operations should clearly express intent.  Prefer:  ```text cancelInvoice revokeUserSessions reserveInventory approveOrder ```  over vague operations such as:  ```text updateEntity executeAction changeStatus processRequest ```  CRUD operations are perfectly fine when the business operation really is CRUD.  For example:  ```http DELETE /drafts/{id} ```  is appropriate if the object is actually deleted.  But a business operation such as cancelling an issued invoice should probably be represented explicitly:  ```http POST /invoices/{id}/cancel ```  rather than pretending that cancellation is equivalent to deletion.  The important principle is:  &gt; The API should expose business capabilities, not merely database mutations.  ---  ## Generate Strongly Typed Clients  The coding agent should normally not construct HTTP requests manually.  Instead of generating:  ```csharp await httpClient.DeleteAsync(     $&quot;/users/{userId}/sessions&quot;); ```  prefer a generated typed client:  ```csharp await identityClient.RevokeUserSessionsAsync(     userId,     cancellationToken); ```  The client can be generated from OpenAPI using tools such as:  - Kiota,      - NSwag,      - OpenAPI Generator.       The flow becomes:  ```text OpenAPI    Ôåô Client generator    Ôåô Strongly typed client    Ôåô LLM-generated application code ```  This significantly reduces the space in which the agent can make mistakes.  It no longer needs to reconstruct:  - the URL,      - HTTP method,      - serialization format,      - request schema,      - response schema,      - query parameter names.       Instead, it chooses a typed method.  ---  ## Preserve Documentation in Generated Clients  Ideally, descriptions from OpenAPI should become XML documentation or equivalent comments in the generated client.  For example:  ```csharp public interface IInvoicesClient {     /// &lt;summary&gt;     /// Cancels an issued invoice while preserving it for audit.     /// Do not use for draft invoices.     /// &lt;/summary&gt;     Task CancelInvoiceAsync(         Guid id,         CancellationToken cancellationToken);      /// &lt;summary&gt;     /// Permanently deletes a draft invoice.     /// Issued invoices cannot be deleted.     /// &lt;/summary&gt;     Task DeleteDraftInvoiceAsync(         Guid id,         CancellationToken cancellationToken); } ```  This is particularly useful for coding agents because the most relevant semantic information is available directly next to the methods they are expected to use.  If the generated client loses all API descriptions, much of the semantic value of OpenAPI is lost.  ---  ## Client Discoverability  Having good generated clients is not enough.  The agent must also be able to discover which client provides a given capability.  Prefer domain-oriented names:  ```text IIdentityClient IOrdersClient IBillingClient IInvoicesClient ```  instead of implementation-oriented names:  ```text IServiceAClient IBackendClient IApiV2Client ```  Likewise, operation names should expose intent clearly:  ```text RevokeUserSessionsAsync CancelInvoiceAsync ReserveInventoryAsync ```  This allows a coding agent to search the repository by business concepts.  Example reasoning:  ```text Requirement: &quot;When an employee is disabled, invalidate all login sessions.&quot;  Ôåô search for: session revoke session identity  Ôåô find: IIdentityClient  Ôåô inspect methods: RevokeUserSessionsAsync  Ôåô generate: await identityClient.RevokeUserSessionsAsync(...) ```  The repository itself becomes a semantic index of available capabilities.  ---  ## Repository Guidance for Agents  The agent should be explicitly told how external integrations are organized.  For example, an `AGENTS.md`, repository instruction, or coding skill may contain:  ```text When integrating with another service:  1. Search existing generated clients by business concept. 2. Inspect method names and documentation. 3. Prefer generated clients over direct HTTP calls. 4. If the correct operation is unclear, inspect the source OpenAPI specification. 5. Do not invent endpoint URLs or construct REST requests manually when a generated client exists. ```  The instruction tells the agent **how to discover and use capabilities**.  The OpenAPI specification tells it **which capabilities exist and what they mean**.  These are different responsibilities.  ---  ## OpenAPI Does Not Always Need to Be Read Directly  If the generated client is well named and well documented, the coding agent may not need to inspect `swagger.json` for every task.  In the common case:  ```text Business requirement         Ôåô Search generated clients         Ôåô Inspect documented methods         Ôåô Generate code ```  OpenAPI remains the authoritative contract and can be consulted when additional details are needed.  For example:  - detailed error responses,      - optional parameters,      - lifecycle constraints,      - response schemas,      - operation semantics not fully exposed by the generated client.       Therefore, a useful hierarchy is:  ```text OpenAPI    Ôåô Generated typed client    Ôåô Generated documentation/comments    Ôåô Coding agent ```  ---  ## Error Responses Should Also Be Semantic  Avoid responses such as:  ```json {   &quot;errorCode&quot;: 3817 } ```  Prefer errors that expose the state and possible resolution:  ```json {   &quot;code&quot;: &quot;invoice_already_issued&quot;,   &quot;message&quot;: &quot;Issued invoices cannot be deleted.&quot;,   &quot;suggestedOperation&quot;: &quot;cancelInvoice&quot; } ```  This is useful both for generated application code and for an LLM trying to understand the intended workflow.  ---  ## The Same Principle Applies Beyond REST  The same architecture can be applied to other integration styles.  ### GraphQL  Use:  - well-described schema fields,      - meaningful query and mutation names,      - introspection,      - generated typed GraphQL clients.       Example:  ```graphql &quot;&quot;&quot; Cancels an issued invoice while preserving it for audit. Do not use for draft invoices. &quot;&quot;&quot; cancelInvoice(id: ID!): Invoice! ```  ### Messaging  Use message contracts plus AsyncAPI.  For example:  ```text RevokeUserSessions ```  should be clearly distinguishable from:  ```text UserSessionsRevoked ```  The first may be a command that application code sends.  The second is an event produced as a result of processing that command.  AsyncAPI can describe:  - messages,      - payload schemas,      - channels/topics,      - send/receive direction,      - headers,      - operation semantics.       A coding agent can then generate or discover the correct publisher abstraction.  ---  ## Preferred Architecture  A good integration architecture for LLM-generated code is:  ```text                        Business requirement                                 Ôåô                            Coding agent                                 Ôåô                  Discover business capability                                 Ôåô                      Strongly typed interface                                 Ôåô            ÔöîÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔö╝ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÉ            Ôöé                    Ôöé                    Ôöé         OpenAPI             GraphQL              AsyncAPI            Ôöé                    Ôöé                    Ôöé          REST                GraphQL             Messaging ```  The important abstraction presented to the coding agent should usually be a **typed, semantically named application client**.  Transport details should remain underneath it.  ---  ## Core Principle  A useful rule is:  &gt; External integrations should expose well-documented formal contracts, generate strongly typed clients from those contracts, and make those clients easy for coding agents to discover by business capability.  The coding agent should prefer those generated clients over constructing transport-level calls directly.  A well-designed API therefore becomes more than a machine-readable protocol description.  It becomes part of the semantic environment from which the LLM can infer:  - what capabilities exist,      - which capability matches the requested business operation,      - how it should be called,      - and which operations must not be confused with one another.</p>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Core Integration Flow</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Coding agents must not construct raw HTTP requests. The agent discovers capabilities, selects typed clients, and generates calling code.</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Requirement -&gt; Discover Client -&gt; Select Method -&gt; Generate Code -&gt; Typed Client -&gt; API</code></pre>
    </td>

  </tr>

  <tr style='background-color: var(--background-secondary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Business Intent Over Generic CRUD</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>External APIs must expose stable domain capabilities. Never expose internal database schemas or internal mechanics. Express intent directly in endpoint names. Prefer `cancelInvoice` over `updateEntity`.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>For actual deletions, standard CRUD works:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>DELETE /drafts/{id}</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>For state transitions, use explicit action routes:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>POST /invoices/{id}/cancel</code></pre>
    </td>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>OpenAPI Semantic Contracts</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>OpenAPI specs define runtime semantics, not just routes.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Weak spec:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>/users/{id}/sessions:
  delete:
    operationId: deleteSessions</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Strong spec:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>/users/{userId}/sessions:
  delete:
    operationId: revokeUserSessions
    summary: Revoke all active sessions for a user
    description: |
      Revokes all active authentication sessions belonging
      to the specified user.

      Use this operation when access for the user must be
      immediately invalidated.

      This operation does not delete the user account.</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Add negative constraints to descriptions:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>description: |
  Permanently deletes a draft invoice.

  Only draft invoices can be deleted.

  Do not use this operation for issued invoices.
  Issued invoices must be cancelled using cancelInvoice.</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Negative constraints stop agents from picking wrong endpoints.</p>
    </td>

  </tr>

  <tr style='background-color: var(--background-secondary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Strongly Typed Clients</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Generate typed clients with Kiota, NSwag, or OpenAPI Generator. Typed clients eliminate route typos and JSON parse bugs.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Do not let agents generate manual HTTP requests:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>await httpClient.DeleteAsync(
    $&quot;/users/{userId}/sessions&quot;);</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Direct agents to call typed client methods:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>await identityClient.RevokeUserSessionsAsync(
    userId,
    cancellationToken);</code></pre>
    </td>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Preserve Documentation in Generated SDKs</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Configure generators to emit OpenAPI descriptions as client docstrings. Docstrings put domain rules directly into the agent context window.</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>public interface IInvoicesClient {
    /// &lt;summary&gt;
    /// Cancels an issued invoice while preserving it for audit.
    /// Do not use for draft invoices.
    /// &lt;/summary&gt;
    Task CancelInvoiceAsync(
        Guid id,
        CancellationToken cancellationToken);

    /// &lt;summary&gt;
    /// Permanently deletes a draft invoice.
    /// Issued invoices cannot be deleted.
    /// &lt;/summary&gt;
    Task DeleteDraftInvoiceAsync(
        Guid id,
        CancellationToken cancellationToken);
}</code></pre>
    </td>

  </tr>

  <tr style='background-color: var(--background-secondary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Interface Discoverability</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Name client interfaces by business domain, not infrastructure.</p>
<li style='margin-left: 18px;'>Prefer: `IIdentityClient`, `IOrdersClient`, `IBillingClient`, `IInvoicesClient`</li>
<li style='margin-left: 18px;'>Avoid: `IServiceAClient`, `IBackendClient`, `IApiV2Client`</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>Domain names let agents locate tools through repository search.</p>
    </td>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Repository Guidance (`AGENTS.md`)</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Add integration rules to `AGENTS.md`:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>When integrating with another service:
1. Search generated clients by business domain.
2. Inspect method names and docstrings.
3. Call generated clients instead of raw HTTP clients.
4. Read the OpenAPI schema only to resolve parameter ambiguity.
5. Never construct raw URLs manually.</code></pre>
    </td>

  </tr>

  <tr style='background-color: var(--background-secondary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Semantic Errors</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Return machine-readable errors with recovery hints. Avoid opaque numeric codes:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>{
  &quot;errorCode&quot;: 3817
}</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Provide semantic error payloads with recovery paths:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>{
  &quot;code&quot;: &quot;invoice_already_issued&quot;,
  &quot;message&quot;: &quot;Issued invoices cannot be deleted.&quot;,
  &quot;suggestedOperation&quot;: &quot;cancelInvoice&quot;
}</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Agents use `suggestedOperation` to trigger fallback calls automatically.</p>
    </td>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Beyond REST</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Apply these rules across all integration patterns.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>GraphQL</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Write explicit mutation names and docstrings:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>&quot;&quot;&quot;
Cancels an issued invoice while preserving it for audit.
Do not use for draft invoices.
&quot;&quot;&quot;
cancelInvoice(id: ID!): Invoice!</code></pre>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Messaging</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Document message contracts with AsyncAPI. Distinguish commands from events by name:</p>
<li style='margin-left: 18px;'>Command: `RevokeUserSessions`</li>
<li style='margin-left: 18px;'>Event: `UserSessionsRevoked`</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>Commands execute tasks; events report state changes. Keep transport protocols below a typed, semantically named client interface.</p>
    </td>

  </tr>

</table>



---

## Note: Designing Software Architecture with LLM Assistance

**Metrics**: Original: **3314 words** | Restored: **899 words** | Compression: **-72.9%**


<table style='width: 100%; table-layout: fixed; border-collapse: collapse; margin-bottom: 24px;'>

  <tr style='background-color: var(--background-secondary-alt); border-bottom: 2px solid var(--background-modifier-border);'>

    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Original Input Note (3314 words)</th>

    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Restored Note - Gemini Flash High-Thinking (899 words)</th>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<strong style='color: var(--text-accent);'>Overview / Introduction</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>﻿--- title: Designing Software Architecture with LLM Assistance tags:   - software-architecture   - system-design   - ai-agents   - llm   - decision-making   - tradeoff-analysis aliases:   - LLM-Assisted Software Architecture   - Architecture Exploration with AI ---  ## Core idea  LLMs can significantly accelerate architectural exploration, but they are not reliable guarantees of completeness.  They are good at:  - exploring unfamiliar technologies,      - generating design alternatives,      - extracting constraints from available context,      - comparing trade-offs,      - producing prototypes,      - identifying common risks,      - reviewing an existing proposal.       They are weaker at:  - discovering constraints that were never documented,      - recognizing questions that neither the user nor the model knows should be asked,      - distinguishing a true requirement from an accidental property of the current implementation,      - understanding organizational and domain knowledge that exists only in peopleÔÇÖs heads,      - reliably signaling that the problem description is incomplete.       The main risk is not only hallucination.  A more subtle risk is that the model fills missing information with a plausible, typical scenario. The result may be coherent and professionally justified, even though it depends on assumptions that were never confirmed.  This creates an illusion of completeness.  ---  ## The model may provide a plausible answer instead of revealing missing knowledge  When the description is incomplete, an LLM tends to complete the story.  For example, it may implicitly assume that:  - eventual consistency is acceptable,      - operations are idempotent,      - messages may be retried safely,      - status transitions are linear,      - no external system reads the database directly,      - a relational database is suitable,      - rolling deployments do not create compatibility problems.       These assumptions may be reasonable in a typical system, but they may be false in the actual one.  The dangerous part is that a reasonable answer can look like an evidence-based answer.  A model can generate:  - a clean architecture,      - a detailed justification,      - diagrams,      - migration steps,      - code,      - a list of advantages and disadvantages.       This can make the user accept the proposal without examining the assumptions behind it.  Therefore:  &gt; A fluent and internally consistent answer should not be treated as evidence that the problem was understood completely.  ---  ## Constraints may come from business logic  Technical constraints often originate in business requirements.  The reasoning chain should be:  ```text Business requirement ÔåÆ required system property ÔåÆ architectural constraint ÔåÆ technology choice ```  Examples:  ```text Business rule: A customer must never be charged twice.  Required property: Duplicate execution must be safe or prevented.  Architectural consequence: Idempotency, deduplication, transactional boundaries, or unique operation identifiers are required. ```  ```text Business rule: The user must immediately know whether a reservation succeeded.  Required property: The result cannot rely only on eventual consistency.  Architectural consequence: A purely asynchronous workflow may be insufficient. ```  ```text Business rule: The organization must reconstruct why a decision was made years later.  Required property: Historical state and decision inputs must be preserved.  Architectural consequence: Audit records, versioning, immutable logs, or event history may be required. ```  A technology choice such as a database type may therefore be derived from the domain rather than being a purely technical preference.  At the same time, a stated constraint such as ÔÇ£we must use SQL ServerÔÇØ should be questioned.  It may represent:  - a real organizational standard,      - existing expertise,      - licensing constraints,      - integration dependencies,      - transactional requirements,      - direct reporting access,      - or only historical habit.       The model should ask what underlying requirement makes the constraint necessary.  ---  ## Categories of constraints  It is useful to divide constraints into three groups.  ### Explicit constraints  These are written in:  - requirements,      - tickets,      - documentation,      - ADRs,      - contracts,      - security policies.       The model can usually handle them well if they are clearly provided.  ### Discoverable constraints  These are not explicitly documented, but can be inferred from:  - code,      - tests,      - schemas,      - deployment manifests,      - integrations,      - production data,      - telemetry,      - incident history.       Finding them requires a dedicated discovery phase.  ### Hidden constraints  These exist only in:  - peopleÔÇÖs experience,      - manual processes,      - informal agreements,      - organizational politics,      - undocumented customer behavior,      - historical exceptions.       The model cannot discover them unless some trace of them is available.  This is the most dangerous category.  ---  ## Do not start with architecture selection  A weak process is:  ```text Problem description ÔåÆ architecture proposal ÔåÆ implementation ```  A stronger process is:  ```text Problem description ÔåÆ confirmed facts ÔåÆ missing information ÔåÆ assumptions ÔåÆ required system properties ÔåÆ design alternatives ÔåÆ attempt to invalidate alternatives ÔåÆ conditional recommendation ÔåÆ implementation ```  The first phase should be constraint discovery, not solution generation.  The model should first identify:  - what is known,      - what is inferred,      - what is assumed,      - what is unknown,      - what can be interpreted in multiple ways,      - what information could reverse the decision.       Only then should it propose technologies or architecture.  ---  ## Separate facts, inferences, assumptions, and unknowns  Important design analysis should not be presented as one continuous narrative.  A useful classification is:  ### Confirmed fact  Supported by a trusted source.  Example:  &gt; Deployments are rolling and old instances may run for up to thirty minutes.  ### Inference  Logically derived from confirmed facts.  Example:  &gt; Database changes must remain compatible with both application versions.  ### Assumption  Used temporarily because information is missing.  Example:  &gt; No external reporting system reads the modified table directly.  ### Unknown  Not yet established.  Example:  &gt; Whether message ordering must be preserved across all customers.  ### Typical practice  A common recommendation that may not apply here.  Example:  &gt; Using a message broker for long-running operations.  This classification prevents plausible assumptions from silently becoming requirements.  ---  ## Ask what could reverse the recommendation  One of the most valuable questions is:  &gt; Which missing information could make your recommendation completely different?  Other useful questions include:  - Under what conditions is this solution wrong?      - Which assumption has the greatest effect on the decision?      - What did you assume even though I did not provide it?      - What must be true for this design to work?      - Which of those conditions have not been verified?      - What system property would make another alternative preferable?      - Which parts of the recommendation come from my context, and which come from generic best practices?       A good recommendation should be conditional.  For example:  &gt; If delayed consistency is acceptable, operations are idempotent, and the team can operate the broker, asynchronous messaging is a strong option. If the user requires an immediate authoritative result, a synchronous transactional path may be more appropriate.  This is more useful than declaring one architecture universally best.  ---  ## Ask for the whole solution space, not only several technologies  When asked for ÔÇ£a few options,ÔÇØ the model may generate several variations of the same idea.  Instead, request options from different strategic categories:  - the simplest solution,      - a solution using existing infrastructure,      - an incremental solution,      - a reversible experiment,      - a conservative solution,      - a long-term target architecture,      - a less obvious but realistic option,      - a non-technical process change,      - changing or removing the requirement,      - doing nothing for now.       For every option, require:  - applicability conditions,      - assumptions,      - benefits,      - risks,      - operational cost,      - migration path,      - rollback difficulty,      - validation method,      - information that could change its evaluation.       ---  ## The model may prefer solutions it can implement comfortably  Even when the user asks a neutral question and does not suggest an answer, the resulting recommendation is not necessarily neutral.  An LLM tends to favor solutions that are:  - common in its training data, - well documented, - represented by many public examples, - easy to explain using familiar patterns, - easy for the model to turn into plausible code.  The model does not have to consciously decide, ÔÇ£I will choose this because I can implement it.ÔÇØ The bias arises indirectly:  ```text Familiar and high-probability approach ÔåÆ proposed more often ÔåÆ justified more fluently ÔåÆ implemented more successfully by the same model ```  This correlation is useful, because implementability matters. However, it can also narrow the solution space.  &gt; The solution the model can describe and generate most confidently is not necessarily the solution that best fits the problem.  ### Earlier context can anchor the recommendation  The bias can be triggered by merely mentioning a technology earlier in the conversation.  For example, if SQL Server, Kafka, Temporal, Kubernetes, microservices, or event sourcing appeared anywhere in the preceding discussion, the model may assign that technology more importance than it deserves. It may interpret the mention as:  - an implicit preference, - an available part of the infrastructure, - a constraint that should be preserved, - evidence that the user expects the technology to be used, - or the intended direction of the conversation.  This can happen even when the technology was mentioned only as an example, comparison point, rejected idea, or unrelated background detail.  The effect is a form of contextual anchoring:  ```text Technology appears in the context ÔåÆ becomes more available during generation ÔåÆ shapes the alternatives and evaluation criteria ÔåÆ is more likely to be recommended ```  Therefore, a neutral-sounding question asked after discussing a specific technology is not fully context-neutral. The model may produce a high-quality answer to the solution space implied by the conversation rather than reconsidering the entire solution space from first principles.  To reduce contextual anchoring:  - state explicitly that previously mentioned technologies are examples, not requirements, - ask the model to solve the problem once without using any technologies already mentioned, - request alternatives derived only from confirmed requirements, - ask which recommendations would disappear if the earlier technology names were removed from the conversation, - use a fresh context or an independent reviewer for important decisions, - distinguish technologies that are required, available, preferred, merely considered, and explicitly rejected.  A useful instruction is:  &gt; Treat every previously mentioned technology as non-binding unless it appears in the confirmed constraints. Derive the required system properties first, then generate alternatives without privileging technologies already present in the conversation.  A particularly risky workflow is:  ```text The model selects the criteria ÔåÆ selects the technology ÔåÆ justifies its own selection ÔåÆ implements it ÔåÆ reviews its own result ```  The entire chain may be internally consistent while optimizing for an unverified interpretation of the problem. A convincing implementation can then be mistaken for evidence that the architectural choice was correct.  To reduce this bias:  - separate solution selection from implementation, - ask for alternatives from genuinely different strategic categories, - require the model to distinguish problem fit from its confidence in implementation, - explicitly include less familiar or harder-to-generate approaches when they may fit the constraints, - let a human define or approve the evaluation criteria, - use an independent review that does not inherit the original recommendation as a fact, - evaluate the architecture before showing how easily code can be generated for it.  A useful question is:  &gt; Is this solution recommended because it best satisfies the confirmed constraints, or because it is popular, well documented, and easy for the model to implement?  The model cannot perfectly inspect its own internal reasoning, so its answer should not be treated as proof. The question is still valuable because it forces an explicit comparison between problem fit, ecosystem familiarity, and implementation confidence.  For important decisions, ask the model to report these dimensions separately:  | Dimension | Question | | --- | --- | | Problem fit | How well does the option satisfy confirmed requirements and constraints? | | Evidence quality | Which parts are supported by project evidence rather than generic practice? | | Implementation confidence | How reliably can the model produce and test the implementation? | | Ecosystem familiarity | Is the recommendation favored because examples and documentation are abundant? | | Decision uncertainty | Which missing information could change the ranking? |  Implementation confidence is a legitimate criterion, but it should be visible and weighted deliberately rather than silently determining the architecture.  ---   ## Review the problem across multiple dimensions  A model should be asked to inspect the problem from several perspectives, not only technology selection.  Useful dimensions include:  - business rules and invariants,      - state transitions,      - data ownership,      - consistency,      - transactions,      - concurrency,      - ordering,      - duplication and idempotency,      - retries and timeouts,      - partial failures,      - integration contracts,      - version compatibility,      - deployment strategy,      - rollback,      - migration,      - security and trust boundaries,      - privacy,      - auditability,      - retention,      - performance,      - scale,      - observability,      - diagnostics,      - operational support,      - cost,      - team expertise,      - vendor lock-in,      - reversibility.       The purpose is not to generate an enormous checklist for every decision.  The purpose is to identify which dimensions can materially change this specific decision.  ---  ## Use the model in multiple roles  A single model can be prompted to perform different reviews.  ### Domain analyst  Extracts:  - business rules,      - actors,      - invariants,      - states,      - exceptions,      - ambiguous behavior.       ### Architect  Generates design alternatives and trade-offs.  ### Skeptic  Searches for:  - hidden assumptions,      - missing constraints,      - failure scenarios,      - cases that invalidate the recommendation.       ### Operator  Checks:  - deployment,      - monitoring,      - rollback,      - support procedures,      - failure recovery,      - maintenance cost.       ### Security reviewer  Checks:  - trust boundaries,      - sensitive data,      - authorization,      - abuse scenarios,      - compliance implications.       ### Migration reviewer  Checks:  - old and new versions running together,      - schema compatibility,      - staged rollout,      - backfill,      - rollback,      - external consumers.       Using multiple roles does not make the model automatically correct.  It forces the reasoning to be examined from different angles.  ---  ## Exploration mode and commitment mode  LLMs are especially valuable because they reduce the cost of experimentation.  They allow teams to:  - explore unfamiliar approaches,      - build prototypes quickly,      - compare several options,      - generate test harnesses,      - simulate migrations,      - investigate new libraries,      - prepare disposable proofs of concept.       This supports a more experimental architecture process:  ```text Hypothesis ÔåÆ cheap prototype ÔåÆ measurement ÔåÆ criticism ÔåÆ decision ```  However, fast implementation must not be confused with understanding.  The model greatly reduces the cost of entering a new solution, but may not equally reduce the cost of understanding:  - its failure model,      - operational complexity,      - long-term maintenance,      - migration difficulty,      - scaling behavior,      - guarantees and limitations,      - organizational impact.       Therefore it is useful to distinguish two modes.  ### Exploration mode  Optimize for speed and learning.  - Generate many ideas.      - Try unfamiliar technologies.      - Accept explicitly labeled temporary assumptions.      - Build disposable prototypes.      - Avoid production-level completeness.      - Prefer reversible experiments.       ### Commitment mode  Optimize for correctness and reversibility.  - Confirm constraints.      - Verify primary documentation.      - Test failures and edge cases.      - Review operational requirements.      - Remove hidden assumptions.      - Plan migration and rollback.      - Record the architecture decision.      - Require human approval.       The dangerous transition is when an exploration prototype silently becomes production architecture.  ---  ## The best role of the model  The model should not be treated as an authority that produces the architecture.  It is better used as an accelerator for:  - knowledge exploration,      - question generation,      - constraint discovery,      - option generation,      - trade-off analysis,      - prototype creation,      - adversarial review,      - documentation,      - verification planning.       The human remains responsible for confirming the model of reality on which the architecture depends.  The most important question is not:  &gt; Did the model produce a reasonable solution?  It is:  &gt; Is the solution based on confirmed properties of this system, or on plausible defaults borrowed from typical systems?  ---  ## Practical conversation pattern  ### Phase 1: problem discovery  Ask the model not to design anything yet.  Request:  - confirmed facts,      - inferred consequences,      - assumptions,      - unknowns,      - ambiguities,      - missing dimensions,      - questions ranked by decision impact.       ### Phase 2: constraint verification  For each important claim, identify:  - its source,      - confidence,      - effect on the architecture,      - method of verification.       ### Phase 3: option generation  Generate alternatives from meaningfully different categories.  Do not allow an unconditional recommendation.  ### Phase 4: adversarial review  Assume each proposal is wrong.  Search for:  - domain properties that invalidate it,      - partial failure scenarios,      - hidden consumers,      - deployment problems,      - migration traps,      - operational costs,      - POC-to-production gaps.       ### Phase 5: conditional recommendation  State:  - the preferred option,      - the assumptions under which it is preferred,      - the conditions that would change the recommendation,      - unresolved risks,      - required experiments or measurements.       ### Phase 6: implementation  Provide the implementing agent with:  - business goal,      - global invariants,      - approved architecture,      - local module context,      - neighboring contracts,      - known assumptions,      - required tests,      - prohibited changes.       ---  ## Reusable prompt: discovery before design  ```text Help me analyze this architecture problem, but do not propose a solution yet.  First, separate the available information into:  - confirmed facts, - conclusions derived from those facts, - working assumptions, - missing information, - typical practices that may not apply to this system.  Do not fill missing information with standard assumptions without labeling them explicitly.  Identify all important dimensions of the problem, including dimensions I may not know to ask about:  - business rules and invariants, - data and consistency, - transactions and concurrency, - ordering, retries, and idempotency, - partial failures, - integrations, - performance and scale, - security and privacy, - audit and retention, - deployment, migration, and rollback, - observability and operations, - cost and team expertise.  Prepare the questions whose answers could materially change the architecture decision. Rank them by impact.  Also identify:  - assumptions you would otherwise make from the description, - the riskiest assumptions, - missing information that could completely reverse the recommendation, - questions that an inexperienced person might not know to ask.  Stop after the problem analysis and questions. Do not select technologies or architecture yet. ```  ---  ## Reusable prompt: generating alternatives  ```text Based only on confirmed facts and explicitly stated assumptions, generate meaningfully different solution options.  Include:  - the simplest option, - an option using the current system, - an incremental option, - a reversible option, - a conservative option, - a long-term target option, - a less obvious but realistic option, - changing the requirement or avoiding a technical solution.  For each option, provide:  1. What it solves. 2. The conditions it requires. 3. Its assumptions. 4. When it is a good choice. 5. When it is a bad choice. 6. Costs and risks. 7. Operational consequences. 8. Migration and rollback difficulty. 9. A cheap experiment that could validate it. 10. Missing information that could change its evaluation.  Do not present any option as unconditionally best. ```  ---  ## Reusable prompt: adversarial review  ```text Assume the proposed solution is wrong.  Find:  - hidden assumptions, - missing constraints, - edge cases, - unusual domain properties, - concurrency problems, - partial failures, - retry and duplication issues, - migration and deployment risks, - operational costs, - organizational dependencies, - cases where the solution works in a proof of concept but fails in production.  Then answer:  1. What must be true for the solution to work? 2. Which of those conditions have not been verified? 3. What could completely reverse the recommendation? 4. What tests, measurements, documents, code analysis, or stakeholder conversations would verify the assumptions? 5. Which parts come from the actual context, and which come only from generic best practices? ```  ---  ## Final mental model  An LLM answer is not the architecture.  It is a proposal generated from a model of the system.  That model contains:  - facts,      - inferred consequences,      - assumptions,      - omissions,      - generic patterns.       The first task is therefore not to validate the proposed technology.  The first task is to validate the model of reality that produced the proposal.  LLMs make it possible to explore more options, learn faster, and run cheaper experiments. They should increase the amount of reversible experimentation, not the amount of irreversible architectural risk.</p>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Overview / Introduction</strong><hr style='margin: 4px 0 8px 0;'><h2 style='margin-top: 16px; margin-bottom: 8px; color: var(--text-accent);'>LLM-Assisted Systems Design</h2>
<p style='margin-bottom: 8px; line-height: 1.45;'>LLMs generate plausible architectures but miss undocumented boundaries.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Models fill unstated requirements with typical defaults.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>They implicitly assume eventual consistency, idempotent endpoints, or linear states.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>These defaults often fail in production systems.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Never accept fluent output as proof of technical accuracy.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Audit core assumptions before picking technologies or writing code.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>---</p>
    </td>

  </tr>

  <tr style='background-color: var(--background-secondary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Deriving Constraints from Invariants</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Technical choices stem from business invariants.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Always trace choices through this derivation chain:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Business Rule -&gt; System Invariant -&gt; Architecture Constraint -&gt; Technology Choice</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Examples:</p>
<li style='margin-left: 18px;'>**Rule**: Never double-charge a customer.</li>
<li style='margin-left: 18px;'>**Invariant**: Operations require duplicate execution prevention.</li>
<li style='margin-left: 18px;'>**Constraint**: Enforce idempotency keys with unique database constraints.</li>
<li style='margin-left: 18px;'>**Rule**: Deliver immediate booking confirmations.</li>
<li style='margin-left: 18px;'>**Invariant**: The user path cannot rely on asynchronous convergence.</li>
<li style='margin-left: 18px;'>**Constraint**: Use synchronous ACID transactions over eventual consistency.</li>
<li style='margin-left: 18px;'>**Rule**: Audit decision inputs five years later.</li>
<li style='margin-left: 18px;'>**Invariant**: Preserve point-in-time state transitions and inputs.</li>
<li style='margin-left: 18px;'>**Constraint**: Implement an immutable, append-only event log.</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>Challenge arbitrary mandates like &quot;must use PostgreSQL&quot;.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Extract the underlying driver: license limits, reporting tools, DBA skills, or legacy habit.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>---</p>
    </td>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Constraint Taxonomy</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Classify constraints into three operational groups:</p>
<li style='margin-left: 18px;'>**Explicit**: Exists in ADRs, tickets, specifications, and schemas. Models parse these well.</li>
<li style='margin-left: 18px;'>**Discoverable**: Exists in codebases, configs, migrations, and telemetry. Extract these with targeted prompts.</li>
<li style='margin-left: 18px;'>**Hidden**: Exists in tribal memory, manual runbooks, and informal agreements. Humans must supply this context.</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>---</p>
    </td>

  </tr>

  <tr style='background-color: var(--background-secondary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Discovery-First Architecture Workflow</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Do not jump directly to stack selection.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Flawed pipeline:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Problem -&gt; Tech Stack -&gt; Code</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Pragmatic pipeline:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Problem -&gt; Facts -&gt; Gaps -&gt; Invariants -&gt; Alternatives -&gt; Invalidation -&gt; Stack Choice</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Structure context into five explicit categories:</p>
<li style='margin-left: 18px;'>**Confirmed Fact**: Verified property backed by code, tests, or production metrics.</li>
<li style='margin-left: 18px;'>**Inference**: Logical deduction derived directly from confirmed facts.</li>
<li style='margin-left: 18px;'>**Assumption**: Temporary placeholder filling a context gap.</li>
<li style='margin-left: 18px;'>**Unknown**: Unresolved variable requiring investigation.</li>
<li style='margin-left: 18px;'>**Common Practice**: Industry default that might fail your specific workload.</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>---</p>
    </td>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Bias and Context Anchoring</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Models suffer from contextual anchoring.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Mentioning a tool primes the model to recommend it.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>The model designs around mentioned tools, even when unsuited for the workload.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Reset context windows when evaluating critical architectural forks.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Instruct the model to solve the problem without previously mentioned technologies.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Models also favor patterns frequent in public training data.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Easy generation does not indicate correct architecture.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Evaluate proposals against this matrix:</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>| Dimension | Evaluation Focus |</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>| :--- | :--- |</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>| **Problem Fit** | Satisfies verified business invariants |</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>| **Grounding** | Draws from project telemetry or code |</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>| **Operational Risk** | Quantifies failure modes, rollouts, and rollback costs |</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>| **Availability Bias** | Over-indexes on boilerplate code and documentation |</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>---</p>
    </td>

  </tr>

  <tr style='background-color: var(--background-secondary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Strategic Solution Exploration</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Reject homogeneous technology options.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Force alternatives across distinct strategic archetypes:</p>
<li style='margin-left: 18px;'>**Simplest viable**: Minimum moving parts.</li>
<li style='margin-left: 18px;'>**Existing stack**: Zero new operational dependencies.</li>
<li style='margin-left: 18px;'>**Reversible experiment**: High-leverage feature flag or adapter pattern.</li>
<li style='margin-left: 18px;'>**Non-technical change**: Policy shift or dropped requirement.</li>
<li style='margin-left: 18px;'>**Long-term architecture**: Eventual target state under sustained scale.</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>Require explicit failure modes, operational burdens, and rollback mechanics for every option.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>---</p>
    </td>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Dual Operating Modes</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Run architecture work in two separate modes:</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Exploration Mode</h4>
<li style='margin-left: 18px;'>Prioritize discovery speed.</li>
<li style='margin-left: 18px;'>Build quick spikes.</li>
<li style='margin-left: 18px;'>Test unfamiliar libraries.</li>
<li style='margin-left: 18px;'>Accept labeled assumptions.</li>
<li style='margin-left: 18px;'>Write throwaway prototypes.</li>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Commitment Mode</h4>
<li style='margin-left: 18px;'>Prioritize correctness and reversibility.</li>
<li style='margin-left: 18px;'>Verify edge cases.</li>
<li style='margin-left: 18px;'>Audit failure domains.</li>
<li style='margin-left: 18px;'>Write migration scripts.</li>
<li style='margin-left: 18px;'>Eliminate hidden assumptions.</li>
<li style='margin-left: 18px;'>Require human sign-off.</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>Never promote an exploration prototype directly to production.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>---</p>
    </td>

  </tr>

  <tr style='background-color: var(--background-secondary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Review Roles and System Dimensions</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Prompt the model through distinct operational personas:</p>
<li style='margin-left: 18px;'>**Domain Analyst**: Extract business invariants, actors, state transitions, and edge cases.</li>
<li style='margin-left: 18px;'>**Architect**: Map tradeoffs, state boundaries, component coupling, and blast radiuses.</li>
<li style='margin-left: 18px;'>**Skeptic**: Find broken assumptions, scale limits, poison messages, and race conditions.</li>
<li style='margin-left: 18px;'>**Operator**: Review deployment mechanics, zero-downtime rollouts, observability, and disaster recovery.</li>
<li style='margin-left: 18px;'>**Security Lead**: Audit trust boundaries, auth models, data retention, and compliance limits.</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>Audit every proposal across these technical vectors:</p>
<li style='margin-left: 18px;'>**State**: Concurrency, idempotency keys, ordering guarantees, transactional boundaries.</li>
<li style='margin-left: 18px;'>**Failure**: Partial outages, cascading failures, backoff retries, dead-letter queues.</li>
<li style='margin-left: 18px;'>**Operations**: Dual-write avoidance, backward schema compatibility, telemetry, rollback cost.</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>---</p>
    </td>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<em>(No matching section)</em>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Core Architecture Prompts</strong><hr style='margin: 4px 0 8px 0;'><h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Discovery Prompt</h4>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Analyze this system problem. Do not propose solutions yet.

Separate the input into:
- Confirmed facts
- Inferences derived from facts
- Working assumptions
- Missing information
- Generic defaults that might fail here

Highlight business invariants, concurrency models, transactional boundaries, and failure states.
List questions whose answers could reverse the architectural direction.
Rank questions by impact.
Stop here.</code></pre>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Alternatives Prompt</h4>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Generate distinct architectural options using only confirmed facts and explicit assumptions.

Include these archetypes:
- Simplest viable design
- Zero-new-infrastructure design (existing stack only)
- Reversible experiment
- Non-technical or process-level fix
- Long-term target architecture

For each option detail:
1. Required system properties
2. Operational cost and blast radius
3. Failure modes
4. Migration and rollback strategy
5. Information that invalidates this choice

Do not declare any option universally superior.</code></pre>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Adversarial Invalidation Prompt</h4>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Assume this proposed solution fails in production.

Identify:
- Unstated assumptions
- Latent race conditions and concurrency failures
- Partial outage behaviors
- Deployment or backward-compatibility traps
- Production costs hidden during prototyping

Answer:
1. What unverified condition breaks this system?
2. What findings reverse this decision?
3. What benchmarks or tests prove this design?</code></pre>
    </td>

  </tr>

</table>



---

## Note: Developing Features with AI Coding Agents

**Metrics**: Original: **487 words** | Restored: **290 words** | Compression: **-40.5%**


<table style='width: 100%; table-layout: fixed; border-collapse: collapse; margin-bottom: 24px;'>

  <tr style='background-color: var(--background-secondary-alt); border-bottom: 2px solid var(--background-modifier-border);'>

    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Original Input Note (487 words)</th>

    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Restored Note - Gemini Flash High-Thinking (290 words)</th>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<strong style='color: var(--text-accent);'>Overview / Introduction</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>﻿--- title: Developing Features with AI Coding Agents tags:   - ai-agents   - software-engineering   - agentic-workflows   - feature-development   - testing   - code-review aliases:   - Feature Development with Agents   - End-to-End Agentic Feature Lifecycle ---  ## A Strong Workflow for Larger Features  A useful process is:  ```text repository analysis ÔåÆ behavioral specification ÔåÆ examples and decision tables ÔåÆ acceptance tests ÔåÆ human review ÔåÆ implementation of one vertical slice ÔåÆ architectural review ÔåÆ full implementation ÔåÆ independent skeptical review ÔåÆ documentation update ```  ### Step 1: Repository Analysis  The agent should first locate:  - existing business flows,      - data models,      - integration points,      - transactions,      - existing tests,      - compatibility risks,      - hidden assumptions.       It should not modify the code yet.  ### Step 2: Behavioral Specification  The specification should include:  - business objective,      - terminology,      - rules,      - exceptions,      - negative cases,      - side effects,      - compatibility requirements,      - non-functional constraints,      - explicit out-of-scope items.       ### Step 3: Tests Before Implementation  The agent can prepare:  - business-rule tests,      - acceptance tests,      - regression tests,      - API contract tests,      - integration tests.       New tests may initially fail. That confirms that they detect the missing behavior.  ### Step 4: Human Review of Meaning  The reviewer should not focus only on test implementation quality.  The main questions are:  - Does the test describe the correct business behavior?      - Did the agent invent an unstated rule?      - Are negative cases present?      - Are priorities between rules correct?      - Is the test coupled to one implementation unnecessarily?      - Does the test preserve an accidental legacy behavior?       ### Step 5: Freeze the Acceptance Contract  The implementing agent should not freely modify approved acceptance tests.  It may add technical tests, but changes to the accepted business contract require another review.  ### Step 6: Implement a Small Vertical Slice  Instead of generating the whole feature at once, implement one full path from entry point to result.  This reveals whether the architecture is appropriate before dozens of files are created.  ---  ## Tests Are Executable Specifications, but Not Complete Specifications  A test demonstrates an expected example.  It does not always explain:  - why the rule exists,      - what a domain term means,      - what must not be simplified,      - why two similar cases differ,      - which behavior is historical but still required.       The strongest combination is:  ```text business decision + examples or decision table + acceptance tests + explicit implementation ```  The agent should not be allowed to define both the implementation and the meaning of correctness without independent human review.  Otherwise, it can write tests that confirm its own incorrect interpretation.  ---  ## Practical Working Rules  ### For feature development  - Analyze before modifying.      - Write or approve the behavioral specification.      - Use examples and decision tables.      - Review acceptance tests before implementation.      - Freeze approved business tests.      - Implement one vertical slice first.      - Separate mechanical changes from business changes.      - Require a skeptical second review.</p>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Agent Feature Workflow</strong><hr style='margin: 4px 0 8px 0;'><pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Analyze repo -&gt; Write spec -&gt; Build decision tables -&gt; Write acceptance tests -&gt; Human audit -&gt; Build vertical slice -&gt; Arch review -&gt; Full build -&gt; Skeptical review</code></pre>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>1. Repository Analysis</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Point the agent at the codebase before writing code.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Map data models, integration boundaries, transactions, and hidden constraints.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Keep code read-only during this phase.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>2. Behavioral Specification</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Define business rules, domain terms, negative paths, and out-of-scope boundaries.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Build decision tables for branching logic.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Models invent requirements when branch priorities stay ambiguous.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>3. Test-First Setup</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Write acceptance and contract tests before writing feature code.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Run tests to confirm they fail.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Failing tests prove the suite catches missing behavior.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>4. Audit Test Semantics</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Review test meaning, not syntax.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Check whether the agent hallucinated unstated requirements.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Ensure negative cases run.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Verify the tests reject accidental legacy behavior.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>5. Freeze Test Contracts</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Lock approved acceptance tests in git.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Block the agent from editing these tests while writing code.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Allow the agent to add internal unit tests only.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Review all changes to acceptance files manually.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>6. Vertical Slice</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Build one complete path from ingress to storage.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Validate architectural boundaries on this single slice.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Do not scaffold multiple files before this slice passes review.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>7. Stop Circular Logic</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Tests show examples. They do not capture intent.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Never let the agent write both tests and code unsupervised.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Self-authored tests confirm the agent&#x27;s own misconceptions.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Anchor tests to explicit decision tables.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Execution Checklist</h4>
<li style='margin-left: 18px;'>Inspect the repo before editing.</li>
<li style='margin-left: 18px;'>Write explicit specs with decision tables.</li>
<li style='margin-left: 18px;'>Freeze failing acceptance tests.</li>
<li style='margin-left: 18px;'>Build one end-to-end slice first.</li>
<li style='margin-left: 18px;'>Separate mechanical refactors from business changes.</li>
<li style='margin-left: 18px;'>Review final output with a skeptical peer.</li>
    </td>

  </tr>

</table>



---

## Note: Hidden Abstractions May Become More Expensive in Agent-Maintained Code

**Metrics**: Original: **2509 words** | Restored: **543 words** | Compression: **-78.4%**


<table style='width: 100%; table-layout: fixed; border-collapse: collapse; margin-bottom: 24px;'>

  <tr style='background-color: var(--background-secondary-alt); border-bottom: 2px solid var(--background-modifier-border);'>

    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Original Input Note (2509 words)</th>

    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Restored Note - Gemini Flash High-Thinking (543 words)</th>

  </tr>

  <tr style='background-color: var(--background-primary);; border-bottom: 1px solid var(--background-modifier-border);'>

    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>
<strong style='color: var(--text-accent);'>Overview / Introduction</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>﻿--- title: Hidden Abstractions May Become More Expensive in Agent-Maintained Code tags:   - software-architecture   - ai-agents   - abstraction   - code-maintainability   - simplicity   - software-engineering aliases:   - Cost of Hidden Abstractions with Agents   - Explicit vs Magic Abstractions in AI Era ---  Modern software engineering often tries to remove repetitive concerns from local code.  Instead of explicitly writing validation, authorization, retries, transactions, logging, tracing, error mapping, and other infrastructure in every operation, we move them into reusable mechanisms such as:  - middleware,      - interceptors,      - decorators,      - dependency injection,      - HTTP message handlers,      - framework filters,      - MediatR behaviors,      - Entity Framework interceptors and query filters,      - global exception handling,      - conventions,      - assembly scanning,      - ambient context.       This can make individual methods extremely small.  For example:  ```csharp public Task&lt;Response&gt; GetOrder(GetOrderRequest request) {     return mediator.Send(request); } ```  The method appears simple.  However, the actual execution may look more like:  ```text HTTP request ÔåÆ authentication middleware ÔåÆ authorization middleware ÔåÆ exception middleware ÔåÆ request validation ÔåÆ MediatR ÔåÆ logging behavior ÔåÆ transaction behavior ÔåÆ handler ÔåÆ Entity Framework query filter ÔåÆ database interceptor ÔåÆ SQL ÔåÆ response mapping ÔåÆ serialization ```  The local code is simple, but the semantics are not.  This distinction may become increasingly important when software is primarily modified by agents.  ## Local Simplicity Is Not the Same as Semantic Simplicity  An agent working on a method must understand more than the code visible inside the method.  Consider:  ```csharp await httpClient.SendAsync(request); ```  The request may implicitly include:  - authentication headers,      - correlation identifiers,      - retry policies,      - circuit breakers,      - timeouts,      - telemetry,      - logging,      - tenant context.       The important behavior is distributed across configuration and framework mechanisms.  Similarly:  ```csharp context.Orders.ToListAsync(); ```  may actually mean:  ```text load Orders where TenantId == CurrentTenant excluding soft-deleted records using an interceptor-defined database command behavior ```  because of global query filters and other Entity Framework configuration.  The problem is therefore not simply abstraction.  The deeper problem is **non-local semantics**.  The meaning of a line of code depends on code that is not locally visible.  ## Hidden Execution Context Is Particularly Difficult  Some dependencies are not passed explicitly at all.  They may come from:  ```text HttpContext AsyncLocal Activity.Current ClaimsPrincipal current tenant services current culture scoped dependency resolution feature flags environment configuration ```  A method can therefore appear to depend on:  ```csharp Process(Order order) ```  while its real inputs include:  ```text order current user tenant feature configuration current transaction request metadata culture authorization context ```  This makes the true dependency graph much larger than the function signature suggests.  Humans often tolerate this because experienced developers gradually learn the architecture.  An agent entering a repository for a single task must rediscover it.  ## Dynamic Dependency Injection Makes the Problem Worse  Constructor injection itself is usually relatively easy to understand.  The situation becomes more difficult when implementations depend on runtime context:  ```csharp services.AddScoped&lt;IPriceCalculator&gt;(sp =&gt; {     var context = sp.GetRequiredService&lt;OperationContext&gt;();      return context.Channel switch     {         Channel.Web =&gt; new WebPriceCalculator(),         Channel.Api =&gt; new ApiPriceCalculator(),         _ =&gt; new DefaultPriceCalculator()     }; }); ```  Local code may only contain:  ```csharp priceCalculator.Calculate(order); ```  but the implementation that actually runs depends on external state.  Similar problems appear with:  - keyed services,      - decorators,      - assembly scanning,      - open generic registrations,      - conditional registration,      - plugin architectures.       The call site no longer tells the agent what code it is calling.  ## Interceptors and Pipelines Can Hide Business-Relevant Semantics  Cross-cutting abstractions become especially problematic when they contain behavior that changes the meaning of an operation.  A call such as:  ```csharp repository.Save(order); ```  may secretly perform:  ```text authorization ÔåÆ validation ÔåÆ transaction creation ÔåÆ audit logging ÔåÆ persistence ÔåÆ event publication ÔåÆ cache invalidation ```  Some of these are infrastructure concerns.  Others are part of the operation&#x27;s semantics.  The distinction matters.  A generic timing metric being invisible is usually harmless.  A transaction boundary, retry policy, tenant filter, authorization rule, or business validation being invisible can fundamentally change how an agent should modify the operation.  ## Agents May Change the Economics of Explicit Code  Traditional software engineering strongly rewards removing repetition.  The reasoning is understandable:  ```text duplication ÔåÆ more code ÔåÆ more maintenance ÔåÆ more opportunities for inconsistency ```  This encourages patterns such as:  ```text DRY ÔåÆ centralize behavior ÔåÆ hide repeated mechanics behind abstractions ```  But agents reduce the cost of producing and maintaining repetitive code.  This creates the possibility of a different tradeoff:  ```text some duplication ÔåÆ greater semantic locality ÔåÆ easier reasoning ÔåÆ safer automated modification ```  The goal does not need to be eliminating abstractions.  It may instead be eliminating **invisible semantics**.  ## Explicit Execution Pipelines  One possible direction is to make important operation semantics visible directly in the operation definition.  Instead of:  ```csharp return mediator.Send(request); ```  an operation might resemble:  ```csharp return Operation     .From(request)     .Validate&lt;GetOrderValidator&gt;()     .Authorize&lt;ReadOrderPolicy&gt;()     .Retry(ExternalPolicies.Read)     .Execute&lt;GetOrderHandler&gt;()     .ValidateResponse&lt;GetOrderResponseValidator&gt;()     .MapErrors&lt;OrderHttpErrors&gt;()     .Return(); ```  The exact syntax is not important.  The important property is that the execution graph becomes visible:  ```text request ÔåÆ validation ÔåÆ authorization ÔåÆ retry policy ÔåÆ execution ÔåÆ response validation ÔåÆ error mapping ÔåÆ response ```  An agent can reason about the operation without reconstructing several layers of framework configuration.  ## This Does Not Mean Eliminating All Abstraction  Some abstractions should remain hidden.  For example, an ASP.NET action can reasonably receive:  ```csharp GetOrderRequest request ```  without explicitly handling:  ```text TCP HTTP parsing TLS UTF-8 JSON tokenization object allocation deserialization ```  These are implementation mechanisms.  The operation usually does not care how the DTO was produced.  Similarly, returning a response object does not require the business operation to explicitly handle HTTP serialization or socket writes.  A useful boundary may therefore be:  ```text framework owns mechanics operation owns semantics ```  The framework can hide how input becomes a DTO.  The operation should make visible the decisions that influence what the operation means.  ## Infrastructure Can Be Implicit More Safely Than Business Semantics  Not all hidden behavior has the same cost.  Relatively safe candidates for implicit handling include:  ```text generic logging tracing request timing metrics compression correlation IDs serialization ```  More dangerous hidden behavior includes:  ```text authorization tenant selection business validation transaction boundaries retry behavior idempotency cache semantics feature flags currency or locale selection handler selection error interpretation ```  A possible rule is:  &gt; Infrastructure may be implicit. Business-relevant semantics should preferably be explicit.  The boundary will not always be perfect, but it provides a useful design direction.  ## Global Configuration Still Has Value  Making behavior explicit does not require copying implementation details into every operation.  For example, retry may still be centrally configured:  ```csharp RetryPolicies.ExternalRead ```  could define:  ```text 3 attempts exponential backoff jitter retry on timeout retry on HTTP 502/503/504 ```  while the operation only says:  ```csharp .Retry(RetryPolicies.ExternalRead) ```  This separates two different concerns:  ```text local code: WHAT semantic policy applies  central configuration: HOW that policy works ```  This may be a particularly useful compromise.  Global configuration defines reusable policy.  The call site explicitly declares that the policy participates in the operation.  ## Named Semantics Are Better Than Silent Global Behavior  Compare:  ```csharp await client.SendAsync(request); ```  where retry is silently injected by global `HttpClient` configuration,  with:  ```csharp await request     .Retry(RetryPolicies.ExternalRead)     .Execute(); ```  The second version still uses abstraction.  However, the abstraction leaves a visible semantic trace.  The agent immediately knows that:  ```text this operation may execute more than once ```  That knowledge can affect decisions about:  - idempotency,      - database writes,      - external side effects,      - request identifiers,      - duplicate handling.       The exact implementation of retry remains reusable and centrally controlled.  ## Large Applications Already Struggle With Truly Global Policies  This approach may also address a problem that exists even without AI.  In a large system containing:  ```text hundreds of endpoints many modules multiple databases different external integrations different SLA requirements different business risks ```  a single global policy is rarely actually global.  It gradually becomes:  ```text default behavior except Payments except Reporting except legacy integration except bulk operations except endpoint X unless attribute Y exists unless interface Z is implemented ```  The centralized configuration eventually becomes another complex program.  The apparent simplicity of each endpoint is paid for by complexity elsewhere.  Module-level or operation-class policies may therefore scale better:  ```text system defaults ÔåÆ module defaults ÔåÆ operation category ÔåÆ explicit operation override ```  For example:  ```text Catalog:     external reads may retry  Payments:     commands do not retry unless explicitly idempotent  Reporting:     long timeout     read-only transaction semantics ```  The policy implementation remains centralized, while the semantic choice stays close to the operation.  ## Abstractions Could Become Mechanically Expandable  There is another possible solution that does not require removing existing abstractions.  Future frameworks and development tools could expose the resolved semantics of an operation.  The source might contain:  ```csharp .Retry(RetryPolicies.ExternalRead) ```  while an agent can request:  ```text resolve RetryPolicies.ExternalRead ```  and receive:  ```text max attempts: 3 backoff: exponential jitter: enabled retry:   timeout   502   503   504 ```  The same mechanism could resolve an entire endpoint:  ```text GetOrder  authentication:     required  authorization:     ReadOrderPolicy  validation:     GetOrderValidator  tenant:     request tenant  transaction:     read-only  retry:     ExternalRead     attempts: 3  handler:     GetOrderHandler  cache:     OrderById     TTL: 5 minutes ```  This suggests an important property for future abstractions:  &gt; Abstractions should be mechanically expandable.  Documentation is useful.  A machine-readable resolved execution model is much more useful to an agent.  ## Good Abstractions for Agents May Optimize for Different Things  Traditional APIs often optimize for:  ```text few lines few parameters minimal boilerplate maximum reuse ```  Agent-oriented APIs may increasingly optimize for:  ```text semantic locality explicit dependencies visible execution flow mechanically discoverable behavior predictable composition ```  This does not imply that code must become low-level.  For example:  ```csharp .RetryTransient(3) ```  is still an abstraction.  It hides backoff implementation, timers, exception matching, and scheduling.  But it preserves the fact that matters semantically:  ```text the operation may execute multiple times ```  By contrast:  ```csharp .ExecuteUsingStandardEnterprisePolicies() ```  may hide almost everything the agent needs to know.  A useful distinction is therefore:  &gt; A good abstraction reduces syntax without hiding important semantics.   ## Business Meaning Should Be Encoded in the Same Vocabulary  Semantic locality is not only about where behavior executes.  It is also about whether the code uses the same concepts and vocabulary as the domain, documentation, API contracts, database schema, tests, and operational descriptions.  Consider:  ```csharp if (payment != null) {     ... } ```  In a particular system, this may implicitly mean:  ```text the invoice is unpaid ```  A developer who has worked on the system for years may know that convention.  An agent may not.  The agent sees evidence:  ```text Payment exists ```  but must infer the business conclusion:  ```text invoice is unpaid ```  That inference may be correct, incorrect, or missed entirely.  Compare that with:  ```csharp if (payment.Status == PaymentStatus.Unpaid) {     ... } ```  or:  ```csharp if (payment.IsUnpaid) {     ... } ```  Now the business concept is explicitly represented in the code.  This matters particularly when the same concept appears elsewhere in the system.  Suppose the documentation says:  ```text retry unpaid payments ```  the API specification contains:  ```text paymentStatus: unpaid ```  and tests are named:  ```text ShouldRetryUnpaidPayment ```  An agent searching for or reasoning about &quot;unpaid payment&quot; can directly associate all of these artifacts with:  ```csharp PaymentStatus.Unpaid ```  It has a much weaker semantic connection to:  ```csharp payment != null ```  The same problem appears with sentinel values and technical representations:  ```csharp amount == 0 endDate == null retryCount == -1 status == 2 customerId != null ```  These values may encode business meanings such as:  ```text free active unlimited retries awaiting payment customer assigned ```  but the meaning is not present in the expression itself.  A more agent-friendly model exposes the conclusion:  ```csharp price.IsFree subscription.IsActive retryPolicy.IsUnlimited payment.Status == PaymentStatus.Unpaid order.HasAssignedCustomer ```  This suggests a broader rule:  &gt; Prefer code that encodes business conclusions rather than only technical evidence from which those conclusions must be inferred.  The principle extends beyond source code.  Ideally, the same domain vocabulary should appear consistently in:  ```text domain model API contracts database schema tests documentation events and messages logs and telemetry ```  For example:  ```text Documentation:     unpaid payment  Code:     PaymentStatus.Unpaid  API:     paymentStatus = &quot;unpaid&quot;  Database:     payment_status = &quot;unpaid&quot;  Event:     PaymentBecameUnpaid  Test:     ShouldRetryUnpaidPayment ```  This creates **semantic alignment across artifacts**.  For an agent, that alignment has several benefits:  - repository search becomes more reliable, - embeddings and RAG retrieval are more likely to connect relevant artifacts, - documentation can be mapped to implementation more directly, - fewer hidden conventions must be reconstructed, - code review requires less inference, - generated changes are more likely to use the correct business concept.  Comments can help:  ```csharp // A non-null Payment means the invoice has not been paid yet. if (payment != null) ```  but comments are weaker than encoding the meaning in the model itself.  They can become stale, they may not participate in all tooling, and they still leave the underlying representation semantically indirect.  Documentation or schema descriptions are also useful when the technical representation cannot be changed.  For example, if a legacy database uses:  ```text payment_state = 2 ```  then the schema or mapping layer should make the meaning mechanically discoverable:  ```text 2 = unpaid ```  or preferably expose it to application code as:  ```csharp PaymentStatus.Unpaid ```  This leads to another useful design principle:  &gt; Use the same business vocabulary across code, contracts, schemas, tests, and documentation whenever practical.  For humans, this reduces the amount of institutional knowledge needed to understand the system.  For agents, it reduces the number of semantic translations that must be inferred before a change can be made safely.  In this sense, agent-friendly code should not merely be readable.  It should be **semantically searchable and cross-referenceable**.   ## Semantic Locality May Become an Architectural Goal  We can think about code as having different levels of semantic locality.  High semantic locality:  ```csharp CalculatePrice(order, customer, pricingRules); ```  The important inputs are visible.  Lower semantic locality:  ```csharp priceCalculator.Calculate(order); ```  The implementation must be discovered.  Even lower semantic locality:  ```csharp priceCalculator.Calculate(order); ```  where dependency injection selects the implementation based on runtime context.  Very low semantic locality:  ```csharp priceCalculator.Calculate(order); ```  where the result also depends on:  ```text current tenant feature flags ambient user interceptors global cache transaction context dynamic configuration ```  The textual code can remain equally short while the reasoning cost increases dramatically.  For agent-maintained systems, **semantic locality may become as important as traditional measures such as coupling, cohesion, and duplication**.  ## The Likely Direction Is Not &quot;No Abstractions&quot;  The more realistic direction is:  ```text hide mechanisms expose semantic decisions centralize implementation localize intent make abstractions inspectable ```  This could lead to code that is somewhat more verbose than today&#x27;s most heavily abstracted application architectures.  But the code may also become:  - easier for agents to modify,      - easier for humans to review,      - easier to test,      - easier to analyze statically,      - less dependent on institutional knowledge,      - safer to refactor automatically.       The important shift may therefore not be from abstraction to no abstraction.  It may be from:  ```text implicit, non-local behavior ```  toward:  ```text explicit, composable, mechanically discoverable behavior ```  In software increasingly written and maintained by agents, the cost of repetition may fall while the cost of hidden semantics becomes much more visible.  That could change what we consider &quot;clean&quot; architecture.</p>
    </td>

    <td style='vertical-align: top; padding: 12px;'>
<strong style='color: var(--text-accent);'>Overview / Introduction</strong><hr style='margin: 4px 0 8px 0;'><p style='margin-bottom: 8px; line-height: 1.45;'>Syntactic brevity often hides massive execution pipelines.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Consider this common MediatR call:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>public Task&lt;Response&gt; GetOrder(GetOrderRequest request) =&gt; mediator.Send(request);</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>The call site hides the true execution flow:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>Auth -&gt; Validation -&gt; Logging -&gt; Transaction -&gt; EF Interceptors -&gt; Handler -&gt; SQL</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Local code stays small. Semantic complexity explodes.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Coding agents struggle with this hidden execution context.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Non-Local Semantics and Ambient State</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Agents cannot infer dependencies outside the local context window.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Consider an HTTP call:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>await httpClient.SendAsync(request);</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Global handlers inject headers, auth, telemetry, and retries silently.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Entity Framework query filters also inject hidden SQL clauses:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>context.Orders.ToListAsync();
// Injects: WHERE TenantId = @currentTenant AND IsDeleted = 0</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Do not hide business dependencies in ambient state.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Avoid `AsyncLocal`, `HttpContext.Items`, or implicit thread-local state.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Pass required context explicitly.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Dynamic DI Breaks Static Analysis</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Dynamic DI and runtime factories break static analysis tools.</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>services.AddScoped&lt;IPriceCalculator&gt;(sp =&gt; {
    var context = sp.GetRequiredService&lt;OperationContext&gt;();
    return context.Channel switch
    {
        Channel.Web =&gt; new WebPriceCalculator(),
        Channel.Api =&gt; new ApiPriceCalculator(),
        _ =&gt; new DefaultPriceCalculator()
    };
});</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>The call site obscures the concrete implementation:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>priceCalculator.Calculate(order);</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Keyed services, decorators, and assembly scanning destroy call-site discoverability.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Agents fail to identify the active execution path.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Interceptors also hide critical business semantics:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>repository.Save(order); // Silently runs auth, validation, and audit logging</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Keep business-critical operations visible at the call site.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>The Shift in DRY Economics</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Traditional DRY minimizes typing and repeated lines.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Agents generate and maintain repeated code cheaply.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Prioritize semantic locality over extreme deduplication.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Allow repeated code to keep pipelines explicit.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Explicit Execution Pipelines</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Expose the execution pipeline directly in the handler:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>return Operation
    .From(request)
    .Validate&lt;GetOrderValidator&gt;()
    .Authorize&lt;ReadOrderPolicy&gt;()
    .Retry(ExternalPolicies.Read)
    .Execute&lt;GetOrderHandler&gt;()
    .ValidateResponse&lt;GetOrderResponseValidator&gt;()
    .MapErrors&lt;OrderHttpErrors&gt;()
    .Return();</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>This code exposes the full execution graph.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Agents parse this pipeline without inspecting external framework configurations.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Mechanics vs. Business Semantics</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Let frameworks hide low-level mechanics.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Keep domain semantics explicit.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Safe to hide (Mechanics):</p>
<li style='margin-left: 18px;'>JSON parsing, serializing, TCP handling</li>
<li style='margin-left: 18px;'>Low-level telemetry, correlation IDs, compression</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>Keep explicit (Semantics):</p>
<li style='margin-left: 18px;'>Authorization and tenant filtering</li>
<li style='margin-left: 18px;'>Business validation and retry policies</li>
<li style='margin-left: 18px;'>Transaction bounds and idempotency keys</li>
<li style='margin-left: 18px;'>Cache invalidation and feature flags</li>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Named Semantics Over Silent Policies</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Do not hide retries inside `HttpClient`.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Expose the retry policy at the call site:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>await request
    .Retry(RetryPolicies.ExternalRead)
    .Execute();</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>The call site declares *what* policy applies.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Central configuration defines *how* the policy executes.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Agents immediately recognize that the call may run multiple times.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>They then handle idempotency and side effects correctly.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Ubiquitous Vocabulary</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Encode domain conclusions directly into code.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Avoid technical sentinels.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Bad:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>if (payment != null) // Implicitly means unpaid
if (amount == 0)     // Implicitly means free
if (status == 2)     // Implicitly means active</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Good:</p>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>if (payment.IsUnpaid)
if (price.IsFree)
if (subscription.IsActive)</code></pre>
<p style='margin-bottom: 8px; line-height: 1.45;'>Align naming across schemas, API contracts, tests, and code:</p>
<li style='margin-left: 18px;'>Spec: `paymentStatus: &quot;unpaid&quot;`</li>
<li style='margin-left: 18px;'>DB: `payment_status = &quot;unpaid&quot;`</li>
<li style='margin-left: 18px;'>Code: `PaymentStatus.Unpaid`</li>
<li style='margin-left: 18px;'>Test: `ShouldRetryUnpaidPayment()`</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>Consistent terminology improves agent retrieval and code reasoning.</p>
<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>Semantic Locality Spectrum</h4>
<p style='margin-bottom: 8px; line-height: 1.45;'>Measure code quality by semantic locality:</p>
<li style='margin-left: 18px;'>**High Locality:**</li>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>CalculatePrice(order, customer, pricingRules);</code></pre>
<li style='margin-left: 18px;'>**Medium Locality:**</li>
<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>priceCalculator.Calculate(order);</code></pre>
<li style='margin-left: 18px;'>**Low Locality:** Ambient DI resolves implementations via runtime tenant and flags.</li>
<p style='margin-bottom: 8px; line-height: 1.45;'>Syntactic brevity no longer equals architectural simplicity.</p>
<p style='margin-bottom: 8px; line-height: 1.45;'>Prioritize explicit, composable, and mechanically discoverable pipelines.</p>
    </td>

  </tr>

</table>

