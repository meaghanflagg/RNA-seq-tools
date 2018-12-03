#!/usr/bin/env python

'''
#Author: Meaghan Flagg
#September 28, 2018
#Harvard University

#Script for subsampling FASTQ files, built on HTSeq library
#Dependencies:
#HTSeq

'''
from __future__ import division
import random, HTSeq, argparse, sys, gzip

parser = argparse.ArgumentParser()

parser.add_argument("r1", help="path to fastq file for read 1 (or single end reads)")
parser.add_argument("r2", nargs='?', default=None, help="path to fastq file for read 2 (paired end mode)")
parser.add_argument("out_r1", help="output filename for subsampled r1 (or single end) reads")
parser.add_argument("out_r2", nargs='?', help="output filename for subsampled r2 reads")

group=parser.add_mutually_exclusive_group()
group.add_argument("-percent", type=int, help="the percentage (as an integer) of original reads to return")
group.add_argument("-n_reads", type=int, help="the number of subsampled reads to return. Note, this must be less than the total number of reads in r1/r2")

args=parser.parse_args()

# count number of reads:
#### could clean up handling zipped files ####
def read_count(filepath):
    n_reads=0
    if filepath.endswith('gz'):
        with gzip.open(filepath) as f:
            for line in f:
                if line.startswith('@'): # count lines starting with '@' so extra newlines at the end don't throw off the read count
                    n_reads=n_reads+1
    else:
        with open(filepath) as f:
            for line in f:
                if line.startswith('@'):
                    n_reads=n_reads+1
    return n_reads


n_reads_r1=read_count(args.r1)


# read in fastq file:
fastq_r1 = HTSeq.FastqReader(args.r1)
#n_reads_r1=len(list(fastq_r1))         # this was accurate, but way too memory intensive for large fastqs.


PAIRED_END=False    # default is to process single-end reads

if args.r2:
    fastq_r2=HTSeq.FastaReader(args.r2)
    PAIRED_END=True

    #n_reads_r2=len(list(fastq_r2))
    n_reads_r2=read_count(args.r2)
    if not n_reads_r1 == n_reads_r2: sys.exit("r1 and r2 have different read counts!")

# determine how many reads to return:
if args.percent:
    n_reads_to_return = int(round(n_reads_r1 * args.percent / 100))
elif args.n_reads:
    if args.n_reads >= n_reads_r1: sys.exit("The number of reads requested for resampling is greater than or equal to the total number of reads!")
    n_reads_to_return = args.n_reads

# generate set of record "indexes" to grab reads at random:
# random.sample is sampling without replacement
record_indexes=random.sample(xrange(0,n_reads_r1),n_reads_to_return)

while len(set(record_indexes)) < len(record_indexes):   # make sure none of the elements are duplicated
    record_indexes=random.sample(xrange(0,n_reads_r1),n_reads_to_return)

# iterate throught the fastq file and grab the appropriate lines:

with open(args.out_r1, 'w') as r1_out:
    record_number=0     # initialize a counter to keep track of what line we're on
    for record in fastq_r1:
        if record_number in record_indexes:
            record.write_to_fastq_file(r1_out)
        record_number=record_number + 1

if PAIRED_END == True:
    if not args.out_r2: sys.exit("Please provide an output filename for subsampled r2 reads.")
    
    with open(args.out_r2, 'w') as r2_out:
        record_number=0     # initialize a counter to keep track of what line we're on
        for record in fastq_r2:
            if record_number in record_indexes:
                record.write_to_fastq_file(r2_out)
            record_number=record_number + 1
    