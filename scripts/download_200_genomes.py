#!/usr/bin/env python3
"""Download genome FASTA files from NCBI Datasets API.
Uses genome_list (or labels.csv) to determine WHICH genomes to download,
then looks up assembly_accession from Genomes_labeled.csv.
"""
import csv
import io
import os
import time
import urllib.request
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "Genomes_labeled.csv")
GENOMES_DIR = os.path.join(PROJECT_ROOT, "data", "genomes")
GENOME_LIST = os.path.join(PROJECT_ROOT, "genome_list")
API_BASE = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession"


def main():
    os.makedirs(GENOMES_DIR, exist_ok=True)

    # Load OUR genome list (from labels - first 100 HP + 100 NHP)
    with open(GENOME_LIST) as f:
        target_ids = [line.strip() for line in f if line.strip()]

    # Build genome_id -> assembly_accession lookup from CSV
    gid_to_assembly = {}
    with open(CSV_PATH) as f:
        r = csv.DictReader(f)
        for row in r:
            gid = (row.get("genome_id") or "").strip()
            acc = (row.get("assembly_accession") or "").strip()
            if gid and acc and (acc.startswith("GCA_") or acc.startswith("GCF_")):
                gid_to_assembly[gid] = acc

    rows = []
    for gid in target_ids:
        acc = gid_to_assembly.get(gid)
        if acc:
            rows.append((gid, acc))
        else:
            print(f"No assembly for {gid}, skipping")
    
    downloaded = 0
    for i, (genome_id, assembly_acc) in enumerate(rows):
        out_path = os.path.join(GENOMES_DIR, f"{genome_id}.fna")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            downloaded += 1
            continue
        url = f"{API_BASE}/{assembly_acc}/download?include_annotation_type=GENOME_FASTA&filename=genome.zip"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "pathogenprediction/1.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                for name in zf.namelist():
                    if name.endswith("_genomic.fna"):
                        content = zf.read(name).decode("utf-8", errors="replace")
                        with open(out_path, "w") as out:
                            out.write(content)
                        downloaded += 1
                        break
        except Exception as e:
            print(f"Failed {genome_id} ({assembly_acc}): {e}")
        if (i + 1) % 20 == 0:
            print(f"Processed {i+1}/{len(rows)}")
        time.sleep(0.5)
    
    print(f"Downloaded: {downloaded}/{len(rows)}")
    return downloaded

if __name__ == "__main__":
    main()
