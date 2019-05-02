#!/usr/bin/env python

#SBATCH -p short               #partition
#SBATCH -t 0:30:00             #wall time
#SBATCH -c 1                   #cores requested
#SBATCH --mem 1G              #memory requested
#SBATCH -o fastqc.%j.out         #job out logs
#SBATCH -e fastqc.%j.err         #job error logs

import os, fnmatch, re, sys, argparse, errno

# which directory to look thru:
#try: directory = os.path.abspath(sys.argv[1])
#except IndexError: directory=os.getcwd()

parser=argparse.ArgumentParser("DESCRIPTION: submit fastqc jobs as sbatch array")
group=parser.add_mutually_exclusive_group()
group.add_argument("-dir", type=str, nargs='?', default=os.getcwd(), help="path to directory with fastq files")
group.add_argument("-files_list", type=str, nargs="*", help="Alternative to '-dir'. Specify input fastq files separated by spaces")
parser.add_argument("-outdir", type=str, nargs='?', help="Directory to store output files. Defaults to specififed input directory, or current working directory if none specified.")
parser.add_argument("-glob_pattern", type=str, default="*.fastq*", help="Unix-style pattern to find files in directory. Defaults to '*.fastq*'.")

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



SLURM_ARRAY_TASK_ID=os.environ.get('SLURM_ARRAY_TASK_ID')

if SLURM_ARRAY_TASK_ID == None:  # build list of files and create job array
    
    ### make list of files for array: ####
    if args.files_list:
        files_list=args.files_list
    
    elif args.dir:
        files_list=[]
        for f in os.listdir(args.dir):
        # build file array
            if fnmatch.fnmatch(f, args.glob_pattern):
                files_list.append(os.path.join(os.path.abspath(args.dir),f))
    
    if not len(files_list) > 1:
        sys.exit("Error: No files found!")
    
    print "found {0} files in {1}".format(len(files_list), args.dir)
    
    os.environ['ARRAY_FILES']=":".join(files_list)
    #os.environ['DIRECTORY']=args.dir
    
    sbatch_cmd=["sbatch","--array=0-{0}".format(len(files_list)-1),__file__,]+sys.argv[1:]

    os.system( " ".join(sbatch_cmd) )
    
else:    # job array has been created, now submit the jobs
    files_list = os.environ.get('ARRAY_FILES').split(':')
    
    #directory=os.environ.get('DIRECTORY')
    
    #output_dir='/n/groups/kwon/meg/2018_11_22_bulk_NextSeq/fastqc_out/trimmed_fastqs'
    
    
    cmd="fastqc -o {0} {1}".format(outdir, files_list[int(SLURM_ARRAY_TASK_ID)])
    
    os.system(cmd)
    
