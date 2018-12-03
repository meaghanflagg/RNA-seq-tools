#!/usr/bin/env python

#SBATCH -p short               #partition
#SBATCH -t 0:15:00             #wall time
#SBATCH -c 1                   #cores requested
#SBATCH --mem 1G              #memory requested
#SBATCH -o fastqc.%j.out         #job out logs
#SBATCH -e fastqc.%j.err         #job error logs

import os, fnmatch, re, sys

# which directory to look thru:
try: directory = os.path.abspath(sys.argv[1])
except IndexError: directory=os.getcwd()


SLURM_ARRAY_TASK_ID=os.environ.get('SLURM_ARRAY_TASK_ID')

if SLURM_ARRAY_TASK_ID == None:  # build list of files and create job array
    files_list=[]
    for f in os.listdir(directory):
    # build file array
        if fnmatch.fnmatch(f, '*.fastq.gz'):
            files_list.append(os.path.join(os.path.abspath(directory),f))
    
    if not len(files_list) > 1:
        sys.exit("Error: No files found!")
    
    print "found {0} files in {1}".format(len(files_list), directory)
    
    os.environ['ARRAY_FILES']=":".join(files_list)
    os.environ['DIRECTORY']=directory
    
    sbatch_cmd=["sbatch","--array=0-{0}".format(len(files_list)-1),__file__]

    os.system( " ".join(sbatch_cmd) )
    
else:    # job array has been created, now submit the jobs
    files_list = os.environ.get('ARRAY_FILES').split(':')
    
    directory=os.environ.get('DIRECTORY')
    
    output_dir='/n/groups/kwon/meg/2018_11_22_bulk_NextSeq/fastqc_out/raw_fastqs'
    
    cmd="fastqc -o {0} {1}".format(output_dir, files_list[int(SLURM_ARRAY_TASK_ID)])
    
    os.system(cmd)
    
