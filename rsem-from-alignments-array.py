#!/usr/bin/env python

#!/usr/bin/python

#SBATCH -J rsem
#SBATCH --cpus-per-task 4
#SBATCH -p short
#SBATCH -t 0-6:00       #  "days-hours:minutes"
#SBATCH --mem-per-cpu=4G
#SBATCH -o 'rsem_%A_%a.out'
#SBATCH -e 'rsem_%A_%a.err'
import glob, os, json, re, fnmatch

pwd=os.getcwd()

SLURM_ARRAY_TASK_ID=os.environ.get('SLURM_ARRAY_TASK_ID')

if SLURM_ARRAY_TASK_ID == None:
    # walking thru output dirs to get file paths:
    files_list=[]
    #files_list=glob.glob("/n/groups/kwon/crystal/bulk_rna_seq/fastqs/*.fastq.gz")
    for path, subdirs, files in os.walk(os.getcwd()):
        for f in files:
            if fnmatch.fnmatch(f, '*.transcript.deduplicated.rsem.bam'):
                files_list.append(os.path.join(path,f))
    
    #print "\n".join(files_list)
    
    # make and write out a lookup table to match files with their slurm array task IDs:
    slurm_array_task_id_list=range(len(files_list))
    
    slurm_array_task_id_to_filename_dict=dict(zip(slurm_array_task_id_list, files_list))
    
    with open('rsem_slurm_array_task_id_to_filename_dict.json', 'w') as f:
        json.dump(slurm_array_task_id_to_filename_dict, f, sort_keys=True, indent=4)
    
    
    os.environ['ARRAY_FILES']=":".join(files_list)
    sbatch_cmd=["sbatch", "--array=0-{0}".format(len(files_list)-1), __file__]
#    sbatch_cmd=["sbatch", "--array=1-2", __file__]
    os.system( " ".join(sbatch_cmd) )
    
else:
    files_list = os.environ.get('ARRAY_FILES').split(':')
    #print "SLURM_ARRAY_TASK_ID: {0}".format(SLURM_ARRAY_TASK_ID)
    #print "file: {0}".format(files_list[int(SLURM_ARRAY_TASK_ID)])
    
    fq=files_list[int(SLURM_ARRAY_TASK_ID)]
    SAMPLE_NAME=re.search(r'[0-9]{6}_CD103_[a-z]+',fq,re.I).group(0)+"_dedup"
    
    # make a directory to catch rsem output and navigate to this directory
    newdir=SAMPLE_NAME+'_dedup_out'
    os.mkdir(newdir)
    os.chdir(newdir)
    
    cmd=['rsem-calculate-expression -p 4 --alignments', fq, '/n/groups/kwon/data1/databases/human/hg38/rsem-indices-refseq/hg38', SAMPLE_NAME]
    os.system(" ".join(cmd))
    #print " ".join(cmd)