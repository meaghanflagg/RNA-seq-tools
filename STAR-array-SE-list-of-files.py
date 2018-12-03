#!/usr/bin/env python
#SBATCH -p short               #partition
#SBATCH -t 2:00:00             #wall time
#SBATCH -c 8                   #cores requested
#SBATCH --mem 60G              #memory requested
#SBATCH -o star.%j.out         #job out logs
#SBATCH -e star.%j.err         #job error logs


import os, fnmatch, re, sys, warnings

SLURM_ARRAY_TASK_ID=os.environ.get('SLURM_ARRAY_TASK_ID')
if SLURM_ARRAY_TASK_ID == None:
    # which directory to look thru:
    directory=os.getcwd()

    # read command line arguments into list of files:
    args=sys.argv[1:]
    if len(args) < 1:
        sys.exit("No input files specified!")
    
    files_list=[]
    for f in args:
        if not os.path.isfile(f):
            warnings.warn("{filename} does not exist! Skipping.".format(filename=f))
        else:
            files_list.append(os.path.abspath(f))

    #print '\n'.join(files_list)
  
    os.environ['ARRAY_FILES']=":".join(files_list)
    os.environ['DIRECTORY']=directory
    
    sbatch_cmd=["sbatch","--array=0-{0}".format(len(files_list)-1),__file__]
    
    os.system( " ".join(sbatch_cmd) )


else:
    files_list = os.environ.get('ARRAY_FILES').split(':')
    
    directory=os.environ.get('DIRECTORY')

    os.system("module load star/2.5.2b")
    
    read1=files_list[int(SLURM_ARRAY_TASK_ID)]
    
    #read2=read1.replace('_R1_','_R2_')
    
    ###extract sample name from read names using regex to match illumina naming convention, and grab part before that.
    # sample_name=read1.split(re.search(r'_S[0-9]+_R[12]_001',read1).group(0))[0].split('/')[-1]
    
    ### for now use regex to match crystal's sample naming convention:
    sample_name=re.search(r'[0-9]{6}_CD103_[a-z]+',read1).group(0)
    
    # make directory for results:
    results_directory=os.path.join(directory,sample_name+"_STAR_out")
    try:
        os.mkdir(results_directory)     # this fails if the directory already exists!
    except OSError, e:
        if e.errno != os.errno.EEXIST:      #check if the error is a "file exists" error. if so, use existing directory. if not, raise the OS error.
            raise
        else:
            pass
    
    # create filename prefix for STAR, including the results directory
    outFnamePrefix="{res_dir}/{samp_name}_STAR_".format(res_dir=results_directory, samp_name=sample_name)


## parameters for running STAR ##
    nthreads=8
    genomeDir='/n/groups/kwon/data1/databases/human/hg38/gencode_GRCh38/STAR_indices'
    unzip_cmd='zcat'   # command to unzip your files
    quantMode='GeneCounts'

    cmd_list=['STAR', '--runThreadN', '{threads}', '--genomeDir', '{genomeDir}', '--readFilesIn', '{read1}', \
        '--readFilesCommand', '{unzip_cmd}', '--outFileNamePrefix', '{outFnamePrefix}', '--outSAMtype BAM SortedByCoordinate', \
        '--outSAMunmapped None', '--outSAMattributes All', '--outReadsUnmapped Fastx', '--quantMode', '{quantMode}']

    cmd=" ".join(cmd_list).format(threads=nthreads, genomeDir=genomeDir, read1=read1, unzip_cmd=unzip_cmd, \
            outFnamePrefix=outFnamePrefix, quantMode=quantMode)
    
    os.system(cmd)


