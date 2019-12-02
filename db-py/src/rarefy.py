#!/usr/bin/env/python

# Pull data from database and calculate coverage per ecotype per station per gene.

from mysql.connector import connect
import os, pandas as pd, sys
import dask.dataframe as ddf

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

# Fetch stations
stations = {} # name => id
cur.execute('SELECT id, name FROM stations')
for stationId, stationName in cur.fetchall():
    stations[stationName] = stationId
    print(stationName)

#    df = pd.read_sql('''
#        SELECT gr.gene_id, gr.read_number, s.name, gr.read_length FROM gene_reads gr
#        LEFT JOIN stations s ON s.id = gr.station_id
#        LEFT JOIN contigs c ON c.id = gr.contig_id
#        LEFT JOIN ecotypes e ON e.id = c.ecotype_id
#        WHERE 1=1
#            AND e.name = '%s'
#            AND s.name = '%s'
#        ''' % (ECOTYPE, stationName),
#        con=con
#    )
    MYSQL_DB=os.getenv('MYSQL_DB')
    MYSQL_USER=os.getenv('MYSQL_USER')
    MYSQL_PASS=os.getenv('MYSQL_PASS')
    MYSQL_PORT=os.getenv('MYSQL_PORT')

    ddf_con_string = 'mysql://'+MYSQL_USER+':'+MYSQL_PASS+'@0.0.0.0:'+MYSQL_PORT+'/'+MYSQL_DB
    df = ddf.read_sql_table('gene_reads', ddf_con_string, index_col='id')
    print(df)
    exit()

