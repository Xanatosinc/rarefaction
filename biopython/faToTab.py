#!/usr/bin/python
#Convert fasta to table 
#Usage: python faToTab.py test.fa

import string
import sys
import re

from Bio import SeqIO
from Bio.SeqUtils import GC


for record in SeqIO.parse(sys.argv[1], 'fasta'):
	line = str(sys.argv[1])+'_'+record.description
	lines = line.replace('|','\t').replace('.fa','').replace('sample_id:','').replace('sample_id:','').replace('reverse:','') .replace('contig_name:','') 
	print('{}\t{}\t{}'.format(lines, len(record.seq), GC(record.seq)))
