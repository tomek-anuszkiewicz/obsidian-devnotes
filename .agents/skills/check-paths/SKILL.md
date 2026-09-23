---
name: check-paths
description: Detect and automatically repair machine-specific absolute file paths and file URIs in vault markdown notes, ensuring all links use Obsidian wikilinks or portable relative paths.
---

# Check and Repair File Paths

Detect and eliminate machine-specific absolute paths, Windows drive letters, Unix user directories, and `file://` protocol URIs in vault notes to comply with [no-absolute-paths.md](../rules/no-absolute-paths.md).

Verification and automated repair are powered by [scripts/check_paths.py](../../scripts/check_paths.py).

## When to Run

- **After authoring or editing notes**: Run on modified files to verify no absolute paths or local file URIs leaked into prose or links.
- **Before git commits**: Run on staged files to ensure clean commits.
- **During vault audits**: Run a full vault scan to catch lingering absolute links or paths.

## Commands

Run commands from the repository root:

### 1. Check Specific File(s)
To verify one or more modified files:
```bash
python scripts/check_paths.py "path/to/note.md"
python scripts/check_paths.py "note1.md" "note2.md"
```

### 2. Check Git Staged Files
Before creating a commit, check all staged files:
```bash
python scripts/check_paths.py --git
```

### 3. Scan Entire Vault
To audit all markdown notes in the vault:
```bash
python scripts/check_paths.py --vault
```

### 4. Automatically Repair Violations
To automatically convert detected absolute paths to Obsidian wikilinks or relative paths:
```bash
# Auto-fix specific files
python scripts/check_paths.py "path/to/note.md" --fix

# Auto-fix entire vault
python scripts/check_paths.py --vault --fix
```

### 5. Preview Repairs (Dry-Run)
To inspect proposed replacements without modifying files on disk:
```bash
python scripts/check_paths.py --vault --fix --dry-run
```

## How Auto-Repair Works

When `--fix` is passed, the tool resolves paths against the vault repository:

```text
Markdown Note Links:
  [Label](D:\Path\To\Vault\Folder\Note.md)      ->  [[Note|Label]]
  [Note](file:///C:/Vault/Folder/Note.md)       ->  [[Note]]
  [Section](file:///.../Note.md#heading)        ->  [[Note#heading|Section]]

Obsidian Wikilinks:
  [[D:\...\Note.md|Label]]                      ->  [[Note|Label]]

Vault Asset References & Embeds:
  ![Alt](file:///.../image.png)                 ->  ![[image.png]]
  [Script](file:///.../scripts/tool.py)         ->  [Script](scripts/tool.py)

Prose Mentions of Vault Files:
  D:\Path\To\Vault\scripts\tool.py              ->  scripts/tool.py
```

## Handling Unresolvable Violations

If an absolute path points outside the repository (e.g., an external personal directory not tracked in git):
- The tool flags it with `(manual fix required)`.
- Replace the link with a public web URL, move the referenced resource inside the repository under an appropriate folder, or rewrite the sentence using practitioner-voice without hardcoding personal local machine paths.
