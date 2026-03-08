#!/usr/bin/env python3
"""
Train Random Forest classifier on k-mer features.
Uses RandomForestClassifier with 500 trees. Output: results/rf_predictions.csv
"""

import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_PATH = os.path.join(PROJECT_ROOT, "results", "k6_features.csv")
SPLIT_PATH = os.path.join(PROJECT_ROOT, "results", "split.csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "results", "rf_predictions.csv")


def main():
    features = pd.read_csv(FEATURES_PATH, index_col=0)
    features.index = features.index.astype(str)
    split_df = pd.read_csv(SPLIT_PATH, dtype={"id": str})

    train_ids = split_df[split_df["split"] == "TRAIN"]["id"].values
    test_ids = split_df[split_df["split"] == "TEST"]["id"].values

    X_train = features.loc[features.index.isin(train_ids)]
    y_train = split_df[split_df["id"].isin(train_ids)].set_index("id").loc[X_train.index, "label"]

    X_test = features.loc[features.index.isin(test_ids)]
    y_test = split_df[split_df["id"].isin(test_ids)].set_index("id").loc[X_test.index, "label"]

    clf = RandomForestClassifier(n_estimators=500, random_state=0)
    clf.fit(X_train, y_train)

    pred = clf.predict(X_test)

    out = pd.DataFrame({
        "id": X_test.index,
        "true_label": y_test.values,
        "pred_label": pred,
    })
    out.to_csv(OUTPUT_PATH, index=False)


if __name__ == "__main__":
    main()
