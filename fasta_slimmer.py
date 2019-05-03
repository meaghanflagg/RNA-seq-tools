#!/usr/bin/env python

####TODO:
#add random sampling


###this script takes first X percentage (or number) of reads in fasta file, creates new (smaller) fasta file.
from __future__ import division
import argparse

parser=argparse.ArgumentParser()

parser.add_argument("-input", type=str, help="enter input fasta filename")
parser.add_argument("-P", type=int, help="enter percentage of reads to write to new file")
parser.add_argument("-N", type=int, help="number of reads to keep")
parser.add_argument("-out", type=str, help="enter output filename")
parser.add_argument("-fq", action='store_true', help="indicates fastq input")

args=parser.parse_args()
if args.fq:
    readID='@'
    divider=4
else:
    readID='>'
    divider=2



f1=open(args.input,'r')
f2=open(args.out,'w')
lines=f1.readlines()
readsnum=len(lines)/divider
f1.close()
f3=open(args.input,'r')

if args.P:    
    keepreads=int(readsnum*(args.P/100))    #calculates number of reads to keep
if args.N:
    keepreads=args.N


counter=0

for line in f3:
    if line.startswith(readID):
        counter=counter+1
        f2.write(line)
    else:
        f2.write(line)
    
    if counter >= keepreads:
        break
