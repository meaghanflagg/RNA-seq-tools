#!/usr/bin/env python

#SBATCH -n 4                    # number of cores requested
#SBATCH -t 4:00:00                   # runtime in minutes. Can also use HH:MM:SS or D-HH:MM:SS
#SBATCH -p short                # submit to 'short' partition
#SBATCH --mem-per-cpu=3G
#SBATCH -o 'trimmomatic_%A_%a.out'     #%A=job id, %a=array index
#SBATCH -e 'trimmomatic_%A_%a.err'     #%A=job id, %a=array index

import os, fnmatch, re, sys, subprocess, argparse, time, errno, json
from datetime import datetime
#import pdb      # debugging only

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
    
def write_json_logfile(files_list, filename):
    slurm_array_task_id_list=range(len(files_list))
    slurm_array_task_id_to_filename_dict=dict(zip(slurm_array_task_id_list, files_list))
    with open(filename, 'w') as f:
        json.dump(slurm_array_task_id_to_filename_dict, f, sort_keys=True, indent=4)
    return
    
def trim_SE(r1):
    ## do stuff##
    return


def trimmomatic_PE_command(r1, outdir, adapter_file):
    '''
    returns a string containing a properly formatted command to run Trimmomatic (v0.36) in paired-end mode for a given read 1 fastq filename.
    '''
    
    # r1 = read 1
    r2=r1.replace('_R1_','_R2_')
    r1_out=os.path.join(outdir,os.path.basename(r1.replace('_001.fastq','_001_trimmed.fastq')))
    r2_out=os.path.join(outdir,os.path.basename(r2.replace('_001.fastq','_001_trimmed.fastq')))
    r1_unpaired=os.path.join(outdir,os.path.basename(r1.replace('_001.fastq','_001_trimmed_unpaired.fastq')))
    r2_unpaired=os.path.join(outdir,os.path.basename(r2.replace('_001.fastq','_001_trimmed_unpaired.fastq')))
    
    trimlog=os.path.join(outdir,"{0}_trimlog".format(os.path.basename(r1).split('.fastq')[0]))

    #adapter_file="/n/groups/kwon/crystal/bulk_rna_seq/resequencing/trimmomatic_testing/TruSeq-2-3-nextera-tso-adapters.fa" # old adapter file I used
    
    module="module load trimmomatic/0.36"  # command to load the appropriate trimmomatic module
    cmd="java -jar $TRIMMOMATIC/trimmomatic-0.36.jar PE -threads 4 -trimlog {trimlog} \
    {r1} {r2} {r1_out} {r1_unpaired} {r2_out} {r2_unpaired} \
    ILLUMINACLIP:{adapter_file}:2:30:10:1:True LEADING:3 TRAILING:3 MINLEN:20".format(trimlog=trimlog,
    r1=r1, r2=r2, r1_out=r1_out, r1_unpaired=r1_unpaired, r2_out=r2_out, r2_unpaired=r2_unpaired,
    adapter_file=adapter_file)

    #process=subprocess.Popen("{load_module} ; {cmd}".format(load_module=load_module, cmd=cmd),
    #                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    #stdout, stderr = process.communicate()
    return module, cmd

if __name__ == '__main__':
    
    ### Argument Handling for universal arguments ###
    parser = argparse.ArgumentParser(description="DESCRIPTION: submit trimmomatic jobs as an sbatch array")
    parser.add_argument("-PE", action="store_true", help="Flag for paired-end data. Default=False", default=False)
    parser.add_argument("-glob_pattern", type=str, default="*R1_001.fastq*", help="Unix-style pattern to find files in directory. Defaults to illumina-style naming convention '*R1_001.fastq*'.")
    parser.add_argument("-adapter_file", type=str, default='/n/app/trimmomatic/0.36/bin/adapters/NexteraPE-PE.fa', help="Specify path to custom adapter file. Defaults to 'NexteraPE-PE.fa' provided in trimmomatic distribution.")
    parser.add_argument("-logfile", type=str, nargs='?', help="Filename for STDOUT and STDERR logs. Defaults to job array ID with timestamp.")
    parser.add_argument("-outdir", type=str, nargs='?', help="Directory to store output files. Defaults to specififed input directory, or current working directory if none specified.")
    # loop through a directory or pass a list of files:
    group=parser.add_mutually_exclusive_group()
    group.add_argument("-dir", type=str, default=os.getcwd(), help="path to directory containing fastq files. Default: current working directory")
    group.add_argument("-files_list", type=str, nargs='*', help="Alternative to '-dir'. Specify input fastq files separated by spaces") # accept zero or more arguments
    
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
            for f in os.listdir(args.dir):
            # build file array
                if fnmatch.fnmatch(f, args.glob_pattern):
                    files_list.append(os.path.join(os.path.abspath(args.dir),f))
        
        
        if not len(files_list) >= 1:
            sys.exit("Error: No files found!")
        
        os.environ['ARRAY_FILES']=":".join(files_list)
        
        # submit the job array, and capture standard out (e.g. job ID), and anything written to stderr
        job_array_command=submit_job_array(files_list)
        
        os.system(job_array_command)
        
        #job_array_id = os.environ.get('SLURM_ARRAY_JOB_ID')  # this returns None, not sure why
        
        # write a dictionary of SLURM_ARRAY_TASK_ID:filename so I can rename files later:
        json_log = "trimmomatic_array_{timestamp}.json".format(timestamp=datetime.strftime(datetime.now(), '%Y-%m-%d_%Hh%Mm'))
        write_json_logfile(files_list, json_log)
        
    
    else: # array exists (e.g. $SLURM_ARRAY_TASK_ID has a integer value), so begin submitting jobs
        
        files_list = os.environ.get('ARRAY_FILES').split(':')   # get the list of files
        r1=files_list[int(SLURM_ARRAY_TASK_ID)]      # this is the file from the list that we are submitting the job for
        
        
        ### make logfiles ###
        job_id=os.environ.get('SLURM_JOB_ID')
        #basename=os.path.join(outdir,'trimmomatic_array_'+str(job_id)+'_'+os.path.basename(r1))
        #errlog=open("{0}_log.err".format(basename), 'w')
        #outlog=open("{0}_log.out".format(basename), 'w')
        
        # open up the master log (log of logfiles) I created earlier:
#        with open(os.environ.get('MASTERLOG'), 'a') as masterlog:
            # write names of logfiles to masterlog:
#            masterlog.write("{errlog}\n{outlog}\n".format(errlog=errlog.name, outlog=outlog.name))
        
        if args.PE == True:
            module, cmd = trimmomatic_PE_command(r1, outdir, args.adapter_file)
            print "{load_module} ; {cmd}".format(load_module=module, cmd=cmd)
        #    process=subprocess.Popen("{load_module} ; {cmd}".format(load_module=module, cmd=cmd),
        #                     stdout=outlog, stderr=errlog, shell=True)
        
            os.system("{load_module} ; {cmd}".format(load_module=module, cmd=cmd))
        
        else:
            ###### FIX ME ########
            sys.exit("Single end trimming not yet supported :( line 193")
            
        
        
        #errlog.close()
        #outlog.close()
        