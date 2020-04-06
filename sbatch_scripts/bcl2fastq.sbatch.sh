#!/bin/bash


#SBATCH -J bcl2fastq                    # job name for the array
#SBATCH -n 8                    # number of cores requested
#SBATCH -t 6:00:00              # runtime in HH:MM:SS. Can also use D-HH:MM:SS
#SBATCH -p priority             # submit to 'short' partition
#SBATCH --mem-per-cpu=4G        # allocate memory PER CORE (default = 1 GB)


#SBATCH -o bcl2fastq_%j.out             # STDOUT goes to this file
#SBATCH -e bcl2fastq_%j.err             # STDERR goes to this file

module load bcl2fastq/2.20.0.422

bcl2fastq --runfolder-dir <path_to_run_folder> \
--output-dir <path_to_run_folder>/fastqs \
--sample-sheet <path_to_sample_sheet.csv> \
--no-lane-splitting
