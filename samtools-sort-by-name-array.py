#!/usr/bin/python

#SBATCH -J samtools_sort 
#SBATCH -p short
#SBATCH -t 0-4:00       #  "days-hours:minutes"
#SBATCH --cpus-per-task 8
#SBATCH --mem-per-cpu=8G
#SBATCH -o 'samtools_%A_%a.out'
#SBATCH -e 'samtools_%A_%a.err'

import os, sys, fnmatch
#import glob

#print("HELLO WORLD!")
#sys.stderr.write("ERROR HANDLE.");

SLURM_ARRAY_TASK_ID=os.environ.get('SLURM_ARRAY_TASK_ID')

if SLURM_ARRAY_TASK_ID == None:
    # walking thru output dirs to get file paths:
    files_list=[]
    for path, subdirs, files in os.walk(os.getcwd()):
        for f in files:
            if fnmatch.fnmatch(f, '*.transcript.deduplicated.bam'):
                files_list.append(os.path.join(path,f))
    
    #test_files=glob.glob("/etc/*rc")
    os.environ['ARRAY_FILES']=":".join(files_list)
    sbatch_cmd=["sbatch", "--array=0-{0}".format(len(files_list)-1), __file__]
    #sbatch_cmd=["sbatch", "--array=1-2", __file__]
    os.system( " ".join(sbatch_cmd) )
    
else:
    files_list = os.environ.get('ARRAY_FILES').split(':')
    #print "SLURM_ARRAY_TASK_ID: {0}".format(SLURM_ARRAY_TASK_ID)
    #print "file: {0}".format(files_list[int(SLURM_ARRAY_TASK_ID)])
    infile=files_list[int(SLURM_ARRAY_TASK_ID)]
    outfile=infile.replace('.transcript.deduplicated.bam','.transcript.deduplicated.sorted.bam')
    cmd=['samtools sort -@ 8 -m 6G -n -o', outfile, infile]
    os.system(" ".join(cmd))
    


