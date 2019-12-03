#!/usr/bin/env/python

# rarefy.py
# Pull data from database and calculate coverage per ecotype per station per gene.
# Stations that have a summed read_length less than the defined THRESHOLD value are ignored.

# Number of gene_read records per station per ecotype required for consideration
STATION_READ_MIN = 10000

# Number of gene_reads randomly sampled per station per ecotype
DEPTHS = (10000, 25000, 50000, 75000, 100000)

from mysql.connector import connect
import os, pandas as pd, sys

if len(sys.argv) != 2:
    exit('Usage: rarefy.py ECOTYPE')

ECOTYPE = sys.argv[1]
OUTPUT_DIR = '/app/output'

if not (os.access(OUTPUT_DIR, os.W_OK) and os.path.isdir(OUTPUT_DIR)):
    exit('Problem with output directory ' + OUTPUT_DIR + '. Ensure it exists and is writeable.')

# Connect to MySQL DB
con = connect(
    database=os.getenv('MYSQL_DB'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASS'),
)
cur = con.cursor()

# Fetch ecotypes, verify input
ecotypes = {} # name => id
cur.execute('SELECT id, name FROM ecotypes')
for ecotypeId, ecotypeName in cur.fetchall():
    ecotypes[ecotypeName] = ecotypeId
if ECOTYPE not in ecotypes:
    exit('Ecotype ' + ECOTYPE + ' not found in database. Ecotypes found: ' + ecotypes.keys().join(', '))

# Fetch data
print('fetching joined gene_reads data')
df = pd.read_sql('''
    SELECT gr.gene_id, gr.read_number, s.name station_name, gr.read_length FROM gene_reads gr
    LEFT JOIN stations s ON s.id = gr.station_id
    LEFT JOIN contigs c ON c.id = gr.contig_id
    LEFT JOIN ecotypes e ON e.id = c.ecotype_id
    WHERE 1=1
        AND e.name = '%s'
    ''' % (ECOTYPE),
    con=con
)

# Length of genes based on reference sequence
geneLengths = pd.read_sql('SELECT gene_id, length FROM gene_ref_lengths', con=con).set_index('gene_id')

# Output for this script: genes x stations
outputTables = {}
for sampleDepth in DEPTHS:
    outputTables[sampleDepth] = pd.DataFrame(index=geneLengths.index)

print('Iterating through stations')

# Fetch stations
cur.execute('SELECT id, name FROM stations')
for stationId, stationName in cur.fetchall():

    print(stationName)

    stationDf = df[df.station_name == stationName]

    stationReadCount = len(stationDf.index)

    if (stationReadCount > STATION_READ_MIN):
        for sampleDepth in DEPTHS:

            # If stationReadCount < sampleDepth, zerofill the station
            if stationReadCount < sampleDepth:
                print('station had fewer than sampleDepth (' + sampleDepth + ') reads')
                outputTables[sampleDepth][stationName] = 0
                break

            # Random sampling of this station's gene_reads
            sampleDf = stationDf.sample(n = sampleDepth)

            # Sums of the read_length for each gene for this station
            geneReadLengthSums = sampleDf.groupby('gene_id')['read_length'].sum().reset_index(name = 'sum').set_index('gene_id')

            # The number of gene_reads for this gene in this station
            uniqueGeneCount = sampleDf['gene_id'].nunique()

            # Join sums of read lengths with gene reference lengths, so it has two columns: sum and length
            grls = geneReadLengthSums.join(geneLengths, how='right')
            grls.fillna(0, downcast='infer', inplace=True)

            # Populate the output dataframe's stationName column with the calculated coverage
            outputTables[sampleDepth][stationName] = grls['sum'] / grls['length']
            outputTables[sampleDepth] = outputTables[sampleDepth].round(4)
#            print('summary data for ' + stationName)
#            print(outputTables[sampleDepth].dropna(subset=[stationName])[stationName])

    # If station's read count is less than threshold, zerofill
    else:
        print('Station had fewer reads than threshold')
        outputTables[sampleDepth][stationName] = 0

cur.close()
con.close()

for sampleDepth in DEPTHS:
    fileOutName = OUTPUT_DIR + '/' + ECOTYPE + '_' + str(sampleDepth) + '.tsv'
    print('Writing to file ' + fileOutName)
    fileOut = open(fileOutName, 'w')
    outputTables[sampleDepth].to_csv(fileOut, sep='\t')
