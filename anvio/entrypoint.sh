#!/bin/bash


if [ ! -f /app/gene_list ]; then
	echo "gene list not found."
	exit 1
fi
if [ ! -d /app/bams ]; then
	echo "error mounting bams directory."
	exit 1
fi
if [ ! -f /app/db.db ]; then
	echo "error finding db file."
	exit 1
fi
if [ ! -d /output ]; then
	echo "error mounting output directory."
	exit 1
fi

while read p
do
	gene=$(cut -d$'\t' -f3 <<<"$p")
	anvi-get-short-reads-mapping-to-a-gene \
		-i /app/bams/*.bam \
		-c /app/db.db \
		--gene-caller-id $gene \
		--leeway 35 \
		-o "/output/${gene}.fa"
done < /app/gene_list
