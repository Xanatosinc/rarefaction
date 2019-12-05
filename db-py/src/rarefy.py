#!/usr/bin/env/python

# rarefy.py
# Pull data from database and calculate coverage per ecotype per station per gene.
# Stations that have a summed read_length less than the defined THRESHOLD value are ignored.

# Number of gene_read records per station per ecotype required for consideration
STATION_READ_MIN = 0 # TODO: Deprecated

# Number of gene_reads randomly sampled per station per ecotype
DEPTHS = [10000, 25000, 50000, 75000, 100000]
#DEPTHS = [1000]

import multiprocessing as mp
from mysql.connector import connect
import os, pandas as pd, sys


def populateOutputTable(df, sampleDepth, stationName, geneLengths):
#    print(stationName)

    outputSeries = pd.Series(index=geneLengths.index)
    outputSeries.values[:] = 0
    stationDf = df[df.station_name == stationName]
    stationReadCount = len(stationDf.index)

    # If stationReadCount < sampleDepth, zerofill the station
    if stationReadCount < sampleDepth:
        print('Station %s had fewer reads than sampleDepth\t(%s)' % (stationName, str(sampleDepth)))

        return outputSeries

    # Random sampling of this station's gene_reads
    sampleDf = stationDf.sample(n = sampleDepth)

    # Sums of the `read_length` column for each gene for this station
    geneReadLengthSums = sampleDf.groupby('gene_id')['read_length'].sum().reset_index(name = 'sum').set_index('gene_id')

    # The number of gene_reads for this gene in this station
    uniqueGeneCount = sampleDf['gene_id'].nunique()

    # Join sums of read lengths with gene reference lengths, so it has two columns: sum and length
    grls = geneReadLengthSums.join(geneLengths, how='right')
    grls.fillna(0, downcast='infer', inplace=True)

    # Populate the output dataframe's stationName column with the calculated coverage
    outputSeries = grls['sum'] / grls['length']
    outputSeries = outputSeries.round(4)

#    print('summary data for ' + stationName)
#    print(outputSeries[outputSeries != 0])

    return outputSeries


def main():
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

    ecotypeId = ecotypes[ECOTYPE]

    # Fetch data
    print('Fetching joined gene_reads data')
    df = pd.read_sql('''
        SELECT gr.gene_id, s.name station_name, gr.read_length FROM gene_reads gr
        LEFT JOIN genes g ON g.gene_id = gr.gene_id
        LEFT JOIN stations s ON s.id = gr.station_id
        LEFT JOIN contigs c ON c.id = gr.contig_id
        LEFT JOIN ecotypes e ON e.id = c.ecotype_id
        WHERE 1=1
            AND e.name = '%s'
            AND g.ecotype_id = '%s'
        ''' % (ECOTYPE, ecotypeId),
        con=con
    )

    # Length of genes based on reference sequence
    print('Fetching Gene Lengths')
    geneLengths = pd.read_sql('SELECT gene_id, length FROM genes', con=con).set_index('gene_id')

    # Output for this script: genes x stations
    outputTables = {}
    for sampleDepth in DEPTHS:
        outputTables[sampleDepth] = pd.DataFrame(index=geneLengths.index)

    # Fetch stations
    cur.execute('SELECT id, name FROM stations')
    stations = {id: name for id, name in cur.fetchall()}

    cur.close()
    con.close()

    for sampleDepth in DEPTHS:
        print('\n###############\nDepth: %s\n###############\n' % str(sampleDepth))

        outputTable = pd.DataFrame(index=geneLengths.index)

#        with mp.Pool(16) as pool:
#
#            results = [pool.apply(populateOutputTable, args=(df, sampleDepth, stationName, geneLengths)) for stationName in stations.values()]
#            outputTable = pd.concat(results)

        for stationId, stationName in stations.items():
            outputTable[stationName] = populateOutputTable(df, sampleDepth, stationName, geneLengths)

        fileOutName = OUTPUT_DIR + '/' + ECOTYPE + '_' + str(sampleDepth) + '.tsv'
        print('Writing to file: ' + fileOutName)
        print(outputTable)
#        print(
#            outputTable[(outputTable.T != 0).all()] # This is slow
#        )
        fileOut = open(fileOutName, 'w')
        outputTable.to_csv(fileOut, sep='\t')
        del outputTable

if __name__ == "__main__":
    main()
