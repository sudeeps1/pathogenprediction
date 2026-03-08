#!/bin/bash
# Download genome FASTA files from BV-BRC FTP.
# Requires genome_list in project root with one genome ID per line.
# Move downloaded .fna files to data/genomes/

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
GENOME_LIST="$PROJECT_ROOT/genome_list"
GENOMES_DIR="$PROJECT_ROOT/data/genomes"
mkdir -p "$GENOMES_DIR"
cd "$PROJECT_ROOT"

for i in $(cat "$GENOME_LIST"); do
  wget -qN "ftp://ftp.bvbrc.org/genomes/$i/$i.fna" || true
done

mv -f *.fna "$GENOMES_DIR/" 2>/dev/null || true
