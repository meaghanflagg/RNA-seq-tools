#!/usr/bin/env python

#SBATCH -n 1                    # number of cores requested
#SBATCH -t 90                   # runtime in minutes. Can also use HH:MM:SS or D-HH:MM:SS
#SBATCH -p short                # submit to 'short' partition
#SBATCH --mem-per-cpu=3G
#SBATCH -o 'concatenate_fastq_%A_%a.out'     #%A=job id, %a=array index
#SBATCH -e 'concatenate_fastq_%A_%a.err'     #%A=job id, %a=array index


## pseudocode ##
# input: list of run directories
    # also required: name of dir inside run dir where fastqs were written, "project name" (if applicable) e.g. "gut bx epi"
    # OR, just provide a list of dirs where the actual fastqs are.
# output: command to "cat" files with the same name

# 1. establish regex to extract sample identifier from fastq filename
# 2. initialize two empty dictionaries, one for read1, one for read2
# 3. for each fastq directory:
    # A. iterate over directory contents
    # B. decide if element belongs to R1 or R2 (if contains '_R1_001')
    # C. add to appopriate dictionary. keys=sample identifier, values=filename (abspath). For each new runfolder dir, append sample name to dict
# 4. initialize empty list to contain commands
# 5. for each sample ID in dict (keys), create cat command for the values. should contain all the filenames. append to list.


## Illumina filenaming convention ##
# samplename_S1_R1_001.fastq.gz #

import argparse, re, os, sys, errno
from collections import defaultdict

def build_file_dict(dirs_list):
    
    R1_dict=defaultdict(list)   # initialize empty dictionary, where in the absense of an existing k/v pair, the value is an empty list which can be appended to.
    R2_dict=defaultdict(list)
    
    for directory in dirs_list:
        files=os.listdir(directory)
        for f in files:
            if re.search(r'_R1_001.*\.fastq.gz$|\.fastq$', f):     # R1 fastq file, ends with .fastq or .fastq.gz
                try: samplename=re.search(args.sample_regex, f).group(0)
                except AttributeError: sys.exit("improper sample name regex! found sample: {0}".format(f))
                filepath=os.path.join(os.path.abspath(directory), f)
                R1_dict[samplename].append(filepath)
            
            elif re.search(r'_R2_001.*\.fastq.gz$|\.fastq$',f):     # R2 fastq file
                try: samplename=re.search(args.sample_regex, f).group(0)
                except AttributeError: sys.exit("improper sample name regex! found sample: {0}".format(f))
                filepath=os.path.join(os.path.abspath(directory), f)
                R2_dict[samplename].append(filepath)
            else:
                pass
    
    return R1_dict, R2_dict


# create list of commands:
def build_cat_cmds(dictionary, outdir, read_pair=1):
    cmd_list=[]
    if not read_pair in [1,2]:
        return # invalid read pair
    for k, v in dictionary.items():
        if v[0].endswith('.gz'):        # gzipped fastqs
            out_fname=os.path.join(outdir, "{0}_R{1}_001.fastq".format(k, str(read_pair)))
            cmd="zcat {0} > {1}".format(" ".join(v), out_fname)
        else:                           # unzipped fastqs
            out_fname=os.path.join(outdir, "{0}_R{1}_001.fastq".format(k, str(read_pair)))
            cmd="cat {0} > {1}".format(" ".join(v), out_fname)
        cmd_list.append(cmd)
    return cmd_list

def submit_job_array(big_list):
    '''
    returns a text string that when executed will submit a Slurm job array of appropriate length for a given list of files
    
    TO DO:
    add arguments to control memory, cores, etc
    '''
    
    #os.environ['ARRAY_FILES']=":".join(files_list)     # I do this outside of the function, after creating the files list.
    
    arg_list=sys.argv[1:] # grab all agruments (except script name) to pass to sbatch job.
    
    #sbatch_array_cmd=" ".join(["sbatch","--array=0-{0}".format(len(files_list)-1),__file__])   # passing __file__ alone doesn't work, since it doesn't pass script arguments along.
    sbatch_array_cmd=" ".join(["sbatch","--array=0-{0}".format(len(big_list)-1),__file__,]+arg_list)
    
    return sbatch_array_cmd

if __name__ == '__main__':

    ### Argument Handling ###
    
    parser = argparse.ArgumentParser(description="DESCRIPTION: concatenate fastq files from multiple sequencing runs. Files must share the same sample name")
    parser.add_argument("-dirs", type=str, nargs="+", help="Specify directories containing fastq files, separated by spaces")
    parser.add_argument("-outdir", type=str, nargs='?', help="Path to directory to store output files. Defaults to current working directory")
    parser.add_argument("-sample_regex", type=str, help="Regex string for sample name", default='[0-9]{1}_[A-H]{1}[0-9]+')
    args=parser.parse_args()
    
    # handle outdir setup:
    if args.outdir:
        # test if directory exists, if not create it
        try: os.makedirs(args.outdir)
        except OSError as e:
            if e.errno != errno.EEXIST:     # if directory exists, ignore the error and proceed.
                raise   # if the error is something else, raise it.    
        outdir=os.path.abspath(args.outdir)
    else:
        outdir=os.getcwd()  # defaults to os.getcwd()
    
    
    #R1_dict, R2_dict=build_file_dict(args.dirs)
    #
    #R1_list=build_cat_cmds(R1_dict, outdir)
    #R2_list=build_cat_cmds(R2_dict, outdir)
    #
    #big_list=R1_list+R2_list
    
    
    ### check for array: ###
    # for the first iteration of this script, this will be None.
    # Therefore, we will parse arguments, grab the list of files, and submit a slurm job array.
    # after the job array is submitted, this will have an integer value. 
    SLURM_ARRAY_TASK_ID=os.environ.get('SLURM_ARRAY_TASK_ID')
    
    if SLURM_ARRAY_TASK_ID == None: # array does not exist yet, so create it
        
        R1_dict, R2_dict=build_file_dict(args.dirs)
    
        R1_list=build_cat_cmds(R1_dict, outdir)
        R2_list=build_cat_cmds(R2_dict, outdir, read_pair=2)
    
        big_list=R1_list+R2_list
        
        # temporary, write commands to file #
        with open('commands_list.txt', 'w') as out:
            out.write('\n'.join(big_list))
        
        #os.environ['COMMAND_LIST']=":".join(big_list)
        
        ## For some fucking weird-ass reason, using os.environ breaks os.system. WTF? so I'll do it differently.
        ## write list of commands to file, then read 'em back.
        
        job_array_command=submit_job_array(big_list)
        #print job_array_command
        #os.system("echo {0}".format(job_array_command))
        os.system(job_array_command)
    
    else:       # array exists (e.g. $SLURM_ARRAY_TASK_ID has a integer value), so begin submitting jobs
        #command_list = os.environ.get('COMMAND_LIST').split(':')   # get the list of commands
        
        with open('commands_list.txt', 'r') as f:
            command_list=f.readlines()
        
        cmd=command_list[int(SLURM_ARRAY_TASK_ID)]
        
        os.system(cmd)



