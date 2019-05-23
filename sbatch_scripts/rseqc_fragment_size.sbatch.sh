#!/bin/bash
#SBATCH -p short               #partition
#SBATCH -t 1:00:00             #wall time
#SBATCH --mem 1G              #memory requested
#SBATCH -o rseqc_fragment_size.%j.out         #job out logs
#SBATCH -e rseqc_fragment_size.%j.err         #job error logs


# execute this on a list of files with the following command:
# for i in `find STAR_out/ -name "*.bam"`; do sbatch rseqc_fragment_size.sbatch.sh $i; done

# input file is $1 (first argument)

# grab filename from $1 (in case it is a path)
FNAME=$(awk -F/ '{print $NF}' <<< $1)

# create output filename:  samplename_Aligned.sortedByCoord.out.bam
# split on '_Aligned', take first portion
OUTFILE=$(awk -F_Aligned '{print $1}' <<< $FNAME)


RNA_fragment_size.py -i $1 -r /n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/gencode.v28.primary_assembly.annotation.bed > ${OUTFILE}_rseqc_fragment_size.txt
