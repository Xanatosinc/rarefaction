#!/bin/bash

IMAGE="paranvio"

GENE_LIST_DIR="/home/larkinsa/I09_allmeta/CallerIds/caller-splits"
BAMS_DIR="/home/larkinsa/I09_allmeta/BAMS"
DB="/home/larkinsa/I09_allmeta/AllFileAnalysis/ProSynSAR_GDB_reformat.db"
OUTPUT_DIR="./output"


if [ ! -d ${GENE_LIST_DIR} ]; then
	echo "gene list dir not found."
	exit 1
fi
if [ ! -d ${BAMS_DIR} ]; then
	echo "error finding bams directory."
	exit 1
fi
if [ ! -f ${DB} ]; then
	echo "error finding db file."
	exit 1
fi
if [ ! -d ${OUTPUT_DIR} ]; then
	echo "error mounting output directory."
	exit 1
fi

starting_port=8080
port_offest=0
for gene_list in $(ls $GENE_LIST_DIR)
do
	port=$((port_offset+${starting_port}))
	((port_offset++))
	docker run \
		--name ${gene_list} \
		-v ${GENE_LIST_DIR}/${gene_list}:/app/gene_list:z \
		-v ${BAMS_DIR}:/app/bams:z \
		-v ${DB}:/app/db.db:z \
		-v ${OUTPUT_DIR}:/output:z \
		-w /app \
		-p $port:8080 \
		${IMAGE} &
done
