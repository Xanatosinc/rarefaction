#!/bin/bash

IMAGE="anvio-parallel"

if [ ! -f ./config ]; then
	echo "config file not present"
	exit 1
fi

# Import config variables
. config

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

port_offest=0
for gene_list in $(ls $GENE_LIST_DIR)
do
	port=$((port_offset+${STARTING_PORT}))
	((port_offset++))
	docker run \
		--name ${gene_list} \
		-v ${GENE_LIST_DIR}/${gene_list}:/app/gene_list:z \
		-v ${BAMS_DIR}:/app/bams:z \
		-v ${DB}:/app/db.db:z \
		-v ${OUTPUT_DIR}:/output:z \
		-w /app \
		-p $port:${CONTAINER_PORT} \
		${IMAGE} &
done
