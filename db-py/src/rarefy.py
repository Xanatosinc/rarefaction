#!/usr/bin/env/python

# rarefy.py
#
# Pull data from database and calculate coverage per ecotype per station per gene.
# Stations that have a summed read_length less than the defined THRESHOLD value are ignored.

# NOTE: This version queries each depth, each station -- so it uses less memory, but is SLOWER.
# This should only be used on very large ecotypes, if the other version uses too much memory.

OUTPUT_DIR = '/app/output'
POOL_SIZE = 30

import argparse
from datetime import datetime as dt
from mysql.connector import connect
import os
import pandas as pd
from pathvalidate import (sanitize_filename as sfn, sanitize_filepath as sfp)
import pytz
import sys

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
    sys.stdout.write('\t[T+%s s]\t[^%s s]' % (
        str(totalElapsedSeconds).rjust(8, ' '),
        str(elapsedSinceStation).rjust(7, ' '),
    ))
    return stationTime

def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='''
        Pull data from database and calculate coverage per ecotype per station per gene.
        Ecotype-Stations that have gene reads less than the sample depth value are ignored.
        Since this involves a random sampling, these calculations will be performed multiple times, once per replicant.
    ''', usage='rarefy.py [-h] ECOTYPE --replicants REPLICANT [REPLICANT ...] --depths DEPTH [DEPTH ...]')
    parser.add_argument('ecotype', metavar='ECOTYPE',
            help='The ecotype to be analyzed')
    flag_req = parser.add_argument_group(title='required flag arguments')
    flag_req.add_argument('--replicants', required=True, metavar='REPLICANT', nargs='+',
            help='Series of replicant names used as file suffixes')
    flag_req.add_argument('--depths', required=True, metavar='DEPTH', type=int, nargs='+',
            help='Sample depths to be considered')

    args = parser.parse_args()

    # Check output directory
    if not (os.access(OUTPUT_DIR, os.W_OK) and os.path.isdir(OUTPUT_DIR)):
        exit('Problem with output directory %s. Ensure it exists and is writeable.' % OUTPUT_DIR)

    print('### %s ###' % args.ecotype)

    # Connect to MySQL DB
    con = connect(
        database=os.getenv('MYSQL_DB'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASS'),
    )
    cur = con.cursor()

    # Fetch ecotypes, verify input
    print('Fetching Ecotypes')
    cur.execute('SELECT id, name FROM ecotypes')
    ecotypes = {name: id for id, name in cur.fetchall()}

    if args.ecotype not in ecotypes:
        exit('Ecotype "%s" not found in database. Ecotypes found: %s' % (args.ecotype, ', '.join([*ecotypes])))

    ecotypeId = ecotypes[args.ecotype]

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
    for sampleDepth in args.depths:
        outputTables[sampleDepth] = {}
        for rep in args.replicants:
            outputTables[sampleDepth][rep] = pd.DataFrame(index=geneLengths.index)

    START_TIME = previousStationTime = dt.now(TZ)

    stationPool = {} # id: name
    stationsRunCount = 0
    sys.stdout.write('[%s]\n' % START_TIME)
    stationIndex = 0
    for stationId, stationName in stations.items():

        # Add to stationPool
        stationPool[stationId] = stationName

        # Perform calculations per station per depth, reset stationPool
        if (len(stationPool) == POOL_SIZE) or (stationsRunCount + len(stationPool) == len(stations)):
            df = dfFromQuery(con, ecotypeId, stationPool)

            for stationPoolId, stationPoolName in stationPool.items():
                stationIndex += 1

                # Print which station we're on
                sys.stdout.write('\n(%4d/%4d)' % (stationIndex, len(stations)))

                # Print out elapsed time information
                previousStationTime = printTimeInfo(START_TIME, previousStationTime)
                sys.stdout.write('\t%s' % stationPoolName.ljust(maxStationNameLength, ' '))

                # Do the calculating
                for sampleDepth in args.depths:

                    replicantDepthStation = populateOutputTable(
                        df, ecotypeId, sampleDepth, stationPoolId, stationPoolName, geneLengths, args.replicants
                    )

                    # Put the calculated values in our output tables
                    for replicant, stationSeries in replicantDepthStation.items():
                        outputTables[sampleDepth][replicant][stationPoolName] = stationSeries
                        del stationSeries

            del df
            stationsRunCount += len(stationPool)
            stationPool = {}

    print()
    for sampleDepth in args.depths:
        for replicant in args.replicants:
            fileOutName = sfp(
                OUTPUT_DIR + '/' + sfn(args.ecotype) + '_' + str(sampleDepth) + '_' + sfn(replicant) + '.tsv'
            )
            print('Writing to file: ' + fileOutName)
            fileOut = open(fileOutName, 'w')
            outputTables[sampleDepth][replicant].to_csv(fileOut, sep='\t')
        del outputTables[sampleDepth]

    del outputTables

    cur.close()
    con.close()

if __name__ == "__main__":
    main()
