#!/bin/bash
#SBATCH -p short
#SBATCH -t 02:30:00
#SBATCH -n 4
#SBATCH --mem 48G
#SBATCH -o starGenomeGenerate_gencode2.%j.out
#SBATCH -e starGenomeGenerate_gencode2.%j.err

STAR --runThreadN 4 --runMode genomeGenerate --genomeDir /n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/STAR_indices \
--genomeFastaFiles /n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/GRCh38.primary_assembly.genome.fa \
--sjdbGTFfile /n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/gencode.v28.primary_assembly.annotation.gtf \
--sjdbOverhang 75
