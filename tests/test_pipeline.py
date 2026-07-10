"""
tests/test_pipeline.py - Unit test suite for pathogenprediction pipeline functions.
Validates sequence reading, k-mer generation/counting, one-hot encoding, and metrics computation.
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd
import torch

# Ensure scripts directory is in path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))

from kmer_table import get_all_kmers, count_kmers, compute_kmer_frequencies
from train_rc_cnn import onehot_encode, reverse_complement
from score import accuracy

class TestPathogenPipeline(unittest.TestCase):

    def test_get_all_kmers(self):
        """Verify k-mer list sizes for various lengths."""
        kmers_k1 = get_all_kmers(1)
        self.assertEqual(len(kmers_k1), 4)
        self.assertEqual(kmers_k1, ["A", "C", "G", "T"])
        
        kmers_k2 = get_all_kmers(2)
        self.assertEqual(len(kmers_k2), 16)
        self.assertIn("AA", kmers_k2)
        self.assertIn("TT", kmers_k2)

    def test_count_kmers(self):
        """Test k-mer occurrences counting on specific target sequences."""
        seq = "AAAAAA"  # Single 6-mer occurrence
        counts = count_kmers(seq, 6)
        self.assertEqual(counts["AAAAAA"], 1)
        self.assertEqual(sum(counts.values()), 1)

        seq_mixed = "ACGTACGT"
        counts_k2 = count_kmers(seq_mixed, 2)
        self.assertEqual(counts_k2["AC"], 2)
        self.assertEqual(counts_k2["CG"], 2)
        self.assertEqual(counts_k2["GT"], 2)

    def test_compute_kmer_frequencies(self):
        """Verify frequency calculations and edge cases."""
        counts = {"A": 1, "C": 1, "G": 1, "T": 1}
        freqs = compute_kmer_frequencies(counts)
        for k in freqs:
            self.assertEqual(freqs[k], 0.25)
            
        empty_counts = {"A": 0, "C": 0}
        empty_freqs = compute_kmer_frequencies(empty_counts)
        self.assertEqual(empty_freqs["A"], 0.0)

    def test_onehot_encode(self):
        """Check tensor shape and hot positions for onehot encodings."""
        seq = "ACGT"
        encoded = onehot_encode(seq)
        # Expected shape is (Length, Channels) -> (4, 4)
        self.assertEqual(encoded.shape, (4, 4))
        
        # Verify specific channel indices: A=0, C=1, G=2, T=3
        self.assertEqual(encoded[0, 0], 1.0)  # A
        self.assertEqual(encoded[1, 1], 1.0)  # C
        self.assertEqual(encoded[2, 2], 1.0)  # G
        self.assertEqual(encoded[3, 3], 1.0)  # T

    def test_reverse_complement(self):
        """Verify sequence flipping and nucleotide complement conversions."""
        seq = "AAAA"
        self.assertEqual(reverse_complement(seq), "TTTT")
        
        seq_mixed = "ACGT"
        # Complement of ACGT is TGCA, reversed is ACGT (self-complementary)
        self.assertEqual(reverse_complement(seq_mixed), "ACGT")
        
        seq_complex = "GGACCT"
        # Complement of GGACCT is CCTGGA, reversed is AGGTCC
        self.assertEqual(reverse_complement(seq_complex), "AGGTCC")

    def test_accuracy_metric(self):
        """Verify math correctness of prediction scoring function."""
        data = {
            "true_label": [1, 0, 1, 1, 0],
            "pred_label": [1, 0, 0, 1, 1]  # 3 correct, 2 incorrect
        }
        df = pd.DataFrame(data)
        self.assertAlmostEqual(accuracy(df), 0.6)
        
        empty_df = pd.DataFrame(columns=["true_label", "pred_label"])
        self.assertEqual(accuracy(empty_df), 0.0)

if __name__ == "__main__":
    unittest.main()
