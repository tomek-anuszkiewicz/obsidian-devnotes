import os
import shutil

def main():
    csv_path = 'pairs.csv'
    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    pairs = []
    for line in lines:
        parts = [p.strip() for p in line.split(';')]
        if len(parts) == 2:
            pairs.append((parts[0], parts[1]))
        else:
            print(f"Skipping invalid line: {line}")

    print(f"Found {len(pairs)} pairs to process.")

    # Validation pass first
    for dst, src in pairs:
        if not os.path.exists(src):
            raise FileNotFoundError(f"Source file not found: {src}")
        if not os.path.exists(dst):
            raise FileNotFoundError(f"Destination file not found: {dst}")

    copied_count = 0
    deleted_count = 0

    for dst, src in pairs:
        # Copy content of column 2 (src) to column 1 (dst)
        shutil.copyfile(src, dst)
        copied_count += 1
        
        # Delete file from column 2 (src)
        os.remove(src)
        deleted_count += 1

    print(f"Successfully copied {copied_count} files and deleted {deleted_count} source files.")

if __name__ == '__main__':
    main()
