#!/usr/bin/env python

#SBATCH -n 4                    # number of cores requested
#SBATCH -t 4:00:00                   # runtime in minutes. Can also use HH:MM:SS or D-HH:MM:SS
#SBATCH -p short                # submit to 'short' partition
#SBATCH --mem-per-cpu=3G
#SBATCH -o trimmomatic_%j.out               # write stdout to file jobID.out
#SBATCH -e trimmomatic_%j.err               # write stderr to file jobID.err

import os, fnmatch, re, sys

# which directory to look thru:
try: directory = sys.argv[1]
except IndexError: directory=os.getcwd()


SLURM_ARRAY_TASK_ID=os.environ.get('SLURM_ARRAY_TASK_ID')

if SLURM_ARRAY_TASK_ID == None:
    files_list=[]
    for f in os.listdir(directory):
    # build file array
        if fnmatch.fnmatch(f, '*R1_001.fastq*'):
            #### FIX ME #####
            files_list.append(os.path.join(os.path.abspath(directory),f))
    
    if not len(files_list) > 1:
        sys.exit("Error: No files found!")
    
    os.environ['ARRAY_FILES']=":".join(files_list)
    
    sbatch_cmd=["sbatch","--array=0-{0}".format(len(files_list)-1),__file__]

    os.system( " ".join(sbatch_cmd) )


else:
    files_list = os.environ.get('ARRAY_FILES').split(':')

    
    infile_r1=files_list[int(SLURM_ARRAY_TASK_ID)]
    infile_r2=infile_r1.replace('_R1_','_R2_')
    
    outfile_r1_paired=infile_r1.replace('_001.fastq','_001_trimmed.fastq')
    outfile_r2_paired=infile_r2.replace('_001.fastq','_001_trimmed.fastq')
    
    outfile_r1_unpaired=infile_r1.replace('_001.fastq','_001_trimmed_unpaired.fastq')
    outfile_r2_unpaired=infile_r2.replace('_001.fastq','_001_trimmed_unpaired.fastq')
    
    
    trimfile="trimlog_{0}".format(re.search(r'[0-9]{6}_CD103_[a-z]+',infile_r1,re.I).group(0))   # regex grabs the sample name
 
    adapter_file="/n/groups/kwon/crystal/bulk_rna_seq/resequencing/trimmomatic_testing/TruSeq-2-3-nextera-tso-adapters.fa"

    cmd="java -jar $TRIMMOMATIC/trimmomatic-0.36.jar PE -threads 4 -trimlog {Trimfile} \
{Infile_r1} {Infile_r2} {Outfile_r1_paired} {Outfile_r1_unpaired} {Outfile_r2_paired} {Outfile_r2_unpaired} \
ILLUMINACLIP:{Adapter_file}:2:30:10:1:True LEADING:3 TRAILING:3 MINLEN:20".format(Trimfile=trimfile, \
        Infile_r1=infile_r1, Infile_r2=infile_r2, Outfile_r1_paired=outfile_r1_paired, Outfile_r1_unpaired=outfile_r1_unpaired, \
        Outfile_r2_paired=outfile_r2_paired, Outfile_r2_unpaired=outfile_r2_unpaired, Adapter_file=adapter_file)

    os.system(cmd)
    