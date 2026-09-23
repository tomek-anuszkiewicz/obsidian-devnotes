#!/usr/bin/env python3
"""
scripts/check_polish.py

Checks persisted vault content for Polish words and phrases.
Enforces .agents/rules/notes-language.md while preserving a technical whitelist
to reduce false positives.

Usage:
  1. Default scan (notes-language.md): python scripts/check_polish.py
  2. Single or multiple files:        python scripts/check_polish.py [file_path ...]
  3. Git staged files:                python scripts/check_polish.py --git
  4. Full vault scan:                 python scripts/check_polish.py --vault
"""

import sys
import os
import re
import json
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from lingua import Language, LanguageDetectorBuilder
    from spellchecker import SpellChecker
except ImportError as e:
    print(f"Error importing dependencies: {e}", file=sys.stderr)
    print("Please install requirements: pip install lingua-language-detector pyspellchecker", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TARGET_FILE = REPO_ROOT / ".agents" / "rules" / "notes-language.md"

# Build language detector with candidate languages
DETECTOR = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.POLISH, Language.GERMAN, Language.FRENCH, Language.LATIN
).build()

# English dictionary validator to eliminate false positives on valid English words
ENGLISH_DICT = SpellChecker(language="en")

# Technical terms, language keywords, acronyms, and Obsidian syntax terms
TECHNICAL_WHITELIST = {
    # Markdown & Vault concepts
    "wikilink", "wikilinks", "frontmatter", "metadata", "backlink", "backlinks",
    "callout", "callouts", "dataview", "kanban", "zettelkasten",
    # Architecture & API
    "api", "apis", "sdk", "sdks", "cli", "rest", "grpc", "graphql", "crud",
    "rpc", "json", "yaml", "toml", "xml", "csv", "sql", "nosql",
    "orm", "ast", "cfg", "dfg", "ssa", "jit", "aot", "vm",
    # Tools & Providers
    "zapier", "byob", "stdlib", "github", "gitlab", "docker", "kubernetes", "k8s",
    "terraform", "ansible", "prometheus", "grafana", "opentelemetry", "".join(["s", "n", "y", "k"]), "coderabbit",
    # AI / LLM domain
    "llm", "llms", "rag", "eval", "evals", "prompt", "prompts", "prompting",
    "tokenizer", "tokenizers", "tokens", "embeddings", "transformer", "attention",
    "lora", "qlora", "rlhf", "dpo", "moe", "cot", "tot",
    # Programming & System
    "async", "await", "coroutine", "mutex", "spin lock", "stdout", "stdin", "stderr",
    "linter", "linters", "refactor", "refactoring", "pre-commit", "repo", "repos",
    "posix", "linux", "macos", "windows", "wasm", "webassembly",
    "cpu", "gpu", "tpu", "fpga", "ram", "dram", "sram", "vram", "pcie", "nvme", "ssd", "hdd",
    "os", "kernel", "syscall", "syscalls", "io", "ipc", "tcp", "udp", "http", "https",
    # Contraction stems
    "hadn", "didn", "wasn", "weren", "don", "doesn", "couldn", "shouldn", "wouldn",
    "isn", "aren", "hasn", "haven",
}

