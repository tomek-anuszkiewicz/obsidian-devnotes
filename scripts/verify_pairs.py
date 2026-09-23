import os
import glob
import yaml
import re

def get_frontmatter(p):
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            try:
                data = yaml.safe_load(parts[1])
                if isinstance(data, dict):
                    return data
            except:
                pass
    return {}

def extract_content(p):
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            return parts[2]
    return text

def main():
    pairs = []
    for p in glob.glob('*/**/* - original.md', recursive=True):
        cur_p = p.replace(' - original.md', '.md')
        if os.path.exists(cur_p):
            pairs.append((p, cur_p))

    print(f"Total pairs: {len(pairs)}")

    discrepancies = []
    for orig_p, cur_p in pairs:
        fm_orig = get_frontmatter(orig_p)
        fm_cur = get_frontmatter(cur_p)
        
        t_orig = fm_orig.get('title', os.path.basename(orig_p).replace(' - original.md', ''))
        t_cur = fm_cur.get('title', os.path.basename(cur_p).replace('.md', ''))
        
        aliases_cur = [str(a).strip().lower() for a in fm_cur.get('aliases', []) if a]
        aliases_orig = [str(a).strip().lower() for a in fm_orig.get('aliases', []) if a]
        
        title_exact = (str(t_orig).strip().lower() == str(t_cur).strip().lower())
        in_aliases = (str(t_orig).strip().lower() in aliases_cur) or (str(t_cur).strip().lower() in aliases_orig)
        
        # Content overlap
        c_orig = extract_content(orig_p)
        c_cur = extract_content(cur_p)
        
        orig_words = set(re.findall(r'[a-z]{4,}', c_orig.lower()))
        cur_words = set(re.findall(r'[a-z]{4,}', c_cur.lower()))
        
        overlap = len(orig_words & cur_words) / len(orig_words) if orig_words else 0
        jaccard = len(orig_words & cur_words) / len(orig_words | cur_words) if (orig_words | cur_words) else 0

        # Check for any flag
        if not title_exact and not in_aliases:
            discrepancies.append((orig_p, cur_p, t_orig, t_cur, overlap, jaccard, "TITLE_MISMATCH"))
        elif overlap < 0.35:
            discrepancies.append((orig_p, cur_p, t_orig, t_cur, overlap, jaccard, "LOW_OVERLAP"))

    print(f"\nDiscrepancies found: {len(discrepancies)}")
    for orig_p, cur_p, t_o, t_c, ov, jc, reason in discrepancies:
        print(f"[{reason}]")
        print(f"  Orig Path: {orig_p}")
        print(f"  Cur Path:  {cur_p}")
        print(f"  Orig Title: {t_o}")
        print(f"  Cur Title:  {t_c}")
        print(f"  Word Overlap (how much of orig words in cur): {ov:.1%}, Jaccard: {jc:.2f}\n")

if __name__ == '__main__':
    main()
