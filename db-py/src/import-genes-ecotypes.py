#!/usr/bin/env/python

# import-genes-ecotypes.py
# Read data from a three-column .tsv: [gene_id \t length \t ecotype]
# Where first column is the gene_id, and the second column is its length in nucleotides, and the third column is its ecotype.
# Insert that data into ecotypes and genes mysql tables.

from mysql.connector import connect
import os, sys

GENE_ID_COL = 0
LENGTH_COL = 1
ECOTYPE_COL = 2

TABLE_NAME = 'genes'

def load_ecotypes(con):
    cur = con.cursor()
    cur.execute('SELECT id, name FROM ecotypes')
    ecotypes = {name: id for id, name in cur.fetchall()}
    cur.close()
    return ecotypes


def insert_ecotype(con, ecotype):
    cur = con.cursor()
    cur.execute('INSERT INTO ecotypes (name) VALUE (%s)', (ecotype,))
    id = cur.lastrowid
    con.commit()
    cur.close()
    return id


def main():
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

    # Fetch ecotypes as {name: id} from DB
    ecotypes = load_ecotypes(con) # name: id

    sql_values = []
    for line in open(filename, 'r'):
        record = line.strip().split('\t')

        # Verify ecotype, insert if needed
        ecotypeName = record[ECOTYPE_COL]
        if ecotypeName not in ecotypes.keys():
            ecotypeId = insert_ecotype(con, ecotypeName)
            ecotypes[ecotypeName] = ecotypeId
        else:
            ecotypeId = ecotypes[ecotypeName]

        # Three Columns:
        sql_values.append("(%s, %s, %s)" % (record[GENE_ID_COL], record[LENGTH_COL], ecotypes[ecotypeName]))

    sql = """
        INSERT INTO """+TABLE_NAME+"""
            (gene_id, length, ecotype_id)
            VALUES
        """ + ', '.join(sql_values)
    cur.execute(sql)
    con.commit()
    cur.close()
    print('Done.')


if __name__ == "__main__":
    main()
