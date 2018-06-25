#!/usr/bin/python

#SBATCH -J picard_MarkDups 
#SBATCH -p short
#SBATCH -t 0-4:00       #  "days-hours:minutes"
#SBATCH --mem=9G
#SBATCH -o 'picard_MarkDuplicates_%A_%a.out'
#SBATCH -e 'picard_MarkDuplicates_%A_%a.err'

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
            if fnmatch.fnmatch(f, '*.transcript.sorted.bam'):
                files_list.append(os.path.join(path,f))
    
    #test_files=glob.glob("/etc/*rc")
    os.environ['ARRAY_FILES']=":".join(files_list)
    sbatch_cmd=["sbatch",
                "--array=0-{0}".format(len(files_list)-1),
                __file__]
    
    os.system( " ".join(sbatch_cmd) )
else:
    files_list = os.environ.get('ARRAY_FILES').split(':')
    #print "SLURM_ARRAY_TASK_ID: {0}".format(SLURM_ARRAY_TASK_ID)
    #print "file: {0}".format(files_list[int(SLURM_ARRAY_TASK_ID)])
    infile=files_list[int(SLURM_ARRAY_TASK_ID)]
    outfile=infile.replace('.sorted.bam','.deduplicated.bam')
    metrics_file=infile.split("/")[-2]+"_dedup_metrics"
    cmd=['java -Xmx4g -jar $PICARD/picard-2.8.0.jar MarkDuplicates MAX_FILE_HANDLES=1000 TAGGING_POLICY=All REMOVE_DUPLICATES=true', 'I=',infile, " O=",outfile, " M=", metrics_file]
    os.system(" ".join(cmd))

    


