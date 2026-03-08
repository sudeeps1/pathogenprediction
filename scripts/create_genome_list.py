#!/usr/bin/env python3
"""Create genome_list from labels.csv (one genome ID per line).
Used by download scripts to know which genomes to fetch.
"""
import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
LABELS_CSV = os.path.join(PROJECT_ROOT, "labels", "labels.csv")
GENOME_LIST = os.path.join(PROJECT_ROOT, "genome_list")


def main():
    if not os.path.exists(LABELS_CSV):
        print(f"Missing {LABELS_CSV}. Run create_labels_from_accessions.py first.")
        return
    ids = []
    with open(LABELS_CSV) as f:
        r = csv.DictReader(f)
        for row in r:
            gid = (row.get("id") or "").strip()
            if gid:
                ids.append(gid)
    with open(GENOME_LIST, "w") as f:
        f.write("\n".join(ids) + "\n")
    print(f"Wrote {len(ids)} genome IDs to {GENOME_LIST}")


if __name__ == "__main__":
    main()
