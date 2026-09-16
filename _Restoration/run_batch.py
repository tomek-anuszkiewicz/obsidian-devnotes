#!/usr/bin/env python3
"""
_Restoration/run_batch.py

Executes parallel restoration across notes from vault_to_original_mapping.json
using restore_notes.py with --with-original.
Audits all output notes using verify_restoration_stats.py upon completion.
"""

import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO_ROOT = Path(__file__).resolve().parent.parent
MAPPING_JSON = REPO_ROOT / "_Restoration" / "vault_to_original_mapping.json"
RESTORE_SCRIPT = REPO_ROOT / "_Restoration" / "restore_notes.py"
VERIFY_SCRIPT = REPO_ROOT / "_Restoration" / "verify_restoration_stats.py"
OUT_DIR = REPO_ROOT / "_Restoration" / "restored_output"


def process_single_note(item: dict, out_dir: Path, force: bool = False):
    rel_path = item["current_path"]
    abs_path = REPO_ROOT / rel_path
    filename = abs_path.name
    target_out = out_dir / filename

    if target_out.exists() and not force:
        return filename, "SKIPPED_EXISTS", 0

    cmd = [
        sys.executable,
        str(RESTORE_SCRIPT),
        "--file", str(abs_path),
        "--output-dir", str(out_dir),
        "--with-original"
    ]

    t0 = time.time()
    for attempt in range(3):
        try:
            ret = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            elapsed = time.time() - t0
            if ret.returncode == 0:
                return filename, "SUCCESS", elapsed
            else:
                if "429" in ret.stderr or "RESOURCE_EXHAUSTED" in ret.stderr:
                    time.sleep(5 * (attempt + 1))
                    continue
                return filename, f"FAIL ({ret.stderr.strip()[:120]})", elapsed
        except Exception as e:
            if attempt == 2:
                return filename, f"ERROR ({e})", time.time() - t0
            time.sleep(3)

    return filename, "FAIL_RETRIES_EXHAUSTED", time.time() - t0


def main():
    parser = argparse.ArgumentParser(description="Run batch restoration on vault notes")
    parser.add_argument("--count", "-c", type=int, default=108, help="Number of notes to process (default: 108)")
    parser.add_argument("--start", "-s", type=int, default=0, help="Starting index in mapping (default: 0)")
    parser.add_argument("--workers", "-w", type=int, default=3, help="Concurrent workers (default: 3)")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite already restored notes")

    args = parser.parse_args()

    with open(MAPPING_JSON, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    target_slice = mapping[args.start : args.start + args.count]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("============================================================")
    print(f"Batch Restoration: {len(target_slice)} notes (indices {args.start} to {args.start + len(target_slice) - 1})")
    print(f"Workers: {args.workers} | Target Dir: {OUT_DIR} | Overwrite: {args.force}")
    print("============================================================\n")

    completed = 0
    total = len(target_slice)

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_map = {
            executor.submit(process_single_note, item, OUT_DIR, args.force): item
            for item in target_slice
        }

        for future in as_completed(future_map):
            completed += 1
            filename, status, elapsed = future.result()
            print(f"[{completed:3d}/{total:3d}] {status:16s} ({elapsed:4.1f}s) -> {filename}")

    print("\n============================================================")
    print("Running Statistical Quality Gate & Audit across all restored notes...")
    print("============================================================\n")
    subprocess.run([sys.executable, str(VERIFY_SCRIPT)])


if __name__ == "__main__":
    main()
