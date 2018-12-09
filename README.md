# RNA-seq-tools
#### Author: Meaghan Flagg
A set of useful python scripts for RNA seq analysis.
## Dependencies:
python 2.7.14  
pandas version 0.20.3


## Tools
### fastqc_parser.py
**DESCRIPTION:** Extracts over-represented sequences from FASTQC output files and returns a FASTA file with an entry for each sequence.
Operates on a directory containing 'fastqc.zip' output files.  
**POSITIONAL ARGUMENTS:**  
`directory`   path to directory with FASTQC output files. Accepts UNIX-style abbreviation  
`outfile`     filename to write ouput FASTA  
**OPTIONAL ARGUMENTS:**  
`-h, --help`  show help message and exit  
`--all_hits`  flag to write all sequences to FASTA. Default behavior is to write only sequences with no hit identified by FASTQC  
**EXAMPLE:**  
`fastqc_parser.py path/to/fastqc/data outfile.fasta`

### trimmomatic_array.py
**DESCRIPTION:** Submits trimmomatic jobs to slurm job scheduler as an array.  
**OPTIONAL ARGUMENTS:**  
`-h, --help`  show help message and exit  
`-PE` Flag for paired-end data. Default=False  
`-glob_pattern GLOB_PATTERN` Unix-style pattern to find files in directory.
                        Defaults to illumina-style naming convention
                        '\*R1_001.fastq\*'.  
`-adapter_file ADAPTER_FILE` Specify path to custom adapter file. Defaults to
                        'NexteraPE-PE.fa' provided in trimmomatic
                        distribution.  
`-logfile [LOGFILE]` Filename for STDOUT and STDERR logs. Defaults to job
                        array ID with timestamp. Currently defunct.  
`-outdir [OUTDIR]` Directory to store output files. Defaults to
                        specified input directory, or current working
                        directory if none specified.  
`-dir DIR` path to directory containing fastq files. Default:
                        current working directory  
`-files_list [FILES_LIST [FILES_LIST ...]]` Alternative to '-dir'. Specify input fastq files separated by spaces  
**EXAMPLE:**  
`trimmomatic_array.py -PE -outdir trimmed_fastqs -dir fastqs/`
