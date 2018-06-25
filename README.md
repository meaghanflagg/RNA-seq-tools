# RNA-seq-tools
#### Author: Meaghan Flagg
A set of useful python scripts for RNA seq analysis


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
