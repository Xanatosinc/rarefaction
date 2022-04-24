#!/usr/bin/env/python

# rarefy.py
#
# Pull data from database and calculate coverage per ecotype per station per gene.
# Stations that have a summed read_length less than the defined THRESHOLD value are ignored.

# NOTE: This version queries each depth, each station -- so it uses less memory, but is SLOWER.
# This should only be used on very large ecotypes, if the other version uses too much memory.

import argparse
from datetime import datetime as dt
from mysql.connector import connect
import os
import pandas as pd
from pathvalidate import (sanitize_filename as sfn, sanitize_filepath as sfp)
import pytz
import sys

OUTPUT_DIR = '/app/output'
POOL_SIZE = 30
TZ = pytz.timezone('US/Pacific')


def df_from_query(con, ecotypeId, stationPool):
    station_ids_string = '(%s)' % ', '.join(str(x) for x in stationPool.keys())

    # Simpler query through genes table
    return pd.read_sql('''
        SELECT gr.gene_id, gr.station_id, gr.read_length FROM gene_reads gr
        LEFT JOIN genes g ON g.gene_id = gr.gene_id
        LEFT JOIN ecotypes e ON e.id = g.ecotype_id
        WHERE 1=1
            AND g.ecotype_id = %s
            AND gr.station_id IN %s
        ''' % (ecotypeId, station_ids_string),
                       con=con
                       )


def populate_output_table(df, ecotype_id, sample_depth, station_id, station_name, gene_lengths, replicants):
    output_series = {}
    for replicant in replicants:
        output_series[replicant] = pd.Series(index=gene_lengths.index)
        output_series[replicant].values[:] = 0
        station_df = df[df.station_id == station_id]
        station_read_count = len(station_df.index)

    del df

    # If stationReadCount < sampleDepth, zerofill the station
    if station_read_count < sample_depth:
        sys.stdout.write('\t!%s' % str(sample_depth))

        return output_series

    for replicant in replicants:
        # Random sampling of this station's gene_reads
        sample_df = station_df.sample(n=sample_depth)

        # Sums of the `read_length` column for each gene for this station
        gene_read_length_sums = sample_df.groupby('gene_id')['read_length'].sum().reset_index(name='sum') \
            .set_index('gene_id')

        # The number of gene_reads for this gene in this station
        unique_gene_count = sample_df['gene_id'].nunique()

        del sample_df

        # Join sums of read lengths with gene reference lengths, so it has two columns: sum and length
        grls = gene_read_length_sums.join(gene_lengths, how='right')
        grls.fillna(0, downcast='infer', inplace=True)

        del gene_read_length_sums

        # Populate the output dataframe's stationName column with the calculated coverage
        output_series[replicant] = grls['sum'] / grls['length']
        output_series[replicant] = output_series[replicant].round(4)

        del grls

    sys.stdout.write('\t %s' % str(sample_depth))

    return output_series


def print_time_info(start_time, prev_time):
    station_time = dt.now(TZ)
    total_elapsed_seconds = round((station_time - start_time).total_seconds())
    elapsed_since_station = round((station_time - prev_time).total_seconds(), 1)
    sys.stdout.write('\t[T+%s s]\t[^%s s]' % (
        str(total_elapsed_seconds).rjust(8, ' '),
        str(elapsed_since_station).rjust(7, ' '),
    ))
    return station_time


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='''
            Pull data from database and calculate coverage per ecotype per station per gene.
            Ecotype-Stations that have gene reads less than the sample depth value are ignored.
            Since this involves a random sampling, these calculations will be performed multiple times, once per
            replicant.
        ''',
        usage='rarefy.py [-h] ECOTYPE --replicants REPLICANT [REPLICANT ...] --depths DEPTH [DEPTH ...]'
    )
    parser.add_argument(
        'ecotype',
        metavar='ECOTYPE',
        help='The ecotype to be analyzed'
    )
    flag_req = parser.add_argument_group(title='required flag arguments')
    flag_req.add_argument(
        '--replicants',
        required=True,
        metavar='REPLICANT',
        nargs='+',
        help='Series of replicant names used as file suffixes'
    )
    flag_req.add_argument(
        '--depths',
        required=True,
        metavar='DEPTH',
        type=int,
        nargs='+',
        help='Sample depths to be considered'
    )

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

    ecotype_id = ecotypes[args.ecotype]

    # Length of genes based on reference sequence
    print('Fetching Gene Lengths')
    gene_lengths = pd.read_sql('SELECT gene_id, length FROM genes WHERE ecotype_id = %s' % ecotype_id, con=con) \
        .set_index('gene_id')

    # Fetch stations
    print('Fetching Stations')
    cur.execute('SELECT id, name FROM stations')
    stations = {id: name for id, name in cur.fetchall()}

    max_station_name_length = max(len(x) for x in stations.values())

    # Generate blank dataframes
    output_tables = {}
    for sample_depth in args.depths:
        output_tables[sample_depth] = {}
        for rep in args.replicants:
            output_tables[sample_depth][rep] = pd.DataFrame(index=gene_lengths.index)

    start_time = previous_station_time = dt.now(TZ)

    station_pool = {}  # id: name
    stations_run_count = 0
    sys.stdout.write('[%s]\n' % start_time)
    station_index = 0
    for station_id, station_name in stations.items():

        # Add to stationPool
        station_pool[station_id] = station_name

        # Perform calculations per station per depth, reset stationPool
        if (len(station_pool) == POOL_SIZE) or (stations_run_count + len(station_pool) == len(stations)):
            df = df_from_query(con, ecotype_id, station_pool)

            for station_pool_id, station_pool_name in station_pool.items():
                station_index += 1

                # Print which station we're on
                sys.stdout.write('\n(%4d/%4d)' % (station_index, len(stations)))

                # Print out elapsed time information
                previous_station_time = print_time_info(start_time, previous_station_time)
                sys.stdout.write('\t%s' % station_pool_name.ljust(max_station_name_length, ' '))

                # Do the calculating
                for sample_depth in args.depths:

                    replicant_depth_station = populate_output_table(
                        df, ecotype_id, sample_depth, station_pool_id, station_pool_name, gene_lengths, args.replicants
                    )

                    # Put the calculated values in our output tables
                    for replicant, station_series in replicant_depth_station.items():
                        output_tables[sample_depth][replicant][station_pool_name] = station_series
                        del station_series
            del df
            stations_run_count += len(station_pool)
            station_pool = {}

    print()
    for sample_depth in args.depths:
        for replicant in args.replicants:
            file_out_name = sfp(
                OUTPUT_DIR + '/' + sfn(args.ecotype) + '_' + str(sample_depth) + '_' + sfn(replicant) + '.tsv'
            )
            print('Writing to file: ' + file_out_name)
            file_out = open(file_out_name, 'w')
            output_tables[sample_depth][replicant].to_csv(file_out, sep='\t')
        del output_tables[sample_depth]

    del output_tables

    cur.close()
    con.close()


if __name__ == '__main__':
    main()
