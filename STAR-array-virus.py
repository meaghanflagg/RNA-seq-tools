#!/usr/bin/env python
#SBATCH -p short               #partition
#SBATCH -t 1:00:00             #wall time
#SBATCH -c 8                   #cores requested
#SBATCH --mem 5G              #memory requested
#SBATCH -o star.%A_%a.out         #job out logs
#SBATCH -e star.%A_%a.err         #job error logs


import os, fnmatch, re, sys, argparse, errno, json, warnings, linecache
from datetime import datetime

def files_list_from_dir(directory, glob_pattern):
    files_list=[]
    for path, subdirs, files in os.walk(directory):
        for f in files:
            if fnmatch.fnmatch(f, glob_pattern):
                files_list.append(os.path.abspath(os.path.join(path,f)))
    return files_list

def write_json_logfile(files_list, filename):
    slurm_array_task_id_list=range(len(files_list))
    slurm_array_task_id_to_filename_dict=dict(zip(slurm_array_task_id_list, files_list))
    with open(filename, 'w') as f:
        json.dump(slurm_array_task_id_to_filename_dict, f, sort_keys=True, indent=4)
    return

def star_command_PE(read1, read2, outFnamePrefix, genomeDir, nthreads, quantMode, kwargs_dict, unzip_cmd):
    readFiles=read1+" "+read2

    cmd_dict={'--runThreadN':nthreads, '--genomeDir':genomeDir, '--readFilesIn':readFiles, \
        '--outFileNamePrefix':outFnamePrefix, '--outSAMtype': 'SAM', \
        '--outSAMunmapped': 'None', '--outSAMattributes': 'Standard', '--outReadsUnmapped': 'Fastx', \
        '--readFilesCommand':unzip_cmd, '--outFilterMismatchNmax': '4', \
        '--outFilterMultimapNmax': '1000', '--limitOutSAMoneReadBytes': '1000000'}

    # update cmd dict with kwargs:
    cmd_dict.update(kwargs)

    # remove any args that are None:
    for k,v in list(cmd_dict.items()):
        if v is None:
            del cmd_dict[k]

    # generate final command
    cmd_list=[]
    for k, v in cmd_dict.items():
        cmd_list.append(" ".join([k,v]))

    cmd = "STAR " + " ".join(cmd_list)
    return cmd


parser = argparse.ArgumentParser(description="DESCRIPTION: submit STAR alignment jobs as an sbatch array.\nAdditional keyword arguments will be passed to STAR aligner.")
# handle file input as either directory or list of files:
group=parser.add_mutually_exclusive_group()
group.add_argument("-dir", type=str, default=os.getcwd(), help="path to directory containing fastq files. Default: current working directory")
group.add_argument("-files_list", type=str, nargs='*', help="Alternative to '-dir'. Specify input fastq files separated by spaces") # accept zero or more arguments

parser.add_argument("-glob_pattern", type=str, default="*R1_001_trimmed.fastq.gz", help="Unix-style pattern to find files in directory if '-dir' specified. Defaults to illumina-style naming convention '*R1_001_trimmed.fastq.gz'.")
parser.add_argument("-readFilesCmd", choices=["zcat","'gunzip -c'","'bunzip2 -c'",'None'], default=None, help="If input files are compressed, specify command necessary for reading. Default: None")
parser.add_argument("-genomeDir", type=str, default='/n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/STAR_indices',
        help="Specify path to STAR references. Defaults to '/n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/STAR_indices'.")
parser.add_argument("-outdir", type=str, nargs='?',
        help="Directory to store output files. Defaults to specififed input directory, or current working directory if none specified.")
