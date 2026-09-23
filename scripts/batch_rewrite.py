#!/usr/bin/env python3
"""
scripts/batch_rewrite.py

Executes surgical delta-merge / restore on note pairs:
  [Note] - original.md  (baseline structure, examples, and tone)
  [Note].md              (source of new technical facts, runtime mechanics, metrics)

Using Gemini 3.8 Flash with thinking_level='high'.
The merged output directly overwrites [Note] - original.md.
"""

import os
import sys
import glob
import json
import time
import argparse
import re
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent

# Load environment variables (.env)
load_dotenv(REPO_ROOT / '.env')

def load_prompt_and_style():
    rewrite_prompt_path = REPO_ROOT / 'Rewrite prompt.md'
    style_path = REPO_ROOT / 'Practitioner Writing Style.md'

    if not rewrite_prompt_path.exists():
        raise FileNotFoundError(f"Missing {rewrite_prompt_path}")
    if not style_path.exists():
        raise FileNotFoundError(f"Missing {style_path}")

    rewrite_prompt = rewrite_prompt_path.read_text(encoding='utf-8')
    style_guide = style_path.read_text(encoding='utf-8')

    return rewrite_prompt, style_guide

def clean_model_output(text: str) -> str:
    """Strip outermost markdown code fence if the model wrapped the entire output."""
    stripped = text.strip()
    # Check if wrapped in ```markdown ... ``` or ``` ... ```
    pattern = r'^```(?:markdown)?\s*\n(.*?)\n```$'
    match = re.match(pattern, stripped, re.DOTALL)
    if match:
        return match.group(1).strip() + '\n'
    return stripped + '\n'

def find_pairs():
    """Find all valid pairs of [Note] - original.md and [Note].md."""
    pairs = []
    for orig_str in glob.glob(str(REPO_ROOT / '*/**/* - original.md'), recursive=True):
        orig_p = Path(orig_str)
        cur_p = Path(orig_str.replace(' - original.md', '.md'))
        if cur_p.exists():
            rel_orig = orig_p.relative_to(REPO_ROOT)
            rel_cur = cur_p.relative_to(REPO_ROOT)
            pairs.append((rel_orig, rel_cur))
    return sorted(pairs, key=lambda x: str(x[0]))

