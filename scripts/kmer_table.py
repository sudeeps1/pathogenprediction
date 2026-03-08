#!/usr/bin/env python3
"""
Generate k-mer frequency features from genome FASTA files.
For each genome: read sequence, keep only A/C/G/T, count 6-mers, convert to frequencies.
Output: results/k6_features.csv (rows=genomes, columns=6-mer features)
"""

import os
from itertools import product

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOMES_DIR = os.path.join(PROJECT_ROOT, "data", "genomes")
RESULTS_PATH = os.path.join(PROJECT_ROOT, "results", "k6_features.csv")
K = 6


def get_all_kmers(k):
    """Generate all possible k-mers of length k (A, C, G, T only)."""
    bases = "ACGT"
    return ["".join(p) for p in product(bases, repeat=k)]


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


def count_kmers(seq, k):
    """Count all k-mers in sequence."""
    kmer_list = get_all_kmers(k)
    counts = {km: 0 for km in kmer_list}
    for i in range(len(seq) - k + 1):
        kmer = seq[i : i + k]
        if kmer in counts:
            counts[kmer] += 1
    return counts


def compute_kmer_frequencies(counts):
    """Convert raw counts to frequencies."""
    total = sum(counts.values())
    if total == 0:
        return {k: 0.0 for k in counts}
    return {k: v / total for k, v in counts.items()}


def main():
    kmer_order = get_all_kmers(K)
    rows = []
    genome_ids = []

    for fname in sorted(os.listdir(GENOMES_DIR)):
        if not fname.endswith(".fna"):
            continue
        genome_id = fname.replace(".fna", "")
        fasta_path = os.path.join(GENOMES_DIR, fname)

        seq = read_genome_sequence(fasta_path)
        counts = count_kmers(seq, K)
        freqs = compute_kmer_frequencies(counts)

        genome_ids.append(genome_id)
        row = [freqs[km] for km in kmer_order]
        rows.append(row)

    df = pd.DataFrame(rows, index=genome_ids, columns=kmer_order)
    df.index.name = "id"

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    df.to_csv(RESULTS_PATH)


if __name__ == "__main__":
    main()
