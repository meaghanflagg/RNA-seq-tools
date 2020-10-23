#!/usr/bin/env python

#SBATCH -p short               #partition
#SBATCH -t 6:00:00             #wall time
#SBATCH --mem 1G              #memory requested
#SBATCH -o rseqc_transcript_integrity.%j.out         #job out logs
#SBATCH -e rseqc_transcript_integrity.%j.err         #job error logs


import os, fnmatch, re, sys, argparse, errno

def submit_job_array(files_list):
    '''
    returns a text string that when executed will submit a Slurm job array of appropriate length for a given list of files
    
    TO DO:
    add arguments to control memory, cores, etc
    '''
    
    #os.environ['ARRAY_FILES']=":".join(files_list)     # I do this outside of the function, after creating the files list.
    
    arg_list=sys.argv[1:] # grab all agruments (except script name) to pass to sbatch job.
    
    #sbatch_array_cmd=" ".join(["sbatch","--array=0-{0}".format(len(files_list)-1),__file__])   # passing __file__ alone doesn't work, since it doesn't pass script arguments along.
    sbatch_array_cmd=" ".join(["sbatch","--array=0-{0}".format(len(files_list)-1),__file__,]+arg_list)
    
    return sbatch_array_cmd

def rseqc_transcript_integrity_cmd(bam_file, outdir, ref):
    # grab sample name (use star naming convention), extra insurance to remove ".bam" portion in case filename doesn't match STAR convention
    samplename=bam_file.split("_Aligned")[0].rstrip(".bam")
    outfile=os.path.join(outdir, samplename)
    cmd="tin.py -i {bam_file} -r {ref} > {outfile}".format(bam_file=bam_file, ref=ref, outfile=outfile)
    return cmd

if __name__ == '__main__':
    parser=argparse.ArgumentParser("DESCRIPTION: submit RSeQC transcript integrity jobs as sbatch array")
    group=parser.add_mutually_exclusive_group()
    group.add_argument("-dir", type=str, nargs='?', default=os.getcwd(), help="path to directory with bam alignment files")
    group.add_argument("-files_list", type=str, nargs="*", help="Alternative to '-dir'. Specify input bam alignment files separated by spaces")
    parser.add_argument("-outdir", type=str, nargs='?', help="Directory to store output files. Defaults to specififed input directory, or current working directory if none specified.")
    parser.add_argument("-glob_pattern", type=str, default="*.bam", help="Unix-style pattern to find files in directory. Defaults to '*.bam'.")
    parser.add_argument("-ref", type=str, default="/n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/gencode.v28.primary_assembly.annotation.bed",
                        help="Path to reference genome annotation file in BED 12-column format.Defaults to '/n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/gencode.v28.primary_assembly.annotation.bed'")
    
    args=parser.parse_args()
    
    ### catch bad args ###    
    if args.dir:
        # check if directory exists:
        if not os.path.isdir(args.dir):
            sys.exit("Path error: {0} is not a valid directory!".format(args.dir))
    
    if args.outdir:
        # test if directory exists, if not create it
        try: os.makedirs(args.outdir)
        except OSError as e:
            if e.errno != errno.EEXIST:     # if directory exists, ignore the error and proceed.
                raise   # if the error is something else, raise it.    
        outdir=os.path.abspath(args.outdir)
    else:
        outdir=os.path.abspath(args.dir)   # defaults to specified input directory, or os.getcwd() if no input dir was specified.
        

### check for array: ###
    # for the first iteration of this script, this will be None.
    # Therefore, we will parse arguments, grab the list of files, and submit a slurm job array.
    # after the job array is submitted, this will have an integer value. 
    SLURM_ARRAY_TASK_ID=os.environ.get('SLURM_ARRAY_TASK_ID')
    
    
    if SLURM_ARRAY_TASK_ID == None: # array does not exist yet, so create it
        
        ### make list of files for array: ####
        if args.files_list:
            files_list=args.files_list
        
        elif args.dir:
            files_list=[]
            for path, subdirs, files in os.walk(args.dir):
                for f in files:
                    if fnmatch.fnmatch(f, args.glob_pattern):
                        files_list.append(os.path.join(path, f))
            

        if not len(files_list) >= 1:
            sys.exit("Error: No files found!")
        
        os.environ['ARRAY_FILES']=":".join(files_list)
        
        # submit the job array
        job_array_command=submit_job_array(files_list) 
        os.system(job_array_command)

    else: # array exists (e.g. $SLURM_ARRAY_TASK_ID has a integer value), so begin submitting jobs
        
        files_list = os.environ.get('ARRAY_FILES').split(':')   # get the list of files
        bam_file=files_list[int(SLURM_ARRAY_TASK_ID)]      # this is the file from the list that we are submitting the job for
        
        cmd=rseqc_transcript_integrity_cmd(bam_file, outdir, args.ref)
        
        os.system("module load {module} ; {cmd}".format(module="rseqc/2.6.4", cmd=cmd))

