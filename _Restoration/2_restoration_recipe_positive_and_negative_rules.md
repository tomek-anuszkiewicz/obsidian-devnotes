# Note Restoration Recipe: Positive and Negative Rules for Gemini

Use this guide when rewriting inflated or degraded notes into dense, pragmatic engineering notes.

---

## Part 1: Positive Rules (What TO DO)

1. **Start Directly with the Core Technical Proposition**:
   - The very first sentence must state what the note is about or how the system works.
   - Example: *"When coding agents maintain a repository, implicit global state causes subtle regressions. Keep critical parameters explicit at the call site."*

2. **Sentence Length: Max 12–15 Words per Sentence**:
   - Cut complex sentences at conjunctions.
   - If a sentence has multiple clauses or two commas, split it into two or three sentences.
   - Short sentences force clear thinking and eliminate waffle.

3. **Active Voice and Direct Verbs**:
   - Use active voice exclusively.
   - Prefer imperative or direct technical statements: *"Pass parameters explicitly"*, *"Run tests before committing"*, *"The compiler catches type mismatches"*.

4. **Restore Concrete Code Snippets**:
   - If a concept can be proven with 5 lines of code, include the code.
   - Show the difference between the ambiguous pattern and the explicit pattern (e.g. `payment != null` vs `payment.Status == PaymentStatus.Unpaid`).
   - Code anchors the explanation in physical engineering reality.

5. **Deconstruct to Core Technical Facts**:
   - Extract the technical mechanism: *What is the input? What fails? What tool detects it? What is the fix?*
   - Discard all rhetorical framing and meta-commentary about "the future of software engineering".

6. **Preserve Nuance and Trade-Offs**:
   - State when an approach works and when it does not.
   - Avoid black-and-white absolutism.

---

## Part 2: Negative Rules (What NOT TO DO)

1. **NO Shouting ASCII Art or Propaganda Banners**:
   - BANNED: Boxes labeled `TOXIC AMBIENT MAGIC`, `NAIVE ACCEPTANCE`, or `CATASTROPHIC FAILURE`.
   - BANNED: Metaphors like *"The call site is an iceberg: 10% visible, 90% underwater"*.
   - ALLOWED: Simple text or mermaid diagrams showing actual components and data flow.

2. **NO Cookie-Cutter "Core Invariants" Sections**:
   - Do not force a list titled "Core Invariants" into notes where it does not belong.
   - Use headings that describe the actual technical topic (e.g. `## Handling Transient Failures`, `## Domain Vocabulary Alignment`).

3. **NO Sensationalist Openings (Movie-Trailer Hooks)**:
   - BANNED: *"The Big Question hits every software architect..."*
   - BANNED: *"The dangerous part is that the proposal will sound completely plausible."*
   - BANNED: *"In the era of autonomous agents, everything changes..."*
   - BANNED: *"It is worth noting that..."* or *"A key takeaway is..."*

4. **NO Academic or Philosophical Jargon**:
   - Replace *"stochastic foundations"* $\to$ *"unpredictable models"*
   - Replace *"mechanical exoskeleton"* $\to$ *"runtime harness and test scripts"*
   - Replace *"deterministic substrate"* $\to$ *"compiler and test suite"*
   - Replace *"epistemic dialectic"* $\to$ *"verifying assumptions"*
   - Replace *"collapses the action space"* $\to$ *"constrains methods"*
   - Replace *"axioms"* $\to$ *"principles"* or *"rules"*

5. **NO Nominalizations**:
   - Do not use noun-heavy corporate phrasing:
     - ❌ *"The realization of the implementation of the mechanism..."*
     - ✅ *"Implement the mechanism..."* or *"Write the code..."*

6. **NO Artificial Truncation of Technical Depth**:
   - Do not cut out valuable domain explanations or code examples just to make a note short.
   - Compress the prose, not the technical content.
