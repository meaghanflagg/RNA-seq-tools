#!/usr/bin/env python

#SBATCH -n 1                    # number of cores requested
#SBATCH -t 10                   # runtime in minutes. Can also use HH:MM:SS or D-HH:MM:SS
#SBATCH -p short                # submit to 'short' partition
#SBATCH --mem 1G

import os, fnmatch, re, sys, subprocess, argparse, time, sys

parser=argparse.ArgumentParser()
parser.add_argument("-arg1")
parser.add_argument("-arg2")

args=parser.parse_args()

#print " ".join(sys.argv[1:].insert(0,__file__))

#print sys.argv[1:].insert(0,__file__)

arglist=sys.argv[1:]
arglist.insert(0,__file__)

print "__file__ :"" ".join(arglist)
print " ".join(sys.argv)

