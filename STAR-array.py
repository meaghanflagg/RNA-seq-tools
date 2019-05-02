#!/usr/bin/env python
#SBATCH -p short               #partition
#SBATCH -t 1:00:00             #wall time
#SBATCH -c 8                   #cores requested
#SBATCH --mem 48G              #memory requested
#SBATCH -o star.%A_%a.out         #job out logs
#SBATCH -e star.%A_%a.err         #job error logs


import os, fnmatch, re, sys, argparse, errno, json
from datetime import datetime

def files_list_from_dir(directory, glob_pattern):
    files_list=[]
    for f in os.listdir(directory):
        if fnmatch.fnmatch(f, glob_pattern):
            files_list.append(os.path.join(os.path.abspath(directory),f))
    return files_list

def write_json_logfile(files_list, filename):
    slurm_array_task_id_list=range(len(files_list))
    slurm_array_task_id_to_filename_dict=dict(zip(slurm_array_task_id_list, files_list))
    with open(filename, 'w') as f:
        json.dump(slurm_array_task_id_to_filename_dict, f, sort_keys=True, indent=4)
    return

def star_command_PE(read1, read2, sample_name, genomeDir='/n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/STAR_indices', nthreads=8,
                    unzip_cmd='zcat', quantMode='GeneCounts'):
    
    cmd_list=['STAR', '--runThreadN', '{threads}', '--genomeDir', '{genomeDir}', '--readFilesIn', '{read1}', '{read2}', \
        '--readFilesCommand', '{unzip_cmd}', '--outFileNamePrefix', '{outFnamePrefix}', '--outSAMtype BAM SortedByCoordinate', \
        '--outSAMunmapped None', '--outSAMattributes All', '--outReadsUnmapped Fastx', '--quantMode', '{quantMode}']

    cmd=" ".join(cmd_list).format(threads=nthreads, genomeDir=genomeDir, read1=read1, read2=read2, unzip_cmd=unzip_cmd, \
            outFnamePrefix=outFnamePrefix, quantMode=quantMode)
    
    return cmd

# which directory to look thru:
try: directory = os.path.abspath(sys.argv[1])
except IndexError: directory=os.getcwd()

parser = argparse.ArgumentParser(description="DESCRIPTION: submit STAR alignment jobs as an sbatch array")
parser.add_argument("-glob_pattern", type=str, default="*R1_001_trimmed.fastq.gz", help="Unix-style pattern to find files in directory. Defaults to illumina-style naming convention '*R1_001_trimmed.fastq.gz'.")
parser.add_argument("-genomeDir", type=str, default='/n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/STAR_indices',
        help="Specify path to STAR references. Defaults to '/n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/STAR_indices'.")
parser.add_argument("-outdir", type=str, nargs='?',
        help="Directory to store output files. Defaults to specififed input directory, or current working directory if none specified.")
parser.add_argument("-sampleNameRegex", type=str, default=r'_S[0-9]+.*_R[12]_001', help="regular expression to capture non-sample name portion of fastq filename. Defaults to match Illumina naming convention.")
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

if args.outdir: # make base output directory, e.g. STAR_out
    # test if directory exists, if not create it
    try: os.makedirs(args.outdir)
    except OSError as e:
        if e.errno != errno.EEXIST:     # if directory exists, ignore the error and proceed.
            raise   # if the error is something else, raise it.    
    outdir=os.path.abspath(args.outdir)
else:
    outdir=os.path.abspath(args.dir)   # defaults to specified input directory, or os.getcwd() if no input dir was specified.


SLURM_ARRAY_TASK_ID=os.environ.get('SLURM_ARRAY_TASK_ID')

if SLURM_ARRAY_TASK_ID == None:
    
    if args.files_list:
            files_list=args.files_list
    else:
        files_list=files_list_from_dir(args.dir, args.glob_pattern)
    
    if not len(files_list) >= 1:
        sys.exit("Error: No files found!")
    
    os.environ['ARRAY_FILES']=":".join(files_list)
    #os.environ['DIRECTORY']=directory
    
    sbatch_cmd=["sbatch","--array=0-{0}".format(len(files_list)-1),__file__,]+sys.argv[1:]

    os.system( " ".join(sbatch_cmd) )

    # write a dictionary of SLURM_ARRAY_TASK_ID:filename so I can rename files later:
    json_log = "star_array_{timestamp}.json".format(timestamp=datetime.strftime(datetime.now(), '%Y-%m-%d_%Hh%Mm'))
    write_json_logfile(files_list, json_log)

else:
    files_list = os.environ.get('ARRAY_FILES').split(':')
    
    #directory=os.environ.get('DIRECTORY')

    #os.system("module load star/2.5.2b")
    
    read1=files_list[int(SLURM_ARRAY_TASK_ID)]
    
    read2=read1.replace('_R1_','_R2_')
    
    #extract sample name from read names using regex to match illumina naming convention, and grab part before that.
    try: sample_name=read1.split(re.search(args.sampleNameRegex,read1).group(0))[0].split('/')[-1]
    except AttributeError: sample_name=read1.split('.fastq')[0]
    
    # make directory for results:
    results_directory=os.path.join(outdir,sample_name+"_STAR_out")
    #os.mkdir(results_directory)
    
    try: os.makedirs(results_directory)
    except OSError as e:
        if e.errno != errno.EEXIST:     # if directory exists, ignore the error and proceed.
            raise   # if the error is something else, raise it.
    
    
    # create filename prefix for STAR, including the results directory
    outFnamePrefix="{res_dir}/{samp_name}_STAR_".format(res_dir=results_directory, samp_name=sample_name)


## parameters for running STAR ##
    nthreads=8
    genomeDir='/n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/STAR_indices'
    unzip_cmd='zcat'   # command to unzip your files
    quantMode='GeneCounts'

    cmd_list=['STAR', '--runThreadN', '{threads}', '--genomeDir', '{genomeDir}', '--readFilesIn', '{read1}', '{read2}', \
        '--readFilesCommand', '{unzip_cmd}', '--outFileNamePrefix', '{outFnamePrefix}', '--outSAMtype BAM SortedByCoordinate', \
        '--outSAMunmapped None', '--outSAMattributes All', '--outReadsUnmapped Fastx', '--quantMode', '{quantMode}']

    cmd=" ".join(cmd_list).format(threads=nthreads, genomeDir=genomeDir, read1=read1, read2=read2, unzip_cmd=unzip_cmd, \
            outFnamePrefix=outFnamePrefix, quantMode=quantMode)
    load_module='module load star/2.5.2b'
    
    os.system("{module} ; {command}".format(module=load_module, command=cmd))
