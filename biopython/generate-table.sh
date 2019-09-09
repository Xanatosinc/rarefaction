#!/bin/bash

for file in $(ls /fastas); do
	python /biopython/faToTab.py /fastas/${file} >> /output/fasta-table.tsv
done
