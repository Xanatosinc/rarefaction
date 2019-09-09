Map Short Reads to Genes in Parallel

get-short-reads-mapping-to-a-gene

Files:

* Gene Lists Directory: Identified single copy core genes arranged into multiple files. The number of gene list files will determine how many containers will be run in parallel.
* Bam Files Direcotry: .bam files generated by bowtie
* DB File: .db file generated by anvio (anvi-gen-contigs database -> .db file)

```bash
make build
```
Generates paranvio image with anvio docker layer and the entrypoint shell script, with the actual anvio command.

```bash
run.sh
```
Runs the bash for loop that creates a series of docker containers, each running anvio. Each container uses one gene list file. run.sh uses shell variables to define the location of the files listed above, as well as an output directory.