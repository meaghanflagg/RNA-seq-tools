#!/bin/bash
#SBATCH -p short               #partition
#SBATCH -t 1:00:00             #wall time
#SBATCH --mem 1G              #memory requested
#SBATCH -o rseqc_infer_strand.%j.out         #job out logs
#SBATCH -e rseqc_infer_strand.%j.err         #job error logs

# input file is $1 (first argument)

echo $1

infer_experiment.py -i $1 -r /n/groups/kwon/data1/databases/human/hg38/annotations_from_UCSC_table_browser/Hg38_refseq.gtf.bed
