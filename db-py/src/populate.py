#!/usr/bin/env python

# populate.py
# Connects to existing gene_reads database and inserts entries based on the data contained in
# an input.tsv file given as a commandline argument.

from mysql.connector import connect
import os, sys

if len(sys.argv) != 2:
    exit('Usage: populate.py INPUT.TSV')

filename = sys.argv[1]

def load_stations(con):
    stations = {}
    cur = con.cursor()
    cur.execute('SELECT id, name FROM stations')
    for id, name in cur.fetchall():
        stations[name] = id
    return stations

def insert_station(con, station):
    cur = con.cursor()
    cur.execute('INSERT INTO stations (name) VALUE (%s)', (station,))
    id = cur.lastrowid
    con.commit()
    cur.close()
    return id

def load_contigs(con):
    contigs = {}
    cur = con.cursor()
    cur.execute('SELECT id, name FROM contigs')
    for id, name in cur.fetchall():
        contigs[name] = id
    return contigs

def insert_contig(con, contig):
    if (len(contig) > 191):
        print("WARNING: contig exceeds maximum character length. %s truncating to %s." % contig, contig[:191])
    cur = con.cursor()
    cur.execute('INSERT INTO contigs (name) VALUE (%s)', (contig,))
    id = cur.lastrowid
    con.commit()
    cur.close()
    return id

def main():
    # Connect to MySQL DB
    con = connect(
        database=os.getenv('MYSQL_DB'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASS'),
    )
    cur = con.cursor()

    records = []

    # Load existing Contigs into memory
    sys.stdout.write('Loading Contigs: ')
    contigs = load_contigs(con)
    print("%s initial contigs" % len(contigs))

    # Load existing Stations into memory
    sys.stdout.write('Loading Stations: ')
    stations = load_stations(con)
    print("%s initial stations" % len(stations))

    ## Load existing Records (from this file) into memory
    sys.stdout.write('Loading Records: ')
    for line in open(filename, 'r'):
        record = line.strip().split('\t')
        checkRecord = record[0].split('/')[-1]
        station = record[1]
        (geneId, readNumber) = checkRecord.split('_')
        readNumber  = str(int(readNumber))
        stationId = stations[station]
        records.append(str(geneId) + '_' + str(readNumber) + '_' + str(stationId))
    print("%s initial records" % len(records))

    # Process .tsv file
    print('Processing '+filename)
    buff = 0
    sqlValues = []
    for line in open(filename, 'r'):
        record = line.strip().split('\t')
        checkRecord = record[0].split('/')[-1]
        station = record[1]
        (geneId, readNumber) = checkRecord.split('_')
        readNumber = str(int(readNumber))

        # Check Station
        stationId = stations[station]
        if station not in stations.keys():
            stations = load_stations(con)
            if station not in stations.keys():
                stationId = insert_station(con, station)
                stations[station] = stationId
            else:
                stationId = stations[station]
        else:
            stationId = stations[station]

        # Check Record Index
        if geneId + '_' + readNumber + '_' + str(stations[station]) in records:
            continue
        records.append(str(geneId) + '_' + str(readNumber) + '_' + str(stationId))

        # Check Contig
        contig = record[3]
        if contig not in contigs.keys():
            contigs = load_contigs(con)
            if contig not in contigs.keys():
                contigId = insert_contig(con, contig)
                contigs[contig] = contigId
            else:
                contigId = contigs[contig]
        else:
            contigId = contigs[contig]

        # gc_content can't be 100 in db
        if float(record[5]) == 100:
            record[5] = '99.9'

        sqlValues.append(
            "(%s, %s, %s, %s, %s, %s)" % (
                geneId, readNumber, stationId, contigId, record[4], record[5]
            )
        )
        if buff == 999:
            sql = """
                INSERT INTO gene_reads
                    (gene_id, read_number, station_id, contig_id, read_length, gc_content)
                VALUES
            """ + ', '.join(sqlValues)
            cur.execute(sql)
            con.commit()
            sqlValues = []
            buff = 0
        else:
            buff += 1

    if buff != 0:
        sql = """
            INSERT INTO gene_reads
                (gene_id, read_number, station_id, contig_id, read_length, gc_content)
            VALUES
        """ + ', '.join(sqlValues)
        cur.execute(sql)
        con.commit()
    cur.close()
    con.close()
    print()

if __name__ == "__main__":
    main()
