#!/usr/bin/python

#SBATCH -J samtools_sort 
#SBATCH -p short
#SBATCH -t 0-4:00       #  "days-hours:minutes"
#SBATCH --mem 4G
#SBATCH -o 'samtools_index_%A_%a.out'
#SBATCH -e 'samtools_index_%A_%a.err'

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
            if fnmatch.fnmatch(f, '*.sortedByCoord.out.bam'):
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
    cmd=['samtools index -b', infile]
    os.system(" ".join(cmd))
    


