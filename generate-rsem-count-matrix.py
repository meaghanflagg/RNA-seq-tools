#!/usr/bin/env python

import os, sys, fnmatch, argparse
import pandas as pd


def generate_count_matrix(paths_to_files,datafield):
    
    datafield_dict={"gene_id": 0, "transcript_id(s)": 1, "length": 2, "effective_length": 3, "expected_count": 4, "TPM": 5, "FPKM": 6}
    datafield_index=datafield_dict[datafield]   # this is used to select which column to parse
    
    
    
    frames=[]       # create list to collect dataframes read from each file
    for FILE in paths_to_files:
        sample_name=FILE.split('/')[-1].split('.genes.results')[0]      #extract sample name from genes.results file
        column_names=['gene_id',sample_name+'_'+datafield]
        frame=pd.read_table(FILE,index_col=0, header=0, names=column_names, usecols=[0,datafield_index])
        frames.append(frame)
    
    
    count_matrix=pd.concat(frames, axis='columns')
    return count_matrix

def round_count_matrix_DESeq2(count_matrix):
    count_matrix_rounded=count_matrix.round(decimals=0)     #pandas df.round returns rounded number with ".0" at end (still dtype float) 
    count_matrix_rounded_int=count_matrix_rounded.astype(dtype='int32')     # convert the rounded number to integer to get rid of trailing zero
    return count_matrix_rounded_int

if __name__ == '__main__':
    
    # argument handling
    parser = argparse.ArgumentParser(description="DESCRIPTION: searches recursively through a directory containing RSEM outputs \
                                 and combines genes.results data from multiple samples into a matrix for downstream analysis")
    parser.add_argument("directory", nargs='?', default=os.getcwd(), help="path to directory with rsem output files")
    parser.add_argument("outfile", help="filname to write ouput matrix")
    parser.add_argument("--data_type",choices=["expected_count","TPM","FPKM"],nargs='?', default='expected_count', help="select type of expression data to use in matrix.")
    parser.add_argument("--outformat", choices=["csv","txt"],nargs='?', default='csv', help="format of output matrix")
    parser.add_argument("--deseq", action='store_true', help="flag to output rounded integer matrix for DESeq2")
    args=parser.parse_args()
    
    # identify directory containing rsem outputs
    
    results_directory=args.directory    # default = os.getcwd(), specified in argument definition.
    
    print "searching {0} for rsem output files".format(os.path.abspath(results_directory))
    
    # select type of expression data to populate matrix
    # genes.results datafields are: gene_id, transcript_id(s), length, effective_length, expected_count, TPM, FPKM
    # DESeq works with count matrices, so default will be expected_count
    
    datafield=args.data_type    #default is csv
    
    print "Using {0} to populate count matrix".format(datafield)
    
    
    # grab paths to rsem output files:
    
    output_files=[]         # a list of rsem output files we will use to generate expression matrix
    output_file_paths=[]    # a list of paths to output files
    
    for path, subdirs, files in os.walk(results_directory):
        for f in files:
            if fnmatch.fnmatch(f,'*.genes.results'):
                output_files.append(path+'/'+f)
                output_file_paths.append(path)
    
    print "found the following output files:\n{0}".format('\n'.join(output_files))
    
    count_matrix=generate_count_matrix(output_files,datafield)
    
    if args.deseq:
        count_matrix=round_count_matrix_DESeq2(count_matrix)
    else:
        count_matrix=count_matrix
    

    if args.outformat == 'csv':
        sep=','
    elif args.outformat == 'txt':
        sep='\t'
    else:
        sep=','
    count_matrix.to_csv(args.outfile+'.'+args.outformat, sep=sep)


