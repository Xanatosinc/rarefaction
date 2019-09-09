# Rarefaction

* anvio: Run Anvio docker containers in parallel. Currently used to map short reads to gene lists. Generates series of fasta files, one per gene.

* biopython: Read in fasta files generated from anvio step from a fastas directory and generate one .tsv file with the read lengths and GC content associated with each gene / replicant, along with its contig and station.

* mysql: Runs a mysql server container and generates a database designed for performing rarefaction on the data arranged in the biopython step.
