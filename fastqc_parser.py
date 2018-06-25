#!/usr/bin/env python

import re, sys, glob, zipfile, fnmatch, argparse, os
import pandas as pd
# python 2 vs 3 version control:
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO



def extract_overrep_seqs(FILE):
    '''
    extracts the ">>Overrepresented sequences" module from a "fastqc_data.txt" file
    Returns each sequence, percentage of reads, and hit as a pandas dataframe
    Input is the contents of a "fastqc_data.txt" that has been read into a string (e.g with f.read())
    ---
    Usage:
    extract_overrep_seqs(file_as_string)
    ---
    Author: Meaghan Flagg\thttps://github.com/meaghanflagg
    '''
    
    regex=re.compile(r'>>Overrepresented sequences.*?>>END_MODULE', re.DOTALL)
    
    block=regex.findall(FILE)[0]

    cleanBlock='\n'.join(re.findall(r'^(?!>>).*', block, flags=re.MULTILINE))
    
    blockIO=StringIO(cleanBlock)
    
    table=pd.read_table(blockIO, sep='\t')
    return table

if __name__ == '__main__':
    
    
    # parse arguments:
    parser = argparse.ArgumentParser(description="DESCRIPTION:\
            Extracts over-represented sequences from FASTQC output files and returns a FASTA file with an entry for each sequence.\n\
            Operates on a directory containing 'fastqc.zip' output files.")
    parser.add_argument("directory", nargs='?', default=os.getcwd(), help="path to directory with FASTQC output files")
    parser.add_argument("outfile", help="filname to write ouput FASTA")
    parser.add_argument("--all_hits", action='store_true', help="flag to write all sequences to FASTA. \
                        Default behavior is to write only sequences with no hit identified by FASTQC")
    args=parser.parse_args()
    
    
    
    
    # setup path to glob through:
    path_to_dir_with_fastqc_outputs=args.directory
    path_to_dir_with_fastqc_outputs=os.path.join(path_to_dir_with_fastqc_outputs,'*fastqc.zip')
    
    # initalize list to contain dfs frome each sample:
    frames=[]
    
    # loop through a directory containing FASTQC output files:
    for archive in glob.glob(path_to_dir_with_fastqc_outputs):
        if zipfile.is_zipfile(archive):    # test if zip file is a real zip archive
            with zipfile.ZipFile(archive) as z:   # read the archive
                for f in z.namelist():
                    if fnmatch.fnmatch(f, '*fastqc_data.txt'):
                        FILE=z.read(f)
                        sampleName=archive.split('/')[-1].split('_fastqc')[0]
                        try:
                            table=extract_overrep_seqs(FILE) # throws EmptyDataError if the sample 'passes' overrep seqs module
                            table['sample_name']=sampleName
                            frames.append(table)
                        except pd.errors.EmptyDataError :
                            print '{0} passed QC and has no over-represented sequences'.format(sampleName)
                            
    
    # concatenate the dfs:
    concatted=pd.concat(frames, axis=0)
    
    
    # parsing known vs. unknown hits:
    known_hits=concatted[concatted['Possible Source'] != 'No Hit']    # known hits
    unknown_hits=concatted[concatted['Possible Source'] == 'No Hit']    # unknown hits    # default will only write these
    if args.all_hits:
        hits=concatted
    else:
        hits=unknown_hits
    
    
    # initate outfile:
    with open(args.outfile,'w') as out:
    
    # format the overrepresented sequences into a FASTA file so they can be blasted:
        grouped=hits.groupby('sample_name')
        for group in grouped.groups.keys():
        
            counter=0
            seqs=grouped.get_group(group)['#Sequence'].values
            
            ## list method: ##
            for seq in seqs:
                counter=counter+1    #makes a unique header for each sequence entry
                out.write('>{0}_{1}\n{2}\n'.format(group, counter, seq))
            
            
            ## to_dict method: ##
            #nested_dict=grouped.get_group(group)[['sample_name','#Sequence']].to_dict('records')
            #for dic in nested_dict:
                #counter=counter+1
                #out.write('>{0}_{1}\n{2}\n'.format(dic['sample_name'], counter, dic['#Sequence']))

        



    
