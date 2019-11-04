#!/usr/bin/env python

from mysql.connector import connect
import os, sys

if len(sys.argv) != 2:
    exit('Usage: populate.py INPUT.TSV')

filename = sys.argv[1]

def insert_station(con, station):
    cur = con.cursor()
    cur.execute('INSERT INTO stations (name) VALUE (%s)', (station,))
    id = cur.lastrowid
    con.commit()
    cur.close()

    return id

def insert_contig(con, contig):
    if (len(contig) > 191):
        print("WARNING: contig exceeds maximum character length. %s truncating to %s." % contig, contig[:191])
    cur = con.cursor()
    cur.execute('INSERT INTO contigs (name) VALUE (%s)', (contig,))
    id = cur.lastrowid
    con.commit()
    cur.close()

    return id

# Connect to MySQL DB
con = connect(
    database=os.getenv('MYSQL_DB'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASS'),
)
cur = con.cursor()

contigs = {}
stations = {}
records = []

# Load existing Contigs into memory
sys.stdout.write('Loading Contigs: ')
cur.execute('SELECT id, name from contigs')
for id, name in cur.fetchall():
    contigs[name] = id
print("%s initial contigs" % len(contigs))

# Load existing Stations into memory
sys.stdout.write('Loading Stations: ')
cur.execute('SELECT id, name FROM stations')
for id, name in cur.fetchall():
    stations[name] = id
print("%s initial stations" % len(stations))

# Load existing Records into memory
sys.stdout.write('Loading Records: ')
cur.execute('SELECT id, gene_id, read_number, station_id FROM gene_reads')
for id, geneId, readNumber, stationId in cur.fetchall():
    records.append(str(geneId) + '_' + str(readNumber) + '_' + str(stationId))
print("%s initial records" % len(records))

# Process .tsv file
print('Processing '+filename)
for line in open(filename, 'r'):
    record = line.strip().split('\t')
    checkRecord = record[0].split('/')[-1]
    station = record[1]
    (geneId, readNumber) = checkRecord.split('_')
    readNumber = str(int(readNumber))

    # Check Station
    if station not in stations.keys():
        stationId = insert_station(con, station)
        stations[station] = stationId
    else:
        stationId = stations[station]

    # Check Record Index
    if geneId + '_' + readNumber + '_' + str(stations[station]) in records:
        continue

    # Check Contig
    contig = record[3]
    if contig not in contigs.keys():
        contigId = insert_contig(con, contig)
        contigs[contig] = contigId
    else:
        contigId = contigs[contig]

    cur.execute("""
        INSERT INTO gene_reads
            (gene_id, read_number, station_id, contig_id, read_length, gc_content)
        VALUES
            (%s, %s, %s, %s, %s, %s)
        """, ( geneId, readNumber, stationId, contigId, record[4], record[5])
    )
    con.commit()
    records.append(str(geneId) + '_' + str(readNumber) + '_' + str(stationId))
cur.close()
con.close()
print()

