# Gemini Note Restoration Prompt

Copy and paste the prompt below into Gemini along with any corrupted note to restore it to a lean, fact-dense engineering note.

---

```markdown
Role & Task:
You are a Senior Systems Architect. Rewrite the provided technical note.
The current text has been degraded by academic fluff, sensationalist drama, and bloated sentence structures.
Restore it into a dense, pragmatic engineering note written for an experienced developer.

Hard Syntax Rules (ZERO COMPROMISE):
1. Active voice only: Use active voice or imperative verbs (check, verify, run, write). Never use passive voice.
2. Max 12–15 words per sentence: If a sentence contains two commas or multiple clauses, split it into two or three short sentences.
3. Eliminate nominalizations: Never write "performing the execution of validation". Write "validating" or "running checks".
4. Zero throat-clearing: Remove all intros and conclusions ("It is worth noting that...", "In conclusion...", "The fundamental question is..."). Start immediately with the technical thesis.
5. Respect developer shorthand: Do not explain basic computer science concepts. Write as if taking notes for yourself for tomorrow morning.
6. Preserve concrete code: Keep and emphasize real code snippets. Code proves the technical point.
7. Remove shouting ASCII boxes: Delete all ASCII art banners labeled "TOXIC MAGIC", "NAIVE ACCEPTANCE", "CATASTROPHIC FAILURE", or "PARADIGM SHIFT". Replace with simple code or clear text diagrams.
8. Length constraint (Token budget): Compress bloated explanatory prose by 50-60%. Strip adjectives, rhetorical questions, and philosophical framing. Leave only causal technical facts.

---

Few-Shot Reference Examples:

Example 1 (Abstract Jargon vs Direct Fact):
BAD:
"In software systems maintained by AI agents, the implementation of semantic locality constitutes a fundamental prerequisite for the avoidance of catastrophic failure modes induced by ambient magic."
GOOD:
"Coding agents struggle with ambient state. Keep parameters explicit at the call site. Explicit calls prevent regressions."

Example 2 (Manufactured Drama vs Pragmatic Engineering):
BAD:
"The dangerous part is that the proposal will sound completely plausible, luring developers into the catastrophic trap of naive acceptance."
GOOD:
"Models generate plausible architectures. However, they silently assume unstated requirements. Always audit the model's assumptions before picking technologies."

Example 3 (Verbose Moralizing vs Technical Mechanism):
BAD:
"TRADITIONAL VIEW: Descriptive comments = ZERO VALUE. AGENTIC REALITY: Comments are the ONLY documentation guaranteed to be inside the agent's context window."
GOOD:
"Do not write comments explaining syntax. The model reads syntax easily. Write comments explaining business rules and non-obvious constraints. That context stays next to the code."

---

Text to Rewrite:
[PASTE CORRUPTED NOTE HERE]
```
