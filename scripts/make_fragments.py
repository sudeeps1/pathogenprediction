#!/usr/bin/env python3
"""
Create fixed-length DNA fragments from genome sequences for CNN training.
For each genome: read sequence, keep A/C/G/T only, split into 250bp fragments,
retain first 10,000 per genome. Output: results/fragments.tsv
"""

import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOMES_DIR = os.path.join(PROJECT_ROOT, "data", "genomes")
SPLIT_PATH = os.path.join(PROJECT_ROOT, "results", "split.csv")
RESULTS_PATH = os.path.join(PROJECT_ROOT, "results", "fragments.tsv")
FRAGMENT_LENGTH = 250
MAX_FRAGMENTS_PER_GENOME = 10_000


def read_genome_sequence(fasta_path):
    """Read FASTA and return concatenated sequence (A, C, G, T only)."""
    seq_parts = []
    with open(fasta_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                continue
            seq_parts.append(line.upper())
    full_seq = "".join(seq_parts)
    return "".join(c for c in full_seq if c in "ACGT")


def main():
    split_df = pd.read_csv(SPLIT_PATH, dtype={"id": str})
    split_by_id = split_df.set_index("id")["split"].to_dict()
    label_by_id = split_df.set_index("id")["label"].to_dict()

    rows = []
    for fname in sorted(os.listdir(GENOMES_DIR)):
        if not fname.endswith(".fna"):
            continue
        genome_id = fname.replace(".fna", "")
        split_val = split_by_id.get(genome_id)
        label_val = label_by_id.get(genome_id)
        if split_val is None or label_val is None:
            continue

        fasta_path = os.path.join(GENOMES_DIR, fname)
        seq = read_genome_sequence(fasta_path)

        n_fragments = 0
        for i in range(0, len(seq) - FRAGMENT_LENGTH + 1, FRAGMENT_LENGTH):
            if n_fragments >= MAX_FRAGMENTS_PER_GENOME:
                break
            frag = seq[i : i + FRAGMENT_LENGTH]
            if len(frag) == FRAGMENT_LENGTH:
                rows.append({
                    "id": genome_id,
                    "split": split_val,
                    "label": label_val,
                    "fragment_sequence": frag,
                })
                n_fragments += 1

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    df.to_csv(RESULTS_PATH, sep="\t", index=False)


if __name__ == "__main__":
    main()
