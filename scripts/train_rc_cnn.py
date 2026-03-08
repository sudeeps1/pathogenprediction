#!/usr/bin/env python3
"""
Train CNN with reverse-complement for DNA fragment pathogenicity classification.
One-hot encodes fragments, applies CNN to forward and reverse-complement,
averages probabilities, trains 10 epochs. Aggregates fragment predictions to
organism-level. Output: results/cnn_predictions.csv
"""

import os
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAGMENTS_PATH = os.path.join(PROJECT_ROOT, "results", "fragments.tsv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "results", "cnn_predictions.csv")
EPOCHS = 10

BASE_TO_IDX = {"A": 0, "C": 1, "G": 2, "T": 3}
COMPLEMENT = {"A": "T", "T": "A", "C": "G", "G": "C"}


def onehot_encode(seq):
    """Convert DNA string to one-hot matrix (L, 4)."""
    arr = torch.zeros(len(seq), 4)
    for i, c in enumerate(seq):
        if c in BASE_TO_IDX:
            arr[i, BASE_TO_IDX[c]] = 1.0
    return arr


def reverse_complement(seq):
    """Return reverse complement of DNA sequence."""
    return "".join(COMPLEMENT.get(c, c) for c in reversed(seq))


class RCConvBlock(nn.Module):
    """Conv1D block: Conv -> ReLU -> MaxPool."""

    def __init__(self, in_ch, out_ch, kernel_size=7):
        super().__init__()
        self.conv = nn.Conv1d(in_ch, out_ch, kernel_size, padding=kernel_size // 2)
        self.pool = nn.MaxPool1d(2)

    def forward(self, x):
        return self.pool(torch.relu(self.conv(x)))


class DNACNN(nn.Module):
    """CNN for 250bp one-hot DNA. Input: (B, 4, 250)."""

    def __init__(self, num_classes=2):
        super().__init__()
        self.conv1 = RCConvBlock(4, 32, 7)
        self.conv2 = RCConvBlock(32, 64, 5)
        self.conv3 = RCConvBlock(64, 128, 3)
        # After 3 pools of 2: 250 -> 125 -> 62 -> 31
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 31, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        return self.fc(x)


class FragmentDataset(Dataset):
    def __init__(self, df):
        self.df = df.reset_index(drop=True)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, i):
        row = self.df.iloc[i]
        seq = row["fragment_sequence"]
        oh = onehot_encode(seq).T  # (4, 250)
        label = int(row["label"])
        return oh, label, row["id"]


def train_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    for x, y, _ in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(loader)


@torch.no_grad()
def predict_with_rc(model, loader, device):
    """Predict: forward + reverse-complement, average probs."""
    model.eval()
    results = []
    for x, y, gid in loader:
        x = x.to(device)
        # Forward strand
        logits_f = model(x)
        prob_f = torch.softmax(logits_f, dim=1)
        # Reverse complement: flip sequence, then swap channels A<->T, C<->G
        x_rev = x.flip(2)  # reverse along sequence length
        x_rc = x_rev[:, [3, 2, 1, 0], :]  # complement: A->T,C->G,G->C,T->A
        logits_rc = model(x_rc)
        prob_rc = torch.softmax(logits_rc, dim=1)
        prob_avg = (prob_f + prob_rc) / 2
        for i in range(len(gid)):
            gid_val = gid[i]
            gid_str = str(gid_val.item()) if hasattr(gid_val, "item") else str(gid_val)
            results.append((gid_str, y[i].item(), prob_avg[i, 1].item()))
    return results


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    df = pd.read_csv(FRAGMENTS_PATH, sep="\t", dtype={"id": str})

    train_df = df[df["split"] == "TRAIN"]
    test_df = df[df["split"] == "TEST"]

    train_ds = FragmentDataset(train_df)
    test_ds = FragmentDataset(test_df)
    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=64, shuffle=False, num_workers=0)

    model = DNACNN().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    for _ in range(EPOCHS):
        train_epoch(model, train_loader, optimizer, criterion, device)

    results = predict_with_rc(model, test_loader, device)
    out_df = pd.DataFrame(results, columns=["id", "true_label", "pred_prob"])
    # Aggregate to organism level: average fragment probs per genome
    agg = out_df.groupby("id").agg({"true_label": "first", "pred_prob": "mean"}).reset_index()
    agg["pred_label"] = (agg["pred_prob"] >= 0.5).astype(int)
    agg[["id", "true_label", "pred_label"]].to_csv(OUTPUT_PATH, index=False)


if __name__ == "__main__":
    main()
