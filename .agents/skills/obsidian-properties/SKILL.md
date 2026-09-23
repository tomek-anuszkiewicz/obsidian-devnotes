---
name: obsidian-properties
description: Add or refresh standard Obsidian YAML frontmatter properties (title, tags, aliases) at the top of vault notes. Use when creating notes, reviewing note metadata, or aligning taxonomy and search aliases.
---

# Obsidian Properties

Maintain standard Obsidian YAML frontmatter (`properties`) at line 1 of every markdown note in this vault.

Frontmatter serves three core operational functions in this vault:
1. **Title**: Canonical reference name for readers and tools.
2. **Tags**: Domain taxonomy for discovery, filtering, and Dataview or search queries.
3. **Aliases**: Alternative titles, sub-concepts, and semantic entry points that enable quick switcher navigation and automatic `[[wikilink]]` completions.

## Canonical Property Schema

Every vault note must start strictly on line 1 with a YAML block (`---`):

```yaml
---
title: Note Title in Title Case
tags:
  - primary-topic
  - secondary-topic
  - architectural-pattern
aliases:
  - Full Alternative Title
  - Concept Name
  - Semantic Search Alias
---
```

### Property Rules

- **`title`**:
  - Concise, descriptive string in Title Case.
  - Matches the note's primary topic or H1 heading.
  - Avoid duplicate titles across distinct notes.
  - If the title contains special characters such as colons (`:`) or question marks (`?`), wrap the entire title in double quotes (`"..."`).

- **`tags`**:
  - List of lowercase kebab-case strings (e.g., `software-architecture`, `ai-agents`, `reverse-engineering`).
  - Use between 3 and 8 tags reflecting the engineering domain, architectural layer, operational concerns, and methodologies.
  - Prefer existing vault taxonomy tags to avoid fragmenting tag queries (e.g., reuse tags like `software-architecture`, `ai-agents`, `modularity`, `code-generation`, `developer-experience`, `safety`).
  - Do not use `#` prefixes in YAML lists.

- **`aliases`**:
  - List of non-empty strings.
  - Include 3 to 8 high-value alternative representations:
    - Expanded or abbreviated variants of the title.
    - Key architectural mechanisms or core ideas introduced in the note (e.g., `Documentation as Semantic Cache`, `Architectural Drift Detection`).
    - Phrasings that engineers or agents might type when creating a wikilink or querying the topic.
  - Keep aliases distinct and informative.

## When to Add vs. When to Refresh

### 1. Adding Properties (New or Missing Frontmatter)
- Inspect the file content, headings, and concrete engineering arguments.
- Determine the canonical `title`.
- Extract 3–8 kebab-case `tags` capturing the technical domain and mechanisms.
- Formulate 3–8 `aliases` capturing alternative titles and core conceptual sub-topics.
- Insert the frontmatter block at line 1, ensuring no comments, blank lines, or headings precede the opening `---`.

### 2. Refreshing Properties (Existing Notes)
- Check whether the note's scope, architecture, or terminology evolved.
- **Preserve intentional tags and aliases** that remain accurate; do not discard existing links or aliases arbitrarily.
- **Prune dead concepts**: Remove tags or aliases that refer to removed sections or obsolete terminology.
- **Add newly introduced mechanisms**: If a note expanded to discuss new patterns, add corresponding tags and aliases.
- **Fix misplaced frontmatter**: If comments or markdown headers were placed above the opening `---`, move the YAML block back to line 1.

## Verification

After adding or updating properties, run the frontmatter validator from repository root:

```bash
# Verify specific note
python scripts/check_frontmatter.py "path/to/note.md"

# Verify all git staged notes before committing
python scripts/check_frontmatter.py --git

# Audit entire vault
python scripts/check_frontmatter.py --vault
```

Also verify that no non-English words were introduced:

```bash
python scripts/check_polish.py "path/to/note.md"
```
