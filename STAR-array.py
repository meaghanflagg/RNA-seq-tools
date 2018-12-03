#!/usr/bin/env python
#SBATCH -p short               #partition
#SBATCH -t 1:00:00             #wall time
#SBATCH -c 8                   #cores requested
#SBATCH --mem 48G              #memory requested
#SBATCH -o star.%j.out         #job out logs
#SBATCH -e star.%j.err         #job error logs


import os, fnmatch, re, sys

# which directory to look thru:
try: directory = os.path.abspath(sys.argv[1])
except IndexError: directory=os.getcwd()


SLURM_ARRAY_TASK_ID=os.environ.get('SLURM_ARRAY_TASK_ID')

if SLURM_ARRAY_TASK_ID == None:
    files_list=[]
    for f in os.listdir(directory):
    # build file array
        if fnmatch.fnmatch(f, '*R1_001_trimmed.fastq.gz'):
            files_list.append(os.path.abspath(f))
    
    if not len(files_list) > 1:
        sys.exit("Error: No files found!")
    
    
    os.environ['ARRAY_FILES']=":".join(files_list)
    os.environ['DIRECTORY']=directory
    
    sbatch_cmd=["sbatch","--array=0-{0}".format(len(files_list)-1),__file__]

    os.system( " ".join(sbatch_cmd) )


else:
    files_list = os.environ.get('ARRAY_FILES').split(':')
    
    directory=os.environ.get('DIRECTORY')

    os.system("module load star/2.5.2b")
    
    read1=files_list[int(SLURM_ARRAY_TASK_ID)]
    
    read2=read1.replace('_R1_','_R2_')
    
    #extract sample name from read names using regex to match illumina naming convention, and grab part before that.
    sample_name=read1.split(re.search(r'_S[0-9]+_R[12]_001',read1).group(0))[0].split('/')[-1]
    
    # make directory for results:
    results_directory=os.path.join(directory,sample_name+"_STAR_out")
    os.mkdir(results_directory)
    
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
    
    os.system(cmd)
