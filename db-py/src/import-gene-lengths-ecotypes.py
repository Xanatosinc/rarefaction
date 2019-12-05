#!/usr/bin/env/python

# import-gene-lengths-ecotype.py
# Read data from a two-column .tsv: [gene_id \t length]
# Where first column is the gene_id, and the second column is its length in nucleotides
# Insert that data into gene_ref_lengths table.
# NOTE: This needs to be run *after* ecotypes table is populated with ALL relevant ecotypes

from mysql.connector import connect
import os, sys

if len(sys.argv) != 2:
    exit('Usage: import-gene-ref-lengths.py INPUT.tsv')

filename = sys.argv[1]

GENE_ID_COL = 0
LENGTH_COL = 1
ECOTYPE_COL = 2

TABLE_NAME = 'genes'

# Connect to MySQL DB

con = connect(
    database=os.getenv('MYSQL_DB'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASS'),
    )
cur = con.cursor()

# Fetch ecotypes as {name: id} from DB
cur.execute("SELECT id, name FROM ecotypes")
ecotypes = {name: id for id, name in cur.fetchall()}

sql_values = []
for line in open(filename, 'r'):
    record = line.strip().split('\t')

    # Three Columns:
    sql_values.append("(%s, %s, %s)" % (record[GENE_ID_COL], record[LENGTH_COL], ecotypes[record[ECOTYPE_COL]]))

sql = """
    INSERT INTO """+TABLE_NAME+"""
        (gene_id, length, ecotype_id)
        VALUES
    """ + ', '.join(sql_values)
print(sql[:1000])
cur.execute(sql)
con.commit()
cur.close()
print('Done.')
