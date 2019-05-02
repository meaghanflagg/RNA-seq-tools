# Workflow for analysis of RNA sequencing data using the HMS O2 cluster
for general information on the HMS O2 cluster please reference the wiki: https://wiki.rc.hms.harvard.edu/display/O2

### De-multiplex with bcl2fastq
1. create sample sheet:  
*(insert example sample sheet here)*
2. Load bcl2fastq module:  
`module load bcl2fastq/2.20.0.422`
3. Execute bcl2fastq sbatch script:  
  *(insert sbatch script here)*
4. After the job has completed, check if demultiplexing was successful:  
Demux stats are stored in ?? *(finish this part)*

### Check quality of sequences with FastQC
1. create directory to store fastqc output files:  
  `mkdir fastqc_out`
2. Load fastqc module:  
  `module load fastqc`
3. run fastqc on all of your fastq files using `fastqc_array.py`:  
  `fastqc_array.py -dir <path/to/fastqs> -outdir <fastqc_out>`
4. Aggregate results using MultiQC: (https://multiqc.info/)   
  `module load multiqc`  
  `sbatch -p priority -t 30 --mem=6G --wrap "multiqc <fastqc_out> -n <multiqc_fastqc_out>"`  
  *Note:* if you have paired-end data, you can look at them separately:  
   `sbatch -p priority -t 30 --mem=6G --wrap "multiqc <fastqc_out>/*R1_001* -n <multiqc_fastqc_out_R1>"`

### Adapter/Quality trim with Trimmomatic
1. create directory to store trimmed fastq files:  
`mkdir fastqs_trimmed`
2. load trimmomatic v0.36 module:  
`module load trimmomatic/0.36`  
3. run trimmomatic on all of your fastqs using `trimmomatic_array_v2.py`  
  `trimmomatic_array_v2.py -dir <path/to/fastqs/> -outdir <fastqs_trimmed>`  
  *Note:* for paired-end data, add `-PE` flag to the above command.  
4. run FastQC and multiQC again (as above) to verify that contaminating adapter and low-quality bases have been removed.

### Align reads with STAR:
1. create directory to store STAR output files:  
`mkdir STAR_out`  
*Note:* `STAR-array.py` will create subdirectories for each sample in this output directory.
2. Load STAR (version 2.5.2b) module:  
`module load star/2.5.2b`   
3. Align your trimmed fastq files using `STAR-array.py`  
`STAR-array.py -outdir <STAR_out> -dir <path/to/trimmed/fastqs/>`  
*Note:* by default this script directs the STAR aligner to pre-built references for the human genome (Gencode GRCH38, transcriptome annotation v28). You can specify a different reference with the `-genomeDir` parameter.  
4. run multiQC to aggregate data from STAR logfiles:  
`sbatch -p priority -t 30 --mem=6G --wrap "multiqc <STAR_out>/*R1_001* -n <multiqc_STAR>"`

### Create count matrix from STAR outputs:
1. use `generate-star-count-matrix.py`  
`sbatch -p priority -t 30 --mem=3G --wrap "generate-star-count-matrix.py <STAR_out/> <star_counts_matrix> --column unstranded"`  
*Note:* STAR output ReadsPerGene.out.tab is strand-specific. If your library preparation was also strand-specific, you need to select the appropriate column of the ReadsPerGene.out.tab file to compile into the counts matrix:
  - unstranded library prep: column 2, `--column unstranded`
  - first read forward: column 3, `--column 3`
  - first read reverse: column 4, `--column 4`
  - see section below on determining "stranded-ness" using RseQC


### Helpful hints for working on the cluster:
- List uncompleted jobs: (this will also show failed jobs):  
`sacct -j <jobid> | grep -v "COMPLETED"`
- find and delete 0 byte files:  
`find <directory> -maxdepth 1 -size 0 -delete`
- list currently loaded modules:  
`module list`

# Appendix
### Determining stranded-ness of your data with RSeQC
1. Load RSeQC module: (http://rseqc.sourceforge.net/)  
`module load rseqc/2.6.4`
2. use the `infer_experiment.py` module from RSeQC. I have a short sbatch script written (`rseqc_infer_experiment.sbatch.sh`) which allows you to execute this using a bash for loop:  
``for i in `find STAR_out/ -name "*.bam"` ; do sbatch rseqc_infer_experiment.sbatch.sh $i; done``  
*Note:* `infer_experiment.py` requires an annotation file in BED format. The sbatch script currently points to a RefSeq BED annotation file I got from the UCSC genome browser. This will not work with the gencode annotations. I will need to fix this.
3. Interpret results:  
"++,--" indicates stranded data with first read forward. Use column 2 from STAR ReadsPerGene.out.tab.  
"+-,-+" indicates stranded data with first read reverse. Use column 3 from STAR ReadsPerGene.out.tab.  
You can add up columns from the STAR ReadsPerGene.out.tab file to confirm:  
`cat <ReadsPerGene.out.tab> | head -n 104 | tail -n 100 | cut -f <2> | paste -sd+ - | bc`
