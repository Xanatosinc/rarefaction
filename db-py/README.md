# DB-Py

Docker container to run Python scripts to populate, then use, the database.
Run `make run` to enter into the container, then run the python scripts as given below.

## Populate

### Ecotypes, Genes

`python import-genes-ecotypes.py INPUT.TSV`
Read data from a three-column .tsv: [gene_id \t length \t ecotype]

Where first column is the gene_id, and the second column is its length in nucleotides, and the third column is its ecotype.

Inserts that data into `ecotypes` and `genes` mysql tables.


### Gene Reads
`python populate.py INPUT.TSV`

Script to populate mysql database with data from biopython output. Namely, the .tsv file containing the following columns:
`[gene_id]_[read_number]`
`Station`
`Sense`
`Contig_Name`
`Read_Length`
`GC_Content`

THIS SHOULD BE RUN AFTER POPULATING `ecotypes` AND `genes` TABLES.

The `gene_reads` and `stations` tables  found in the `mysql1` container will be populated with this script.

This assumes uniqueness across gene_id, read_number, and Station.

Run `make build` to build image, `make run` to run container with shell.

This .tsv file can be split into parts and consumed piecewise, for a large dataset this is recommended.

When splitting, use a bash for loop within the container to populate the db with the included python script, eg.:
`for file in $(ls /app/data/*) ; do python src/populate.py ${file} ; done`
Where /app/data maps to the directory defined in `config`, which contains the split .tsv files.


## Rarefy

`python rarefy.py ECOTYPE "rep1 rep2"`

NB: You can use `seq` to create a sequence of numbers, to serve as a list of replicants. eg.:
`time python src/rarefy.py HLII --r $(seq -w -s ' ' 01 30) --d 50000`

* (Sample depths defined in rarefy.py)

* ECOTYPE: The name of the ecotype to be run.

* rep#: Replication number. The list of replications is given as a quoted string on the command line, separated by spaces.
	Each replication number will be added to the end of each file.

Read the data from the database and generate a series of matrices, one per ecotype, showing the coverage for each gene at each station.

Each gene-station's coverage is an aggregate of a random subsample of gene reads, defined by a particular depth.

For each station in each ecotype, if the total number of station's reads is less than the current sample depth, it is skipped.

The files output by each call to this function appear in the output directory as: ECOTYPE_SAMPLEDEPTH_REPLICATION.tsv.
