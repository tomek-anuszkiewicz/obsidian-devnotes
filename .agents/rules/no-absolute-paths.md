---
trigger: always_on
description: Forbid machine-specific absolute file paths and file URIs; require relative paths or Obsidian wikilinks across vault notes, links, and scripts.
---

# No Absolute Paths

Keep vault notes, links, embeds, and documentation strictly portable across different machines, operating systems, and git checkouts.

## Core Rules

- **No host-specific absolute paths**: Never write machine-specific drive paths (e.g. `C:\...`, `D:\...`), Unix user home paths (e.g. `/home/...`, `/Users/...`), or `file://` protocol URIs in vault notes, frontmatter, markdown links, image embeds, or code comments.
- **Use Obsidian wikilinks for notes**: Reference other vault notes using standard wikilinks: `[[Note Title]]` or piped wikilinks: `[[Note Title|Custom Label]]`. Obsidian resolves note titles globally across directories without folder prefixes.
- **Use relative paths for repository assets**: When referencing non-note assets, scripts, or media files, use relative paths from the current file or repository root (e.g., `scripts/check_paths.py`, `../attachments/diagram.png`).
- **Never embed local file URLs**: Never use `file:///...` links in markdown or documentation.
- **Illustrative examples**: In notes discussing path handling or guardrail tests (e.g., architecture tests catching hardcoded host paths), use generic placeholders such as `username` or `runner`, or fence them within code blocks.

## Rationale

Absolute paths break whenever a repository is opened on another machine, cloned under a different path, reviewed on GitHub, or synced across devices. They also leak developer usernames and private directory structures into public or shared engineering notes.
