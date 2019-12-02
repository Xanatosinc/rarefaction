#!/usr/bin/env/python

# Map and insert ecotypes to the db, given a tsv with genotype, ecotype columns.
# Assume contigs' name up to its first '_' is the genotype.
# NOTE: This assumes that no ecotypes have been inserted into the db yet.

from mysql.connector import connect
import os, sys

if len(sys.argv) !=2:
    exit('Usage: map-ecotypes-to-contigs.py INPUT.tsv')

filename = sys.argv[1]

def insert_ecotype(con, ecotype):
    cur = con.cursor()
    cur.execute('INSERT INTO ecotypes (name) VALUE (%s)', (ecotype,))
    id = cur.lastrowid
    con.commit()
    cur.close()

    return id


def update_contig(con, contigId, ecotypeId):
    cur = con.cursor()
    cur.execute('UPDATE contigs SET ecotype_id = %s WHERE id = %s' % (ecotypeId, contigId))
    con.commit()
    cur.close()


# Connect to MySQL DB
con = connect(
    database=os.getenv('MYSQL_DB'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASS'),
)
cur = con.cursor()

# Process .tsv file
ecotypeGenotypeDict = {}
print('Processing '+filename)
for line in open(filename, 'r'):
    record = line.strip().split('\t')

    # key: genotype, value: ecotype
    ecotypeGenotypeDict[record[0]] = record[1]

# SELECT Contigs, execute UPDATEs / INSERTs
insertedEcotypes = {} # name => id
sys.stdout.write('Loading Contigs: ')
cur.execute('SELECT id, name FROM contigs')
for contigId, contigName in cur.fetchall():
    genotype = contigName.split('_')[0]
    if genotype in ecotypeGenotypeDict:
        ecotype = ecotypeGenotypeDict[genotype]
        if ecotype not in insertedEcotypes: # Ecotype not yet in db
            ecoId = insert_ecotype(con, ecotype)
            insertedEcotypes[ecotype] = ecoId
        else: # Ecotype already in db
            ecoId = insertedEcotypes[ecotype]
        update_contig(con, contigId, ecoId)
    else:
        print(genotype+' not in record dictionary')

