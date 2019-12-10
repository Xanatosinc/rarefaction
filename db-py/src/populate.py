#!/usr/bin/env python

# populate.py
# Connects to existing gene_reads database and inserts entries based on the data contained in
# an input.tsv file given as a commandline argument.
# Checks for presence of stations as it goes and inserts them as needed.
# NOTE: does not do this for genes (or ecotypes). Use import-genes-ecotypes.py first for that.

from mysql.connector import connect
import os, sys

POOL_SIZE = 100

# Establish order of table columns
GENE_READNUM_COL = 0
STATION_COL      = 1
READ_LEN_COL     = 4
GC_COL           = 5

# Print '.' or '+' for each Pool, depending on whether at least one row was inserted.
PROGRESS = 1

def insert_gene_reads(con, sqlValues):
    cur = con.cursor()
    sql = """
        INSERT IGNORE INTO gene_reads
            (gene_id, read_number, station_id, read_length, gc_content)
        VALUES
    """ + ', '.join(sqlValues)
    cur.execute(sql)
    if PROGRESS:
        if cur.lastrowid == 0:
            sys.stdout.write('.')
        else:
            sys.stdout.write('+')
    con.commit()
    cur.close()


def insert_station(con, station):
    cur = con.cursor()
    cur.execute('INSERT INTO stations (name) VALUE (%s)', (station,))
    id = cur.lastrowid
    con.commit()
    cur.close()
    return id


def load_genes(con):
    genes = {}


def load_stations(con):
    stations = {}
    cur = con.cursor()
    cur.execute('SELECT id, name FROM stations')
    for id, name in cur.fetchall():
        stations[name] = id # name: id
    return stations


def main():

    if len(sys.argv) != 2:
        exit('Usage: populate.py INPUT.TSV')

    filename = sys.argv[1]

    # Connect to MySQL DB
    con = connect(
        database=os.getenv('MYSQL_DB'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASS'),
    )

    # Load existing Stations into memory
    sys.stdout.write('Loading Stations: ')
    stations = load_stations(con)
    print("%s initial stations" % len(stations))

    # Process .tsv file
    print('Processing '+filename)
    sqlValues = []
    for line in open(filename, 'r'):
        record = line.strip().split('\t')
        geneReadNum = record[GENE_READNUM_COL].split('/')[-1]
        station = record[STATION_COL]
        (geneId, readNumber) = geneReadNum.split('_')
        readNumber = str(int(readNumber))

        # Check Station
        if station not in stations.keys():
            stations = load_stations(con)
            if station not in stations.keys():
                stationId = insert_station(con, station)
                stations[station] = stationId

        # Set stationId whether or not station was present
        stationId = stations[station]

        # gc_content can't be 100 in db
        if float(record[GC_COL]) == 100:
            record[GC_COL] = '99.9'

        sqlValues.append(
            "(%s, %s, %s, %s, %s)" % (
                geneId, readNumber, stationId, record[READ_LEN_COL], record[GC_COL]
            )
        )
        if len(sqlValues) == POOL_SIZE:
            summary = insert_gene_reads(con, sqlValues)
            sqlValues = []

    if len(sqlValues) != 0:
        insert_gene_reads(con, sqlValues)
    con.close()
    print()


if __name__ == "__main__":
    main()