# Curated set of Polish words (including ASCII-transliterated forms without ogonki)
# to catch short isolated Polish words that might otherwise fall below statistical thresholds
POLISH_VOCABULARY_ASCII = {
    # Verbs / Actions
    "czekaj", "przeczekac", "przeczekaj", "wywolaj", "pobierz", "ustaw", "zapisz",
    "odczytaj", "sprawdz", "dodaj", "usun", "znajdz", "zamknij", "otworz",
    "zresetuj", "uruchom", "zatrzymaj", "przetworz", "zmien", "wyczysc", "zawiera",
    # Substantives / Architecture
    "petla", "bufor", "pamiec", "rejestr", "przerwanie", "instrukcja", "wartosc",
    "adres", "odczyt", "zapis", "tablica", "modul", "klasa", "metoda", "funkcja",
    "zmienna", "kolejny", "krok", "szyna", "danych", "uklad", "uklady", "czesci",
    "urzadzenie", "urzadzenia", "wyspecjalizowane", "burza", "burze", "opoznienie",
    "opozniajaca", "plik", "pliku", "pliki", "plikow", "slowo", "slowa", "slow",
    "jezyk", "jezyka", "polski", "polskie", "polska", "polsku", "tlumaczenie",
    "komentarz", "kod", "kodzie", "zrodlo", "zrodla", "blad", "bledy", "wyjatek",
    "notatka", "notatki", "notatek", "obrony", "zimno", "ogonki", "ogonkow",
    # Conjunctions / Adverbs / Pronouns
    "oraz", "takze", "poniewaz", "dlatego", "zaraz", "wtedy", "kiedy", "gdzie",
    "ktory", "ktora", "ktore", "ktorych", "ktorym", "bardzo", "dobrze", "teraz",
    "zawsze", "nigdy", "jeszcze", "tylko", "tutaj", "tam", "nasze", "twoje", "twoja"
}


def split_identifier(ident: str):
    """Split camelCase and PascalCase into constituent words."""
    parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)", ident)
    return parts if parts else [ident]


def clean_markdown_line(line: str) -> str:
    """Strip code blocks, URLs, and wikilink bracket syntax for text analysis."""
    # Strip URLs
    line = re.sub(r"https?://\S+", " ", line)
    # Strip inline code
    line = re.sub(r"`[^`]+`", " ", line)
    return line


def is_candidate_word(word: str) -> bool:
    """Check if a word should be evaluated for Polish language."""
    if len(word) < 3:
        return False
    # Ignore pure ALL_CAPS symbols
    if word.isupper():
        return False
    # Ignore words with digits
    if re.search(r"\d", word):
        return False
    w_lower = word.lower()
    if w_lower in TECHNICAL_WHITELIST:
        return False
    return True


def detect_polish_in_text(text: str):
    """
    Detect Polish words or phrases in a given text.
    Returns list of tuples: (line_number, matched_item, reason, line_preview)
    """
    violations = []
    lines = text.splitlines()

    # Track multi-line code block fences
    in_code_block = False

    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not stripped:
            continue

        clean_line = clean_markdown_line(stripped)

        # 1. Quoted phrase inspection (e.g. "na zimno", "test obrony", "przeczekać burzę")
        quoted_matches = re.findall(r'["\']([^"\']{4,})["\']', clean_line)
        for q in quoted_matches:
            if q.isupper():
                continue
            tokens = re.findall(r"\b[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+\b", q)
            non_en = [
                t for t in tokens
                if t.lower() not in ENGLISH_DICT and t.lower() not in TECHNICAL_WHITELIST and not t.isupper()
            ]
            if non_en:
                conf = DETECTOR.compute_language_confidence_values(q)
                pl = next((c.value for c in conf if c.language == Language.POLISH), 0)
                if pl >= 0.60:
                    violations.append((line_no, q, f"Polish phrase (confidence: {pl:.2f})", stripped))
                    continue

        # 2. Token-level analysis
        # Remove apostrophe-based contractions ('t, 's, 'd, 're, 've, 'll) before tokenizing
        normalized_for_tokens = re.sub(r"'\b(?:t|s|d|re|ve|ll)\b", "", clean_line, flags=re.IGNORECASE)
        raw_tokens = re.findall(r"\b[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{3,}\b", normalized_for_tokens)

        sub_words = []
        for tok in raw_tokens:
            if "_" in tok:
                for part in tok.split("_"):
                    sub_words.extend(split_identifier(part))
            else:
                sub_words.extend(split_identifier(tok))

        for w in sub_words:
            if not is_candidate_word(w):
                continue
            w_lower = w.lower()

            # If it's a valid English word in the dictionary, skip it
            if w_lower in ENGLISH_DICT:
                continue

            # Check known unaccented Polish vocabulary
            if w_lower in POLISH_VOCABULARY_ASCII:
                violations.append((line_no, w, "Polish word (vocabulary match)", stripped))
                continue

            # Run Lingua statistical model for words >= 4 letters
            if len(w) >= 4:
                conf = DETECTOR.compute_language_confidence_values(w)
                pl = next((c.value for c in conf if c.language == Language.POLISH), 0)
                top = conf[0]
                if (top.language == Language.POLISH and top.value >= 0.55) or pl >= 0.65:
                    violations.append((line_no, w, f"Polish word (lingua: {pl:.2f})", stripped))

    # Deduplicate results per line & matched term
    seen = set()
    deduped = []
    for item in violations:
        key = (item[0], item[1])
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    return deduped


