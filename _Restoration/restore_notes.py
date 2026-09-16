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
    """Build the master system instruction based directly on practitioner-voice-and-tone.md."""
    return """You are a seasoned Hands-On Lead Architect and Principal Systems Engineer.
Your task is to re-articulate the provided technical note to adhere strictly to the Practitioner Voice and Tone standard.

CRITICAL DIRECTIVE ON LENGTH AND DEPTH:
- DO NOT SHORTEN OR SUMMARIZE. Preserve the full, comprehensive depth, all sections, all arguments, nuanced trade-offs, and edge cases of the note.
- This is NOT an executive summary or a compression pass. The target length must match the original technical depth.
- Preserve and format all code examples, interfaces, schemas, and configurations.

CORE PRINCIPLES (from practitioner-voice-and-tone.md):
1. The Practitioner Persona:
   - Write with the natural authority and pragmatic clarity of a veteran technical lead who actively builds, profiles, debugs, and ships complex production systems.
   - Avoid detached academic neutrality, pseudo-philosophical lecturing, and theatrical framing.
2. The Coffee & Tech Talk Standard:
   - Apply the Core Heuristic to every paragraph: "Would a seasoned tech lead explain this system architecture this way to a teammate over coffee, or during an engaging engineering conference talk?"
   - Keep explanations grounded, relatable, engaging, and direct.
   - Use active voice, natural cadence, and punchy, clear sentences. Avoid mechanical staccato or telegraphic bullet points.
3. Thought Density Through Substance, Not Jargon:
   - Deliver dense intellectual value through accurate mental models, causal depth, and clear explanations of underlying system mechanics (runtimes, memory, database query planners, context windows, network boundaries).
   - Cut inflated, purple buzzwords:
     - Replace "stochastic foundations" with "unpredictable models" or "stochastic behavior".
     - Replace "mechanical exoskeleton" with "runtime harness and test scripts".
     - Replace "deterministic substrate" with "compiler and test suites".
     - Replace "epistemic dialectic" with "validating assumptions".
     - Replace "axioms" with "principles" or "rules".
4. Natural Formatting & Zero Sloganeering:
   - Delete shouting ASCII art banners labeled "TOXIC MAGIC", "NAIVE ACCEPTANCE", "CATASTROPHIC FAILURE", or "PARADIGM SHIFT". Replace with clear diagrams or code.
   - Do NOT force cookie-cutter "Core Invariants" lists. Follow the organic, logical flow of the topic.
   - Eliminate throat-clearing openings ("It is worth noting that...", "The fundamental question is..."). Dive straight into the core engineering reality.

Output exclusively raw markdown with full technical depth and natural practitioner cadence."""


def get_original_baseline(input_path: Path) -> str:
    """Retrieve the original baseline content from commit f909d7a for a given note."""
    mapping_file = RESTORATION_DIR / "vault_to_original_mapping.json"
    f909_path = None

    # 1. Try reading from precomputed mapping JSON
    if mapping_file.exists():
        try:
            import json
            mappings = json.loads(mapping_file.read_text(encoding="utf-8"))
            rel_posix = input_path.relative_to(REPO_ROOT).as_posix() if input_path.is_relative_to(REPO_ROOT) else input_path.name
            for m in mappings:
                if m.get("current_path") == rel_posix or Path(m.get("current_path", "")).name == input_path.name:
                    if m.get("status") == "ORIGINAL_EXISTS":
                        f909_path = m.get("f909_path")
                    break
        except Exception:
            pass

    # 2. Fallback: Check if file exists in _Restoration/original_notes/
    if not f909_path:
        local_orig = RESTORATION_DIR / "original_notes" / input_path.name
        if local_orig.exists():
            return local_orig.read_text(encoding="utf-8", errors="ignore")

    # 3. Fallback: Search f909d7a directly by basename
    if not f909_path:
        import subprocess
        try:
            raw = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "f909d7a"], encoding="utf-8")
            for line in raw.splitlines():
                if Path(line.strip()).name == input_path.name:
                    f909_path = line.strip()
                    break
        except Exception:
            pass

    if f909_path:
        import subprocess
        try:
            return subprocess.check_output(["git", "show", f"f909d7a:{f909_path}"], encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"  [WARN] Failed to fetch git show f909d7a:{f909_path}: {e}", file=sys.stderr)

    return None


def restore_note_content(client: genai.Client, raw_content: str, original_baseline: str = None, model_name: str = "gemini-3.8-flash") -> str:
    """Restore a single note using an isolated Gemini call with high thinking."""
    frontmatter, body = split_frontmatter(raw_content)

    if original_baseline:
        orig_fm, orig_body = split_frontmatter(original_baseline)
        user_prompt = f"""# TASK: Practitioner Tone Restoration & Intelligent Delta Merge

You are provided with two versions of this engineering note:

======================================================================
1. ORIGINAL GROUND-TRUTH BASELINE (Commit f909d7a - ChatGPT)
======================================================================
{orig_body}

======================================================================
2. CURRENT VAULT VERSION (Edited)
======================================================================
{body}

======================================================================
DIRECTIVES FOR THE SYNTHESIZED NOTE
======================================================================
1. THE ORIGINAL BASELINE IS YOUR ANCHOR:
   - Match the calm, grounded, authoritative voice of the original.
   - PRESERVE ALL ORIGINAL CODE SNIPPETS, SCHEMAS, INTERFACES, AND DATA MODELS. Do not summarize or delete any code examples.
2. DELTA MERGE:
   - If the CURRENT VERSION introduces genuine, high-value technical observations, edge cases, trade-offs, or contemporary perspectives not present in the original, integrate them cleanly into the flow.
   - REJECT and DISCARD all purple prose, academic buzzwords, sensationalist hooks, and forced "Core Invariants" templates.
3. OUTPUT:
   - Output exclusively the unified, fully detailed markdown note with rich technical depth."""
    else:
        user_prompt = f"Rewrite this technical note in the Practitioner Voice and Tone. Maintain full depth, all sections, all trade-offs, and all code examples. Do NOT summarize or shorten:\n\n{body}"

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


def process_file(client: genai.Client, input_path: Path, output_dir: Path, in_place: bool = False, model_name: str = "gemini-3.8-flash", with_original: bool = False):
    """Process a single markdown file."""
    print(f"\n>> Processing: {input_path.name}")
    raw_content = input_path.read_text(encoding="utf-8", errors="ignore")
    orig_words = len(raw_content.split())

    orig_baseline = None
    if with_original:
        orig_baseline = get_original_baseline(input_path)
        if orig_baseline:
            print(f"  [ANCHOR] Found original baseline from f909d7a ({len(orig_baseline.split())} words)")
        else:
            print("  [ANCHOR] No baseline found in f909d7a (treating as new note)")

    try:
        restored_content = restore_note_content(client, raw_content, original_baseline=orig_baseline, model_name=model_name)
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
    parser.add_argument("--with-original", action="store_true", help="Merge with historical ChatGPT baseline from f909d7a as ground-truth anchor")

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

    print(f"Starting restoration batch ({len(targets)} note(s)) using {args.model} [thinking_level=HIGH, with_original={args.with_original}]...")
    success_count = 0
    for t in targets:
        if process_file(client, t, out_dir, in_place=args.in_place, model_name=args.model, with_original=args.with_original):
            success_count += 1

    print(f"\nFinished: {success_count}/{len(targets)} notes successfully processed.")


if __name__ == "__main__":
    main()
