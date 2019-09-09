#!/bin/bash

echo "Using" $(ls /fastas | wc -l) "fasta files"
/app/generate-table.sh /fastas
