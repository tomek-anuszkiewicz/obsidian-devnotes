---
name: check-polish
description: Verify vault markdown files for unintended Polish words or phrases using scripts/check_polish.py to enforce English-only vault rules. Use when creating or editing notes, auditing content, or preparing git commits.
---

# Check Polish Language

Detect and eliminate unintended Polish words, phrases, or transliterated stems in vault notes to comply with [notes-language.md](../rules/notes-language.md).

Verification is powered by [scripts/check_polish.py](../../scripts/check_polish.py), which combines statistical language detection (Lingua), English dictionary validation (pyspellchecker), a curated list of unaccented Polish words, and a technical whitelist.

## When to Run

- **After authoring or editing notes**: Run on modified files before finishing a task.
- **Before git commits**: Run on staged files to ensure clean commits.
- **During vault audits**: Run a full vault scan to catch lingering non-English content.

## Commands

Run commands from the repository root:

### 1. Check Specific File(s)
To verify one or more modified files:
```bash
python scripts/check_polish.py "path/to/note.md"
python scripts/check_polish.py "note1.md" "note2.md"
```

### 2. Check Git Staged Files
Before creating a commit, check all staged files:
```bash
python scripts/check_polish.py --git
```

### 3. Scan Entire Vault
To audit all public notes in the vault:
```bash
python scripts/check_polish.py --vault
```

## Interpreting Output and Exit Codes

- **Exit code 0 (`[CLEAN]` or `[PASS]`)**: No violations found.
- **Exit code 1 (`[VIOLATIONS DETECTED]` or `[FAIL]`)**: Polish terms detected. Output lists:
  - Line number
  - Flagged term
  - Detection reason (`vocabulary match`, `lingua confidence`, or `quoted phrase`)
  - Line preview
- **Exit code 2**: Missing dependencies. Install with `pip install lingua-language-detector pyspellchecker`.

## Handling Flagged Violations

1. **Genuine Polish words or phrases**:
   - Translate the flagged content into concise English.
   - Follow `practitioner-voice`: explain mechanics directly rather than writing literal or stilted translations.
   - Re-run `python scripts/check_polish.py <file>` to verify the fix.

2. **False Positives (Valid Technical Terms / Acronyms)**:
   - Code blocks (```` ``` ````) and inline code (`` `code` ``) are automatically ignored by the scanner.
   - If an unquoted technical term, library, tool name, or acronym is flagged as Polish, consider adding it to `TECHNICAL_WHITELIST` in `scripts/check_polish.py`.
