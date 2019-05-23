# SBATCH scripts to accompany RNA-Seq-Tools
#### Author: Meaghan Flagg

#### General usage guidelines:
A set of sbatch scripts that may be useful for your RNA-seq analysis. Designed for use on the HMS O2 cluster with Slurm job scheduler. They include the necessary arguments for the slurm scheduler (e.g. parition, memory, etc) in the file header. Written in bash, they are executed directly from the command line following the `sbatch` command. Example:  
`sbatch rseqc_fragment_size.sbatch.sh`

Most of these scripts are written to accept an input file as the first positional argument (`$1` in bash). Therefore, you can run these scripts on a list of files using a for loop as in the following example:  
``for i in `find STAR_out/ -name "*.bam"`;``  
`do sbatch rseqc_fragment_size.sbatch.sh $i;`  
`done`
