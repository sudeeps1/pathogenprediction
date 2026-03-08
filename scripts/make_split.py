#!/usr/bin/env python3
"""
Create train-test split for pathogenicity classification dataset.
Loads labels/labels.csv, sorts by genome ID, assigns 80% to train and 20% to test.
Output: results/split.csv with columns id, label, split
"""

import os
import pandas as pd

# Paths relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABELS_PATH = os.path.join(PROJECT_ROOT, "labels", "labels.csv")
RESULTS_PATH = os.path.join(PROJECT_ROOT, "results", "split.csv")


def main():
    # Load the dataset
    df = pd.read_csv(LABELS_PATH, dtype={"id": str})
    df = df.dropna(subset=["id", "label"])

    # Sort by genome identifier
    df = df.sort_values("id").reset_index(drop=True)

    # Assign first 80% to training, remaining 20% to testing
    n_total = len(df)
    n_train = int(0.8 * n_total)
    df["split"] = ["TRAIN"] * n_train + ["TEST"] * (n_total - n_train)

    # Save to results
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    df[["id", "label", "split"]].to_csv(RESULTS_PATH, index=False)


if __name__ == "__main__":
    main()
