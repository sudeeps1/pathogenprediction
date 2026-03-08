#!/usr/bin/env python3
"""Create labels.csv from accessions_pathogenic.txt and accessions_nonpathogenic.txt.
Output: labels/labels.csv with columns id,label (1=HP, 0=NHP).
"""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
LABELS_DIR = os.path.join(PROJECT_ROOT, "labels")
PATHOGENIC = os.path.join(LABELS_DIR, "accessions_pathogenic.txt")
NONPATHOGENIC = os.path.join(LABELS_DIR, "accessions_nonpathogenic.txt")
OUT_CSV = os.path.join(LABELS_DIR, "labels.csv")


def main():
    rows = []
    for path, label in [(PATHOGENIC, 1), (NONPATHOGENIC, 0)]:
        if not os.path.exists(path):
            print(f"Missing {path} — create it from BacSPaD export (first 100 HP/NHP genome IDs)")
            continue
        with open(path) as f:
            for line in f:
                gid = line.strip()
                if gid:
                    rows.append((gid, label))
    if not rows:
        print("No labels found. Add accessions_pathogenic.txt and accessions_nonpathogenic.txt")
        return
    os.makedirs(LABELS_DIR, exist_ok=True)
    with open(OUT_CSV, "w") as f:
        f.write("id,label\n")
        for gid, label in rows:
            f.write(f"{gid},{label}\n")
    print(f"Wrote {len(rows)} labels to {OUT_CSV}")


if __name__ == "__main__":
    main()
