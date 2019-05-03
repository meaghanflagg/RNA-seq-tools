#!/usr/bin/env python

def read_multiQC(path_to_multiqc_text_file, sample_regex=None):
    '''
    reads data from multiQC txt output file
    '''
    import pandas as pd
    multiQC_data=pd.read_table(path_to_multiqc_text_file)
    if sample_regex:
        import re
        multiQC_data.index=multiQC_data['Sample'].map(lambda x: re.search(sample_regex,x).group(0))
    else:
        multiQC_data.set_index('Sample')
    
    return multiQC_data


def plot_reads_per_sample(fastqc_data):
    '''
    plots the median reads per sample for all libraries
    '''
    import seaborn as sns