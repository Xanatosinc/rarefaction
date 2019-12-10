#!/usr/bin/env/python

# rarefy.py
#
# Pull data from database and calculate coverage per ecotype per station per gene.
# Stations that have a summed read_length less than the defined THRESHOLD value are ignored.

# NOTE: This version queries each depth, each station -- so it uses less memory, but is SLOWER.
# This should only be used on very large ecotypes, if the other version uses too much memory.

# Number of gene_reads randomly sampled per station per ecotype
DEPTHS = [10000, 25000, 50000, 75000, 100000]

POOL_SIZE = 50

import multiprocessing as mp
from datetime import datetime as dt
from mysql.connector import connect
import os, pandas as pd, sys
import pytz

TZ = pytz.timezone('US/Pacific')

def dfFromQuery(con, ecotypeId, stationPool):
    stationIdsString = '(%s)' % ', '.join(str(x) for x in stationPool.keys())

    # Simpler query through genes table
    return pd.read_sql('''
        SELECT gr.gene_id, gr.station_id, gr.read_length FROM gene_reads gr
        LEFT JOIN genes g ON g.gene_id = gr.gene_id
        LEFT JOIN ecotypes e ON e.id = g.ecotype_id
        WHERE 1=1
            AND g.ecotype_id = %s
            AND gr.station_id IN %s
        ''' % (ecotypeId, stationIdsString),
        con=con
    )

def populateOutputTable(df, ecotypeId, sampleDepth, stationId, stationName, geneLengths, replicants):

    outputSeries = {}
    for replicant in replicants:
        outputSeries[replicant] = pd.Series(index=geneLengths.index)
        outputSeries[replicant].values[:] = 0
        stationDf = df[df.station_id == stationId]
        stationReadCount = len(stationDf.index)

    del df

    # If stationReadCount < sampleDepth, zerofill the station
    if stationReadCount < sampleDepth:
        sys.stdout.write('\t!%s' % str(sampleDepth))

        return outputSeries

    for replicant in replicants:
        # Random sampling of this station's gene_reads
        sampleDf = stationDf.sample(n = sampleDepth)

        # Sums of the `read_length` column for each gene for this station
        geneReadLengthSums = sampleDf.groupby('gene_id')['read_length'].sum().reset_index(name = 'sum').set_index('gene_id')

        # The number of gene_reads for this gene in this station
        uniqueGeneCount = sampleDf['gene_id'].nunique()

        del sampleDf

        # Join sums of read lengths with gene reference lengths, so it has two columns: sum and length
        grls = geneReadLengthSums.join(geneLengths, how='right')
        grls.fillna(0, downcast='infer', inplace=True)

        del geneReadLengthSums

        # Populate the output dataframe's stationName column with the calculated coverage
        outputSeries[replicant] = grls['sum'] / grls['length']
        outputSeries[replicant] = outputSeries[replicant].round(4)

        del grls

    sys.stdout.write('\t %s' % str(sampleDepth))

    return outputSeries

def printTimeInfo(startTime, prevTime):
    stationTime = dt.now(TZ)
    totalElapsedSeconds = round((stationTime - startTime).total_seconds())
    elapsedSinceStation = round((stationTime - prevTime).total_seconds(), 1)
    sys.stdout.write('\n[T+%s s]\t[^%s s]' % (
        str(totalElapsedSeconds).rjust(8, ' '),
        str(elapsedSinceStation).rjust(7, ' '),
    ))
    return stationTime

def main():
    if len(sys.argv) not in (2, 3):
        exit('Usage: rarefy.py ECOTYPE')

    ECOTYPE = sys.argv[1]
    OUTPUT_DIR = '/app/output'

    # If second argument is given, use as suffixes for file name (eg. "a", "a b", etc.)
    REPLICANTS = sys.argv[2].split(' ') if len(sys.argv) == 3 else ''

    if not (os.access(OUTPUT_DIR, os.W_OK) and os.path.isdir(OUTPUT_DIR)):
        exit('Problem with output directory %s. Ensure it exists and is writeable.' % OUTPUT_DIR)


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
        exit('Ecotype "%s" not found in database. Ecotypes found: %s' % (ECOTYPE, ', '.join([*ecotypes])))

    ecotypeId = ecotypes[ECOTYPE]

    # Length of genes based on reference sequence
    print('Fetching Gene Lengths')
    geneLengths = pd.read_sql('SELECT gene_id, length FROM genes WHERE ecotype_id = %s' % ecotypeId, con=con).set_index('gene_id')

    # Fetch stations
    print('Fetching Stations')
    cur.execute('SELECT id, name FROM stations')
    stations = {id: name for id, name in cur.fetchall()}

    maxStationNameLength = max(len(x) for x in stations.values())

    # Generate blank dataframes
    outputTables = {}
    for sampleDepth in DEPTHS:
        outputTables[sampleDepth] = {}
        for rep in REPLICANTS:
            outputTables[sampleDepth][rep] = pd.DataFrame(index=geneLengths.index)

    START_TIME = previousStationTime = dt.now(TZ)

    stationPool = {} # id: name
    stationsRunCount = 0
    sys.stdout.write('[%s]\n' % START_TIME)
    for stationId, stationName in stations.items():

        # Add to stationPool
        stationPool[stationId] = stationName

        # Perform calculations per station per depth, reset stationPool
        if (len(stationPool) == POOL_SIZE) or (stationsRunCount + len(stationPool) == len(stations)):
            df = dfFromQuery(con, ecotypeId, stationPool)

            for stationPoolId, stationPoolName in stationPool.items():

                # Print out elapsed time information
                previousStationTime = printTimeInfo(START_TIME, previousStationTime)
                sys.stdout.write('\t%s' % stationPoolName.ljust(maxStationNameLength, ' '))

                # Do the calculating
                for sampleDepth in DEPTHS:

                    replicantDepthStation = populateOutputTable(
                        df, ecotypeId, sampleDepth, stationPoolId, stationPoolName, geneLengths, REPLICANTS
                    )
                    for replicant, stationSeries in replicantDepthStation.items():
                        outputTables[sampleDepth][replicant][stationPoolName] = stationSeries
                        del stationSeries

            del df
            stationsRunCount += len(stationPool)
            stationPool = {}

    print()
    for sampleDepth in DEPTHS:
        for replicant in REPLICANTS:
            fileOutName = OUTPUT_DIR + '/' + ECOTYPE + '_' + str(sampleDepth) + '_' + replicant + '.tsv'
            print('Writing to file: ' + fileOutName)
            fileOut = open(fileOutName, 'w')
            outputTables[sampleDepth][replicant].to_csv(fileOut, sep='\t')
        del outputTables[sampleDepth]

    del outputTables

    cur.close()
    con.close()

if __name__ == "__main__":
    main()
