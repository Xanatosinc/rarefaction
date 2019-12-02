#!/usr/bin/env/python

# import-gene-ref-lengths.py
# Read data from a two-column .tsv: [gene_id \t length]
# Where first column is the gene_id, and the second column is its length in nucleotides
# Insert that data into gene_ref_lengths table.

from mysql.connector import connect
import os, sys

if len(sys.argv) != 2:
    exit('Usage: import-gene-ref-lengths.py INPUT.tsv')

filename = sys.argv[1]

# Connect to MySQL DB

con = connect(                              
    database=os.getenv('MYSQL_DB'),         
    user=os.getenv('MYSQL_USER'),           
    password=os.getenv('MYSQL_PASS'),       
    )                                           
cur = con.cursor()                          

sql_values = []
print('Processing '+filename)
for line in open(filename, 'r'):
    record = line.strip().split('\t')

    sql_values.append("(%s, %s)" % (record[0], record[1]))

sql = """
    INSERT INTO gene_ref_lengths
        (gene_id, length)
        VALUES
    """ + ', '.join(sql_values)
cur.execute(sql)
con.commit()
cur.close()
print('Done.')
