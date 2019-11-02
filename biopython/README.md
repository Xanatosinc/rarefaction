# Biopython
Read in fasta files generated from anvio step from a fastas directory and generate one .tsv file with the read lengths and GC content associated with each gene / replicant, along with its contig and station.
Configure `config` file to set input (FASTA_DIR) and output (OUTPUT_DIR) directories.
Run `make build` to build the docker image
Run `make run` to run it.
