# Pathogen Prediction Protocol

**Computational Protocol for Organism-Level Pathogenicity Classification from Bacterial Genomes Using Machine Learning**

*Developed as part of the Department of Biology research at the University of North Texas.*

Bacterial pathogen identification is critical for clinical diagnostics, public health surveillance, and biodefense. Traditional culture-based methods or alignment-heavy sequence queries are slow and struggle with novel or highly mutated strains. This repository provides a state-of-the-art, alignment-free computational pipeline that extracts high-dimensional sequence features (k-mers) and DNA structural representations directly from raw genomic files, classifying bacterial organisms into **human pathogens (HP)** or **non-human pathogens (NHP)** using three optimized machine learning paradigms: Sparse SVM, Random Forests, and Reverse-Complement Convolutional Neural Networks.

## Programmatic API & Usage Examples

While the pipeline is fully executable via the shell scripts in the `scripts/` directory, the core utilities can also be integrated directly into custom Python pipelines.

### 1. Extracting K-Mer Frequencies
```python
from scripts.kmer_table import count_kmers, compute_kmer_frequencies

# Analyze custom raw DNA sequence sequence
seq = "ATGCGATCGATCGATCGATCGATCGATCGATC"
counts = count_kmers(seq, k=6)
frequencies = compute_kmer_frequencies(counts)

print(f"Computed frequencies for {len(frequencies)} distinct 6-mers.")
```

### 2. Reverse-Complement Invariant Encoding
```python
import torch
from scripts.train_rc_cnn import onehot_encode, reverse_complement

seq = "ATGCGATCG"
# Generate strand-invariant representations
forward_encoding = onehot_encode(seq).T               # Shape: (4, L)
rc_sequence = reverse_complement(seq)
rc_encoding = onehot_encode(rc_sequence).T           # Shape: (4, L)
```

## Citation

If you use this code, please cite:

```bibtex
@article{senivarapu2026pathogen,
  author = {Senivarapu, Sudeep and Coxe, Tallon and Murari, Anishsairam},
  title = {Computational Protocol for Organism-Level Pathogenicity Classification from Bacterial Genomes Using Machine Learning},
  journal = {Forthcoming},
  year = {2026},
  note = {Code available at https://github.com/sudeeps1/pathogenprediction}
}
```

## Requirements

- Python 3.10+
- 16 GB RAM, 50 GB disk
- Conda (recommended) or pip

## Setup

```bash
conda create -n pathogen python=3.10 -y
conda activate pathogen
conda install -c conda-forge ncbi-datasets-cli  # optional, for NCBI genome downloads
pip install -r requirements.txt
```

## Directory Structure

```
pathogenprediction/
├── data/
│   └── genomes/          # Genome FASTA files (.fna)
├── labels/
│   ├── accessions_pathogenic.txt
│   ├── accessions_nonpathogenic.txt
│   └── labels.csv
├── figures/               # Workflow and architecture diagrams
├── results/               # Pipeline outputs
├── scripts/
│   ├── create_genome_list.py
│   ├── create_labels_from_accessions.py
│   ├── download_200_genomes.py
│   ├── download_genomes.sh
│   ├── make_split.py
│   ├── kmer_table.py
│   ├── train_svm.py
│   ├── train_rf.py
│   ├── make_fragments.py
│   ├── train_rc_cnn.py
│   └── score.py
├── genome_list
├── requirements.txt
└── README.md
```

## Workflow

### 1. Prepare labels from BacSPaD

1. Download the BacSPaD dataset from [https://bacspad.altrabio.com/#data](https://bacspad.altrabio.com/#data).  
2. Filter HP rows → select first 100 genome IDs → save to `labels/accessions_pathogenic.txt`  
3. Filter NHP rows → select first 100 genome IDs → save to `labels/accessions_nonpathogenic.txt`  
4. Create labels:
   ```bash
   python scripts/create_labels_from_accessions.py
   ```
5. Create genome list:
   ```bash
   python scripts/create_genome_list.py
   ```

### 2. Download genomes

**Option A – NCBI Datasets API** (recommended if BV-BRC FTP fails):

Requires `data/Genomes_labeled.csv` (from BacSPaD export with `genome_id` and `assembly_accession` columns) and `genome_list`:

```bash
python scripts/download_200_genomes.py
```

**Option B – BV-BRC FTP**:

```bash
bash scripts/download_genomes.sh
```

Or manually:
```bash
for i in $(cat genome_list); do wget -qN "ftp://ftp.bvbrc.org/genomes/$i/$i.fna"; done
mv *.fna data/genomes/
```

### 3. Run pipeline

```bash
python scripts/make_split.py
python scripts/kmer_table.py
python scripts/train_svm.py
python scripts/train_rf.py
python scripts/make_fragments.py
python scripts/train_rc_cnn.py
python scripts/score.py
```

### 4. Results

- `results/svm_predictions.csv` – SVM predictions  
- `results/rf_predictions.csv` – Random Forest predictions  
- `results/cnn_predictions.csv` – CNN predictions  
- `results/metrics.txt` – Accuracy for each model  

## Design Decisions & Model Architecture

This protocol implements three distinct machine learning approaches to classify bacterial pathogenicity, optimized for genomic sequence characteristics:

1. **L1-Regularized (Sparse) SVM**: Genomic 6-mer analysis produces a high-dimensional feature space ($4^6 = 4,096$ frequencies). We apply a Linear Support Vector Classifier (SVC) with an L1 regularization penalty. The L1 penalty forces the coefficients of non-informative k-mers to exactly zero, performing embedded feature selection and preventing overfitting in sparse feature spaces.
2. **Random Forest (RF)**: While linear SVMs capture independent feature impacts, Random Forests model complex, non-linear interactions and epistatic combinations of k-mers without requiring explicit feature scaling. Configured with 500 estimators to ensure variance minimization.
3. **Reverse-Complement CNN (RC-CNN)**: DNA is double-stranded and read orientations are arbitrary. To enforce strand invariance, the CNN evaluates both the forward sequence and its reverse complement. The model averages the forward and reverse logits to ensure predictions are identical regardless of which strand was sequenced.

## Testing & Verification

### Unit Tests
A Python `unittest` suite verifies core pipeline functions, including k-mer generation/counting, one-hot encoding shapes, and reverse-complement flipping:
```bash
python tests/test_pipeline.py
```

### End-to-End Integration Demo
To verify that the entire split, extraction, training, and scoring pipeline works without needing NCBI downloads, run:
```bash
python run_demo.py
```
This script generates a temporary mock dataset of 4 genomes, executes all processing steps, verifies outputs in the `results/` folder, and clean up.

### Sample Outputs
Sample predictions and metric runs from the demo integration are preserved in `results/sample_outputs/` for immediate reference.

## Data

Labels follow `labels.csv` with columns `id,label` (1 = HP, 0 = NHP). Genome FASTA files go in `data/genomes/` as `{genome_id}.fna`.

## License

MIT