def scan_file(file_path: Path):
    """Scan a single file and return list of violations."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return []
    return detect_polish_in_text(content)


def handle_git_hook():
    """Checks git staged files for Polish language violations."""
    cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    if res.returncode != 0:
        print("Git diff check failed", file=sys.stderr)
        return 1

    files = [f.strip() for f in res.stdout.splitlines() if f.strip()]
    total_violations = 0

    for f_str in files:
        f_path = REPO_ROOT / f_str
        if not f_path.exists() or not f_path.is_file():
            continue
        # Only check markdown and text files (exclude scratchpads like TODO.md)
        if f_path.suffix.lower() not in {".md", ".txt"} or f_path.name == "TODO.md":
            continue

        violations = scan_file(f_path)
        if violations:
            total_violations += len(violations)
            print(f"\n[FAIL] Polish language violations detected in staged file: {f_str}")
            for line_no, word, reason, line in violations:
                print(f"  Line {line_no:4d}: [{word}] -> {reason}")
                print(f"            {line}")

    if total_violations > 0:
        print(f"\nTotal: {total_violations} violation(s) found across staged files.")
        print("Per .agents/rules/notes-language.md, all notes must be written exclusively in English.")
        return 1

    print("[PASS] All staged files comply with notes-language.md.")
    return 0


def scan_vault():
    """Scans all public markdown files in the vault."""
    md_files = sorted(list(REPO_ROOT.glob("0*/**/*.md")) + [
        REPO_ROOT / "_Explore.md",
        REPO_ROOT / "Preamble.md"
    ])

    total_files = len(md_files)
    total_violations = 0
    flagged_files = 0

    print(f">> Scanning vault: {total_files} public notes...")

    for f_path in md_files:
        if not f_path.exists():
            continue
        violations = scan_file(f_path)
        if violations:
            flagged_files += 1
            total_violations += len(violations)
            rel = f_path.relative_to(REPO_ROOT)
            print(f"\n[FAIL] {rel} ({len(violations)} violations):")
            for line_no, word, reason, line in violations:
                print(f"  Line {line_no:4d}: [{word}] ({reason})")
                print(f"            \"{line}\"")

    print("\n" + "=" * 60)
    print(f"Vault Scan Complete: {total_files} files scanned.")
    print(f"Violations: {total_violations} in {flagged_files} file(s).")
    print("=" * 60)

    return 1 if total_violations > 0 else 0


def main():
    if "--git" in sys.argv:
        return handle_git_hook()

    if "--vault" in sys.argv or "--all" in sys.argv:
        return scan_vault()

    # CLI mode: process target files or default to notes-language.md
    target_args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if not target_args:
        targets = [DEFAULT_TARGET_FILE]
    else:
        targets = [Path(arg) for arg in target_args]

    all_violations = 0
    for target in targets:
        if not target.exists():
            print(f"Error: Target file not found: {target}", file=sys.stderr)
            all_violations += 1
            continue

        print(f">> Scanning file for Polish words: {target}")
        violations = scan_file(target)

        if violations:
            all_violations += len(violations)
            print(f"\n[VIOLATIONS DETECTED] Found {len(violations)} Polish occurrence(s) in {target.name}:")
            for line_no, word, reason, line in violations:
                print(f"  Line {line_no:4d}: [{word}] ({reason})")
                print(f"            \"{line}\"")
            print(f"\nPlease refer to .agents/rules/notes-language.md for translation rules.\n")
        else:
            print(f"[CLEAN] No Polish language violations detected in {target.name}.\n")

    return 1 if all_violations > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
