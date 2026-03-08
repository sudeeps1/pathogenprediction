#!/usr/bin/env python3
"""
Compute classification accuracy for each ML pipeline.
Loads svm_predictions.csv, rf_predictions.csv, cnn_predictions.csv.
Output: results/metrics.txt
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
OUTPUT_PATH = os.path.join(RESULTS_DIR, "metrics.txt")


def accuracy(df):
    correct = (df["true_label"] == df["pred_label"]).sum()
    return correct / len(df) if len(df) > 0 else 0.0


def main():
    lines = []

    for name, fname in [
        ("Sparse SVM", "svm_predictions.csv"),
        ("Random Forest", "rf_predictions.csv"),
        ("CNN", "cnn_predictions.csv"),
    ]:
        path = os.path.join(RESULTS_DIR, fname)
        if not os.path.exists(path):
            lines.append(f"Model: {name}\nAccuracy: (file not found)\n")
            continue
        import pandas as pd
        df = pd.read_csv(path)
        acc = accuracy(df)
        lines.append(f"Model: {name}\nAccuracy: {acc:.2f}\n")

    with open(OUTPUT_PATH, "w") as f:
        f.write("\n".join(lines).rstrip() + "\n")


if __name__ == "__main__":
    main()
