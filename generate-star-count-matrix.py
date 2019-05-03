#!/usr/bin/env python

import os, sys, fnmatch, argparse
import pandas as pd


def generate_count_matrix(paths_to_files,datafield):
    
    datafield_dict={"gene_id": 0, "unstranded": 1, "first": 2, "second": 3}
    datafield_index=datafield_dict[datafield]   # this is used to select which column to parse
    
    
    
    frames=[]       # create list to collect dataframes read from each file
    for FILE in paths_to_files:
        sample_name=FILE.split('/')[-1].split('ReadsPerGene.out.tab')[0].rstrip('_')      #extract sample name from output file
        column_names=['gene_id',sample_name]
        frame=pd.read_table(FILE,index_col=0, header=0, names=column_names, usecols=[0,datafield_index], skiprows=3)
        frames.append(frame)
    
    
    count_matrix=pd.concat(frames, axis='columns')
    return count_matrix

if __name__ == '__main__':
    
    # argument handling
    parser = argparse.ArgumentParser(description="DESCRIPTION: searches recursively through a directory containing STAR outputs \
                                 and combines ReadsPerGene.out.tab data from multiple samples into a matrix for downstream analysis")
    parser.add_argument("directory", nargs='?', default=os.getcwd(), help="path to directory with STAR output files")
    parser.add_argument("outfile", help="filname to write ouput matrix")
    parser.add_argument("--column",choices=["unstranded","first","second"],nargs='?', default='second', help="select which counts column to use based on strandedness of data.\
                        'unstranded': column 2; 'first': column 3; 'second': column 4. Default='second'. See STAR documentation for explanation.")
    parser.add_argument("--outformat", choices=["csv","txt"],nargs='?', default='csv', help="format of output matrix. Default='csv'")
    args=parser.parse_args()
    
    # identify directory containing star outputs
    
    results_directory=args.directory    # default = os.getcwd(), specified in argument definition.
    
    print "searching {0} for STAR output files".format(os.path.abspath(results_directory))
    
    # select type of expression data to populate matrix
    # genes.results datafields are: gene_id, transcript_id(s), length, effective_length, expected_count, TPM, FPKM
    # DESeq works with count matrices, so default will be expected_count
    
    datafield=args.column    #default is csv
    
    print "Using {0} to populate count matrix".format(datafield)
    
    
    # grab paths to star output files:
    
    output_files=[]         # a list of rsem output files we will use to generate expression matrix
    output_file_paths=[]    # a list of paths to output files
    
    for path, subdirs, files in os.walk(results_directory):
        for f in files:
            if fnmatch.fnmatch(f,'*ReadsPerGene.out.tab'):
                output_files.append(path+'/'+f)
                output_file_paths.append(path)
    
    print "found the following output files:\n{0}".format('\n'.join(output_files))
    
    count_matrix=generate_count_matrix(output_files,datafield)
    
    
    if args.outformat == 'csv':
        sep=','
    elif args.outformat == 'txt':
        sep='\t'
    else:
        sep=','
    count_matrix.to_csv(args.outfile+'.'+args.outformat, sep=sep)


