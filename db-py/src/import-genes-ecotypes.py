#!/usr/bin/env/python

# import-genes-ecotypes.py
# Read data from a three-column .tsv: [gene_id \t length \t ecotype]
# Where first column is the gene_id, and the second column is its length in nucleotides, and the third column is its ecotype.
# Insert that data into `ecotypes` and `genes` mysql tables.

import argparse
from mysql.connector import connect
import os, sys

GENE_ID_COL = 0
LENGTH_COL = 1
ECOTYPE_COL = 2

ECOTYPES_TABLE_NAME = 'ecotypes'
GENES_TABLE_NAME = 'genes'

def load_ecotypes(con):
    cur = con.cursor()
    cur.execute('SELECT id, name FROM %s' % ECOTYPES_TABLE_NAME)
    ecotypes = {name: int(id) for id, name in cur.fetchall()}
    cur.close()
    return ecotypes


def load_genes(con):
    cur = con.cursor()
    cur.execute('SELECT gene_id FROM %s' % GENES_TABLE_NAME)
    genes = [ int(gene[0]) for gene in cur.fetchall() ]
    cur.close()
    return genes


def insert_ecotype(con, ecotype):
    cur = con.cursor()
    cur.execute('INSERT INTO %s (name) VALUE (%s)' % (ECOTYPES_TABLE_NAME, ecotype))
    id = cur.lastrowid
    con.commit()
    cur.close()
    return id


def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='''
        Read data from a three-column .tsv: [gene_id \\t length \\t ecotype]
        Where first column is the gene_id, and the second column is its length
        in nucleotides, and the third column is its ecotype.
        Insert that data into `ecotypes` and `genes` mysql tables.
    ''', usage='import-genes-ecotypes.py [-h] [-f] INPUT.tsv')
    parser.add_argument('input_filename', metavar='INPUT.tsv',
            help='The 3-column input.tsv')
    parser.add_argument('-f', action='store_true',
            help='UPDATE existing db entries. Otherwise INSERT IGNORE.')

    args = parser.parse_args()

    filename = args.input_filename
    force_update = args.f

    # Check input file
    if not (os.access(filename, os.R_OK)):
        exit('Problem with input file %s. Ensure it exists and is readable.' % filename)

    # Connect to MySQL DB
    con = connect(
        database=os.getenv('MYSQL_DB'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASS'),
        )
    cur = con.cursor()

    # Fetch ecotypes as {name: id,} from DB
    sys.stdout.write('Loading ecotypes: ')
    ecotypes = load_ecotypes(con) # name: id
    sys.stdout.write('%s ecotypes currently exist in the DB.\n' % len(ecotypes.keys()))

    # Fetch genes as (gene_id,) from DB
    sys.stdout.write('Loading genes: ')
    genes = load_genes(con)
    sys.stdout.write('%s genes currently exist in the DB.\n' % len(genes))

    # entries formatted for insertion to db
    sql_insert_values = []
    sql_update_values = []
    # keep track of a unique list of genes found in records
    genes_found_in_file = {}
    warn_flag = 0
    for line in open(filename, 'r'):
        items = line.strip().split('\t')
        record = {}
        record['gene_id'] = int(items[GENE_ID_COL])
        record['length'] = int(items[LENGTH_COL])
        record['ecotypeName'] = items[ECOTYPE_COL]

        # Verify ecotype, insert if needed
        if record['ecotypeName'] not in ecotypes.keys():
            print('Ecotype %s not found. Inserting into DB.' % record['ecotypeName'])
            ecotypeId = insert_ecotype(con, record['ecotypeName'])
            ecotypes[record['ecotypeName']] = ecotypeId
        else:
            ecotypeId = ecotypes[record['ecotypeName']]

        # Check if the current matches a gene_id already found in the file
        if (record['gene_id'] not in genes_found_in_file.keys()):
            genes_found_in_file[record['gene_id']] = 1

            # Check if the current record being read matches a gene already in the DB
            if (record['gene_id'] not in genes):

                # Three Columns:
                sql_insert_values.append('(%s, %s, %s)' % (record['gene_id'], record['length'], ecotypeId))

            # Current record matches an existing entry. If force_update is set, add to UPDATE list.
            elif (force_update):
                sql_update_values.append('(%s, %s, %s)' % (record['gene_id'], record['length'], ecotypeId))

        # This gene_id exists elsewhere in the file
        else:
            genes_found_in_file[record['gene_id']] += 1
            warn_flag = 1

    if (warn_flag):
        duplicate_genes = [k for (k, v) in genes_found_in_file.items() if v > 1]
        print("WARNING: %s duplicate `gene_id`s found in %s." % (len(duplicate_genes), filename))

    print('%s records to be inserted in the DB.' % len(sql_insert_values))
    if (force_update):
        print('%s records to be updated in the DB.' % len(sql_update_values))

    if (len(sql_insert_values) == 0 and len(sql_update_values) == 0):
        print('Nothing to be done!')
        exit()

    if (len(sql_insert_values)):
        print("Inserting.")
        insert_sql = """
            INSERT INTO """ + GENES_TABLE_NAME + """
                (gene_id, length, ecotype_id)
                VALUES
            """ + ', '.join(sql_insert_values)
        cur.execute(insert_sql)

    if (force_update and len(sql_update_values)):
        print("Updating.")
        update_sql = """
            INSERT INTO """ + GENES_TABLE_NAME + """
            (gene_id, length, ecotype_id)
            VALUES
        """ + ', '.join(sql_update_values) + """
        ON DUPLICATE KEY UPDATE length=VALUES(length), ecotype_id=VALUES(ecotype_id)
        """
        cur.execute(update_sql)
    con.commit()
    cur.close()
    print('Done.')


if __name__ == "__main__":
    main()
