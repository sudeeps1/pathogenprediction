"""
run_demo.py - E2E integration test and demo runner for the pathogenprediction pipeline.
Generates synthetic DNA FASTA genomes, constructs labels, runs split/kmer/CNN steps,
and outputs classification accuracy metrics.
"""

import os
import sys
import shutil
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
GENOMES_DIR = os.path.join(DATA_DIR, "genomes")
LABELS_DIR = os.path.join(PROJECT_ROOT, "labels")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

def generate_random_dna(length):
    import random
    return "".join(random.choice("ACGT") for _ in range(length))

def create_mock_dataset():
    """Generates temporary FASTA genomes and labels.csv for the integration run."""
    print("[demo] Generating mock genomes and label files...")
    os.makedirs(GENOMES_DIR, exist_ok=True)
    os.makedirs(LABELS_DIR, exist_ok=True)

    # We generate 4 mock genomes, each of length 600bp (larger than the 250bp fragment size)
    genomes = {
        "G001": 1,  # Pathogenic (HP)
        "G002": 1,  # Pathogenic (HP)
        "G003": 0,  # Non-pathogenic (NHP)
        "G004": 0   # Non-pathogenic (NHP)
    }

    for gid, label in genomes.items():
        fasta_path = os.path.join(GENOMES_DIR, f"{gid}.fna")
        # Write dummy FASTA
        with open(fasta_path, "w") as f:
            f.write(f">genome_{gid} | mock genomic sequence\n")
            # Write sequence in blocks of 80 characters
            seq = generate_random_dna(600)
            for chunk_start in range(0, len(seq), 80):
                f.write(seq[chunk_start:chunk_start + 80] + "\n")

    # Write labels.csv
    labels_csv = os.path.join(LABELS_DIR, "labels.csv")
    with open(labels_csv, "w") as f:
        f.write("id,label\n")
        for gid, label in genomes.items():
            f.write(f"{gid},{label}\n")

    print(f"[demo] Dataset prepared. Created 4 mock genomes in {GENOMES_DIR}.")

def run_script(script_name):
    """Executes a pipeline script via subprocess."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    print(f"[demo] Running: python {script_name}...")
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    if result.returncode != 0:
        print(f"[demo] ERROR running {script_name}:")
        print(result.stderr)
        sys.exit(1)

def main():
    print("=" * 60)
    print("PATHOGEN PREDICTION PIPELINE - INTEGRATION DEMO RUNNER")
    print("=" * 60)

    # 1. Create mock data
    create_mock_dataset()

    # 2. Run pipeline scripts in sequence
    pipeline_scripts = [
        "make_split.py",
        "kmer_table.py",
        "make_fragments.py",
        "train_svm.py",
        "train_rf.py",
        "train_rc_cnn.py",
        "score.py"
    ]

    for script in pipeline_scripts:
        run_script(script)

    # 3. Read and print resulting metrics
    metrics_path = os.path.join(RESULTS_DIR, "metrics.txt")
    if os.path.exists(metrics_path):
        print("\n" + "=" * 40)
        print("PIPELINE EXECUTION METRICS")
        print("=" * 40)
        with open(metrics_path) as f:
            print(f.read())
        print("=" * 40)
        print("[demo] SUCCESS: Predictions and performance metrics written to results/ directory.")
    else:
        print("[demo] ERROR: results/metrics.txt was not generated.")
        sys.exit(1)

    # 4. Clean up mock dataset directories (keeps results intact)
    print("\n[demo] Cleaning up temporary genomes and label directories...")
    shutil.rmtree(GENOMES_DIR)
    shutil.rmtree(LABELS_DIR)
    print("[demo] Cleanup complete. Demo run finished successfully!\n")

if __name__ == "__main__":
    main()