parser.add_argument("-quantMode", choices=['GeneCounts','TranscriptomeSAM','None'], default='GeneCounts', help="See STAR manual --quantMode. Default: GeneCounts")
parser.add_argument("-sampleNameRegex", type=str, default=r'_S[0-9]+.*_R[12]_001', help="regular expression to capture non-sample name portion of fastq filename. Defaults to match Illumina naming convention. Specify contents of expression without quotes, e.g. for r'[A-Z]{1}_[0-9]+' specify [A-Z]{1}_[0-9]+")
parser.add_argument("-readPair1Name", type=str, default='_R1_', help="indicate naming convention of read 1. Will be used to replace portion of readname indicating R1 with R2. Default: _R1_")


# parse known and unknown args
args, kwargs=parser.parse_known_args()
# create dict from unknown kwargs, remove any conflicting args
kwargsIter=iter(kwargs)
kwargs=dict(zip(kwargsIter,kwargsIter))

for k in list(kwargs.keys()):
    if k in args:
        del kwargs[k]


### catch bad args ###
if not os.path.isdir(os.path.abspath(args.dir)):
    raise ValueError("{0} is not a valid directory!".format(args.dir))

if args.outdir: # make base output directory, e.g. STAR_out
    # test if directory exists, if not create it
    try: os.makedirs(args.outdir)
    except OSError as e:
        if e.errno != errno.EEXIST:     # if directory exists, ignore the error and proceed.
            raise   # if the error is something else, raise it.
    outdir=os.path.abspath(args.outdir)
else: # no outdir specified, use input dir.
    outdir=os.path.abspath(args.dir)

if args.readFilesCmd=='None':
    args.readFilesCmd=None
if args.quantMode=='None':
    args.quantMode=None

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
    read1=files_list[int(SLURM_ARRAY_TASK_ID)]

    # generate read2 name using appropriate naming convention:
    r2replace=args.readPair1Name.replace('1','2')
    read2=read1.replace(args.readPair1Name,r2replace)

    #extract sample name from read names using regex to match illumina naming convention, and grab part before that.
    try: sample_name=re.search(args.sampleNameRegex,read1).group(0)
    except AttributeError: sample_name=read1.split('.fastq')[0]

    # make directory for results:
    results_directory=os.path.join(outdir,sample_name+"_STAR_out")

    try: os.makedirs(results_directory)
    except OSError as e:
        if e.errno != errno.EEXIST:     # if directory exists, ignore the error and proceed.
            raise   # if the error is something else, raise it.
        else:
            warnings.warn("Results directory ({0}) already exists. Files may be overwritten!".format(results_directory))


    # create filename prefix for STAR, including the results directory
    outFnamePrefix=os.path.join(results_directory,sample_name+"_STAR_")

## parameters for running STAR ##
    # determine number of threads:
    line=linecache.getline(__file__, 4)
    match=re.search(r"-c [0-9]*", line).group(0)
    nthreads=match.split("-c ")[1]


    #genomeDir='/n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/STAR_indices'
    #unzip_cmd='zcat'   # command to unzip your files
    #quantMode='GeneCounts'

    #cmd_list=['STAR', '--runThreadN', '{threads}', '--genomeDir', '{genomeDir}', '--readFilesIn', '{read1}', '{read2}', \
    #    '--readFilesCommand', '{unzip_cmd}', '--outFileNamePrefix', '{outFnamePrefix}', '--outSAMtype BAM SortedByCoordinate', \
    #    '--outSAMunmapped None', '--outSAMattributes All', '--outReadsUnmapped Fastx', '--quantMode', '{quantMode}']

    #cmd=" ".join(cmd_list).format(threads=nthreads, genomeDir=genomeDir, read1=read1, read2=read2, unzip_cmd=unzip_cmd, \
    #        outFnamePrefix=outFnamePrefix, quantMode=quantMode)
    cmd = star_command_PE(read1, read2, outFnamePrefix, genomeDir=args.genomeDir, nthreads=nthreads,
                    unzip_cmd=args.readFilesCmd, quantMode=args.quantMode, kwargs_dict=kwargs)

    load_module='module load star/2.5.2b'

    print(cmd)
    os.system("{module} ; {command}".format(module=load_module, command=cmd))

