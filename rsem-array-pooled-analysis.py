#!/usr/bin/env python

#SBATCH -J rsem
#SBATCH -c 8                   #cores requested
#SBATCH -p short
#SBATCH -t 0-6:00       #  "days-hours:minutes"
#SBATCH --mem 60G              #memory requested
#SBATCH -o 'rsem_%A_%a.out'
#SBATCH -e 'rsem_%A_%a.err'
import glob, os, json, re

pwd=os.getcwd()

SLURM_ARRAY_TASK_ID=os.environ.get('SLURM_ARRAY_TASK_ID')

if SLURM_ARRAY_TASK_ID == None:
    # walking thru output dirs to get file paths:

    files_list=glob.glob("/n/groups/kwon/crystal/bulk_rna_seq/pooled_runs/fastqs_trimmed/*.fastq.gz")
    
    #print "\n".join(files_list)
    
    # make and write out a lookup table to match files with their slurm array task IDs:
    slurm_array_task_id_list=range(len(files_list))
    
    slurm_array_task_id_to_filename_dict=dict(zip(slurm_array_task_id_list, files_list))
    
    with open('rsem_slurm_array_task_id_to_filename_dict.json', 'w') as f:
        json.dump(slurm_array_task_id_to_filename_dict, f, sort_keys=True, indent=4)
    
    
    os.environ['ARRAY_FILES']=":".join(files_list)
    sbatch_cmd=["sbatch", "--array=1-{0}".format(len(files_list)-1), __file__]
#    sbatch_cmd=["sbatch", "--array=1-2", __file__]
    os.system( " ".join(sbatch_cmd) )
    
else:
    files_list = os.environ.get('ARRAY_FILES').split(':')
    #print "SLURM_ARRAY_TASK_ID: {0}".format(SLURM_ARRAY_TASK_ID)
    #print "file: {0}".format(files_list[int(SLURM_ARRAY_TASK_ID)])
    
    fq=files_list[int(SLURM_ARRAY_TASK_ID)]
    SAMPLE_NAME=re.search(r'[0-9]{6}_CD103_[a-z]+',fq,re.I).group(0)
    
    # make a directory to catch rsem output and navigate to this directory
    newdir=SAMPLE_NAME+'_out'
      
    try:
        os.mkdir(newdir)     # this fails if the directory already exists!
        os.chdir(newdir)
    except OSError, e:
        if e.errno != os.errno.EEXIST:      #check if the error is a "file exists" error. if so, use existing directory. if not, raise the OS error.
            raise
        else:
            os.chdir(newdir)

    
    ### rsem parameters ###
    # --forward-prob 0 : Probability of generating a read from the forward strand of a transcript.
    #                    Set to 1 for a strand-specific protocol where all (upstream) reads are derived
    #                    from the forward strand, 0 for a strand-specific protocol where all (upstream)
    #                    read are derived from the reverse strand, or 0.5 for a non-strand-specific protocol. (Default: 0.5)
    
    ### required modules ###
    # module load star/2.5.2b
    # module load rsem/1.3.0
    
    cmd=['rsem-calculate-expression -p 4 --star --star-output-genome-bam --star-gzipped-read-file --forward-prob 0', fq,
         '/n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/rsem-gencode-GRCh38/hg38', SAMPLE_NAME]
    os.system(" ".join(cmd))
    #print " ".join(cmd)