#!/usr/bin/env python3
"""
_Restoration/restore_notes.py

Automated Note Restoration using Gemini 3.8 Flash (High Thinking).
Deconstructs bloated, academic notes into lean, dense engineering notes.
Processes each note in an isolated context to prevent context drift.
"""

import os
import sys
import re
import argparse
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
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package not found. Run: pip install google-genai", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
RESTORATION_DIR = REPO_ROOT / "_Restoration"
PROMPT_FILE = RESTORATION_DIR / "3_gemini_rewrite_prompt.md"
RECIPE_FILE = RESTORATION_DIR / "2_restoration_recipe_positive_and_negative_rules.md"
DEFAULT_OUTPUT_DIR = RESTORATION_DIR / "restored_output"


def load_api_key(cli_key: str = None) -> str:
    """Retrieve Gemini API key from CLI argument or environment variables."""
    key = cli_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        # Check .env file if present
        env_file = REPO_ROOT / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("GEMINI_API_KEY=") or line.startswith("GOOGLE_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    return key


def split_frontmatter(content: str):
    """Separate YAML frontmatter from document body."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = f"---{parts[1]}---\n\n"
            body = parts[2].strip()
            return frontmatter, body
    return "", content.strip()


def build_system_instruction() -> str:
    """Build the master system instruction combining hard syntax rules and few-shots."""
    return """You are a Senior Systems Architect and Technical Lead.
Your task is to rewrite the provided technical note.
The input text has been corrupted by academic fluff, sensationalist drama, and bloated sentences.
You must restore it into a dense, pragmatic engineering note written for an experienced software engineer.

HARD SYNTAX RULES (ZERO COMPROMISE):
1. Active voice only: Use active voice or imperative verbs (check, verify, run, write). Never use passive voice.
2. Max 12–15 words per sentence: If a sentence has multiple clauses or two commas, split it into two or three short sentences.
3. Zero nominalizations: Never write "performing the execution of validation". Write "validating" or "running checks".
4. Zero introductory throat-clearing: Remove all intros and conclusions ("It is worth noting that...", "In conclusion...", "The fundamental question is..."). Start immediately with the core technical thesis.
5. Respect developer shorthand: Do not explain basic computer science concepts. Write as if taking notes for yourself for tomorrow morning.
6. Preserve concrete code snippets: Keep and highlight real code snippets. Code proves the technical point.
7. Remove shouting ASCII boxes: Delete all ASCII art banners labeled "TOXIC MAGIC", "NAIVE ACCEPTANCE", "CATASTROPHIC FAILURE", or "PARADIGM SHIFT". Replace with simple code or clear text diagrams.
8. Length budget (Token constraint): Compress bloated prose by 50-60%. Strip adjectives, rhetorical questions, and philosophical framing. Leave only causal technical facts and mechanisms.

FEW-SHOT EXAMPLES:

Example 1 (Abstract Jargon vs Direct Fact):
INPUT: "In software systems maintained by AI agents, the implementation of semantic locality constitutes a fundamental prerequisite for the avoidance of catastrophic failure modes induced by ambient magic."
OUTPUT: "Coding agents struggle with ambient state. Keep parameters explicit at the call site. Explicit calls prevent regressions."

Example 2 (Manufactured Drama vs Pragmatic Engineering):
INPUT: "The dangerous part is that the proposal will sound completely plausible, luring developers into the catastrophic trap of naive acceptance."
OUTPUT: "Models generate plausible architectures. However, they silently assume unstated requirements. Always audit the model's assumptions before picking technologies."

Example 3 (Verbose Moralizing vs Technical Mechanism):
INPUT: "TRADITIONAL VIEW: Descriptive comments = ZERO VALUE. AGENTIC REALITY: Comments are the ONLY documentation guaranteed to be inside the agent's context window."
OUTPUT: "Do not write comments explaining syntax. The model reads syntax easily. Write comments explaining business rules and non-obvious constraints. That context stays next to the code."

Output exclusively raw markdown without surrounding conversational banter or outer code blocks."""


def restore_note_content(client: genai.Client, raw_content: str, model_name: str = "gemini-3.8-flash") -> str:
    """Restore a single note using an isolated Gemini call with high thinking."""
    frontmatter, body = split_frontmatter(raw_content)

    user_prompt = f"Rewrite and deconstruct the following note into a dense, pragmatic engineering note:\n\n{body}"

    config = types.GenerateContentConfig(
        system_instruction=build_system_instruction(),
        thinking_config=types.ThinkingConfig(thinking_level="high"),
        temperature=0.2,
    )

    response = client.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=config,
    )

    restored_body = response.text.strip()
    # Strip wrapping markdown code blocks if the model wrapped its output
    if restored_body.startswith("```markdown"):
        restored_body = restored_body[len("```markdown"):].strip()
    elif restored_body.startswith("```"):
        restored_body = restored_body[len("```"):].strip()
    if restored_body.endswith("```"):
        restored_body = restored_body[:-3].strip()

    return frontmatter + restored_body + "\n"


def process_file(client: genai.Client, input_path: Path, output_dir: Path, in_place: bool = False, model_name: str = "gemini-3.8-flash"):
    """Process a single markdown file."""
    print(f"\n>> Processing: {input_path.name}")
    raw_content = input_path.read_text(encoding="utf-8", errors="ignore")
    orig_words = len(raw_content.split())

    try:
        restored_content = restore_note_content(client, raw_content, model_name=model_name)
    except Exception as e:
        print(f"  [ERROR] Gemini call failed for {input_path.name}: {e}", file=sys.stderr)
        return False

    new_words = len(restored_content.split())
    compression = ((orig_words - new_words) / orig_words) * 100 if orig_words > 0 else 0

    if in_place:
        target_path = input_path
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        target_path = output_dir / input_path.name

    target_path.write_text(restored_content, encoding="utf-8")
    print(f"  [SUCCESS] Saved to {target_path}")
    print(f"  Stats: {orig_words} words -> {new_words} words ({compression:.1f}% compression)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Restore notes using Gemini 3.8 Flash (High Thinking)")
    parser.add_argument("--file", "-f", type=str, help="Path to single markdown file to restore")
    parser.add_argument("--dir", "-d", type=str, help="Path to directory of markdown files to restore")
    parser.add_argument("--output-dir", "-o", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Output directory (default: _Restoration/restored_output)")
    parser.add_argument("--in-place", action="store_true", help="Overwrite input files in-place")
    parser.add_argument("--api-key", "-k", type=str, help="Gemini API key")
    parser.add_argument("--model", "-m", type=str, default="gemini-3.8-flash", help="Gemini model name (default: gemini-3.8-flash)")
    parser.add_argument("--reference-test", action="store_true", help="Run restoration test on all files in _Restoration/original_notes/")

    args = parser.parse_args()

    api_key = load_api_key(args.api_key)
    if not api_key:
        print("\n[ERROR] Gemini API Key not found!", file=sys.stderr)
        print("Please provide it via:", file=sys.stderr)
        print("  1. Environment variable: export GEMINI_API_KEY='your-key' (or $env:GEMINI_API_KEY='your-key')", file=sys.stderr)
        print("  2. CLI argument: python _Restoration/restore_notes.py --api-key 'your-key' ...", file=sys.stderr)
        print("  3. File: Add GEMINI_API_KEY='your-key' in .env at repository root.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    out_dir = Path(args.output_dir)

    targets = []
    if args.reference_test:
        ref_dir = RESTORATION_DIR / "original_notes"
        targets = sorted(list(ref_dir.glob("*.md")))
    elif args.file:
        p = Path(args.file)
        if not p.exists():
            print(f"File not found: {p}", file=sys.stderr)
            sys.exit(1)
        targets = [p]
    elif args.dir:
        d = Path(args.dir)
        if not d.exists():
            print(f"Directory not found: {d}", file=sys.stderr)
            sys.exit(1)
        targets = sorted(list(d.glob("*.md")))
    else:
        print("Specify --file, --dir, or --reference-test. Run with --help for options.")
        sys.exit(1)

    print(f"Starting restoration batch ({len(targets)} note(s)) using {args.model} [thinking_level=HIGH]...")
    success_count = 0
    for t in targets:
        if process_file(client, t, out_dir, in_place=args.in_place, model_name=args.model):
            success_count += 1

    print(f"\nFinished: {success_count}/{len(targets)} notes successfully processed.")


if __name__ == "__main__":
    main()
