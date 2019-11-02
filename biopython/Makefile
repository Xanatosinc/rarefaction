include config

build:
	docker build -t biopy-rare .

config: 
	if [ ! -f ./config ]; then \
		echo "config not found" exit 1 \
	fi

run: config
	docker run --rm -d \
		-v ${FASTA_DIR}:/fastas:Z \
		-v ${OUTPUT_DIR}:/output:Z \
		biopy-rare:latest 