def process_pair(client, model_name: str, orig_rel: Path, cur_rel: Path, rewrite_prompt: str, style_guide: str, dry_run: bool = False):
    from google.genai import types

    orig_full = REPO_ROOT / orig_rel
    cur_full = REPO_ROOT / cur_rel

    orig_content = orig_full.read_text(encoding='utf-8')
    cur_content = cur_full.read_text(encoding='utf-8')

    system_instruction = f"""You are a Lead Architect performing a surgical delta-merge / restore of software engineering vault notes.

STRICT INSTRUCTIONS:
{rewrite_prompt}

PRACTITIONER WRITING STYLE & TONE GUIDELINES:
{style_guide}

CRITICAL RULES:
1. All vault notes MUST be in English.
2. The output must be the COMPLETE, READY-TO-PERSIST note that directly overwrites the baseline file.
3. ZERO MICRO-EDITS / NO SENTENCE CHOPPING: Keep existing baseline sentences, bullet points, and paragraphs 100% verbatim. Do not rewrite, paraphrase, or splice new words into existing sentences.
4. ATOMIC CHANGES ONLY: Any added knowledge must be inserted as complete, standalone new paragraphs or subsections. Any removals must be entire paragraphs or complete bullet points that became obsolete.
5. NO ARTIFICIAL ADDITIONS: Do not generate artificial comparison tables, PR review checklists, ASCII frame boxes, or long lists of related notes.
6. Output ONLY the raw markdown of the note (including frontmatter). Do NOT wrap the entire output in outer ```markdown ... ``` code fences. Do NOT add conversational pleasantries or preamble.
"""

    prompt = f"""Please perform the surgical delta-merge for this note pair:

### BASELINE NOTE: `{orig_rel.name}` (Baseline text & structure to preserve):
```markdown
{orig_content}
```

### CURRENT UPDATED NOTE: `{cur_rel.name}` (Source of new technical facts and mechanics to extract):
```markdown
{cur_content}
```

Now output the complete restored markdown note:"""

    # Retry logic for API calls
    max_retries = 5
    delay = 5
    for attempt in range(1, max_retries + 1):
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                thinking_config=types.ThinkingConfig(thinking_level="high"),
                temperature=0.2
            )
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            break
        except Exception as e:
            if attempt == max_retries:
                raise e
            print(f"    [Warning] Attempt {attempt} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2

    cleaned = clean_model_output(response.text)

    # Sanity checks
    if len(cleaned) < 200:
        raise ValueError(f"Generated text too short ({len(cleaned)} chars) for {orig_rel}")

    if dry_run:
        print(f"    [DRY-RUN] Generated {len(cleaned.split())} words (original: {len(orig_content.split())} words)")
        return cleaned

    # Overwrite the original note
    orig_full.write_text(cleaned, encoding='utf-8')
    print(f"    [SUCCESS] Overwritten {orig_rel} ({len(cleaned.split())} words)")
    return cleaned

def main():
    parser = argparse.ArgumentParser(description="Rewrite note pairs using Gemini 3.8 Flash High.")
    parser.add_argument("--file", type=str, help="Relative or absolute path to a specific - original.md file")
    parser.add_argument("--all", action="store_true", help="Process all note pairs")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of notes to process")
    parser.add_argument("--filter", type=str, default=None, help="Filter pairs by substring in path")
    parser.add_argument("--dry-run", action="store_true", help="Perform run without writing files to disk")
    parser.add_argument("--force", action="store_true", help="Re-process even if recorded in state file")
    parser.add_argument("--model", type=str, default="gemini-3.8-flash", help="Model code (default: gemini-3.8-flash)")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: No GEMINI_API_KEY or GOOGLE_API_KEY found in environment or .env file.", file=sys.stderr)
        sys.exit(1)

    from google import genai
    client = genai.Client(api_key=api_key)

    rewrite_prompt, style_guide = load_prompt_and_style()
    state_file = REPO_ROOT / 'scripts' / '.rewrite_state.json'
    state = {}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding='utf-8'))
        except Exception:
            state = {}

    pairs = find_pairs()
    print(f"Total pairs found in repository: {len(pairs)}")

    if args.file:
        target = Path(args.file)
        if not target.is_absolute():
            target = REPO_ROOT / target
        norm_target = target.resolve()
        matching = [p for p in pairs if (REPO_ROOT / p[0]).resolve() == norm_target]
        if not matching:
            # Try matching basename or without ' - original.md'
            matching = [p for p in pairs if norm_target.name in str(p[0])]
        if not matching:
            print(f"ERROR: Could not find pair matching {args.file}", file=sys.stderr)
            sys.exit(1)
        pairs_to_process = matching
    else:
        pairs_to_process = pairs
        if args.filter:
            pairs_to_process = [p for p in pairs_to_process if args.filter.lower() in str(p[0]).lower()]

    if not args.force:
        pairs_to_process = [p for p in pairs_to_process if str(p[0]) not in state]

    if args.limit:
        pairs_to_process = pairs_to_process[:args.limit]

    print(f"Notes to process: {len(pairs_to_process)} (already completed: {len(state)})\n")

    for idx, (orig_rel, cur_rel) in enumerate(pairs_to_process, start=1):
        print(f"[{idx}/{len(pairs_to_process)}] Processing: {orig_rel}...", flush=True)
        t0 = time.time()
        try:
            process_pair(
                client=client,
                model_name=args.model,
                orig_rel=orig_rel,
                cur_rel=cur_rel,
                rewrite_prompt=rewrite_prompt,
                style_guide=style_guide,
                dry_run=args.dry_run
            )
            elapsed = time.time() - t0
            print(f"    Completed in {elapsed:.1f}s\n", flush=True)
            if not args.dry_run:
                state[str(orig_rel)] = {
                    "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "elapsed_s": round(elapsed, 1)
                }
                state_file.write_text(json.dumps(state, indent=2), encoding='utf-8')
        except Exception as e:
            print(f"    [ERROR] Failed on {orig_rel}: {e}\n", file=sys.stderr, flush=True)

    print("Batch processing completed.", flush=True)

if __name__ == '__main__':
    main()
